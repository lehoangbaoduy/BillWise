
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function SettingsSession() {

    return (
        <>
            <Layout breadcrumbTitle="Session">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu/>
                        <div className="row">
                            <div className="col-xxl-12">
                                <h4 className="card-title mb-3">Third-Party Applications </h4>
                                <div className="card">
                                    <div className="card-body">
                                        <div className="d-flex align-items-center"><span className="me-3 icon-circle bg-warning text-white"><i className="fi fi-rs-messages-question" /></span>
                                            <div>
                                                <h5 className="mb-0">You haven&apos;t authorized any applications yet.</h5>
                                                <p>After connecting an application with your account, you can manage or
                                                    revoke its
                                                    access here.</p><Link href="#" className="btn btn-primary">Authorize now</Link>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <h4 className="card-title mb-3">Web Sessions</h4>
                                <div className="card">
                                    <div className="card-body">
                                        <div className="table-responsive table-icon">
                                            <table className="table">
                                                <thead>
                                                    <tr>
                                                        <th>Signed In</th>
                                                        <th>Browser</th>
                                                        <th>IP Address</th>
                                                        <th>Near</th>
                                                        <th>Current</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>1 day ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td>250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>1 day ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td>250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>1 day ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td>250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                <h4 className="card-title mb-3">Confirmed Devices</h4>
                                <div className="card">
                                    <div className="card-body">
                                        <div className="table-responsive">
                                            <table className="table">
                                                <thead>
                                                    <tr>
                                                        <th>Confirmed</th>
                                                        <th>Browser</th>
                                                        <th>IP Address</th>
                                                        <th>Near</th>
                                                        <th>Current</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>1 day ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td> 250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>8 days ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td> 250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>15 days ago</td>
                                                        <td>Chrome (Windows)</td>
                                                        <td> 250.364.239.254</td>
                                                        <td>Bangladesh, Dhaka</td>
                                                        <td><span><i className="fi fi-bs-check text-success me-1" /></span><span><i className="fi fi-sr-cross-small text-danger" /></span></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                <h4 className="card-title mb-3">Account Activity</h4>
                                <div className="card">
                                    <div className="card-body">
                                        <div className="table-responsive">
                                            <table className="table">
                                                <thead>
                                                    <tr>
                                                        <th>Action</th>
                                                        <th>Source</th>
                                                        <th>IP Address</th>
                                                        <th>Location</th>
                                                        <th>When</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>api</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">about 1 hour ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>api</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">about 2 hours ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>second factor failure</td>
                                                        <td>api</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">about 2 hours ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>device confirmation completed</td>
                                                        <td>web</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">1 day ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signin</td>
                                                        <td>web</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">1 day ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>web</td>
                                                        <td>157.119.239.254</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">1 day ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signout</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signin</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signout</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signout</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>device confirmation completed</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signin</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">8 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signout</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signin</td>
                                                        <td>web</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signout</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>web</td>
                                                        <td>23.106.249.39</td>
                                                        <td>Singapore</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>verified second factor</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>xs verified</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>xs added</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                    <tr>
                                                        <td>signin</td>
                                                        <td>api</td>
                                                        <td>157.119.239.214</td>
                                                        <td>Bangladesh</td>
                                                        <td><Link href="#">15 days ago</Link></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                <h4 className="card-title mb-3">Close Account</h4>
                                <div className="card transparent">
                                    <div className="card-body">
                                        <p>Withdraw funds and close your account - <span className="text-danger">this
                                            cannot be
                                            undone</span></p><Link href="#" className="btn btn-danger">Close Account</Link>
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