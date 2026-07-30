'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import EmptyState from "@/components/elements/EmptyState"
import { paymentMethodsApi } from "@/lib/api"

const TYPE_OPTIONS = ["Credit Card", "Debit Card", "Cash", "Tracked Savings", "Other"]

const TYPE_ICONS = {
    "Credit Card": "fi fi-rr-credit-card",
    "Debit Card": "fi fi-rr-credit-card",
    "Cash": "fi fi-rr-money-bill-wave-alt",
    "Tracked Savings": "fi fi-rr-piggy-bank",
    "Other": "fi fi-rr-wallet",
}

function formatCurrency(value) {
    if (value === null || value === undefined) return null
    return `$${Number(value).toFixed(2)}`
}

function PaymentMethodCard({ method, onDelete, isDeleting }) {
    return (
        <div className="col-xl-4 col-lg-6 col-md-6">
            <div className="card">
                <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start">
                        <div className="d-flex align-items-center">
                            <span className="me-3"><i className={TYPE_ICONS[method.type] || "fi fi-rr-wallet"} /></span>
                            <div>
                                <h5 className="mb-0">{method.name}</h5>
                                <span className="text-muted">{method.type}</span>
                            </div>
                        </div>
                        <button
                            type="button"
                            className="btn btn-sm btn-outline-danger"
                            aria-label={`Delete ${method.name}`}
                            disabled={isDeleting}
                            onClick={() => onDelete(method)}
                        >
                            <i className="fi fi-rr-trash" />
                        </button>
                    </div>
                    <div className="mt-3">
                        {method.issuer && <p className="mb-1">{method.issuer}</p>}
                        {method.last_four_optional && <p className="mb-1">•••• {method.last_four_optional}</p>}
                        {formatCurrency(method.current_balance) && <p className="mb-1">Balance: {formatCurrency(method.current_balance)}</p>}
                        {method.default_cashback_rate !== null && method.default_cashback_rate !== undefined && (
                            <p className="mb-1">Cashback: {method.default_cashback_rate}%</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function Wallets() {
    const { data: methods, mutate } = useSWR("/payment-methods", () => paymentMethodsApi.list())

    const [name, setName] = useState("")
    const [type, setType] = useState(TYPE_OPTIONS[0])
    const [issuer, setIssuer] = useState("")
    const [lastFour, setLastFour] = useState("")
    const [currentBalance, setCurrentBalance] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [deletingId, setDeletingId] = useState(null)

    async function handleCreate(event) {
        event.preventDefault()
        if (!name.trim()) {
            setFormError("Name is required.")
            return
        }
        if (lastFour && lastFour.length !== 4) {
            setFormError("Last four digits must be exactly 4 digits.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            await paymentMethodsApi.create({
                name: name.trim(),
                type,
                issuer: issuer.trim() || null,
                last_four_optional: lastFour || null,
                current_balance: currentBalance === "" ? null : Number(currentBalance),
            })
            await mutate()
            setName("")
            setType(TYPE_OPTIONS[0])
            setIssuer("")
            setLastFour("")
            setCurrentBalance("")
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDelete(method) {
        if (!window.confirm(`Delete "${method.name}"?`)) return
        setDeletingId(method.id)
        try {
            await paymentMethodsApi.remove(method.id)
            await mutate()
            setFormError(null)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setDeletingId(null)
        }
    }

    return (
        <Layout breadcrumbTitle="Wallets">
            <div className="row">
                <div className="col-xl-4 col-lg-5">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Add a payment method</h4>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleCreate}>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="payment-method-name">Name</label>
                                    <input
                                        id="payment-method-name"
                                        type="text"
                                        className="form-control"
                                        placeholder="e.g. Everyday Visa"
                                        value={name}
                                        onChange={(event) => setName(event.target.value)}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="payment-method-type">Type</label>
                                    <select id="payment-method-type" className="form-select" value={type} onChange={(event) => setType(event.target.value)}>
                                        {TYPE_OPTIONS.map((option) => (
                                            <option key={option} value={option}>{option}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="payment-method-issuer">Issuer (optional)</label>
                                    <input
                                        id="payment-method-issuer"
                                        type="text"
                                        className="form-control"
                                        placeholder="e.g. Chase"
                                        value={issuer}
                                        onChange={(event) => setIssuer(event.target.value)}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="payment-method-last-four">Last 4 digits (optional)</label>
                                    <input
                                        id="payment-method-last-four"
                                        type="text"
                                        className="form-control"
                                        placeholder="1234"
                                        value={lastFour}
                                        maxLength={4}
                                        onChange={(event) => setLastFour(event.target.value.replace(/\D/g, ""))}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="payment-method-balance">Current balance (optional)</label>
                                    <input
                                        id="payment-method-balance"
                                        type="number"
                                        step="0.01"
                                        className="form-control"
                                        placeholder="0.00"
                                        value={currentBalance}
                                        onChange={(event) => setCurrentBalance(event.target.value)}
                                    />
                                </div>
                                {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}
                                <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                    {isSubmitting ? "Adding…" : "Add payment method"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
                <div className="col-xl-8 col-lg-7">
                    {(methods ?? []).length === 0 ? (
                        <div className="card">
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-wallet" message="No payment methods added yet." />
                            </div>
                        </div>
                    ) : (
                        <div className="row">
                            {methods.map((method) => (
                                <PaymentMethodCard key={method.id} method={method} onDelete={handleDelete} isDeleting={deletingId === method.id} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    )
}
