"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useState } from "react"
import useSWR from "swr"
import EmptyState from "@/components/elements/EmptyState"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import Layout from "@/components/layout/Layout"
import { categoriesApi, paymentMethodsApi, transactionsApi } from "@/lib/api"

function formatCurrency(value) {
    return `$${Number(value).toFixed(2)}`
}

function TransactionRow({ transaction, categoriesById, paymentMethodsById, onDelete, isDeleting }) {
    const categoryNames = transaction.line_items
        .map((item) => categoriesById[item.category_id]?.name)
        .filter(Boolean)
        .join(", ")

    return (
        <tr>
            <td data-label="Date">{transaction.date}</td>
            <td data-label="Merchant">{transaction.merchant}</td>
            <td data-label="Category">{categoryNames || "—"}</td>
            <td data-label="Payment method">{paymentMethodsById[transaction.payment_method_id]?.name || "—"}</td>
            <td data-label="Type">{transaction.transaction_type}</td>
            <td className="text-end" data-label="Amount">{formatCurrency(transaction.total_amount)}</td>
            <td className="text-end mobile-cards-actions" data-label="">
                <Link
                    className="btn btn-sm btn-outline-secondary me-2"
                    href={`/add-transaction?edit=${transaction.id}`}
                    aria-label={`Edit transaction with ${transaction.merchant}`}
                >
                    <i className="fi fi-rr-pencil" />
                </Link>
                <button
                    type="button"
                    className="btn btn-sm btn-outline-danger"
                    aria-label={`Delete transaction with ${transaction.merchant}`}
                    disabled={isDeleting}
                    onClick={() => onDelete(transaction)}
                >
                    <i className="fi fi-rr-trash" />
                </button>
            </td>
        </tr>
    )
}

function TransactionHistoryContent() {
    const searchParams = useSearchParams()
    const showDuplicateBanner = searchParams.get("duplicate") === "1"

    const [month, setMonth] = useState("")
    const [categoryId, setCategoryId] = useState("")
    const [paymentMethodId, setPaymentMethodId] = useState("")
    const [amountMin, setAmountMin] = useState("")
    const [amountMax, setAmountMax] = useState("")
    const [search, setSearch] = useState("")
    const [deletingId, setDeletingId] = useState(null)
    const [listError, setListError] = useState(null)

    const filters = {
        month: month || undefined,
        category_id: categoryId || undefined,
        payment_method_id: paymentMethodId || undefined,
        amount_min: amountMin || undefined,
        amount_max: amountMax || undefined,
        search: search || undefined,
    }
    const filtersKey = JSON.stringify(filters)

    const { data: transactions, mutate } = useSWR(["/transactions", filtersKey], () => transactionsApi.list(filters))
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())

    const categoriesById = Object.fromEntries((categories ?? []).map((category) => [category.id, category]))
    const paymentMethodsById = Object.fromEntries((paymentMethods ?? []).map((method) => [method.id, method]))

    async function handleDelete(transaction) {
        if (!window.confirm(`Delete the ${formatCurrency(transaction.total_amount)} transaction at "${transaction.merchant}"?`)) return
        setDeletingId(transaction.id)
        try {
            await transactionsApi.remove(transaction.id)
            await mutate()
            setListError(null)
        } catch (error) {
            setListError(error.message)
        } finally {
            setDeletingId(null)
        }
    }

    function clearFilters() {
        setMonth("")
        setCategoryId("")
        setPaymentMethodId("")
        setAmountMin("")
        setAmountMax("")
        setSearch("")
    }

    return (
        <Layout breadcrumbTitle="Transaction History">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <AnalyticsMenu />

                    {showDuplicateBanner && (
                        <div className="alert alert-warning" role="alert">
                            Saved — but it looked similar to an existing transaction (same merchant, date, amount, and
                            payment method). Review below and delete it if it&apos;s a duplicate.
                        </div>
                    )}

                    <div className="row">
                        <div className="col-xl-12">
                            <div className="card">
                                <div className="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
                                    <h4 className="card-title mb-0">Transaction History</h4>
                                    <Link className="btn btn-success btn-sm" href="/add-transaction">
                                        + Add transaction
                                    </Link>
                                </div>
                                <div className="card-body">
                                    <div className="row g-2 mb-3">
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-month">Month</label>
                                            <input
                                                id="filter-month"
                                                type="month"
                                                className="form-control"
                                                value={month}
                                                onChange={(event) => setMonth(event.target.value)}
                                            />
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-category">Category</label>
                                            <select
                                                id="filter-category"
                                                className="form-select"
                                                value={categoryId}
                                                onChange={(event) => setCategoryId(event.target.value)}
                                            >
                                                <option value="">All categories</option>
                                                {(categories ?? []).map((category) => (
                                                    <option key={category.id} value={category.id}>{category.name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-payment-method">Payment method</label>
                                            <select
                                                id="filter-payment-method"
                                                className="form-select"
                                                value={paymentMethodId}
                                                onChange={(event) => setPaymentMethodId(event.target.value)}
                                            >
                                                <option value="">All methods</option>
                                                {(paymentMethods ?? []).map((method) => (
                                                    <option key={method.id} value={method.id}>{method.name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-amount-min">Min amount</label>
                                            <input
                                                id="filter-amount-min"
                                                type="number"
                                                step="0.01"
                                                className="form-control"
                                                value={amountMin}
                                                onChange={(event) => setAmountMin(event.target.value)}
                                            />
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-amount-max">Max amount</label>
                                            <input
                                                id="filter-amount-max"
                                                type="number"
                                                step="0.01"
                                                className="form-control"
                                                value={amountMax}
                                                onChange={(event) => setAmountMax(event.target.value)}
                                            />
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-search">Search</label>
                                            <input
                                                id="filter-search"
                                                type="search"
                                                className="form-control"
                                                placeholder="Merchant or description"
                                                value={search}
                                                onChange={(event) => setSearch(event.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <button type="button" className="btn btn-sm btn-outline-secondary mb-3" onClick={clearFilters}>
                                        Clear filters
                                    </button>

                                    {listError && <div className="alert alert-danger" role="alert">{listError}</div>}

                                    {(transactions ?? []).length === 0 ? (
                                        <EmptyState icon="fi fi-rr-receipt" message="No transactions match these filters." />
                                    ) : (
                                        <div className="table-responsive">
                                            <table className="table table-hover table-mobile-cards">
                                                <thead>
                                                    <tr>
                                                        <th>Date</th>
                                                        <th>Merchant</th>
                                                        <th>Category</th>
                                                        <th>Payment method</th>
                                                        <th>Type</th>
                                                        <th className="text-end">Amount</th>
                                                        <th className="text-end">Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {transactions.map((transaction) => (
                                                        <TransactionRow
                                                            key={transaction.id}
                                                            transaction={transaction}
                                                            categoriesById={categoriesById}
                                                            paymentMethodsById={paymentMethodsById}
                                                            onDelete={handleDelete}
                                                            isDeleting={deletingId === transaction.id}
                                                        />
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

export default function AnalyticsTransaction() {
    return (
        <Suspense fallback={null}>
            <TransactionHistoryContent />
        </Suspense>
    )
}
