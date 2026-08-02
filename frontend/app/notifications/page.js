'use client'
import useSWR from "swr"
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import { notificationsApi } from "@/lib/api"

const SEVERITY_ICON = {
    critical: "fi fi-rr-triangle-warning",
    warning: "fi fi-rr-clock",
    info: "fi fi-rr-info",
}

function NotificationRow({ notification }) {
    return (
        <div className={`item severity-${notification.severity} p-3`}>
            <div className="d-flex align-items-start gap-2">
                <i className={SEVERITY_ICON[notification.severity] || "fi fi-rr-bell"} />
                <div>
                    <h5 className="mb-1">{notification.title}</h5>
                    <p className="mb-0">{notification.message}</p>
                </div>
            </div>
        </div>
    )
}

export default function Notifications() {
    const { data: notifications, isLoading } = useSWR("/notifications", () => notificationsApi.list())

    return (
        <Layout breadcrumbTitle="Notifications">
            <div className="row">
                <div className="col-xl-12">
                    <div className="card">
                        <div className="card-header">
                            <h4 className="card-title">Recent Notification</h4>
                        </div>
                        <div className="card-body p-0">
                            {isLoading ? null : !notifications || notifications.length === 0 ? (
                                <EmptyState icon="fi fi-rr-bell" message="No notifications yet. You're all caught up." className="py-5" />
                            ) : (
                                <div className="lists">
                                    {notifications.map((notification, index) => (
                                        <NotificationRow notification={notification} key={`${notification.type}-${index}`} />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    )
}
