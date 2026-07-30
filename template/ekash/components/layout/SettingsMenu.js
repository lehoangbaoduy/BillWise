'use client'
import Link from "next/link"
import { usePathname } from 'next/navigation'

export default function SettingsMenu() {
    const pathname = usePathname()
    return (
        <>
            <div className="settings-menu">
                <Link className={pathname == "/settings" ? "active" : ""} href="/settings">Account</Link>
                <Link className={pathname == "/settings-general" ? "active" : ""} href="/settings-general">General</Link>
                <Link className={pathname == "/settings-profile" ? "active" : ""} href="/settings-profile">Profile</Link>
                <Link className={pathname == "/settings-bank" ? "active" : ""} href="/settings-bank">Add Bank</Link>
                <Link className={pathname == "/settings-security" ? "active" : ""} href="/settings-security">Security</Link>
                <Link className={pathname == "/settings-session" ? "active" : ""} href="/settings-session">Session</Link>
                <Link className={pathname == "/settings-categories" ? "active" : ""} href="/settings-categories">Categories</Link>
                <Link className={pathname == "/settings-currencies" ? "active" : ""} href="/settings-currencies">Currencies</Link>
                <Link className={pathname == "/settings-api" ? "active" : ""} href="/settings-api">Api</Link>
                <Link className={pathname == "/support" ? "active" : ""} href="/support">Support</Link>
            </div>

        </>
    )
}
