'use client'
import { Fragment, useMemo, useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmptyState from "@/components/elements/EmptyState"
import MerchantInput from "@/components/elements/MerchantInput"
import { cashbackApi, categoriesApi, merchantsApi, paymentMethodsApi } from "@/lib/api"

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

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

function RuleForm({ initial, paymentMethods, categories, merchants, onSubmit, isSubmitting, submitLabel }) {
    const [paymentMethodId, setPaymentMethodId] = useState(initial?.payment_method_id ?? "")
    const [categoryId, setCategoryId] = useState(initial?.category_id ?? "")
    const [merchant, setMerchant] = useState(initial?.merchant ?? "")
    const [merchantType, setMerchantType] = useState(initial?.merchant_type ?? "")
    const [cashbackRate, setCashbackRate] = useState(initial?.cashback_rate ?? "")
    const [startDate, setStartDate] = useState(initial?.start_date ?? "")
    const [endDate, setEndDate] = useState(initial?.end_date ?? "")
    const [notes, setNotes] = useState(initial?.notes ?? "")

    const merchantTypes = useMemo(
        () => [...new Set((merchants ?? []).map((m) => m.type).filter(Boolean))].sort(),
        [merchants]
    )

    // Mutually exclusive per the backend's validation -- picking one clears
    // the other rather than letting both sit filled and submitting whichever
    // wins, which would be confusing to recover from after a 422.
    function handleMerchantChange(value) {
        setMerchant(value)
        if (value) setMerchantType("")
    }

    function handleMerchantTypeChange(value) {
        setMerchantType(value)
        if (value) setMerchant("")
    }

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit({
            payment_method_id: paymentMethodId,
            category_id: categoryId || null,
            merchant: merchant.trim() || null,
            merchant_type: merchantType || null,
            cashback_rate: Number(cashbackRate),
            start_date: startDate,
            end_date: endDate || null,
            notes: notes.trim() || null,
        })
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="row g-2">
                <div className="col-md-6">
                    <label className="form-label" htmlFor="rule-pm">Payment method</label>
                    <select
                        id="rule-pm"
                        className="form-select"
                        value={paymentMethodId}
                        disabled={Boolean(initial)}
                        onChange={(event) => setPaymentMethodId(event.target.value)}
                    >
                        <option value="">Choose…</option>
                        {paymentMethods.map((pm) => (
                            <option key={pm.id} value={pm.id}>{pm.name}</option>
                        ))}
                    </select>
                </div>
                <div className="col-md-6">
                    <label className="form-label" htmlFor="rule-category">Category (blank = default rate)</label>
                    <select id="rule-category" className="form-select" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
                        <option value="">Default for this card</option>
                        {categories.map((category) => (
                            <option key={category.id} value={category.id}>
                                {category.emoji ? `${category.emoji} ` : ""}{category.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="col-md-6">
                    <label className="form-label" htmlFor="rule-merchant">Merchant (optional, overrides category)</label>
                    <MerchantInput id="rule-merchant" value={merchant} onChange={handleMerchantChange} placeholder="e.g. Costco" />
                </div>
                <div className="col-md-6">
                    <label className="form-label" htmlFor="rule-merchant-type">
                        Merchant type (optional, alternative to a specific merchant)
                    </label>
                    <select
                        id="rule-merchant-type"
                        className="form-select"
                        value={merchantType}
                        onChange={(event) => handleMerchantTypeChange(event.target.value)}
                    >
                        <option value="">None</option>
                        {merchantTypes.map((type) => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </select>
                </div>
                <div className="col-md-4">
                    <label className="form-label" htmlFor="rule-rate">Rate (%)</label>
                    <input
                        id="rule-rate"
                        type="number"
                        step="0.01"
                        min="0"
                        max="100"
                        className="form-control"
                        value={cashbackRate}
                        onChange={(event) => setCashbackRate(event.target.value)}
                    />
                </div>
                <div className="col-md-4">
                    <label className="form-label" htmlFor="rule-start">Start date</label>
                    <input
                        id="rule-start"
                        type="date"
                        className="form-control"
                        value={startDate}
                        onChange={(event) => setStartDate(event.target.value)}
                    />
                </div>
                <div className="col-md-4">
                    <label className="form-label" htmlFor="rule-end">End date (optional)</label>
                    <input
                        id="rule-end"
                        type="date"
                        className="form-control"
                        value={endDate}
                        onChange={(event) => setEndDate(event.target.value)}
                    />
                </div>
                <div className="col-12">
                    <label className="form-label" htmlFor="rule-notes">Notes (optional)</label>
                    <input
                        id="rule-notes"
                        type="text"
                        className="form-control"
                        value={notes}
                        onChange={(event) => setNotes(event.target.value)}
                    />
                </div>
                <div className="col-12">
                    <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                        {isSubmitting ? "Saving…" : submitLabel}
                    </button>
                </div>
            </div>
        </form>
    )
}

function RecordOverrideForm({ record, onSubmit, onCancel, isSubmitting }) {
    const [estimatedAmount, setEstimatedAmount] = useState(record.estimated_amount)
    const [redeemedAmount, setRedeemedAmount] = useState(record.redeemed_amount)
    const [status, setStatus] = useState(record.status)

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit({ estimated_amount: Number(estimatedAmount), redeemed_amount: Number(redeemedAmount), status })
    }

    return (
        <form className="d-flex flex-wrap gap-2 align-items-end" onSubmit={handleSubmit}>
            <div>
                <label className="form-label" htmlFor={`override-estimated-${record.id}`}>Estimated</label>
                <input
                    id={`override-estimated-${record.id}`}
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-control"
                    value={estimatedAmount}
                    onChange={(event) => setEstimatedAmount(event.target.value)}
                />
            </div>
            <div>
                <label className="form-label" htmlFor={`override-redeemed-${record.id}`}>Redeemed</label>
                <input
                    id={`override-redeemed-${record.id}`}
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-control"
                    value={redeemedAmount}
                    onChange={(event) => setRedeemedAmount(event.target.value)}
                />
            </div>
            <div>
                <label className="form-label" htmlFor={`override-status-${record.id}`}>Status</label>
                <select
                    id={`override-status-${record.id}`}
                    className="form-select"
                    value={status}
                    onChange={(event) => setStatus(event.target.value)}
                >
                    <option value="estimated">Estimated</option>
                    <option value="redeemed">Redeemed</option>
                </select>
            </div>
            <button type="submit" className="btn btn-sm btn-success" disabled={isSubmitting}>Save</button>
            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onCancel}>Cancel</button>
        </form>
    )
}

export default function Cashback() {
    const today = new Date()
    const [month, setMonth] = useState(today.getMonth() + 1)
    const [year, setYear] = useState(today.getFullYear())
    const [isYearly, setIsYearly] = useState(false)

    const periodKey = isYearly ? `${year}` : `${year}-${String(month).padStart(2, "0")}`
    const { data: summary, mutate: mutateSummary } = useSWR(
        ["/cashback", periodKey],
        () => cashbackApi.summary(year, isYearly ? null : month)
    )
    const { data: rules, mutate: mutateRules } = useSWR("/cashback-rules", () => cashbackApi.listRules())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const { data: merchants } = useSWR("/merchants", () => merchantsApi.list())
    const expenseCategories = (categories ?? []).filter((category) => category.category_type === "expense")

    const [isRuleFormOpen, setIsRuleFormOpen] = useState(false)
    // Separate error states because the "Add rule" panel and a rule's inline
    // edit view can both be on screen at once (independent isRuleFormOpen /
    // editingRuleId state) — a single shared error would leak between them,
    // same bug class as the Recurring Bills slice's formError split.
    const [createRuleError, setCreateRuleError] = useState(null)
    const [editRuleError, setEditRuleError] = useState(null)
    const [editingRuleId, setEditingRuleId] = useState(null)
    const [editingRecordId, setEditingRecordId] = useState(null)
    const [recordError, setRecordError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const paymentMethodName = (id) => (paymentMethods ?? []).find((pm) => pm.id === id)?.name ?? "Unknown"
    const categoryName = (id) => (categories ?? []).find((category) => category.id === id)?.name ?? "Default"

    function changePeriod(delta) {
        let nextMonth = month + delta
        let nextYear = year
        if (nextMonth > 12) {
            nextMonth = 1
            nextYear += 1
        } else if (nextMonth < 1) {
            nextMonth = 12
            nextYear -= 1
        }
        setMonth(nextMonth)
        setYear(nextYear)
    }

    async function handleCreateRule(payload) {
        if (!payload.payment_method_id || !payload.cashback_rate || !payload.start_date) {
            setCreateRuleError("Payment method, rate, and start date are required.")
            return
        }
        setIsSubmitting(true)
        setCreateRuleError(null)
        try {
            await cashbackApi.createRule(payload)
            await mutateRules()
            setIsRuleFormOpen(false)
        } catch (error) {
            setCreateRuleError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleUpdateRule(ruleId, payload) {
        setIsSubmitting(true)
        setEditRuleError(null)
        try {
            const { payment_method_id: _paymentMethodId, ...updatable } = payload
            await cashbackApi.updateRule(ruleId, updatable)
            await mutateRules()
            setEditingRuleId(null)
        } catch (error) {
            setEditRuleError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDeleteRule(rule) {
        setEditRuleError(null)
        try {
            await cashbackApi.removeRule(rule.id)
            await mutateRules()
        } catch (error) {
            setEditRuleError(error.message)
        }
    }

    async function handleUpdateRecord(recordId, payload) {
        setIsSubmitting(true)
        setRecordError(null)
        try {
            await cashbackApi.updateRecord(recordId, payload)
            await mutateSummary()
            setEditingRecordId(null)
        } catch (error) {
            setRecordError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <Layout breadcrumbTitle="Cashback">
            <div className="cashback-tab">
                <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                    {isYearly ? (
                        <h5 className="mb-0">{year}</h5>
                    ) : (
                        <div className="d-flex align-items-center gap-2">
                            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => changePeriod(-1)}>
                                <i className="fi fi-rr-angle-left" />
                            </button>
                            <h5 className="mb-0">{MONTH_NAMES[month - 1]} {year}</h5>
                            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => changePeriod(1)}>
                                <i className="fi fi-rr-angle-right" />
                            </button>
                        </div>
                    )}
                    <button type="button" className="btn btn-sm btn-outline-primary" onClick={() => setIsYearly((value) => !value)}>
                        {isYearly ? "View monthly" : "View full year"}
                    </button>
                </div>

                <div className="row">
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-success"><span><i className="fi fi-rr-badge-percent" /></span></div>
                            <div className="widget-content">
                                <p>Estimated</p>
                                <h3>{formatCurrency(summary?.total_estimated)}</h3>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-primary"><span><i className="fi fi-rr-hand-holding-usd" /></span></div>
                            <div className="widget-content">
                                <p>Redeemed</p>
                                <h3>{formatCurrency(summary?.total_redeemed)}</h3>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-warning"><span><i className="fi fi-rr-time-past" /></span></div>
                            <div className="widget-content">
                                <p>Unredeemed</p>
                                <h3>{formatCurrency(summary?.total_unredeemed)}</h3>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xl-6">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">By card</h4>
                            </div>
                            <div className="card-body">
                                {(summary?.by_card ?? []).length === 0 ? (
                                    <EmptyState icon="fi fi-rr-credit-card" message="No cashback recorded for this period." />
                                ) : (
                                    <ul className="list-group list-group-flush">
                                        {summary.by_card.map((row) => (
                                            <li key={row.payment_method_id} className="list-group-item d-flex justify-content-between align-items-center">
                                                <span>{row.name}</span>
                                                <span>{formatCurrency(row.estimated)} est. / {formatCurrency(row.redeemed)} redeemed</span>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-6">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">By category</h4>
                            </div>
                            <div className="card-body">
                                {(summary?.by_category ?? []).length === 0 ? (
                                    <EmptyState icon="fi fi-rr-tags" message="No cashback recorded for this period." />
                                ) : (
                                    <ul className="list-group list-group-flush">
                                        {summary.by_category.map((row) => (
                                            <li key={row.category_id} className="list-group-item d-flex justify-content-between align-items-center">
                                                <span>{row.name}</span>
                                                <span>{formatCurrency(row.estimated)} est. / {formatCurrency(row.redeemed)} redeemed</span>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">By transaction</h4>
                            </div>
                            <div className="card-body">
                                {recordError && <div className="text-danger mb-3" role="alert">{recordError}</div>}
                                {(summary?.records ?? []).length === 0 ? (
                                    <EmptyState icon="fi fi-rr-receipt" message="No cashback records for this period." />
                                ) : (
                                    <div className="table-responsive">
                                        <table className="table mb-0 table-responsive-sm">
                                            <thead>
                                                <tr>
                                                    <th>Card</th>
                                                    <th>Category</th>
                                                    <th>Estimated</th>
                                                    <th>Redeemed</th>
                                                    <th>Status</th>
                                                    <th />
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {summary.records.map((record) => (
                                                    <Fragment key={record.id}>
                                                        <tr>
                                                            <td>{paymentMethodName(record.payment_method_id)}</td>
                                                            <td>{categoryName(record.category_id)}</td>
                                                            <td>
                                                                {formatCurrency(record.estimated_amount)}
                                                                {record.cashback_rule_id === null && Number(record.estimated_amount) === 0 && (
                                                                    <span
                                                                        className="badge bg-secondary ms-2"
                                                                        title="No cashback rule matched this card/category/merchant -- $0 isn't a 0% rule, nothing matched at all."
                                                                    >
                                                                        No matching rule
                                                                    </span>
                                                                )}
                                                            </td>
                                                            <td>{formatCurrency(record.redeemed_amount)}</td>
                                                            <td>
                                                                <span className={`badge ${record.status === "redeemed" ? "bg-success" : "bg-warning text-dark"}`}>
                                                                    {record.status === "redeemed" ? "Redeemed" : "Estimated"}
                                                                </span>
                                                            </td>
                                                            <td>
                                                                {editingRecordId !== record.id && (
                                                                    <button
                                                                        type="button"
                                                                        className="btn btn-sm btn-outline-secondary"
                                                                        onClick={() => {
                                                                            setEditingRecordId(record.id)
                                                                            setRecordError(null)
                                                                        }}
                                                                    >
                                                                        <i className="fi fi-rr-pencil" />
                                                                    </button>
                                                                )}
                                                            </td>
                                                        </tr>
                                                        {editingRecordId === record.id && (
                                                            <tr>
                                                                <td colSpan={6}>
                                                                    <RecordOverrideForm
                                                                        record={record}
                                                                        isSubmitting={isSubmitting}
                                                                        onSubmit={(payload) => handleUpdateRecord(record.id, payload)}
                                                                        onCancel={() => {
                                                                            setEditingRecordId(null)
                                                                            setRecordError(null)
                                                                        }}
                                                                    />
                                                                </td>
                                                            </tr>
                                                        )}
                                                    </Fragment>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <h4 className="card-title">Cashback rules</h4>
                                <button
                                    type="button"
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={() => {
                                        setIsRuleFormOpen((open) => !open)
                                        setCreateRuleError(null)
                                    }}
                                    aria-expanded={isRuleFormOpen}
                                    aria-controls="add-rule-form"
                                >
                                    Add rule
                                </button>
                            </div>
                            <div className="card-body">
                                {isRuleFormOpen && (
                                    <div className="mb-4" id="add-rule-form">
                                        {createRuleError && <div className="text-danger mb-3" role="alert">{createRuleError}</div>}
                                        <RuleForm
                                            paymentMethods={paymentMethods ?? []}
                                            categories={expenseCategories}
                                            merchants={merchants ?? []}
                                            onSubmit={handleCreateRule}
                                            isSubmitting={isSubmitting}
                                            submitLabel="Add rule"
                                        />
                                    </div>
                                )}

                                {(rules ?? []).length === 0 ? (
                                    <EmptyState icon="fi fi-rr-badge-percent" message="No cashback rules set up yet." />
                                ) : (
                                    <ul className="list-group list-group-flush">
                                        {rules.map((rule) => (
                                            <li key={rule.id} className="list-group-item">
                                                {editingRuleId === rule.id ? (
                                                    <>
                                                        {editRuleError && <div className="text-danger mb-3" role="alert">{editRuleError}</div>}
                                                        <RuleForm
                                                            initial={rule}
                                                            paymentMethods={paymentMethods ?? []}
                                                            categories={expenseCategories}
                                                            merchants={merchants ?? []}
                                                            isSubmitting={isSubmitting}
                                                            submitLabel="Save changes"
                                                            onSubmit={(payload) => handleUpdateRule(rule.id, payload)}
                                                        />
                                                        <button
                                                            type="button"
                                                            className="btn btn-sm btn-outline-secondary mt-2"
                                                            onClick={() => {
                                                                setEditingRuleId(null)
                                                                setEditRuleError(null)
                                                            }}
                                                        >
                                                            Cancel
                                                        </button>
                                                    </>
                                                ) : (
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>{paymentMethodName(rule.payment_method_id)}</strong>
                                                            {" — "}
                                                            {rule.merchant || (rule.merchant_type ? `Merchant type: ${rule.merchant_type}` : null) || (rule.category_id ? categoryName(rule.category_id) : "Default")}
                                                            {" · "}{rule.cashback_rate}%
                                                            {" · "}{formatDate(rule.start_date)} – {rule.end_date ? formatDate(rule.end_date) : "ongoing"}
                                                            {rule.notes && <div className="text-muted small">{rule.notes}</div>}
                                                        </div>
                                                        <div className="d-flex gap-2">
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-outline-secondary"
                                                                onClick={() => {
                                                                    setEditingRuleId(rule.id)
                                                                    setEditRuleError(null)
                                                                }}
                                                            >
                                                                <i className="fi fi-rr-pencil" />
                                                            </button>
                                                            <ConfirmButton
                                                                className="btn btn-sm btn-outline-danger"
                                                                message={`Delete this cashback rule for ${paymentMethodName(rule.payment_method_id)}?`}
                                                                onConfirm={() => handleDeleteRule(rule)}
                                                            >
                                                                <i className="fi fi-rr-trash" />
                                                            </ConfirmButton>
                                                        </div>
                                                    </div>
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
