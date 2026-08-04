import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.db import get_session
from app.models._common import utcnow
from app.models.cashback import CashbackRecord, CashbackRule
from app.models.category import Category
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.cashback import (
    CashbackCardSummary,
    CashbackCategorySummary,
    CashbackRecordPublic,
    CashbackRecordUpdate,
    CashbackRuleCreate,
    CashbackRulePublic,
    CashbackRuleUpdate,
    CashbackSummary,
)
from app.services.item_visibility import user_can_access_item, visibility_condition
from app.services.transaction_validation import validate_payment_method

router = APIRouter(tags=["cashback"])


def _rule_to_public(rule: CashbackRule, payment_method_is_shared: bool) -> CashbackRulePublic:
    return CashbackRulePublic(
        id=rule.id,
        payment_method_id=rule.payment_method_id,
        category_id=rule.category_id,
        merchant=rule.merchant,
        cashback_rate=rule.cashback_rate,
        start_date=rule.start_date,
        end_date=rule.end_date,
        notes=rule.notes,
        is_shared=payment_method_is_shared,
    )


def _record_to_public(record: CashbackRecord, payment_method_is_shared: bool) -> CashbackRecordPublic:
    return CashbackRecordPublic(
        id=record.id,
        transaction_id=record.transaction_id,
        line_item_id=record.line_item_id,
        payment_method_id=record.payment_method_id,
        category_id=record.category_id,
        cashback_rule_id=record.cashback_rule_id,
        estimated_amount=record.estimated_amount,
        redeemed_amount=record.redeemed_amount,
        status=record.status,
        is_shared=payment_method_is_shared,
    )


async def _validate_category_if_set(session: AsyncSession, user: User, category_id: uuid.UUID | None) -> None:
    if category_id is None:
        return
    category = await session.get(Category, category_id)
    if category is None or category.user_id != household_owner_id(user) or not category.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")


