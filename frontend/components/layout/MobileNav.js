'use client'
import { usePathname } from 'next/navigation'
import Link from "next/link"
import { useRef, useState } from "react"
import MobileMoreMenu from "./MobileMoreMenu"

const MORE_ROUTES = [
    "/goals", "/recurring-bills", "/cashback", "/wallets",
    "/settings-exports", "/profile", "/household",
]

export default function MobileNav() {
    const pathname = usePathname()
    const [isMoreOpen, setMoreOpen] = useState(false)
    const moreButtonRef = useRef(null)
    const isMoreActive = MORE_ROUTES.some((route) => pathname === route || pathname.startsWith(`${route}-`) || pathname.startsWith(`${route}/`))

    return (
        <>
            <nav className="mobile-nav" aria-label="Mobile navigation">
                <Link href="/" className={`mobile-nav-link${pathname === "/" ? " active" : ""}`}>
                    <i className="fi fi-rr-dashboard" />
                    <span>Dashboard</span>
                </Link>
                <Link
                    href="/analytics-transaction-history"
                    className={`mobile-nav-link${pathname === "/analytics-transaction-history" ? " active" : ""}`}
                >
                    <i className="fi fi-rr-receipt" />
                    <span>Transactions</span>
                </Link>
                <Link href="/add-transaction" className="mobile-nav-add" aria-label="Add transaction">
                    <span className="mobile-nav-add-btn">
                        <i className="fi fi-rr-plus" />
                    </span>
                    <span>Add</span>
                </Link>
                <Link href="/budgets" className={`mobile-nav-link${pathname === "/budgets" ? " active" : ""}`}>
                    <i className="fi fi-rr-donate" />
                    <span>Budgets</span>
                </Link>
                <button
                    ref={moreButtonRef}
                    type="button"
                    className={`mobile-nav-link${isMoreOpen || isMoreActive ? " active" : ""}`}
                    aria-expanded={isMoreOpen}
                    aria-controls="mobile-more-menu"
                    aria-label="More"
                    onClick={() => setMoreOpen(true)}
                >
                    <i className="fi fi-rr-menu-dots" />
                    <span>More</span>
                </button>
            </nav>
            <MobileMoreMenu isOpen={isMoreOpen} onClose={() => setMoreOpen(false)} triggerRef={moreButtonRef} />
        </>
    )
}
