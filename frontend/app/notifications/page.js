
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
export default function Notifications() {

    return (
        <Layout breadcrumbTitle="Notifications">
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Recent Notification </h4>
                        </div>
                        <div className="card-body">
                            <EmptyState icon="fi fi-rr-bell" message="No notifications yet." />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
