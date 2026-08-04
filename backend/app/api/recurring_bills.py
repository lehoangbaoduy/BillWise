import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod
from app.models.recurring_bill import RecurringBill, RecurringBillPayment, RecurringBillPaymentStatus
from app.models.user import User
from app.schemas.recurring_bill import (
    MarkPaidRequest,
    RecurringBillCreate,
    RecurringBillPaymentPublic,
    RecurringBillPublic,
    RecurringBillSharingUpdate,
    RecurringBillUpdate,
)
from app.services.item_visibility import user_can_access_item, visibility_condition
from app.services.recurring_bill_service import ensure_recurring_bill_state, mark_bill_paid, resolve_card_payment_due_date
from app.services.transaction_validation import validate_payment_method

router = APIRouter(prefix="/recurring-bills", tags=["recurring-bills"])

_OPEN_STATUSES = {RecurringBillPaymentStatus.UPCOMING, RecurringBillPaymentStatus.OVERDUE}
_NOT_NULLABLE_UPDATE_FIELDS = {"payment_method_id", "category_id", "name", "amount", "frequency", "due_date"}


async def _validate_expense_category(session: AsyncSession, user: User, category_id: uuid.UUID) -> None:
    category = await session.get(Category, category_id)
    if category is None or category.user_id != household_owner_id(user) or not category.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")
    if category.category_type != CategoryType.EXPENSE:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Recurring bills require an expense category")


