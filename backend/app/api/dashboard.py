"""Dashboard read endpoints (PRD §21.4: partner dashboards are filtered to
shared categories only; payment methods and net worth stay owner-only
regardless of sharing).

Two scoping conventions coexist here by design -- both derive
`owner_id = household_owner_id(user)` rather than using `user.id` directly,
since a co-owner (a PARTNER-role user granted require_owner_or_co_owner
access) has a different id than the household's data:
- Partner-visible helpers (sum_by_type, category_expense_spend, and the
  monthly/yearly/category-breakdown/cash-flow endpoints) additionally call
  apply_partner_transaction_visibility() to exclude private-category data
  for a plain (non-co-owner) partner.
- Owner-or-co-owner-only helpers (_payment_method_expense_spend,
  net_worth_dashboard, payment_method_breakdown) skip that visibility
  filtering entirely and must only ever be called from a
  `require_owner_or_co_owner`-gated endpoint.
A new helper should pick whichever convention matches its endpoint's auth
dependency, not mix the two.
"""

import uuid
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import case, extract, true
from sqlmodel import and_, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, is_owner_or_co_owner, require_household_member, require_owner_or_co_owner
from app.api.net_worth import load_balances_by_snapshot, to_snapshot_public
from app.core.config import settings
from app.core.db import get_session
from app.core.rate_limit import limiter
from app.models.budget import Budget
from app.models.category import Category
from app.models.net_worth import NetWorthSnapshot
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction, TransactionLineItem, TransactionType
from app.models.transaction_share import TransactionShare
from app.models.user import User
from app.schemas.dashboard import (
    BudgetStatusItem,
    CashFlow,
    CategoryBreakdownItem,
    CategorySpend,
    MonthlyOverview,
    MonthSpend,
    PaymentMethodBreakdownItem,
    PaymentMethodSpend,
    PreviousMonthComparison,
    TopCategory,
    TopPaymentMethod,
    YearlyOverview,
)
from app.schemas.net_worth import NetWorthDashboard
from app.services.item_visibility import effective_creator_id, visibility_condition
from app.services.partner_visibility import apply_partner_transaction_visibility, shared_category_ids_subquery


def _personal_visibility_condition(owner_id: uuid.UUID, user: User, viewer_is_owner_or_co_owner: bool):
    """Every household/category/type total in this file is personalized per
    viewer: shared-payment-method activity (visible to anyone) plus the
    viewer's own private-payment-method activity (invisible to everyone
    else). This is the Transaction-join equivalent of
    item_visibility.visibility_condition, applied via PaymentMethod.

    The private/shared *wallet* distinction only ever exists between an
    owner and a co-owner -- a plain (non-co-owner) partner can never be a
    payment method's creator (Wallet CRUD is require_owner_or_co_owner-
    gated), so this condition is a no-op for them; their visibility stays
    governed entirely by apply_partner_transaction_visibility's
    category-based rule, same as before this feature existed."""
    if not viewer_is_owner_or_co_owner:
        return true()
    return or_(
        PaymentMethod.is_shared == True,  # noqa: E712
        PaymentMethod.created_by_user_id == user.id,
        and_(PaymentMethod.created_by_user_id.is_(None), user.id == owner_id),
    )

def _split_share_subqueries(owner_id: uuid.UUID, user_id: uuid.UUID):
    """Correlated subqueries (against the enclosing query's Transaction row)
    used to prorate spend per PRD §7.5's true per-person split: how much of
    this transaction was given away in total, and how much (if any) this
    specific viewer was given."""
    total_shared_out = (
        select(func.coalesce(func.sum(TransactionShare.share_amount), 0))
        .where(TransactionShare.transaction_id == Transaction.id)
        .scalar_subquery()
    )
    viewer_share = (
        select(TransactionShare.share_amount)
        .where(TransactionShare.transaction_id == Transaction.id, TransactionShare.shared_with_user_id == user_id)
        .scalar_subquery()
    )
    effective_payer_id = func.coalesce(Transaction.created_by_user_id, owner_id)
    return effective_payer_id, total_shared_out, viewer_share


