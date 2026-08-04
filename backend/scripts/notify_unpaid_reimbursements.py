"""Ops entrypoint for PRD v2 §7.4's end-of-month unpaid-reimbursement email nudge.

Not wired to any scheduler in this repo — run on/near the 1st of each month
via cron/systemd-timer/platform scheduled task in production, e.g.:

    5 0 1 * * cd /app && python -m scripts.notify_unpaid_reimbursements

Idempotent in the sense that mattered here isn't "never re-sends" — the
digest re-sends for any reimbursement that's still unpaid on a re-run within
the same month — but a re-run doesn't duplicate database writes, and a
reimbursement that got marked paid before the next run simply stops
appearing.
"""

import asyncio
import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import engine
from app.services.reimbursement_digest_service import send_unpaid_reimbursement_digest

logger = logging.getLogger("billwise.reimbursement_digest")


async def main() -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        sent_count = await send_unpaid_reimbursement_digest(session)
    logger.info("Unpaid-reimbursement digest run complete: %d email(s) sent", sent_count)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
