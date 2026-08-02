import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
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
from app.services.transaction_validation import validate_payment_method

router = APIRouter(tags=["cashback"])


async def _validate_category_if_set(session: AsyncSession, user: User, category_id: uuid.UUID | None) -> None:
    if category_id is None:
        return
    category = await session.get(Category, category_id)
    if category is None or category.user_id != user.id or not category.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid category")


async def _get_owned_rule_or_404(session: AsyncSession, user: User, rule_id: uuid.UUID) -> CashbackRule:
    rule = await session.get(CashbackRule, rule_id)
    if rule is None or rule.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback rule not found")
    return rule


async def _get_owned_record_or_404(session: AsyncSession, user: User, record_id: uuid.UUID) -> CashbackRecord:
    record = await session.get(CashbackRecord, record_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashback record not found")
    return record


@router.get("/cashback-rules", response_model=list[CashbackRulePublic])
async def list_cashback_rules(
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[CashbackRule]:
    """Not in PRD §25.9's literal endpoint list, but every other resource
    section (payment methods, categories, budgets, goals, recurring bills)
    has a GET list route and this one doesn't — without it, the PATCH/DELETE
    rule endpoints PRD §25.9 does list are unreachable from any UI, since
    there's no way to discover a rule's id. Added to match the app's
    established REST shape; a pure additive gap-fill, not a behavior change."""
    rules = (await session.exec(select(CashbackRule).where(CashbackRule.user_id == user.id))).all()
    return rules


@router.post("/cashback-rules", response_model=CashbackRulePublic, status_code=status.HTTP_201_CREATED)
async def create_cashback_rule(
    body: CashbackRuleCreate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRule:
    await validate_payment_method(session, user, body.payment_method_id)
    await _validate_category_if_set(session, user, body.category_id)
    rule = CashbackRule(user_id=user.id, **body.model_dump())
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.patch("/cashback-rules/{rule_id}", response_model=CashbackRulePublic)
async def update_cashback_rule(
    rule_id: uuid.UUID,
    body: CashbackRuleUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRule:
    rule = await _get_owned_rule_or_404(session, user, rule_id)
    updates = body.model_dump(exclude_unset=True)
    if "category_id" in updates:
        await _validate_category_if_set(session, user, updates["category_id"])
    for field, value in updates.items():
        setattr(rule, field, value)
    rule.updated_at = utcnow()
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


@router.delete("/cashback-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cashback_rule(
    rule_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    rule = await _get_owned_rule_or_404(session, user, rule_id)
    await session.delete(rule)
    await session.commit()


@router.patch("/cashback-records/{record_id}", response_model=CashbackRecordPublic)
async def update_cashback_record(
    record_id: uuid.UUID,
    body: CashbackRecordUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackRecord:
    """PRD §17.3: manually overridable at the line-item level (records are
    always per line item) — setting estimated_amount here is the override
    mechanism, and it persists: nothing in this codebase recomputes an
    existing record after transaction edits that don't replace its line item
    (see recompute-on-edit note in transactions.py's update_transaction)."""
    record = await _get_owned_record_or_404(session, user, record_id)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)
    record.updated_at = utcnow()
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


@router.get("/cashback", response_model=CashbackSummary)
async def get_cashback_summary(
    year: int = Query(ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> CashbackSummary:
    """PRD §17.4/§17.1: monthly (month set) or yearly (month omitted) earned,
    by card, by category, redeemed, unredeemed estimate. A single flexible
    endpoint per PRD §25.9's list (no separate /monthly or /yearly variants,
    unlike the Dashboard section). Filters by the linked transaction's date
    since CashbackRecord itself has no date column (PRD §23.12)."""
    conditions = [CashbackRecord.user_id == user.id, extract("year", Transaction.date) == year]
    if month is not None:
        conditions.append(extract("month", Transaction.date) == month)

    statement = select(CashbackRecord).join(Transaction, Transaction.id == CashbackRecord.transaction_id).where(*conditions)
    records = (await session.exec(statement)).all()

    payment_method_ids = {r.payment_method_id for r in records}
    category_ids = {r.category_id for r in records}
    payment_methods: dict[uuid.UUID, PaymentMethod] = {}
    if payment_method_ids:
        rows = (await session.exec(select(PaymentMethod).where(PaymentMethod.id.in_(payment_method_ids)))).all()  # type: ignore[union-attr]
        payment_methods = {pm.id: pm for pm in rows}
    categories: dict[uuid.UUID, Category] = {}
    if category_ids:
        rows = (await session.exec(select(Category).where(Category.id.in_(category_ids)))).all()  # type: ignore[union-attr]
        categories = {c.id: c for c in rows}

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
        records=[CashbackRecordPublic.model_validate(record) for record in records],
    )
