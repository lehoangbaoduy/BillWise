import uuid
from datetime import date as date_type
from decimal import ROUND_HALF_UP, Decimal

from sqlmodel import and_, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.cashback import CashbackRecord, CashbackRecordStatus, CashbackRule
from app.models.transaction import Transaction, TransactionLineItem
from app.services.transaction_validation import EXPENSE_LIKE_TYPES, quantize

_CENTS = Decimal("0.01")


async def resolve_cashback_rate(
    session: AsyncSession,
    user_id: uuid.UUID,
    payment_method_id: uuid.UUID,
    category_id: uuid.UUID,
    on_date: date_type,
    merchant: str | None = None,
) -> Decimal:
    """PRD §17.2/§27.5: a category-specific rule (category_id set) takes
    precedence over the payment method's default rule (category_id null) when
    both are in effect for the same date. A merchant-specific rule (merchant
    set) outranks a category-specific one, on the same "more specific wins"
    principle -- "5% at Costco" should win over "2% on Shopping" even though
    both match. Among rules tied on specificity, the one with the latest
    start_date wins (§27.5: 'Rule changes mid-month → new rate applies going
    forward only'). No matching rule → 0 (§27.5: 'No rule → $0 estimated').
    Deliberately does NOT fall back to the payment method's own
    default_cashback_rate column -- that field is display-only (Wallets card
    visual); §27.5 is explicit that estimation looks at rules alone."""
    merchant_condition = CashbackRule.merchant.is_(None)  # type: ignore[union-attr]
    if merchant:
        merchant_condition = or_(merchant_condition, func.lower(CashbackRule.merchant) == merchant.strip().lower())
    statement = select(CashbackRule).where(
        CashbackRule.user_id == user_id,
        CashbackRule.payment_method_id == payment_method_id,
        CashbackRule.start_date <= on_date,
        or_(CashbackRule.end_date.is_(None), CashbackRule.end_date >= on_date),  # type: ignore[union-attr]
        or_(CashbackRule.category_id == category_id, CashbackRule.category_id.is_(None)),  # type: ignore[union-attr]
        merchant_condition,
    )
    candidates = (await session.exec(statement)).all()
    if not candidates:
        return Decimal("0")

    def specificity(rule: CashbackRule) -> int:
        return (2 if rule.merchant else 0) + (1 if rule.category_id == category_id else 0)

    best_specificity = max(specificity(r) for r in candidates)
    pool = [r for r in candidates if specificity(r) == best_specificity]
    best = max(pool, key=lambda r: r.start_date)
    return best.cashback_rate


async def record_cashback_for_line_items(
    session: AsyncSession, transaction: Transaction, line_items: list[TransactionLineItem]
) -> None:
    """Computed per line item (PRD §17.3), only for expense-like transactions
    (cashback is earned on spending, not Income/Adjustment). Called explicitly
    by each transaction-creation call site (manual entry, OCR confirm,
    recurring-bill mark-paid) rather than baked into the shared
    create_transaction_record, keeping that foundational helper feature-agnostic.
    Not wired into Goal add-funds, which doesn't go through
    create_transaction_record at all (pre-existing M4 architecture) —
    documented gap, not silently dropped.

    Scoped by transaction.user_id (always the household owner — see
    app.api.deps.household_owner_id) rather than the acting user, since cashback
    rules and payment methods are owner-managed; this also makes cashback
    resolve correctly for a partner-entered transaction without needing the
    acting user passed in at all.

    Accepted residual risk: this commits separately from the transaction it's
    computing cashback for (create_transaction_record already committed by the
    time callers reach this). A DB failure in the narrow window between the two
    commits would leave a transaction with no cashback records — self-correcting
    (worst case is a missing/zero estimate, not corrupted financial data) and
    not worth restructuring create_transaction_record's commit boundary across
    its three already-shipped call sites to close."""
    if transaction.transaction_type not in EXPENSE_LIKE_TYPES:
        return
    for item in line_items:
        rate = await resolve_cashback_rate(
            session,
            transaction.user_id,
            transaction.payment_method_id,
            item.category_id,
            transaction.date,
            merchant=transaction.merchant,
        )
        estimated = quantize(item.amount * rate / Decimal("100")) if rate else Decimal("0.00")
        session.add(
            CashbackRecord(
                user_id=transaction.user_id,
                transaction_id=transaction.id,
                line_item_id=item.id,
                payment_method_id=transaction.payment_method_id,
                category_id=item.category_id,
                estimated_amount=estimated,
                redeemed_amount=Decimal("0"),
                status=CashbackRecordStatus.ESTIMATED,
            )
        )
    await session.commit()
