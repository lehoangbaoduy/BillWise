import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_household_member, require_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User, UserRole
from app.schemas.budget import BudgetCreate, BudgetPublic, BudgetUpdate
from app.services.budget_rollover import ensure_budget_rollover_as_owner
from app.services.partner_visibility import shared_category_ids_subquery

router = APIRouter(prefix="/budgets", tags=["budgets"])


async def _validate_category(session: AsyncSession, user: User, category_id: uuid.UUID) -> None:
    category = await session.get(Category, category_id)
    if (
        category is None
        or category.user_id != user.id
        or not category.is_active
        or category.category_type != CategoryType.EXPENSE
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")


async def _get_owned_or_404(session: AsyncSession, user: User, budget_id: uuid.UUID) -> Budget:
    budget = await session.get(Budget, budget_id)
    if budget is None or budget.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.get("", response_model=list[BudgetPublic])
async def list_budgets(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> list[Budget]:
    owner_id = household_owner_id(user)
    await ensure_budget_rollover_as_owner(session, user, month, year)
    conditions = [Budget.user_id == owner_id, Budget.month == month, Budget.year == year]
    if user.role == UserRole.PARTNER:
        conditions.append(Budget.category_id.in_(shared_category_ids_subquery(owner_id)))  # type: ignore[union-attr]
    statement = select(Budget).where(and_(*conditions))
    return (await session.exec(statement)).all()


@router.post("", response_model=BudgetPublic, status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: Request,
    body: BudgetCreate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> Budget:
    await _validate_category(session, user, body.category_id)

    existing = (
        await session.exec(
            select(Budget).where(
                Budget.user_id == user.id,
                Budget.category_id == body.category_id,
                Budget.month == body.month,
                Budget.year == body.year,
            )
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A budget already exists for this category and month",
        )

    budget = Budget(user_id=user.id, **body.model_dump())
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
    user: User = Depends(require_owner),
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


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    request: Request,
    budget_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    budget = await _get_owned_or_404(session, user, budget_id)
    await session.delete(budget)
    await session.commit()
    await log_audit_event(
        session, "budget.deleted", user_id=user.id, entity_type="budget", entity_id=budget_id, request=request,
    )
