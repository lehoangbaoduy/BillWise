"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { ApiError, authApi } from "@/lib/api"

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
                                        <h4>Sign Up</h4>
                                        {error && <div className="alert alert-danger">{error}</div>}
                                        <form onSubmit={handleSubmit}>
                                            <div className="row">
                                                <div className="col-12 mb-3">
                                                    <label className="form-label">Full Name</label>
                                                    <input
                                                        name="fullName"
                                                        type="text"
                                                        className="form-control"
                                                        value={fullName}
                                                        onChange={(e) => setFullName(e.target.value)}
                                                        required
                                                    />
                                                </div>
                                                <div className="col-12 mb-3"><label className="form-label">Email</label>
                                                    <input
                                                        name="email"
                                                        type="email"
                                                        className="form-control"
                                                        value={email}
                                                        onChange={(e) => setEmail(e.target.value)}
                                                        required
                                                    />
                                                </div>
                                                <div className="col-12 mb-3"><label className="form-label">Password</label>
                                                    <input
                                                        name="password"
                                                        type="password"
                                                        className="form-control"
                                                        value={password}
                                                        onChange={(e) => setPassword(e.target.value)}
                                                        minLength={8}
                                                        required
                                                    />
                                                </div>
                                                <div className="col-12">
                                                    <div className="form-check">
                                                        <input
                                                            name="acceptTerms"
                                                            type="checkbox"
                                                            className="form-check-input"
                                                            id="acceptTerms"
                                                            checked={acceptTerms}
                                                            onChange={(e) => setAcceptTerms(e.target.checked)}
                                                        />
                                                        <label className="form-check-label" htmlFor="acceptTerms">I
                                                            certify that I
                                                            am 18 years of age or
                                                            older, and agree to the <Link href="#" className="text-primary">User
                                                                Agreement</Link> and <Link href="#" className="text-primary">Privacy
                                                                    Policy</Link>.</label>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="mt-3 d-grid gap-2">
                                                <button type="submit" className="btn btn-primary me-8 text-white" disabled={isSubmitting}>
                                                    {isSubmitting ? "Creating account..." : "Sign Up"}
                                                </button>
                                            </div>
                                        </form>
                                        <p className="mt-3 mb-0 undefined">Already have an account?<Link className="text-primary" href="/signin"> Sign In</Link></p>
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
