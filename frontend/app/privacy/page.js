
import Layout from "@/components/layout/Layout"

export default function Privacy() {

    return (
        <Layout breadcrumbTitle="Privacy">
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Privacy Policy</h4>
                        </div>
                        <div className="card-body">
                            <div className="privacy-content">
                                <p>BillWise is a personal expense-tracking tool. It stores the transactions, categories,
                                    payment method aliases, and budgets you enter so you can track your own spending —
                                    it does not move money, connect to bank accounts, or process payments.</p>
                            </div>
                            <div className="privacy-content">
                                <h5>What we store</h5>
                                <p>Your account details (email, display name), the financial data you enter (transactions,
                                    categories, budgets, goals, payment method aliases you name yourself), and, if you
                                    invite a partner, the data you choose to share with them.</p>
                            </div>
                            <div className="privacy-content">
                                <h5>What we don&apos;t collect</h5>
                                <p>BillWise never asks for or stores full card numbers, CVV codes, bank account or
                                    routing numbers, or banking login credentials. Payment methods are user-defined
                                    labels, not linked accounts.</p>
                            </div>
                            <div className="privacy-content">
                                <h5>Sharing</h5>
                                <p>Your data is not sold or shared with third parties. If you invite a partner to your
                                    household, they can see only the data you mark as shared.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
