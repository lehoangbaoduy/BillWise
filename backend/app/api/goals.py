import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import and_, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.goal import SavingsGoal
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction, TransactionLineItem, TransactionSource, TransactionType
from app.models.user import User
from app.schemas.goal import AddFundsRequest, GoalContributionPublic, GoalCreate, GoalDetail, GoalPublic, GoalSharingUpdate, GoalUpdate
from app.schemas.transaction import TransactionLineItemCreate
from app.services.item_visibility import user_can_access_item, visibility_condition
from app.services.transaction_validation import validate_line_items, validate_payment_method

router = APIRouter(prefix="/goals", tags=["goals"])


async def _get_owned_active_or_404(session: AsyncSession, user: User, goal_id: uuid.UUID) -> SavingsGoal:
    goal = await session.get(SavingsGoal, goal_id)
    owner_id = household_owner_id(user)
    if (
        goal is None
        or goal.user_id != owner_id
        or not goal.is_active
        or not user_can_access_item(goal.is_shared, goal.created_by_user_id, owner_id, user)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


def _personal_contribution_condition(owner_id: uuid.UUID, user: User):
    # Mirrors dashboard.py's _personal_visibility_condition: a shared goal's
    # current_amount must not leak how much someone else privately contributed
    # via their own private wallet -- only shared-wallet contributions and the
    # viewer's own private-wallet contributions count toward what they see.
    return or_(
        PaymentMethod.is_shared == True,  # noqa: E712
        PaymentMethod.created_by_user_id == user.id,
        and_(PaymentMethod.created_by_user_id.is_(None), user.id == owner_id),
    )


async def _current_amounts(session: AsyncSession, owner_id: uuid.UUID, user: User, goal_ids: list[uuid.UUID]) -> dict[uuid.UUID, Decimal]:
    if not goal_ids:
        return {}
    statement = (
        select(Transaction.goal_id, func.sum(Transaction.total_amount))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(Transaction.goal_id.in_(goal_ids), _personal_contribution_condition(owner_id, user))  # type: ignore[union-attr]
        .group_by(Transaction.goal_id)
    )
    rows = (await session.exec(statement)).all()
    return {goal_id: total for goal_id, total in rows}


async def _current_amount(session: AsyncSession, owner_id: uuid.UUID, user: User, goal_id: uuid.UUID) -> Decimal:
    statement = (
        select(func.sum(Transaction.total_amount))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(Transaction.goal_id == goal_id, _personal_contribution_condition(owner_id, user))
    )
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
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[GoalPublic]:
    owner_id = household_owner_id(user)
    statement = select(SavingsGoal).where(
        SavingsGoal.user_id == owner_id,
        SavingsGoal.is_active == True,  # noqa: E712
        visibility_condition(SavingsGoal, owner_id, user),
    )
    goals = (await session.exec(statement)).all()
    amounts = await _current_amounts(session, owner_id, user, [g.id for g in goals])
    return [_to_public(goal, amounts.get(goal.id, Decimal("0"))) for goal in goals]


@router.post("", response_model=GoalPublic, status_code=status.HTTP_201_CREATED)
async def create_goal(
    request: Request,
    body: GoalCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    owner_id = household_owner_id(user)
    goal = SavingsGoal(user_id=owner_id, created_by_user_id=user.id if user.id != owner_id else None, **body.model_dump())
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    await log_audit_event(
        session, "goal.created", user_id=user.id, entity_type="goal", entity_id=goal.id,
        metadata={"name": goal.name}, request=request,
    )
    return _to_public(goal, Decimal("0"))


@router.get("/{goal_id}", response_model=GoalDetail)
async def get_goal(
    goal_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalDetail:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    owner_id = household_owner_id(user)
    contributions = (
        await session.exec(
            select(Transaction)
            .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
            .where(Transaction.goal_id == goal_id, _personal_contribution_condition(owner_id, user))  # type: ignore[union-attr]
            .order_by(Transaction.date.desc())
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
    request: Request,
    goal_id: uuid.UUID,
    body: GoalUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    updated_fields = body.model_dump(exclude_unset=True)
    for field, value in updated_fields.items():
        setattr(goal, field, value)
    goal.updated_at = utcnow()
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    await log_audit_event(
        session, "goal.updated", user_id=user.id, entity_type="goal", entity_id=goal.id,
        metadata={"fields": list(updated_fields.keys())}, request=request,
    )
    owner_id = household_owner_id(user)
    return _to_public(goal, await _current_amount(session, owner_id, user, goal.id))


@router.patch("/{goal_id}/sharing", response_model=GoalPublic)
async def update_goal_sharing(
    request: Request,
    goal_id: uuid.UUID,
    body: GoalSharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    goal.is_shared = body.is_shared
    goal.updated_at = utcnow()
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    await log_audit_event(
        session, "goal.updated", user_id=user.id, entity_type="goal", entity_id=goal.id,
        metadata={"fields": ["is_shared"], "is_shared": body.is_shared}, request=request,
    )
    owner_id = household_owner_id(user)
    return _to_public(goal, await _current_amount(session, owner_id, user, goal.id))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_goal(
    request: Request,
    goal_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
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
    await log_audit_event(
        session, "goal.deactivated", user_id=user.id, entity_type="goal", entity_id=goal_id, request=request,
    )


@router.post("/{goal_id}/add-funds", response_model=GoalPublic, status_code=status.HTTP_201_CREATED)
async def add_funds(
    request: Request,
    goal_id: uuid.UUID,
    body: AddFundsRequest,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> GoalPublic:
    goal = await _get_owned_active_or_404(session, user, goal_id)
    await validate_payment_method(session, user, body.payment_method_id)
    line_item = TransactionLineItemCreate(category_id=body.category_id, item_name=goal.name, amount=body.amount)
    await validate_line_items(session, user, TransactionType.SAVING_EXPENSE, body.amount, [line_item])

    owner_id = household_owner_id(user)
    transaction = Transaction(
        user_id=owner_id,
        created_by_user_id=user.id if user.id != owner_id else None,
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
    await log_audit_event(
        session, "transaction.created", user_id=user.id, entity_type="transaction", entity_id=transaction.id,
        metadata={"source": "goal_add_funds", "goal_id": str(goal.id), "total_amount": str(transaction.total_amount)},
        request=request,
    )

    return _to_public(goal, await _current_amount(session, owner_id, user, goal.id))
