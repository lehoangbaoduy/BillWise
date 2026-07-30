
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import SettingsMenu from "@/components/layout/SettingsMenu"

export default function SettingsGeneral() {
    return (
        <Layout breadcrumbTitle="General">
            <div className="row">
                <div className="col-xxl-12 col-xl-12">
                    <SettingsMenu />
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Preferences</h4>
                        </div>
                        <div className="card-body">
                            <EmptyState icon="fi fi-rr-settings-sliders" message="Preferences aren't configurable yet." />
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
