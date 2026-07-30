'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import EmptyState from "@/components/elements/EmptyState"
import { useAuth } from "@/hooks/useAuth"
import { categoriesApi } from "@/lib/api"

function CategoryList({ title, categories, canManage, onDelete, deletingId }) {
    return (
        <div className="card">
            <div className="card-header">
                <h4 className="card-title">{title}</h4>
            </div>
            <div className="card-body">
                {categories.length === 0 ? (
                    <EmptyState icon="fi fi-rr-shapes" message={`No ${title.toLowerCase()} yet.`} />
                ) : (
                    <div className="category-type">
                        <ul>
                            {categories.map((category) => (
                                <li key={category.id}>
                                    <div className="left-category">
                                        <span className="category-icon">
                                            {category.emoji ? `${category.emoji} ` : ""}{category.name}
                                        </span>
                                    </div>
                                    {canManage && (
                                        <div className="right-category">
                                            <button
                                                type="button"
                                                aria-label={`Delete ${category.name}`}
                                                disabled={deletingId === category.id}
                                                onClick={() => onDelete(category)}
                                            >
                                                <i className="fi fi-rr-trash" />
                                            </button>
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    )
}

export default function SettingsCategories() {
    const { user } = useAuth()
    const canManage = user?.role === "owner"
    const { data: categories, mutate } = useSWR(user ? "/categories" : null, () => categoriesApi.list())

    const [name, setName] = useState("")
    const [categoryType, setCategoryType] = useState("expense")
    const [emoji, setEmoji] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [deletingId, setDeletingId] = useState(null)

    const incomeCategories = (categories ?? []).filter((c) => c.category_type === "income")
    const expenseCategories = (categories ?? []).filter((c) => c.category_type === "expense")

    async function handleCreate(event) {
        event.preventDefault()
        if (!name.trim()) {
            setFormError("Name is required.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            await categoriesApi.create({
                name: name.trim(),
                category_type: categoryType,
                emoji: emoji.trim() || null,
            })
            await mutate()
            setName("")
            setEmoji("")
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDelete(category) {
        if (!window.confirm(`Delete category "${category.name}"?`)) return
        setDeletingId(category.id)
        try {
            await categoriesApi.remove(category.id)
            await mutate()
            setFormError(null)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setDeletingId(null)
        }
    }

    return (
        <Layout breadcrumbTitle="Categories">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    <div className="row">
                        {canManage && (
                            <div className="col-xxl-4 col-xl-4 col-lg-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Create a new category</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="create-new-category">
                                            <form className="row" onSubmit={handleCreate}>
                                                <div className="mb-3 col-12">
                                                    <label className="form-label" htmlFor="category-name">Name</label>
                                                    <input
                                                        id="category-name"
                                                        type="text"
                                                        className="form-control"
                                                        placeholder="category name"
                                                        value={name}
                                                        onChange={(event) => setName(event.target.value)}
                                                    />
                                                </div>
                                                <div className="mb-3 col-12">
                                                    <label className="form-label" htmlFor="category-type">Type</label>
                                                    <select
                                                        id="category-type"
                                                        className="form-select"
                                                        value={categoryType}
                                                        onChange={(event) => setCategoryType(event.target.value)}
                                                    >
                                                        <option value="expense">Expense</option>
                                                        <option value="income">Income</option>
                                                    </select>
                                                </div>
                                                <div className="mb-3 col-12">
                                                    <label className="form-label" htmlFor="category-emoji">Emoji (optional)</label>
                                                    <input
                                                        id="category-emoji"
                                                        type="text"
                                                        className="form-control"
                                                        placeholder="e.g. 🛒"
                                                        value={emoji}
                                                        onChange={(event) => setEmoji(event.target.value)}
                                                        maxLength={8}
                                                    />
                                                </div>
                                                {formError && <div className="col-12 text-danger mb-3" role="alert">{formError}</div>}
                                                <div className="col-12">
                                                    <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                                        {isSubmitting ? "Creating…" : "Create new category"}
                                                    </button>
                                                </div>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div className={canManage ? "col-xxl-8 col-xl-8 col-lg-6" : "col-xxl-12 col-xl-12"}>
                            <CategoryList title="Income Categories" categories={incomeCategories} canManage={canManage} onDelete={handleDelete} deletingId={deletingId} />
                            <CategoryList title="Expense Categories" categories={expenseCategories} canManage={canManage} onDelete={handleDelete} deletingId={deletingId} />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
