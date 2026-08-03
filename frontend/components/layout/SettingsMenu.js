'use client'
import Link from "next/link"
import { usePathname } from 'next/navigation'

export default function SettingsMenu() {
    const pathname = usePathname()
    return (
        <div className="settings-menu">
            <Link className={pathname == "/profile" ? "active" : ""} href="/profile">Profile</Link>
            <Link className={pathname == "/settings-exports" ? "active" : ""} href="/settings-exports">Exports</Link>
        </div>
    )
}
