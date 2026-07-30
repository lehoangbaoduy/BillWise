'use client'
import ChartjsIncomeVsExpense from "@/components/chart/ChartjsIncomeVsExpense"
import ChartjsProfileWallet from "@/components/chart/ChartjsProfileWallet"
import ChartjsWeeklyExpenses from "@/components/chart/ChartjsWeeklyExpenses"
import CircularProgress from "@/components/elements/CircularProgress"
import Layout from "@/components/layout/Layout"
import Link from "next/link"
import PerfectScrollbar from "react-perfect-scrollbar"
export default function Home() {

    return (
        <>
            <Layout breadcrumbTitle="Dashboard">
                <div className="row">
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Balance</h6>
                            <h3>$ 432568</h3>
                            <p>
                                <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                Last month <strong>$24,478</strong>
                            </p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Change</h6>
                            <h3>$ 245860</h3>
                            <p>
                                <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                Last month <strong>$24,478</strong>
                            </p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Expenses</h6>
                            <h3>$ 25.35</h3>
                            <p>
                                <span className="text-danger"><i className="fi fi-rr-arrow-trend-down" />2.47%</span>
                                Last month <strong>$24,478</strong>
                            </p>
                        </div>
                    </div>
                    <div className="col-xl-3 col-lg-6 col-md-6 col-sm-6">
                        <div className="stat-widget-1">
                            <h6>Total Period Income</h6>
                            <h3>$ 22.56</h3>
                            <p>
                                <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                Last month <strong>$24,478</strong>
                            </p>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col-xxl-8 col-xl-8 col-lg-6">
                        <div className="card">
                            <div className="card-header balance-trend">
                                <h4 className="card-title">Balace Trends <br /> <span>$221,478</span></h4>
                                <div className="trend-stats">
                                    <p className="mb-0">Last Month</p>
                                    <span className="text-success">
                                        <i className="fi fi-rr-arrow-trend-up" />
                                        12.25%
                                    </span>
                                </div>
                            </div>
                            <div className="card-body">
                                <ChartjsProfileWallet />
                            </div>
                        </div>
                    </div>
                    <div className=" col-xxl-4 col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Expenses Breakdown</h4>
                            </div>
                            <div className="card-body">
                                <div className="progress-stacked">
                                    <div className="progress" style={{ width: '38%' }}>
                                        <div className="progress-bar bg-orange-500" />
                                    </div>
                                    <div className="progress" style={{ width: '22%' }}>
                                        <div className="progress-bar bg-amber-500" />
                                    </div>
                                    <div className="progress" style={{ width: '12%' }}>
                                        <div className="progress-bar bg-yellow-500" />
                                    </div>
                                    <div className="progress" style={{ width: '9%' }}>
                                        <div className="progress-bar bg-lime-500" />
                                    </div>
                                    <div className="progress" style={{ width: '8%' }}>
                                        <div className="progress-bar bg-green-500" />
                                    </div>
                                    <div className="progress" style={{ width: '6%' }}>
                                        <div className="progress-bar bg-cyan-500" />
                                    </div>
                                    <div className="progress" style={{ width: '5%' }}>
                                        <div className="progress-bar bg-stone-500" />
                                    </div>
                                </div>
                                <div className="list-1 mt-3">
                                    <ul>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-orange-500" />Food</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-amber-500" />Transport</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-yellow-500" />Healthcare</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-lime-500" />Education</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-green-500" />Clothes</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-cyan-500" />Pets</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                        <li>
                                            <p className="mb-0"><i className="fi fi-ss-circle text-stone-500" />Entertainment</p>
                                            <h5 className="mb-0"><span>$1200</span>38%</h5>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Budgets</h4>
                            </div>
                            <div className="card-body">
                                <div className="budget-content">
                                    <PerfectScrollbar>
                                        <ul>
                                            <li>
                                                <div className="budget-info flex-grow-2 me-3">
                                                    <div className="d-flex justify-content-between align-items-center mb-1">
                                                        <h5 className="mb-1"><i className="bg-green-500 fi fi-rr-carrot" />Grocery
                                                            Stores</h5>
                                                        <p className="mb-0"><strong>75 </strong>/ 100</p>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar bg-green-500" role="progressbar" style={{ width: '75%' }}>
                                                        </div>
                                                    </div>
                                                </div>
                                            </li>
                                            <li>
                                                <div className="budget-info flex-grow-2 me-3">
                                                    <div className="d-flex justify-content-between align-items-center mb-1">
                                                        <h5 className="mb-1"><i className="bg-cyan-500 fi fi-rr-bus" />Transportation
                                                        </h5>
                                                        <p className="mb-0"><strong>25 </strong>/ 100</p>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar bg-cyan-500" role="progressbar" style={{ width: '25%' }} />
                                                    </div>
                                                </div>
                                            </li>
                                            <li>
                                                <div className="budget-info flex-grow-2 me-3">
                                                    <div className="d-flex justify-content-between align-items-center mb-1">
                                                        <h5 className="mb-1"><i className="bg-sky-500 fi fi-sr-cat" />Pets</h5>
                                                        <p className="mb-0"><strong>50 </strong>/ 100</p>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar bg-sky-500" role="progressbar" style={{ width: '50%' }} />
                                                    </div>
                                                </div>
                                            </li>
                                            <li>
                                                <div className="budget-info flex-grow-2 me-3">
                                                    <div className="d-flex justify-content-between align-items-center mb-1">
                                                        <h5 className="mb-1"><i className="bg-indigo-500 fi fi-rr-graduation-cap" />Education</h5>
                                                        <p className="mb-0"><strong>45 </strong>/ 100</p>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar bg-indigo-500" role="progressbar" style={{ width: '45%' }} />
                                                    </div>
                                                </div>
                                            </li>
                                            <li>
                                                <div className="budget-info flex-grow-2 me-3">
                                                    <div className="d-flex justify-content-between align-items-center mb-1">
                                                        <h5 className="mb-1"><i className="bg-violet-500 fi fi-rr-shirt-long-sleeve" />Clothes
                                                        </h5>
                                                        <p className="mb-0"><strong>35 </strong>/ 100</p>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar bg-violet-500" role="progressbar" style={{ width: '35%' }} />
                                                    </div>
                                                </div>
                                            </li>
                                        </ul>
                                    </PerfectScrollbar>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className=" col-xxl-8 col-xl-8 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Monthly Income vs Expenses</h4>
                            </div>
                            <div className="card-body">
                                <ChartjsIncomeVsExpense />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-8 col-lg-6">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Weekly Expenses</h4>
                            </div>
                            <div className="card-body">
                                <ChartjsWeeklyExpenses />
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4 col-lg-6 col-md-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Payments History</h4>
                                <Link href="#">See more</Link>
                            </div>
                            <div className="card-body">
                                <div className="invoice-content">
                                    <PerfectScrollbar>
                                        <ul>
                                            <li className="d-flex justify-content-between active">
                                                <div className="d-flex align-items-center">
                                                    <div className="invoice-info">
                                                        <h5 className="mb-0">Electricity</h5>
                                                        <p>5 january 2024</p>
                                                    </div>
                                                </div>
                                                <div className="text-end">
                                                    <h5 className="mb-2">+450.00</h5>
                                                    <span className=" text-white bg-success">Paid</span>
                                                </div>
                                            </li>
                                            <li className="d-flex justify-content-between">
                                                <div className="d-flex align-items-center">
                                                    <div className="invoice-info">
                                                        <h5 className="mb-0">Internet</h5>
                                                        <p>5 january 2024</p>
                                                    </div>
                                                </div>
                                                <div className="text-end">
                                                    <h5 className="mb-2">+450.00</h5>
                                                    <span className=" text-white bg-warning">Due</span>
                                                </div>
                                            </li>
                                            <li className="d-flex justify-content-between">
                                                <div className="d-flex align-items-center">
                                                    <div className="invoice-info">
                                                        <h5 className="mb-0">Apple Music</h5>
                                                        <p>5 january 2024</p>
                                                    </div>
                                                </div>
                                                <div className="text-end">
                                                    <h5 className="mb-2">+450.00</h5>
                                                    <span className=" text-white bg-danger">Cancel</span>
                                                </div>
                                            </li>
                                            <li className="d-flex justify-content-between">
                                                <div className="d-flex align-items-center">
                                                    <div className="invoice-info">
                                                        <h5 className="mb-0">Groceries</h5>
                                                        <p>5 january 2024</p>
                                                    </div>
                                                </div>
                                                <div className="text-end">
                                                    <h5 className="mb-2">+450.00</h5>
                                                    <span className=" text-white bg-success">Paid</span>
                                                </div>
                                            </li>
                                        </ul>
                                    </PerfectScrollbar>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-4">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Saving Goals </h4>
                            </div>
                            <div className="card-body">
                                <div className="row">
                                    <div className="col-xl-6 col-md-3 col-sm-6">
                                        <div className="circle-progress-content">
                                            <CircularProgress value={80} height={130} width={130} margin="0 auto" />
                                            <h6>Vacation</h6>
                                        </div>
                                    </div>
                                    <div className="col-xl-6 col-md-3 col-sm-6">
                                        <div className="circle-progress-content">
                                            <CircularProgress value={90} height={130} width={130} margin="0 auto" />
                                            <h6>Gift</h6>
                                        </div>
                                    </div>
                                    <div className="col-xl-6 col-md-3 col-sm-6">
                                        <div className="circle-progress-content">
                                            <CircularProgress value={95} height={130} width={130} margin="0 auto" />
                                            <h6>New Car</h6>
                                        </div>
                                    </div>
                                    <div className="col-xl-6 col-md-3 col-sm-6">
                                        <div className="circle-progress-content">
                                            <CircularProgress value={99} height={130} width={130} margin="0 auto" />
                                            <h6>Laptop</h6>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-xl-8">
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
                                                        <span className="table-category-icon"><i className="bg-cyan-500 fi fi-rr-car-side" /> Car</span>
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
            </Layout>
        </>
    )
}