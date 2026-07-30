'use client'
import Link from "next/link"
import Layout from "@/components/layout/Layout"
import { useAuth } from "@/hooks/useAuth"

export default function Profile() {
    const { user } = useAuth()

    return (
        <Layout breadcrumbTitle="Profile">
            <div className="row">
                <div className="col-xl-6">
                    <div className="card">
                        <div className="card-body">
                            <div className="profile-name">
                                <div className="d-flex align-items-center">
                                    <i className="fi fi-rr-user" style={{ fontSize: "2.5rem" }} />
                                    <div className="flex-grow-1 ms-3">
                                        <h4 className="mb-0">{user?.display_name || " "}</h4>
                                        <p className="mb-0">{user?.email || " "}</p>
                                    </div>
                                </div>
                            </div>
                            <div className="profile-reg mt-3">
                                <div className="registered">
                                    <h5>{user?.role === "owner" ? "Owner" : "Partner"}</h5>
                                    <p className="mb-0">Role</p>
                                </div>
                                <span className="reg_divider" />
                                <div className="rank">
                                    <h5>{user?.email_verified ? "Verified" : "Unverified"}</h5>
                                    <p className="mb-0">Email status</p>
                                </div>
                            </div>
                            <Link href="/wallets" className="btn btn-primary mt-3">View payment methods</Link>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
