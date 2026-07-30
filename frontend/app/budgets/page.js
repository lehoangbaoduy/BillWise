'use client'
import ChartjsBudgetPeriod from "@/components/chart/ChartjsBudgetPeriod"
import ChartjsBudgetPeriod2 from "@/components/chart/ChartjsBudgetPeriod2"
import ChartjsBudgetPeriod3 from "@/components/chart/ChartjsBudgetPeriod3"
import ChartjsBudgetPeriod4 from "@/components/chart/ChartjsBudgetPeriod4"
import Layout from "@/components/layout/Layout"
import Link from "next/link"
import { useState } from "react"
export default function Budgets() {
    const [activeIndex, setActiveIndex] = useState(1)
    const handleOnClick = (index) => {
        setActiveIndex(index)
    }
    return (
        <>
            <Layout breadcrumbTitle="Budgets">
                <div className="budgets-tab">
                    <div className="row g-0">
                        <div className="col-xl-3">
                            <div className="nav d-block">
                                <div className="row">
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(1)} className={activeIndex === 1 ? "budgets-nav active" : "budgets-nav"}>
                                            <div className="budgets-nav-icon">
                                                <span><i className="fi fi-rr-carrot" /></span>
                                            </div>
                                            <div className="budgets-nav-text">
                                                <h3>Grocery</h3>
                                                <p>$1458.30</p>
                                            </div>
                                            <span className="show-time">Overtime</span>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(2)} className={activeIndex === 2 ? "budgets-nav active" : "budgets-nav"}>
                                            <div className="budgets-nav-icon">
                                                <span><i className="fi fi-rr-shirt-long-sleeve" /></span>
                                            </div>
                                            <div className="budgets-nav-text">
                                                <h3>Cloths</h3>
                                                <p>$1458.30</p>
                                            </div>
                                            <span className="show-time">Week</span>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(3)} className={activeIndex === 3 ? "budgets-nav active" : "budgets-nav"}>
                                            <div className="budgets-nav-icon">
                                                <span><i className="fi fi-rr-car-bus" /></span>
                                            </div>
                                            <div className="budgets-nav-text">
                                                <h3>Transportation</h3>
                                                <p>$1458.30</p>
                                            </div>
                                            <span className="show-time">Month</span>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(4)} className={activeIndex === 4 ? "budgets-nav active" : "budgets-nav"}>
                                            <div className="budgets-nav-icon">
                                                <span><i className="fi fi-rr-graduation-cap" /></span>
                                            </div>
                                            <div className="budgets-nav-text">
                                                <h3>Education</h3>
                                                <p>$1458.30</p>
                                            </div>
                                            <span className="show-time">Day</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="add-budgets-link">
                                <h5 className="mb-0">Add new budget</h5>
                                <Link href="/add-new-account">
                                    <i className="fi fi-rr-square-plus" />
                                </Link>
                            </div>
                        </div>
                        <div className="col-xl-9">
                            <div className="tab-content budgets-tab-content">
                                <div className={activeIndex == 1 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="budgets-tab-title">
                                        <h3>Grocery</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Spend</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Budget</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar" style={{ width: '25%' }} role="progressbar">
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>25%</span>
                                                        <span>75%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="row">
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Debt</p>
                                                                <h3>$365,478</h3>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Budget Period </h4>
                                                </div>
                                                <div className="card-body">
                                                    <ChartjsBudgetPeriod />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 2 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="budgets-tab-title">
                                        <h3>Cloths</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Spend</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Budget</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar" style={{ width: '25%' }} role="progressbar">
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>25%</span>
                                                        <span>75%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="row">
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Debt</p>
                                                                <h3>$365,478</h3>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Budget Period </h4>
                                                </div>
                                                <div className="card-body">
                                                    <ChartjsBudgetPeriod2 />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 3 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="budgets-tab-title">
                                        <h3>Transportation</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Spend</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Budget</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar" style={{ width: '25%' }} role="progressbar">
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>25%</span>
                                                        <span>75%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="row">
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Debt</p>
                                                                <h3>$365,478</h3>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Budget Period </h4>
                                                </div>
                                                <div className="card-body">
                                                    <ChartjsBudgetPeriod3 />
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 4 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="budgets-tab-title">
                                        <h3>Education</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Spend</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Budget</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                    </div>
                                                    <div className="progress">
                                                        <div className="progress-bar" style={{ width: '25%' }} role="progressbar">
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-2">
                                                        <span>25%</span>
                                                        <span>75%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="row">
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="budget-widget">
                                                                <p>Debt</p>
                                                                <h3>$365,478</h3>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Budget Period </h4>
                                                </div>
                                                <div className="card-body">
                                                    <ChartjsBudgetPeriod4 />
                                                </div>
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