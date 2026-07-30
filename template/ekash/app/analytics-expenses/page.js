
import ChartjsDonut from "@/components/chart/ChartjsDonut"
import Layout from "@/components/layout/Layout"
import AnalyticsMenu from "@/components/layout/AnalyticsMenu"
export default function AnalyticsExpenses() {

    return (
        <>
            <Layout breadcrumbTitle="Expenses">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <AnalyticsMenu />
                        <div className="row">
                            <div className=" col-xxl-4 col-xl-4 col-lg-4 col-md-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Expenses Breakdown</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="text-center">
                                            <ChartjsDonut />
                                        </div>
                                        <div className="list-1 mt-3">
                                            <ul>
                                                <li>
                                                    <p className="mb-0">Food</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Transport</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Healthcare</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Education</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Clothes</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Pets</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                                <li>
                                                    <p className="mb-0">Entertainment</p>
                                                    <h5 className="mb-0"><span>$1200</span>38%</h5>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-8 col-lg-8">
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