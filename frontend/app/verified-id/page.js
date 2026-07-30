
import Layout from "@/components/layout/Layout"
export default function VerifiedId() {

    return (
        <>
            <Layout breadcrumbTitle="Verified Id">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body identity-content">
                                        <form action="settings-security">
                                            <span className="icon"><i className="fi fi-bs-check" /></span>
                                            <h4>Identity Verified</h4>
                                            <p>Congrats! your identity has been successfully verified and your
                                                investment
                                                limit has been increased.</p>
                                            <div className="text-center">
                                                <button type="submit" className="btn btn-success pl-5 pr-5">Continue</button>
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