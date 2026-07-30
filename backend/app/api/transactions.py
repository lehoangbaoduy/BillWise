import uuid
from datetime import date as date_type
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.goal import SavingsGoal
from app.models.transaction import Transaction, TransactionLineItem, TransactionSource, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionPublic, TransactionUpdate
from app.services.transaction_validation import validate_line_items, validate_payment_method

router = APIRouter(prefix="/transactions", tags=["transactions"])

_GOAL_ELIGIBLE_TYPES = {TransactionType.SAVING_EXPENSE, TransactionType.ADJUSTMENT}


async def _validate_goal(
    session: AsyncSession, user: User, transaction_type: TransactionType, goal_id: uuid.UUID | None
) -> None:
    if goal_id is None:
        return
    if transaction_type not in _GOAL_ELIGIBLE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="goal_id is only valid for Saving expense or Adjustment transactions",
        )
    goal = await session.get(SavingsGoal, goal_id)
    if goal is None or goal.user_id != user.id or not goal.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid goal")


async def _detect_duplicate(
    session: AsyncSession,
    user: User,
    merchant: str,
    date: date_type,
    total_amount: Decimal,
    payment_method_id: uuid.UUID,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    conditions = [
        Transaction.user_id == user.id,
        Transaction.merchant == merchant,
        Transaction.date == date,
        Transaction.total_amount == total_amount,
        Transaction.payment_method_id == payment_method_id,
    ]
    if exclude_id is not None:
        conditions.append(Transaction.id != exclude_id)
    statement = select(Transaction).where(and_(*conditions))
    result = await session.exec(statement)
    return result.first() is not None


async def _get_owned_or_404(session: AsyncSession, user: User, transaction_id: uuid.UUID) -> Transaction:
    transaction = await session.get(Transaction, transaction_id)
    if transaction is None or transaction.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


async def _load_line_items(session: AsyncSession, transaction_id: uuid.UUID) -> list[TransactionLineItem]:
    statement = select(TransactionLineItem).where(TransactionLineItem.transaction_id == transaction_id)
    return (await session.exec(statement)).all()


async def _to_public(session: AsyncSession, transaction: Transaction, possible_duplicate: bool = False) -> TransactionPublic:
    line_items = await _load_line_items(session, transaction.id)
    return TransactionPublic(
        id=transaction.id,
        payment_method_id=transaction.payment_method_id,
        goal_id=transaction.goal_id,
        date=transaction.date,
        merchant=transaction.merchant,
        description=transaction.description,
        total_amount=transaction.total_amount,
        transaction_type=transaction.transaction_type,
        source=transaction.source,
        notes=transaction.notes,
        line_items=line_items,
        possible_duplicate=possible_duplicate,
    )


@router.get("", response_model=list[TransactionPublic])
async def list_transactions(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    category_id: uuid.UUID | None = None,
    payment_method_id: uuid.UUID | None = None,
    amount_min: Decimal | None = None,
    amount_max: Decimal | None = None,
    search: str | None = None,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionPublic]:
    conditions = [Transaction.user_id == user.id]
    if month is not None:
        year, mon = month.split("-")
        conditions.append(and_(extract("year", Transaction.date) == int(year), extract("month", Transaction.date) == int(mon)))
    if payment_method_id is not None:
        conditions.append(Transaction.payment_method_id == payment_method_id)
    if amount_min is not None:
        conditions.append(Transaction.total_amount >= amount_min)
    if amount_max is not None:
        conditions.append(Transaction.total_amount <= amount_max)
    if search is not None and search.strip():
        pattern = f"%{search.strip()}%"
        conditions.append(
            Transaction.merchant.ilike(pattern) | Transaction.description.ilike(pattern)  # type: ignore[union-attr]
        )
    if category_id is not None:
        conditions.append(
            Transaction.id.in_(
                select(TransactionLineItem.transaction_id).where(TransactionLineItem.category_id == category_id)
            )
        )

    statement = select(Transaction).where(and_(*conditions)).order_by(Transaction.date.desc(), Transaction.created_at.desc())
    transactions = (await session.exec(statement)).all()

    line_items_by_transaction: dict[uuid.UUID, list[TransactionLineItem]] = {t.id: [] for t in transactions}
    if transactions:
        all_line_items = (
            await session.exec(
                select(TransactionLineItem).where(
                    TransactionLineItem.transaction_id.in_([t.id for t in transactions])  # type: ignore[union-attr]
                )
            )
        ).all()
        for item in all_line_items:
            line_items_by_transaction[item.transaction_id].append(item)

    return [
        TransactionPublic(
            id=t.id,
            payment_method_id=t.payment_method_id,
            goal_id=t.goal_id,
            date=t.date,
            merchant=t.merchant,
            description=t.description,
            total_amount=t.total_amount,
            transaction_type=t.transaction_type,
            source=t.source,
            notes=t.notes,
            line_items=line_items_by_transaction[t.id],
            possible_duplicate=False,
        )
        for t in transactions
    ]


@router.post("", response_model=TransactionPublic, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: TransactionCreate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    await validate_payment_method(session, user, body.payment_method_id)
    await validate_line_items(session, user, body.transaction_type, body.total_amount, body.line_items)
    await _validate_goal(session, user, body.transaction_type, body.goal_id)

    possible_duplicate = await _detect_duplicate(
        session, user, body.merchant, body.date, body.total_amount, body.payment_method_id
    )

    transaction = Transaction(
        user_id=user.id,
        payment_method_id=body.payment_method_id,
        goal_id=body.goal_id,
        date=body.date,
        merchant=body.merchant,
        description=body.description,
        total_amount=body.total_amount,
        transaction_type=body.transaction_type,
        source=TransactionSource.MANUAL,
        notes=body.notes,
    )
    session.add(transaction)
    await session.flush()

    for item in body.line_items:
        session.add(
            TransactionLineItem(
                transaction_id=transaction.id,
                category_id=item.category_id,
                item_name=item.item_name,
                amount=item.amount,
                quantity=item.quantity,
                notes=item.notes,
            )
        )
    await session.commit()
    await session.refresh(transaction)
    return await _to_public(session, transaction, possible_duplicate=possible_duplicate)


@router.get("/{transaction_id}", response_model=TransactionPublic)
async def get_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    transaction = await _get_owned_or_404(session, user, transaction_id)
    return await _to_public(session, transaction)


@router.patch("/{transaction_id}", response_model=TransactionPublic)
async def update_transaction(
    transaction_id: uuid.UUID,
    body: TransactionUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    transaction = await _get_owned_or_404(session, user, transaction_id)

    updates = body.model_dump(exclude_unset=True, exclude={"line_items"})
    payment_method_id = body.payment_method_id if body.payment_method_id is not None else transaction.payment_method_id
    if body.payment_method_id is not None:
        await validate_payment_method(session, user, body.payment_method_id)

    transaction_type = body.transaction_type if body.transaction_type is not None else transaction.transaction_type
    total_amount = body.total_amount if body.total_amount is not None else transaction.total_amount

    if "goal_id" in updates and updates["goal_id"] is not None:
        await _validate_goal(session, user, transaction_type, updates["goal_id"])

    if body.line_items is not None:
        await validate_line_items(session, user, transaction_type, total_amount, body.line_items)
        existing_line_items = await _load_line_items(session, transaction.id)
        for item in existing_line_items:
            await session.delete(item)
        await session.flush()
        for item in body.line_items:
            session.add(
                TransactionLineItem(
                    transaction_id=transaction.id,
                    category_id=item.category_id,
                    item_name=item.item_name,
                    amount=item.amount,
                    quantity=item.quantity,
                    notes=item.notes,
                )
            )
    elif body.total_amount is not None or body.transaction_type is not None:
        existing_line_items = await _load_line_items(session, transaction.id)
        await validate_line_items(session, user, transaction_type, total_amount, existing_line_items)

    for field, value in updates.items():
        setattr(transaction, field, value)
    transaction.updated_at = utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return await _to_public(session, transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    transaction = await _get_owned_or_404(session, user, transaction_id)
    await session.delete(transaction)
    await session.commit()
