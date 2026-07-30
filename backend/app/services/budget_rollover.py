from sqlmodel import and_, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.budget import Budget
from app.models.user import User


async def ensure_budget_rollover(session: AsyncSession, user: User, month: int, year: int) -> None:
    """PRD §14.4: a new month with no budget rows yet auto-copies the most recent
    earlier month's amounts, as new independent rows (editing them never touches
    the source month's stored figures). Shared by the Budgets router (on list) and
    the Dashboard router (budget_status needs the same rolled-over view)."""
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
