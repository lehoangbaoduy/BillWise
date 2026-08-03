"""Dashboard read endpoints (PRD §21.4: partner dashboards are filtered to
shared categories only; payment methods and net worth stay owner-only
regardless of sharing).

Two scoping conventions coexist here by design:
- Partner-visible helpers (sum_by_type, category_expense_spend, and the
  monthly/yearly/category-breakdown/cash-flow endpoints) accept `user`,
  derive `owner_id = household_owner_id(user)` internally, and call
  apply_partner_transaction_visibility() to exclude private-category data.
- Owner-only helpers (_payment_method_expense_spend, net_worth_dashboard,
  payment_method_breakdown) use `user.id` directly and must only ever be
  called from a `require_owner`-gated endpoint, where user.id IS the
  household owner's id.
A new helper should pick whichever convention matches its endpoint's auth
dependency, not mix the two.
"""

import uuid
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import extract
from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_household_member, require_owner
from app.api.net_worth import load_balances_by_snapshot, to_snapshot_public
from app.core.config import settings
from app.core.db import get_session
from app.core.rate_limit import limiter
from app.models.budget import Budget
from app.models.category import Category
from app.models.net_worth import NetWorthSnapshot
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction, TransactionLineItem, TransactionType
from app.models.user import User, UserRole
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
from app.services.budget_rollover import ensure_budget_rollover_as_owner
from app.services.partner_visibility import apply_partner_transaction_visibility, shared_category_ids_subquery

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_ZERO = Decimal("0")
_PERCENT_PLACES = Decimal("0.01")


def _pct(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    if denominator == 0:
        return None
    return ((numerator / denominator) * 100).quantize(_PERCENT_PLACES, rounding=ROUND_HALF_UP)


def previous_period(month: int, year: int) -> tuple[int, int]:
    return (12, year - 1) if month == 1 else (month - 1, year)


async def sum_by_type(session: AsyncSession, user: User, month: int, year: int, transaction_type: TransactionType) -> Decimal:
    owner_id = household_owner_id(user)
    conditions = [
        Transaction.user_id == owner_id,
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == transaction_type,
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    statement = select(func.coalesce(func.sum(Transaction.total_amount), 0)).where(*conditions)
    return (await session.exec(statement)).one()


async def category_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
    owner_id = household_owner_id(user)
    conditions = [
        Transaction.user_id == owner_id,
        Category.user_id == owner_id,
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    statement = (
        select(Category.id, Category.name, Category.parent_category_id, func.sum(TransactionLineItem.amount))
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .where(*conditions)
        .group_by(Category.id, Category.name, Category.parent_category_id)
    )
    return (await session.exec(statement)).all()


async def _payment_method_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
    """Owner-only caller (payment_method_breakdown) — no partner-visibility
    scoping needed since payment methods stay owner-only regardless of
    sharing (PRD §21.4)."""
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
            Transaction.user_id == user.id,
            PaymentMethod.user_id == user.id,
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year,
            Transaction.transaction_type == TransactionType.EXPENSE,
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
    total_income = await sum_by_type(session, user, month, year, TransactionType.INCOME)
    total_expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)

    category_rows = await category_expense_spend(session, user, month, year)
    top_category = None
    if category_rows:
        category_id, name, _parent_id, amount = max(category_rows, key=lambda row: row[3])
        top_category = TopCategory(category_id=category_id, name=name, amount=amount)

    # Payment methods stay owner-only regardless of sharing (PRD §21.4) — a
    # partner's monthly overview never identifies which payment method was used.
    top_payment_method = None
    if user.role != UserRole.PARTNER:
        payment_method_rows = await _payment_method_expense_spend(session, user, month, year)
        if payment_method_rows:
            pm_id, name, _type, _balance, amount, _count = max(payment_method_rows, key=lambda row: row[4])
            top_payment_method = TopPaymentMethod(payment_method_id=pm_id, name=name, amount=amount)

    await ensure_budget_rollover_as_owner(session, user, month, year)
    budget_conditions = [Budget.user_id == owner_id, Budget.month == month, Budget.year == year]
    if user.role == UserRole.PARTNER:
        budget_conditions.append(Budget.category_id.in_(shared_category_ids_subquery(owner_id)))  # type: ignore[union-attr]
    budgets = (await session.exec(select(Budget).where(*budget_conditions))).all()
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

    month_conditions = [
        Transaction.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
    ]
    apply_partner_transaction_visibility(month_conditions, user, owner_id)
    month_statement = (
        select(extract("month", Transaction.date), func.sum(Transaction.total_amount))
        .where(*month_conditions)
        .group_by(extract("month", Transaction.date))
    )
    month_rows = (await session.exec(month_statement)).all()
    spend_by_month_map = {int(month_number): total for month_number, total in month_rows}
    spend_by_month = [MonthSpend(month=m, total=spend_by_month_map.get(m, _ZERO)) for m in range(1, 13)]
    total_yearly_spending = sum((entry.total for entry in spend_by_month), _ZERO)

    category_conditions = [
        Transaction.user_id == owner_id,
        Category.user_id == owner_id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.EXPENSE,
    ]
    apply_partner_transaction_visibility(category_conditions, user, owner_id)
    category_statement = (
        select(Category.id, Category.name, func.sum(TransactionLineItem.amount))
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .where(*category_conditions)
        .group_by(Category.id, Category.name)
    )
    spend_by_category = [
        CategorySpend(category_id=category_id, name=name, total=total)
        for category_id, name, total in (await session.exec(category_statement)).all()
    ]

    # Payment methods stay owner-only regardless of sharing (PRD §21.4).
    spend_by_payment_method: list[PaymentMethodSpend] = []
    if user.role != UserRole.PARTNER:
        pm_statement = (
            select(PaymentMethod.id, PaymentMethod.name, func.sum(Transaction.total_amount))
            .select_from(Transaction)
            .join(PaymentMethod, PaymentMethod.id == Transaction.payment_method_id)
            .where(
                Transaction.user_id == user.id,
                PaymentMethod.user_id == user.id,
                extract("year", Transaction.date) == year,
                Transaction.transaction_type == TransactionType.EXPENSE,
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
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.SAVING_EXPENSE,
    ]
    apply_partner_transaction_visibility(ytd_savings_conditions, user, owner_id)
    ytd_savings_statement = select(func.coalesce(func.sum(Transaction.total_amount), 0)).where(*ytd_savings_conditions)
    ytd_savings_total = (await session.exec(ytd_savings_statement)).one()

    return YearlyOverview(
        year=year,
        total_yearly_spending=total_yearly_spending,
        spend_by_month=spend_by_month,
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
    category_rows = await category_expense_spend(session, user, month, year)
    total_expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    spend_by_category = {row[0]: (row[1], row[2], row[3]) for row in category_rows}

    await ensure_budget_rollover_as_owner(session, user, month, year)
    budget_conditions = [Budget.user_id == owner_id, Budget.month == month, Budget.year == year]
    if user.role == UserRole.PARTNER:
        budget_conditions.append(Budget.category_id.in_(shared_category_ids_subquery(owner_id)))  # type: ignore[union-attr]
    budgets = (await session.exec(select(Budget).where(*budget_conditions))).all()
    budget_by_category = {budget.category_id: budget for budget in budgets}

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
    user: User = Depends(require_owner),
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
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> NetWorthDashboard:
    snapshots = (
        await session.exec(
            select(NetWorthSnapshot).where(NetWorthSnapshot.user_id == user.id).order_by(NetWorthSnapshot.snapshot_date)
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
