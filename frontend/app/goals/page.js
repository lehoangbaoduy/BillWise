'use client'
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
export default function Goals() {
    return (
        <Layout breadcrumbTitle="Goals">
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-body">
                            <EmptyState icon="fi fi-rr-piggy-bank" message="No savings goals yet. Goal creation is coming soon." />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
