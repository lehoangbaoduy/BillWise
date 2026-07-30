
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsIncomeExpenses() {

    return (
        <Layout breadcrumbTitle="Income Expenses">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <AnalyticsMenu />
                        <div className="row">
                            <div className="col-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Income vs Expense Graph</h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-chart-line-up" message="No income or expenses recorded yet." />
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Transaction History</h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-receipt" message="No transactions yet — add your first one." />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

        </Layout>
    )
}
