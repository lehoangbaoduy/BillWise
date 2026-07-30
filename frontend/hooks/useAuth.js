import useSWR from "swr"
import { authApi } from "@/lib/api"

/**
 * Wraps GET /auth/me. `error` carries the ApiError (401 when there's no valid
 * session) so callers can distinguish "still checking" from "checked, not
 * logged in" — both look like `user === undefined` otherwise.
 */
export function useAuth() {
    const { data: user, error, isLoading, mutate } = useSWR("/auth/me", () => authApi.me(), {
        shouldRetryOnError: false,
        revalidateOnFocus: false,
    })

    return {
        user,
        isLoading,
        isAuthenticated: !!user,
        error,
        refresh: mutate,
    }
}
