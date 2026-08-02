"""Ops entrypoint for PRD §22.6's 30-day account-deletion grace period.

Not wired to any scheduler in this repo — run daily via cron/systemd-timer/
platform scheduled task in production, e.g.:

    0 3 * * * cd /app && python -m scripts.hard_delete_expired_accounts

Idempotent: an account only matches the query once its grace period has
passed and its data has already been purged, it no longer matches (is_active
stays False, but its rows are gone, so a re-run finds nothing left to delete).
"""

import asyncio
import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine
from app.services.account_deletion_service import hard_delete_expired_accounts

logger = logging.getLogger("billwise.account_deletion")


async def main() -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        deleted_owner_ids = await hard_delete_expired_accounts(session)
    logger.info("Hard-delete run complete: %d account(s) purged", len(deleted_owner_ids))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
