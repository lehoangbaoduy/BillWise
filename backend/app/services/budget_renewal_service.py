from datetime import date
from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.budget import Budget
from app.models._common import utcnow

_ZERO = Decimal("0")


async def renew_monthly_budgets(session: AsyncSession, today: date | None = None) -> int:
    """PRD v2 §8.2: scheduled replacement for the old lazy/reactive rollover
    (ensure_budget_rollover, removed). Run on the 1st of each month (see
    scripts/renew_monthly_budgets.py): creates a new budget row for every
    (owner, category, creator) that had a budget the prior month, with
    budget_amount reset to $0 -- supersedes original PRD §14.4's copy-forward
    behavior. The user re-enters each category's target for the new month,
    but doesn't have to manually re-create the rows/categories themselves.

    Idempotent by construction (skips any key that already has a row this
    month), so a re-run -- or a household opening Budgets before this job has
    run on the 1st -- never double-creates or clobbers a row."""
    today = today or utcnow().date()
    month, year = today.month, today.year
    previous_month, previous_year = (12, year - 1) if month == 1 else (month - 1, year)

    previous_rows = (
        await session.exec(select(Budget).where(Budget.month == previous_month, Budget.year == previous_year))
    ).all()
    if not previous_rows:
        return 0

    existing_rows = (await session.exec(select(Budget).where(Budget.month == month, Budget.year == year))).all()
    existing_keys = {(row.user_id, row.category_id, row.created_by_user_id) for row in existing_rows}

    created = 0
    for row in previous_rows:
        key = (row.user_id, row.category_id, row.created_by_user_id)
        if key in existing_keys:
            continue
        session.add(
            Budget(
                user_id=row.user_id,
                created_by_user_id=row.created_by_user_id,
                category_id=row.category_id,
                month=month,
                year=year,
                budget_amount=_ZERO,
                is_shared=row.is_shared,
            )
        )
        existing_keys.add(key)
        created += 1

    await session.commit()
    return created
