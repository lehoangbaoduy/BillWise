"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { ApiError, authApi } from "@/lib/api"

export default function SignIn() {
    const router = useRouter()
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

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
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-card-brand">
                    <Link href="/" className="auth-card-brand-link">
                        <img src="/images/logoi.png" alt="" width={28} height={28} />
                        <span>BillWise</span>
                    </Link>
                </div>
                <h1 className="auth-card-title">Welcome back</h1>
                <p className="auth-card-subtitle">Sign in to keep track of your household spending.</p>

                {error && <div className="auth-alert" role="alert">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                    <div className="auth-field">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="auth-field">
                        <div className="auth-field-label-row">
                            <label htmlFor="password">Password</label>
                            <Link href="/reset" className="auth-inline-link">Forgot password?</Link>
                        </div>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="auth-submit" disabled={isSubmitting}>
                        {isSubmitting ? "Signing in…" : "Sign In"}
                    </button>
                </form>

                <p className="auth-card-footer">
                    Don&apos;t have an account? <Link href="/signup">Sign up</Link>
                </p>
            </div>
        </div>
    )
}
