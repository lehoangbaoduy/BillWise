'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import EmptyState from "@/components/elements/EmptyState"
import { categoriesApi, paymentMethodsApi, recurringBillsApi } from "@/lib/api"

const FREQUENCIES = ["weekly", "biweekly", "monthly", "quarterly", "yearly", "custom"]

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

function todayISO() {
    // toISOString() reports the UTC date, which can be a day ahead of/behind
    // the user's local date near midnight — build from local Y/M/D instead.
    const today = new Date()
    const month = String(today.getMonth() + 1).padStart(2, "0")
    const day = String(today.getDate()).padStart(2, "0")
    return `${today.getFullYear()}-${month}-${day}`
}

function capitalize(value) {
    return value ? value.charAt(0).toUpperCase() + value.slice(1) : ""
}

// Bootstrap color alone would fail WCAG 1.4.1 for colorblind users, so every
// status badge also carries the status name as text (see ConfidenceBadge in
// add-transaction/page.js for the same pattern).
function StatusBadge({ status }) {
    if (!status) return null
    const variant =
        status === "paid" ? "bg-success" : status === "overdue" ? "bg-danger" : status === "skipped" ? "bg-secondary" : "bg-warning text-dark"
    return <span className={`badge ${variant}`}>{capitalize(status)}</span>
}

function BillNavItem({ bill, isActive, onSelect }) {
    return (
        <div className="col-xl-12 col-md-6">
            <button
                type="button"
                className={isActive ? "goals-nav active w-100 border-0 text-start" : "goals-nav w-100 border-0 text-start"}
                aria-pressed={isActive}
                onClick={() => onSelect(bill.id)}
            >
                <div className="goals-nav-text">
                    <h3>{bill.name}</h3>
                    <p>
                        <strong>{formatCurrency(bill.amount)}</strong> · {formatDate(bill.current_period?.due_date)}{" "}
                        <StatusBadge status={bill.current_period?.status} />
                    </p>
                </div>
            </button>
        </div>
    )
}

function BillForm({ initial, categories, paymentMethods, onSubmit, isSubmitting, submitLabel }) {
    const [name, setName] = useState(initial?.name ?? "")
    const [categoryId, setCategoryId] = useState(initial?.category_id ?? "")
    const [paymentMethodId, setPaymentMethodId] = useState(initial?.payment_method_id ?? "")
    const [amount, setAmount] = useState(initial?.amount ?? "")
    const [frequency, setFrequency] = useState(initial?.frequency ?? "monthly")
    const [dueDate, setDueDate] = useState(initial?.due_date ?? "")
    const [autoCreateTransaction, setAutoCreateTransaction] = useState(initial?.auto_create_transaction ?? false)
    const [reminderEnabled, setReminderEnabled] = useState(initial?.reminder_enabled ?? false)
    const [notes, setNotes] = useState(initial?.notes ?? "")

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit({
            name: name.trim(),
            category_id: categoryId,
            payment_method_id: paymentMethodId,
            amount: Number(amount),
            frequency,
            due_date: dueDate || null,
            auto_create_transaction: autoCreateTransaction,
            reminder_enabled: reminderEnabled,
            notes: notes.trim() || null,
        })
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-name">Name</label>
                <input
                    id="bill-name"
                    type="text"
                    className="form-control"
                    placeholder="e.g. Internet"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                />
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-category">Category</label>
                <select id="bill-category" className="form-select" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
                    <option value="">Choose…</option>
                    {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                            {category.emoji ? `${category.emoji} ` : ""}{category.name}
                        </option>
                    ))}
                </select>
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-pm">Payment method</label>
                <select id="bill-pm" className="form-select" value={paymentMethodId} onChange={(event) => setPaymentMethodId(event.target.value)}>
                    <option value="">Choose…</option>
                    {paymentMethods.map((pm) => (
                        <option key={pm.id} value={pm.id}>{pm.name}</option>
                    ))}
                </select>
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-amount">Amount</label>
                <input
                    id="bill-amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    className="form-control"
                    placeholder="0.00"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                />
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-frequency">Frequency</label>
                <select id="bill-frequency" className="form-select" value={frequency} onChange={(event) => setFrequency(event.target.value)}>
                    {FREQUENCIES.map((value) => (
                        <option key={value} value={value}>{capitalize(value)}</option>
                    ))}
                </select>
                {frequency === "custom" && (
                    <div className="form-text">Custom bills don&apos;t auto-generate their next period — roll the due date forward manually after each payment.</div>
                )}
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-due-date">Due date</label>
                <input
                    id="bill-due-date"
                    type="date"
                    className="form-control"
                    value={dueDate}
                    onChange={(event) => setDueDate(event.target.value)}
                />
                <div className="form-text">Leave blank for a card-payment bill to auto-populate from the payment method&apos;s due/statement day.</div>
            </div>
            <div className="mb-3 form-check">
                <input
                    id="bill-auto-tx"
                    type="checkbox"
                    className="form-check-input"
                    checked={autoCreateTransaction}
                    onChange={(event) => setAutoCreateTransaction(event.target.checked)}
                />
                <label className="form-check-label" htmlFor="bill-auto-tx">Create a transaction automatically when marked paid</label>
            </div>
            <div className="mb-3 form-check">
                <input
                    id="bill-reminder"
                    type="checkbox"
                    className="form-check-input"
                    checked={reminderEnabled}
                    onChange={(event) => setReminderEnabled(event.target.checked)}
                />
                <label className="form-check-label" htmlFor="bill-reminder">Remind me before it&apos;s due</label>
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="bill-notes">Notes (optional)</label>
                <input
                    id="bill-notes"
                    type="text"
                    className="form-control"
                    value={notes}
                    onChange={(event) => setNotes(event.target.value)}
                />
            </div>
            <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                {isSubmitting ? "Saving…" : submitLabel}
            </button>
        </form>
    )
}

