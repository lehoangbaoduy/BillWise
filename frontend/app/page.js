'use client'
import { useMemo, useState } from "react"
import Link from "next/link"
import useSWR from "swr"
import CircularProgress from "@/components/elements/CircularProgress"
import DashboardCategoryDonut from "@/components/chart/DashboardCategoryDonut"
import DashboardSpendTrendChart from "@/components/chart/DashboardSpendTrendChart"
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import { aiInsightsApi, dashboardApi, goalsApi, paymentMethodsApi, recurringBillsApi, transactionsApi } from "@/lib/api"

const _OPEN_BILL_STATUSES = new Set(["upcoming", "overdue"])

const MONTH_ABBREVIATIONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

const INSIGHT_ICONS = {
    category_spending_change: "fi fi-rr-chart-pie-alt",
    over_budget_alert: "fi fi-rr-exclamation",
    multi_month_trend: "fi fi-rr-chart-line-up",
    top_cashback_card: "fi fi-rr-badge-percent",
    recurring_bill_share: "fi fi-rr-calendar-clock",
    cash_flow_change: "fi fi-rr-money-bill-wave-alt",
    goal_progress: "fi fi-rr-piggy-bank",
}

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function formatDate(value) {
    if (!value) return "—"
    // Date-only strings ("YYYY-MM-DD") parse as UTC midnight; rendering that
    // in a timezone behind UTC rolls the displayed date back a day. Build the
    // Date from the Y/M/D components directly so it's always local-midnight.
    const [year, month, day] = value.slice(0, 10).split("-").map(Number)
    return new Date(year, month - 1, day).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
}

function progressPercent(current, target) {
    if (!target || Number(target) <= 0) return 0
    return Math.min(100, Math.round((Number(current) / Number(target)) * 100))
}

// Calendar weeks would need real week-of-year math; a fixed 7-day bucket
// counted from day 1 is a simpler, still-useful "which part of the month"
// breakdown and needs no more than the transactions already on hand.
function weeklyBuckets(transactions, daysInMonth) {
    const bucketCount = Math.ceil(daysInMonth / 7)
    const totals = new Array(bucketCount).fill(0)
    for (const transaction of transactions) {
        const day = Number(transaction.date.slice(8, 10))
        const bucket = Math.min(bucketCount - 1, Math.floor((day - 1) / 7))
        totals[bucket] += Number(transaction.total_amount)
    }
    return totals
}

