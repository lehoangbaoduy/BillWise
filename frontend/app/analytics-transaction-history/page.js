"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useEffect, useState } from "react"
import useSWR from "swr"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmptyState from "@/components/elements/EmptyState"
import SharingBadge from "@/components/elements/SharingBadge"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import Layout from "@/components/layout/Layout"
import { categoriesApi, paymentMethodsApi, transactionsApi } from "@/lib/api"
import { revalidateDashboard } from "@/lib/dashboardCache"

const PAGE_SIZE = 20
const TRANSACTION_TYPES = ["Expense", "Income", "Saving expense", "Adjustment", "Reimbursement"]

function formatCurrency(value) {
    return `$${Number(value).toFixed(2)}`
}

function currentMonthKey() {
    const today = new Date()
    return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`
}

function TransactionRow({ transaction, categoriesById, paymentMethodsById, onDelete, isDeleting, onMarkPaid }) {
    const categoryNames = transaction.line_items
        .map((item) => categoriesById[item.category_id]?.name)
        .filter(Boolean)
        .join(", ")
    const needsReimbursementAction =
        transaction.transaction_type === "Reimbursement" && transaction.reimbursement_status === "unpaid"

    return (
        <tr>
            <td data-label="Date">{transaction.date}</td>
            <td data-label="Merchant">{transaction.merchant}</td>
            <td data-label="Category">{categoryNames || "—"}</td>
            <td data-label="Payment method">{paymentMethodsById[transaction.payment_method_id]?.name || "—"}</td>
            <td data-label="Type">{transaction.transaction_type}</td>
            <td data-label="Action">
                {needsReimbursementAction && (
                    <ConfirmButton
                        className="btn btn-sm btn-outline-warning"
                        confirmLabel="Mark Paid"
                        message={`Mark the ${formatCurrency(transaction.total_amount)} reimbursement at "${transaction.merchant}" as paid?`}
                        inputLabel="Paid by who?"
                        inputPlaceholder="Name"
                        onConfirm={(paidBy) => onMarkPaid(transaction, paidBy)}
                    >
                        Mark Paid
                    </ConfirmButton>
                )}
            </td>
            <td data-label="Private/Shared">
                <SharingBadge isShared={transaction.is_shared} showText />
            </td>
            <td className="text-end" data-label="Amount">{formatCurrency(transaction.total_amount)}</td>
            <td className="text-end mobile-cards-actions" data-label="">
                <Link
                    className="btn btn-sm btn-outline-secondary me-2"
                    href={`/add-transaction?edit=${transaction.id}`}
                    aria-label={`Edit transaction with ${transaction.merchant}`}
                >
                    <i className="fi fi-rr-pencil" />
                </Link>
                <ConfirmButton
                    className="btn btn-sm btn-outline-danger"
                    aria-label={`Delete transaction with ${transaction.merchant}`}
                    disabled={isDeleting}
                    message={`Delete the ${formatCurrency(transaction.total_amount)} transaction at "${transaction.merchant}"?`}
                    onConfirm={() => onDelete(transaction)}
                >
                    <i className="fi fi-rr-trash" />
                </ConfirmButton>
            </td>
        </tr>
    )
}

function TransactionHistoryContent() {
    const searchParams = useSearchParams()
    const showDuplicateBanner = searchParams.get("duplicate") === "1"

    const [month, setMonth] = useState(currentMonthKey)
    const [categoryId, setCategoryId] = useState("")
    const [paymentMethodId, setPaymentMethodId] = useState("")
    const [merchant, setMerchant] = useState("")
    const [amountMin, setAmountMin] = useState("")
    const [amountMax, setAmountMax] = useState("")
    const [transactionTypes, setTransactionTypes] = useState([])
    const [page, setPage] = useState(1)
    const [deletingId, setDeletingId] = useState(null)
    const [listError, setListError] = useState(null)

    const filters = {
        month: month || undefined,
        category_id: categoryId || undefined,
        payment_method_id: paymentMethodId || undefined,
        amount_min: amountMin || undefined,
        amount_max: amountMax || undefined,
        merchant: merchant || undefined,
        transaction_type: transactionTypes.length > 0 ? transactionTypes : undefined,
    }
    const filtersKey = JSON.stringify(filters)

    useEffect(() => {
        setPage(1)
    }, [filtersKey])

    const { data: page_result, mutate } = useSWR(
        ["/transactions", filtersKey, page],
        () => transactionsApi.listPage(filters, { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE })
    )
    const transactions = page_result?.items
    const totalCount = page_result?.total ?? 0
    const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE))
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: merchants } = useSWR("/transactions/merchants", () => transactionsApi.merchants())

    const categoriesById = Object.fromEntries((categories ?? []).map((category) => [category.id, category]))
    const paymentMethodsById = Object.fromEntries((paymentMethods ?? []).map((method) => [method.id, method]))

    async function handleDelete(transaction) {
        setDeletingId(transaction.id)
        try {
            await transactionsApi.remove(transaction.id)
            await mutate()
            revalidateDashboard()
            setListError(null)
        } catch (error) {
            setListError(error.message)
        } finally {
            setDeletingId(null)
        }
    }

    async function handleMarkPaid(transaction, paidBy) {
        try {
            await transactionsApi.markReimbursementPaid(transaction.id, paidBy)
            await mutate()
            setListError(null)
        } catch (error) {
            setListError(error.message)
        }
    }

    function clearFilters() {
        setMonth("")
        setCategoryId("")
        setPaymentMethodId("")
        setMerchant("")
        setAmountMin("")
        setAmountMax("")
        setTransactionTypes([])
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
                                            <label className="form-label" htmlFor="filter-merchant">Merchant</label>
                                            <select
                                                id="filter-merchant"
                                                className="form-select"
                                                value={merchant}
                                                onChange={(event) => setMerchant(event.target.value)}
                                            >
                                                <option value="">All merchants</option>
                                                {(merchants ?? []).map((merchantName) => (
                                                    <option key={merchantName} value={merchantName}>{merchantName}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="col-md-2">
                                            <label className="form-label" htmlFor="filter-type">Type</label>
                                            <select
                                                id="filter-type"
                                                className="form-select"
                                                multiple
                                                value={transactionTypes}
                                                onChange={(event) =>
                                                    setTransactionTypes(
                                                        Array.from(event.target.selectedOptions, (option) => option.value)
                                                    )
                                                }
                                            >
                                                {TRANSACTION_TYPES.map((type) => (
                                                    <option key={type} value={type}>{type}</option>
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
                                                        <th>Action</th>
                                                        <th>Private/Shared</th>
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
                                                            onMarkPaid={handleMarkPaid}
                                                        />
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}
                                    {totalCount > 0 && (
                                        <div className="d-flex justify-content-between align-items-center mt-3">
                                            <span className="text-muted">
                                                Page {page} of {totalPages} ({totalCount} transaction{totalCount === 1 ? "" : "s"})
                                            </span>
                                            <div className="d-flex gap-2">
                                                <button
                                                    type="button"
                                                    className="btn btn-sm btn-outline-secondary"
                                                    disabled={page <= 1}
                                                    onClick={() => setPage((current) => Math.max(1, current - 1))}
                                                >
                                                    Previous
                                                </button>
                                                <button
                                                    type="button"
                                                    className="btn btn-sm btn-outline-secondary"
                                                    disabled={page >= totalPages}
                                                    onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
                                                >
                                                    Next
                                                </button>
                                            </div>
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
