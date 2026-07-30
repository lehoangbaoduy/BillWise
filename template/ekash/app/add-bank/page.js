
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function AddBank() {

    return (
        <>
            <Layout breadcrumbTitle="Add Bank">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Link a bank account</h4>
                                    </div>
                                    <div className="card-body">
                                        <form action="bank-add-successful">
                                            <div className="form-row">
                                                <div className="mb-3 col-xl-12">
                                                    <label className="mr-sm-2">Routing number </label>
                                                    <input type="text" className="form-control" placeholder={25487} />
                                                </div>
                                                <div className="mb-3 col-xl-12">
                                                    <label className="mr-sm-2">Account number </label>
                                                    <input type="text" className="form-control" placeholder={36475} />
                                                </div>
                                                <div className="mb-3 col-xl-12">
                                                    <label className="mr-sm-2">Fulll name </label>
                                                    <input type="text" className="form-control" placeholder="Carla Pascle" />
                                                </div>
                                                <div className="mb-3 col-xl-12">
                                                    <img src="./images/routing.png" alt="" className="img-fluid" />
                                                </div>
                                                <div className="col-12 mt-5">
                                                    <div className="row">
                                                        <div className="col-6">
                                                            <Link href="/add-new-account" className="btn btn-primary w-100">Back</Link>
                                                        </div>
                                                        <div className="col-6">
                                                            <Link href="/settings-bank" className="btn btn-success  w-100">Save</Link>
                                                        </div>
                                                    </div>
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