"use client"

import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Suspense, useEffect, useRef, useState } from "react"
import { authApi } from "@/lib/api"
import AuthCard from "@/components/auth/AuthCard"

const TITLES = {
    pending: "Check your inbox",
    verifying: "Verifying…",
    verified: "Email verified",
    failed: "Link expired",
}

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
        <AuthCard title={TITLES[status]}>
            <div className="auth-card-message">
                <div className="auth-card-message-icon"><i className="fi fi-rr-envelope" /></div>
                {status === "pending" && (
                    <p>
                        We sent a verification email to <strong>{email || "your inbox"}</strong>. Click the link
                        inside to get started!
                    </p>
                )}
                {status === "verifying" && <p>Verifying your email…</p>}
                {status === "verified" && (
                    <>
                        <p>Your email is verified.</p>
                        <Link className="auth-submit" href="/signin">Sign In</Link>
                    </>
                )}
                {status === "failed" && (
                    <p>That verification link is invalid or has expired. <Link href="/signup">Sign up again?</Link></p>
                )}
            </div>
        </AuthCard>
    )
}

export default function VerifyEmail() {
    return (
        <Suspense fallback={null}>
            <VerifyEmailContent />
        </Suspense>
    )
}
