'use client'
import useSWR from "swr"
import EmptyState from "@/components/elements/EmptyState"
import Layout from "@/components/layout/Layout"
import { aiInsightsApi, notificationsApi } from "@/lib/api"

const SEVERITY_ICON = {
    critical: "fi fi-rr-triangle-warning",
    warning: "fi fi-rr-clock",
    info: "fi fi-rr-info",
}

function NotificationRow({ notification, onAcknowledge }) {
    return (
        <div className={`item severity-${notification.severity} p-3`}>
            <div className="d-flex align-items-start justify-content-between gap-2">
                <div className="d-flex align-items-start gap-2">
                    <i className={SEVERITY_ICON[notification.severity] || "fi fi-rr-bell"} />
                    <div>
                        <h5 className="mb-1">{notification.title}</h5>
                        <p className="mb-0">{notification.message}</p>
                    </div>
                </div>
                {notification.is_acknowledged ? (
                    <span className="text-muted small flex-shrink-0">Acknowledged</span>
                ) : (
                    <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary flex-shrink-0"
                        onClick={() => onAcknowledge(notification)}
                    >
                        Acknowledge
                    </button>
                )}
            </div>
        </div>
    )
}

export default function Notifications() {
    const { data: notifications, isLoading, mutate } = useSWR("/notifications", () => notificationsApi.list())

    async function handleAcknowledge(notification) {
        if (notification.type === "ai_insight" && notification.entity_id) {
            await aiInsightsApi.dismiss(notification.entity_id)
        } else {
            await notificationsApi.acknowledge(notification.key)
        }
        await mutate()
    }

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
                                    {notifications.map((notification) => (
                                        <NotificationRow
                                            notification={notification}
                                            onAcknowledge={handleAcknowledge}
                                            key={notification.key}
                                        />
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
