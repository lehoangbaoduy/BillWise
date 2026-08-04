"""Gathers backend-computed aggregates for AI Insight generation (PRD §19.3/§29.3:
only computed totals/trends are sent to the AI, never raw transaction rows).
Reuses existing dashboard/cashback/goals aggregation logic directly as plain
async function calls rather than duplicating queries."""

from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.cashback import get_cashback_summary
from app.api.dashboard import category_expense_spend, previous_period, sum_by_type
from app.api.deps import household_owner_id
from app.api.goals import list_goals
from app.models.budget import Budget
from app.models.category import Category
from app.models.recurring_bill import RecurringBill, RecurringFrequency
from app.models.transaction import TransactionType
from app.models.user import User

_TREND_MONTHS = 3


def _decimal_to_number(value: Decimal) -> float:
    return float(value)


async def _monthly_expense_trend(session: AsyncSession, user: User, month: int, year: int) -> list[dict]:
    # Sequential queries (one per month) rather than a single grouped query —
    # this whole gather runs at most once per user per day (see the 24h cache
    # in api/ai_insights.py), so three small queries add negligible latency
    # and keep this consistent with sum_by_type's per-month signature.
    trend = []
    cursor_month, cursor_year = month, year
    for _ in range(_TREND_MONTHS):
        total = await sum_by_type(session, user, cursor_month, cursor_year, TransactionType.EXPENSE)
        trend.append({"month": cursor_month, "year": cursor_year, "total": _decimal_to_number(total)})
        cursor_month, cursor_year = previous_period(cursor_month, cursor_year)
    return list(reversed(trend))


async def _budget_status(session: AsyncSession, user: User, month: int, year: int, spend_by_category: dict) -> list[dict]:
    budgets = (
        await session.exec(
            select(Budget).where(Budget.user_id == household_owner_id(user), Budget.month == month, Budget.year == year)
        )
    ).all()
    if not budgets:
        return []
    category_ids = {budget.category_id for budget in budgets}
    categories = (await session.exec(select(Category).where(Category.id.in_(category_ids)))).all()  # type: ignore[union-attr]
    name_by_id = {category.id: category.name for category in categories}
    return [
        {
            "category_name": name_by_id.get(budget.category_id, ""),
            "budget_amount": _decimal_to_number(budget.budget_amount),
            "actual_amount": _decimal_to_number(spend_by_category.get(budget.category_id, Decimal("0"))),
            "is_over_budget": spend_by_category.get(budget.category_id, Decimal("0")) > budget.budget_amount,
        }
        for budget in budgets
    ]


async def _recurring_bill_summary(session: AsyncSession, user: User, monthly_expenses: Decimal) -> dict:
    bills = (
        await session.exec(
            select(RecurringBill).where(
                RecurringBill.user_id == household_owner_id(user), RecurringBill.is_active == True  # noqa: E712
            )
        )
    ).all()
    # Only monthly-frequency bills are comparable to a single month's total
    # expenses — weekly/quarterly/yearly amounts aren't the same unit, so they're
    # listed for context but excluded from the "share of monthly spend" ratio.
    monthly_total = sum((bill.amount for bill in bills if bill.frequency == RecurringFrequency.MONTHLY), Decimal("0"))
    share_pct = float((monthly_total / monthly_expenses) * 100) if monthly_expenses > 0 else None
    return {
        "monthly_frequency_total": _decimal_to_number(monthly_total),
        "share_of_monthly_expenses_pct": share_pct,
        "bills": [
            {"name": bill.name, "amount": _decimal_to_number(bill.amount), "frequency": bill.frequency.value} for bill in bills
        ],
    }


async def gather_insight_inputs(session: AsyncSession, user: User, month: int, year: int) -> dict:
    # Sequential rather than gathered/parallelized: this runs at most once per
    # user per day (see api/ai_insights.py's 24h cache), all queries share one
    # AsyncSession (SQLAlchemy async sessions aren't safe for concurrent use
    # anyway), and the dataset per query is small — not worth the complexity.
    previous_month, previous_year = previous_period(month, year)

    current_income = await sum_by_type(session, user, month, year, TransactionType.INCOME)
    current_expenses = await sum_by_type(session, user, month, year, TransactionType.EXPENSE)
    previous_income = await sum_by_type(session, user, previous_month, previous_year, TransactionType.INCOME)
    previous_expenses = await sum_by_type(session, user, previous_month, previous_year, TransactionType.EXPENSE)

    current_category_rows = await category_expense_spend(session, user, month, year)
    previous_category_rows = await category_expense_spend(session, user, previous_month, previous_year)
    spend_by_category = {row[0]: row[3] for row in current_category_rows}

    budgets = await _budget_status(session, user, month, year, spend_by_category)
    trend = await _monthly_expense_trend(session, user, month, year)
    recurring = await _recurring_bill_summary(session, user, current_expenses)
    cashback = await get_cashback_summary(year=year, month=month, user=user, session=session)
    goals = await list_goals(user=user, session=session)

    return {
        "period": {"month": month, "year": year},
        "income_expense": {
            "current": {
                "income": _decimal_to_number(current_income),
                "expenses": _decimal_to_number(current_expenses),
                "net": _decimal_to_number(current_income - current_expenses),
            },
            "previous": {
                "income": _decimal_to_number(previous_income),
                "expenses": _decimal_to_number(previous_expenses),
                "net": _decimal_to_number(previous_income - previous_expenses),
            },
        },
        "category_spend_current": [{"name": row[1], "amount": _decimal_to_number(row[3])} for row in current_category_rows],
        "category_spend_previous": [{"name": row[1], "amount": _decimal_to_number(row[3])} for row in previous_category_rows],
        "monthly_expense_trend": trend,
        "budgets": budgets,
        "cashback": {
            "total_estimated": _decimal_to_number(cashback.total_estimated),
            "total_redeemed": _decimal_to_number(cashback.total_redeemed),
            "by_card": [
                {"name": card.name, "estimated": _decimal_to_number(card.estimated)} for card in cashback.by_card
            ],
        },
        "recurring_bills": recurring,
        "goals": [
            {
                "name": goal.name,
                "target_amount": _decimal_to_number(goal.target_amount),
                "current_amount": _decimal_to_number(goal.current_amount),
                "progress_pct": _decimal_to_number((goal.current_amount / goal.target_amount) * 100)
                if goal.target_amount > 0
                else None,
            }
            for goal in goals
        ],
    }
