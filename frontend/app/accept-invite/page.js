"use client"

import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { Suspense, useState } from "react"
import { ApiError, householdApi } from "@/lib/api"

function AcceptInviteContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const token = searchParams.get("token")
    const [displayName, setDisplayName] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [error, setError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function handleSubmit(event) {
        event.preventDefault()
        setError(null)

        if (!displayName.trim()) {
            setError("Please enter your name.")
            return
        }
        if (password.length < 8) {
            setError("Password must be at least 8 characters.")
            return
        }
        if (password !== confirmPassword) {
            setError("Passwords don't match.")
            return
        }

        setIsSubmitting(true)
        try {
            await householdApi.acceptInvite(token, password, displayName.trim())
            router.push("/signin")
        } catch (err) {
            if (err instanceof ApiError && err.status === 409) {
                setError("An account with that email already exists.")
            } else if (err instanceof ApiError && err.status === 400) {
                setError("This invite is invalid, expired, or has already been used.")
            } else {
                setError("Something went wrong. Please try again.")
            }
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
                                    <p>This invite link is missing a token. Ask the household owner to resend it.</p>
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
                                    <h4>Join your household</h4>
                                    {error && <div className="alert alert-danger">{error}</div>}
                                    <form onSubmit={handleSubmit}>
                                        <div className="row">
                                            <div className="col-12 mb-3">
                                                <label className="form-label" htmlFor="invite-display-name">Your name</label>
                                                <input
                                                    id="invite-display-name"
                                                    type="text"
                                                    className="form-control"
                                                    value={displayName}
                                                    onChange={(e) => setDisplayName(e.target.value)}
                                                    required
                                                />
                                            </div>
                                            <div className="col-12 mb-3">
                                                <label className="form-label" htmlFor="invite-password">Password</label>
                                                <input
                                                    id="invite-password"
                                                    type="password"
                                                    className="form-control"
                                                    value={password}
                                                    onChange={(e) => setPassword(e.target.value)}
                                                    required
                                                />
                                            </div>
                                            <div className="col-12 mb-3">
                                                <label className="form-label" htmlFor="invite-confirm-password">Confirm password</label>
                                                <input
                                                    id="invite-confirm-password"
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
                                                {isSubmitting ? "Joining…" : "Accept invite"}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function AcceptInvite() {
    return (
        <Suspense fallback={null}>
            <AcceptInviteContent />
        </Suspense>
    )
}
