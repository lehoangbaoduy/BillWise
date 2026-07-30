
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Affiliates() {

    return (
        <>
            <Layout breadcrumbTitle="Affiliates">
                <div className="row">
                    <div className="col-xl-3 col-lg-3">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Your Credit</h4>
                            </div>
                            <div className="card-body">
                                <div className="credit-content">
                                    <div className="invited d-flex justify-content-between">
                                        <h6>Invited</h6>
                                        <h6 className="text-primary">12</h6>
                                    </div>
                                    <div className="earnings d-flex justify-content-between">
                                        <h6>Earnings</h6>
                                        <h6 className="text-primary">$ 111</h6>
                                    </div>
                                    <button className="btn btn-primary">CLAIM REWARDS</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-9 col-lg-9">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Referral link</h4>
                            </div>
                            <div className="card-body">
                                <p>Your earn 5% of the Coins your referrals earn through an offer ! Give them this
                                    link
                                    to sign up and you’re good to go</p>
                                <div className="referral-form">
                                    <form action="#">
                                        <div className="form-row align-items-center">
                                            <div className="mb-3 col-xl-8">
                                                <label htmlFor>Your Referral Link</label>
                                                <input type="text" className="form-control" placeholder="Your Referral link" />
                                                <div className="edit-copy">
                                                    <span><i className="fi fi-rr-copy-alt" /></span>
                                                </div>
                                            </div>
                                            <div className="form-social col-xl-4">
                                                <Link href="#">
                                                    <span><i className="fi fi-brands-facebook" /></span>
                                                </Link>
                                                <Link href="#">
                                                    <span><i className="fi fi-brands-twitter" /></span>
                                                </Link>
                                                <Link href="#">
                                                    <span><i className="fi fi-brands-instagram" /></span>
                                                </Link>
                                                <Link href="#">
                                                    <span><i className="fi fi-brands-whatsapp" /></span>
                                                </Link>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        <div className="refferal-level">
                            <div className="card">
                                <div className="card-header">
                                    <h4 className="card-title">Referral level</h4>
                                    <span className="current-bonus">Current Bonus : 5%</span>
                                </div>
                                <div className="card-body">
                                    <div className="referral-progress-content">
                                        <div className="progress-popup first">
                                            <h5>Bronze <span className="divider">|</span><span>5%</span></h5>
                                            <p>Referral : 0</p>
                                        </div>
                                        <div className="progress-popup middle">
                                            <h5>Bronze <span className="divider">|</span><span>5%</span></h5>
                                            <p>Referral : 0</p>
                                        </div>
                                        <div className="progress-popup last">
                                            <h5>Bronze <span className="divider">|</span><span>5%</span></h5>
                                            <p>Referral : 0</p>
                                        </div>
                                        <div className="progress">
                                            <div className="progress-bar w-50" role="progressbar" aria-valuenow={75} aria-valuemin={0} aria-valuemax={100} />
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