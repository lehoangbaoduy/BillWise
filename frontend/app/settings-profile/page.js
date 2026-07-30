'use client'
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import { useAuth } from "@/hooks/useAuth"

export default function SettingsProfile() {
    const { user } = useAuth()

    return (
        <Layout breadcrumbTitle="Profile">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    <div className="row">
                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">User Profile</h4>
                                </div>
                                <div className="card-body">
                                    <div className="d-flex align-items-center mb-3">
                                        <i className="fi fi-rr-user" style={{ fontSize: "2rem" }} />
                                        <div className="ms-3">
                                            <h5 className="mb-0">{user?.display_name || " "}</h5>
                                            <p className="mb-0 text-muted">{user?.email || " "}</p>
                                        </div>
                                    </div>
                                    <p className="text-muted mb-0">Editing your name or email isn&apos;t available yet.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
