'use client'
import { useState } from "react"
import useSWR from "swr"
import CircularProgress from "@/components/elements/CircularProgress"
import Layout from "@/components/layout/Layout"
import ColorPicker, { COLOR_PRESETS } from "@/components/elements/ColorPicker"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmojiPicker from "@/components/elements/EmojiPicker"
import EmptyState from "@/components/elements/EmptyState"
import FilterTabs from "@/components/elements/FilterTabs"
import SharingBadge from "@/components/elements/SharingBadge"
import SharingToggle from "@/components/elements/SharingToggle"
import { useAuth } from "@/hooks/useAuth"
import { categoriesApi, goalsApi, paymentMethodsApi } from "@/lib/api"
import { VISIBILITY_TABS, filterByVisibility, isItemCreator } from "@/lib/sharing"

function todayISO() {
    // toISOString() reports the UTC date, which can be a day ahead of/behind
    // the user's local date near midnight — build from local Y/M/D instead.
    const today = new Date()
    const month = String(today.getMonth() + 1).padStart(2, "0")
    const day = String(today.getDate()).padStart(2, "0")
    return `${today.getFullYear()}-${month}-${day}`
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

function progressPercent(goal) {
    if (!goal || Number(goal.target_amount) <= 0) return 0
    return Math.min(100, Math.round((Number(goal.current_amount) / Number(goal.target_amount)) * 100))
}

// Quick-pick presets prefill the name/icon fields below but never lock them --
// the free-text Name input and EmojiPicker stay fully editable so a preset is
// a shortcut, not a restriction.
const GOAL_PRESETS = [
    { name: "Emergency Fund", icon: "💰" },
    { name: "Vacation", icon: "✈️" },
    { name: "New Car", icon: "🚗" },
    { name: "Home", icon: "🏠" },
    { name: "Wedding", icon: "💍" },
    { name: "Education", icon: "🎓" },
    { name: "New Gadget", icon: "📱" },
    { name: "Gift", icon: "🎁" },
]

function GoalNavItem({ goal, isActive, onSelect, onDelete }) {
    return (
        <div className="col-xl-12 col-md-6">
            <div className={isActive ? "goals-nav active w-100" : "goals-nav w-100"}>
                <button
                    type="button"
                    className="goals-nav-trigger"
                    aria-pressed={isActive}
                    onClick={() => onSelect(goal.id)}
                >
                    <CircularProgress value={progressPercent(goal)} height={50} width={50} margin="0 15px 0 0" />
                    <div className="goals-nav-text">
                        <h3>
                            {goal.icon ? `${goal.icon} ` : ""}{goal.name}
                            {" "}<SharingBadge isShared={goal.is_shared} />
                        </h3>
                        <p><strong>{formatCurrency(goal.current_amount)}</strong> / {formatCurrency(goal.target_amount)}</p>
                    </div>
                </button>
                <div className="goals-nav-actions">
                    <ConfirmButton
                        className="btn btn-sm btn-outline-danger"
                        aria-label={`Delete goal ${goal.name}`}
                        message={`Delete goal "${goal.name}"? Linked transactions will stay, unlinked from this goal.`}
                        onConfirm={() => onDelete(goal)}
                    >
                        <i className="fi fi-rr-trash" />
                    </ConfirmButton>
                </div>
            </div>
        </div>
    )
}

function GoalEditForm({ goal, onSubmit, onCancel, isSubmitting }) {
    const [name, setName] = useState(goal.name ?? "")
    const [targetAmount, setTargetAmount] = useState(goal.target_amount ?? "")
    const [targetDate, setTargetDate] = useState(goal.target_date ? goal.target_date.slice(0, 10) : "")
    const [icon, setIcon] = useState(goal.icon ?? "")
    const [color, setColor] = useState(goal.color ?? COLOR_PRESETS[0].value)

    function handleSubmit(event) {
        event.preventDefault()
        // Sharing is toggled from the title-row switch instead of this form --
        // GoalUpdate (this form's PATCH /goals/{id}) uses extra="forbid" and
        // doesn't declare the field anyway.
        onSubmit({
            name: name.trim(),
            target_amount: Number(targetAmount),
            target_date: targetDate || null,
            icon: icon.trim() || null,
            color: color || null,
        })
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="mb-3">
                <label className="form-label" htmlFor="edit-goal-name">Name</label>
                <input
                    id="edit-goal-name"
                    type="text"
                    className="form-control"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                />
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="edit-goal-target">Target amount</label>
                <input
                    id="edit-goal-target"
                    type="number"
                    step="0.01"
                    min="0.01"
                    className="form-control"
                    value={targetAmount}
                    onChange={(event) => setTargetAmount(event.target.value)}
                />
            </div>
            <div className="mb-3">
                <label className="form-label" htmlFor="edit-goal-date">Target date (optional)</label>
                <input
                    id="edit-goal-date"
                    type="date"
                    className="form-control"
                    value={targetDate}
                    onChange={(event) => setTargetDate(event.target.value)}
                />
            </div>
            <div className="mb-3">
                <label className="form-label">Icon (optional)</label>
                <EmojiPicker value={icon} onChange={setIcon} name="edit-goal-icon" />
            </div>
            <div className="mb-3">
                <label className="form-label">Color</label>
                <ColorPicker value={color} onChange={setColor} name="edit-goal-color" />
            </div>
            <div className="d-flex gap-2">
                <button type="submit" className="btn btn-success flex-grow-1" disabled={isSubmitting}>
                    {isSubmitting ? "Saving…" : "Save changes"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onCancel}>Cancel</button>
            </div>
        </form>
    )
}

export default function Goals() {
    const { user } = useAuth()
    const { data: goals, mutate: mutateGoals } = useSWR("/goals", () => goalsApi.list())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const expenseCategories = (categories ?? []).filter((category) => category.category_type === "expense")

    const [selectedId, setSelectedId] = useState(null)
    const [detail, setDetail] = useState(null)
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
    const [isEditFormOpen, setIsEditFormOpen] = useState(false)
    const [formError, setFormError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [name, setName] = useState("")
    const [targetAmount, setTargetAmount] = useState("")
    const [targetDate, setTargetDate] = useState("")
    const [icon, setIcon] = useState("")
    const [color, setColor] = useState(COLOR_PRESETS[0].value)
    const [isShared, setIsShared] = useState(false)

    const [fundsAmount, setFundsAmount] = useState("")
    const [fundsPaymentMethodId, setFundsPaymentMethodId] = useState("")
    const [fundsCategoryId, setFundsCategoryId] = useState("")
    const [fundsDate, setFundsDate] = useState(todayISO)
    const [fundsNotes, setFundsNotes] = useState("")
    const [visibilityFilter, setVisibilityFilter] = useState("all")

    const filteredGoals = filterByVisibility(goals ?? [], visibilityFilter)
    // Falls back to the filtered list's first goal both when nothing is
    // selected yet AND when the previously-selected goal just got filtered
    // out by switching tabs -- not only the "nothing selected" case.
    const activeGoalId = filteredGoals.find((goal) => goal.id === selectedId)?.id ?? filteredGoals[0]?.id ?? null
    const activeGoal = detail?.id === activeGoalId ? detail : filteredGoals.find((goal) => goal.id === activeGoalId) ?? null

    async function loadDetail(goalId) {
        setSelectedId(goalId)
        setFormError(null)
        setIsEditFormOpen(false)
        try {
            const goalDetail = await goalsApi.get(goalId)
            setDetail(goalDetail)
        } catch (error) {
            setFormError(error.message)
        }
    }

    async function refreshDetail() {
        if (!activeGoalId) return
        const goalDetail = await goalsApi.get(activeGoalId)
        setDetail(goalDetail)
        await mutateGoals()
    }

    async function handleCreate(event) {
        event.preventDefault()
        if (!name.trim() || !targetAmount) {
            setFormError("Name and target amount are required.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            const created = await goalsApi.create({
                name: name.trim(),
                target_amount: Number(targetAmount),
                target_date: targetDate || null,
                icon: icon.trim() || null,
                color: color || null,
                is_shared: isShared,
            })
            await mutateGoals()
            setName("")
            setTargetAmount("")
            setTargetDate("")
            setIcon("")
            setColor(COLOR_PRESETS[0].value)
            setIsShared(false)
            setIsCreateFormOpen(false)
            await loadDetail(created.id)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleAddFunds(event) {
        event.preventDefault()
        if (!activeGoal || !fundsAmount || !fundsPaymentMethodId || !fundsCategoryId) {
            setFormError("Amount, payment method, and category are required.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            await goalsApi.addFunds(activeGoal.id, {
                amount: Number(fundsAmount),
                payment_method_id: fundsPaymentMethodId,
                category_id: fundsCategoryId,
                date: fundsDate,
                notes: fundsNotes.trim() || null,
            })
            await refreshDetail()
            setFundsAmount("")
            setFundsDate(todayISO())
            setFundsNotes("")
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleToggleSharing(goal, isShared) {
        setFormError(null)
        try {
            await goalsApi.updateSharing(goal.id, isShared)
            await refreshDetail()
        } catch (error) {
            setFormError(error.message)
        }
    }

    async function handleEdit(payload) {
        if (!activeGoal) return
        setIsSubmitting(true)
        setFormError(null)
        try {
            await goalsApi.update(activeGoal.id, payload)
            await refreshDetail()
            setIsEditFormOpen(false)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDelete(goal) {
        if (!goal) return
        try {
            await goalsApi.remove(goal.id)
            // Only clear the selection/detail cache if the deleted goal was the
            // one currently showing -- deleting a different row from the list
            // shouldn't knock the user's current view back to the first goal.
            if (goal.id === activeGoalId) {
                setSelectedId(null)
                setDetail(null)
            }
            await mutateGoals()
        } catch (error) {
            setFormError(error.message)
        }
    }

    return (
        <Layout breadcrumbTitle="Goals">
            <div className="goals-tab">
                <div className="row g-0">
                    <div className="col-xl-4">
                        {(goals ?? []).length > 0 && (
                            <FilterTabs options={VISIBILITY_TABS} value={visibilityFilter} onChange={setVisibilityFilter} className="mb-3" />
                        )}
                        <div className="nav d-block">
                            <div className="row">
                                {filteredGoals.map((goal) => (
                                    <GoalNavItem
                                        key={goal.id}
                                        goal={goal}
                                        isActive={activeGoalId === goal.id}
                                        onSelect={loadDetail}
                                        onDelete={handleDelete}
                                    />
                                ))}
                            </div>
                        </div>
                        {!isCreateFormOpen && (
                            <button
                                type="button"
                                className="add-goals-link w-100 border-0"
                                onClick={() => setIsCreateFormOpen(true)}
                                aria-expanded={isCreateFormOpen}
                                aria-controls="add-goal-form"
                            >
                                <h5 className="mb-0">Add new goal</h5>
                                <i className="fi fi-rr-square-plus" />
                            </button>
                        )}

                        {isCreateFormOpen && (
                            <div className="card mt-3" id="add-goal-form">
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-center mb-2">
                                        <h5 className="mb-0">Add new goal</h5>
                                        <button
                                            type="button"
                                            className="modal-close-btn"
                                            aria-label="Close add goal form"
                                            onClick={() => setIsCreateFormOpen(false)}
                                        >
                                            <i className="fi fi-rr-cross" />
                                        </button>
                                    </div>
                                    <form onSubmit={handleCreate}>
                                        <SharingToggle id="goal-shared" isShared={isShared} onChange={setIsShared} />
                                        <div className="mb-3">
                                            <label className="form-label">Quick pick (optional)</label>
                                            <div className="emoji-picker" role="radiogroup" aria-label="Goal preset">
                                                {GOAL_PRESETS.map((preset) => (
                                                    <button
                                                        key={preset.name}
                                                        type="button"
                                                        role="radio"
                                                        aria-checked={name === preset.name && icon === preset.icon}
                                                        aria-label={preset.name}
                                                        title={preset.name}
                                                        className={`emoji-picker-swatch emoji-picker-swatch--labeled${name === preset.name && icon === preset.icon ? " active" : ""}`}
                                                        onClick={() => { setName(preset.name); setIcon(preset.icon) }}
                                                    >
                                                        <span aria-hidden="true">{preset.icon}</span>
                                                        <span className="emoji-picker-swatch-name">{preset.name}</span>
                                                    </button>
                                                ))}
                                            </div>
                                            <div className="form-text">Pick a preset to prefill the name and icon below, or type your own.</div>
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="goal-name">Name</label>
                                            <input
                                                id="goal-name"
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. Vacation"
                                                value={name}
                                                onChange={(event) => setName(event.target.value)}
                                            />
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="goal-target">Target amount</label>
                                            <input
                                                id="goal-target"
                                                type="number"
                                                step="0.01"
                                                min="0.01"
                                                className="form-control"
                                                placeholder="0.00"
                                                value={targetAmount}
                                                onChange={(event) => setTargetAmount(event.target.value)}
                                            />
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="goal-date">Target date (optional)</label>
                                            <input
                                                id="goal-date"
                                                type="date"
                                                className="form-control"
                                                value={targetDate}
                                                onChange={(event) => setTargetDate(event.target.value)}
                                            />
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label">Icon (optional)</label>
                                            <EmojiPicker value={icon} onChange={setIcon} name="goal-icon" />
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label">Color</label>
                                            <ColorPicker value={color} onChange={setColor} name="goal-color" />
                                        </div>
                                        {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}
                                        <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                            {isSubmitting ? "Adding…" : "Add goal"}
                                        </button>
                                    </form>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="col-xl-8">
                        <div className="goals-tab-content">
                            {!activeGoal ? (
                                <div className="card">
                                    <div className="card-body">
                                        <EmptyState
                                            icon="fi fi-rr-piggy-bank"
                                            message={
                                                (goals ?? []).length === 0
                                                    ? "No savings goals yet."
                                                    : `No ${visibilityFilter} goals.`
                                            }
                                        />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="goals-tab-title d-flex justify-content-between align-items-center flex-wrap gap-2">
                                        <h3 className="mb-0">{activeGoal.icon ? `${activeGoal.icon} ` : ""}{activeGoal.name}</h3>
                                        <div className="d-flex align-items-center gap-2">
                                            <SharingToggle
                                                id="goal-title-shared"
                                                isShared={activeGoal.is_shared}
                                                onChange={(checked) => handleToggleSharing(activeGoal, checked)}
                                                disabled={!isItemCreator(user, activeGoal)}
                                                hint={isItemCreator(user, activeGoal) ? undefined : "Only the creator can change this goal's sharing"}
                                                compact
                                            />
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-primary"
                                                onClick={() => {
                                                    setIsEditFormOpen((open) => !open)
                                                    setFormError(null)
                                                }}
                                                aria-expanded={isEditFormOpen}
                                                aria-controls="edit-goal-form"
                                            >
                                                <i className="fi fi-rr-pencil" /> Edit
                                            </button>
                                        </div>
                                    </div>
                                    {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}

                                    {isEditFormOpen && (
                                        <div className="row mb-3" id="edit-goal-form">
                                            <div className="col-xl-12">
                                                <div className="card">
                                                    <div className="card-header">
                                                        <h4 className="card-title">Edit goal</h4>
                                                    </div>
                                                    <div className="card-body">
                                                        <GoalEditForm
                                                            goal={activeGoal}
                                                            onSubmit={handleEdit}
                                                            onCancel={() => setIsEditFormOpen(false)}
                                                            isSubmitting={isSubmitting}
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
                                                            <span>Saved</span>
                                                            <h3>{formatCurrency(activeGoal.current_amount)}</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Goal</span>
                                                            <h3>{formatCurrency(activeGoal.target_amount)}</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar" style={{ width: `${progressPercent(activeGoal)}%` }} role="progressbar" />
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>{progressPercent(activeGoal)}%</span>
                                                        {activeGoal.target_date && <span>Target: {formatDate(activeGoal.target_date)}</span>}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Add funds</h4>
                                                </div>
                                                <div className="card-body">
                                                    <form className="row g-2 align-items-end" onSubmit={handleAddFunds}>
                                                        <div className="col-md-3">
                                                            <label className="form-label" htmlFor="funds-amount">Amount</label>
                                                            <input
                                                                id="funds-amount"
                                                                type="number"
                                                                step="0.01"
                                                                min="0.01"
                                                                className="form-control"
                                                                value={fundsAmount}
                                                                onChange={(event) => setFundsAmount(event.target.value)}
                                                            />
                                                        </div>
                                                        <div className="col-md-3">
                                                            <label className="form-label" htmlFor="funds-pm">From wallet</label>
                                                            <select
                                                                id="funds-pm"
                                                                className="form-select"
                                                                value={fundsPaymentMethodId}
                                                                onChange={(event) => setFundsPaymentMethodId(event.target.value)}
                                                            >
                                                                <option value="">Choose…</option>
                                                                {(paymentMethods ?? []).map((pm) => (
                                                                    <option key={pm.id} value={pm.id}>{pm.name}</option>
                                                                ))}
                                                            </select>
                                                        </div>
                                                        <div className="col-md-3">
                                                            <label className="form-label" htmlFor="funds-category">Category</label>
                                                            <select
                                                                id="funds-category"
                                                                className="form-select"
                                                                value={fundsCategoryId}
                                                                onChange={(event) => setFundsCategoryId(event.target.value)}
                                                            >
                                                                <option value="">Choose…</option>
                                                                {expenseCategories.map((category) => (
                                                                    <option key={category.id} value={category.id}>
                                                                        {category.emoji ? `${category.emoji} ` : ""}{category.name}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                        </div>
                                                        <div className="col-md-3">
                                                            <label className="form-label" htmlFor="funds-date">Date</label>
                                                            <input
                                                                id="funds-date"
                                                                type="date"
                                                                className="form-control"
                                                                value={fundsDate}
                                                                onChange={(event) => setFundsDate(event.target.value)}
                                                            />
                                                        </div>
                                                        <div className="col-12">
                                                            <label className="form-label" htmlFor="funds-notes">Notes (optional)</label>
                                                            <input
                                                                id="funds-notes"
                                                                type="text"
                                                                className="form-control"
                                                                value={fundsNotes}
                                                                onChange={(event) => setFundsNotes(event.target.value)}
                                                            />
                                                        </div>
                                                        <div className="col-12">
                                                            <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                                                {isSubmitting ? "Adding funds…" : "Add funds"}
                                                            </button>
                                                        </div>
                                                    </form>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">History</h4>
                                                </div>
                                                <div className="card-body">
                                                    {(activeGoal.contributing_transactions ?? []).length === 0 ? (
                                                        <EmptyState icon="fi fi-rr-receipt" message="No contributions yet." />
                                                    ) : (
                                                        <div className="table-responsive">
                                                            <table className="table mb-0 table-responsive-sm goals-history-table">
                                                                <thead>
                                                                    <tr>
                                                                        <th>Date</th>
                                                                        <th>Merchant</th>
                                                                        <th>Amount</th>
                                                                    </tr>
                                                                </thead>
                                                                <tbody>
                                                                    {activeGoal.contributing_transactions.map((contribution) => (
                                                                        <tr key={contribution.id}>
                                                                            <td><span><i className="fi fi-rr-calendar" /></span> {formatDate(contribution.date)}</td>
                                                                            <td>{contribution.merchant}</td>
                                                                            <td><h5>{formatCurrency(contribution.total_amount)}</h5></td>
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
