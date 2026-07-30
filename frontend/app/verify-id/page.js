
import Layout from "@/components/layout/Layout"
export default function VerifyId() {

    return (
        <>
            <Layout breadcrumbTitle="Verify Id">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body identity-content">
                                        <form action="id-front-and-back-upload">
                                            <span className="icon"><i className="fi fi-bs-shield-keyhole" /></span>
                                            <h4>Please verify your identity before adding your card</h4>
                                            <p>Uploading your ID helps as ensure the safety and security of your founds
                                            </p>
                                            <div className="text-center">
                                                <button type="submit" className="btn btn-success pl-5 pr-5">Upload ID</button>
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