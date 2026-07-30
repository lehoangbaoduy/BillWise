import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import and_, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetPublic, BudgetUpdate

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


async def _rollover_if_needed(session: AsyncSession, user: User, month: int, year: int) -> None:
    """PRD §14.4: a new month with no budget rows yet auto-copies the most recent
    earlier month's amounts, as new independent rows (editing them never touches
    the source month's stored figures)."""
    existing = (
        await session.exec(select(Budget).where(Budget.user_id == user.id, Budget.month == month, Budget.year == year))
    ).first()
    if existing is not None:
        return

    earlier_condition = or_(Budget.year < year, and_(Budget.year == year, Budget.month < month))
    candidates = (await session.exec(select(Budget).where(Budget.user_id == user.id, earlier_condition))).all()
    if not candidates:
        return
    source_period = max((b.year, b.month) for b in candidates)
    source_rows = [b for b in candidates if (b.year, b.month) == source_period]

    for row in source_rows:
        session.add(Budget(user_id=user.id, category_id=row.category_id, month=month, year=year, budget_amount=row.budget_amount))
    await session.commit()


@router.get("", response_model=list[BudgetPublic])
async def list_budgets(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[Budget]:
    await _rollover_if_needed(session, user, month, year)
    statement = select(Budget).where(and_(Budget.user_id == user.id, Budget.month == month, Budget.year == year))
    return (await session.exec(statement)).all()


@router.post("", response_model=BudgetPublic, status_code=status.HTTP_201_CREATED)
async def create_budget(
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
    return budget


@router.patch("/{budget_id}", response_model=BudgetPublic)
async def update_budget(
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
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    budget = await _get_owned_or_404(session, user, budget_id)
    await session.delete(budget)
    await session.commit()
