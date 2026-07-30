'use client'
import { usePathname } from 'next/navigation'
import Link from "next/link"

export default function Sidebar() {
    const pathname = usePathname()
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
                        <li className={pathname == "/support" ? "active" : ""}>
                            <Link href="/support">
                                <span>
                                    <i className="fi fi-rr-user-headset" />
                                </span>
                                <span className="nav-text">Support</span>
                            </Link>
                        </li>
                        <li className={pathname == "/affiliates" ? "active" : ""}>
                            <Link href="/affiliates">
                                <span>
                                    <i className="fi fi-rs-link-alt" />
                                </span>
                                <span className="nav-text">Affiliates</span>
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
