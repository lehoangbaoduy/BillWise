'use client'
import { useState } from "react"
import Link from "next/link"
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import { useAuth } from "@/hooks/useAuth"
import { authApi } from "@/lib/api"

function EditNameForm({ user, onDone, refresh }) {
    const [displayName, setDisplayName] = useState(user?.display_name || "")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)

    async function handleSubmit(event) {
        event.preventDefault()
        setIsSubmitting(true)
        setError(null)
        try {
            await authApi.updateProfile(displayName)
            await refresh()
            onDone()
        } catch (submitError) {
            setError(submitError.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <form className="mt-3" onSubmit={handleSubmit}>
            <label className="form-label" htmlFor="display-name">Name</label>
            <input
                id="display-name"
                type="text"
                className="form-control"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                required
            />
            {error && <div className="text-danger mt-2" role="alert">{error}</div>}
            <div className="d-flex gap-2 mt-2">
                <button type="submit" className="btn btn-success" disabled={isSubmitting}>
                    {isSubmitting ? "Saving…" : "Save"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onDone}>
                    Cancel
                </button>
            </div>
        </form>
    )
}

function ChangePasswordForm({ onDone }) {
    const [currentPassword, setCurrentPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState(null)

    async function handleSubmit(event) {
        event.preventDefault()
        if (newPassword !== confirmPassword) {
            setError("New password and confirmation don't match.")
            return
        }
        setIsSubmitting(true)
        setError(null)
        try {
            await authApi.changePassword(currentPassword, newPassword)
            onDone()
        } catch (submitError) {
            setError(submitError.message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <form className="mt-3" onSubmit={handleSubmit}>
            <label className="form-label" htmlFor="current-password">Current password</label>
            <input
                id="current-password"
                type="password"
                className="form-control mb-2"
                value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)}
                required
            />
            <label className="form-label" htmlFor="new-password">New password</label>
            <input
                id="new-password"
                type="password"
                className="form-control mb-2"
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                minLength={8}
                required
            />
            <label className="form-label" htmlFor="confirm-password">Confirm new password</label>
            <input
                id="confirm-password"
                type="password"
                className="form-control"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                minLength={8}
                required
            />
            {error && <div className="text-danger mt-2" role="alert">{error}</div>}
            <div className="d-flex gap-2 mt-2">
                <button type="submit" className="btn btn-success" disabled={isSubmitting}>
                    {isSubmitting ? "Saving…" : "Change password"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onDone}>
                    Cancel
                </button>
            </div>
        </form>
    )
}

export default function Profile() {
    const { user, refresh } = useAuth()
    const [activeForm, setActiveForm] = useState(null)

    return (
        <Layout breadcrumbTitle="Profile">
            <SettingsMenu />
            <div className="row">
                <div className="col-xl-6">
                    <div className="card">
                        <div className="card-body">
                            <div className="profile-name">
                                <div className="d-flex align-items-center">
                                    <i className="fi fi-rr-user" style={{ fontSize: "2.5rem" }} />
                                    <div className="flex-grow-1 ms-3">
                                        <h4 className="mb-0">{user?.display_name || " "}</h4>
                                        <p className="mb-0">{user?.email || " "}</p>
                                    </div>
                                </div>
                            </div>
                            <div className="profile-reg mt-3">
                                <div className="registered">
                                    <h5>{user?.role === "owner" ? "Owner" : "Partner"}</h5>
                                    <p className="mb-0">Role</p>
                                </div>
                                <span className="reg_divider" />
                                <div className="rank">
                                    <h5>{user?.email_verified ? "Verified" : "Unverified"}</h5>
                                    <p className="mb-0">Email status</p>
                                </div>
                            </div>
                            <div className="d-flex flex-wrap gap-2 mt-3">
                                <Link href="/wallets" className="btn btn-primary">View payment methods</Link>
                                <button
                                    type="button"
                                    className="btn btn-outline-secondary"
                                    onClick={() => setActiveForm(activeForm === "name" ? null : "name")}
                                >
                                    Change name
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-outline-secondary"
                                    onClick={() => setActiveForm(activeForm === "password" ? null : "password")}
                                >
                                    Change password
                                </button>
                            </div>
                            {activeForm === "name" && (
                                <EditNameForm user={user} refresh={refresh} onDone={() => setActiveForm(null)} />
                            )}
                            {activeForm === "password" && (
                                <ChangePasswordForm onDone={() => setActiveForm(null)} />
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-xl-6">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Email Verification</h4>
                        </div>
                        <div className="card-body">
                            <div className="email-verification">
                                <ul>
                                    <li className={user?.email_verified ? "verified" : "pending"}>
                                        <div className="d-flex">
                                            <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                            <div>
                                                <h5>{user?.email || " "}</h5>
                                                {user?.email_verified ? (
                                                    <p><span><i className="fi fi-sr-badge-check" /></span>Verified</p>
                                                ) : (
                                                    <p className="text-danger">
                                                        <span className="text-danger"><i className="fi fi-rs-circle-xmark" /></span>
                                                        Verification pending
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
