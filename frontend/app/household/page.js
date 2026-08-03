'use client'
import { useState } from "react"
import useSWR from "swr"
import Layout from "@/components/layout/Layout"
import ConfirmButton from "@/components/elements/ConfirmButton"
import EmptyState from "@/components/elements/EmptyState"
import { useAuth } from "@/hooks/useAuth"
import { ApiError, householdApi } from "@/lib/api"

function formatDate(value) {
    if (!value) return "—"
    const [year, month, day] = value.slice(0, 10).split("-").map(Number)
    return new Date(year, month - 1, day).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" })
}

export default function Household() {
    const { user, isLoading: isAuthLoading } = useAuth()
    const isOwner = user?.role === "owner"
    const { data: household, mutate, error } = useSWR(isOwner ? "/household" : null, () => householdApi.get())

    const [email, setEmail] = useState("")
    const [canAddTransactions, setCanAddTransactions] = useState(false)
    const [formError, setFormError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [actioningId, setActioningId] = useState(null)

    async function handleInvite(event) {
        event.preventDefault()
        if (!email.trim()) {
            setFormError("Email is required.")
            return
        }
        setIsSubmitting(true)
        setFormError(null)
        try {
            await householdApi.invitePartner(email.trim(), canAddTransactions)
            await mutate()
            setEmail("")
            setCanAddTransactions(false)
        } catch (err) {
            if (err instanceof ApiError && err.status === 409) {
                setFormError("This email can't be invited right now. Please try again later.")
            } else {
                setFormError(err.message)
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    async function handleCancelInvite(invite) {
        setActioningId(invite.id)
        try {
            await householdApi.removePartner(invite.id)
            await mutate()
        } catch (err) {
            setFormError(err.message)
        } finally {
            setActioningId(null)
        }
    }

    async function handleRevokePartner(partner) {
        setActioningId(partner.id)
        try {
            await householdApi.removePartner(partner.id)
            await mutate()
        } catch (err) {
            setFormError(err.message)
        } finally {
            setActioningId(null)
        }
    }

    async function handleTogglePermission(partner) {
        setActioningId(partner.id)
        try {
            await householdApi.updatePermissions(partner.id, !partner.can_add_transactions)
            await mutate()
        } catch (err) {
            setFormError(err.message)
        } finally {
            setActioningId(null)
        }
    }

    if (isAuthLoading) return null

    if (!isOwner) {
        return (
            <Layout breadcrumbTitle="Household">
                <div className="card">
                    <div className="card-body">
                        <EmptyState icon="fi fi-rr-lock" message="Only the household owner can manage partner access." />
                    </div>
                </div>
            </Layout>
        )
    }

    return (
        <Layout breadcrumbTitle="Household">
            <div className="row">
                <div className="col-xxl-4 col-xl-4 col-lg-6">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Invite a partner</h4>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleInvite}>
                                <div className="mb-3">
                                    <label className="form-label" htmlFor="partner-email">Email</label>
                                    <input
                                        id="partner-email"
                                        type="email"
                                        className="form-control"
                                        placeholder="partner@example.com"
                                        value={email}
                                        onChange={(event) => setEmail(event.target.value)}
                                    />
                                </div>
                                <div className="mb-3 form-check">
                                    <input
                                        id="partner-can-add-transactions"
                                        type="checkbox"
                                        className="form-check-input"
                                        checked={canAddTransactions}
                                        onChange={(event) => setCanAddTransactions(event.target.checked)}
                                    />
                                    <label className="form-check-label" htmlFor="partner-can-add-transactions">
                                        Allow adding transactions
                                    </label>
                                </div>
                                {formError && <div className="text-danger mb-3" role="alert">{formError}</div>}
                                <button type="submit" className="btn btn-success w-100" disabled={isSubmitting}>
                                    {isSubmitting ? "Sending invite…" : "Send invite"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <div className="col-xxl-8 col-xl-8 col-lg-6">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Pending invites</h4>
                        </div>
                        <div className="card-body">
                            {error ? (
                                <div className="text-danger" role="alert">Could not load household data.</div>
                            ) : (household?.pending_invites ?? []).length === 0 ? (
                                <EmptyState icon="fi fi-rr-envelope" message="No pending invites." />
                            ) : (
                                <ul className="list-unstyled mb-0">
                                    {household.pending_invites.map((invite) => (
                                        <li key={invite.id} className="d-flex justify-content-between align-items-center py-2 border-bottom">
                                            <div>
                                                <div>{invite.email}</div>
                                                <small className="text-muted">
                                                    {invite.can_add_transactions ? "Can add transactions" : "View only"} · Expires {formatDate(invite.expires_at)}
                                                </small>
                                            </div>
                                            <ConfirmButton
                                                className="btn btn-sm btn-outline-danger"
                                                aria-label={`Cancel invite to ${invite.email}`}
                                                disabled={actioningId === invite.id}
                                                message={`Cancel the invite to ${invite.email}?`}
                                                onConfirm={() => handleCancelInvite(invite)}
                                            >
                                                Cancel
                                            </ConfirmButton>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>

                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Household partners</h4>
                        </div>
                        <div className="card-body">
                            {(household?.partners ?? []).length === 0 ? (
                                <EmptyState icon="fi fi-rr-users" message="No partners yet." />
                            ) : (
                                <ul className="list-unstyled mb-0">
                                    {household.partners.map((partner) => (
                                        <li key={partner.id} className="d-flex justify-content-between align-items-center py-2 border-bottom">
                                            <div>
                                                <div>
                                                    {partner.display_name || partner.email}
                                                    {!partner.is_active && <span className="text-muted"> (revoked)</span>}
                                                </div>
                                                <small className="text-muted">{partner.email} · Joined {formatDate(partner.joined_at)}</small>
                                            </div>
                                            {partner.is_active && (
                                                <div className="d-flex gap-2">
                                                    <button
                                                        type="button"
                                                        className="btn btn-sm btn-outline-secondary"
                                                        aria-label={`${partner.can_add_transactions ? "Prevent" : "Allow"} ${partner.display_name || partner.email} from adding transactions`}
                                                        disabled={actioningId === partner.id}
                                                        onClick={() => handleTogglePermission(partner)}
                                                    >
                                                        {partner.can_add_transactions ? "Can add transactions" : "View only"}
                                                    </button>
                                                    <ConfirmButton
                                                        className="btn btn-sm btn-outline-danger"
                                                        aria-label={`Revoke access for ${partner.display_name || partner.email}`}
                                                        disabled={actioningId === partner.id}
                                                        message={`Revoke ${partner.display_name || partner.email}'s access? This ends their session immediately.`}
                                                        onConfirm={() => handleRevokePartner(partner)}
                                                    >
                                                        Revoke
                                                    </ConfirmButton>
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
        </Layout>
    )
}
