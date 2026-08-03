const HIDDEN_MERCHANTS_STORAGE_KEY = "billwise-hidden-merchants"

// Local-only per-browser denylist for the merchant suggestion dropdown --
// there's no standalone Merchant table (merchant names are just distinct
// values pulled from saved transactions, see /transactions/merchants), so
// "deleting" a merchant here only hides it from future suggestions; it never
// touches existing transactions or cashback rules that already reference it.
export function getHiddenMerchants() {
    if (typeof window === "undefined") return []
    try {
        const raw = window.localStorage.getItem(HIDDEN_MERCHANTS_STORAGE_KEY)
        return raw ? JSON.parse(raw) : []
    } catch {
        return []
    }
}

export function hideMerchant(name) {
    const normalized = name.trim().toLowerCase()
    const hidden = getHiddenMerchants()
    if (hidden.includes(normalized)) return
    window.localStorage.setItem(HIDDEN_MERCHANTS_STORAGE_KEY, JSON.stringify([...hidden, normalized]))
}
