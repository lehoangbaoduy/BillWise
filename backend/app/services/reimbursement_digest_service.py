"""PRD v2 §7.4: end-of-month email nudge for unpaid Reimbursement transactions.

Runs via the scheduled job in scripts/notify_unpaid_reimbursements.py (cron
precedent: scripts/hard_delete_expired_accounts.py), not triggered by any
in-app request. There is no pre-existing recurring-bill-reminder email digest
in this codebase to reuse (recurring-bill reminders are in-app only, computed
live by notification_service.py) -- this reuses the same transactional-email
abstraction as verification/reset/invite emails (app.core.email) instead.
"""

from datetime import date
from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.email import get_email_sender
from app.models.transaction import Transaction, TransactionType
from app.models.user import User


def _closed_month(today: date) -> tuple[int, int]:
    return (12, today.year - 1) if today.month == 1 else (today.month - 1, today.year)


async def send_unpaid_reimbursement_digest(session: AsyncSession, today: date | None = None) -> int:
    today = today or date.today()
    month, year = _closed_month(today)

    transactions = (
        await session.exec(
            select(Transaction).where(
                Transaction.transaction_type == TransactionType.REIMBURSEMENT,
                Transaction.reimbursement_status == "unpaid",
            )
        )
    ).all()
    closed_month_transactions = [t for t in transactions if t.date.month == month and t.date.year == year]
    if not closed_month_transactions:
        return 0

    by_owner: dict = {}
    for transaction in closed_month_transactions:
        by_owner.setdefault(transaction.user_id, []).append(transaction)

    owners = (await session.exec(select(User).where(User.id.in_(by_owner.keys())))).all()  # type: ignore[union-attr]
    email_by_owner_id = {owner.id: owner.email for owner in owners}

    sender = get_email_sender()
    sent_count = 0
    for owner_id, owner_transactions in by_owner.items():
        to_email = email_by_owner_id.get(owner_id)
        if not to_email:
            continue
        total = sum((t.total_amount for t in owner_transactions), Decimal("0"))
        lines = "\n".join(f"- {t.merchant}: {t.total_amount} on {t.date}" for t in owner_transactions)
        sender.send(
            to=to_email,
            subject="Unpaid reimbursements from last month",
            body=(
                f"You have {len(owner_transactions)} unpaid reimbursement(s) totaling "
                f"{total} from last month:\n\n{lines}"
            ),
        )
        sent_count += 1
    return sent_count
