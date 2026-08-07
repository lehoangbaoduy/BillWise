'use client'
import { useState } from "react"
import Link from "next/link"
import useSWR from "swr"
import DashboardCategoryDonut from "@/components/chart/DashboardCategoryDonut"
import IncomeVsExpenseChart from "@/components/chart/IncomeVsExpenseChart"
import EmptyState from "@/components/elements/EmptyState"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import Layout from "@/components/layout/Layout"
import { categoriesApi, dashboardApi, transactionsApi } from "@/lib/api"

const MONTH_ABBREVIATIONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

const TYPE_FILTERS = ["All", "Income", "Expense"]

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function formatDate(value) {
    if (!value) return "—"
    const [year, month, day] = value.slice(0, 10).split("-").map(Number)
    return new Date(year, month - 1, day).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
}

// No backend endpoint aggregates income by category (dashboard's
// category-breakdown is expense-only per PRD scope) -- group the already
// type-filtered transaction list client-side instead of adding a
// near-duplicate server route for a single small chart.
function groupByCategory(transactions, categoriesById) {
    const totals = new Map()
    for (const transaction of transactions) {
        for (const item of transaction.line_items) {
            const name = categoriesById[item.category_id]?.name ?? "Uncategorized"
            totals.set(name, (totals.get(name) ?? 0) + Number(item.amount))
        }
    }
    return [...totals.entries()]
        .map(([name, amount]) => ({ name, amount }))
        .sort((a, b) => b.amount - a.amount)
}

export default function AnalyticsIncomeExpenses() {
    const today = new Date()
    const month = today.getMonth() + 1
    const year = today.getFullYear()
    const periodKey = `${year}-${String(month).padStart(2, "0")}`

    const [typeFilter, setTypeFilter] = useState("All")

    const { data: yearly } = useSWR(["/dashboard/yearly", year], () => dashboardApi.yearly(year))
    const { data: categoryBreakdown } = useSWR(
        ["/dashboard/category-breakdown", periodKey],
        () => dashboardApi.categoryBreakdown(month, year)
    )
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const { data: transactions } = useSWR(["/transactions", periodKey], () => transactionsApi.list({ month: periodKey }))

    const hasChartData = (yearly?.income_by_month ?? []).some((entry) => Number(entry.total) > 0)
        || (yearly?.spend_by_month ?? []).some((entry) => Number(entry.total) > 0)
    const income = (yearly?.income_by_month ?? []).map((entry) => Number(entry.total))
    const expenses = (yearly?.spend_by_month ?? []).map((entry) => Number(entry.total))

    // category-breakdown also injects zero-spend *budgeted* categories (budgets/page.js
    // needs those to show "$0 of $100 budgeted" rows) -- drop them here so a $0.00 slice
    // doesn't show up in a chart that's meant to reflect actual spending.
    const expenseSorted = [...(categoryBreakdown ?? [])]
        .filter((category) => Number(category.amount) > 0)
        .sort((a, b) => Number(b.amount) - Number(a.amount))
    const expenseLabels = expenseSorted.map((category) => category.name)
    const expenseAmounts = expenseSorted.map((category) => Number(category.amount))

    const categoriesById = Object.fromEntries((categories ?? []).map((category) => [category.id, category]))
    const incomeTransactions = (transactions ?? []).filter((transaction) => transaction.transaction_type === "Income")
    const incomeBreakdown = groupByCategory(incomeTransactions, categoriesById)
    const incomeLabels = incomeBreakdown.map((category) => category.name)
    const incomeAmounts = incomeBreakdown.map((category) => category.amount)

    const filteredTransactions = (transactions ?? []).filter(
        (transaction) => typeFilter === "All" || transaction.transaction_type === typeFilter
    )
    const recentTransactions = filteredTransactions.slice(0, 8)

    return (
        <Layout breadcrumbTitle="Income vs Expenses">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <AnalyticsMenu />
                    <div className="row">
                        <div className="col-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Income vs Expense Graph</h4>
                                </div>
                                <div className="card-body">
                                    {!hasChartData ? (
                                        <EmptyState icon="fi fi-rr-chart-line-up" message="No income or expenses recorded yet." />
                                    ) : (
                                        <IncomeVsExpenseChart labels={MONTH_ABBREVIATIONS} income={income} expenses={expenses} />
                                    )}
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-6 col-lg-6 col-md-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Expenses Breakdown</h4>
                                </div>
                                <div className="card-body">
                                    {expenseLabels.length === 0 ? (
                                        <EmptyState icon="fi fi-rr-chart-pie-alt" message="No spending recorded yet." />
                                    ) : (
                                        <DashboardCategoryDonut labels={expenseLabels} amounts={expenseAmounts} />
                                    )}
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-6 col-lg-6 col-md-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Income Breakdown</h4>
                                </div>
                                <div className="card-body">
                                    {incomeLabels.length === 0 ? (
                                        <EmptyState icon="fi fi-rr-chart-pie-alt" message="No income recorded yet." />
                                    ) : (
                                        <DashboardCategoryDonut labels={incomeLabels} amounts={incomeAmounts} />
                                    )}
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-12">
                            <div className="card">
                                <div className="card-header d-flex justify-content-between align-items-center">
                                    <h4 className="card-title mb-0">Transaction History</h4>
                                    <Link className="d-block" href="/analytics-transaction-history">View all</Link>
                                </div>
                                <div className="card-body">
                                    <div className="mb-3" style={{ maxWidth: 220 }}>
                                        <label className="form-label" htmlFor="transaction-type-filter">Type</label>
                                        <select
                                            id="transaction-type-filter"
                                            className="form-select"
                                            value={typeFilter}
                                            onChange={(event) => setTypeFilter(event.target.value)}
                                        >
                                            {TYPE_FILTERS.map((option) => (
                                                <option key={option} value={option}>{option}</option>
                                            ))}
                                        </select>
                                    </div>
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
                                                        <th className="text-end">Amount</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {recentTransactions.map((transaction) => (
                                                        <tr key={transaction.id}>
                                                            <td>{formatDate(transaction.date)}</td>
                                                            <td>{transaction.merchant}</td>
                                                            <td>{transaction.transaction_type}</td>
                                                            <td className="text-end">{formatCurrency(transaction.total_amount)}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
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
