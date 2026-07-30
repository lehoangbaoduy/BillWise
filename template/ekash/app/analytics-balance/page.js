
import ChartjsBalanceWallet from "@/components/chart/ChartjsBalanceWallet"
import ChartjsTotalBalance from "@/components/chart/ChartjsTotalBalance"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsBanalce() {

    return (
        <>
            <Layout breadcrumbTitle="Banalce">
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
                                        <ChartjsTotalBalance />
                                    </div>
                                </div>
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Balance by Wallet </h4>
                                    </div>
                                    <div className="card-body">
                                        <ChartjsBalanceWallet />
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