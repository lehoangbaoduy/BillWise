'use client'
import CircularProgress from "@/components/elements/CircularProgress"
import Layout from "@/components/layout/Layout"
import Link from "next/link"
import { useState } from "react"
export default function Goals() {
    const [activeIndex, setActiveIndex] = useState(1)
    const handleOnClick = (index) => {
        setActiveIndex(index)
    }
    return (
        <>
            <Layout breadcrumbTitle="Goals">
                <div className="goals-tab">
                    <div className="row g-0">
                        <div className="col-xl-3">
                            <div className="nav d-block">
                                <div className="row">
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(1)} className={activeIndex === 1 ? "goals-nav active" : "goals-nav"}>
                                            <CircularProgress value={80} height={50} width={50} margin="0 15px 0 0" />
                                            <div className="goals-nav-text">
                                                <h3>Car</h3>
                                                <p><strong>$1458.30</strong> / $4580.85</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(2)} className={activeIndex === 2 ? "goals-nav active" : "goals-nav"}>
                                            <CircularProgress value={80} height={50} width={50} margin="0 15px 0 0" />
                                            <div className="goals-nav-text">
                                                <h3>Laptop</h3>
                                                <p><strong>$1458.30</strong> / $4580.85</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(3)} className={activeIndex === 3 ? "goals-nav active" : "goals-nav"}>
                                            <CircularProgress value={80} height={50} width={50} margin="0 15px 0 0" />
                                            <div className="goals-nav-text">
                                                <h3>Vacation</h3>
                                                <p><strong>$1458.30</strong> / $4580.85</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-xl-12 col-md-6">
                                        <div onClick={() => handleOnClick(4)} className={activeIndex === 4 ? "goals-nav active" : "goals-nav"}>
                                            <CircularProgress value={80} height={50} width={50} margin="0 15px 0 0" />
                                            <div className="goals-nav-text">
                                                <h3>Phone</h3>
                                                <p><strong>$1458.30</strong> / $4580.85</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="add-goals-link">
                                <h5 className="mb-0">Add new goals</h5>
                                <Link href="/add-new-account">
                                    <i className="fi fi-rr-square-plus" />
                                </Link>
                            </div>
                        </div>
                        <div className="col-xl-9">
                            <div className="tab-content goals-tab-content">
                                <div className={activeIndex == 1 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="goals-tab-title">
                                        <h3>Car</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Saved</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Goals</span>
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
                                                            <div className="goals-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
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
                                                    <h4 className="card-title">Available by Wallet</h4>
                                                </div>
                                                <div className="card-body available-wallet">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-yellow-500"><i className="fi fi-rr-bank" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">City Bank</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar" role="progressbar" style={{ width: '75%' }}>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-indigo-500"><i className="fi fi-rr-money-bills-simple" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Cash Wallet</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-success" role="progressbar" style={{ width: '25%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-purple-500"><i className="fi fi-rr-credit-card" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Visa Card</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-info" role="progressbar" style={{ width: '50%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">History </h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="table-responsive">
                                                        <table className="table mb-0 table-responsive-sm goals-history-table">
                                                            <thead>
                                                                <tr>
                                                                    <th>Date</th>
                                                                    <th>wallet</th>
                                                                    <th>Description</th>
                                                                    <th>Amount</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 2 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="goals-tab-title">
                                        <h3>Laptop</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Saved</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Goals</span>
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
                                                            <div className="goals-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
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
                                                    <h4 className="card-title">Available by Wallet</h4>
                                                </div>
                                                <div className="card-body available-wallet">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-yellow-500"><i className="fi fi-rr-bank" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">City Bank</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar" role="progressbar" style={{ width: '75%' }}>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-indigo-500"><i className="fi fi-rr-money-bills-simple" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Cash Wallet</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-success" role="progressbar" style={{ width: '25%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-purple-500"><i className="fi fi-rr-credit-card" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Visa Card</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-info" role="progressbar" style={{ width: '50%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">History </h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="table-responsive">
                                                        <table className="table mb-0 table-responsive-sm goals-history-table">
                                                            <thead>
                                                                <tr>
                                                                    <th>Date</th>
                                                                    <th>wallet</th>
                                                                    <th>Description</th>
                                                                    <th>Amount</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 3 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="goals-tab-title">
                                        <h3>Vacation</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Saved</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Goals</span>
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
                                                            <div className="goals-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
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
                                                    <h4 className="card-title">Available by Wallet</h4>
                                                </div>
                                                <div className="card-body available-wallet">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-yellow-500"><i className="fi fi-rr-bank" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">City Bank</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar" role="progressbar" style={{ width: '75%' }}>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-indigo-500"><i className="fi fi-rr-money-bills-simple" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Cash Wallet</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-success" role="progressbar" style={{ width: '25%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-purple-500"><i className="fi fi-rr-credit-card" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Visa Card</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-info" role="progressbar" style={{ width: '50%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">History </h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="table-responsive">
                                                        <table className="table mb-0 table-responsive-sm goals-history-table">
                                                            <thead>
                                                                <tr>
                                                                    <th>Date</th>
                                                                    <th>wallet</th>
                                                                    <th>Description</th>
                                                                    <th>Amount</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={activeIndex == 4 ? "tab-pane fade show active" : "tab-pane fade"}>
                                    <div className="goals-tab-title">
                                        <h3>Phone</h3>
                                    </div>
                                    <div className="row">
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-body">
                                                    <div className="d-flex justify-content-between">
                                                        <div>
                                                            <span>Saved</span>
                                                            <h3>$1458.30</h3>
                                                        </div>
                                                        <div className="text-end">
                                                            <span>Goals</span>
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
                                                            <div className="goals-widget">
                                                                <p>Last Month</p>
                                                                <h3>$42,678</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Expenses</p>
                                                                <h3>$1,798</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
                                                                <p>Taxes</p>
                                                                <h3>$255.25</h3>
                                                            </div>
                                                        </div>
                                                        <div className="col-xl-3 col-lg-3 col-md-6 col-sm-6">
                                                            <div className="goals-widget">
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
                                                    <h4 className="card-title">Available by Wallet</h4>
                                                </div>
                                                <div className="card-body available-wallet">
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-yellow-500"><i className="fi fi-rr-bank" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">City Bank</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar" role="progressbar" style={{ width: '75%' }}>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-indigo-500"><i className="fi fi-rr-money-bills-simple" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Cash Wallet</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-success" role="progressbar" style={{ width: '25%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="d-flex justify-content-between align-items-center">
                                                        <div className="d-flex flex-grow-2 goals-wallet-progress">
                                                            <div className="goals-icon">
                                                                <span className="bg-purple-500"><i className="fi fi-rr-credit-card" /></span>
                                                            </div>
                                                            <div className="goals-info flex-grow-2 me-3">
                                                                <div className="d-flex justify-content-between mb-1">
                                                                    <h5 className="mb-1">Visa Card</h5>
                                                                    <p className="mb-0">150$</p>
                                                                </div>
                                                                <div className="progress">
                                                                    <div className="progress-bar bg-info" role="progressbar" style={{ width: '50%' }} />
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-12">
                                            <div className="card">
                                                <div className="card-header">
                                                    <h4 className="card-title">History </h4>
                                                </div>
                                                <div className="card-body">
                                                    <div className="table-responsive">
                                                        <table className="table mb-0 table-responsive-sm goals-history-table">
                                                            <thead>
                                                                <tr>
                                                                    <th>Date</th>
                                                                    <th>wallet</th>
                                                                    <th>Description</th>
                                                                    <th>Amount</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td><span><i className="fi fi-rr-calendar" /></span> 29 Jan 2024</td>
                                                                    <td><span><i className="fi fi-rr-credit-card" /></span> Master Card</td>
                                                                    <td>Necessities</td>
                                                                    <td>
                                                                        <h5>+100.00$</h5>
                                                                        <span>12.368$</span>
                                                                    </td>
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

            </Layout>
        </>
    )
}