async def _get_owned_rule_or_404(session: AsyncSession, user: User, rule_id: uuid.UUID) -> tuple[CashbackRule, PaymentMethod]:
    rule = await session.get(CashbackRule, rule_id)
    owner_id = household_owner_id(user)
    if rule is None or rule.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback rule not found")
    payment_method = await session.get(PaymentMethod, rule.payment_method_id)
    # A rule tied to a private wallet is invisible to anyone but that wallet's
    # creator -- same 404-not-403 reasoning as item_visibility elsewhere.
    if payment_method is None or not user_can_access_item(
        payment_method.is_shared, payment_method.created_by_user_id, owner_id, user
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback rule not found")
    return rule, payment_method


async def _get_owned_record_or_404(session: AsyncSession, user: User, record_id: uuid.UUID) -> tuple[CashbackRecord, PaymentMethod]:
    record = await session.get(CashbackRecord, record_id)
    owner_id = household_owner_id(user)
    if record is None or record.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback record not found")
    payment_method = await session.get(PaymentMethod, record.payment_method_id)
    if payment_method is None or not user_can_access_item(
        payment_method.is_shared, payment_method.created_by_user_id, owner_id, user
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback record not found")
    return record, payment_method


@router.get("/cashback-rules", response_model=list[CashbackRulePublic])
async def list_cashback_rules(
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[CashbackRulePublic]:
    """Not in PRD §25.9's literal endpoint list, but every other resource
    section (payment methods, categories, budgets, goals, recurring bills)
    has a GET list route and this one doesn't — without it, the PATCH/DELETE
    rule endpoints PRD §25.9 does list are unreachable from any UI, since
    there's no way to discover a rule's id. Added to match the app's
    established REST shape; a pure additive gap-fill, not a behavior change.

    Filtered by the linked payment method's visibility: a rule tied to a
    private wallet is invisible to everyone but that wallet's creator."""
    owner_id = household_owner_id(user)
    statement = (
        select(CashbackRule, PaymentMethod)
        .join(PaymentMethod, PaymentMethod.id == CashbackRule.payment_method_id)
        .where(CashbackRule.user_id == owner_id, visibility_condition(PaymentMethod, owner_id, user))
    )
    rows = (await session.exec(statement)).all()
    return [_rule_to_public(rule, payment_method.is_shared) for rule, payment_method in rows]


@router.post("/cashback-rules", response_model=CashbackRulePublic, status_code=status.HTTP_201_CREATED)
async def create_cashback_rule(
    body: CashbackRuleCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRulePublic:
    await validate_payment_method(session, user, body.payment_method_id)
    await _validate_category_if_set(session, user, body.category_id)
    payment_method = await session.get(PaymentMethod, body.payment_method_id)
    rule = CashbackRule(user_id=household_owner_id(user), **body.model_dump())
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return _rule_to_public(rule, payment_method.is_shared)


@router.patch("/cashback-rules/{rule_id}", response_model=CashbackRulePublic)
async def update_cashback_rule(
    rule_id: uuid.UUID,
    body: CashbackRuleUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRulePublic:
    rule, payment_method = await _get_owned_rule_or_404(session, user, rule_id)
    updates = body.model_dump(exclude_unset=True)
    if "category_id" in updates:
        await _validate_category_if_set(session, user, updates["category_id"])
    for field, value in updates.items():
        setattr(rule, field, value)
    rule.updated_at = utcnow()
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return _rule_to_public(rule, payment_method.is_shared)


@router.delete("/cashback-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cashback_rule(
    rule_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    rule, _payment_method = await _get_owned_rule_or_404(session, user, rule_id)
    await session.delete(rule)
    await session.commit()


@router.patch("/cashback-records/{record_id}", response_model=CashbackRecordPublic)
async def update_cashback_record(
    record_id: uuid.UUID,
    body: CashbackRecordUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRecordPublic:
    """PRD §17.3: manually overridable at the line-item level (records are
    always per line item) — setting estimated_amount here is the override
    mechanism, and it persists: nothing in this codebase recomputes an
    existing record after transaction edits that don't replace its line item
    (see recompute-on-edit note in transactions.py's update_transaction)."""
    record, payment_method = await _get_owned_record_or_404(session, user, record_id)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)
    record.updated_at = utcnow()
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return _record_to_public(record, payment_method.is_shared)


@router.get("/cashback", response_model=CashbackSummary)
async def get_cashback_summary(
    year: int = Query(ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackSummary:
    """PRD §17.4/§17.1: monthly (month set) or yearly (month omitted) earned,
    by card, by category, redeemed, unredeemed estimate. A single flexible
    endpoint per PRD §25.9's list (no separate /monthly or /yearly variants,
    unlike the Dashboard section). Filters by the linked transaction's date
    since CashbackRecord itself has no date column (PRD §23.12).

    Personalized per viewer, same rule as the Dashboard totals: shared-wallet
    cashback plus the viewer's own private-wallet cashback -- never someone
    else's private-wallet cashback (item_visibility.user_can_access_item)."""
    owner_id = household_owner_id(user)
    conditions = [
        CashbackRecord.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("year", Transaction.date) == year,
        visibility_condition(PaymentMethod, owner_id, user),
    ]
    if month is not None:
        conditions.append(extract("month", Transaction.date) == month)

    statement = (
        select(CashbackRecord, PaymentMethod.is_shared)
        .select_from(CashbackRecord)
        .join(Transaction, Transaction.id == CashbackRecord.transaction_id)
        .join(PaymentMethod, PaymentMethod.id == CashbackRecord.payment_method_id)
        .where(*conditions)
    )
    rows = (await session.exec(statement)).all()
    records = [record for record, _is_shared in rows]
    shared_by_record = {record.id: is_shared for record, is_shared in rows}

    payment_method_ids = {r.payment_method_id for r in records}
    category_ids = {r.category_id for r in records}
    payment_methods: dict[uuid.UUID, PaymentMethod] = {}
    if payment_method_ids:
        pm_rows = (await session.exec(select(PaymentMethod).where(PaymentMethod.id.in_(payment_method_ids)))).all()  # type: ignore[union-attr]
        payment_methods = {pm.id: pm for pm in pm_rows}
    categories: dict[uuid.UUID, Category] = {}
    if category_ids:
        cat_rows = (await session.exec(select(Category).where(Category.id.in_(category_ids)))).all()  # type: ignore[union-attr]
        categories = {c.id: c for c in cat_rows}

    by_card_totals: dict[uuid.UUID, dict[str, Decimal]] = {}
    by_category_totals: dict[uuid.UUID, dict[str, Decimal]] = {}
    total_estimated = Decimal("0")
    total_redeemed = Decimal("0")
    for record in records:
        total_estimated += record.estimated_amount
        total_redeemed += record.redeemed_amount

        card_bucket = by_card_totals.setdefault(record.payment_method_id, {"estimated": Decimal("0"), "redeemed": Decimal("0")})
        card_bucket["estimated"] += record.estimated_amount
        card_bucket["redeemed"] += record.redeemed_amount

        category_bucket = by_category_totals.setdefault(record.category_id, {"estimated": Decimal("0"), "redeemed": Decimal("0")})
        category_bucket["estimated"] += record.estimated_amount
        category_bucket["redeemed"] += record.redeemed_amount

    return CashbackSummary(
        year=year,
        month=month,
        total_estimated=total_estimated,
        total_redeemed=total_redeemed,
        total_unredeemed=max(total_estimated - total_redeemed, Decimal("0")),
        by_card=[
            CashbackCardSummary(
                payment_method_id=pm_id,
                name=payment_methods[pm_id].name if pm_id in payment_methods else "Unknown",
                estimated=totals["estimated"],
                redeemed=totals["redeemed"],
            )
            for pm_id, totals in by_card_totals.items()
        ],
        by_category=[
            CashbackCategorySummary(
                category_id=cat_id,
                name=categories[cat_id].name if cat_id in categories else "Unknown",
                estimated=totals["estimated"],
                redeemed=totals["redeemed"],
            )
            for cat_id, totals in by_category_totals.items()
        ],
        records=[_record_to_public(record, shared_by_record[record.id]) for record in records],
    )
