import { Menu } from '@headlessui/react'
import dynamic from 'next/dynamic'
import Link from "next/link"
const ThemeSwitch = dynamic(() => import('@/components/elements/ThemeSwitch'), {
    ssr: false
})
export default function Header1({ isMobileMenu, handleMobileMenu }) {
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
                                                <input type="text" className="form-control" placeholder="Search Here" />
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
                                                <Link href="#">
                                                    <div className="d-flex align-items-center">
                                                        <span className="me-3 icon success"><i className="fi fi-bs-check" /></span>
                                                        <div>
                                                            <p>Account created successfully</p>
                                                            <span>2024-11-04 12:00:23</span>
                                                        </div>
                                                    </div>
                                                </Link>
                                                <Link href="#">
                                                    <div className="d-flex align-items-center">
                                                        <span className="me-3 icon fail"><i className="fi fi-sr-cross-small" /></span>
                                                        <div>
                                                            <p>2FA verification failed</p>
                                                            <span>2024-11-04 12:00:23</span>
                                                        </div>
                                                    </div>
                                                </Link>
                                                <Link href="#">
                                                    <div className="d-flex align-items-center">
                                                        <span className="me-3 icon success"><i className="fi fi-bs-check" /></span>
                                                        <div>
                                                            <p>Device confirmation completed</p>
                                                            <span>2024-11-04 12:00:23</span>
                                                        </div>
                                                    </div>
                                                </Link>
                                                <Link href="#">
                                                    <div className="d-flex align-items-center">
                                                        <span className="me-3 icon pending"><i className="fi fi-rr-triangle-warning" /></span>
                                                        <div>
                                                            <p>Phone verification pending</p>
                                                            <span>2024-11-04 12:00:23</span>
                                                        </div>
                                                    </div>
                                                </Link>
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
                                                    <span className="thumb"><img className="rounded-full" src="./images/avatar/3.jpg" alt="" /></span>
                                                    <div className="user-info">
                                                        <h5>Hafsa Humaira</h5>
                                                        <span>hello@email.com</span>
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
                                            <Link className="dropdown-item logout" href="/signin">
                                                <span><i className="fi fi-bs-sign-out-alt" /></span>
                                                Logout
                                            </Link>
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
