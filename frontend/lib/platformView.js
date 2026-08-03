export const PLATFORM_VIEW_STORAGE_KEY = "billwise-platform-view"

// "mobile" | "pc" | null ("Auto" -- leave the existing width-based @media
// behavior untouched). Local-only by design, so the preference doesn't sync
// across devices; it just remembers this browser's choice.
export function getStoredPlatformView() {
    if (typeof window === "undefined") return null
    const stored = window.localStorage.getItem(PLATFORM_VIEW_STORAGE_KEY)
    return stored === "mobile" || stored === "pc" ? stored : null
}

export function storePlatformView(mode) {
    if (mode === null) {
        window.localStorage.removeItem(PLATFORM_VIEW_STORAGE_KEY)
    } else {
        window.localStorage.setItem(PLATFORM_VIEW_STORAGE_KEY, mode)
    }
}
