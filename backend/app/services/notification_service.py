"""PRD §24.15 scopes notifications to bill reminders, AI insights, and partner
activity; the user additionally required a category budget-threshold alert as
a mandatory, non-negotiable notification type. All notification types here are
computed live on each request rather than persisted, consistent with this
codebase's other dashboard-style read endpoints (app/api/dashboard.py) —
there's no user-facing "mark as read" concept yet, so a materialized table
would just be a cache with no invalidation story.
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dashboard import category_expense_spend
from app.api.deps import household_owner_id
from app.models._common import utcnow
from app.models.acknowledged_notification import AcknowledgedNotification
from app.models.ai_insight import AIInsight
from app.models.budget import Budget
from app.models.category import Category
from app.models.goal import SavingsGoal
from app.models.recurring_bill import RecurringBill, RecurringBillPayment, RecurringBillPaymentStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.notification import NotificationItem
from app.services.budget_rollover import ensure_budget_rollover_as_owner
from app.services.partner_visibility import apply_partner_transaction_visibility, shared_category_ids_subquery
from app.services.recurring_bill_service import ensure_recurring_bill_state

_ZERO = Decimal("0")
_NEAR_LIMIT_PERCENT = Decimal("90")
_DUE_SOON_WINDOW = timedelta(days=3)
_DUPLICATE_WINDOW = timedelta(days=14)
_SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


async def _budget_notifications(session: AsyncSession, user: User, owner_id, today: date) -> list[NotificationItem]:
    month, year = today.month, today.year
    await ensure_budget_rollover_as_owner(session, user, month, year)
    spend_by_category = {row[0]: row[3] for row in await category_expense_spend(session, user, month, year)}

    budget_conditions = [Budget.user_id == owner_id, Budget.month == month, Budget.year == year]
    if user.role == UserRole.PARTNER:
        budget_conditions.append(Budget.category_id.in_(shared_category_ids_subquery(owner_id)))  # type: ignore[union-attr]
    budgets = (await session.exec(select(Budget).where(*budget_conditions))).all()
    if not budgets:
        return []

    category_ids = {budget.category_id for budget in budgets}
    categories = (await session.exec(select(Category).where(Category.id.in_(category_ids)))).all()  # type: ignore[union-attr]
    name_by_id = {category.id: category.name for category in categories}

    items: list[NotificationItem] = []
    for budget in budgets:
        if budget.budget_amount <= 0:
            continue
        spend = spend_by_category.get(budget.category_id, _ZERO)
        name = name_by_id.get(budget.category_id, "")
        percentage_used = (spend / budget.budget_amount) * 100
        if spend > budget.budget_amount:
            items.append(
                NotificationItem(
                    key=f"budget_exceeded:{budget.category_id}:{year}-{month:02d}",
                    type="budget_exceeded",
                    severity="critical",
                    title=f"{name} is over budget",
                    message=f"You've spent {spend} of your {budget.budget_amount} budget for {name} this month.",
                    category_id=budget.category_id,
                )
            )
        elif percentage_used >= _NEAR_LIMIT_PERCENT:
            items.append(
                NotificationItem(
                    key=f"budget_near_limit:{budget.category_id}:{year}-{month:02d}",
                    type="budget_near_limit",
                    severity="warning",
                    title=f"{name} is close to its budget limit",
                    message=f"You've used {percentage_used:.0f}% of your {budget.budget_amount} budget for {name} this month.",
                    category_id=budget.category_id,
                )
            )
    return items


async def _recurring_bill_notifications(session: AsyncSession, user: User, owner_id, today: date) -> list[NotificationItem]:
    # Recurring bills stay owner-only regardless of sharing (PRD §21.4).
    if user.role == UserRole.PARTNER:
        return []

    await ensure_recurring_bill_state(session, owner_id, today=today)
    statement = (
        select(RecurringBillPayment, RecurringBill)
        .join(RecurringBill, RecurringBill.id == RecurringBillPayment.recurring_bill_id)
        .where(
            RecurringBill.user_id == owner_id,
            RecurringBill.is_active == True,  # noqa: E712
            RecurringBill.reminder_enabled == True,  # noqa: E712
            RecurringBillPayment.status.in_(  # type: ignore[union-attr]
                [RecurringBillPaymentStatus.OVERDUE, RecurringBillPaymentStatus.UPCOMING]
            ),
            RecurringBillPayment.due_date <= today + _DUE_SOON_WINDOW,
        )
    )
    rows = (await session.exec(statement)).all()

    items: list[NotificationItem] = []
    for payment, bill in rows:
        if payment.status == RecurringBillPaymentStatus.OVERDUE:
            items.append(
                NotificationItem(
                    key=f"bill_overdue:{bill.id}:{payment.due_date.isoformat()}",
                    type="recurring_bill_overdue",
                    severity="critical",
                    title=f"{bill.name} is overdue",
                    message=f"{bill.name} (${payment.amount_due}) was due on {payment.due_date} and hasn't been paid.",
                    entity_id=bill.id,
                )
            )
        else:
            items.append(
                NotificationItem(
                    key=f"bill_due_soon:{bill.id}:{payment.due_date.isoformat()}",
                    type="recurring_bill_due_soon",
                    severity="warning",
                    title=f"{bill.name} is due soon",
                    message=f"{bill.name} (${payment.amount_due}) is due on {payment.due_date}.",
                    entity_id=bill.id,
                )
            )
    return items


async def _goal_notifications(session: AsyncSession, user: User, owner_id, today: date) -> list[NotificationItem]:
    conditions = [
        SavingsGoal.user_id == owner_id,
        SavingsGoal.is_active == True,  # noqa: E712
        SavingsGoal.target_date.is_not(None),  # type: ignore[union-attr]
        SavingsGoal.target_date < today,
    ]
    if user.role == UserRole.PARTNER:
        conditions.append(SavingsGoal.is_shared == True)  # noqa: E712
    goals = (await session.exec(select(SavingsGoal).where(*conditions))).all()
    if not goals:
        return []

    goal_ids = [goal.id for goal in goals]
    amount_rows = (
        await session.exec(
            select(Transaction.goal_id, func.sum(Transaction.total_amount))
            .where(Transaction.goal_id.in_(goal_ids))  # type: ignore[union-attr]
            .group_by(Transaction.goal_id)
        )
    ).all()
    current_amount_by_id = {goal_id: total for goal_id, total in amount_rows}

    items: list[NotificationItem] = []
    for goal in goals:
        current_amount = current_amount_by_id.get(goal.id, _ZERO)
        if current_amount >= goal.target_amount:
            continue
        items.append(
            NotificationItem(
                key=f"goal_target_date_passed:{goal.id}:{goal.target_date.isoformat()}",
                type="goal_target_date_passed",
                severity="warning",
                title=f"{goal.name} missed its target date",
                message=f"{goal.name} was due {goal.target_date} but is only at {current_amount} of {goal.target_amount}.",
                entity_id=goal.id,
            )
        )
    return items


async def _ai_insight_notifications(session: AsyncSession, user: User, owner_id) -> list[NotificationItem]:
    # AI Insights are owner-only (app/api/ai_insights.py uses require_owner).
    if user.role == UserRole.PARTNER:
        return []

    statement = (
        select(AIInsight)
        .where(AIInsight.user_id == owner_id, AIInsight.is_dismissed == False)  # noqa: E712
        .order_by(AIInsight.generated_at.desc())
    )
    insights = (await session.exec(statement)).all()
    return [
        NotificationItem(
            key=f"ai_insight:{insight.id}",
            type="ai_insight",
            severity="info",
            title="New AI insight",
            message=insight.message,
            entity_id=insight.id,
        )
        for insight in insights
    ]


async def _duplicate_transaction_notifications(
    session: AsyncSession, user: User, owner_id, today: date
) -> list[NotificationItem]:
    """Mirrors the same merchant/date/amount/payment-method duplicate
    signature already used at transaction-creation time (`detect_duplicate` in
    transaction_validation.py, surfaced there as `possible_duplicate` on the
    create response) but as a recurring notification rather than a one-time
    creation-time warning — so a duplicate entered outside that check (e.g.
    edited after creation, or created before this feature existed) still
    surfaces. Scoped to a rolling window, unlike the all-history creation-time
    check, so this acts as a timely nudge rather than a permanent flag on old,
    presumably-already-reviewed transactions."""
    window_start = today - _DUPLICATE_WINDOW
    conditions = [
        Transaction.user_id == owner_id,
        Transaction.date >= window_start,
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    statement = (
        select(
            Transaction.merchant,
            Transaction.total_amount,
            Transaction.date,
            func.count(Transaction.id),
        )
        .where(*conditions)
        .group_by(Transaction.merchant, Transaction.total_amount, Transaction.date, Transaction.payment_method_id)
        .having(func.count(Transaction.id) > 1)
    )
    rows = (await session.exec(statement)).all()
    return [
        NotificationItem(
            key=f"duplicate_transaction:{merchant}:{amount}:{tx_date.isoformat()}",
            type="duplicate_transaction",
            severity="warning",
            title="Possible duplicate transaction",
            message=f"{count} transactions of {amount} at {merchant} on {tx_date} — check for a duplicate entry.",
        )
        for merchant, amount, tx_date, count in rows
    ]


async def _reimbursement_notifications(
    session: AsyncSession, user: User, owner_id, today: date
) -> list[NotificationItem]:
    """PRD v2 §7.4: nags continuously (any past-month unpaid reimbursement,
    not just the one from the month that just closed) until marked paid --
    the separate scheduled job in scripts/notify_unpaid_reimbursements.py
    handles the one-time end-of-month email specifically."""
    current_month_start = date(today.year, today.month, 1)
    conditions = [
        Transaction.user_id == owner_id,
        Transaction.transaction_type == TransactionType.REIMBURSEMENT,
        Transaction.reimbursement_status == "unpaid",
        Transaction.date < current_month_start,
    ]
    apply_partner_transaction_visibility(conditions, user, owner_id)
    transactions = (await session.exec(select(Transaction).where(*conditions))).all()
    return [
        NotificationItem(
            key=f"reimbursement_unpaid:{transaction.id}",
            type="reimbursement_unpaid",
            severity="warning",
            title=f"Unpaid reimbursement from {transaction.merchant}",
            message=(
                f"{transaction.merchant} (${transaction.total_amount}) on {transaction.date} "
                "hasn't been marked paid yet."
            ),
            entity_id=transaction.id,
        )
        for transaction in transactions
    ]


async def list_notifications(session: AsyncSession, user: User) -> list[NotificationItem]:
    owner_id = household_owner_id(user)
    today = utcnow().date()

    items: list[NotificationItem] = []
    items += await _budget_notifications(session, user, owner_id, today)
    items += await _recurring_bill_notifications(session, user, owner_id, today)
    items += await _goal_notifications(session, user, owner_id, today)
    items += await _ai_insight_notifications(session, user, owner_id)
    items += await _duplicate_transaction_notifications(session, user, owner_id, today)
    items += await _reimbursement_notifications(session, user, owner_id, today)

    acknowledged_keys = set(
        (
            await session.exec(
                select(AcknowledgedNotification.notification_key).where(
                    AcknowledgedNotification.user_id == user.id
                )
            )
        ).all()
    )
    for item in items:
        item.is_acknowledged = item.key in acknowledged_keys

    items.sort(key=lambda item: (_SEVERITY_ORDER.get(item.severity, 3), item.title))
    return items


async def acknowledge_notification(session: AsyncSession, user: User, key: str) -> None:
    existing = (
        await session.exec(
            select(AcknowledgedNotification).where(
                AcknowledgedNotification.user_id == user.id,
                AcknowledgedNotification.notification_key == key,
            )
        )
    ).first()
    if existing:
        return
    session.add(AcknowledgedNotification(user_id=user.id, notification_key=key))
    await session.commit()
