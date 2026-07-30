
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function SettingsBank() {

    return (
        <>
            <Layout breadcrumbTitle="Bank">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu/>
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Add Bank Account or Card</h4>
                            </div>
                            <div className="card-body">
                                <div className="verify-content">
                                    <div className="d-flex align-items-center">
                                        <span className="me-3 icon-circle bg-primary text-white">
                                            <i className="fi fi-rs-bank" /></span>
                                        <div className="primary-number">
                                            <h5 className="mb-0">Bank of America</h5>
                                            <small>Bank **************5421</small>
                                            <br />
                                            <span className="text-success">Verified</span>
                                        </div>
                                    </div>
                                    <button className=" btn btn-outline-primary">Manage</button>
                                </div>
                                <hr className="border opacity-1" />
                                <div className="verify-content">
                                    <div className="d-flex align-items-center">
                                        <span className="me-3 icon-circle bg-primary text-white"><i className="fi fi-rr-credit-card" /></span>
                                        <div className="primary-number">
                                            <h5 className="mb-0">Master Card</h5>
                                            <small>Credit Card *********5478</small>
                                            <br />
                                            <span className="text-success">Verified</span>
                                        </div>
                                    </div>
                                    <button className=" btn btn-outline-primary">Manage</button>
                                </div>
                                <div className="mt-5">
                                    <Link href="/add-bank" className="btn btn-primary m-2">Add New Bank</Link>
                                    <Link href="/add-card" className="btn btn-primary m-2">Add New Card</Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}