def _split_adjusted_total(owner_id: uuid.UUID, user_id: uuid.UUID):
    """Per-viewer net cost for a Transaction.total_amount-level sum: the
    payer's own net cost drops by whatever they split away, a named
    recipient sees only their prorated share instead of the pooled/
    visibility-based full amount, and anyone else (no share relationship to
    this transaction) is unaffected -- including transactions with no shares
    at all, where this is a no-op identity."""
    effective_payer_id, total_shared_out, viewer_share = _split_share_subqueries(owner_id, user_id)
    return func.round(
        case(
            (effective_payer_id == user_id, Transaction.total_amount - total_shared_out),
            (viewer_share.is_not(None), viewer_share),
            else_=Transaction.total_amount,
        ),
        2,
    )


def _split_adjusted_line_item(line_item_amount, owner_id: uuid.UUID, user_id: uuid.UUID):
    """Same rule as _split_adjusted_total, prorated across an individual line
    item (for category-level spend) proportional to its share of the
    transaction's total -- line items always reconcile to Transaction.total_amount
    (see transaction_validation's reconciliation check), so this proportion is exact."""
    effective_payer_id, total_shared_out, viewer_share = _split_share_subqueries(owner_id, user_id)
    return func.round(
        case(
            (
                effective_payer_id == user_id,
                line_item_amount * (Transaction.total_amount - total_shared_out) / Transaction.total_amount,
            ),
            (
                viewer_share.is_not(None),
                line_item_amount * viewer_share / Transaction.total_amount,
            ),
            else_=line_item_amount,
        ),
        2,
    )


router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_ZERO = Decimal("0")
_PERCENT_PLACES = Decimal("0.01")


