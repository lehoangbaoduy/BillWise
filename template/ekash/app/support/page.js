
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Support() {

    return (
        <>
            <Layout breadcrumbTitle="Support">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Your Ticket</h4>
                                <Link href="/support-create-ticket" className="btn btn-primary">Create Ticket</Link>
                            </div>
                            <div className="card-body height-200 d-flex align-items-center justify-content-center">
                                <p className="mt-5">You have no ticket yet! Create one by hitting the <Link href="/support-create-ticket" className="text-primary">Create
                                    Button</Link> </p>
                            </div>
                        </div>
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Your Ticket Notification</h4>
                                <Link href="#" className="text-warning">Clear All Notification</Link>
                            </div>
                            <div className="card-body">
                                <p>Opps sorry, There are no notification to show </p>
                            </div>
                        </div>
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Recent Tickets</h4>
                            </div>
                            <div className="card-body">
                                <div className="ticket-list">
                                    <Link href="/support-ticket-details">
                                        <div>
                                            <h5>I’m having issues claming with my daily hours <span className="badge badge-success">OPEN</span></h5>
                                            <p>Posted on 24 June 2024</p>
                                        </div>
                                        <span><i className="fi fi-ss-angle-right" /></span>
                                    </Link>
                                    <Link href="/support-ticket-details">
                                        <div>
                                            <h5>I’m having issues claming with my daily hours <span className="badge badge-success">OPEN</span></h5>
                                            <p>Posted on 24 June 2024</p>
                                        </div>
                                        <span><i className="fi fi-ss-angle-right" /></span>
                                    </Link>
                                    <Link href="/support-ticket-details">
                                        <div>
                                            <h5>I’m having issues claming with my daily hours <span className="badge badge-success">OPEN</span></h5>
                                            <p>Posted on 24 June 2024</p>
                                        </div>
                                        <span><i className="fi fi-ss-angle-right" /></span>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}