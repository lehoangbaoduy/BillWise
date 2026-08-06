'use client'
import { useMemo, useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import CircularProgress from "@/components/elements/CircularProgress"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmptyState from "@/components/elements/EmptyState"
import EmojiPicker, { EMOJI_PRESETS } from "@/components/elements/EmojiPicker"
import SharingBadge from "@/components/elements/SharingBadge"
import SharingToggle from "@/components/elements/SharingToggle"
import { useAuth } from "@/hooks/useAuth"
import { budgetsApi, categoriesApi, dashboardApi } from "@/lib/api"
import { isItemCreator } from "@/lib/sharing"

// Deterministic per-category fallback so a category without its own emoji
// still gets a real icon (never the generic tag glyph) and keeps the same
// pick across renders/reloads.
function fallbackEmojiFor(categoryId) {
    let hash = 0
    for (let index = 0; index < categoryId.length; index += 1) {
        hash = (hash * 31 + categoryId.charCodeAt(index)) >>> 0
    }
    return EMOJI_PRESETS[hash % EMOJI_PRESETS.length]
}

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

function formatCurrency(value) {
    return `$${Number(value ?? 0).toFixed(2)}`
}

function budgetPercent(item) {
    return Math.min(100, Math.round(Number(item?.budget_percentage_used ?? 0)))
}

function BudgetAmountForm({ activeItem, onSubmit, isSubmitting }) {
    const [amount, setAmount] = useState("")

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit(Number(amount || 0))
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="d-flex gap-2 mb-3">
                <label className="visually-hidden" htmlFor="edit-budget-amount">New budget amount</label>
                <input
                    id="edit-budget-amount"
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-control"
                    placeholder={String(activeItem.budget_amount)}
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                />
                <button type="submit" className="btn btn-success" disabled={isSubmitting}>
                    Save
                </button>
            </div>
        </form>
    )
}

function BudgetNavItem({ item, emoji, isShared, isActive, onSelect, onDelete }) {
    return (
        <div className="col-xl-12 col-md-6">
            <div className={isActive ? "budgets-nav active w-100" : "budgets-nav w-100"}>
                <button
                    type="button"
                    className="budgets-nav-trigger"
                    aria-pressed={isActive}
                    onClick={() => onSelect(item.category_id)}
                >
                    <CircularProgress value={budgetPercent(item)} height={50} width={50} margin="0 15px 0 0" variant="budget" />
                    <div className="budgets-nav-text">
                        <h3>
                            {emoji || fallbackEmojiFor(item.category_id)} {item.name}
                            {" "}<SharingBadge isShared={isShared} />
                        </h3>
                        <p><strong>{formatCurrency(item.amount)}</strong> / {formatCurrency(item.budget_amount)}</p>
                    </div>
                </button>
                <div className="budgets-nav-actions">
                    {item.is_over_budget && <span className="show-time">Over budget</span>}
                    <ConfirmButton
                        className="btn btn-sm btn-outline-danger"
                        aria-label={`Delete budget for ${item.name}`}
                        message={`Remove the budget for "${item.name}"?`}
                        onConfirm={() => onDelete(item)}
                    >
                        <i className="fi fi-rr-trash" />
                    </ConfirmButton>
                </div>
            </div>
        </div>
    )
}

