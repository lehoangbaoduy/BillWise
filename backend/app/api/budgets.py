import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetPublic, BudgetSharingUpdate, BudgetUpdate
from app.services.item_visibility import effective_creator_id, user_can_access_item, visibility_condition

router = APIRouter(prefix="/budgets", tags=["budgets"])


async def _validate_category(session: AsyncSession, user: User, category_id: uuid.UUID) -> None:
    category = await session.get(Category, category_id)
    if (
        category is None
        or category.user_id != household_owner_id(user)
        or not category.is_active
        or category.category_type != CategoryType.EXPENSE
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")


async def _get_owned_or_404(session: AsyncSession, user: User, budget_id: uuid.UUID) -> Budget:
    budget = await session.get(Budget, budget_id)
    owner_id = household_owner_id(user)
    if (
        budget is None
        or budget.user_id != owner_id
        or not user_can_access_item(budget.is_shared, budget.created_by_user_id, owner_id, user)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.get("", response_model=list[BudgetPublic])
async def list_budgets(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[Budget]:
    owner_id = household_owner_id(user)
    statement = select(Budget).where(
        Budget.user_id == owner_id,
        Budget.month == month,
        Budget.year == year,
        visibility_condition(Budget, owner_id, user),
    )
    return (await session.exec(statement)).all()


@router.post("", response_model=BudgetPublic, status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: Request,
    body: BudgetCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Budget:
    await _validate_category(session, user, body.category_id)
    owner_id = household_owner_id(user)

    # A category can carry one budget target per creator -- an owner and a
    # co-owner may each set their own independent target for the same
    # category/month, so the duplicate check is scoped by creator too.
    existing = (
        await session.exec(
            select(Budget).where(
                Budget.user_id == owner_id,
                Budget.category_id == body.category_id,
                Budget.month == body.month,
                Budget.year == body.year,
                Budget.created_by_user_id == (user.id if user.id != owner_id else None),
            )
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A budget already exists for this category and month",
        )

    budget = Budget(
        user_id=owner_id,
        created_by_user_id=user.id if user.id != owner_id else None,
        **body.model_dump(),
    )
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    await log_audit_event(
        session, "budget.created", user_id=user.id, entity_type="budget", entity_id=budget.id,
        metadata={"category_id": str(budget.category_id), "budget_amount": str(budget.budget_amount)}, request=request,
    )
    return budget


@router.patch("/{budget_id}", response_model=BudgetPublic)
async def update_budget(
    request: Request,
    budget_id: uuid.UUID,
    body: BudgetUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Budget:
    budget = await _get_owned_or_404(session, user, budget_id)
    budget.budget_amount = body.budget_amount
    budget.updated_at = utcnow()
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    await log_audit_event(
        session, "budget.updated", user_id=user.id, entity_type="budget", entity_id=budget.id,
        metadata={"budget_amount": str(budget.budget_amount)}, request=request,
    )
    return budget


@router.patch("/{budget_id}/sharing", response_model=BudgetPublic)
async def update_budget_sharing(
    request: Request,
    budget_id: uuid.UUID,
    body: BudgetSharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Budget:
    budget = await _get_owned_or_404(session, user, budget_id)
    owner_id = household_owner_id(user)
    if user.id != effective_creator_id(budget.created_by_user_id, owner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can change this budget's sharing"
        )
    budget.is_shared = body.is_shared
    budget.updated_at = utcnow()
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    await log_audit_event(
        session, "budget.updated", user_id=user.id, entity_type="budget", entity_id=budget.id,
        metadata={"fields": ["is_shared"], "is_shared": body.is_shared}, request=request,
    )
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    request: Request,
    budget_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    budget = await _get_owned_or_404(session, user, budget_id)
    await session.delete(budget)
    await session.commit()
    await log_audit_event(
        session, "budget.deleted", user_id=user.id, entity_type="budget", entity_id=budget_id, request=request,
    )