export default function RecurringBills() {
    const { data: bills, mutate: mutateBills } = useSWR("/recurring-bills", () => recurringBillsApi.list())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const expenseCategories = (categories ?? []).filter((category) => category.category_type === "expense")

    const [selectedId, setSelectedId] = useState(null)
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
    const [isEditFormOpen, setIsEditFormOpen] = useState(false)
    // Separate error states because the create-form panel (left column) and the
    // detail panel (right column) render simultaneously, not as mutually
    // exclusive views — a single shared error would leak between them.
    const [createError, setCreateError] = useState(null)
    const [detailError, setDetailError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [paidDate, setPaidDate] = useState(todayISO)
    const [amountPaid, setAmountPaid] = useState("")

    const activeBillId = selectedId ?? (bills ?? [])[0]?.id ?? null
    const activeBill = (bills ?? []).find((bill) => bill.id === activeBillId) ?? null

    function selectBill(billId) {
        setSelectedId(billId)
        setDetailError(null)
        setIsEditFormOpen(false)
        setAmountPaid("")
        setPaidDate(todayISO())
    }

    async function handleCreate(payload) {
        if (!payload.name || !payload.category_id || !payload.payment_method_id || !payload.amount) {
            setCreateError("Name, category, payment method, and amount are required.")
            return
        }
        setIsSubmitting(true)
        setCreateError(null)
        try {
            const created = await recurringBillsApi.create(payload)
            await mutateBills()
            setIsCreateFormOpen(false)
            selectBill(created.id)
        } catch (error) {
            setCreateError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleEdit(payload) {
        if (!activeBill) return
        setIsSubmitting(true)
        setDetailError(null)
        try {
            await recurringBillsApi.update(activeBill.id, payload)
            await mutateBills()
            setIsEditFormOpen(false)
        } catch (error) {
            setDetailError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleMarkPaid(event) {
        event.preventDefault()
        if (!activeBill) return
        setIsSubmitting(true)
        setDetailError(null)
        try {
            await recurringBillsApi.markPaid(activeBill.id, {
                paid_date: paidDate || null,
                amount_paid: amountPaid ? Number(amountPaid) : null,
            })
            await mutateBills()
            setAmountPaid("")
        } catch (error) {
            setDetailError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDeactivate() {
        if (!activeBill) return
        const confirmed = window.confirm(
            `Deactivate "${activeBill.name}"? This bill won't generate future periods and there's no undo — you'd need to create it again.`
        )
        if (!confirmed) return
        try {
            await recurringBillsApi.remove(activeBill.id)
            setSelectedId(null)
            await mutateBills()
        } catch (error) {
            setDetailError(error.message)
        }
    }

    return (
        <Layout breadcrumbTitle="Recurring Bills">
            <div className="goals-tab">
                <div className="row g-0">
                    <div className="col-xl-4">
                        <div className="nav d-block">
                            <div className="row">
                                {(bills ?? []).map((bill) => (
                                    <BillNavItem key={bill.id} bill={bill} isActive={activeBillId === bill.id} onSelect={selectBill} />
                                ))}
                            </div>
                        </div>
                        <button
                            type="button"
                            className="add-goals-link w-100 border-0"
                            onClick={() => {
                                setIsCreateFormOpen((open) => !open)
                                setCreateError(null)
                            }}
                            aria-expanded={isCreateFormOpen}
                            aria-controls="add-bill-form"
                        >
                            <h5 className="mb-0">Add recurring bill</h5>
                            <i className="fi fi-rr-square-plus" />
                        </button>

                        {isCreateFormOpen && (
                            <div className="card mt-3" id="add-bill-form">
                                <div className="card-body">
                                    {createError && <div className="text-danger mb-3" role="alert">{createError}</div>}
                                    <BillForm
                                        categories={expenseCategories}
                                        paymentMethods={paymentMethods ?? []}
                                        onSubmit={handleCreate}
                                        isSubmitting={isSubmitting}
                                        submitLabel="Add bill"
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="col-xl-8">
                        <div className="goals-tab-content">
                            {!activeBill ? (
                                <div className="card">
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-calendar-clock" message="No recurring bills yet." />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="goals-tab-title d-flex justify-content-between align-items-center">
                                        <h3>{activeBill.name}</h3>
                                        <div className="d-flex gap-2">
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-secondary"
                                                onClick={() => {
                                                    setIsEditFormOpen((open) => !open)
                                                    setDetailError(null)
                                                }}
                                                aria-expanded={isEditFormOpen}
                                                aria-controls="edit-bill-form"
                                            >
                                                <i className="fi fi-rr-pencil" /> Edit
                                            </button>
                                            <button type="button" className="btn btn-sm btn-outline-danger" onClick={handleDeactivate}>
                                                <i className="fi fi-rr-trash" />
                                            </button>
                                        </div>
                                    </div>
                                    {detailError && <div className="text-danger mb-3" role="alert">{detailError}</div>}

                                    {isEditFormOpen && (
                                        <div className="row mb-3" id="edit-bill-form">
                                            <div className="col-xl-12">
                                                <div className="card">
                                                    <div className="card-header">
                                                        <h4 className="card-title">Edit bill</h4>
                                                    </div>
                                                    <div className="card-body">
                                                        <BillForm
                                                            initial={activeBill}
                                                            categories={expenseCategories}
                                                            paymentMethods={paymentMethods ?? []}
                                                            onSubmit={handleEdit}
                                                            isSubmitting={isSubmitting}
                                                            submitLabel="Save changes"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Amount</span>
                                                            <h3>{formatCurrency(activeBill.amount)}</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Current period</span>
                                                            <h3>
                                                                <StatusBadge status={activeBill.current_period?.status} />
                                                            </h3>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>{capitalize(activeBill.frequency)}</span>
                                                        {activeBill.current_period && <span>Due: {formatDate(activeBill.current_period.due_date)}</span>}
                                                    </div>
                                                    {activeBill.notes && <p className="mt-2 mb-0">{activeBill.notes}</p>}
                                                </div>
                                            </div>
                                        </div>

                                        {activeBill.current_period && activeBill.current_period.status !== "paid" && activeBill.current_period.status !== "skipped" && (
                                            <div className="col-xl-12">
                                                <div className="card">
                                                    <div className="card-header">
                                                        <h4 className="card-title">Mark paid</h4>
                                                    </div>
                                                    <div className="card-body">
                                                        <form className="row g-2 align-items-end" onSubmit={handleMarkPaid}>
                                                            <div className="col-md-4">
                                                                <label className="form-label" htmlFor="paid-date">Paid date</label>
                                                                <input
                                                                    id="paid-date"
                                                                    type="date"
                                                                    className="form-control"
                                                                    value={paidDate}
                                                                    onChange={(event) => setPaidDate(event.target.value)}
                                                                />
                                                            </div>
                                                            <div className="col-md-4">
                                                                <label className="form-label" htmlFor="amount-paid">Amount paid (optional)</label>
                                                                <input
                                                                    id="amount-paid"
                                                                    type="number"
                                                                    step="0.01"
                                                                    min="0.01"
                                                                    className="form-control"
                                                                    placeholder={formatCurrency(activeBill.current_period.amount_due)}
                                                                    value={amountPaid}
                                                                    onChange={(event) => setAmountPaid(event.target.value)}
                                                                />
                                                            </div>
                                                            <div className="col-md-4">
                                                                <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                                                    {isSubmitting ? "Marking…" : "Mark paid"}
                                                                </button>
                                                            </div>
                                                        </form>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Payment history</h4>
                                                </div>
                                                <div className="card-body">
                                                    {(activeBill.payments ?? []).length === 0 ? (
                                                        <EmptyState icon="fi fi-rr-receipt" message="No periods yet." />
                                                    ) : (
                                                        <div className="table-responsive">
                                                            <table className="table mb-0 table-responsive-sm goals-history-table">
                                                                <thead>
                                                                    <tr>
                                                                        <th>Due date</th>
                                                                        <th>Amount</th>
                                                                        <th>Status</th>
                                                                        <th>Paid date</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {activeBill.payments.map((period) => (
                                                                        <tr key={period.id}>
                                                                            <td><span><i className="fi fi-rr-calendar" /></span> {formatDate(period.due_date)}</td>
                                                                            <td><h5>{formatCurrency(period.amount_due)}</h5></td>
                                                                            <td><StatusBadge status={period.status} /></td>
                                                                            <td>{formatDate(period.paid_date)}</td>
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
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
