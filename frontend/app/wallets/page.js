'use client'
import ChartjsBalanceOvertime from "@/components/chart/ChartjsBalanceOvertime"
import ChartjsBalanceOvertime2 from "@/components/chart/ChartjsBalanceOvertime2"
import ChartjsBalanceOvertime3 from "@/components/chart/ChartjsBalanceOvertime3"
import ChartjsBalanceOvertime4 from "@/components/chart/ChartjsBalanceOvertime4"
import Layout from "@/components/layout/Layout"
import Link from "next/link"
import { useState } from "react"
export default function Wallets() {
    const [activeIndex, setActiveIndex] = useState(1)
    const handleOnClick = (index) => {
        setActiveIndex(index)
    }
    return (
        <>
            <Layout breadcrumbTitle="Wallets">
                <div className="wallet-tab">
                    <div className="row g-0">
                        <div className="col-xl-3">
                            <div className="nav d-block">
                                <div className="row">
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(1)} className={activeIndex === 1 ? "wallet-nav active" : "wallet-nav"}>
                                            <div className="wallet-nav-icon">
                                                <span><i className="fi fi-rr-bank" /></span>
                                            </div>
                                            <div className="wallet-nav-text">
                                                <h3>City Bank</h3>
                                                <p>$221,478</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(2)} className={activeIndex === 2 ? "wallet-nav active" : "wallet-nav"}>
                                            <div className="wallet-nav-icon">
                                                <span><i className="fi fi-rr-credit-card" /></span>
                                            </div>
                                            <div className="wallet-nav-text">
                                                <h3>Debit Card</h3>
                                                <p>$221,478</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(3)} className={activeIndex === 3 ? "wallet-nav active" : "wallet-nav"}>
                                            <div className="wallet-nav-icon">
                                                <span><i className="fi fi-brands-visa" /></span>
                                            </div>
                                            <div className="wallet-nav-text">
                                                <h3>Visa Card</h3>
                                                <p>$221,478</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(4)} className={activeIndex === 4 ? "wallet-nav active" : "wallet-nav"}>
                                            <div className="wallet-nav-icon">
                                                <span><i className="fi fi-rr-money-bill-wave-alt" /></span>
                                            </div>
                                            <div className="wallet-nav-text">
                                                <h3>Cash</h3>
                                                <p>$221,478</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="add-card-link">
                                <h5 className="mb-0">Add new wallet</h5>
                                <Link href="/add-new-account">
                                    <i className="fi fi-rr-square-plus" />
                                </Link>
                            </div>
                        </div>
                        <div className="col-xl-9">
                            <div className="tab-content wallet-tab-content">
                                <div className={activeIndex == 1 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="wallet-tab-title">
                                        <h3>City Bank</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="wallet-total-balance">
                                                        <p className="mb-0">Total Balance</p>
                                                        <h2>$221,478</h2>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Personal Funds</p>
                                                        <h5>$32,500.28</h5>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Credit Limits</p>
                                                        <h5>$2500.00</h5>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="credit-card visa">
                                                <div className="type-brand">
                                                    <h4>Debit Card</h4>
                                                    <img src="./images/cc/visa.png" alt="" />
                                                </div>
                                                <div className="cc-number">
                                                    <h6>1234</h6>
                                                    <h6>5678</h6>
                                                    <h6>7890</h6>
                                                    <h6>9875</h6>
                                                </div>
                                                <div className="cc-holder-exp">
                                                    <h5>Saiful Islam</h5>
                                                    <div className="exp"><span>EXP:</span><strong>12/21</strong></div>
                                                </div>
                                                <div className="cc-info">
                                                    <div className="row justify-content-between align-items-center">
                                                        <div className="col-5">
                                                            <div className="d-flex">
                                                                <p className="me-3">Status</p>
                                                                <p><strong>Active</strong></p>
                                                            </div>
                                                            <div className="d-flex">
                                                                <p className="me-3">Currency</p>
                                                                <p><strong>USD</strong></p>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-7">
                                                            <div className="d-flex justify-content-between">
                                                                <div className="ms-3">
                                                                    <p>Credit Limit</p>
                                                                    <p><strong>2000 USD</strong></p>
                                                                </div>
                                                                <div id="circle1" />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Total Balance</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Monthly Expenses</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Balance Overtime</h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="chartjs-size-monitor">
                                                        <div className="chartjs-size-monitor-expand">
                                                            <div />
                                                        </div>
                                                        <div className="chartjs-size-monitor-shrink">
                                                            <div />
                                                        </div>
                                                    </div>
                                                    <ChartjsBalanceOvertime />
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
                                                                            <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" />
                                                                                Bills &amp;
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
                                <div className={activeIndex == 2 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="wallet-tab-title">
                                        <h3>Debit Card</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="wallet-total-balance">
                                                        <p className="mb-0">Total Balance</p>
                                                        <h2>$221,478</h2>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Personal Funds</p>
                                                        <h5>$32,500.28</h5>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Credit Limits</p>
                                                        <h5>$2500.00</h5>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="credit-card visa">
                                                <div className="type-brand">
                                                    <h4>Debit Card</h4>
                                                    <img src="./images/cc/visa.png" alt="" />
                                                </div>
                                                <div className="cc-number">
                                                    <h6>1234</h6>
                                                    <h6>5678</h6>
                                                    <h6>7890</h6>
                                                    <h6>9875</h6>
                                                </div>
                                                <div className="cc-holder-exp">
                                                    <h5>Saiful Islam</h5>
                                                    <div className="exp"><span>EXP:</span><strong>12/21</strong></div>
                                                </div>
                                                <div className="cc-info">
                                                    <div className="row justify-content-between align-items-center">
                                                        <div className="col-5">
                                                            <div className="d-flex">
                                                                <p className="me-3">Status</p>
                                                                <p><strong>Active</strong></p>
                                                            </div>
                                                            <div className="d-flex">
                                                                <p className="me-3">Currency</p>
                                                                <p><strong>USD</strong></p>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-7">
                                                            <div className="d-flex justify-content-between">
                                                                <div className="ms-3">
                                                                    <p>Credit Limit</p>
                                                                    <p><strong>2000 USD</strong></p>
                                                                </div>
                                                                <div id="circle1" />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Total Balance</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Monthly Expenses</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Balance Overtime</h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="chartjs-size-monitor">
                                                        <div className="chartjs-size-monitor-expand">
                                                            <div />
                                                        </div>
                                                        <div className="chartjs-size-monitor-shrink">
                                                            <div />
                                                        </div>
                                                    </div>
                                                    <ChartjsBalanceOvertime2 />
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
                                                                            <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" />
                                                                                Bills &amp;
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
                                <div className={activeIndex == 3 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="wallet-tab-title">
                                        <h3>Visa Card</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="wallet-total-balance">
                                                        <p className="mb-0">Total Balance</p>
                                                        <h2>$221,478</h2>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Personal Funds</p>
                                                        <h5>$32,500.28</h5>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Credit Limits</p>
                                                        <h5>$2500.00</h5>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="credit-card visa">
                                                <div className="type-brand">
                                                    <h4>Debit Card</h4>
                                                    <img src="./images/cc/visa.png" alt="" />
                                                </div>
                                                <div className="cc-number">
                                                    <h6>1234</h6>
                                                    <h6>5678</h6>
                                                    <h6>7890</h6>
                                                    <h6>9875</h6>
                                                </div>
                                                <div className="cc-holder-exp">
                                                    <h5>Saiful Islam</h5>
                                                    <div className="exp"><span>EXP:</span><strong>12/21</strong></div>
                                                </div>
                                                <div className="cc-info">
                                                    <div className="row justify-content-between align-items-center">
                                                        <div className="col-5">
                                                            <div className="d-flex">
                                                                <p className="me-3">Status</p>
                                                                <p><strong>Active</strong></p>
                                                            </div>
                                                            <div className="d-flex">
                                                                <p className="me-3">Currency</p>
                                                                <p><strong>USD</strong></p>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-7">
                                                            <div className="d-flex justify-content-between">
                                                                <div className="ms-3">
                                                                    <p>Credit Limit</p>
                                                                    <p><strong>2000 USD</strong></p>
                                                                </div>
                                                                <div id="circle1" />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Total Balance</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Monthly Expenses</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Balance Overtime</h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="chartjs-size-monitor">
                                                        <div className="chartjs-size-monitor-expand">
                                                            <div />
                                                        </div>
                                                        <div className="chartjs-size-monitor-shrink">
                                                            <div />
                                                        </div>
                                                    </div>
                                                    <ChartjsBalanceOvertime3 />
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
                                                                            <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" />
                                                                                Bills &amp;
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
                                <div className={activeIndex == 4 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="wallet-tab-title">
                                        <h3>Cash</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="wallet-total-balance">
                                                        <p className="mb-0">Total Balance</p>
                                                        <h2>$221,478</h2>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Personal Funds</p>
                                                        <h5>$32,500.28</h5>
                                                    </div>
                                                    <div className="funds-credit">
                                                        <p className="mb-0">Credit Limits</p>
                                                        <h5>$2500.00</h5>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xxl-6 col-xl-6 col-lg-6">
                                            <div className="credit-card visa">
                                                <div className="type-brand">
                                                    <h4>Debit Card</h4>
                                                    <img src="./images/cc/visa.png" alt="" />
                                                </div>
                                                <div className="cc-number">
                                                    <h6>1234</h6>
                                                    <h6>5678</h6>
                                                    <h6>7890</h6>
                                                    <h6>9875</h6>
                                                </div>
                                                <div className="cc-holder-exp">
                                                    <h5>Saiful Islam</h5>
                                                    <div className="exp"><span>EXP:</span><strong>12/21</strong></div>
                                                </div>
                                                <div className="cc-info">
                                                    <div className="row justify-content-between align-items-center">
                                                        <div className="col-5">
                                                            <div className="d-flex">
                                                                <p className="me-3">Status</p>
                                                                <p><strong>Active</strong></p>
                                                            </div>
                                                            <div className="d-flex">
                                                                <p className="me-3">Currency</p>
                                                                <p><strong>USD</strong></p>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-7">
                                                            <div className="d-flex justify-content-between">
                                                                <div className="ms-3">
                                                                    <p>Credit Limit</p>
                                                                    <p><strong>2000 USD</strong></p>
                                                                </div>
                                                                <div id="circle1" />
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Total Balance</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                                            <div className="stat-widget-1">
                                                <h6>Monthly Expenses</h6>
                                                <h3>$ 432568</h3>
                                                <p>
                                                    <span className="text-success"><i className="fi fi-rr-arrow-trend-up" />2.47%</span>
                                                    Last month <strong>$24,478</strong>
                                                </p>
                                            </div>
                                        </div>
                                        <div className="col-xxl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">Balance Overtime</h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="chartjs-size-monitor">
                                                        <div className="chartjs-size-monitor-expand">
                                                            <div />
                                                        </div>
                                                        <div className="chartjs-size-monitor-shrink">
                                                            <div />
                                                        </div>
                                                    </div>
                                                    <ChartjsBalanceOvertime4 />
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
                                                                            <span className="table-category-icon"><i className="bg-teal-500 fi fi-rr-receipt" />
                                                                                Bills &amp;
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
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}