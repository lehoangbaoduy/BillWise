
'use client'
import { useEffect, useState } from "react"
import Breadcrumb from './Breadcrumb'
import PageHead from './PageHead'
import Sidebar from "./Sidebar"
import Footer1 from './footer/Footer1'
import Header1 from "./header/Header1"

export default function Layout({ headerStyle, footerStyle, headTitle, breadcrumbTitle, children }) {
    const [scroll, setScroll] = useState(0)
    // Moblile Menu
    const [isMobileMenu, setMobileMenu] = useState(false)
    const handleMobileMenu = () => setMobileMenu(!isMobileMenu)

    useEffect(() => {
        const WOW = require('wowjs')
        window.wow = new WOW.WOW({
            live: false
        })
        window.wow.init()

        document.addEventListener("scroll", () => {
            const scrollCheck = window.scrollY > 100
            if (scrollCheck !== scroll) {
                setScroll(scrollCheck)
            }
        })
    }, [])
    return (
        <>
            <PageHead headTitle={headTitle} />
            <div id="main-wrapper">
                <Header1 scroll={scroll} isMobileMenu={isMobileMenu} handleMobileMenu={handleMobileMenu} />
                <Sidebar />

                <div className="content-body">
                    <div className="container">
                        {breadcrumbTitle && <Breadcrumb breadcrumbTitle={breadcrumbTitle} />}

                        {children}
                    </div>
                </div>
                < Footer1 />
            </div>
        </>
    )
}
