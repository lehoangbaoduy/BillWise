
import Link from "next/link"
export default function Locked() {

    return (
        <>
            <div className="authincation">
                <div className="container">
                    <div className="row justify-content-center align-items-center g-0">
                        <div className="col-xl-8">
                            <div className="row g-0">
                                <div className="col-lg-6">
                                    <div className="welcome-content">
                                        <div className="welcome-title">
                                            <div className="mini-logo">
                                                <Link href="/index">
                                                    <img src="/images/logo-white.png" alt="" width={30} /></Link>
                                            </div>
                                            <h3>Welcome to Ekash</h3>
                                        </div>
                                        <div className="privacy-social">
                                            <div className="privacy-link"><Link href="#">Have an issue with 2-factor
                                                authentication?</Link><br /><Link href="#">Privacy Policy</Link></div>
                                            <div className="intro-social">
                                                <ul>
                                                    <li><Link href="#"><i className="fi fi-brands-facebook" /></Link></li>
                                                    <li><Link href="#"><i className="fi fi-brands-twitter-alt" /></Link></li>
                                                    <li><Link href="#"><i className="fi fi-brands-linkedin" /></Link></li>
                                                    <li><Link href="#"><i className="fi fi-brands-pinterest" /></Link></li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-lg-6">
                                    <div className="auth-form">
                                        <h4>Locked</h4>
                                        <form action="#">
                                            <div className="row">
                                                <div className="col-12 mb-3">
                                                    <label className="form-label">Enter Password</label>
                                                    <input name="password" type="text" className="form-control" />
                                                </div>
                                            </div>
                                            <div className="mt-3 d-grid gap-2">
                                                <button type="submit" className="btn btn-primary me-8 text-white">Submit</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </>
    )
}