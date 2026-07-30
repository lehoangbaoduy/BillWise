
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function SettingsSecurity() {

    return (
        <>
            <Layout breadcrumbTitle="Security">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu/>
                        <div className="row">
                            <div className="col-xl-4">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Social Security Card</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="id-card-img">
                                            <img src="./images/id.png" alt="" className="img-fluid" />
                                        </div>
                                        <div className="id-info mt-3">
                                            <h4>Carla Pascle </h4>
                                            <ul>
                                                <li className="verified mb-0">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-br-id-badge" /></span>
                                                        <div>
                                                            <h5>
                                                                0024 5687 2254 3698</h5>
                                                            <p>
                                                                <span><i className="fi fi-sr-badge-check" /></span>
                                                                Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                            </ul>
                                            <Link href="/id-front-and-back-upload" className="btn btn-primary mt-3">
                                                Add New ID
                                            </Link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Email Verification</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="email-verification">
                                            <ul>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                                        <div>
                                                            <h5> hello@example.com</h5>
                                                            <p> <span><i className="fi fi-sr-badge-check" /></span>Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                                        <div>
                                                            <h5> hello@example.com</h5>
                                                            <p> <span><i className="fi fi-sr-badge-check" /></span>Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                                        <div>
                                                            <h5> hello@example.com</h5>
                                                            <p> <span><i className="fi fi-sr-badge-check" /></span>Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="pending">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-envelope" /></span>
                                                        <div>
                                                            <h5> hello@example.com</h5>
                                                            <p className="text-danger">
                                                                <span className="text-danger"><i className="fi fi-rs-circle-xmark" /></span>Verification
                                                                pending
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                        <form action="verify-email">
                                            <input type="text" className="form-control" placeholder="hello@example.com " />
                                            <button className="btn btn-primary mt-3">Add New Email</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Phone Verification</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="phone-verification">
                                            <ul>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-phone-call" /></span>
                                                        <div>
                                                            <h5> +1 135 468 45 </h5>
                                                            <p>
                                                                <span><i className="fi fi-sr-badge-check" /></span>
                                                                Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-phone-call" /></span>
                                                        <div>
                                                            <h5> +1 135 468 45 </h5>
                                                            <p>
                                                                <span><i className="fi fi-sr-badge-check" /></span>
                                                                Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="verified">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-phone-call" /></span>
                                                        <div>
                                                            <h5> +1 135 468 45 </h5>
                                                            <p>
                                                                <span><i className="fi fi-sr-badge-check" /></span>
                                                                Verified
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                                <li className="pending">
                                                    <div className="d-flex">
                                                        <span className="round-icon"><i className="fi fi-rr-phone-call" /></span>
                                                        <div>
                                                            <h5> +1 135 468 45</h5>
                                                            <p className="text-danger">
                                                                <span className="text-danger"><i className="fi fi-rs-circle-xmark" /></span>
                                                                Verification pending
                                                            </p>
                                                        </div>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                        <form action="otp-code">
                                            <input type="text" className="form-control" placeholder="+1 135 468 45 " />
                                            <button className="btn btn-primary mt-3">Add New Phone</button>
                                        </form>
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