
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"
import Link from "next/link"
export default function SettingsApi() {

    return (
        <>
            <Layout breadcrumbTitle="Api">
                <div className="row">
                    <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu/>
                        <div className="row">
                            <div className="col-xxl-12">
                                <h4 className="card-title mb-3">Create API Key</h4>
                                <div className="card">
                                    <div className="card-body">
                                        <form action="#">
                                            <div className="row">
                                                <div className="col-xxl-6 col-xl-6 col-lg-6 mb-3"><label className="form-label">Generate New
                                                    Key</label><input name="generateKey" type="text" className="form-control" /></div>
                                                <div className="col-xxl-6 col-xl-6 col-lg-6 mb-3"><label className="form-label">Confirm
                                                    Passphrase</label><input name="confirmKey" type="text" className="form-control" /></div>
                                            </div>
                                            <div className="mt-3"><button type="submit" className="btn btn-primary mr-2">Save</button></div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            <div className="col-xl-12">
                                <h4 className="card-title mb-3">Your API Keys</h4>
                                <div className="card">
                                    <div className="card-body">
                                        <div className="table-responsive api-table">
                                            <table className="table">
                                                <thead>
                                                    <tr>
                                                        <th>Key</th>
                                                        <th>Status</th>
                                                        <th>Action</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>69e387f1-31c3-45ad-9c68-5a51e5e78b43</td>
                                                        <td>
                                                            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" defaultChecked /></div>
                                                        </td>
                                                        <td><span><i className="fi fi-rs-trash" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>69e387f1-31c3-45ad-9c68-5a51e5e78b43</td>
                                                        <td>
                                                            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" /></div>
                                                        </td>
                                                        <td><span><i className="fi fi-rs-trash" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>69e387f1-31c3-45ad-9c68-5a51e5e78b43</td>
                                                        <td>
                                                            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" /></div>
                                                        </td>
                                                        <td><span><i className="fi fi-rs-trash" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>69e387f1-31c3-45ad-9c68-5a51e5e78b43</td>
                                                        <td>
                                                            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" /></div>
                                                        </td>
                                                        <td><span><i className="fi fi-rs-trash" /></span></td>
                                                    </tr>
                                                    <tr>
                                                        <td>69e387f1-31c3-45ad-9c68-5a51e5e78b43</td>
                                                        <td>
                                                            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" /></div>
                                                        </td>
                                                        <td><span><i className="fi fi-rs-trash" /></span></td>
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