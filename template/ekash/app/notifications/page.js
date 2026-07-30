
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Notifications() {

    return (
        <>
            <Layout breadcrumbTitle="Notifications">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Recent Notification </h4>
                            </div>
                            <div className="card-body">
                                <div className="notification">
                                    <div className="lists">
                                        <Link href="#">
                                            <div className="d-flex align-items-center">
                                                <span className="me-3 icon success"><i className="fi fi-bs-check" /></span>
                                                <div>
                                                    <p>Account created successfully</p>
                                                    <span>2024-11-04 12:00:23</span>
                                                </div>
                                            </div>
                                        </Link>
                                        <Link href="#">
                                            <div className="d-flex align-items-center">
                                                <span className="me-3 icon fail"><i className="fi fi-sr-cross-small" /></span>
                                                <div>
                                                    <p>2FA verification failed</p>
                                                    <span>2024-11-04 12:00:23</span>
                                                </div>
                                            </div>
                                        </Link>
                                        <Link href="#">
                                            <div className="d-flex align-items-center">
                                                <span className="me-3 icon success"><i className="fi fi-bs-check" /></span>
                                                <div>
                                                    <p>Device confirmation completed</p>
                                                    <span>2024-11-04 12:00:23</span>
                                                </div>
                                            </div>
                                        </Link>
                                        <Link href="#">
                                            <div className="d-flex align-items-center">
                                                <span className="me-3 icon pending"><i className="fi fi-rr-triangle-warning" /></span>
                                                <div>
                                                    <p>Phone verification pending</p>
                                                    <span>2024-11-04 12:00:23</span>
                                                </div>
                                            </div>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}