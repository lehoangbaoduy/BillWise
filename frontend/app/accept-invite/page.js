"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Suspense, useState } from "react"
import { ApiError, householdApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"
import AuthField from "@/components/auth/AuthField"

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
            <AuthCard title="Invalid invite">
                <div className="auth-card-message">
                    <p>This invite link is missing a token. Ask the household owner to resend it.</p>
                </div>
            </AuthCard>
        )
    }

    return (
        <AuthCard title="Join your household">
            {error && <div className="auth-alert" role="alert">{error}</div>}
            <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                <AuthField
                    id="invite-display-name"
                    label="Your name"
                    type="text"
                    autoComplete="name"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    required
                />
                <AuthField
                    id="invite-password"
                    label="Password"
                    type="password"
                    autoComplete="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <AuthField
                    id="invite-confirm-password"
                    label="Confirm password"
                    type="password"
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit" className="auth-submit" disabled={isSubmitting}>
                    {isSubmitting ? "Joining…" : "Accept invite"}
                </button>
            </form>
        </AuthCard>
    )
}

export default function AcceptInvite() {
    return (
        <Suspense fallback={null}>
            <AcceptInviteContent />
        </Suspense>
    )
}
