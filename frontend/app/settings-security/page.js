'use client'
import Link from "next/link"
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import { useAuth } from "@/hooks/useAuth"

export default function SettingsSecurity() {
    const { user } = useAuth()

    return (
        <Layout breadcrumbTitle="Security">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    <div className="row">
                        <div className="col-xl-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Email Verification</h4>
                                </div>
                                <div className="card-body">
                                    <div className="email-verification">
                                        <ul>
                                            <li className={user?.email_verified ? "verified" : "pending"}>
                                                <div className="d-flex">
                                                    <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                                    <div>
                                                        <h5>{user?.email || " "}</h5>
                                                        {user?.email_verified ? (
                                                            <p><span><i className="fi fi-sr-badge-check" /></span>Verified</p>
                                                        ) : (
                                                            <p className="text-danger">
                                                                <span className="text-danger"><i className="fi fi-rs-circle-xmark" /></span>
                                                                Verification pending
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-xl-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Password</h4>
                                </div>
                                <div className="card-body">
                                    <p className="text-muted">Reset your password by email.</p>
                                    <Link href="/reset" className="btn btn-primary">Change password</Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
