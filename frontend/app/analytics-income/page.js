
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsIncome() {

    return (
        <Layout breadcrumbTitle="Income">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <AnalyticsMenu />
                        <div className="row">
                            <div className=" col-xxl-4 col-xl-4 col-lg-6 col-md-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Income Breakdown</h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-chart-pie-alt" message="No income recorded yet." />
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-8">
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
