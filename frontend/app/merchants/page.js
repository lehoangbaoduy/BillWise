'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmptyState from "@/components/elements/EmptyState"
import FilterTabs from "@/components/elements/FilterTabs"
import { useAuth } from "@/hooks/useAuth"
import { merchantsApi } from "@/lib/api"

const _OTHER_GROUP = "Other"

function groupByType(merchants) {
    const groups = new Map()
    for (const merchant of merchants) {
        const groupName = merchant.type || _OTHER_GROUP
        if (!groups.has(groupName)) groups.set(groupName, [])
        groups.get(groupName).push(merchant)
    }
    return [...groups.entries()].sort(([a], [b]) => {
        if (a === _OTHER_GROUP) return 1
        if (b === _OTHER_GROUP) return -1
        return a.localeCompare(b)
    })
}

function typeTabsFor(merchants) {
    const distinctTypes = [...new Set(merchants.map((m) => m.type).filter(Boolean))].sort((a, b) => a.localeCompare(b))
    const tabs = [{ value: "all", label: "All" }, ...distinctTypes.map((type) => ({ value: type, label: type }))]
    if (merchants.some((m) => !m.type)) tabs.push({ value: _OTHER_GROUP, label: _OTHER_GROUP })
    return tabs
}

function MerchantList({ merchants, canManage, onEdit, onDelete, editingId, emptyMessage }) {
    if (merchants.length === 0) {
        return (
            <div className="card">
                <div className="card-body">
                    <EmptyState icon="fi fi-rr-shop" message={emptyMessage} />
                </div>
            </div>
        )
    }

    return (
        <div className="card">
            <div className="card-body">
                {groupByType(merchants).map(([groupName, groupMerchants]) => (
                    <div key={groupName} className="category-type mb-3">
                        <h5 className="mb-2">{groupName}</h5>
                        <ul>
                            {groupMerchants.map((merchant) => (
                                <li key={merchant.id}>
                                    <div className="left-category">
                                        <button
                                            type="button"
                                            className={`btn btn-link p-0 text-start text-decoration-none${merchant.id === editingId ? " fw-bold" : ""}`}
                                            onClick={() => onEdit(merchant)}
                                        >
                                            {merchant.name}
                                            {(merchant.city || merchant.state) && (
                                                <span className="text-muted small ms-2">
                                                    {[merchant.city, merchant.state].filter(Boolean).join(", ")}
                                                </span>
                                            )}
                                        </button>
                                    </div>
                                    {canManage && (
                                        <div className="right-category">
                                            <ConfirmButton
                                                className="btn btn-sm btn-outline-danger"
                                                aria-label={`Delete ${merchant.name}`}
                                                message={`Delete merchant "${merchant.name}"?`}
                                                onConfirm={() => onDelete(merchant)}
                                            >
                                                <i className="fi fi-rr-trash" />
                                            </ConfirmButton>
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </div>
    )
}

const _EMPTY_FORM = { name: "", type: "", city: "", state: "", notes: "" }

export default function Merchants() {
    const { user } = useAuth()
    const canManage = Boolean(user?.can_manage_finances)
    const { data: merchants, mutate } = useSWR(user ? "/merchants" : null, () => merchantsApi.list())

    const [form, setForm] = useState(_EMPTY_FORM)
    const [editingId, setEditingId] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [typeFilter, setTypeFilter] = useState("all")

    const typeTabs = typeTabsFor(merchants ?? [])
    // Falls back to "all" if the selected type's last merchant was just
    // deleted, so the filter never points at a tab that no longer exists.
    const effectiveTypeFilter = typeTabs.some((tab) => tab.value === typeFilter) ? typeFilter : "all"
    const visibleMerchants =
        effectiveTypeFilter === "all"
            ? merchants ?? []
            : (merchants ?? []).filter((merchant) => (merchant.type || _OTHER_GROUP) === effectiveTypeFilter)

    function updateField(field, value) {
        setForm((current) => ({ ...current, [field]: value }))
    }

    function startEditing(merchant) {
        setEditingId(merchant.id)
        setForm({
            name: merchant.name,
            type: merchant.type ?? "",
            city: merchant.city ?? "",
            state: merchant.state ?? "",
            notes: merchant.notes ?? "",
        })
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
        const payload = {
            name: form.name.trim(),
            type: form.type.trim() || null,
            city: form.city.trim() || null,
            state: form.state.trim() || null,
            notes: form.notes.trim() || null,
        }
        try {
            if (editingId) {
                await merchantsApi.update(editingId, payload)
            } else {
                await merchantsApi.create(payload)
            }
            await mutate()
            cancelEditing()
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDelete(merchant) {
        try {
            await merchantsApi.remove(merchant.id)
            await mutate()
            if (editingId === merchant.id) cancelEditing()
        } catch (error) {
            setFormError(error.message)
        }
    }

    return (
        <Layout breadcrumbTitle="Merchants">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <AnalyticsMenu />
                    <div className="row">
                        {canManage && (
                            <div className="col-xxl-4 col-xl-4 col-lg-6">
                                <div className="card">
                                    <div className="card-header d-flex justify-content-between align-items-center">
                                        <h4 className="card-title">{editingId ? "Edit merchant" : "Add a new merchant"}</h4>
                                        {editingId && (
                                            <button type="button" className="btn btn-sm btn-outline-secondary" onClick={cancelEditing}>
                                                Cancel
                                            </button>
                                        )}
                                    </div>
                                    <div className="card-body">
                                        <form className="row" onSubmit={handleSubmit}>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="merchant-name">Name</label>
                                                <input
                                                    id="merchant-name"
                                                    type="text"
                                                    className="form-control"
                                                    placeholder="e.g. Costco"
                                                    value={form.name}
                                                    onChange={(event) => updateField("name", event.target.value)}
                                                />
                                            </div>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="merchant-type">Type (optional)</label>
                                                <input
                                                    id="merchant-type"
                                                    type="text"
                                                    className="form-control"
                                                    placeholder="e.g. Whole sale, Restaurant, US Market"
                                                    value={form.type}
                                                    onChange={(event) => updateField("type", event.target.value)}
                                                />
                                            </div>
                                            <div className="mb-3 col-6">
                                                <label className="form-label" htmlFor="merchant-city">City (optional)</label>
                                                <input
                                                    id="merchant-city"
                                                    type="text"
                                                    className="form-control"
                                                    value={form.city}
                                                    onChange={(event) => updateField("city", event.target.value)}
                                                />
                                            </div>
                                            <div className="mb-3 col-6">
                                                <label className="form-label" htmlFor="merchant-state">State (optional)</label>
                                                <input
                                                    id="merchant-state"
                                                    type="text"
                                                    className="form-control"
                                                    value={form.state}
                                                    onChange={(event) => updateField("state", event.target.value)}
                                                />
                                            </div>
                                            <div className="mb-3 col-12">
                                                <label className="form-label" htmlFor="merchant-notes">Notes (optional)</label>
                                                <input
                                                    id="merchant-notes"
                                                    type="text"
                                                    className="form-control"
                                                    value={form.notes}
                                                    onChange={(event) => updateField("notes", event.target.value)}
                                                />
                                            </div>
                                            {formError && <div className="col-12 text-danger mb-3" role="alert">{formError}</div>}
                                            <div className="col-12">
                                                <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                                    {isSubmitting ? "Saving…" : editingId ? "Save changes" : "Add merchant"}
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div className={canManage ? "col-xxl-8 col-xl-8 col-lg-6" : "col-xxl-12 col-xl-12"}>
                            {(merchants ?? []).length > 0 && (
                                <FilterTabs options={typeTabs} value={effectiveTypeFilter} onChange={setTypeFilter} className="mb-3" />
                            )}
                            <MerchantList
                                merchants={visibleMerchants}
                                canManage={canManage}
                                onEdit={startEditing}
                                onDelete={handleDelete}
                                editingId={editingId}
                                emptyMessage={(merchants ?? []).length === 0 ? "No merchants yet." : `No merchants of type "${effectiveTypeFilter}".`}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
