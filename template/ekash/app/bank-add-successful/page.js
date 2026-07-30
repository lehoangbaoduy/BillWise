
import Layout from "@/components/layout/Layout"
export default function BankAddSuccessfull() {

    return (
        <>
            <Layout breadcrumbTitle="Bank Add Successfull">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body identity-content">
                                        <form action="settings-bank">
                                            <span className="icon"><i className="fi fi-bs-check" /></span>
                                            <h4>Congratulation. Successfully your account added</h4>
                                            <p>Efficiently provide access to installed base core competencies and end
                                                end
                                                data Interactively target equity.</p>
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