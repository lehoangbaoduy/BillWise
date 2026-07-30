"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Suspense, useEffect, useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import { categoriesApi, paymentMethodsApi, transactionsApi } from "@/lib/api"

const TRANSACTION_TYPES = ["Expense", "Income", "Saving expense", "Adjustment"]

function todayISO() {
    return new Date().toISOString().slice(0, 10)
}

function makeLineItemKey() {
    return typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `line-item-${Math.random()}`
}

function emptyLineItem() {
    return { key: makeLineItemKey(), categoryId: "", itemName: "", amount: "" }
}

function categoryTypeForTransactionType(transactionType) {
    if (transactionType === "Income") return "income"
    if (transactionType === "Adjustment") return null
    return "expense"
}

function sumLineItems(lineItems) {
    return lineItems.reduce((total, item) => total + (Number(item.amount) || 0), 0)
}

function AddTransactionContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const editId = searchParams.get("edit")
    const isEditing = Boolean(editId)

    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())

    const [date, setDate] = useState(todayISO())
    const [merchant, setMerchant] = useState("")
    const [description, setDescription] = useState("")
    const [totalAmount, setTotalAmount] = useState("")
    const [transactionType, setTransactionType] = useState("Expense")
    const [paymentMethodId, setPaymentMethodId] = useState("")
    const [notes, setNotes] = useState("")
    const [lineItems, setLineItems] = useState([emptyLineItem()])
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [isLoadingExisting, setIsLoadingExisting] = useState(isEditing)

    useEffect(() => {
        if (!isEditing) return
        let cancelled = false
        transactionsApi
            .get(editId)
            .then((txn) => {
                if (cancelled) return
                setDate(txn.date)
                setMerchant(txn.merchant)
                setDescription(txn.description || "")
                setTotalAmount(String(txn.total_amount))
                setTransactionType(txn.transaction_type)
                setPaymentMethodId(txn.payment_method_id)
                setNotes(txn.notes || "")
                setLineItems(
                    txn.line_items.map((item) => ({
                        key: makeLineItemKey(),
                        categoryId: item.category_id,
                        itemName: item.item_name,
                        amount: String(item.amount),
                    }))
                )
            })
            .catch((error) => setFormError(error.message))
            .finally(() => {
                if (!cancelled) setIsLoadingExisting(false)
            })
        return () => {
            cancelled = true
        }
    }, [isEditing, editId])

    useEffect(() => {
        if (paymentMethodId || !paymentMethods?.length) return
        setPaymentMethodId(paymentMethods[0].id)
    }, [paymentMethods, paymentMethodId])

    const relevantCategoryType = categoryTypeForTransactionType(transactionType)
    const availableCategories = (categories ?? []).filter(
        (category) => relevantCategoryType === null || category.category_type === relevantCategoryType
    )

    function updateLineItem(index, field, value) {
        setLineItems((current) => current.map((item, i) => (i === index ? { ...item, [field]: value } : item)))
    }

    function addLineItem() {
        setLineItems((current) => [...current, emptyLineItem()])
    }

    function removeLineItem(index) {
        setLineItems((current) => current.filter((_, i) => i !== index))
    }

    async function handleSubmit(event) {
        event.preventDefault()
        setFormError(null)

        if (!merchant.trim()) {
            setFormError("Merchant is required.")
            return
        }
        if (!paymentMethodId) {
            setFormError("Payment method is required.")
            return
        }
        if (lineItems.some((item) => !item.categoryId || !item.itemName.trim() || item.amount === "")) {
            setFormError("Every line item needs a category, name, and amount.")
            return
        }
        const lineItemsSum = sumLineItems(lineItems)
        const total = Number(totalAmount)
        if (Math.round(lineItemsSum * 100) !== Math.round(total * 100)) {
            setFormError(`Line items sum to ${lineItemsSum.toFixed(2)}, which doesn't match the total (${total.toFixed(2)}).`)
            return
        }

        setIsSubmitting(true)
        try {
            const payload = {
                payment_method_id: paymentMethodId,
                date,
                merchant: merchant.trim(),
                description: description.trim() || null,
                total_amount: totalAmount,
                transaction_type: transactionType,
                notes: notes.trim() || null,
                line_items: lineItems.map((item) => ({
                    category_id: item.categoryId,
                    item_name: item.itemName.trim(),
                    amount: item.amount,
                })),
            }
            let possibleDuplicate = false
            if (isEditing) {
                await transactionsApi.update(editId, payload)
            } else {
                const created = await transactionsApi.create(payload)
                possibleDuplicate = created.possible_duplicate
            }
            router.push(possibleDuplicate ? "/analytics-transaction-history?duplicate=1" : "/analytics-transaction-history")
        } catch (error) {
            setFormError(error.message)
            setIsSubmitting(false)
        }
    }

    if (isLoadingExisting) {
        return (
            <Layout breadcrumbTitle={isEditing ? "Edit Transaction" : "Add Transaction"}>
                <div className="row">
                    <div className="col-xl-12">
                        <p className="text-muted">Loading transaction…</p>
                    </div>
                </div>
            </Layout>
        )
    }

    return (
        <Layout breadcrumbTitle={isEditing ? "Edit Transaction" : "Add Transaction"}>
            <div className="row">
                <div className="col-xl-8 col-lg-10">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">{isEditing ? "Edit transaction" : "Add a transaction"}</h4>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleSubmit}>
                                <div className="row">
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label" htmlFor="txn-date">Date</label>
                                        <input
                                            id="txn-date"
                                            type="date"
                                            className="form-control"
                                            value={date}
                                            onChange={(event) => setDate(event.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label" htmlFor="txn-type">Type</label>
                                        <select
                                            id="txn-type"
                                            className="form-select"
                                            value={transactionType}
                                            onChange={(event) => setTransactionType(event.target.value)}
                                        >
                                            {TRANSACTION_TYPES.map((type) => (
                                                <option key={type} value={type}>{type}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label" htmlFor="txn-merchant">Merchant</label>
                                    <input
                                        id="txn-merchant"
                                        type="text"
                                        className="form-control"
                                        placeholder="e.g. Costco"
                                        value={merchant}
                                        onChange={(event) => setMerchant(event.target.value)}
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label" htmlFor="txn-description">Description (optional)</label>
                                    <input
                                        id="txn-description"
                                        type="text"
                                        className="form-control"
                                        value={description}
                                        onChange={(event) => setDescription(event.target.value)}
                                    />
                                </div>

                                <div className="row">
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label" htmlFor="txn-total">Total amount</label>
                                        <input
                                            id="txn-total"
                                            type="number"
                                            step="0.01"
                                            className="form-control"
                                            placeholder="0.00"
                                            value={totalAmount}
                                            onChange={(event) => setTotalAmount(event.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label" htmlFor="txn-payment-method">Payment method</label>
                                        <select
                                            id="txn-payment-method"
                                            className="form-select"
                                            value={paymentMethodId}
                                            onChange={(event) => setPaymentMethodId(event.target.value)}
                                            required
                                        >
                                            <option value="" disabled>Select a payment method</option>
                                            {(paymentMethods ?? []).map((method) => (
                                                <option key={method.id} value={method.id}>{method.name}</option>
                                            ))}
                                        </select>
                                        {(paymentMethods ?? []).length === 0 && (
                                            <div className="form-text">
                                                No payment methods yet — add one on the <a href="/wallets">Wallets</a> page first.
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <fieldset className="mb-3">
                                    <legend className="col-form-label pt-0">Line items</legend>
                                    {lineItems.map((item, index) => (
                                        <div className="row align-items-end mb-2" key={item.key}>
                                            <div className="col-md-4">
                                                <label className="form-label" htmlFor={`line-item-category-${index}`}>Category</label>
                                                <select
                                                    id={`line-item-category-${index}`}
                                                    className="form-select"
                                                    value={item.categoryId}
                                                    onChange={(event) => updateLineItem(index, "categoryId", event.target.value)}
                                                    required
                                                >
                                                    <option value="" disabled>Select a category</option>
                                                    {availableCategories.map((category) => (
                                                        <option key={category.id} value={category.id}>
                                                            {category.emoji ? `${category.emoji} ` : ""}{category.name}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label" htmlFor={`line-item-name-${index}`}>Item</label>
                                                <input
                                                    id={`line-item-name-${index}`}
                                                    type="text"
                                                    className="form-control"
                                                    placeholder="e.g. Groceries"
                                                    value={item.itemName}
                                                    onChange={(event) => updateLineItem(index, "itemName", event.target.value)}
                                                    required
                                                />
                                            </div>
                                            <div className="col-md-3">
                                                <label className="form-label" htmlFor={`line-item-amount-${index}`}>Amount</label>
                                                <input
                                                    id={`line-item-amount-${index}`}
                                                    type="number"
                                                    step="0.01"
                                                    className="form-control"
                                                    placeholder="0.00"
                                                    value={item.amount}
                                                    onChange={(event) => updateLineItem(index, "amount", event.target.value)}
                                                    required
                                                />
                                            </div>
                                            <div className="col-md-1">
                                                <button
                                                    type="button"
                                                    className="btn btn-sm btn-outline-danger"
                                                    aria-label={`Remove line item ${index + 1}`}
                                                    disabled={lineItems.length === 1}
                                                    onClick={() => removeLineItem(index)}
                                                >
                                                    <i className="fi fi-rr-trash" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                    <button type="button" className="btn btn-sm btn-outline-secondary mt-2" onClick={addLineItem}>
                                        + Split into another category
                                    </button>
                                </fieldset>

                                <div className="mb-3">
                                    <label className="form-label" htmlFor="txn-notes">Notes (optional)</label>
                                    <textarea
                                        id="txn-notes"
                                        className="form-control"
                                        rows={2}
                                        value={notes}
                                        onChange={(event) => setNotes(event.target.value)}
                                    />
                                </div>

                                {formError && <div className="alert alert-danger" role="alert">{formError}</div>}

                                <button type="submit" className="btn btn-success" disabled={isSubmitting}>
                                    {isSubmitting ? "Saving…" : isEditing ? "Save changes" : "Add transaction"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}

export default function AddTransaction() {
    return (
        <Suspense fallback={null}>
            <AddTransactionContent />
        </Suspense>
    )
}
