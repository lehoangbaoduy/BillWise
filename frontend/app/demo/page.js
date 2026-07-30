import ThemeSwitch from "@/components/elements/ThemeSwitch"
import Link from "next/link"

export default function Demo() {
    return (
        <>
            <div id="main-wrapper">
                <div className="header landing">
                    <div className="container">
                        <div className="row">
                            <div className="col-xl-12">
                                <div className="navigation">
                                    <nav className="navbar navbar-expand-lg">
                                        <div className="brand-logo m-0">
                                            <Link href="/">
                                                <img src="/images/logo.png" alt />
                                            </Link>
                                        </div>
                                        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                                            <span className="navbar-toggler-icon" />
                                        </button>
                                        <div className="collapse navbar-collapse" id="navbarNavDropdown">
                                            <ul className="navbar-nav ms-auto demo-nav">
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-intro">Home</Link>
                                                </li>
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-pages">Pages</Link>
                                                </li>
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-widgets">Widgets</Link>
                                                </li>
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-features">Features</Link>
                                                </li>
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-review">Review</Link>
                                                </li>
                                                <li className="nav-item">
                                                    <Link className="nav-link" href="#demo-support">Support</Link>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="header-right">
                                            <Link href="#" className="btn btn-primary">Buy</Link>
                                        </div>
                                    </nav>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="demo-intro" id="demo-intro" data-scroll-index={0}>
                    <div className="container">
                        <div className="row align-items-center justify-content-between">
                            <div className="col-xl-6 col-md-6 my-5">
                                <div className="demo-intro-content">
                                    <h1>Ekash - Personal Finance Management Admin Dashboard Nextjs Template</h1>
                                    <p>Personal Finance Management refers to the process of managing an individual's or a
                                        household's financial resources with the goal of achieving financial stability and meeting
                                        both short-term and long-term financial objectives. </p>
                                </div>
                                <div className="demo-intro-counter">
                                    <div className="row">
                                        <div className="col-md-3">
                                            <h3>45+
                                                <span>Pages</span>
                                            </h3>
                                        </div>
                                        <div className="col-md-4">
                                            <h3>100+
                                                <span>Components</span>
                                            </h3>
                                        </div>
                                        <div className="col-md-3">
                                            <h3>300+
                                                <span>Widgets</span>
                                            </h3>
                                        </div>
                                    </div>
                                </div>
                                <div className="demo-intro-btn">
                                    <Link href="#demo-pages" className="btn btn-primary me-3" data-scroll-nav={1}>View Demo</Link>
                                    <Link href="#" className="btn btn-outline-primary">Buy</Link>
                                </div>
                            </div>
                            <div className="col-xl-6 col-md-6 py-md-5">
                                <div className="row intro-card">
                                    <div className="col-xl-6 intro-card-up">
                                        <img src="/images/card/1.png" alt />
                                        <img src="/images/card/2.png" alt />
                                        <img src="/images/card/3.png" alt />
                                        <img src="/images/card/4.png" alt />
                                        <img src="/images/card/5.png" alt />
                                        <img src="/images/card/6.png" alt />
                                        <img src="/images/card/7.png" alt />
                                        <img src="/images/card/8.png" alt />
                                        <img src="/images/card/9.png" alt />
                                        <img src="/images/card/10.png" alt />
                                        <img src="/images/card/11.png" alt />
                                        <img src="/images/card/12.png" alt />
                                        <img src="/images/card/13.png" alt />
                                        <img src="/images/card/14.png" alt />
                                        <img src="/images/card/15.png" alt />
                                        <img src="/images/card/16.png" alt />
                                        <img src="/images/card/17.png" alt />
                                        <img src="/images/card/18.png" alt />
                                        <img src="/images/card/19.png" alt />
                                        <img src="/images/card/20.png" alt />
                                        <img src="/images/card/37.png" alt />
                                        {/* <img src="/images/card/38.png" alt="" /> */}
                                    </div>
                                    <div className="col-xl-6 intro-card-up">
                                        <img src="/images/card/21.png" alt />
                                        <img src="/images/card/22.png" alt />
                                        <img src="/images/card/23.png" alt />
                                        <img src="/images/card/24.png" alt />
                                        <img src="/images/card/25.png" alt />
                                        <img src="/images/card/26.png" alt />
                                        <img src="/images/card/27.png" alt />
                                        <img src="/images/card/28.png" alt />
                                        <img src="/images/card/29.png" alt />
                                        <img src="/images/card/30.png" alt />
                                        <img src="/images/card/31.png" alt />
                                        <img src="/images/card/32.png" alt />
                                        <img src="/images/card/33.png" alt />
                                        <img src="/images/card/34.png" alt />
                                        <img src="/images/card/35.png" alt />
                                        <img src="/images/card/36.png" alt />
                                        <img src="/images/card/39.png" alt />
                                        <img src="/images/card/40.png" alt />
                                    </div>
                                </div>
                                {/* <div class="intro-demo_img">
                  <img src="/images/demo/intro.png" alt="" class="img-fluid">
              </div> */}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="demo section-padding" id="demo-pages">
                    <div className="container">
                        <div className="row py-lg-5 justify-content-center">
                            <div className="col-xl-7">
                                <div className="section-title text-center">
                                    <span>Pages</span>
                                    <h2>Explore a Package Loaded with Interactive Live Demos</h2>
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/">
                                        <div className="img-wrap">
                                            <img src="/images/demo/dashboard.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Dashboard</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/wallets">
                                        <div className="img-wrap">
                                            <img src="/images/demo/wallets.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Wallets</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/budgets">
                                        <div className="img-wrap">
                                            <img src="/images/demo/budgets.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Budgets</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/goals">
                                        <div className="img-wrap">
                                            <img src="/images/demo/goals.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Goals</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/profile">
                                        <div className="img-wrap">
                                            <img src="/images/demo/profile.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Profile</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Analytics</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics-expenses">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics-expenses.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Expenses</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics-income">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics-income.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Income</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics-income-vs-expenses">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics-income-vs-expenses.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Income vs Expenses</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics-balance">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics-balance.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Balance</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/analytics-transaction-history">
                                        <div className="img-wrap">
                                            <img src="/images/demo/analytics-transaction-history.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Transaction History</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/support">
                                        <div className="img-wrap">
                                            <img src="/images/demo/support.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Support</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/affiliates">
                                        <div className="img-wrap">
                                            <img src="/images/demo/affiliates.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Affiliates</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Settings</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-general">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-general.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>General</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-profile">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-profile.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Profile</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-bank">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-bank.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Bank</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-security">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-security.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Settings</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-session">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-session.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Session</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-categories">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-categories.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Categories</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-currencies">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-currencies.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Currencies</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/settings-api">
                                        <div className="img-wrap">
                                            <img src="/images/demo/settings-api.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Api</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/signin">
                                        <div className="img-wrap">
                                            <img src="/images/demo/signin.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Signin</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/signup">
                                        <div className="img-wrap">
                                            <img src="/images/demo/signup.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Signup</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/reset">
                                        <div className="img-wrap">
                                            <img src="/images/demo/reset.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Reset</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/locked">
                                        <div className="img-wrap">
                                            <img src="/images/demo/locked.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Locked</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/add-bank">
                                        <div className="img-wrap">
                                            <img src="/images/demo/add-bank.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Add Bank</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/add-card">
                                        <div className="img-wrap">
                                            <img src="/images/demo/add-card.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Add Card</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/add-new-account">
                                        <div className="img-wrap">
                                            <img src="/images/demo/add-new-account.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Add New Account</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/bank-add-successful">
                                        <div className="img-wrap">
                                            <img src="/images/demo/bank-add-successful.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Bank Added Successful</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/id-front-and-back-upload">
                                        <div className="img-wrap">
                                            <img src="/images/demo/id-front-and-back-upload.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Upload ID</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/notifications">
                                        <div className="img-wrap">
                                            <img src="/images/demo/notifications.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Notifications</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/otp-phone">
                                        <div className="img-wrap">
                                            <img src="/images/demo/otp-phone.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Phone Verification</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/otp-code">
                                        <div className="img-wrap">
                                            <img src="/images/demo/otp-code.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Code Verification</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/privacy">
                                        <div className="img-wrap">
                                            <img src="/images/demo/privacy.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Privacy</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/verified-id">
                                        <div className="img-wrap">
                                            <img src="/images/demo/verified-id.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Verified ID</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/verify-email">
                                        <div className="img-wrap">
                                            <img src="/images/demo/verify-email.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Verify Email</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/verify-id">
                                        <div className="img-wrap">
                                            <img src="/images/demo/verify-id.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Verify ID</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/verifying-id">
                                        <div className="img-wrap">
                                            <img src="/images/demo/verifying-id.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>Verifying ID</h4>
                                </div>
                            </div>
                            <div className="col-xl-4 col-md-4 col-sm-6">
                                <div className="demo_img">
                                    <Link href="/404">
                                        <div className="img-wrap">
                                            <img src="/images/demo/404.png" alt className="img-fluid" />
                                        </div>
                                    </Link>
                                    <h4>404</h4>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="widgets-masonary section-padding" id="demo-widgets">
                    <div className="container">
                        <div className="row py-lg-5 justify-content-center">
                            <div className="col-xl-7">
                                <div className="section-title text-center">
                                    <span>Widgets</span>
                                    <h2>Accelerate Your Development and Launch Rapidly with Ekash</h2>
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-12">
                                <div className="masonary">
                                    <figure>
                                        <img src="/images/card/1.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/2.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/3.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/4.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/5.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/6.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/7.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/8.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/9.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/10.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/11.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/12.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/13.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/14.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/15.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/16.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/17.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/18.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/19.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/20.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/21.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/22.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/23.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/24.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/25.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/26.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/27.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/28.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/29.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/30.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/31.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/32.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/33.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/34.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/35.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/36.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/37.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/38.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/39.png" alt />
                                    </figure>
                                    <figure>
                                        <img src="/images/card/40.png" alt />
                                    </figure>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="features section-padding" id="demo-features">
                    <div className="container">
                        <div className="row py-lg-5 justify-content-center">
                            <div className="col-xl-7">
                                <div className="section-title text-center">
                                    <span>Features</span>
                                    <h2>Extraordinary Features, Endless Flexibility</h2>
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-magic-wand" />
                                    <h5>2 Theme Colors</h5>
                                    <p>We have included 6 pre-defined Theme Colors with Elegant Admin.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-moon" />
                                    <h5>Dark &amp; Light Sidebar</h5>
                                    <p>Included Dark and Light Sidebar for getting desire look and feel.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-archive" />
                                    <h5>45+ Page Templates</h5>
                                    <p>Yes, we have 1 demos &amp; 45+ Pages per demo to make it easier.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-settings-sliders" />
                                    <h5>150+ UI Components</h5>
                                    <p>Almost 150+ UI Components being given with Ekash Admin Pack.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-brands-bootstrap" />
                                    <h5>Bootstrap 5x</h5>
                                    <p>Its been made with Bootstrap 5 and full responsive layout.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-diamond" />
                                    <h5>2000+ Font Icons</h5>
                                    <p>Lots of Icon Fonts are included here in the package of Elegant Admin.
                                    </p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-laptop-mobile" />
                                    <h5>Fully Responsive</h5>
                                    <p>All the layout of Ekash Admin is Fully Responsive and widely
                                        tested.
                                    </p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-brands-sass" />
                                    <h5>SassBase CSS</h5>
                                    <p>Our Css is written Sass Base to make your life easier.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-shuffle" />
                                    <h5>Easy to Customize</h5>
                                    <p>Customization will be easy as we understand your pain.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-chart-pie" />
                                    <h5>Lots of Chart Options</h5>
                                    <p>You name it and we have it, Yes lots of variations for Charts.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rs-table" />
                                    <h5>Lots of Table Examples</h5>
                                    <p>Data Tables are initial requirement and we added them.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-refresh" />
                                    <h5>Regular Updates</h5>
                                    <p>We are constantly updating our pack with new features.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rr-book" />
                                    <h5>Detailed Documentation</h5>
                                    <p>We have made detailed documentation, so it will easy to use.</p>
                                </div>
                            </div>
                            <div className="col-sm-6 col-md-4 col-lg-3">
                                <div className="features-content">
                                    <i className="fi fi-rs-user-headset" />
                                    <h5>Dedicated Support</h5>
                                    <p>We believe in supreme support is key and we offer that.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="review" id="demo-review">
                    <div className="container">
                        <div className="row py-lg-5 justify-content-center">
                            <div className="col-xl-7">
                                <div className="section-title text-center">
                                    <span>Reviews</span>
                                    <h2>Real Developers, Real Opinions – Read What Your Peers Have to Say!</h2>
                                    {/* <p>Refreshing my inbox, waiting for your mail </p> */}
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6>TpRx_Filo</h6>
                                                        <p> Code Quality</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>To start :
                                                Great support! responsive and attentive to a problem I had.
                                                Functional and super designed site.
                                                I highly recommend !
                                                Thanks You Very Much</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6>djjaron</h6>
                                                        <p>Feature Availability</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>Great full feature UI/UX that covers all user flows and paths. The components are
                                                well organized and the stylization is cleanly coded. A+++++</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6> creativeorange3</h6>
                                                        <p> Design Quality</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>Really professional product and creator is there to help whenever you encounter
                                                problems.
                                                Amazing response time too!
                                                Definitely will work again with Prexius!</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6> mciluke123</h6>
                                                        <p>Customer Support</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>If I could give 6 stars I would. Excellent experience with this template,
                                                fantastically designed and coded. The author is super helpful and friendly. I would
                                                recommend this template and this author to a friend for sure. Thanks!</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6>Minshan Cui</h6>
                                                        <p>Features avaibility</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>The quality of design is excellent, customizability and
                                                flexibility
                                                much better than the other products available in the market. I strongly recommend
                                                the AdminMart to
                                                other buyers.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-4 col-lg-6">
                                <div className="testimonial-content">
                                    <div className="card">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between">
                                                <div className="d-flex">
                                                    <img src="/images/envato.png" alt className="w-auto me-3 rounded-circle" width={50} height={50} />
                                                    <div>
                                                        <h6>gsotirov</h6>
                                                        <p>Customer Support</p>
                                                    </div>
                                                </div>
                                                <div>
                                                    <div className="d-flex">
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                        <i className="fi fi-ss-star" />
                                                    </div>
                                                </div>
                                            </div>
                                            <p>Amazing design and even though i purchased it by mistake as i didn't see that is
                                                react, the owner immediately respond to me and provide me the desired Nextjs Template.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="customer-support section-padding" id="demo-support">
                    <div className="container">
                        <div className="row py-lg-5 justify-content-center">
                            <div className="col-xl-7">
                                <div className="section-title text-center">
                                    <span>Problem?</span>
                                    <h2>Don't Worry, I am waiting your question</h2>
                                    <p>Refreshing my inbox, waiting for your mail </p>
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-6">
                                <div className="customer-support-content">
                                    <span><i className="fi fi-brands-whatsapp" /></span>
                                    <h4>+96897425480</h4>
                                    <p>Without sleeping time, I am avaiable in Whstsapp. I recommend Whstsapp</p>
                                    <Link href="/https://api.whatsapp.com/send?phone=0096897425480">Send Message <i className="la la-angle-right" /></Link>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="customer-support-content">
                                    <span><i className="fi fi-brands-skype" /></span>
                                    <h4>sporsho9</h4>
                                    <p>Without sleeping time, I am avaiable in skype. I also recommend Skype</p>
                                    <Link href="/skype:profile_name?sporsho9">Add Skype <i className="la la-angle-right" /></Link>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="customer-support-content">
                                    <span><i className="fi fi-rr-envelope" /></span>
                                    <h4>imsaifun@gmail.com</h4>
                                    <p>When you send me email, I get notification, and quickly reply you</p>
                                    <Link href="/mailto:imsaifun@gmail.com">Send Email <i className="la la-angle-right" /></Link>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="customer-support-content">
                                    <span><i className="fi fi-rr-headset" /></span>
                                    <h4>Pre sale question</h4>
                                    <p>You have need more design or customization? Dont worry about Quality</p>
                                    <Link href="/https://docs.google.com/forms/d/e/1FAIpQLSflTWPNbUwxUvIDLWx8TlzmDOWt1PgNCX4_TZ59yok-MlzXkg/viewform">Hire
                                        Now <i className="la la-angle-right" /></Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="footer-landing">
                    <div className="container">
                        <div className="row">
                            <div className="col-xl-6">
                                <div className="copyright">
                                    <p>© Copyright
                                        <Link href="#">Ekash</Link> I All Rights Reserved
                                    </p>
                                </div>
                            </div>
                            <div className="col-xl-6">
                                <div className="footer-social">
                                    <ul>
                                        <li><Link href="#"><i className="fi fi-brands-facebook" /></Link></li>
                                        <li><Link href="#"><i className="fi fi-brands-twitter" /></Link></li>
                                        <li><Link href="#"><i className="fi fi-brands-linkedin" /></Link></li>
                                        <li><Link href="#"><i className="fi fi-brands-youtube" /></Link></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </>
    )
}
