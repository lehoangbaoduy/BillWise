'use client'
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
export default function Budgets() {
    return (
        <Layout breadcrumbTitle="Budgets">
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-body">
                            <EmptyState icon="fi fi-rr-wallet" message="No budgets set yet. Budget creation is coming soon." />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
