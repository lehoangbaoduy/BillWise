'use client'
import { useCallback, useEffect, useState } from "react"
import { getStoredPlatformView, storePlatformView } from "@/lib/platformView"

// Forces the sidebar<->bottom-nav layout swap regardless of the real browser
// width -- see the .platform-view-mobile / .platform-view-pc overrides in
// style.css, which mirror the app's existing max-width:767px breakpoint but
// gated by this class instead. Reads localStorage on mount (SSR has no
// window), then keeps document.body's class in sync with the chosen mode.
export function usePlatformView() {
    const [platformView, setPlatformViewState] = useState(null)

    useEffect(() => {
        setPlatformViewState(getStoredPlatformView())
    }, [])

    useEffect(() => {
        document.body.classList.remove("platform-view-mobile", "platform-view-pc")
        if (platformView) document.body.classList.add(`platform-view-${platformView}`)
    }, [platformView])

    const setPlatformView = useCallback((mode) => {
        storePlatformView(mode)
        setPlatformViewState(mode)
    }, [])

    return { platformView, setPlatformView }
}
