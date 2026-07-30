
import ChartjsIncomeVsExpense from "@/components/chart/ChartjsIncomeVsExpense"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsIncomeExpenses() {

    return (
        <>
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
                                        <ChartjsIncomeVsExpense />
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Transaction History</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="transaction-table">
                                            <div className="table-responsive">
                                                <table className="table mb-0 table-responsive-sm">
                                                    <thead>
                                                        <tr>
                                                            <th>Category</th>
                                                            <th>Date</th>
                                                            <th>Description</th>
                                                            <th>Amount</th>
                                                            <th>Currency</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-emerald-500 fi fi-rr-barber-shop" />
                                                                    Beauty</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" /> Bills &amp;
                                                                    Fees</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-cyan-500 fi fi-rr-car-side" />
                                                                    Car</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-sky-500 fi fi-rr-graduation-cap" />
                                                                    Education</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-blue-500 fi fi-rr-clapperboard-play" />
                                                                    Entertainment</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-emerald-500 fi fi-rr-barber-shop" />
                                                                    Beauty</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" /> Bills &amp;
                                                                    Fees</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-cyan-500 fi fi-rr-car-side" />
                                                                    Car</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-sky-500 fi fi-rr-graduation-cap" />
                                                                    Education</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                        <tr>
                                                            <td>
                                                                <span className="table-category-icon"><i className="bg-blue-500 fi fi-rr-clapperboard-play" />
                                                                    Entertainment</span>
                                                            </td>
                                                            <td>
                                                                12.12.2023
                                                            </td>
                                                            <td>
                                                                Grocery Items and Beverage soft drinks
                                                            </td>
                                                            <td>
                                                                -32.20
                                                            </td>
                                                            <td>USD</td>
                                                        </tr>
                                                    </tbody>
                                                </table>
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