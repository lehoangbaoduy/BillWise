"use client"

import Link from "next/link"
import { useState } from "react"
import { authApi } from "@/lib/api"

export default function Reset() {
    const [email, setEmail] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSubmitted, setIsSubmitted] = useState(false)

    async function handleSubmit(event) {
        event.preventDefault()
        setIsSubmitting(true)
        try {
            await authApi.requestPasswordReset(email)
        } finally {
            // Always show the same confirmation regardless of outcome, so this
            // endpoint can't be used to enumerate which emails have accounts.
            setIsSubmitting(false)
            setIsSubmitted(true)
        }
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
                                    <h4>Reset password</h4>
                                    {isSubmitted ? (
                                        <p className="mt-3">If an account exists for that email, a reset link has been sent.</p>
                                    ) : (
                                        <form onSubmit={handleSubmit}>
                                            <div className="row">
                                                <div className="col-12 mb-3">
                                                    <label className="form-label" htmlFor="reset-email">Email</label>
                                                    <input
                                                        id="reset-email"
                                                        name="email"
                                                        type="email"
                                                        className="form-control"
                                                        value={email}
                                                        onChange={(e) => setEmail(e.target.value)}
                                                        required
                                                    />
                                                </div>
                                            </div>
                                            <div className="mt-3 d-grid gap-2">
                                                <button type="submit" className="btn btn-primary me-8 text-white" disabled={isSubmitting}>
                                                    {isSubmitting ? "Sending..." : "Submit"}
                                                </button>
                                            </div>
                                        </form>
                                    )}
                                    <p className="mt-3 mb-0">Already have an account?<Link className="text-primary" href="/signin"> Sign In</Link></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
