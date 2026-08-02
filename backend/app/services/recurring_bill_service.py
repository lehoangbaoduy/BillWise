import calendar
import uuid
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.payment_method import PaymentMethod
from app.models.recurring_bill import RecurringBill, RecurringBillPayment, RecurringBillPaymentStatus, RecurringFrequency
from app.models.transaction import Transaction, TransactionSource, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionLineItemCreate
from app.services.cashback_service import record_cashback_for_line_items
from app.services.transaction_validation import create_transaction_record, load_line_items

_TERMINAL_STATUSES = {RecurringBillPaymentStatus.PAID, RecurringBillPaymentStatus.SKIPPED}
_OPEN_STATUSES = {RecurringBillPaymentStatus.UPCOMING, RecurringBillPaymentStatus.OVERDUE}


def _add_months(source: date, months: int) -> date:
    month_index = source.month - 1 + months
    year = source.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_due_date(frequency: RecurringFrequency, from_date: date) -> date | None:
    """PRD §16.2/§16.3. Custom-frequency bills have no interval to compute a next
    date from (the §23.9 schema has no interval field for 'Custom') — they never
    auto-generate; the owner rolls the bill forward manually by editing due_date."""
    if frequency == RecurringFrequency.WEEKLY:
        return from_date + timedelta(days=7)
    if frequency == RecurringFrequency.BIWEEKLY:
        return from_date + timedelta(days=14)
    if frequency == RecurringFrequency.MONTHLY:
        return _add_months(from_date, 1)
    if frequency == RecurringFrequency.QUARTERLY:
        return _add_months(from_date, 3)
    if frequency == RecurringFrequency.YEARLY:
        return _add_months(from_date, 12)
    return None


def resolve_card_payment_due_date(payment_method: PaymentMethod, today: date) -> date | None:
    """PRD §16.5 Card Payment Bills: when the client omits due_date and the linked
    payment method has a statement/due day configured, auto-populate the next
    occurrence of that day-of-month. Prefers due_day_optional (the actual payment
    due day) over statement_day_optional when both are set."""
    day = payment_method.due_day_optional or payment_method.statement_day_optional
    if day is None:
        return None
    clamped_day = min(day, calendar.monthrange(today.year, today.month)[1])
    candidate = date(today.year, today.month, clamped_day)
    if candidate < today:
        candidate = _add_months(candidate, 1)
        clamped_day = min(day, calendar.monthrange(candidate.year, candidate.month)[1])
        candidate = date(candidate.year, candidate.month, clamped_day)
    return candidate


async def ensure_recurring_bill_state(session: AsyncSession, user_id: uuid.UUID, today: date | None = None) -> None:
    """Lazy reconciliation, same pattern as ensure_budget_rollover: flips
    due-passed 'upcoming' periods to 'overdue', and generates the next period for
    any active, non-custom bill whose latest period has already been resolved
    (paid/skipped). Called at the top of GET /recurring-bills and again after
    mark-paid so the response is always current."""
    today = today or date.today()
    bills = (
        await session.exec(select(RecurringBill).where(RecurringBill.user_id == user_id, RecurringBill.is_active == True))  # noqa: E712
    ).all()
    if not bills:
        return

    bill_ids = [b.id for b in bills]
    payments = (
        await session.exec(select(RecurringBillPayment).where(RecurringBillPayment.recurring_bill_id.in_(bill_ids)))  # type: ignore[union-attr]
    ).all()

    by_bill: dict[uuid.UUID, list[RecurringBillPayment]] = {}
    for payment in payments:
        by_bill.setdefault(payment.recurring_bill_id, []).append(payment)
        if payment.status == RecurringBillPaymentStatus.UPCOMING and payment.due_date < today:
            payment.status = RecurringBillPaymentStatus.OVERDUE
            session.add(payment)

    for bill in bills:
        bill_payments = by_bill.get(bill.id, [])
        if not bill_payments:
            continue
        latest = max(bill_payments, key=lambda p: p.due_date)
        if latest.status not in _TERMINAL_STATUSES:
            continue
        due = next_due_date(bill.frequency, latest.due_date)
        if due is None:
            continue
        next_status = RecurringBillPaymentStatus.OVERDUE if due < today else RecurringBillPaymentStatus.UPCOMING
        session.add(RecurringBillPayment(recurring_bill_id=bill.id, due_date=due, amount_due=bill.amount, status=next_status))

    await session.commit()


async def mark_bill_paid(
    session: AsyncSession,
    user: User,
    bill: RecurringBill,
    paid_date: date,
    amount_paid: Decimal | None,
) -> tuple[RecurringBillPayment, Transaction | None]:
    """PRD §25.8 POST /recurring-bills/{id}/mark-paid. Targets the bill's earliest
    non-terminal period (upcoming or overdue) since the endpoint is parameterized
    by bill id, not period id. Optionally creates a real Transaction via the
    shared create_transaction_record service when the bill's auto_create_transaction
    flag is set, matching the DRY pattern established for OCR confirm and goal
    add-funds."""
    open_payments = (
        await session.exec(
            select(RecurringBillPayment)
            .where(RecurringBillPayment.recurring_bill_id == bill.id, RecurringBillPayment.status.in_(list(_OPEN_STATUSES)))  # type: ignore[attr-defined]
            .order_by(RecurringBillPayment.due_date)
        )
    ).all()
    if not open_payments:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No unpaid period for this bill")
    period = open_payments[0]
    amount = amount_paid if amount_paid is not None else period.amount_due

    transaction = None
    if bill.auto_create_transaction:
        body = TransactionCreate(
            payment_method_id=bill.payment_method_id,
            date=paid_date,
            merchant=bill.name,
            total_amount=amount,
            transaction_type=TransactionType.EXPENSE,
            line_items=[TransactionLineItemCreate(category_id=bill.category_id, item_name=bill.name, amount=amount)],
        )
        transaction, _ = await create_transaction_record(session, user, body, TransactionSource.RECURRING_BILL)
        period.transaction_id = transaction.id
        line_items = await load_line_items(session, transaction.id)
        await record_cashback_for_line_items(session, transaction, line_items)

    period.status = RecurringBillPaymentStatus.PAID
    period.paid_date = paid_date
    session.add(period)
    await session.commit()
    await session.refresh(period)

    # ensure_recurring_bill_state only inserts new future periods — it never
    # touches this now-paid period, so no further refresh is needed.
    await ensure_recurring_bill_state(session, user.id, today=date.today())
    return period, transaction