async def _get_owned_active_or_404(session: AsyncSession, user: User, bill_id: uuid.UUID) -> RecurringBill:
    bill = await session.get(RecurringBill, bill_id)
    owner_id = household_owner_id(user)
    if (
        bill is None
        or bill.user_id != owner_id
        or not bill.is_active
        or not user_can_access_item(bill.is_shared, bill.created_by_user_id, owner_id, user)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurring bill not found")
    return bill


async def _payment_method_is_shared(session: AsyncSession, payment_method_id: uuid.UUID) -> bool:
    payment_method = await session.get(PaymentMethod, payment_method_id)
    return bool(payment_method and payment_method.is_shared)


async def _load_payments(session: AsyncSession, bill_id: uuid.UUID) -> list[RecurringBillPayment]:
    statement = select(RecurringBillPayment).where(RecurringBillPayment.recurring_bill_id == bill_id).order_by(RecurringBillPayment.due_date)
    return (await session.exec(statement)).all()


def _to_public(bill: RecurringBill, payments: list[RecurringBillPayment]) -> RecurringBillPublic:
    open_payments = [p for p in payments if p.status in _OPEN_STATUSES]
    current = min(open_payments, key=lambda p: p.due_date) if open_payments else (payments[-1] if payments else None)
    return RecurringBillPublic(
        id=bill.id,
        payment_method_id=bill.payment_method_id,
        category_id=bill.category_id,
        name=bill.name,
        amount=bill.amount,
        frequency=bill.frequency,
        due_date=bill.due_date,
        auto_create_transaction=bill.auto_create_transaction,
        reminder_enabled=bill.reminder_enabled,
        is_shared=bill.is_shared,
        is_active=bill.is_active,
        notes=bill.notes,
        current_period=RecurringBillPaymentPublic.model_validate(current) if current else None,
        payments=[RecurringBillPaymentPublic.model_validate(p) for p in payments],
    )


@router.get("", response_model=list[RecurringBillPublic])
async def list_recurring_bills(
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[RecurringBillPublic]:
    owner_id = household_owner_id(user)
    await ensure_recurring_bill_state(session, owner_id)
    bills = (
        await session.exec(
            select(RecurringBill).where(
                RecurringBill.user_id == owner_id,
                RecurringBill.is_active == True,  # noqa: E712
                visibility_condition(RecurringBill, owner_id, user),
            )
        )
    ).all()
    if not bills:
        return []

    bill_ids = [bill.id for bill in bills]
    all_payments = (
        await session.exec(select(RecurringBillPayment).where(RecurringBillPayment.recurring_bill_id.in_(bill_ids)))  # type: ignore[union-attr]
    ).all()
    payments_by_bill: dict[uuid.UUID, list[RecurringBillPayment]] = {bill_id: [] for bill_id in bill_ids}
    for payment in sorted(all_payments, key=lambda p: p.due_date):
        payments_by_bill[payment.recurring_bill_id].append(payment)

    return [_to_public(bill, payments_by_bill[bill.id]) for bill in bills]


@router.post("", response_model=RecurringBillPublic, status_code=status.HTTP_201_CREATED)
async def create_recurring_bill(
    request: Request,
    body: RecurringBillCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> RecurringBillPublic:
    await validate_payment_method(session, user, body.payment_method_id)
    await _validate_expense_category(session, user, body.category_id)

    due_date = body.due_date
    payment_method = await session.get(PaymentMethod, body.payment_method_id)
    if due_date is None:
        due_date = resolve_card_payment_due_date(payment_method, date.today())
    if due_date is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="due_date is required unless the payment method has a due day or statement day configured",
        )

    owner_id = household_owner_id(user)
    # A bill tied to a private wallet can't be shared -- nobody else can even
    # see the wallet it's paid from, so a "shared" bill referencing it would
    # be a shared item nobody but the creator could actually act on.
    is_shared = body.is_shared and bool(payment_method and payment_method.is_shared)
    bill = RecurringBill(
        user_id=owner_id,
        created_by_user_id=user.id if user.id != owner_id else None,
        payment_method_id=body.payment_method_id,
        category_id=body.category_id,
        name=body.name,
        amount=body.amount,
        frequency=body.frequency,
        due_date=due_date,
        auto_create_transaction=body.auto_create_transaction,
        reminder_enabled=body.reminder_enabled,
        is_shared=is_shared,
        notes=body.notes,
    )
    session.add(bill)
    await session.flush()
    session.add(RecurringBillPayment(recurring_bill_id=bill.id, due_date=due_date, amount_due=body.amount, status=RecurringBillPaymentStatus.UPCOMING))
    await session.commit()
    await session.refresh(bill)
    await log_audit_event(
        session, "recurring_bill.created", user_id=user.id, entity_type="recurring_bill", entity_id=bill.id,
        metadata={"name": bill.name}, request=request,
    )

    payments = await _load_payments(session, bill.id)
    return _to_public(bill, payments)


@router.patch("/{bill_id}", response_model=RecurringBillPublic)
async def update_recurring_bill(
    bill_id: uuid.UUID,
    body: RecurringBillUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> RecurringBillPublic:
    bill = await _get_owned_active_or_404(session, user, bill_id)

    updates = body.model_dump(exclude_unset=True)
    nulled_fields = _NOT_NULLABLE_UPDATE_FIELDS & {field for field, value in updates.items() if value is None}
    if nulled_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"These fields cannot be cleared: {', '.join(sorted(nulled_fields))}",
        )

    if "payment_method_id" in updates:
        await validate_payment_method(session, user, updates["payment_method_id"])
    if "category_id" in updates:
        await _validate_expense_category(session, user, updates["category_id"])

    for field, value in updates.items():
        setattr(bill, field, value)
    bill.updated_at = utcnow()

    # Re-derive sharing whenever the effective payment method could have
    # changed -- a bill now paid from a private wallet can't stay shared.
    if "payment_method_id" in updates and not await _payment_method_is_shared(session, bill.payment_method_id):
        bill.is_shared = False
    session.add(bill)

    # mark-paid reads period.amount_due/due_date (not the bill's template
    # fields) and the detail view displays current_period.due_date, so an
    # edited amount/due_date is otherwise invisible until the *next* period
    # generates. Sync the still-open (unpaid) period to match.
    if "amount" in updates or "due_date" in updates:
        open_payments = (
            await session.exec(
                select(RecurringBillPayment)
                .where(RecurringBillPayment.recurring_bill_id == bill.id, RecurringBillPayment.status.in_(list(_OPEN_STATUSES)))  # type: ignore[attr-defined]
                .order_by(RecurringBillPayment.due_date)
            )
        ).all()
        if open_payments:
            period = open_payments[0]
            if "amount" in updates:
                period.amount_due = bill.amount
            if "due_date" in updates:
                period.due_date = bill.due_date
                period.status = (
                    RecurringBillPaymentStatus.OVERDUE if bill.due_date < date.today() else RecurringBillPaymentStatus.UPCOMING
                )
            session.add(period)

    await session.commit()
    await session.refresh(bill)

    payments = await _load_payments(session, bill.id)
    return _to_public(bill, payments)


@router.patch("/{bill_id}/sharing", response_model=RecurringBillPublic)
async def update_recurring_bill_sharing(
    request: Request,
    bill_id: uuid.UUID,
    body: RecurringBillSharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> RecurringBillPublic:
    bill = await _get_owned_active_or_404(session, user, bill_id)
    if body.is_shared and not await _payment_method_is_shared(session, bill.payment_method_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Can't share a bill paid from a private wallet -- share the wallet first, or switch this bill to a shared one",
        )
    bill.is_shared = body.is_shared
    bill.updated_at = utcnow()
    session.add(bill)
    await session.commit()
    await session.refresh(bill)
    await log_audit_event(
        session, "recurring_bill.updated", user_id=user.id, entity_type="recurring_bill", entity_id=bill.id,
        metadata={"fields": ["is_shared"], "is_shared": body.is_shared}, request=request,
    )
    payments = await _load_payments(session, bill.id)
    return _to_public(bill, payments)


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_recurring_bill(
    bill_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    bill = await _get_owned_active_or_404(session, user, bill_id)
    bill.is_active = False
    bill.updated_at = utcnow()
    session.add(bill)
    await session.commit()


@router.post("/{bill_id}/mark-paid", response_model=RecurringBillPublic)
async def mark_recurring_bill_paid(
    request: Request,
    bill_id: uuid.UUID,
    body: MarkPaidRequest,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> RecurringBillPublic:
    bill = await _get_owned_active_or_404(session, user, bill_id)
    await mark_bill_paid(session, user, bill, body.paid_date or date.today(), body.amount_paid, request)

    payments = await _load_payments(session, bill.id)
    return _to_public(bill, payments)
