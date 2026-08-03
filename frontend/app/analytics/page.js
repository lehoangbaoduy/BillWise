'use client'
import useSWR from "swr"
import DashboardSpendTrendChart from "@/components/chart/DashboardSpendTrendChart"
import EmptyState from "@/components/elements/EmptyState"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import Layout from "@/components/layout/Layout"
import { dashboardApi, transactionsApi } from "@/lib/api"

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function formatPercent(value) {
    if (value === null || value === undefined) return "0%"
    return `${Number(value) > 0 ? "+" : ""}${Number(value)}%`
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

export default function Analytics() {
    const today = new Date()
    const month = today.getMonth() + 1
    const year = today.getFullYear()
    const periodKey = `${year}-${String(month).padStart(2, "0")}`
    const daysInMonth = new Date(year, month, 0).getDate()
    const daysElapsed = year === today.getFullYear() && month === today.getMonth() + 1 ? today.getDate() : daysInMonth

    const { data: monthly } = useSWR(["/dashboard/monthly", periodKey], () => dashboardApi.monthly(month, year))
    const { data: categoryBreakdown } = useSWR(
        ["/dashboard/category-breakdown", periodKey],
        () => dashboardApi.categoryBreakdown(month, year)
    )
    const { data: expenseTransactions } = useSWR(
        ["/transactions", periodKey, "Expense"],
        () => transactionsApi.list({ month: periodKey, transaction_type: "Expense" })
    )
    const { data: countPage } = useSWR(
        ["/transactions/count", periodKey],
        () => transactionsApi.listPage({ month: periodKey }, { limit: 1 })
    )

    const totalExpenses = Number(monthly?.total_expenses ?? 0)
    const dailyAverage = totalExpenses / Math.max(1, daysElapsed)
    const changePercentage = monthly?.comparison_vs_previous_month?.change_percentage
    const totalTransactionCount = countPage?.total ?? 0
    const categoryCount = (categoryBreakdown ?? []).filter((category) => Number(category.amount) > 0).length

    // Weeks that haven't started yet have no data to show -- drop them
    // instead of plotting a misleading flat 0.
    const elapsedWeekCount = Math.ceil(daysElapsed / 7)
    const weekLabels = Array.from({ length: elapsedWeekCount }, (_, index) => `Week ${index + 1}`)
    const weekAmounts = weeklyBuckets(expenseTransactions ?? [], daysInMonth).slice(0, elapsedWeekCount)
    const hasWeeklyData = weekAmounts.some((amount) => amount > 0)

    return (
        <Layout breadcrumbTitle="Analytics">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <AnalyticsMenu />
                    <div className="row">
                        <div className="col-xl-3 col-sm-6">
                            <div className="analytics-widget">
                                <div className="widget-icon me-3 bg-primary"><span><i className="fi fi-rr-mobile" /></span>
                                </div>
                                <div className="widget-content">
                                    <p>Daily Average</p>
                                    <h3>{formatCurrency(dailyAverage)}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-3 col-sm-6">
                            <div className="analytics-widget">
                                <div className="widget-icon me-3 bg-success"><span><i className="fi fi-rr-replace" /></span>
                                </div>
                                <div className="widget-content">
                                    <p>Change vs last month</p>
                                    <h3>{formatPercent(changePercentage)}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-3 col-sm-6">
                            <div className="analytics-widget">
                                <div className="widget-icon me-3 bg-warning"><span><i className="fi fi-rs-receipt" /></span>
                                </div>
                                <div className="widget-content">
                                    <p>Total Transaction</p>
                                    <h3>{totalTransactionCount}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-3 col-sm-6">
                            <div className="analytics-widget">
                                <div className="widget-icon me-3 bg-danger">
                                    <span><i className="fi fi-ss-confetti" /></span>
                                </div>
                                <div className="widget-content">
                                    <p>Categories</p>
                                    <h3>{categoryCount}</h3>
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Weekly Expenses </h4>
                                </div>
                                <div className="card-body">
                                    {!hasWeeklyData ? (
                                        <EmptyState icon="fi fi-rr-chart-line-up" message="No expenses recorded this week." />
                                    ) : (
                                        <DashboardSpendTrendChart labels={weekLabels} amounts={weekAmounts} />
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
