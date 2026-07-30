
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function TicketDetails() {

    return (
        <>
            <Layout breadcrumbTitle="Ticket Details">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card create_ticket_details">
                            <div className="card-header">
                                <div>
                                    <h5>I’m having issues claming with my daily hours <span className="badge bg-success">OPEN</span></h5>
                                    <p className="mb-0">Posted on 24 June 2024</p>
                                </div>
                                <button className="btn btn-danger">
                                    <span><i className="la la-close" /></span>Close Ticket
                                </button>
                            </div>
                            <div className="card-body">
                                <div className="ticket_details">
                                    <div className="ticket-desc">
                                        <p>lorem Ipsum is simply dummy text of the printing and typesetting industry.
                                            Lorem
                                            Ipsum has been the industry’s standard dummy text ever since the 1500slorem
                                            Ipsum is simply dummy text of the printing and typesetting industry. Lorem
                                            Ipsum
                                            has been the industry’s standard dummy text ever since the 1500s</p>
                                    </div>
                                    <div className="comment-reply">
                                        <div className="d-flex align-items-start">
                                            <img src="./images/profile/2.png" alt="" className="me-3" />
                                            <div className="flex-grow-1">
                                                <h5>Rick Henary</h5>
                                                <span>Posted on 24 June 2024</span>
                                                <p>lorem Ipsum is simply dummy text of the printing and typesetting
                                                    industry. Lorem Ipsum has been the industry’s standard dummy text
                                                    ever
                                                    since the 1500slorem Ipsum is simply dummy text of the printing and
                                                    typesetting industry. Lorem Ipsum has been the industry’s standard
                                                    dummy
                                                    text ever since the 1500s</p>
                                            </div>
                                            <span>REPORT</span>
                                        </div>
                                        <div className="d-flex align-items-start">
                                            <img src="./images/profile/3.png" alt="" className="me-3" />
                                            <div className="flex-grow-1">
                                                <form action="#">
                                                    <textarea name id rows={5} className="form-control" defaultValue={""} />
                                                    <button className="btn btn-primary">Add Response</button>
                                                </form>
                                            </div>
                                        </div>
                                        <div className="d-flex user_admin  align-items-start">
                                            <img src="./images/profile/4.png" alt="" className="me-3" />
                                            <div className="flex-grow-1 ">
                                                <h5>Admin</h5>
                                                <span>Posted on 24 June 2024</span>
                                                <p>lorem Ipsum is simply dummy text of the printing and typesetting
                                                    industry. Lorem Ipsum has been the industry’s standard dummy text
                                                    ever
                                                    since the 1500slorem Ipsum is simply dummy text of the printing and
                                                    typesetting industry. Lorem Ipsum has been the industry’s standard
                                                    dummy
                                                    text ever since the 1500s</p>
                                                <Link href="#">Add Response</Link>
                                            </div>
                                        </div>
                                        <div className="d-flex align-items-start">
                                            <img src="./images/profile/1.png" alt="" className="me-3" />
                                            <div className="flex-grow-1 ">
                                                <h5>Thomas Halva </h5>
                                                <span>Posted on 24 June 2024</span>
                                                <p>lorem Ipsum is simply dummy text of the printing and typesetting
                                                    industry. Lorem Ipsum has been the industry’s standard dummy text
                                                    ever
                                                    since the 1500slorem Ipsum is simply dummy text of the printing and
                                                    typesetting industry. Lorem Ipsum has been the industry’s standard
                                                    dummy
                                                    text ever since the 1500s</p>
                                                <Link href="#">Add Response</Link>
                                            </div>
                                            <span>REPORT</span>
                                        </div>
                                        <div className="d-flex align-items-start">
                                            <img src="./images/profile/2.png" alt="" className="me-3" />
                                            <div className="flex-grow-1 ">
                                                <h5>Bastian Swest</h5>
                                                <span>Posted on 24 June 2024</span>
                                                <p>lorem Ipsum is simply dummy text of the printing and typesetting
                                                    industry. Lorem Ipsum has been the industry’s standard dummy text
                                                    ever
                                                    since the 1500slorem Ipsum is simply dummy text of the printing and
                                                    typesetting industry. Lorem Ipsum has been the industry’s standard
                                                    dummy
                                                    text ever since the 1500s</p>
                                                <Link href="#">Add Response</Link>
                                            </div>
                                            <span>REPORT</span>
                                        </div>
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