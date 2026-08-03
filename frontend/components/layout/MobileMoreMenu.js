'use client'
import Link from "next/link"
import { useEffect, useRef } from "react"
import { useAuth } from "@/hooks/useAuth"

const MORE_ITEMS = [
    { href: "/goals", label: "Savings Goals", icon: "fi fi-sr-bullseye-arrow" },
    { href: "/recurring-bills", label: "Recurring Bills", icon: "fi fi-rr-calendar-clock" },
    { href: "/cashback", label: "Cashback", icon: "fi fi-rr-badge-percent" },
    { href: "/wallets", label: "Payment Methods", icon: "fi fi-rr-wallet" },
    { href: "/settings-exports", label: "Exports", icon: "fi fi-rr-download" },
    { href: "/profile", label: "Profile", icon: "fi fi-rr-user" },
]

// Household is inserted before Exports/Profile so it reads as an
// account-level item grouped near Profile, matching where the desktop
// Sidebar places it relative to its other links.
const HOUSEHOLD_INSERT_INDEX = 4

export default function MobileMoreMenu({ isOpen, onClose, triggerRef }) {
    const { user } = useAuth()
    const closeButtonRef = useRef(null)

    const items = user?.role === "owner"
        ? [
            ...MORE_ITEMS.slice(0, HOUSEHOLD_INSERT_INDEX),
            { href: "/household", label: "Household", icon: "fi fi-rr-users" },
            ...MORE_ITEMS.slice(HOUSEHOLD_INSERT_INDEX),
        ]
        : MORE_ITEMS

    useEffect(() => {
        if (!isOpen) return
        closeButtonRef.current?.focus()
        const trigger = triggerRef?.current

        function handleKeyDown(event) {
            if (event.key === "Escape") onClose()
        }
        document.addEventListener("keydown", handleKeyDown)
        return () => {
            document.removeEventListener("keydown", handleKeyDown)
            trigger?.focus()
        }
    }, [isOpen, onClose, triggerRef])

    return (
        <div className={`mobile-more-menu${isOpen ? " open" : ""}`} aria-hidden={!isOpen}>
            <button
                type="button"
                className="mobile-more-backdrop"
                aria-label="Close menu"
                onClick={onClose}
                tabIndex={isOpen ? 0 : -1}
            />
            <div
                id="mobile-more-menu"
                className="mobile-more-sheet"
                role="dialog"
                aria-modal="true"
                aria-labelledby="mobile-more-menu-title"
            >
                <div className="d-flex justify-content-between align-items-center">
                    <h5 id="mobile-more-menu-title">More</h5>
                    <button
                        ref={closeButtonRef}
                        type="button"
                        className="btn btn-sm btn-link text-dark"
                        aria-label="Close"
                        onClick={onClose}
                        tabIndex={isOpen ? 0 : -1}
                    >
                        <i className="fi fi-rr-cross-small" />
                    </button>
                </div>
                <ul>
                    {items.map((item) => (
                        <li key={item.href}>
                            <Link href={item.href} onClick={onClose} tabIndex={isOpen ? 0 : -1}>
                                <i className={item.icon} />
                                <span>{item.label}</span>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
}
