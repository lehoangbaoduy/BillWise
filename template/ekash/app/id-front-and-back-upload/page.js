
import Layout from "@/components/layout/Layout"
export default function IdUpload() {

    return (
        <>
            <Layout breadcrumbTitle="Id Upload">
                <div className="verification section-padding">
                    <div className="container h-100">
                        <div className="row justify-content-center h-100 align-items-center">
                            <div className="col-xl-5 col-md-6">
                                <div className="card">
                                    <div className="card-body">
                                        <form action="verifying-id" className="identity-upload">
                                            <div className="identity-content">
                                                <h4>Upload your ID card</h4>
                                                <span>(Driving License or Government ID card)</span>
                                                <p>Uploading your ID helps as ensure the safety and security of your founds
                                                </p>
                                            </div>
                                            <div className="mb-4">
                                                <div className="d-flex justify-content-between mb-2">
                                                    <label className="form-label">Upload Front ID </label>
                                                    <span className="float-right">Maximum file size is 2mb</span>
                                                </div>
                                                <div className="file-upload-wrapper" data-text="front.jpg">
                                                    <input name="file-upload-field" type="file" className="file-upload-field" />
                                                </div>
                                            </div>
                                            <div className="mb-3">
                                                <div className="d-flex justify-content-between mb-2">
                                                    <label className="form-label">Upload Back ID </label>
                                                    <span className="float-right">Maximum file size is 2mb</span>
                                                </div>
                                                <div className="file-upload-wrapper" data-text="back.jpg">
                                                    <input name="file-upload-field" type="file" className="file-upload-field" />
                                                </div>
                                            </div>
                                            <div className="mt-5">
                                                <button type="submit" className="btn btn-success w-100">Submit</button>
                                            </div>
                                        </form>
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