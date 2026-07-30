
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
export default function SettingsCurrencies() {

    return (
        <>
            <Layout breadcrumbTitle="Currencies">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                        <SettingsMenu />
                        <div className="row">
                            <div className="col-xl-3 col-sm-6">
                                <div className="stat-widget-2 d-flex align-items-center">
                                    <div className="widget-icon me-3 bg-primary"><span><i className="fi fi-br-dollar" /></span></div>
                                    <div className="widget-content">
                                        <h3>USD</h3>
                                        <p>1 USD = 0.92 Euro</p>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="stat-widget-2 d-flex align-items-center">
                                    <div className="widget-icon me-3 bg-success"><span><i className="fi fi-br-euro" /></span></div>
                                    <div className="widget-content">
                                        <h3>Euro</h3>
                                        <p>1 USD = 0.92 Euro</p>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="stat-widget-2 d-flex align-items-center">
                                    <div className="widget-icon me-3 bg-warning"><span><i className="fi fi-br-pound" /></span>
                                    </div>
                                    <div className="widget-content">
                                        <h3>Pound</h3>
                                        <p>1 USD = 0.92 Euro</p>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-3 col-sm-6">
                                <div className="stat-widget-2 d-flex align-items-center">
                                    <div className="widget-icon me-3 bg-danger"><span><i className="fi fi-br-yen" /></span></div>
                                    <div className="widget-content">
                                        <h3>Yen</h3>
                                        <p>1 USD = 0.92 Euro</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-xl-5 col-lg-12 col-md-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Currency Exchange</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="buy-sell-widget">
                                            <form method="post" name="myform" className="currency_validate">
                                                <div className="mb-3">
                                                    <label className="form-label mb-3">Currency</label>
                                                    <div className="input-group mb-3">
                                                        <div className="input-group-prepend">
                                                            <label className="input-group-text">
                                                                <i className="fi fi-rr-usd-circle" />
                                                            </label>
                                                        </div>
                                                        <select name="currency" className="form-select">
                                                            <option value>Select</option>
                                                            <option value="usd">USD</option>
                                                            <option value="euro">Euro</option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div className="mb-3">
                                                    <label className="form-label mb-3">Payment Method</label>
                                                    <div className="input-group mb-3">
                                                        <div className="input-group-prepend">
                                                            <label className="input-group-text"><i className="fi fi-rr-credit-card" />
                                                            </label>
                                                        </div>
                                                        <select className="form-select" name="method">
                                                            <option value>Select</option>
                                                            <option value="bank">Bank of America ********45845
                                                            </option>
                                                            <option value="master">Master Card ***********5458
                                                            </option>
                                                        </select>
                                                    </div>
                                                </div>
                                                <div className="mb-3">
                                                    <label className="form-label mb-3">Enter your amount</label>
                                                    <div className="input-group">
                                                        <input type="text" name="currency_amount" className="form-control" placeholder="0.0214 BTC" />
                                                        <input type="text" name="usd_amount" className="form-control" placeholder="125.00 USD" />
                                                    </div>
                                                    <div className="d-flex justify-content-between mt-3">
                                                        <p className="mb-0">Monthly Limit</p>
                                                        <h6 className="mb-0">$49750 remaining</h6>
                                                    </div>
                                                </div>
                                                <button type="submit" name="submit" className="btn btn-success btn-block">Exchange
                                                    Now</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-7 col-lg-12 col-md-12">
                                <div className="card">
                                    <div className="card-header">
                                        <h4 className="card-title">Exchange Details</h4>
                                    </div>
                                    <div className="card-body">
                                        <div className="table-responsive">
                                            <table className="table">
                                                <tbody>
                                                    <tr>
                                                        <td><span className="text-primary">Exchange Amount</span></td>
                                                        <td><span className="text-primary">75 USD </span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>Payment Method</td>
                                                        <td>Bank of America Bank ***********5245</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Exchange Rate</td>
                                                        <td>1 USD = 0.92 Euro</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Fee</td>
                                                        <td>$0.75 USD</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Total</td>
                                                        <td>$68.00 Euro</td>
                                                    </tr>
                                                    <tr>
                                                        <td>Vat</td>
                                                        <td>
                                                            <div className="text-danger">$0.25 Euro</div>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td> Sub Total</td>
                                                        <td> $69.00 Euro</td>
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

            </Layout>
        </>
    )
}