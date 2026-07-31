import uuid
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract
from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.db import get_session
from app.models.budget import Budget
from app.models.category import Category
from app.models.payment_method import PaymentMethod
from app.models.transaction import Transaction, TransactionLineItem, TransactionType
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
from app.services.budget_rollover import ensure_budget_rollover

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_ZERO = Decimal("0")
_PERCENT_PLACES = Decimal("0.01")


def _pct(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    if denominator == 0:
        return None
    return ((numerator / denominator) * 100).quantize(_PERCENT_PLACES, rounding=ROUND_HALF_UP)


def _previous_period(month: int, year: int) -> tuple[int, int]:
    return (12, year - 1) if month == 1 else (month - 1, year)


async def _sum_by_type(session: AsyncSession, user: User, month: int, year: int, transaction_type: TransactionType) -> Decimal:
    statement = select(func.coalesce(func.sum(Transaction.total_amount), 0)).where(
        Transaction.user_id == user.id,
        extract("month", Transaction.date) == month,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == transaction_type,
    )
    return (await session.exec(statement)).one()


async def _category_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
    statement = (
        select(Category.id, Category.name, Category.parent_category_id, func.sum(TransactionLineItem.amount))
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .where(
            Transaction.user_id == user.id,
            Category.user_id == user.id,
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year,
            Transaction.transaction_type == TransactionType.EXPENSE,
        )
        .group_by(Category.id, Category.name, Category.parent_category_id)
    )
    return (await session.exec(statement)).all()


async def _payment_method_expense_spend(session: AsyncSession, user: User, month: int, year: int) -> list[tuple]:
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
async def monthly_overview(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> MonthlyOverview:
    total_income = await _sum_by_type(session, user, month, year, TransactionType.INCOME)
    total_expenses = await _sum_by_type(session, user, month, year, TransactionType.EXPENSE)

    category_rows = await _category_expense_spend(session, user, month, year)
    top_category = None
    if category_rows:
        category_id, name, _parent_id, amount = max(category_rows, key=lambda row: row[3])
        top_category = TopCategory(category_id=category_id, name=name, amount=amount)

    payment_method_rows = await _payment_method_expense_spend(session, user, month, year)
    top_payment_method = None
    if payment_method_rows:
        pm_id, name, _type, _balance, amount, _count = max(payment_method_rows, key=lambda row: row[4])
        top_payment_method = TopPaymentMethod(payment_method_id=pm_id, name=name, amount=amount)

    await ensure_budget_rollover(session, user, month, year)
    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == user.id, Budget.month == month, Budget.year == year))
    ).all()
    spend_by_category = {row[0]: row[3] for row in category_rows}
    budget_category_ids = {budget.category_id for budget in budgets}
    category_name_by_id: dict[uuid.UUID, str] = {}
    if budget_category_ids:
        budget_categories = (
            await session.exec(
                select(Category).where(Category.id.in_(budget_category_ids), Category.user_id == user.id)  # type: ignore[union-attr]
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

    previous_month, previous_year = _previous_period(month, year)
    previous_total_expenses = await _sum_by_type(session, user, previous_month, previous_year, TransactionType.EXPENSE)
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
async def yearly_overview(
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> YearlyOverview:
    month_statement = (
        select(extract("month", Transaction.date), func.sum(Transaction.total_amount))
        .where(
            Transaction.user_id == user.id,
            extract("year", Transaction.date) == year,
            Transaction.transaction_type == TransactionType.EXPENSE,
        )
        .group_by(extract("month", Transaction.date))
    )
    month_rows = (await session.exec(month_statement)).all()
    spend_by_month_map = {int(month_number): total for month_number, total in month_rows}
    spend_by_month = [MonthSpend(month=m, total=spend_by_month_map.get(m, _ZERO)) for m in range(1, 13)]
    total_yearly_spending = sum((entry.total for entry in spend_by_month), _ZERO)

    category_statement = (
        select(Category.id, Category.name, func.sum(TransactionLineItem.amount))
        .select_from(TransactionLineItem)
        .join(Transaction, Transaction.id == TransactionLineItem.transaction_id)
        .join(Category, Category.id == TransactionLineItem.category_id)
        .where(
            Transaction.user_id == user.id,
            Category.user_id == user.id,
            extract("year", Transaction.date) == year,
            Transaction.transaction_type == TransactionType.EXPENSE,
        )
        .group_by(Category.id, Category.name)
    )
    spend_by_category = [
        CategorySpend(category_id=category_id, name=name, total=total)
        for category_id, name, total in (await session.exec(category_statement)).all()
    ]

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

    ytd_savings_statement = select(func.coalesce(func.sum(Transaction.total_amount), 0)).where(
        Transaction.user_id == user.id,
        extract("year", Transaction.date) == year,
        Transaction.transaction_type == TransactionType.SAVING_EXPENSE,
    )
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
async def category_breakdown(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[CategoryBreakdownItem]:
    category_rows = await _category_expense_spend(session, user, month, year)
    total_expenses = await _sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    spend_by_category = {row[0]: (row[1], row[2], row[3]) for row in category_rows}

    await ensure_budget_rollover(session, user, month, year)
    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == user.id, Budget.month == month, Budget.year == year))
    ).all()
    budget_by_category = {budget.category_id: budget for budget in budgets}

    zero_spend_budgeted_ids = set(budget_by_category) - set(spend_by_category)
    if zero_spend_budgeted_ids:
        zero_spend_categories = (
            await session.exec(
                select(Category).where(Category.id.in_(zero_spend_budgeted_ids), Category.user_id == user.id)  # type: ignore[union-attr]
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
async def cash_flow(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> CashFlow:
    income = await _sum_by_type(session, user, month, year, TransactionType.INCOME)
    expenses = await _sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    return CashFlow(month=month, year=year, income=income, expenses=expenses, net=income - expenses)
