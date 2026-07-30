import { Menu } from '@headlessui/react'
import dynamic from 'next/dynamic'
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/useAuth"
import { authApi } from "@/lib/api"
const ThemeSwitch = dynamic(() => import('@/components/elements/ThemeSwitch'), {
    ssr: false
})
export default function Header1({ isMobileMenu, handleMobileMenu }) {
    const router = useRouter()
    const { user } = useAuth()

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
                                    <div className="search">
                                        <form action="#">
                                            <div className="input-group">
                                                <input type="text" className="form-control" placeholder="Search Here" aria-label="Search" />
                                                <span className="input-group-text"><i className="fi fi-br-search" /></span>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                                <div className="header-right">
                                    <ThemeSwitch />
                                    <Menu as="div" className="nav-item dropdown notification">
                                        <Menu.Button as="div" className="show">
                                            <div className="notify-bell icon-menu">
                                                <span><i className="fi fi-rs-bells" /></span>
                                            </div>
                                        </Menu.Button>
                                        <Menu.Items as="div" tabIndex={-1} role="menu" aria-hidden="true" className="dropdown-menu dropdown-menu-end show">
                                            <h4>Recent Notification</h4>
                                            <div className="lists">
                                                <p className="text-center p-3 mb-0">No new notifications</p>
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
                                            <Link className="dropdown-item" href="/profile">
                                                <span><i className="fi fi-rr-user" /></span>
                                                Profile
                                            </Link>
                                            <Link className="dropdown-item" href="/wallets">
                                                <span><i className="fi fi-rr-wallet" /></span>
                                                Wallets
                                            </Link>
                                            <Link className="dropdown-item" href="/settings">
                                                <span><i className="fi fi-rr-settings" /></span>
                                                Settings
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