def _pct(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    if denominator == 0:
        return None
    return ((numerator / denominator) * 100).quantize(_PERCENT_PLACES, rounding=ROUND_HALF_UP)


def previous_period(month: int, year: int) -> tuple[int, int]:
    return (12, year - 1) if month == 1 else (month - 1, year)


async def sum_by_type(
    session: AsyncSession, user: User, month: int, year: int, transaction_type: TransactionType
) -> Decimal:
    """Personalized per viewer -- shared-payment-method activity plus the
    viewer's own private-payment-method activity. See
    _personal_visibility_condition. For a solo owner with nothing marked
    shared, this is identical to today's household-wide total (everything is
    "their own"), so existing single-owner households see no change."""
    owner_id = household_owner_id(user)
    viewer_is_owner_or_co_owner = await is_owner_or_co_owner(user, session)
    conditions = [
        Transaction.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == transaction_type,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    statement = (
        select(func.coalesce(func.sum(_split_adjusted_total(owner_id, user.id)), 0))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*conditions)
    )
    return (await session.exec(statement)).one()


async def category_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
    """Personalized per viewer, same rule as sum_by_type -- see its docstring."""
    owner_id = household_owner_id(user)
    viewer_is_owner_or_co_owner = await is_owner_or_co_owner(user, session)
    conditions = [
        Transaction.user_id == owner_id,
        Category.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    statement = (
        select(
            Category.id,
            Category.name,
            Category.parent_category_id,
            func.sum(_split_adjusted_line_item(TransactionLineItem.amount, owner_id, user.id)),
        )
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*conditions)
        .group_by(Category.id, Category.name, Category.parent_category_id)
    )
    return (await session.exec(statement)).all()


async def _visible_budgets_by_category(
    session: AsyncSession, owner_id: uuid.UUID, user: User, month: int, year: int, viewer_is_owner_or_co_owner: bool
) -> dict[uuid.UUID, Budget]:
    """At most one budget per category, for this viewer: their own row (private
    or shared) if they have one, else a shared row someone else created. A
    category could in principle carry two simultaneous rows (the viewer's own
    private target plus a co-owner's shared target) -- picking one keeps the
    existing one-row-per-category UI shape rather than opening up a
    multi-budget-per-category display, which is out of scope for now.

    A plain (non-co-owner) partner was never part of the creator-based model
    (Budget CRUD is require_owner_or_co_owner-gated, so they can never be a
    budget's creator) -- their visibility stays the pre-existing rule: whichever
    categories are shared with them, regardless of a specific Budget row's own
    is_shared/created_by_user_id."""
    if not viewer_is_owner_or_co_owner:
        statement = select(Budget).where(
            Budget.user_id == owner_id,
            Budget.month == month,
            Budget.year == year,
            Budget.category_id.in_(shared_category_ids_subquery(owner_id)),
        )
        budgets = (await session.exec(statement)).all()
        by_category: dict[uuid.UUID, Budget] = {}
        for budget in budgets:
            existing = by_category.get(budget.category_id)
            if existing is None or (budget.is_shared and not existing.is_shared):
                by_category[budget.category_id] = budget
        return by_category

    statement = select(Budget).where(
        Budget.user_id == owner_id, Budget.month == month, Budget.year == year, visibility_condition(Budget, owner_id, user)
    )
    budgets = (await session.exec(statement)).all()
    by_category: dict[uuid.UUID, Budget] = {}
    for budget in budgets:
        existing = by_category.get(budget.category_id)
        is_own = effective_creator_id(budget.created_by_user_id, owner_id) == user.id
        if existing is None or is_own:
            by_category[budget.category_id] = budget
    return by_category


async def _payment_method_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
    """Owner-or-co-owner caller (payment_method_breakdown, top_payment_method).
    Each payment method's own total always includes every transaction against
    it regardless of who created those transactions (PRD §21.4: using a
    payment method in a transaction is unrestricted) -- what's scoped here is
    only *which payment methods this viewer can see at all*, via
    visibility_condition (their own private wallets plus any shared wallet)."""
    owner_id = household_owner_id(user)
    statement = (
        select(
            PaymentMethod.id,
            PaymentMethod.name,
            PaymentMethod.type,
            PaymentMethod.current_balance,
            func.sum(Transaction.total_amount),
            func.count(Transaction.id),
        )
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(
            Transaction.user_id == owner_id,
            PaymentMethod.user_id == owner_id,
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year,
            Transaction.transaction_type == TransactionType.EXPENSE,
            visibility_condition(PaymentMethod, owner_id, user),
        )
        .group_by(PaymentMethod.id, PaymentMethod.name, PaymentMethod.type, PaymentMethod.current_balance)
    )
    return (await session.exec(statement)).all()


@router.get("/monthly", response_model=MonthlyOverview)
# Not rate-limited like the other endpoints below — export_service.py calls
# this directly as a plain function (not over HTTP) to build report exports,
# and slowapi's decorator requires a real starlette Request object, which
# that direct-call path doesn't have. Still auth-gated as normal.
async def monthly_overview(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> MonthlyOverview:
    owner_id = household_owner_id(user)
    viewer_is_owner_or_co_owner = await is_owner_or_co_owner(user, session)
    total_income = await sum_by_type(session, user, month, year, TransactionType.INCOME)
    total_expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)

    category_rows = await category_expense_spend(session, user, month, year)
    top_category = None
    if category_rows:
        category_id, name, _parent_id, amount = max(category_rows, key=lambda row: row[3])
        top_category = TopCategory(category_id=category_id, name=name, amount=amount)

    # Payment methods stay owner-or-co-owner-only regardless of sharing (PRD
    # §21.4) — a plain partner's monthly overview never identifies which
    # payment method was used.
    top_payment_method = None
    if viewer_is_owner_or_co_owner:
        payment_method_rows = await _payment_method_expense_spend(session, user, month, year)
        if payment_method_rows:
            pm_id, name, _type, _balance, amount, _count = max(payment_method_rows, key=lambda row: row[4])
            top_payment_method = TopPaymentMethod(payment_method_id=pm_id, name=name, amount=amount)

    budgets = list(
        (await _visible_budgets_by_category(session, owner_id, user, month, year, viewer_is_owner_or_co_owner)).values()
    )
    spend_by_category = {row[0]: row[3] for row in category_rows}
    budget_category_ids = {budget.category_id for budget in budgets}
    category_name_by_id: dict[uuid.UUID, str] = {}
    if budget_category_ids:
        budget_categories = (
            await session.exec(
                select(Category).where(Category.id.in_(budget_category_ids), Category.user_id == owner_id)  # type: ignore[union-attr]
            )
        ).all()
        category_name_by_id = {category.id: category.name for category in budget_categories}
    budget_status = [
        BudgetStatusItem(
            category_id=budget.category_id,
            category_name=category_name_by_id.get(budget.category_id, ""),
            budget_amount=budget.budget_amount,
            actual_amount=spend_by_category.get(budget.category_id, _ZERO),
            percentage_used=_pct(spend_by_category.get(budget.category_id, _ZERO), budget.budget_amount),
            is_over_budget=spend_by_category.get(budget.category_id, _ZERO) > budget.budget_amount,
        )
        for budget in budgets
    ]

    previous_month, previous_year = previous_period(month, year)
    previous_total_expenses = await sum_by_type(session, user, previous_month, previous_year, TransactionType.EXPENSE)
    change_amount = total_expenses - previous_total_expenses
    comparison = PreviousMonthComparison(
        previous_month=previous_month,
        previous_year=previous_year,
        previous_total_expenses=previous_total_expenses,
        change_amount=change_amount,
        change_percentage=_pct(change_amount, previous_total_expenses),
    )

    return MonthlyOverview(
        month=month,
        year=year,
        total_income=total_income,
        total_expenses=total_expenses,
        net_cash_flow=total_income - total_expenses,
        top_category=top_category,
        top_payment_method=top_payment_method,
        budget_status=budget_status,
        comparison_vs_previous_month=comparison,
    )


@router.get("/yearly", response_model=YearlyOverview)
@limiter.limit(settings.read_rate_limit_window)
async def yearly_overview(
    request: Request,
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> YearlyOverview:
    owner_id = household_owner_id(user)
    viewer_is_owner_or_co_owner = await is_owner_or_co_owner(user, session)

    month_conditions = [
        Transaction.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(month_conditions, user, owner_id)
    month_statement = (
        select(extract("month", Transaction.date), func.sum(_split_adjusted_total(owner_id, user.id)))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*month_conditions)
        .group_by(extract("month", Transaction.date))
    )
    month_rows = (await session.exec(month_statement)).all()
    spend_by_month_map = {int(month_number): total for month_number, total in month_rows}
    spend_by_month = [MonthSpend(month=m, total=spend_by_month_map.get(m, _ZERO)) for m in range(1, 13)]
    total_yearly_spending = sum((entry.total for entry in spend_by_month), _ZERO)

    income_month_conditions = [
        Transaction.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.INCOME,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(income_month_conditions, user, owner_id)
    income_month_statement = (
        select(extract("month", Transaction.date), func.sum(Transaction.total_amount))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*income_month_conditions)
        .group_by(extract("month", Transaction.date))
    )
    income_month_rows = (await session.exec(income_month_statement)).all()
    income_by_month_map = {int(month_number): total for month_number, total in income_month_rows}
    income_by_month = [MonthSpend(month=m, total=income_by_month_map.get(m, _ZERO)) for m in range(1, 13)]

    category_conditions = [
        Transaction.user_id == owner_id,
        Category.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(category_conditions, user, owner_id)
    category_statement = (
        select(
            Category.id,
            Category.name,
            func.sum(_split_adjusted_line_item(TransactionLineItem.amount, owner_id, user.id)),
        )
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*category_conditions)
        .group_by(Category.id, Category.name)
    )
    spend_by_category = [
        CategorySpend(category_id=category_id, name=name, total=total)
        for category_id, name, total in (await session.exec(category_statement)).all()
    ]

    # Per-payment-method totals only need visibility scoping (which wallets this
    # viewer can see) -- each wallet's own total already includes every
    # transaction against it regardless of creator (PRD §21.4), same as
    # _payment_method_expense_spend above.
    spend_by_payment_method: list[PaymentMethodSpend] = []
    if viewer_is_owner_or_co_owner:
        pm_statement = (
            select(PaymentMethod.id, PaymentMethod.name, func.sum(Transaction.total_amount))
            .select_from(Transaction)
            .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
            .where(
                Transaction.user_id == owner_id,
                PaymentMethod.user_id == owner_id,
                extract("year", Transaction.date) == year,
                Transaction.transaction_type == TransactionType.EXPENSE,
                visibility_condition(PaymentMethod, owner_id, user),
            )
            .group_by(PaymentMethod.id, PaymentMethod.name)
        )
        spend_by_payment_method = [
            PaymentMethodSpend(payment_method_id=pm_id, name=name, total=total)
            for pm_id, name, total in (await session.exec(pm_statement)).all()
        ]

    average_month = (total_yearly_spending / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    highest_month = max(spend_by_month, key=lambda entry: entry.total)
    lowest_month = min(spend_by_month, key=lambda entry: entry.total)

    ytd_savings_conditions = [
        Transaction.user_id == owner_id,
        PaymentMethod.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.SAVING_EXPENSE,
        _personal_visibility_condition(owner_id, user, viewer_is_owner_or_co_owner),
    ]
    apply_partner_transaction_visibility(ytd_savings_conditions, user, owner_id)
    ytd_savings_statement = (
        select(func.coalesce(func.sum(Transaction.total_amount), 0))
        .select_from(Transaction)
        .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
        .where(*ytd_savings_conditions)
    )
    ytd_savings_total = (await session.exec(ytd_savings_statement)).one()

    return YearlyOverview(
        year=year,
        total_yearly_spending=total_yearly_spending,
        spend_by_month=spend_by_month,
        income_by_month=income_by_month,
        spend_by_category=spend_by_category,
        spend_by_payment_method=spend_by_payment_method,
        average_month=average_month,
        highest_month=highest_month,
        lowest_month=lowest_month,
        ytd_savings_total=ytd_savings_total,
    )


@router.get("/category-breakdown", response_model=list[CategoryBreakdownItem])
# Not rate-limited — also called directly by export_service.py (see
# monthly_overview's comment above).
async def category_breakdown(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> list[CategoryBreakdownItem]:
    owner_id = household_owner_id(user)
    viewer_is_owner_or_co_owner = await is_owner_or_co_owner(user, session)
    category_rows = await category_expense_spend(session, user, month, year)
    total_expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    spend_by_category = {row[0]: (row[1], row[2], row[3]) for row in category_rows}

    budget_by_category = await _visible_budgets_by_category(
        session, owner_id, user, month, year, viewer_is_owner_or_co_owner
    )

    zero_spend_budgeted_ids = set(budget_by_category) - set(spend_by_category)
    if zero_spend_budgeted_ids:
        zero_spend_categories = (
            await session.exec(
                select(Category).where(Category.id.in_(zero_spend_budgeted_ids), Category.user_id == owner_id)  # type: ignore[union-attr]
            )
        ).all()
        for category in zero_spend_categories:
            spend_by_category[category.id] = (category.name, category.parent_category_id, _ZERO)

    items = []
    for category_id, (name, parent_category_id, amount) in spend_by_category.items():
        budget = budget_by_category.get(category_id)
        items.append(
            CategoryBreakdownItem(
                category_id=category_id,
                name=name,
                parent_category_id=parent_category_id,
                amount=amount,
                percentage_of_total=_pct(amount, total_expenses) or _ZERO,
                budget_amount=budget.budget_amount if budget else None,
                budget_percentage_used=_pct(amount, budget.budget_amount) if budget else None,
                is_over_budget=bool(budget and amount > budget.budget_amount),
            )
        )
    return items


@router.get("/payment-method-breakdown", response_model=list[PaymentMethodBreakdownItem])
# Not rate-limited — also called directly by export_service.py (see
# monthly_overview's comment above).
async def payment_method_breakdown(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> list[PaymentMethodBreakdownItem]:
    rows = await _payment_method_expense_spend(session, user, month, year)
    items = []
    for pm_id, name, pm_type, current_balance, amount, count in rows:
        average = (amount / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if count else _ZERO
        items.append(
            PaymentMethodBreakdownItem(
                payment_method_id=pm_id,
                name=name,
                type=pm_type,
                amount=amount,
                transaction_count=count,
                average_transaction=average,
                current_balance=current_balance,
            )
        )
    return items


@router.get("/cash-flow", response_model=CashFlow)
@limiter.limit(settings.read_rate_limit_window)
async def cash_flow(
    request: Request,
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> CashFlow:
    income = await sum_by_type(session, user, month, year, TransactionType.INCOME)
    expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    return CashFlow(month=month, year=year, income=income, expenses=expenses, net=income - expenses)


@router.get("/net-worth", response_model=NetWorthDashboard)
# Not rate-limited — also called directly by export_service.py (see
# monthly_overview's comment above).
async def net_worth_dashboard(
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> NetWorthDashboard:
    snapshots = (
        await session.exec(
            select(NetWorthSnapshot)
            .where(NetWorthSnapshot.user_id == household_owner_id(user))
            .order_by(NetWorthSnapshot.snapshot_date)
        )
    ).all()
    if not snapshots:
        return NetWorthDashboard(
            current_net_worth=None,
            total_assets=None,
            total_liabilities=None,
            change_vs_previous=None,
            breakdown=[],
            history=[],
        )

    balances_by_snapshot = await load_balances_by_snapshot(session, [snapshot.id for snapshot in snapshots])
    history = [to_snapshot_public(snapshot, balances_by_snapshot[snapshot.id]) for snapshot in snapshots]

    latest = snapshots[-1]
    previous = snapshots[-2] if len(snapshots) > 1 else None

    return NetWorthDashboard(
        current_net_worth=latest.net_worth,
        total_assets=latest.total_assets,
        total_liabilities=latest.total_liabilities,
        change_vs_previous=(latest.net_worth - previous.net_worth) if previous else None,
        breakdown=balances_by_snapshot[latest.id],
        history=history,
    )
