
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Error() {

    return (
        <Layout breadcrumbTitle="Error">
                <div className="row justify-content-center align-items-center g-0">
                    <div className="col-xl-4">
                        <div className="card">
                            <div className="card-body text-center">
                                <div className="py-5">
                                    <h1>404</h1>
                                    <p>Page not found</p>
                                    <Link href="/" className="btn btn-primary mt-3">Home</Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

        </Layout>
    )
}