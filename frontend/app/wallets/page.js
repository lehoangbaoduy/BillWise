'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import EmptyState from "@/components/elements/EmptyState"
import StatementUploadPanel from "@/components/statement/StatementUploadPanel"
import { dashboardApi, paymentMethodsApi, transactionsApi } from "@/lib/api"

const TYPE_OPTIONS = ["Credit Card", "Debit Card", "Cash", "Tracked Savings", "Other"]

const TYPE_ICONS = {
    "Credit Card": "fi fi-rr-credit-card",
    "Debit Card": "fi fi-rr-credit-card",
    "Cash": "fi fi-rr-money-bill-wave-alt",
    "Tracked Savings": "fi fi-rr-piggy-bank",
    "Other": "fi fi-rr-wallet",
}

const CARD_VISUAL_CLASS = {
    "Credit Card": "visa",
    "Debit Card": "master",
}

function formatCurrency(value) {
    if (value === null || value === undefined) return null
    return `$${Number(value).toFixed(2)}`
}

function maskedLastFour(lastFourOptional) {
    return `•••• •••• •••• ${lastFourOptional || "????"}`
}

function WalletNavItem({ method, isActive, onSelect }) {
    return (
        <div className="col-xl-12 col-md-6">
            <button
                type="button"
                className={isActive ? "wallet-nav active w-100 border-0 text-start" : "wallet-nav w-100 border-0 text-start"}
                aria-pressed={isActive}
                onClick={() => onSelect(method.id)}
            >
                <div className="wallet-nav-icon">
                    <span><i className={TYPE_ICONS[method.type] || "fi fi-rr-wallet"} /></span>
                </div>
                <div className="wallet-nav-text">
                    <h3>{method.name}</h3>
                    <p>{formatCurrency(method.current_balance) || method.type}</p>
                </div>
            </button>
        </div>
    )
}

function CreditCardVisual({ method }) {
    return (
        <div className={`credit-card ${CARD_VISUAL_CLASS[method.type] || ""}`}>
            <div className="type-brand">
                <h4>{method.type}</h4>
                <i className="fi fi-rr-sim-card" style={{ fontSize: "22px", color: "#fff" }} />
            </div>
            <div className="cc-number">
                <h6>{maskedLastFour(method.last_four_optional)}</h6>
            </div>
            <div className="cc-holder-exp">
                <h5>{method.name}</h5>
                {method.default_cashback_rate !== null && method.default_cashback_rate !== undefined && (
                    <div className="exp"><span>Cashback:</span><strong> {method.default_cashback_rate}%</strong></div>
                )}
            </div>
        </div>
    )
}

function TrackedBalanceVisual({ method }) {
    return (
        <div className="card">
            <div className="card-body">
                <div className="wallet-total-balance">
                    <p className="mb-0">{method.issuer || method.type}</p>
                    <h2>{formatCurrency(method.current_balance) ?? "—"}</h2>
                </div>
            </div>
        </div>
    )
}

