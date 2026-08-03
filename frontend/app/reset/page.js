"use client"

import Link from "next/link"
import { useState } from "react"
import { authApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"
import AuthField from "@/components/auth/AuthField"

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
        <AuthCard
            title="Reset password"
            subtitle={isSubmitted ? undefined : "Enter your email and we'll send you a reset link."}
        >
            {isSubmitted ? (
                <div className="auth-card-message">
                    <p>If an account exists for that email, a reset link has been sent.</p>
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                    <AuthField
                        id="reset-email"
                        label="Email"
                        type="email"
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <button type="submit" className="auth-submit" disabled={isSubmitting}>
                        {isSubmitting ? "Sending…" : "Submit"}
                    </button>
                </form>
            )}

            <p className="auth-card-footer">
                Already have an account? <Link href="/signin">Sign In</Link>
            </p>
        </AuthCard>
    )
}
