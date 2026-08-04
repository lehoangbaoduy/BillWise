import { mutate } from "swr"

// Dashboard widgets (Monthly Expenses Breakdown, Total Period Expenses/Income,
// etc.) key their SWR cache as ["/dashboard/...", periodKey] and only
// revalidate on their own triggers (mount, focus, interval) -- a mutation made
// elsewhere (e.g. deleting a transaction on the Transaction History page)
// never touches that cache, so navigating back to the dashboard within the
// same client-side session shows stale totals until some other revalidation
// happens to fire. Call this after any transaction/budget/goal/bill mutation
// that could change dashboard totals, so the cache is invalidated regardless
// of which page's SWR hook currently holds it.
export function revalidateDashboard() {
    mutate((key) => Array.isArray(key) && typeof key[0] === "string" && key[0].startsWith("/dashboard"))
}