export default function Home() {
    const today = new Date()
    const month = today.getMonth() + 1
    const year = today.getFullYear()
    const periodKey = `${year}-${String(month).padStart(2, "0")}`

    const { data: monthly } = useSWR(["/dashboard/monthly", periodKey], () => dashboardApi.monthly(month, year))
    const { data: yearly } = useSWR(["/dashboard/yearly", year], () => dashboardApi.yearly(year))
    const { data: categoryBreakdown } = useSWR(
        ["/dashboard/category-breakdown", periodKey],
        () => dashboardApi.categoryBreakdown(month, year)
    )
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: goals } = useSWR("/goals", () => goalsApi.list())
    const { data: transactions } = useSWR(
        ["/transactions", periodKey],
        () => transactionsApi.list({ month: periodKey })
    )
    const { data: insights, mutate: mutateInsights } = useSWR("/dashboard/ai-insights", () => dashboardApi.aiInsights())
    const { data: recurringBills } = useSWR("/recurring-bills", () => recurringBillsApi.list())
    const [dismissError, setDismissError] = useState(null)

    async function handleDismissInsight(id) {
        setDismissError(null)
        mutateInsights((current) => (current ?? []).filter((insight) => insight.id !== id), { revalidate: false })
        try {
            await aiInsightsApi.dismiss(id)
        } catch (error) {
            setDismissError(error.message)
            // Revalidate from the server rather than restoring a captured local
            // snapshot — if another dismissal is in flight concurrently, a
            // restored snapshot could resurrect that one too.
            mutateInsights()
        }
    }

    const totalBalance = (paymentMethods ?? []).reduce((sum, method) => sum + Number(method.current_balance ?? 0), 0)
    // Chart color slots are capped at CATEGORY_DONUT_SLOT_COUNT distinct hues
    // (dataviz palette rule: a 9th+ series is never a generated color). Rather
    // than silently dropping categories beyond that cap, fold their total into
    // an "Other" slice so the donut -- and the total shown in its center --
    // always account for the full month's spending.
    const CATEGORY_DONUT_SLOT_COUNT = 7
    const topCategories = useMemo(() => {
        const sorted = [...(categoryBreakdown ?? [])].sort((a, b) => Number(b.amount) - Number(a.amount))
        if (sorted.length <= CATEGORY_DONUT_SLOT_COUNT + 1) return sorted
        const top = sorted.slice(0, CATEGORY_DONUT_SLOT_COUNT)
        const otherAmount = sorted.slice(CATEGORY_DONUT_SLOT_COUNT).reduce((sum, c) => sum + Number(c.amount), 0)
        return [...top, { name: "Other", amount: otherAmount }]
    }, [categoryBreakdown])
    const recentTransactions = (transactions ?? []).slice(0, 5)
    const daysInMonth = new Date(year, month, 0).getDate()
    const daysElapsed = today.getDate()
    // Weeks that haven't started yet have no data to show -- drop them
    // instead of plotting a misleading flat 0.
    const elapsedWeekCount = Math.ceil(daysElapsed / 7)
    const weekLabels = Array.from({ length: elapsedWeekCount }, (_, index) => `Week ${index + 1}`)
    const weekAmounts = weeklyBuckets(
        (transactions ?? []).filter((transaction) => transaction.transaction_type === "Expense"),
        daysInMonth
    ).slice(0, elapsedWeekCount)
    const hasWeeklyData = weekAmounts.some((amount) => amount > 0)
    const topBudgets = (monthly?.budget_status ?? []).slice(0, 4)
    const topGoals = (goals ?? []).slice(0, 3)
    // Only bills with a still-open (unpaid) current period belong on the
    // dashboard -- a bill stays here until it's marked paid, then the next
    // period (if any) takes its place.
    const upcomingBills = (recurringBills ?? [])
        .filter((bill) => bill.current_period && _OPEN_BILL_STATUSES.has(bill.current_period.status))
        .sort((a, b) => a.current_period.due_date.localeCompare(b.current_period.due_date))
        .slice(0, 5)
    const expensePercentage = monthly && Number(monthly.total_income) > 0
        ? Math.min(100, (Number(monthly.total_expenses) / Number(monthly.total_income)) * 100)
        : 100

    return (
        <Layout breadcrumbTitle="Dashboard">
            <div className="row">
                <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                    <div className="stat-widget-1">
                        <h6>Total Balance</h6>
                        <h3>{formatCurrency(totalBalance)}</h3>
                        <p className="text-muted mb-0">Across all wallets</p>
                    </div>
                </div>
                <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                    <div className="stat-widget-1">
                        <h6>Total Period Change</h6>
                        <h3>{formatCurrency(monthly?.net_cash_flow)}</h3>
                        <p className="text-muted mb-0">This month&apos;s net cash flow</p>
                    </div>
                </div>
                <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                    <div className="stat-widget-1">
                        <h6>Total Period Expenses</h6>
                        <h3>{formatCurrency(monthly?.total_expenses)}</h3>
                        <p className="text-muted mb-0">This month</p>
                    </div>
                </div>
                <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                    <div className="stat-widget-1">
                        <h6>Total Period Income</h6>
                        <h3>{formatCurrency(monthly?.total_income)}</h3>
                        <p className="text-muted mb-0">This month</p>
                    </div>
                </div>
            </div>
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">AI Insights</h4>
                        </div>
                        <div className="card-body">
                            {dismissError && <div className="text-danger mb-3" role="alert">{dismissError}</div>}
                            {(insights ?? []).length === 0 ? (
                                <EmptyState icon="fi fi-rr-lightbulb-on" message="No new insights right now — check back after adding more transactions." />
                            ) : (
                                <ul className="list-group list-group-flush">
                                    {insights.map((insight) => (
                                        <li key={insight.id} className="list-group-item d-flex justify-content-between align-items-start gap-3">
                                            <div className="d-flex align-items-start gap-2">
                                                <i className={INSIGHT_ICONS[insight.insight_type] || "fi fi-rr-lightbulb-on"} aria-hidden="true" />
                                                <span>{insight.message}</span>
                                            </div>
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-secondary"
                                                aria-label={`Dismiss insight: ${insight.message.slice(0, 60)}`}
                                                onClick={() => handleDismissInsight(insight.id)}
                                            >
                                                <i className="fi fi-rr-cross-small" />
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <div className="row">
                <div className="col-xxl-8 col-xl-8 col-lg-6">
                    <div className="card">
                        <div className="card-header balance-trend">
                            <h4 className="card-title">Monthly Spending Trend</h4>
                        </div>
                        <div className="card-body">
                            {yearly && yearly.total_yearly_spending > 0 ? (
                                <DashboardSpendTrendChart
                                    labels={yearly.spend_by_month.map((entry) => MONTH_ABBREVIATIONS[entry.month - 1])}
                                    amounts={yearly.spend_by_month.map((entry) => Number(entry.total))}
                                />
                            ) : (
                                <EmptyState icon="fi fi-rr-chart-line-up" message="Spending trends will appear once you add transactions." />
                            )}
                        </div>
                    </div>
                </div>
                <div className=" col-xxl-4 col-xl-4 col-lg-6 col-md-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Monthly Expenses Breakdown</h4>
                        </div>
                        <div className="card-body d-flex justify-content-center">
                            {topCategories.length > 0 ? (
                                <DashboardCategoryDonut
                                    labels={topCategories.map((category) => category.name)}
                                    amounts={topCategories.map((category) => Number(category.amount))}
                                />
                            ) : (
                                <EmptyState icon="fi fi-rr-chart-pie-alt" message="No spending recorded yet." />
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-xl-4 col-lg-6 col-md-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Monthly Budgets</h4>
                        </div>
                        <div className="card-body">
                            {topBudgets.length === 0 ? (
                                <EmptyState icon="fi fi-rr-wallet" message="No budgets set for this month." />
                            ) : (
                                topBudgets.map((budget) => {
                                    const percentUsed = Math.min(100, Number(budget.percentage_used ?? 0))
                                    return (
                                        <div key={budget.category_id} className="mb-3">
                                            <div className="d-flex justify-content-between mb-1">
                                                <span>{budget.category_name}</span>
                                                <span>{formatCurrency(budget.actual_amount)} / {formatCurrency(budget.budget_amount)}</span>
                                            </div>
                                            <div className="progress">
                                                <div
                                                    className={budget.is_over_budget ? "progress-bar bg-danger" : "progress-bar"}
                                                    style={{ width: `${percentUsed}%` }}
                                                    role="progressbar"
                                                    aria-label={`${budget.category_name} budget`}
                                                    aria-valuenow={percentUsed}
                                                    aria-valuemin={0}
                                                    aria-valuemax={100}
                                                />
                                            </div>
                                        </div>
                                    )
                                })
                            )}
                            <Link href="/budgets" className="d-block text-end">View all</Link>
                        </div>
                    </div>
                </div>
                <div className=" col-xxl-8 col-xl-8 col-lg-6 col-md-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Monthly Income vs Expenses</h4>
                        </div>
                        <div className="card-body">
                            {!monthly || (monthly.total_income === "0" && monthly.total_expenses === "0") ? (
                                <EmptyState icon="fi fi-rr-chart-line-up" message="No income or expenses recorded yet." />
                            ) : (
                                <>
                                    <div className="mb-3">
                                        <div className="d-flex justify-content-between mb-1">
                                            <span>Income</span>
                                            <span>{formatCurrency(monthly.total_income)}</span>
                                        </div>
                                        <div className="progress">
                                            <div
                                                className="progress-bar bg-success"
                                                style={{ width: "100%" }}
                                                role="progressbar"
                                                aria-label="Income"
                                                aria-valuenow={100}
                                                aria-valuemin={0}
                                                aria-valuemax={100}
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="d-flex justify-content-between mb-1">
                                            <span>Expenses</span>
                                            <span>{formatCurrency(monthly.total_expenses)}</span>
                                        </div>
                                        <div className="progress">
                                            <div
                                                className="progress-bar bg-danger"
                                                style={{ width: `${expensePercentage}%` }}
                                                role="progressbar"
                                                aria-label="Expenses vs income"
                                                aria-valuenow={expensePercentage}
                                                aria-valuemin={0}
                                                aria-valuemax={100}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-xl-8 col-lg-6">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Weekly Expenses</h4>
                        </div>
                        <div className="card-body">
                            {!hasWeeklyData ? (
                                <EmptyState icon="fi fi-rr-chart-line-up" message="No expenses recorded this week." />
                            ) : (
                                <DashboardSpendTrendChart labels={weekLabels} amounts={weekAmounts} variant="line" />
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-xl-4 col-lg-6 col-md-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Recurring Bills</h4>
                        </div>
                        <div className="card-body">
                            {upcomingBills.length === 0 ? (
                                <EmptyState icon="fi fi-rr-receipt" message="No recurring bills yet." />
                            ) : (
                                upcomingBills.map((bill) => (
                                    <div key={bill.id} className="d-flex justify-content-between align-items-center mb-3">
                                        <div>
                                            <div>{bill.name}</div>
                                            <small className={bill.current_period.status === "overdue" ? "text-danger" : "text-muted"}>
                                                {formatDate(bill.current_period.due_date)}
                                                {bill.current_period.status === "overdue" ? " · Overdue" : ""}
                                            </small>
                                        </div>
                                        <strong>{formatCurrency(bill.amount)}</strong>
                                    </div>
                                ))
                            )}
                            <Link href="/recurring-bills" className="d-block text-end">View all</Link>
                        </div>
                    </div>
                </div>
                <div className="col-xl-4">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Saving Goals</h4>
                        </div>
                        <div className="card-body">
                            {topGoals.length === 0 ? (
                                <EmptyState icon="fi fi-rr-piggy-bank" message="No savings goals yet." />
                            ) : (
                                topGoals.map((goal) => (
                                    <div key={goal.id} className="d-flex align-items-center mb-3">
                                        <CircularProgress
                                            value={progressPercent(goal.current_amount, goal.target_amount)}
                                            height={40}
                                            width={40}
                                            margin="0 12px 0 0"
                                        />
                                        <div>
                                            <div>{goal.icon ? `${goal.icon} ` : ""}{goal.name}</div>
                                            <small className="text-muted">
                                                {formatCurrency(goal.current_amount)} / {formatCurrency(goal.target_amount)}
                                            </small>
                                        </div>
                                    </div>
                                ))
                            )}
                            <Link href="/goals" className="d-block text-end">View all</Link>
                        </div>
                    </div>
                </div>
                <div className="col-xl-8">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Transaction History</h4>
                        </div>
                        <div className="card-body">
                            {recentTransactions.length === 0 ? (
                                <EmptyState icon="fi fi-rr-receipt" message="No transactions yet — add your first one." />
                            ) : (
                                <div className="table-responsive">
                                    <table className="table mb-0 table-responsive-sm">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Merchant</th>
                                                <th>Type</th>
                                                <th>Amount</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {recentTransactions.map((transaction) => (
                                                <tr key={transaction.id}>
                                                    <td>{formatDate(transaction.date)}</td>
                                                    <td>{transaction.merchant}</td>
                                                    <td>{transaction.transaction_type}</td>
                                                    <td>{formatCurrency(transaction.total_amount)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    <Link href="/analytics-transaction-history" className="d-block text-end mt-2">View all</Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
