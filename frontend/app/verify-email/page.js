"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useEffect, useRef, useState } from "react"
import { authApi } from "@/lib/api"

function VerifyEmailContent() {
    const searchParams = useSearchParams()
    const token = searchParams.get("token")
    const email = searchParams.get("email")
    const [status, setStatus] = useState(token ? "verifying" : "pending")
    // The verification token is single-use server-side, so a duplicate call (e.g.
    // React StrictMode's dev-mode double-invoke of effects) would otherwise race
    // the real success response with a spurious "already used" failure. Guard so
    // only the first call for a given token is ever sent.
    const verifiedTokenRef = useRef(null)

    useEffect(() => {
        if (!token || verifiedTokenRef.current === token) return
        verifiedTokenRef.current = token
        authApi
            .verifyEmail(token)
            .then(() => setStatus("verified"))
            .catch(() => setStatus("failed"))
    }, [token])

    return (
        <div className="authincation">
            <div className="container h-100">
                <div className="row justify-content-center h-100 align-items-center">
                    <div className="col-xl-5 col-md-6">
                        <div className="card">
                            <div className="card-body identity-content text-center p-5">
                                <span className="icon"><i className="fi fi-rr-envelope" /></span>
                                {status === "pending" && (
                                    <p>
                                        We sent a verification email to&nbsp;
                                        <strong className="text-dark">{email || "your inbox"}</strong>. Click the
                                        link inside to get started!
                                    </p>
                                )}
                                {status === "verifying" && <p>Verifying your email…</p>}
                                {status === "verified" && (
                                    <>
                                        <p>Your email is verified.</p>
                                        <Link className="btn btn-primary text-white" href="/signin">Sign In</Link>
                                    </>
                                )}
                                {status === "failed" && (
                                    <p>That verification link is invalid or has expired. <Link href="/signup">Sign up again?</Link></p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default function VerifyEmail() {
    return (
        <Suspense>
            <VerifyEmailContent />
        </Suspense>
    )
}