export default function Wallets() {
    const { data: methods, mutate } = useSWR("/payment-methods", () => paymentMethodsApi.list())

    const [selectedId, setSelectedId] = useState(null)
    const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)
    const [name, setName] = useState("")
    const [type, setType] = useState(TYPE_OPTIONS[0])
    const [issuer, setIssuer] = useState("")
    const [lastFour, setLastFour] = useState("")
    const [currentBalance, setCurrentBalance] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formError, setFormError] = useState(null)
    const [deletingId, setDeletingId] = useState(null)
    const [isImportingStatement, setIsImportingStatement] = useState(false)
    const [importSuccess, setImportSuccess] = useState(null)

    const activeMethod = (methods ?? []).find((method) => method.id === selectedId) ?? (methods ?? [])[0] ?? null

    const totalBalance = (methods ?? []).reduce((sum, method) => sum + Number(method.current_balance ?? 0), 0)

    const now = new Date()
    const { data: monthBreakdown } = useSWR(
        ["/dashboard/payment-method-breakdown", now.getMonth() + 1, now.getFullYear()],
        () => dashboardApi.paymentMethodBreakdown(now.getMonth() + 1, now.getFullYear())
    )
    const monthSpend = (monthBreakdown ?? []).find((row) => row.payment_method_id === activeMethod?.id)?.amount ?? 0

    const { data: walletTransactions } = useSWR(
        activeMethod ? ["/transactions", activeMethod.id] : null,
        () => transactionsApi.list({ payment_method_id: activeMethod.id })
    )

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
            const created = await paymentMethodsApi.create({
                name: name.trim(),
                type,
                issuer: issuer.trim() || null,
                last_four_optional: lastFour || null,
                current_balance: currentBalance === "" ? null : Number(currentBalance),
            })
            await mutate()
            handleSelectWallet(created.id)
            setName("")
            setType(TYPE_OPTIONS[0])
            setIssuer("")
            setLastFour("")
            setCurrentBalance("")
            setIsCreateFormOpen(false)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    function handleSelectWallet(id) {
        setSelectedId(id)
        setIsImportingStatement(false)
        setImportSuccess(null)
    }

    async function handleStatementConfirm(newBalance) {
        await paymentMethodsApi.update(activeMethod.id, { current_balance: newBalance })
        await mutate()
        setIsImportingStatement(false)
        setImportSuccess(`Balance updated to ${formatCurrency(newBalance)}.`)
    }

    async function handleDelete(method) {
        if (!window.confirm(`Delete "${method.name}"?`)) return
        setDeletingId(method.id)
        try {
            await paymentMethodsApi.remove(method.id)
            await mutate()
            if (selectedId === method.id) handleSelectWallet(null)
            setFormError(null)
        } catch (error) {
            setFormError(error.message)
        } finally {
            setDeletingId(null)
        }
    }

    return (
        <Layout breadcrumbTitle="Wallets">
            <div className="wallet-tab">
                <div className="row g-0">
                    <div className="col-xl-4">
                        {(methods ?? []).length > 0 && (
                            <div className="card mb-3">
                                <div className="card-body">
                                    <p className="mb-0 text-muted">Total balance</p>
                                    <h3 className="mb-0">{formatCurrency(totalBalance)}</h3>
                                </div>
                            </div>
                        )}
                        <div className="nav d-block">
                            <div className="row">
                                {(methods ?? []).map((method) => (
                                    <WalletNavItem
                                        key={method.id}
                                        method={method}
                                        isActive={activeMethod?.id === method.id}
                                        onSelect={handleSelectWallet}
                                    />
                                ))}
                            </div>
                        </div>
                        <button
                            type="button"
                            className="add-card-link w-100 border-0"
                            onClick={() => setIsCreateFormOpen((open) => !open)}
                            aria-expanded={isCreateFormOpen}
                            aria-controls="add-wallet-form"
                        >
                            <h5 className="mb-0">Add new wallet</h5>
                            <i className="fi fi-rr-square-plus" />
                        </button>

                        {isCreateFormOpen && (
                            <div className="card mt-3" id="add-wallet-form">
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
                        )}
                    </div>

                    <div className="col-xl-8">
                        <div className="wallet-tab-content">
                            {!activeMethod ? (
                                <div className="card">
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-wallet" message="No payment methods added yet." />
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="wallet-tab-title d-flex justify-content-between align-items-center">
                                        <h3>{activeMethod.name}</h3>
                                        <div className="d-flex gap-2">
                                            {!isImportingStatement && (
                                                <button
                                                    type="button"
                                                    className="btn btn-sm btn-outline-primary"
                                                    onClick={() => {
                                                        setIsImportingStatement(true)
                                                        setImportSuccess(null)
                                                    }}
                                                >
                                                    Import statement
                                                </button>
                                            )}
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-danger"
                                                aria-label={`Delete ${activeMethod.name}`}
                                                disabled={deletingId === activeMethod.id}
                                                onClick={() => handleDelete(activeMethod)}
                                            >
                                                <i className="fi fi-rr-trash" />
                                            </button>
                                        </div>
                                    </div>

                                    {importSuccess && (
                                        <div className="alert alert-success" role="status">{importSuccess}</div>
                                    )}

                                    {isImportingStatement ? (
                                        <div className="card">
                                            <div className="card-body">
                                                <StatementUploadPanel
                                                    onConfirm={handleStatementConfirm}
                                                    onCancel={() => setIsImportingStatement(false)}
                                                />
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="row">
                                                <div className="col-xxl-6 col-xl-12 col-lg-6">
                                                    {["Credit Card", "Debit Card"].includes(activeMethod.type) ? (
                                                        <CreditCardVisual method={activeMethod} />
                                                    ) : (
                                                        <TrackedBalanceVisual method={activeMethod} />
                                                    )}
                                                </div>
                                            </div>

                                            <div className="card mt-3">
                                                <div className="card-body">
                                                    <p className="mb-0 text-muted">This month&apos;s spending</p>
                                                    <h4 className="mb-0">{formatCurrency(monthSpend)}</h4>
                                                </div>
                                            </div>

                                            <div className="card mt-3">
                                                <div className="card-body">
                                                    <h5 className="card-title">Recent transactions</h5>
                                                    {(walletTransactions ?? []).length === 0 ? (
                                                        <EmptyState icon="fi fi-rr-receipt" message="No transactions for this wallet yet." />
                                                    ) : (
                                                        <ul className="list-group list-group-flush">
                                                            {walletTransactions.slice(0, 10).map((transaction) => (
                                                                <li key={transaction.id} className="list-group-item d-flex justify-content-between align-items-center">
                                                                    <div>
                                                                        <div>{transaction.merchant}</div>
                                                                        <small className="text-muted">{transaction.date}</small>
                                                                    </div>
                                                                    <span>{formatCurrency(transaction.total_amount)}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    )}
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
