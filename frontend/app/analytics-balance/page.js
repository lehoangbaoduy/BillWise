
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsBalance() {

    return (
        <Layout breadcrumbTitle="Balance">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <AnalyticsMenu />
                        <div className="row">
                            <div className="col-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Total Balance </h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-chart-line-up" message="Balance trends will appear once you add transactions." />
                                    </div>
                                </div>
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Balance by Wallet </h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-wallet" message="No tracked balances yet." />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

        </Layout>
    )
}
