import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.goal import SavingsGoal
from app.models.transaction import Transaction, TransactionLineItem, TransactionSource, TransactionType
from app.models.user import User
from app.schemas.goal import AddFundsRequest, GoalContributionPublic, GoalCreate, GoalDetail, GoalPublic, GoalSharingUpdate, GoalUpdate
from app.schemas.transaction import TransactionLineItemCreate
from app.services.transaction_validation import validate_line_items, validate_payment_method

router = APIRouter(prefix="/goals", tags=["goals"])


async def _get_owned_active_or_404(session: AsyncSession, user: User, goal_id: uuid.UUID) -> SavingsGoal:
    goal = await session.get(SavingsGoal, goal_id)
    if goal is None or goal.user_id != user.id or not goal.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


async def _current_amounts(session: AsyncSession, goal_ids: list[uuid.UUID]) -> dict[uuid.UUID, Decimal]:
    if not goal_ids:
        return {}
    statement = (
        select(Transaction.goal_id, func.sum(Transaction.total_amount))
        .where(Transaction.goal_id.in_(goal_ids))  # type: ignore[union-attr]
        .group_by(Transaction.goal_id)
    )
    rows = (await session.exec(statement)).all()
    return {goal_id: total for goal_id, total in rows}


async def _current_amount(session: AsyncSession, goal_id: uuid.UUID) -> Decimal:
    statement = select(func.sum(Transaction.total_amount)).where(Transaction.goal_id == goal_id)
    total = (await session.exec(statement)).first()
    return total if total is not None else Decimal("0")


def _to_public(goal: SavingsGoal, current_amount: Decimal) -> GoalPublic:
    return GoalPublic(
        id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=current_amount,
        target_date=goal.target_date,
        icon=goal.icon,
        color=goal.color,
        is_shared=goal.is_shared,
        is_active=goal.is_active,
    )


@router.get("", response_model=list[GoalPublic])
async def list_goals(
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[GoalPublic]:
    goals = (
        await session.exec(select(SavingsGoal).where(SavingsGoal.user_id == user.id, SavingsGoal.is_active == True))  # noqa: E712
    ).all()
    amounts = await _current_amounts(session, [g.id for g in goals])
    return [_to_public(goal, amounts.get(goal.id, Decimal("0"))) for goal in goals]


@router.post("", response_model=GoalPublic, status_code=status.HTTP_201_CREATED)
async def create_goal(
    body: GoalCreate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = SavingsGoal(user_id=user.id, **body.model_dump())
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return _to_public(goal, Decimal("0"))


@router.get("/{goal_id}", response_model=GoalDetail)
async def get_goal(
    goal_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalDetail:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    contributions = (
        await session.exec(
            select(Transaction).where(Transaction.goal_id == goal_id).order_by(Transaction.date.desc())  # type: ignore[union-attr]
        )
    ).all()
    current_amount = sum((t.total_amount for t in contributions), Decimal("0"))
    public = _to_public(goal, current_amount)
    return GoalDetail(
        **public.model_dump(),
        contributing_transactions=[
            GoalContributionPublic(
                id=t.id, date=t.date, merchant=t.merchant, total_amount=t.total_amount, transaction_type=t.transaction_type
            )
            for t in contributions
        ],
    )


@router.patch("/{goal_id}", response_model=GoalPublic)
async def update_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    goal.updated_at = utcnow()
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return _to_public(goal, await _current_amount(session, goal.id))


@router.patch("/{goal_id}/sharing", response_model=GoalPublic)
async def update_goal_sharing(
    goal_id: uuid.UUID,
    body: GoalSharingUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    goal.is_shared = body.is_shared
    goal.updated_at = utcnow()
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return _to_public(goal, await _current_amount(session, goal.id))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_goal(
    goal_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    goal.is_active = False
    goal.updated_at = utcnow()
    session.add(goal)

    linked_transactions = (await session.exec(select(Transaction).where(Transaction.goal_id == goal_id))).all()
    for transaction in linked_transactions:
        transaction.goal_id = None
        session.add(transaction)

    await session.commit()


@router.post("/{goal_id}/add-funds", response_model=GoalPublic, status_code=status.HTTP_201_CREATED)
async def add_funds(
    goal_id: uuid.UUID,
    body: AddFundsRequest,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    await validate_payment_method(session, user, body.payment_method_id)
    line_item = TransactionLineItemCreate(category_id=body.category_id, item_name=goal.name, amount=body.amount)
    await validate_line_items(session, user, TransactionType.SAVING_EXPENSE, body.amount, [line_item])

    transaction = Transaction(
        user_id=user.id,
        payment_method_id=body.payment_method_id,
        goal_id=goal.id,
        date=body.date,
        merchant=body.merchant,
        total_amount=body.amount,
        transaction_type=TransactionType.SAVING_EXPENSE,
        source=TransactionSource.MANUAL,
        notes=body.notes,
    )
    session.add(transaction)
    await session.flush()
    session.add(
        TransactionLineItem(
            transaction_id=transaction.id,
            category_id=body.category_id,
            item_name=goal.name,
            amount=body.amount,
        )
    )
    await session.commit()

    return _to_public(goal, await _current_amount(session, goal.id))
