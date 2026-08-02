'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import EmptyState from "@/components/elements/EmptyState"
import { dashboardApi, netWorthApi } from "@/lib/api"

const ACCOUNT_TYPE_OPTIONS = [
    { value: "asset", label: "Asset" },
    { value: "liability", label: "Liability" },
]

function todayIso() {
    // toISOString() reports the UTC date, which can be a day ahead of/behind
    // the user's local date near midnight — same class of bug as formatDate.
    const today = new Date()
    const month = String(today.getMonth() + 1).padStart(2, "0")
    const day = String(today.getDate()).padStart(2, "0")
    return `${today.getFullYear()}-${month}-${day}`
}

function formatCurrency(value) {
    if (value === null || value === undefined) return "—"
    return `$${Number(value).toFixed(2)}`
}

function formatDate(value) {
    if (!value) return "—"
    // Date-only strings ("YYYY-MM-DD") parse as UTC midnight; rendering that
    // in a timezone behind UTC rolls the displayed date back a day. Build the
    // Date from the Y/M/D components directly so it's always local-midnight.
    const [year, month, day] = value.split("-").map(Number)
    return new Date(year, month - 1, day).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
}

function AccountForm({ initial, onSubmit, isSubmitting, submitLabel }) {
    const [name, setName] = useState(initial?.name ?? "")
    const [type, setType] = useState(initial?.type ?? "asset")

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit({ name: name.trim(), type })
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="row g-2">
                <div className="col-md-7">
                    <label className="form-label" htmlFor="account-name">Account name</label>
                    <input
                        id="account-name"
                        type="text"
                        className="form-control"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                    />
                </div>
                <div className="col-md-5">
                    <label className="form-label" htmlFor="account-type">Type</label>
                    <select id="account-type" className="form-select" value={type} onChange={(event) => setType(event.target.value)}>
                        {ACCOUNT_TYPE_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                    </select>
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

function SnapshotForm({ accounts, onSubmit, isSubmitting }) {
    const [snapshotDate, setSnapshotDate] = useState(todayIso())
    const [notes, setNotes] = useState("")
    const [balances, setBalances] = useState(() => Object.fromEntries(accounts.map((account) => [account.id, ""])))

    function setBalance(accountId, value) {
        setBalances((current) => ({ ...current, [accountId]: value }))
    }

    function handleSubmit(event) {
        event.preventDefault()
        onSubmit({
            snapshot_date: snapshotDate,
            notes: notes.trim() || null,
            balances: accounts.map((account) => ({ account_id: account.id, balance: Number(balances[account.id] || 0) })),
        })
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="row g-2">
                <div className="col-md-6">
                    <label className="form-label" htmlFor="snapshot-date">Snapshot date</label>
                    <input
                        id="snapshot-date"
                        type="date"
                        className="form-control"
                        value={snapshotDate}
                        onChange={(event) => setSnapshotDate(event.target.value)}
                    />
                </div>
                <div className="col-md-6">
                    <label className="form-label" htmlFor="snapshot-notes">Notes (optional)</label>
                    <input
                        id="snapshot-notes"
                        type="text"
                        className="form-control"
                        value={notes}
                        onChange={(event) => setNotes(event.target.value)}
                    />
                </div>
                {accounts.map((account) => (
                    <div className="col-md-6" key={account.id}>
                        <label className="form-label" htmlFor={`snapshot-balance-${account.id}`}>
                            {account.name} <span className="text-muted small">({account.type})</span>
                        </label>
                        <input
                            id={`snapshot-balance-${account.id}`}
                            type="number"
                            step="0.01"
                            className="form-control"
                            value={balances[account.id]}
                            onChange={(event) => setBalance(account.id, event.target.value)}
                            required
                        />
                    </div>
                ))}
                <div className="col-12">
                    <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                        {isSubmitting ? "Saving…" : "Record snapshot"}
                    </button>
                </div>
            </div>
        </form>
    )
}

export default function NetWorth() {
    const { data: dashboard, mutate: mutateDashboard } = useSWR("/dashboard/net-worth", () => dashboardApi.netWorth())
    const { data: accounts, mutate: mutateAccounts } = useSWR("/net-worth-accounts", () => netWorthApi.listAccounts())

    const [isAccountFormOpen, setIsAccountFormOpen] = useState(false)
    // Independent error states: the "Add account" panel and an account's inline
    // edit view can both be on screen at once, same as the Cashback rules and
    // Recurring Bills forms — a single shared error would leak between them.
    const [createAccountError, setCreateAccountError] = useState(null)
    const [editAccountError, setEditAccountError] = useState(null)
    const [editingAccountId, setEditingAccountId] = useState(null)
    const [isSnapshotFormOpen, setIsSnapshotFormOpen] = useState(false)
    const [snapshotError, setSnapshotError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const changeVsPrevious = dashboard?.change_vs_previous
    const changeClass = changeVsPrevious > 0 ? "text-success" : changeVsPrevious < 0 ? "text-danger" : ""

    async function handleCreateAccount(payload) {
        if (!payload.name) {
            setCreateAccountError("Account name is required.")
            return
        }
        setIsSubmitting(true)
        setCreateAccountError(null)
        try {
            await netWorthApi.createAccount(payload)
            await mutateAccounts()
            setIsAccountFormOpen(false)
        } catch (error) {
            setCreateAccountError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleUpdateAccount(accountId, payload) {
        setIsSubmitting(true)
        setEditAccountError(null)
        try {
            await netWorthApi.updateAccount(accountId, payload)
            await mutateAccounts()
            setEditingAccountId(null)
        } catch (error) {
            setEditAccountError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleDeleteAccount(account) {
        if (!window.confirm(`Remove "${account.name}" from Net Worth tracking?`)) return
        setEditAccountError(null)
        try {
            await netWorthApi.removeAccount(account.id)
            await mutateAccounts()
        } catch (error) {
            setEditAccountError(error.message)
        }
    }

    async function handleCreateSnapshot(payload) {
        setIsSubmitting(true)
        setSnapshotError(null)
        try {
            await netWorthApi.createSnapshot(payload)
            await mutateDashboard()
            setIsSnapshotFormOpen(false)
        } catch (error) {
            setSnapshotError(error.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    const activeAccounts = accounts ?? []
    const history = dashboard?.history ?? []
    const breakdown = dashboard?.breakdown ?? []

    return (
        <Layout breadcrumbTitle="Net Worth">
            <div className="net-worth-tab">
                <div className="row">
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-primary"><span><i className="fi fi-rr-stats" /></span></div>
                            <div className="widget-content">
                                <p>Current net worth</p>
                                <h3>{formatCurrency(dashboard?.current_net_worth)}</h3>
                                {changeVsPrevious !== null && changeVsPrevious !== undefined && (
                                    <span className={`small ${changeClass}`}>
                                        {changeVsPrevious > 0 ? "+" : ""}{formatCurrency(changeVsPrevious)} vs previous
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-success"><span><i className="fi fi-rr-sack-dollar" /></span></div>
                            <div className="widget-content">
                                <p>Total assets</p>
                                <h3>{formatCurrency(dashboard?.total_assets)}</h3>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-sm-6">
                        <div className="analytics-widget">
                            <div className="widget-icon me-3 bg-warning"><span><i className="fi fi-rr-credit-card" /></span></div>
                            <div className="widget-content">
                                <p>Total liabilities</p>
                                <h3>{formatCurrency(dashboard?.total_liabilities)}</h3>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xl-6">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Latest breakdown</h4>
                            </div>
                            <div className="card-body">
                                {breakdown.length === 0 ? (
                                    <EmptyState icon="fi fi-rr-stats" message="No snapshot recorded yet." />
                                ) : (
                                    <ul className="list-group list-group-flush">
                                        {breakdown.map((row) => (
                                            <li key={row.account_id} className="list-group-item d-flex justify-content-between align-items-center">
                                                <span>{row.account_name} <span className="text-muted small">({row.account_type})</span></span>
                                                <span>{formatCurrency(row.balance)}</span>
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
                                <h4 className="card-title">History</h4>
                            </div>
                            <div className="card-body">
                                {history.length === 0 ? (
                                    <EmptyState icon="fi fi-rr-time-past" message="No snapshots yet." />
                                ) : (
                                    <div className="table-responsive">
                                        <table className="table mb-0 table-responsive-sm">
                                            <thead>
                                                <tr>
                                                    <th>Date</th>
                                                    <th>Assets</th>
                                                    <th>Liabilities</th>
                                                    <th>Net worth</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {[...history].reverse().map((snapshot) => (
                                                    <tr key={snapshot.id}>
                                                        <td>{formatDate(snapshot.snapshot_date)}</td>
                                                        <td>{formatCurrency(snapshot.total_assets)}</td>
                                                        <td>{formatCurrency(snapshot.total_liabilities)}</td>
                                                        <td>{formatCurrency(snapshot.net_worth)}</td>
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

                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <h4 className="card-title">Record a snapshot</h4>
                                <button
                                    type="button"
                                    className="btn btn-sm btn-outline-primary"
                                    disabled={activeAccounts.length === 0}
                                    onClick={() => {
                                        setIsSnapshotFormOpen((open) => !open)
                                        setSnapshotError(null)
                                    }}
                                    aria-expanded={isSnapshotFormOpen}
                                    aria-controls="record-snapshot-form"
                                >
                                    New snapshot
                                </button>
                            </div>
                            <div className="card-body">
                                {activeAccounts.length === 0 ? (
                                    <EmptyState icon="fi fi-rr-wallet" message="Add at least one account below before recording a snapshot." />
                                ) : isSnapshotFormOpen ? (
                                    <div id="record-snapshot-form">
                                        {snapshotError && <div className="text-danger mb-3" role="alert">{snapshotError}</div>}
                                        <SnapshotForm accounts={activeAccounts} onSubmit={handleCreateSnapshot} isSubmitting={isSubmitting} />
                                    </div>
                                ) : (
                                    <p className="text-muted mb-0">Record balances for all {activeAccounts.length} active account(s) to update your net worth.</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header d-flex justify-content-between align-items-center">
                                <h4 className="card-title">Accounts</h4>
                                <button
                                    type="button"
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={() => {
                                        setIsAccountFormOpen((open) => !open)
                                        setCreateAccountError(null)
                                    }}
                                    aria-expanded={isAccountFormOpen}
                                    aria-controls="add-account-form"
                                >
                                    Add account
                                </button>
                            </div>
                            <div className="card-body">
                                {isAccountFormOpen && (
                                    <div className="mb-4" id="add-account-form">
                                        {createAccountError && <div className="text-danger mb-3" role="alert">{createAccountError}</div>}
                                        <AccountForm onSubmit={handleCreateAccount} isSubmitting={isSubmitting} submitLabel="Add account" />
                                    </div>
                                )}

                                {activeAccounts.length === 0 ? (
                                    <EmptyState icon="fi fi-rr-wallet" message="No net worth accounts yet." />
                                ) : (
                                    <ul className="list-group list-group-flush">
                                        {activeAccounts.map((account) => (
                                            <li key={account.id} className="list-group-item">
                                                {editingAccountId === account.id ? (
                                                    <>
                                                        {editAccountError && <div className="text-danger mb-3" role="alert">{editAccountError}</div>}
                                                        <AccountForm
                                                            initial={account}
                                                            isSubmitting={isSubmitting}
                                                            submitLabel="Save changes"
                                                            onSubmit={(payload) => handleUpdateAccount(account.id, payload)}
                                                        />
                                                        <button
                                                            type="button"
                                                            className="btn btn-sm btn-outline-secondary mt-2"
                                                            onClick={() => {
                                                                setEditingAccountId(null)
                                                                setEditAccountError(null)
                                                            }}
                                                        >
                                                            Cancel
                                                        </button>
                                                    </>
                                                ) : (
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div>
                                                            <strong>{account.name}</strong>
                                                            <span className="text-muted small"> · {account.type}</span>
                                                        </div>
                                                        <div className="d-flex gap-2">
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-outline-secondary"
                                                                aria-label={`Edit account: ${account.name}`}
                                                                onClick={() => {
                                                                    setEditingAccountId(account.id)
                                                                    setEditAccountError(null)
                                                                }}
                                                            >
                                                                <i className="fi fi-rr-pencil" />
                                                            </button>
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-outline-danger"
                                                                aria-label={`Delete account: ${account.name}`}
                                                                onClick={() => handleDeleteAccount(account)}
                                                            >
                                                                <i className="fi fi-rr-trash" />
                                                            </button>
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
