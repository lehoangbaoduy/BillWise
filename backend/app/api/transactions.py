import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_can_add_transactions, require_household_member, require_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.category import Category
from app.models.transaction import Transaction, TransactionLineItem, TransactionSource, TransactionType
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionPublic, TransactionUpdate
from app.services.cashback_service import record_cashback_for_line_items
from app.services.transaction_validation import (
    create_transaction_record,
    load_line_items,
    to_transaction_public,
    validate_goal,
    validate_line_items,
    validate_payment_method,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


async def _get_owned_or_404(session: AsyncSession, user: User, transaction_id: uuid.UUID) -> Transaction:
    transaction = await session.get(Transaction, transaction_id)
    if transaction is None or transaction.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.get("", response_model=list[TransactionPublic])
async def list_transactions(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    category_id: uuid.UUID | None = None,
    payment_method_id: uuid.UUID | None = None,
    amount_min: Decimal | None = None,
    amount_max: Decimal | None = None,
    search: str | None = None,
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> list[TransactionPublic]:
    owner_id = household_owner_id(user)
    conditions = [Transaction.user_id == owner_id]
    if user.role == UserRole.PARTNER:
        # A partner only sees transactions where every line item's category is
        # shared with them — a transaction touching any private category is
        # excluded outright rather than partially redacted, since showing a
        # subset of line items under the real total_amount would itself leak
        # that a hidden private-category amount exists.
        private_category_ids = select(Category.id).where(Category.user_id == owner_id, Category.is_shared == False)  # noqa: E712
        conditions.append(
            Transaction.id.not_in(
                select(TransactionLineItem.transaction_id).where(
                    TransactionLineItem.category_id.in_(private_category_ids)
                )
            )
        )
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
            created_by_user_id=t.created_by_user_id,
        )
        for t in transactions
    ]


@router.post("", response_model=TransactionPublic, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    body: TransactionCreate,
    user: User = Depends(require_can_add_transactions),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    transaction, possible_duplicate = await create_transaction_record(session, user, body, TransactionSource.MANUAL)
    line_items = await load_line_items(session, transaction.id)
    await record_cashback_for_line_items(session, transaction, line_items)
    return await to_transaction_public(session, transaction, possible_duplicate=possible_duplicate)


@router.get("/{transaction_id}", response_model=TransactionPublic)
async def get_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    transaction = await _get_owned_or_404(session, user, transaction_id)
    return await to_transaction_public(session, transaction)


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
        await validate_goal(session, user, transaction_type, updates["goal_id"])

    # Validation must run and raise (if it's going to) before anything below
    # mutates `transaction` or calls session.add — otherwise a later autoflush
    # (triggered by any session.exec/get) can silently persist a half-applied
    # update even though the request ultimately fails with a 422.
    new_line_items: list[TransactionLineItem] | None = None
    if body.line_items is not None:
        await validate_line_items(session, user, transaction_type, total_amount, body.line_items)
        existing_line_items = await load_line_items(session, transaction.id)
        for item in existing_line_items:
            # CashbackRecord.line_item_id has ondelete="CASCADE", so any cashback
            # record tied to a replaced line item is cleaned up automatically —
            # no orphaned records, and no risk of a stale manual override
            # surviving against a line item that no longer exists.
            await session.delete(item)
        await session.flush()
        new_line_items = []
        for item in body.line_items:
            line_item = TransactionLineItem(
                transaction_id=transaction.id,
                category_id=item.category_id,
                item_name=item.item_name,
                amount=item.amount,
                quantity=item.quantity,
                notes=item.notes,
            )
            session.add(line_item)
            new_line_items.append(line_item)
    elif body.total_amount is not None or body.transaction_type is not None:
        existing_line_items = await load_line_items(session, transaction.id)
        await validate_line_items(session, user, transaction_type, total_amount, existing_line_items)

    for field, value in updates.items():
        setattr(transaction, field, value)
    transaction.updated_at = utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    # Cashback is only recomputed when line items are wholesale replaced. Editing
    # just the date/payment-method/amount without touching line_items leaves
    # existing cashback records (including any manual overrides) untouched, per
    # PRD §27.5 "Manual override persists, not overwritten by recalculation" —
    # documented scope choice, not a silent gap.
    if new_line_items is not None:
        await record_cashback_for_line_items(session, transaction, new_line_items)

    return await to_transaction_public(session, transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    transaction = await _get_owned_or_404(session, user, transaction_id)
    await session.delete(transaction)
    await session.commit()
