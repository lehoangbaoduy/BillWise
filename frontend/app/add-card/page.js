
import Layout from "@/components/layout/Layout"
export default function AddCard() {

    return (
        <>
            <Layout breadcrumbTitle="Add Card">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Link a debit card</h4>
                                    </div>
                                    <div className="card-body">
                                        <form action="bank-add-successful">
                                            <div className="row">
                                                <div className="mb-3 col-xl-12">
                                                    <label className="form-label">Name on card </label>
                                                    <input type="text" className="form-control" placeholder="Carla Pascle" />
                                                </div>
                                                <div className="mb-3 col-xl-12">
                                                    <label className="form-label">Card number </label>
                                                    <input type="text" className="form-control" placeholder="5658 4258 6358 4756" />
                                                </div>
                                                <div className="mb-3 col-xl-4">
                                                    <label className="form-label">Expiration </label>
                                                    <input type="text" className="form-control" placeholder="10/22" />
                                                </div>
                                                <div className="mb-3 col-xl-4">
                                                    <label className="form-label">CVC </label>
                                                    <input type="text" className="form-control" placeholder={125} />
                                                </div>
                                                <div className="mb-3 col-xl-4">
                                                    <label className="form-label">Postal code </label>
                                                    <input type="text" className="form-control" placeholder={2368} />
                                                </div>
                                                <div className="text-center col-12">
                                                    <button type="submit" className="btn btn-success w-100">Save</button>
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