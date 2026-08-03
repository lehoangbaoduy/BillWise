"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useState } from "react"
import { authApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"
import AuthField from "@/components/auth/AuthField"

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
            <AuthCard title="Invalid link">
                <div className="auth-card-message">
                    <p>This reset link is missing a token. <Link href="/reset">Request a new one?</Link></p>
                </div>
            </AuthCard>
        )
    }

    if (isDone) {
        return (
            <AuthCard title="Password updated">
                <div className="auth-card-message">
                    <p>Your password has been reset.</p>
                    <Link className="auth-submit" href="/signin">Sign In</Link>
                </div>
            </AuthCard>
        )
    }

    return (
        <AuthCard title="Set a new password">
            {error && <div className="auth-alert" role="alert">{error}</div>}
            <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                <AuthField
                    id="new-password"
                    label="New password"
                    type="password"
                    autoComplete="new-password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                />
                <AuthField
                    id="confirm-new-password"
                    label="Confirm new password"
                    type="password"
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit" className="auth-submit" disabled={isSubmitting}>
                    {isSubmitting ? "Saving…" : "Save new password"}
                </button>
            </form>
        </AuthCard>
    )
}

export default function ResetPassword() {
    return (
        <Suspense fallback={null}>
            <ResetPasswordContent />
        </Suspense>
    )
}
