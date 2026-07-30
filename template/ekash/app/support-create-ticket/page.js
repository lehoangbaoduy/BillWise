
import Layout from "@/components/layout/Layout"
export default function CreateTicket() {

    return (
        <>
            <Layout breadcrumbTitle="Create Ticket">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Create Ticket</h4>
                                <span>Cancel</span>
                            </div>
                            <div className="card-body">
                                <form action="support-tickets">
                                    <div className="mb-3">
                                        <label className="form-label">What the type question do you want?</label>
                                        <select className="form-select">
                                            <option> Earning</option>
                                            <option> Withdrawals</option>
                                            <option> Profile</option>
                                            <option> General</option>
                                            <option> Others</option>
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Employe Respond</label>
                                        <select className="form-select">
                                            <option> Earning</option>
                                            <option> Withdrawals</option>
                                            <option> Profile</option>
                                            <option> General</option>
                                            <option> Others</option>
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">What language do you prefer to be answered?</label>
                                        <select className="form-select">
                                            <option> Earning</option>
                                            <option> Withdrawals</option>
                                            <option> Profile</option>
                                            <option> General</option>
                                            <option> Others</option>
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Please provide a description of the problem you are
                                            encountering</label>
                                        <textarea name id rows={5} className="form-control" defaultValue={""} />
                                    </div>
                                    <button type="submit" className="btn btn-primary">Create</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}