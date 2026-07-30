
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function Settings() {

    return (
        <>
            <Layout breadcrumbTitle="Settings">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <SettingsMenu/>
                        <div className="row">
                            <div className="col-xxl-6 col-xl-6 col-lg-6">
                                <div className="card ">
                                    <div className="card-body">
                                        <div className="welcome-profile">
                                            <div className="d-flex align-items-center">
                                                <img src="./images/avatar/3.jpg" alt="" />
                                                <div className="ms-3">
                                                    <h4>Welcome, Hafsa Humaira!</h4>
                                                    <p>Looks like you are not verified yet. Verify yourself to use the full
                                                        potential of
                                                        Ekash.</p>
                                                </div>
                                            </div>
                                            <ul>
                                                <li><Link href="#"><span className="verified"><i className="fi fi-bs-check" /></span>Verify
                                                    account</Link></li>
                                                <li><Link href="#"><span className="not-verified"><i className="fi fi-rs-shield-check" /></span>Two-factor
                                                    authentication
                                                    (2FA)</Link></li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xxl-6 col-xl-6 col-lg-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Download App</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="app-link">
                                            <h5>Get Verified On Our Mobile App</h5>
                                            <p>Verifying your identity on our mobile app more secure, faster, and reliable.
                                            </p>
                                            <Link href="#" className="btn btn-primary"><img src="./images/android.svg" alt="" /></Link><br />
                                            <div className="mt-3" />
                                            <Link href="#" className="btn btn-primary"><img src="./images/apple.svg" alt="" /></Link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xxl-8 col-xl-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">VERIFY &amp; UPGRADE </h4>
                                    </div>
                                    <div className="card-body">
                                        <h5>Account Status :
                                            <span className="text-warning"> Pending</span>
                                        </h5>
                                        <p>Your account is unverified. Get verified to enable funding, trading, and
                                            withdrawal.</p>
                                        <Link href="#" className="btn btn-primary">Get Verified</Link>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xxl-4 col-xl-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Earn 30% Commission </h4>
                                    </div>
                                    <div className="card-body">
                                        <p>Refer your friends and earn 30% of <br /> their trading fees.</p>
                                        <Link href="/affiliates" className="btn btn-primary">Referral Program</Link>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xxl-12">
                                <div className="card">
                                    <div className="card-header flex-row">
                                        <h4 className="card-title">Information </h4>
                                        <Link className="btn btn-primary" href="/settings-profile">Edit</Link>
                                    </div>
                                    <div className="card-body">
                                        <form className="row">
                                            <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                                <div className="user-info">
                                                    <span>USER ID</span>
                                                    <h4>818778</h4>
                                                </div>
                                            </div>
                                            <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                                <div className="user-info">
                                                    <span>EMAIL ADDRESS</span>
                                                    <h4>email@example.com</h4>
                                                </div>
                                            </div>
                                            <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                                <div className="user-info">
                                                    <span>COUNTRY OF RESIDENCE</span>
                                                    <h4>Bangladesh</h4>
                                                </div>
                                            </div>
                                            <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                                <div className="user-info">
                                                    <span>JOINED SINCE</span>
                                                    <h4>20/10/2020</h4>
                                                </div>
                                            </div>
                                            <div className="col-xxl-4 col-xl-4 col-lg-4 col-md-6">
                                                <div className="user-info">
                                                    <span>TYPE</span>
                                                    <h4>Personal</h4>
                                                </div>
                                            </div>
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