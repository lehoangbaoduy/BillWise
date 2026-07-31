"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Suspense, useEffect, useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import ReceiptUploadPanel from "@/components/receipt/ReceiptUploadPanel"
import { categoriesApi, ocrApi, paymentMethodsApi, transactionsApi } from "@/lib/api"

const TRANSACTION_TYPES = ["Expense", "Income", "Saving expense", "Adjustment"]

function todayISO() {
    return new Date().toISOString().slice(0, 10)
}

function makeLineItemKey() {
    return typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `line-item-${Math.random()}`
}

function emptyLineItem() {
    return { key: makeLineItemKey(), categoryId: "", itemName: "", amount: "", confidence: null }
}

// OCR items carry plain-English category labels (PRD §29.1), not IDs — resolve them
// against the user's real category tree by name. Subcategory match wins since it's
// more specific; "Uncategorized" or an unmatched label is left for manual selection
// (PRD §29.2).
function resolveCategoryId(categories, suggestedCategory, suggestedSubcategory) {
    const byName = new Map((categories ?? []).map((category) => [category.name.trim().toLowerCase(), category.id]))
    if (suggestedSubcategory) {
        const match = byName.get(suggestedSubcategory.trim().toLowerCase())
        if (match) return match
    }
    if (suggestedCategory && suggestedCategory !== "Uncategorized") {
        const match = byName.get(suggestedCategory.trim().toLowerCase())
        if (match) return match
    }
    return ""
}

function ConfidenceBadge({ confidence }) {
    if (confidence == null) return null
    const pct = Math.round(confidence * 100)
    // Percentage text already conveys the tier numerically; the qualifier below
    // makes it explicit without relying on the badge color alone (WCAG 1.4.1).
    const [variant, qualifier] =
        confidence >= 0.85 ? ["bg-success", ""] : confidence >= 0.6 ? ["bg-warning text-dark", ""] : ["bg-danger", " — needs review"]
    return <span className={`badge ${variant} ms-2`}>{pct}% match{qualifier}</span>
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

    // "manual" | "scan-upload" | "scan-review" — PRD §24.4 treats manual entry and
    // receipt scanning as two entry paths into one Add Transaction screen.
    const [entryMode, setEntryMode] = useState("manual")
    const [ocrStatus, setOcrStatus] = useState(null)
    const [ocrWarnings, setOcrWarnings] = useState([])

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
                        confidence: null,
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

    // If a scan completes before the categories SWR fetch resolves, resolveCategoryId
    // has nothing to match against and leaves categoryId empty. Re-resolve once
    // categories arrive so a fast scan doesn't force an unnecessary manual pick.
    useEffect(() => {
        if (entryMode !== "scan-review" || !categories?.length) return
        setLineItems((current) => {
            const stillUnresolved = current.some((item) => item.confidence != null && !item.categoryId)
            if (!stillUnresolved) return current
            return current.map((item) =>
                item.confidence != null && !item.categoryId
                    ? { ...item, categoryId: resolveCategoryId(categories, item.suggestedCategory, item.suggestedSubcategory) }
                    : item
            )
        })
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [categories, entryMode])

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

    function handleExtracted(result) {
        setDate(result.date || todayISO())
        setMerchant(result.merchant || "")
        setDescription("")
        setTotalAmount(result.total != null ? String(result.total) : "")
        setTransactionType("Expense")
        setNotes("")
        setLineItems(
            result.items.length > 0
                ? result.items.map((item) => ({
                      key: makeLineItemKey(),
                      categoryId: resolveCategoryId(categories, item.suggested_category, item.suggested_subcategory),
                      itemName: item.name || "",
                      amount: item.amount != null ? String(item.amount) : "",
                      confidence: item.confidence,
                      suggestedCategory: item.suggested_category,
                      suggestedSubcategory: item.suggested_subcategory,
                  }))
                : [emptyLineItem()]
        )
        setOcrStatus(result.ocr_status)
        setOcrWarnings(result.warnings || [])
        setFormError(null)
        setEntryMode("scan-review")
    }

    function resetToManualEntry() {
        setEntryMode("manual")
        setOcrStatus(null)
        setOcrWarnings([])
    }

    function startNewScan() {
        setDate(todayISO())
        setMerchant("")
        setDescription("")
        setTotalAmount("")
        setTransactionType("Expense")
        setNotes("")
        setLineItems([emptyLineItem()])
        setOcrStatus(null)
        setOcrWarnings([])
        setFormError(null)
        setEntryMode("scan-upload")
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
            } else if (entryMode === "scan-review") {
                const created = await ocrApi.confirmTransaction(payload)
                possibleDuplicate = created.possible_duplicate
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
                            {!isEditing && (
                                <div className="btn-group mb-4" role="group" aria-label="Transaction entry mode">
                                    <button
                                        type="button"
                                        aria-pressed={entryMode === "manual"}
                                        className={`btn btn-sm ${entryMode === "manual" ? "btn-primary" : "btn-outline-primary"}`}
                                        onClick={resetToManualEntry}
                                    >
                                        Manual entry
                                    </button>
                                    <button
                                        type="button"
                                        aria-pressed={entryMode !== "manual"}
                                        className={`btn btn-sm ${entryMode !== "manual" ? "btn-primary" : "btn-outline-primary"}`}
                                        onClick={() => setEntryMode("scan-upload")}
                                    >
                                        Scan receipt
                                    </button>
                                </div>
                            )}

                            {entryMode === "scan-upload" ? (
                                <ReceiptUploadPanel onExtracted={handleExtracted} onCancel={resetToManualEntry} />
                            ) : (
                                <form onSubmit={handleSubmit}>
                                {entryMode === "scan-review" && (
                                    <div
                                        className={`alert ${ocrStatus === "low_confidence" ? "alert-warning" : "alert-success"} d-flex justify-content-between align-items-start`}
                                        role="alert"
                                    >
                                        <div>
                                            <strong>
                                                {ocrStatus === "low_confidence" ? "Review before saving" : "Receipt scanned — review before saving"}
                                            </strong>
                                            {ocrWarnings.length > 0 && (
                                                <ul className="mb-0 mt-1">
                                                    {ocrWarnings.map((warning, index) => (
                                                        <li key={index}>{warning}</li>
                                                    ))}
                                                </ul>
                                            )}
                                        </div>
                                        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={startNewScan}>
                                            Scan a different receipt
                                        </button>
                                    </div>
                                )}
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
                                                <label className="form-label" htmlFor={`line-item-category-${index}`}>
                                                    Category
                                                    <ConfidenceBadge confidence={item.confidence} />
                                                </label>
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
                                    {isSubmitting
                                        ? "Saving…"
                                        : isEditing
                                        ? "Save changes"
                                        : entryMode === "scan-review"
                                        ? "Confirm & save"
                                        : "Add transaction"}
                                </button>
                            </form>
                            )}
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
