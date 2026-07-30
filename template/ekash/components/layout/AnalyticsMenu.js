'use client'
import Link from "next/link"
import { usePathname } from 'next/navigation'

export default function AnalyticsMenu() {
    const pathname = usePathname()
    return (
        <>
            <div className="settings-menu">
                <Link className={pathname == "/analytics" ? "active" : ""} href="/analytics">Analytics</Link>
                <Link className={pathname == "/analytics-expenses" ? "active" : ""} href="/analytics-expenses">Expenses</Link>
                <Link className={pathname == "/analytics-income" ? "active" : ""} href="/analytics-income">Income</Link>
                <Link className={pathname == "/analytics-income-vs-expenses" ? "active" : ""} href="/analytics-income-vs-expenses">Income vs Expenses</Link>
                <Link className={pathname == "/analytics-balance" ? "active" : ""} href="/analytics-balance">Balance</Link>
                <Link className={pathname == "/analytics-transaction-history" ? "active" : ""} href="/analytics-transaction-history">Transaction History</Link>
            </div>

        </>
    )
}
