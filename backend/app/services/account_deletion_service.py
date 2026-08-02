import logging
import uuid
from datetime import timedelta

from fastapi import HTTPException, Request, status
from sqlmodel import delete, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.audit import log_audit_event
from app.core.config import settings
from app.core.email import send_account_deletion_email
from app.core.security import generate_token, hash_token, verify_password
from app.models._common import utcnow
from app.models.audit_log import AuditLog
from app.models.budget import Budget
from app.models.cashback import CashbackRecord, CashbackRule
from app.models.goal import SavingsGoal
from app.models.net_worth import NetWorthAccount, NetWorthSnapshot
from app.models.payment_method import PaymentMethod
from app.models.recurring_bill import RecurringBill, RecurringBillPayment
from app.models.transaction import Transaction
from app.models.user import AccountDeletionToken, User, UserRole

logger = logging.getLogger("billwise.account_deletion")


async def request_account_deletion(
    session: AsyncSession, owner: User, password: str, request: Request | None
) -> None:
    """PRD §22.6 step 1: re-enter password, receive a time-limited confirm link.
    Mirrors the existing password-reset token pattern exactly."""
    if not verify_password(password, owner.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    token = generate_token()
    session.add(
        AccountDeletionToken(
            user_id=owner.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + timedelta(minutes=settings.account_deletion_token_expire_minutes),
        )
    )
    await session.commit()

    confirm_url = f"{settings.frontend_base_url}/account/delete-confirm?token={token}"
    send_account_deletion_email(owner.email, confirm_url)

    await log_audit_event(
        session, "account.deletion_requested", user_id=owner.id, entity_type="user", entity_id=owner.id, request=request
    )


async def confirm_account_deletion(
    session: AsyncSession, token: str, confirmation_email: str, request: Request | None
) -> User:
    """PRD §22.6 step 2: immediate soft-delete. confirmation_email is a
    typed-confirmation safety net against fat-fingering, not a security
    boundary — the token itself already proves email access."""
    token_hash = hash_token(token)
    record = (
        await session.exec(select(AccountDeletionToken).where(AccountDeletionToken.token_hash == token_hash))
    ).first()

    now = utcnow()
    if record is None or record.used_at is not None or record.expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired deletion token")

    owner = await session.get(User, record.user_id)
    if owner.email.lower() != confirmation_email.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Confirmation email does not match")

    record.used_at = now
    session.add(record)

    owner.is_active = False
    owner.hard_delete_at = now + timedelta(days=settings.account_deletion_grace_period_days)
    owner.updated_at = now
    session.add(owner)

    # Deleting the owner deletes the whole household — partner access ends
    # immediately too. Partners are only deactivated, never hard-deleted, so
    # they get no hard_delete_at of their own.
    partners = (
        await session.exec(select(User).where(User.invited_by_user_id == owner.id, User.role == UserRole.PARTNER))
    ).all()
    for partner in partners:
        partner.is_active = False
        partner.updated_at = now
        session.add(partner)

    await session.commit()
    await session.refresh(owner)

    await log_audit_event(
        session, "account.deletion_completed", user_id=owner.id, entity_type="user", entity_id=owner.id, request=request
    )
    return owner


async def cancel_account_deletion(session: AsyncSession, owner: User, request: Request | None) -> None:
    """PRD §22.6: only reachable before confirm — the account is still active at
    this point. Once soft-deleted, restoration is a support-assisted process, not
    self-service, so there is no cancel path after confirm."""
    now = utcnow()
    pending_tokens = (
        await session.exec(
            select(AccountDeletionToken).where(
                AccountDeletionToken.user_id == owner.id,
                AccountDeletionToken.used_at.is_(None),  # type: ignore[union-attr]
                AccountDeletionToken.expires_at >= now,
            )
        )
    ).all()
    for record in pending_tokens:
        record.used_at = now
        session.add(record)
    await session.commit()

    await log_audit_event(
        session, "account.deletion_cancelled", user_id=owner.id, entity_type="user", entity_id=owner.id, request=request
    )


async def hard_delete_expired_accounts(session: AsyncSession) -> list[uuid.UUID]:
    """PRD §22.6: purges an owner's financial data once the 30-day grace period
    has passed, and anonymizes that owner's own audit-log rows. Not an HTTP
    endpoint — run periodically by backend/scripts/hard_delete_expired_accounts.py.

    Deletion order respects FK dependencies that aren't all DB-cascaded:
    recurring_bill_payments (no cascade from either parent) must go before
    cashback_records/cashback_rules/recurring_bills/transactions/payment_methods;
    transactions (whose line_items and cashback_records do cascade) must go
    before savings_goals (Transaction.goal_id has no cascade) and before
    payment_methods (Transaction.payment_method_id has no cascade).
    net_worth_balances cascades from both net_worth_snapshots.id and
    net_worth_accounts.id — deleting snapshots first cascades away all
    balances, making the account-side cascade a harmless no-op. User rows
    themselves are never hard-deleted, only left deactivated.

    Only the owner's own AuditLog rows (user_id == owner_id) are anonymized
    here. A partner's audit rows (e.g. their own "transaction.created" event,
    logged under the partner's own user_id even though the transaction is
    stored under the owner's household) are deliberately left alone — the
    partner's own User row isn't being deleted, only the owner's household
    data is, so those rows' entity_id may end up pointing at a since-purged
    transaction. That's an accepted, documented consequence of retaining
    immutable audit history rather than deleting it: a stale entity_id
    reference, not a live security or privacy boundary (the row still
    correctly attributes the action to the still-existing partner account).
    """
    now = utcnow()
    owners = (
        await session.exec(select(User).where(User.is_active == False, User.hard_delete_at <= now))  # noqa: E712
    ).all()

    deleted_owner_ids: list[uuid.UUID] = []
    for owner in owners:
        owner_id = owner.id
        await session.exec(
            delete(RecurringBillPayment).where(
                RecurringBillPayment.recurring_bill_id.in_(  # type: ignore[union-attr]
                    select(RecurringBill.id).where(RecurringBill.user_id == owner_id)
                )
            )
        )
        await session.exec(delete(CashbackRecord).where(CashbackRecord.user_id == owner_id))
        await session.exec(delete(CashbackRule).where(CashbackRule.user_id == owner_id))
        await session.exec(delete(RecurringBill).where(RecurringBill.user_id == owner_id))
        await session.exec(delete(NetWorthSnapshot).where(NetWorthSnapshot.user_id == owner_id))
        await session.exec(delete(NetWorthAccount).where(NetWorthAccount.user_id == owner_id))
        await session.exec(delete(Transaction).where(Transaction.user_id == owner_id))
        await session.exec(delete(SavingsGoal).where(SavingsGoal.user_id == owner_id))
        await session.exec(delete(Budget).where(Budget.user_id == owner_id))
        await session.exec(delete(PaymentMethod).where(PaymentMethod.user_id == owner_id))

        await session.exec(
            update(AuditLog).where(AuditLog.user_id == owner_id).values(user_id=None, ip_address=None, user_agent=None)
        )

        await session.commit()
        logger.info("Hard-deleted household data for user_id=%s (grace period expired)", owner_id)
        deleted_owner_ids.append(owner_id)

    return deleted_owner_ids
