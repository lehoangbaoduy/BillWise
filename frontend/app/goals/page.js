'use client'
import { useState } from "react"
import useSWR from "swr"
import CircularProgress from "@/components/elements/CircularProgress"
import Layout from "@/components/layout/Layout"
import EmptyState from "@/components/elements/EmptyState"
import { categoriesApi, goalsApi, paymentMethodsApi } from "@/lib/api"

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function formatDate(value) {
    if (!value) return "—"
    return new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
}

function progressPercent(goal) {
    if (!goal || Number(goal.target_amount) <= 0) return 0
    return Math.min(100, Math.round((Number(goal.current_amount) / Number(goal.target_amount)) * 100))
}

function GoalNavItem({ goal, isActive, onSelect }) {
    return (
        <div className="col-xl-12 col-md-6">
            <button
                type="button"
                className={isActive ? "goals-nav active w-100 border-0 text-start" : "goals-nav w-100 border-0 text-start"}
                aria-pressed={isActive}
                onClick={() => onSelect(goal.id)}
            >
                <CircularProgress value={progressPercent(goal)} height={50} width={50} margin="0 15px 0 0" />
                <div className="goals-nav-text">
                    <h3>{goal.icon ? `${goal.icon} ` : ""}{goal.name}</h3>
                    <p><strong>{formatCurrency(goal.current_amount)}</strong> / {formatCurrency(goal.target_amount)}</p>
                </div>
            </button>
        </div>
    )
}

export default function Goals() {
    const { data: goals, mutate: mutateGoals } = useSWR("/goals", () => goalsApi.list())
    const { data: paymentMethods } = useSWR("/payment-methods", () => paymentMethodsApi.list())
    const { data: categories } = useSWR("/categories", () => categoriesApi.list())
    const expenseCategories = (categories ?? []).filter((category) => category.category_type === "expense")

    const [selectedId, setSelectedId] = useState(null)
    const [detail, setDetail] = useState(null)
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
    const [formError, setFormError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [name, setName] = useState("")
    const [targetAmount, setTargetAmount] = useState("")
    const [targetDate, setTargetDate] = useState("")
    const [icon, setIcon] = useState("")
    const [color, setColor] = useState("#51BB25")

    const [fundsAmount, setFundsAmount] = useState("")
    const [fundsPaymentMethodId, setFundsPaymentMethodId] = useState("")
    const [fundsCategoryId, setFundsCategoryId] = useState("")
    const [fundsDate, setFundsDate] = useState(() => new Date().toISOString().slice(0, 10))
    const [fundsNotes, setFundsNotes] = useState("")

    const activeGoalId = selectedId ?? (goals ?? [])[0]?.id ?? null
    const activeGoal = detail?.id === activeGoalId ? detail : (goals ?? []).find((goal) => goal.id === activeGoalId) ?? null

    async function loadDetail(goalId) {
        setSelectedId(goalId)
        setFormError(null)
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
                is_shared: false,
            })
            await mutateGoals()
            setName("")
            setTargetAmount("")
            setTargetDate("")
            setIcon("")
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
            setFundsDate(new Date().toISOString().slice(0, 10))
            setFundsNotes("")
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleToggleSharing() {
        if (!activeGoal) return
        setFormError(null)
        try {
            await goalsApi.updateSharing(activeGoal.id, !activeGoal.is_shared)
            await refreshDetail()
        } catch (error) {
            setFormError(error.message)
        }
    }

    async function handleDelete() {
        if (!activeGoal || !window.confirm(`Delete goal "${activeGoal.name}"? Linked transactions will stay, unlinked from this goal.`)) return
        try {
            await goalsApi.remove(activeGoal.id)
            setSelectedId(null)
            setDetail(null)
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
                        <div className="nav d-block">
                            <div className="row">
                                {(goals ?? []).map((goal) => (
                                    <GoalNavItem
                                        key={goal.id}
                                        goal={goal}
                                        isActive={activeGoalId === goal.id}
                                        onSelect={loadDetail}
                                    />
                                ))}
                            </div>
                        </div>
                        <button
                            type="button"
                            className="add-goals-link w-100 border-0"
                            onClick={() => setIsCreateFormOpen((open) => !open)}
                            aria-expanded={isCreateFormOpen}
                            aria-controls="add-goal-form"
                        >
                            <h5 className="mb-0">Add new goal</h5>
                            <i className="fi fi-rr-square-plus" />
                        </button>

                        {isCreateFormOpen && (
                            <div className="card mt-3" id="add-goal-form">
                                <div className="card-body">
                                    <form onSubmit={handleCreate}>
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
                                            <label className="form-label" htmlFor="goal-icon">Icon emoji (optional)</label>
                                            <input
                                                id="goal-icon"
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. ✈️"
                                                maxLength={8}
                                                value={icon}
                                                onChange={(event) => setIcon(event.target.value)}
                                            />
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="goal-color">Color</label>
                                            <input
                                                id="goal-color"
                                                type="color"
                                                className="form-control form-control-color"
                                                value={color}
                                                onChange={(event) => setColor(event.target.value)}
                                            />
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
                                        <EmptyState icon="fi fi-rr-piggy-bank" message="No savings goals yet." />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="goals-tab-title d-flex justify-content-between align-items-center">
                                        <h3>{activeGoal.icon ? `${activeGoal.icon} ` : ""}{activeGoal.name}</h3>
                                        <div className="d-flex gap-2">
                                            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleToggleSharing}>
                                                {activeGoal.is_shared ? "Shared" : "Private"}
                                            </button>
                                            <button type="button" className="btn btn-sm btn-outline-danger" onClick={handleDelete}>
                                                <i className="fi fi-rr-trash" />
                                            </button>
                                        </div>
                                    </div>
                                    {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}
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
