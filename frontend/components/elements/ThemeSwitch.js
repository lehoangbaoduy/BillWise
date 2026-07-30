'use client'
import React, { useEffect, useState } from "react"

export default function ThemeSwitch() {
    // State for theme
    const [toggleTheme, setToggleTheme] = useState(
        () => JSON.parse(localStorage.getItem("toggleTheme")) || "light-theme"
    )

    // Effect to handle theme changes
    useEffect(() => {
        // Update local storage with the current theme
        localStorage.setItem("toggleTheme", JSON.stringify(toggleTheme))

        // Add theme class to the body
        document.body.classList.add(toggleTheme)

        // Remove previous theme class when component unmounts or theme changes
        return () => {
            document.body.classList.remove(toggleTheme)
        }
    }, [toggleTheme])

    // Toggle theme function
    const handleThemeToggle = () => {
        setToggleTheme((prevTheme) =>
            prevTheme === "light-theme" ? "dark-theme" : "light-theme"
        )
    }

    return (
        <>
            {/* Theme toggle button */}
            <div className="dark-light-toggle" onClick={handleThemeToggle}>
                <span className="dark">
                    <i className="fi fi-rr-eclipse-alt" />
                </span>
                <span className="light">
                    <i className="fi fi-rr-eclipse-alt" />
                </span>
            </div>
        </>
    )
}