'use client'
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"

// M2 scope (PRD §9.1, §9.6): de-mock the template and show honest empty states.
// Real numbers require Transactions (M3), Budgets/Goals (M4), and Recurring
// Bills (M6) backends, none of which exist yet — the charts and widgets below
// get real data wiring when those milestones land, not before.
export default function Home() {

    return (
        <Layout breadcrumbTitle="Dashboard">
                <div className="row">
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Balance</h6>
                            <h3>$ 0.00</h3>
                            <p className="text-muted mb-0">No tracked balances yet</p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Change</h6>
                            <h3>$ 0.00</h3>
                            <p className="text-muted mb-0">No data yet</p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Expenses</h6>
                            <h3>$ 0.00</h3>
                            <p className="text-muted mb-0">No expenses recorded yet</p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Income</h6>
                            <h3>$ 0.00</h3>
                            <p className="text-muted mb-0">No income recorded yet</p>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xxl-8 col-xl-8 col-lg-6">
                        <div className="card">
                            <div className="card-header balance-trend">
                                <h4 className="card-title">Balance Trends</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-chart-line-up" message="Balance trends will appear once you add transactions." />
                            </div>
                        </div>
                    </div>
                    <div className=" col-xxl-4 col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Expenses Breakdown</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-chart-pie-alt" message="No spending recorded yet." />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Budgets</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-wallet" message="No budgets set for this month." />
                            </div>
                        </div>
                    </div>
                    <div className=" col-xxl-8 col-xl-8 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Income vs Expenses</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-chart-line-up" message="No income or expenses recorded yet." />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-8 col-lg-6">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Weekly Expenses</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-chart-line-up" message="No expenses recorded this week." />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Recurring Bills</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-receipt" message="No recurring bills yet." />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Saving Goals</h4>
                            </div>
                            <div className="card-body">
                                <EmptyState icon="fi fi-rr-piggy-bank" message="No savings goals yet." />
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
        </Layout>
    )
}
