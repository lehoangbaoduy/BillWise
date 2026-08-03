'use client'
import { useEffect, useState } from "react"

// Dark mode here is a plain `.dark-theme` class toggled on <body> by
// ThemeSwitch.js (persisted to localStorage), not React state or context --
// a MutationObserver is the only way for other components to react to it.
export function useIsDarkTheme() {
    const [isDark, setIsDark] = useState(false)

    useEffect(() => {
        const body = document.body
        setIsDark(body.classList.contains("dark-theme"))

        const observer = new MutationObserver(() => {
            setIsDark(body.classList.contains("dark-theme"))
        })
        observer.observe(body, { attributes: true, attributeFilter: ["class"] })
        return () => observer.disconnect()
    }, [])

    return isDark
}
