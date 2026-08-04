import { Menu } from '@headlessui/react'
import dynamic from 'next/dynamic'
import Link from "next/link"
import { useRouter } from "next/navigation"
import useSWR from "swr"
import { useAuth } from "@/hooks/useAuth"
import { aiInsightsApi, authApi, notificationsApi } from "@/lib/api"
import PlatformViewToggle from "@/components/elements/PlatformViewToggle"

const ThemeSwitch = dynamic(() => import('@/components/elements/ThemeSwitch'), {
    ssr: false
})

const NOTIFICATIONS_POLL_INTERVAL_MS = 60000
const NOTIFICATIONS_PREVIEW_COUNT = 5

export default function Header1({ isMobileMenu, handleMobileMenu, platformView, setPlatformView }) {
    const router = useRouter()
    const { user } = useAuth()
    const { data: notifications, mutate: mutateNotifications } = useSWR(
        user ? "/notifications" : null,
        () => notificationsApi.list(),
        { refreshInterval: NOTIFICATIONS_POLL_INTERVAL_MS }
    )
    const unacknowledged = (notifications ?? []).filter((notification) => !notification.is_acknowledged)
    const notificationCount = unacknowledged.length

    async function handleAcknowledge(event, notification) {
        event.preventDefault()
        event.stopPropagation()
        if (notification.type === "ai_insight" && notification.entity_id) {
            await aiInsightsApi.dismiss(notification.entity_id)
        } else {
            await notificationsApi.acknowledge(notification.key)
        }
        await mutateNotifications()
    }

    async function handleLogout() {
        try {
            await authApi.logout()
        } catch (error) {
            console.error("Logout request failed; session cookie may still be valid.", error)
        } finally {
            router.push("/signin")
        }
    }

    return (
        <>
            <div className="header">
                <div className="container">
                    <div className="row">
                        <div className="col-xxl-12">
                            <div className="header-content">
                                <div className="header-left">
                                    <div className="brand-logo"><Link className="mini-logo" href="/"><img src="./images/logoi.png" alt="" width={40} /></Link></div>
                                </div>
                                <div className="header-right">
                                    <ThemeSwitch />
                                    <Menu as="div" className="nav-item dropdown notification">
                                        <Menu.Button as="div" className="show">
                                            <div className="notify-bell icon-menu">
                                                <span><i className="fi fi-rs-bells" /></span>
                                                {notificationCount > 0 && (
                                                    <span className="badge-count">{notificationCount > 9 ? "9+" : notificationCount}</span>
                                                )}
                                            </div>
                                        </Menu.Button>
                                        <Menu.Items as="div" tabIndex={-1} role="menu" aria-hidden="true" className="dropdown-menu dropdown-menu-end show">
                                            <h4>Recent Notification</h4>
                                            <div className="lists">
                                                {notificationCount === 0 ? (
                                                    <p className="text-center p-3 mb-0">No new notifications</p>
                                                ) : (
                                                    unacknowledged.slice(0, NOTIFICATIONS_PREVIEW_COUNT).map((notification) => (
                                                        <div className={`item severity-${notification.severity} d-flex justify-content-between align-items-start gap-2`} key={notification.key}>
                                                            <div>
                                                                <h5>{notification.title}</h5>
                                                                <p>{notification.message}</p>
                                                            </div>
                                                            <button
                                                                type="button"
                                                                className="btn btn-sm btn-outline-secondary flex-shrink-0"
                                                                onClick={(event) => handleAcknowledge(event, notification)}
                                                            >
                                                                Acknowledge
                                                            </button>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                            <div className="more">
                                                <Link href="/notifications">More<i className="fi fi-bs-angle-right" /></Link>
                                            </div>
                                        </Menu.Items>
                                    </Menu>
                                    <Menu as="div" className="dropdown profile_log dropdown">
                                        <Menu.Button as="div">
                                            <div className="user icon-menu active"><span><i className="fi fi-rr-user" /></span></div>
                                        </Menu.Button>
                                        <Menu.Items as="div" tabIndex={-1} role="menu" aria-hidden="true" className="dropdown-menu dropdown-menu dropdown-menu-end show">
                                            <div className="user-email">
                                                <div className="user">
                                                    <span className="thumb"><i className="fi fi-rr-user" /></span>
                                                    <div className="user-info">
                                                        <h5>{user?.display_name || " "}</h5>
                                                        <span>{user?.email || " "}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="dropdown-item platform-view-row" role="none">
                                                <span className="platform-view-row-label"><i className="fi fi-rr-mobile-notch" /> Platform view</span>
                                                <PlatformViewToggle variant="menu" platformView={platformView} setPlatformView={setPlatformView} />
                                            </div>
                                            <Link className="dropdown-item" href="/profile">
                                                <span><i className="fi fi-rr-user" /></span>
                                                Profile
                                            </Link>
                                            <Link className="dropdown-item" href="/wallets">
                                                <span><i className="fi fi-rr-wallet" /></span>
                                                Wallets
                                            </Link>
                                            <button type="button" className="dropdown-item logout" onClick={handleLogout}>
                                                <span><i className="fi fi-bs-sign-out-alt" /></span>
                                                Logout
                                            </button>
                                        </Menu.Items>
                                    </Menu>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </>
    )
}
