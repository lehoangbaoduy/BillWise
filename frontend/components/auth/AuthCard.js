"use client"

import Link from "next/link"

export default function AuthCard({ title, subtitle, children }) {
    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-card-brand">
                    <Link href="/" className="auth-card-brand-link">
                        <img src="/images/logoi.png" alt="" width={28} height={28} />
                        <span>BillWise</span>
                    </Link>
                </div>
                {title && <h1 className="auth-card-title">{title}</h1>}
                {subtitle && <p className="auth-card-subtitle">{subtitle}</p>}
                {children}
            </div>
        </div>
    )
}
