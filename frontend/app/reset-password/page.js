"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useState } from "react"
import { authApi } from "@/lib/api"

function ResetPasswordContent() {
    const searchParams = useSearchParams()
    const token = searchParams.get("token")
    const [newPassword, setNewPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [error, setError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isDone, setIsDone] = useState(false)

    async function handleSubmit(event) {
        event.preventDefault()
        setError(null)
        if (newPassword !== confirmPassword) {
            setError("Passwords don't match.")
            return
        }
        setIsSubmitting(true)
        try {
            await authApi.confirmPasswordReset(token, newPassword)
            setIsDone(true)
        } catch (err) {
            setError("That reset link is invalid or has expired.")
        } finally {
            setIsSubmitting(false)
        }
    }

    if (!token) {
        return (
            <div className="authincation">
                <div className="container h-100">
                    <div className="row justify-content-center h-100 align-items-center">
                        <div className="col-xl-5 col-md-6">
                            <div className="card">
                                <div className="card-body identity-content text-center p-5">
                                    <p>This reset link is missing a token. <Link href="/reset">Request a new one?</Link></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="authincation">
            <div className="container">
                <div className="row justify-content-center align-items-center g-0">
                    <div className="col-xl-8">
                        <div className="row g-0">
                            <div className="col-lg-6">
                                <div className="welcome-content">
                                    <div className="welcome-title">
                                        <div className="mini-logo">
                                            <Link href="/">
                                                <img src="/images/logo-white.png" alt="" width={30} /></Link>
                                        </div>
                                        <h3>Welcome to BillWise</h3>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6">
                                <div className="auth-form">
                                    <h4>Set a new password</h4>
                                    {isDone ? (
                                        <>
                                            <p className="mt-3">Your password has been reset.</p>
                                            <Link className="btn btn-primary text-white" href="/signin">Sign In</Link>
                                        </>
                                    ) : (
                                        <>
                                            {error && <div className="alert alert-danger">{error}</div>}
                                            <form onSubmit={handleSubmit}>
                                                <div className="row">
                                                    <div className="col-12 mb-3">
                                                        <label className="form-label" htmlFor="new-password">New password</label>
                                                        <input
                                                            id="new-password"
                                                            type="password"
                                                            className="form-control"
                                                            value={newPassword}
                                                            onChange={(e) => setNewPassword(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                    <div className="col-12 mb-3">
                                                        <label className="form-label" htmlFor="confirm-new-password">Confirm new password</label>
                                                        <input
                                                            id="confirm-new-password"
                                                            type="password"
                                                            className="form-control"
                                                            value={confirmPassword}
                                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                                            required
                                                        />
                                                    </div>
                                                </div>
                                                <div className="mt-3 d-grid gap-2">
                                                    <button type="submit" className="btn btn-primary me-8 text-white" disabled={isSubmitting}>
                                                        {isSubmitting ? "Saving..." : "Save new password"}
                                                    </button>
                                                </div>
                                            </form>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function ResetPassword() {
    return (
        <Suspense fallback={null}>
            <ResetPasswordContent />
        </Suspense>
    )
}
