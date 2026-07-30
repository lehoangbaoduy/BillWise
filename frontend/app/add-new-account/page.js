
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function AddNewAccount() {

    return (
        <>
            <Layout breadcrumbTitle="Add New Account">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-8 col-md-7">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Add New Account</h4>
                                    </div>
                                    <div className="card-body add-bank-card">
                                        <div className="row">
                                            <div className="col-md-6">
                                                <Link href="/add-bank" className="d-block">
                                                    <div className="add-bank-card-content">
                                                        {/* <span class="add-card-icon"><i class="fi fi-rr-bank"></i></span> */}
                                                        <div className="flex-grow-1">
                                                            <h5>Bank account</h5>
                                                            <p>Use bank account to make purchase and sells. Prices are
                                                                locked today. Trades may take 4-5 days to process</p>
                                                            <p className="text-muted">Recommended for invest large amount</p>
                                                        </div>
                                                    </div>
                                                </Link>
                                            </div>
                                            <div className="col-md-6">
                                                <Link href="/add-card" className="d-block">
                                                    <div className="add-bank-card-content">
                                                        {/* <span class="add-card-icon"><i class="fi fi-rr-credit-card"></i></span> */}
                                                        <div className="flex-grow-1">
                                                            <h5>Debit card</h5>
                                                            <p>Use any visa or mastercard debit card to make small
                                                                investment. Add a bank or wallet to sell</p>
                                                            <p className="text-muted">Recommended for invest small amount</p>
                                                        </div>
                                                    </div>
                                                </Link>
                                            </div>
                                        </div>
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