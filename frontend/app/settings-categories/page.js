'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmojiPicker from "@/components/elements/EmojiPicker"
import EmptyState from "@/components/elements/EmptyState"
import FilterTabs from "@/components/elements/FilterTabs"
import { useAuth } from "@/hooks/useAuth"
import { categoriesApi } from "@/lib/api"

const TYPE_TABS = [
    { value: "all", label: "All" },
    { value: "expense", label: "Expense" },
    { value: "income", label: "Income" },
]

function CategoryList({ title, categories, onEdit, onDelete, editingId }) {
    return (
        <div className="card">
            <div className="card-header">
                <h4 className="card-title">{title}</h4>
            </div>
            <div className="card-body">
                {categories.length === 0 ? (
                    <EmptyState icon="fi fi-rr-tags" message={`No ${title.toLowerCase()} yet.`} />
                ) : (
                    <div className="category-type">
                        <ul>
                            {categories.map((category) => (
                                <li key={category.id}>
                                    <div className="left-category">
                                        <button
                                            type="button"
                                            className={`btn btn-link p-0 text-start text-decoration-none${category.id === editingId ? " fw-bold" : ""}`}
                                            onClick={() => onEdit(category)}
                                        >
                                            {category.emoji ? `${category.emoji} ` : ""}{category.name}
                                        </button>
                                    </div>
                                    <div className="right-category">
                                        <ConfirmButton
                                            className="btn btn-sm btn-outline-danger"
                                            aria-label={`Delete ${category.name}`}
                                            message={`Delete category "${category.name}"?`}
                                            onConfirm={() => onDelete(category)}
                                        >
                                            <i className="fi fi-rr-trash" />
                                        </ConfirmButton>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    )
}

const _EMPTY_FORM = { name: "", categoryType: "expense", emoji: "" }

export default function SettingsCategories() {
    const { user } = useAuth()
    const { data: categories, mutate } = useSWR(user ? "/categories" : null, () => categoriesApi.list())

    const [form, setForm] = useState(_EMPTY_FORM)
    const [editingId, setEditingId] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [typeFilter, setTypeFilter] = useState("all")

    const incomeCategories = (categories ?? []).filter((c) => c.category_type === "income")
    const expenseCategories = (categories ?? []).filter((c) => c.category_type === "expense")

    function updateField(field, value) {
        setForm((current) => ({ ...current, [field]: value }))
    }

    function startEditing(category) {
        setEditingId(category.id)
        setForm({ name: category.name, categoryType: category.category_type, emoji: category.emoji ?? "" })
        setFormError(null)
    }

    function cancelEditing() {
        setEditingId(null)
        setForm(_EMPTY_FORM)
        setFormError(null)
    }

    async function handleSubmit(event) {
        event.preventDefault()
        if (!form.name.trim()) {
            setFormError("Name is required.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            if (editingId) {
                // category_type is immutable after creation (CategoryUpdate doesn't
                // accept it) -- only name/emoji are ever sent for an edit.
                await categoriesApi.update(editingId, { name: form.name.trim(), emoji: form.emoji.trim() || null })
            } else {
                await categoriesApi.create({
                    name: form.name.trim(),
                    category_type: form.categoryType,
                    emoji: form.emoji.trim() || null,
                })
            }
            await mutate()
            cancelEditing()
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDelete(category) {
        try {
            await categoriesApi.remove(category.id)
            await mutate()
            if (editingId === category.id) cancelEditing()
        } catch (error) {
            setFormError(error.message)
        }
    }

    return (
        <Layout breadcrumbTitle="Categories">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <AnalyticsMenu />
                    <div className="row">
                        <div className="col-xxl-4 col-xl-4 col-lg-6">
                            <div className="card">
                                <div className="card-header d-flex justify-content-between align-items-center">
                                    <h4 className="card-title">{editingId ? "Edit category" : "Create a new category"}</h4>
                                    {editingId && (
                                        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={cancelEditing}>
                                            Cancel
                                        </button>
                                    )}
                                </div>
                                <div className="card-body">
                                    <div className="create-new-category">
                                        <form className="row" onSubmit={handleSubmit}>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="category-name">Name</label>
                                                <input
                                                    id="category-name"
                                                    type="text"
                                                    className="form-control"
                                                    placeholder="category name"
                                                    value={form.name}
                                                    onChange={(event) => updateField("name", event.target.value)}
                                                />
                                            </div>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="category-type">Type</label>
                                                <select
                                                    id="category-type"
                                                    className="form-select"
                                                    value={form.categoryType}
                                                    onChange={(event) => updateField("categoryType", event.target.value)}
                                                    disabled={Boolean(editingId)}
                                                >
                                                    <option value="expense">Expense</option>
                                                    <option value="income">Income</option>
                                                </select>
                                                {editingId && <div className="form-text">Type can&apos;t be changed after creation.</div>}
                                            </div>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="category-emoji">Icon (optional)</label>
                                                <EmojiPicker value={form.emoji} onChange={(value) => updateField("emoji", value)} name="category-emoji" />
                                            </div>
                                            {formError && <div className="col-12 text-danger mb-3" role="alert">{formError}</div>}
                                            <div className="col-12">
                                                <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                                    {isSubmitting ? "Saving…" : editingId ? "Save changes" : "Create new category"}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-xxl-8 col-xl-8 col-lg-6">
                            <FilterTabs options={TYPE_TABS} value={typeFilter} onChange={setTypeFilter} className="mb-3" />
                            {(typeFilter === "all" || typeFilter === "income") && (
                                <CategoryList title="Income Categories" categories={incomeCategories} onEdit={startEditing} onDelete={handleDelete} editingId={editingId} />
                            )}
                            {(typeFilter === "all" || typeFilter === "expense") && (
                                <CategoryList title="Expense Categories" categories={expenseCategories} onEdit={startEditing} onDelete={handleDelete} editingId={editingId} />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