export default function Budgets() {
    const { user } = useAuth()
    const today = new Date()
    const [month, setMonth] = useState(today.getMonth() + 1)
    const [year, setYear] = useState(today.getFullYear())
    const [selectedCategoryId, setSelectedCategoryId] = useState(null)
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
    const [newCategoryId, setNewCategoryId] = useState("")
    const [isCustomCategory, setIsCustomCategory] = useState(false)
    const [customCategoryName, setCustomCategoryName] = useState("")
    const [customCategoryEmoji, setCustomCategoryEmoji] = useState("")
    const [newAmount, setNewAmount] = useState("")
    const [newIsShared, setNewIsShared] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)

    const periodKey = `${year}-${String(month).padStart(2, "0")}`
    const { data: items, mutate: mutateBreakdown } = useSWR(
        ["/dashboard/category-breakdown", periodKey],
        () => dashboardApi.categoryBreakdown(month, year)
    )
    const { data: budgetRows, mutate: mutateBudgets } = useSWR(
        ["/budgets", periodKey],
        () => budgetsApi.list(month, year)
    )
    const { data: categories, mutate: mutateCategories } = useSWR("/categories", () => categoriesApi.list())

    async function refresh() {
        await Promise.all([mutateBreakdown(), mutateBudgets(), mutateCategories()])
    }

    const budgetByCategory = useMemo(
        () => new Map((budgetRows ?? []).map((row) => [row.category_id, row])),
        [budgetRows]
    )
    const categoriesById = useMemo(
        () => new Map((categories ?? []).map((category) => [category.id, category])),
        [categories]
    )
    const budgetedItems = (items ?? []).filter((item) => item.budget_amount !== null)
    const activeItem = budgetedItems.find((item) => item.category_id === selectedCategoryId) ?? budgetedItems[0] ?? null
    const activeBudget = activeItem ? budgetByCategory.get(activeItem.category_id) : null
    const expenseCategories = (categories ?? []).filter((category) => category.category_type === "expense")
    const budgetedCategoryIds = new Set(budgetedItems.map((item) => item.category_id))
    const availableCategories = expenseCategories.filter((category) => !budgetedCategoryIds.has(category.id))

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
        setSelectedCategoryId(null)
    }

    async function handleCreate(event) {
        event.preventDefault()
        if (isCustomCategory) {
            if (!customCategoryName.trim()) {
                setFormError("Enter a name for the new category.")
                return
            }
        } else if (!newCategoryId) {
            setFormError("Choose a category.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            let categoryId = newCategoryId
            if (isCustomCategory) {
                const category = await categoriesApi.create({
                    name: customCategoryName.trim(),
                    emoji: customCategoryEmoji.trim() || null,
                    category_type: "expense",
                })
                categoryId = category.id
            }
            await budgetsApi.create({
                category_id: categoryId,
                month,
                year,
                budget_amount: Number(newAmount || 0),
                is_shared: newIsShared,
            })
            await refresh()
            setNewCategoryId("")
            setIsCustomCategory(false)
            setCustomCategoryName("")
            setCustomCategoryEmoji("")
            setNewAmount("")
            setNewIsShared(false)
            setIsCreateFormOpen(false)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleUpdateAmount(amount) {
        if (!activeItem || !activeBudget) return
        setIsSubmitting(true)
        setFormError(null)
        try {
            await budgetsApi.update(activeBudget.id, { budget_amount: amount })
            await refresh()
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleToggleSharing(budget, isShared) {
        setFormError(null)
        try {
            await budgetsApi.updateSharing(budget.id, isShared)
            await refresh()
        } catch (error) {
            setFormError(error.message)
        }
    }

    async function handleDelete(item) {
        if (!item) return
        const budgetId = budgetByCategory.get(item.category_id)?.id
        if (!budgetId) return
        setFormError(null)
        try {
            await budgetsApi.remove(budgetId)
            await refresh()
            // Only clear the selection if the deleted item was the one showing in
            // the detail panel -- deleting a different row shouldn't knock the
            // user's current view back to the first budget in the list.
            if (selectedCategoryId === item.category_id) setSelectedCategoryId(null)
        } catch (error) {
            setFormError(error.message)
        }
    }

    const progressPercent = activeItem ? Math.min(100, Number(activeItem.budget_percentage_used ?? 0)) : 0

    return (
        <Layout breadcrumbTitle="Budgets">
            <div className="budgets-tab">
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => changePeriod(-1)}>
                        <i className="fi fi-rr-angle-left" />
                    </button>
                    <h5 className="mb-0">{MONTH_NAMES[month - 1]} {year}</h5>
                    <button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => changePeriod(1)}>
                        <i className="fi fi-rr-angle-right" />
                    </button>
                </div>
                <div className="row g-0">
                    <div className="col-xl-4">
                        <div className="nav d-block">
                            <div className="row">
                                {budgetedItems.map((item) => (
                                    <BudgetNavItem
                                        key={item.category_id}
                                        item={item}
                                        emoji={categoriesById.get(item.category_id)?.emoji}
                                        isShared={budgetByCategory.get(item.category_id)?.is_shared ?? false}
                                        isActive={activeItem?.category_id === item.category_id}
                                        onSelect={setSelectedCategoryId}
                                        onDelete={handleDelete}
                                    />
                                ))}
                            </div>
                        </div>
                        {!isCreateFormOpen && (
                            <button
                                type="button"
                                className="add-budgets-link w-100 border-0"
                                onClick={() => setIsCreateFormOpen(true)}
                                aria-expanded={isCreateFormOpen}
                                aria-controls="add-budget-form"
                            >
                                <h5 className="mb-0">Add new budget</h5>
                                <i className="fi fi-rr-square-plus" />
                            </button>
                        )}

                        {isCreateFormOpen && (
                            <div className="card mt-3" id="add-budget-form">
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-center mb-2">
                                        <h5 className="mb-0">Add new budget</h5>
                                        <button
                                            type="button"
                                            className="modal-close-btn"
                                            aria-label="Close add budget form"
                                            onClick={() => {
                                                setIsCreateFormOpen(false)
                                                setIsCustomCategory(false)
                                                setCustomCategoryName("")
                                                setCustomCategoryEmoji("")
                                            }}
                                        >
                                            <i className="fi fi-rr-cross" />
                                        </button>
                                    </div>
                                    <form onSubmit={handleCreate}>
                                        <SharingToggle id="budget-shared" isShared={newIsShared} onChange={setNewIsShared} />
                                        <div className="mb-3">
                                            <label className="form-label">Category</label>
                                            <div className="emoji-picker" role="radiogroup" aria-label="Category">
                                                {availableCategories.map((category) => (
                                                    <button
                                                        key={category.id}
                                                        type="button"
                                                        role="radio"
                                                        aria-checked={!isCustomCategory && newCategoryId === category.id}
                                                        aria-label={category.name}
                                                        title={category.name}
                                                        className={`emoji-picker-swatch emoji-picker-swatch--labeled${!isCustomCategory && newCategoryId === category.id ? " active" : ""}`}
                                                        onClick={() => { setNewCategoryId(category.id); setIsCustomCategory(false) }}
                                                    >
                                                        <span aria-hidden="true">{category.emoji || fallbackEmojiFor(category.id)}</span>
                                                        <span className="emoji-picker-swatch-name">{category.name}</span>
                                                    </button>
                                                ))}
                                                <button
                                                    type="button"
                                                    role="radio"
                                                    aria-checked={isCustomCategory}
                                                    aria-label="Custom category"
                                                    title="Create a new category"
                                                    className={`emoji-picker-swatch emoji-picker-swatch--labeled${isCustomCategory ? " active" : ""}`}
                                                    onClick={() => { setIsCustomCategory(true); setNewCategoryId("") }}
                                                >
                                                    <span aria-hidden="true">➕</span>
                                                    <span className="emoji-picker-swatch-name">Custom</span>
                                                </button>
                                            </div>
                                            <div className="form-text">
                                                {isCustomCategory
                                                    ? "Type a name and pick an icon below to create a new category."
                                                    : newCategoryId
                                                        ? `Selected: ${availableCategories.find((c) => c.id === newCategoryId)?.name ?? ""}`
                                                        : "Choose a category above, or create your own."}
                                            </div>
                                        </div>
                                        {isCustomCategory && (
                                            <>
                                                <div className="mb-3">
                                                    <label className="form-label" htmlFor="custom-category-name">New category name</label>
                                                    <input
                                                        id="custom-category-name"
                                                        type="text"
                                                        className="form-control"
                                                        placeholder="e.g. Pet Care"
                                                        value={customCategoryName}
                                                        onChange={(event) => setCustomCategoryName(event.target.value)}
                                                    />
                                                </div>
                                                <div className="mb-3">
                                                    <label className="form-label">Icon (optional)</label>
                                                    <EmojiPicker value={customCategoryEmoji} onChange={setCustomCategoryEmoji} name="custom-category-icon" />
                                                </div>
                                            </>
                                        )}
                                        <div className="mb-3">
                                            <label className="form-label" htmlFor="budget-amount">Monthly budget</label>
                                            <input
                                                id="budget-amount"
                                                type="number"
                                                step="0.01"
                                                min="0"
                                                className="form-control"
                                                placeholder="0.00"
                                                value={newAmount}
                                                onChange={(event) => setNewAmount(event.target.value)}
                                            />
                                        </div>
                                        {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}
                                        <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                            {isSubmitting ? "Adding…" : "Add budget"}
                                        </button>
                                    </form>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="col-xl-8">
                        <div className="budgets-tab-content">
                            {!activeItem ? (
                                <div className="card">
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-wallet" message="No budgets set for this month yet." />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="budgets-tab-title d-flex justify-content-between align-items-center flex-wrap gap-2">
                                        <h3 className="mb-0">{activeItem.name}</h3>
                                        {activeBudget && (
                                            <SharingToggle
                                                id="budget-title-shared"
                                                isShared={activeBudget.is_shared}
                                                onChange={(checked) => handleToggleSharing(activeBudget, checked)}
                                                disabled={!isItemCreator(user, activeBudget)}
                                                hint={isItemCreator(user, activeBudget) ? undefined : "Only the creator can change this budget's sharing"}
                                                compact
                                            />
                                        )}
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Spend</span>
                                                            <h3>{formatCurrency(activeItem.amount)}</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Budget</span>
                                                            <h3>{formatCurrency(activeItem.budget_amount)}</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div
                                                            className={activeItem.is_over_budget ? "progress-bar bg-danger" : "progress-bar"}
                                                            style={{ width: `${progressPercent}%` }}
                                                            role="progressbar"
                                                        />
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>{activeItem.budget_percentage_used ?? 0}% used</span>
                                                        {activeItem.is_over_budget && <span className="text-danger">Over budget</span>}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Edit budget amount</h4>
                                                </div>
                                                <div className="card-body">
                                                    <BudgetAmountForm
                                                        key={activeBudget?.id}
                                                        activeItem={activeItem}
                                                        onSubmit={handleUpdateAmount}
                                                        isSubmitting={isSubmitting}
                                                    />
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
