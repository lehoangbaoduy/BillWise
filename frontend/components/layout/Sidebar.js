'use client'
import { usePathname } from 'next/navigation'
import Link from "next/link"
import { useAuth } from "@/hooks/useAuth"

export default function Sidebar() {
    const pathname = usePathname()
    const { user } = useAuth()
    return (
        <>
            <div className="sidebar">
                <div className="brand-logo"><Link className="full-logo" href="/"><img src="./images/logoi.png" alt="" width={30} /></Link></div>
                <div className="menu">
                    <ul>
                        <li className={pathname == "/" ? "active" : ""}>
                            <Link href="/">
                                <span>
                                    <i className="fi fi-rr-dashboard" />
                                </span>
                                <span className="nav-text">Dashboard</span>
                            </Link>
                        </li>
                        <li className={pathname == "/analytics-transaction-history" || pathname == "/add-transaction" ? "active" : ""}>
                            <Link href="/analytics-transaction-history">
                                <span>
                                    <i className="fi fi-rr-receipt" />
                                </span>
                                <span className="nav-text">Transactions</span>
                            </Link>
                        </li>
                        <li className={pathname == "/wallets" ? "active" : ""}>
                            <Link href="/wallets">
                                <span>
                                    <i className="fi fi-rr-wallet" />
                                </span>
                                <span className="nav-text">Wallets</span>
                            </Link>
                        </li>
                        <li className={pathname == "/budgets" ? "active" : ""}>
                            <Link href="/budgets">
                                <span>
                                    <i className="fi fi-rr-donate" />
                                </span>
                                <span className="nav-text">Budgets</span>
                            </Link>
                        </li>
                        <li className={pathname == "/goals" ? "active" : ""}>
                            <Link href="/goals">
                                <span>
                                    <i className="fi fi-sr-bullseye-arrow" />
                                </span>
                                <span className="nav-text">Goals</span>
                            </Link>
                        </li>
                        <li className={pathname == "/recurring-bills" ? "active" : ""}>
                            <Link href="/recurring-bills">
                                <span>
                                    <i className="fi fi-rr-calendar-clock" />
                                </span>
                                <span className="nav-text">Recurring Bills</span>
                            </Link>
                        </li>
                        <li className={pathname == "/cashback" ? "active" : ""}>
                            <Link href="/cashback">
                                <span>
                                    <i className="fi fi-rr-badge-percent" />
                                </span>
                                <span className="nav-text">Cashback</span>
                            </Link>
                        </li>
                        <li className={pathname == "/net-worth" ? "active" : ""}>
                            <Link href="/net-worth">
                                <span>
                                    <i className="fi fi-rr-stats" />
                                </span>
                                <span className="nav-text">Net Worth</span>
                            </Link>
                        </li>
                        {user?.role === "owner" && (
                            <li className={pathname == "/household" ? "active" : ""}>
                                <Link href="/household">
                                    <span>
                                        <i className="fi fi-rr-users" />
                                    </span>
                                    <span className="nav-text">Household</span>
                                </Link>
                            </li>
                        )}
                        <li className={pathname == "/profile" ? "active" : ""}>
                            <Link href="/profile">
                                <span>
                                    <i className="fi fi-rr-user" />
                                </span>
                                <span className="nav-text">Profile</span>
                            </Link>
                        </li>
                        <li className={pathname == "/analytics" ? "active" : ""}>
                            <Link href="/analytics">
                                <span>
                                    <i className="fi fi-rr-chart-histogram" />
                                </span>
                                <span className="nav-text">Analytics</span>
                            </Link>
                        </li>
                        <li className={pathname == "/settings" ? "active" : ""}>
                            <Link href="/settings">
                                <span>
                                    <i className="fi fi-rs-settings" />
                                </span>
                                <span className="nav-text">Settings</span>
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>

        </>
    )
}
