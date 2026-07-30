'use client'
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import { useAuth } from "@/hooks/useAuth"

export default function Settings() {
    const { user } = useAuth()

    return (
        <Layout breadcrumbTitle="Settings">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    <div className="row">
                        <div className="col-xxl-12">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Account</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                            <div className="user-info">
                                                <span>NAME</span>
                                                <h4>{user?.display_name || " "}</h4>
                                            </div>
                                        </div>
                                        <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                            <div className="user-info">
                                                <span>EMAIL ADDRESS</span>
                                                <h4>{user?.email || " "}</h4>
                                            </div>
                                        </div>
                                        <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                            <div className="user-info">
                                                <span>ROLE</span>
                                                <h4>{user?.role === "owner" ? "Owner" : "Partner"}</h4>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
