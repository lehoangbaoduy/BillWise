import Link from "next/link"

export default function Breadcrumb({ breadcrumbTitle }) {
    return (
        <>
            <div className="row">
                <div className="col-12">
                    <div className="page-title">
                        <div className="row align-items-center justify-content-between">
                            <div className="col-xl-4">
                                <div className="page-title-content">
                                    <h3>{breadcrumbTitle}</h3>
                                    <p className="mb-2">Welcome Ekash Finance Management</p>
                                </div>
                            </div>
                            <div className="col-auto">
                                <div className="breadcrumbs"><Link href="#">Home </Link>
                                    <span><i className="fi fi-rr-angle-small-right" /></span>
                                    <Link href="#">{breadcrumbTitle}</Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </>
    )
}
