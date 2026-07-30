"use client"

import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { useAuth } from "@/hooks/useAuth"

/**
 * Gates every authenticated screen behind a real session check (GET /auth/me)
 * rather than trusting client-side state alone — the server is still the
 * source of truth on every subsequent API call regardless, but this stops an
 * unauthenticated visitor from seeing an authenticated screen's chrome/shell
 * before being bounced.
 */
export default function AuthGuard({ children }) {
    const router = useRouter()
    const { isAuthenticated, isLoading } = useAuth()

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.replace("/signin")
        }
    }, [isLoading, isAuthenticated, router])

    if (isLoading || !isAuthenticated) {
        return null
    }

    return children
}
