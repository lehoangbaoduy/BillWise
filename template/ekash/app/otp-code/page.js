
import Link from "next/link"
export default function OtpCode() {

    return (
        <>
            <div className="authincation">
                <div className="container h-100">
                    <div className="row justify-content-center h-100 align-items-center">
                        <div className="col-xl-5 col-md-6">
                            <div className="mini-logo text-center my-5">
                                <Link href="/index"><img src="./images/logo.png" alt="" /></Link>
                            </div>
                            <div className="card">
                                <div className="card-body">
                                    <Link className="page-back text-muted" href="/otp-phone">
                                        <span><i className="fi fi-ss-angle-small-left" /></span> Back</Link>
                                    <h3 className="text-center">OTP Verification</h3>
                                    <p className="text-center mb-5">We will send one time code on ending in +xxx xxxxxxxx60.</p>
                                    <form action="settings-security">
                                        <div className="mb-3  mb-3">
                                            <label className="mb-3">Your OTP Code</label>
                                            <div className="input-group">
                                                <div className="input-group-prepend">
                                                    <span className="input-group-text">
                                                        <i className="fi fi-sr-phone-call" />
                                                    </span>
                                                </div>
                                                <input type="text" className="form-control" defaultValue="11 22 33" />
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <button type="submit" className="btn btn-success w-100">Verify</button>
                                        </div>
                                    </form>
                                    <div className="info mt-3">
                                        <p className="text-muted">You dont recommended to save password to browsers!</p>
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