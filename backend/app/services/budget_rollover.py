from sqlalchemy.exc import IntegrityError
from sqlmodel import and_, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.budget import Budget
from app.models.user import User, UserRole


async def ensure_budget_rollover(session: AsyncSession, user: User, month: int, year: int) -> None:
    """PRD §14.4: a new month with no budget rows yet auto-copies the most recent
    earlier month's amounts, as new independent rows (editing them never touches
    the source month's stored figures). Shared by the Budgets router (on list) and
    the Dashboard router (budget_status/category_breakdown need the same rolled-over
    view) — both can be called concurrently for the same user+period (e.g. the
    Budgets frontend page fetches both in parallel), so a second caller losing the
    existing-rows check to a race is expected and treated as a no-op rather than an
    error."""
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
        session.add(
            Budget(
                user_id=user.id,
                created_by_user_id=row.created_by_user_id,
                category_id=row.category_id,
                month=month,
                year=year,
                budget_amount=row.budget_amount,
                is_shared=row.is_shared,
            )
        )
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
        if constraint_name != "uq_budget_category_period":
            raise


async def ensure_budget_rollover_as_owner(session: AsyncSession, user: User, month: int, year: int) -> None:
    """Guards ensure_budget_rollover against ever running with a partner's
    own id — it writes Budget rows scoped to user.id, and a partner's id is
    never the household's data owner. A partner reads whatever rollover the
    owner already triggered rather than creating owner-domain rows
    misattributed to their own account. Called from the Dashboard and
    Budgets routers, which both now accept partner reads."""
    if user.role != UserRole.PARTNER:
        await ensure_budget_rollover(session, user, month, year)
