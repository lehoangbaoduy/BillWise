"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { ApiError, authApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"
import AuthField from "@/components/auth/AuthField"
import PlatformViewToggle from "@/components/elements/PlatformViewToggle"
import { usePlatformView } from "@/hooks/usePlatformView"

export default function SignIn() {
    const router = useRouter()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { platformView, setPlatformView } = usePlatformView()

    async function handleSubmit(event) {
        event.preventDefault()
        setError(null)
        setIsSubmitting(true)
        try {
            await authApi.login(email, password)
            router.push("/")
        } catch (err) {
            if (err instanceof ApiError && err.status === 403) {
                setError("Please verify your email before signing in.")
            } else if (err instanceof ApiError && err.status === 429) {
                setError("Too many attempts. Please wait a moment and try again.")
            } else {
                setError("Invalid email or password.")
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <AuthCard title="Welcome back" subtitle="Sign in to keep track of your household spending.">
            {error && <div className="auth-alert" role="alert">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                <AuthField
                    id="email"
                    label="Email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <AuthField
                    id="password"
                    label="Password"
                    type="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    action={<Link href="/reset" className="auth-inline-link">Forgot password?</Link>}
                />
                <div>
                    <div className="auth-field-label-row">
                        <label>View as</label>
                    </div>
                    <PlatformViewToggle variant="auth" platformView={platformView} setPlatformView={setPlatformView} />
                </div>
                <button type="submit" className="auth-submit" disabled={isSubmitting}>
                    {isSubmitting ? "Signing in…" : "Sign In"}
                </button>
            </form>

            <p className="auth-card-footer">
                Don&apos;t have an account? <Link href="/signup">Sign up</Link>
            </p>
        </AuthCard>
    )
}
