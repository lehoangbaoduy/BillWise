
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Tickets() {

    return (
        <>
            <Layout breadcrumbTitle="Tickets">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Your Ticket</h4>
                                <Link href="#" className="btn btn-primary">Create Ticket</Link>
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