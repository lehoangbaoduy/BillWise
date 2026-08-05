"""Ops entrypoint for PRD v2 §8.2's monthly budget auto-renewal.

Not wired to any scheduler in this repo — run on the 1st of each month via
cron/systemd-timer/platform scheduled task in production, e.g.:

    5 0 1 * * cd /app && python -m scripts.renew_monthly_budgets

Idempotent: renew_monthly_budgets skips any (owner, category, creator) that
already has a row for the target month, so a re-run (or a household opening
Budgets before this job has run) never double-creates or clobbers a row.
"""

import asyncio
import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine
from app.services.budget_renewal_service import renew_monthly_budgets

logger = logging.getLogger("billwise.budget_renewal")


async def main() -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        created_count = await renew_monthly_budgets(session)
    logger.info("Budget renewal run complete: %d row(s) created", created_count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
