
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function VerifyEmail() {

    return (
        <>
            <Layout breadcrumbTitle="Verify Email">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body identity-content">
                                        <span className="icon"><i className="fi fi-rr-envelope" /></span>
                                        <p>We sent verification email to &nbsp;<strong className="text-dark">example@email.com</strong>. Click the link
                                            inside to get
                                            started!</p><Link href="/signup">Email didn't arrive?</Link>
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