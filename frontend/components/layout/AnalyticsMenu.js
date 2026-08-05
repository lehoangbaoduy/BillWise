'use client'
import Link from "next/link"
import { usePathname } from 'next/navigation'

export default function AnalyticsMenu() {
    const pathname = usePathname()
    return (
        <>
            <div className="settings-menu">
                <Link className={pathname == "/analytics" ? "active" : ""} href="/analytics">Analytics</Link>
                <Link className={pathname == "/analytics-income-vs-expenses" ? "active" : ""} href="/analytics-income-vs-expenses">Expenses &amp; Income</Link>
                <Link className={pathname == "/analytics-transaction-history" ? "active" : ""} href="/analytics-transaction-history">Transaction History</Link>
                <Link className={pathname == "/settings-categories" ? "active" : ""} href="/settings-categories">Categories</Link>
                <Link className={pathname == "/merchants" ? "active" : ""} href="/merchants">Merchants</Link>
            </div>

        </>
    )
}
