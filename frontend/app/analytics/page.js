
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function Analytics() {

    return (
        <Layout breadcrumbTitle="Analytics">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <AnalyticsMenu />
                        <div className="row">
                            <div className="col-xl-3 col-sm-6">
                                <div className="analytics-widget">
                                    <div className="widget-icon me-3 bg-primary"><span><i className="fi fi-rr-mobile" /></span>
                                    </div>
                                    <div className="widget-content">
                                        <p>Daily Average</p>
                                        <h3>$ 0.00</h3>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="analytics-widget">
                                    <div className="widget-icon me-3 bg-success"><span><i className="fi fi-rr-replace" /></span>
                                    </div>
                                    <div className="widget-content">
                                        <p>Change</p>
                                        <h3>0%</h3>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="analytics-widget">
                                    <div className="widget-icon me-3 bg-warning"><span><i className="fi fi-rs-receipt" /></span>
                                    </div>
                                    <div className="widget-content">
                                        <p>Total Transaction</p>
                                        <h3>0</h3>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="analytics-widget">
                                    <div className="widget-icon me-3 bg-danger">
                                        <span><i className="fi fi-ss-confetti" /></span>
                                    </div>
                                    <div className="widget-content">
                                        <p>Categories</p>
                                        <h3>0</h3>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Weekly Expenses </h4>
                                    </div>
                                    <div className="card-body">
                                        <EmptyState icon="fi fi-rr-chart-line-up" message="No expenses recorded this week." />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>


        </Layout>
    )
}
