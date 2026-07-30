
import Layout from "@/components/layout/Layout"
export default function VerifyingId() {

    return (
        <>
            <Layout breadcrumbTitle="Verifying Id">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body identity-content">
                                        <form action="verify-step-4">
                                            <span className="icon"><i className="fi fi-rr-shield-check" /></span>
                                            <h4>We are verifying your ID</h4>
                                            <p>Your identity is being verified. We will email you once your verification
                                                has
                                                completed.
                                            </p>
                                            <div className="upload-loading text-center mb-3">
                                                <i className="fi fi-rs-loading" />
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