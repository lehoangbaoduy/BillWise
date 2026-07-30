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
        <>
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
                                        <h4>Sign In</h4>
                                        {error && <div className="alert alert-danger">{error}</div>}
                                        <form onSubmit={handleSubmit}>
                                            <div className="row">
                                                <div className="col-12 mb-3">
                                                    <label className="form-label">Email</label>
                                                    <input
                                                        name="email"
                                                        type="email"
                                                        className="form-control"
                                                        value={email}
                                                        onChange={(e) => setEmail(e.target.value)}
                                                        required
                                                    />
                                                </div>
                                                <div className="col-12 mb-3">
                                                    <label className="form-label">Password</label>
                                                    <input
                                                        name="password"
                                                        type="password"
                                                        className="form-control"
                                                        value={password}
                                                        onChange={(e) => setPassword(e.target.value)}
                                                        required
                                                    />
                                                </div>
                                                <div className="col-6 text-end ms-auto">
                                                    <Link href="/reset">Forgot Password?</Link>
                                                </div>
                                            </div>
                                            <div className="mt-3 d-grid gap-2">
                                                <button type="submit" className="btn btn-primary me-8 text-white" disabled={isSubmitting}>
                                                    {isSubmitting ? "Signing in..." : "Sign In"}
                                                </button>
                                            </div>
                                        </form>
                                        <p className="mt-3 mb-0 undefined">Don&apos;t have an account?<Link className="text-primary" href="/signup"> Sign up</Link></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
