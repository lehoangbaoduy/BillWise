"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { ApiError, authApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"
import AuthField from "@/components/auth/AuthField"

export default function SignUp() {
    const router = useRouter()
    const [fullName, setFullName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [acceptTerms, setAcceptTerms] = useState(false)
    const [error, setError] = useState(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function handleSubmit(event) {
        event.preventDefault()
        setError(null)

        if (!acceptTerms) {
            setError("Please accept the User Agreement and Privacy Policy.")
            return
        }
        if (password.length < 8) {
            setError("Password must be at least 8 characters.")
            return
        }

        setIsSubmitting(true)
        try {
            await authApi.register(email, password, fullName)
            router.push(`/verify-email?email=${encodeURIComponent(email)}`)
        } catch (err) {
            if (err instanceof ApiError && err.status === 409) {
                setError("An account with that email already exists.")
            } else if (err instanceof ApiError && err.status === 422) {
                setError("Please check your details and try again.")
            } else {
                setError("Something went wrong. Please try again.")
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <AuthCard title="Create your account" subtitle="Track shared expenses with your household in one place.">
            {error && <div className="auth-alert" role="alert">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form-fields" noValidate>
                <AuthField
                    id="fullName"
                    label="Full name"
                    type="text"
                    autoComplete="name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                />
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
                    autoComplete="new-password"
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <div className="auth-checkbox">
                    <input
                        id="acceptTerms"
                        type="checkbox"
                        checked={acceptTerms}
                        onChange={(e) => setAcceptTerms(e.target.checked)}
                    />
                    <label htmlFor="acceptTerms">
                        I certify that I am 18 years of age or older, and agree to the{" "}
                        <Link href="#">User Agreement</Link> and <Link href="#">Privacy Policy</Link>.
                    </label>
                </div>
                <button type="submit" className="auth-submit" disabled={isSubmitting}>
                    {isSubmitting ? "Creating account…" : "Sign Up"}
                </button>
            </form>

            <p className="auth-card-footer">
                Already have an account? <Link href="/signin">Sign In</Link>
            </p>
        </AuthCard>
    )
}
