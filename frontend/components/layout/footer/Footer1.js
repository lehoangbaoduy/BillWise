import Link from "next/link"

export default function Footer1() {
    return (
        <>
            <div className="footer">
                <div className="container">
                    <div className="row">
                        <div className="col-xl-6">
                            <div className="copyright">
                                <p>© Copyright
                                    <Link href="#">Ekash</Link> I All Rights Reserved
                                </p>
                            </div>
                        </div>
                        <div className="col-xl-6">
                            <div className="footer-social">
                                <ul>
                                    <li><Link href="#"><i className="fi fi-brands-facebook" /></Link></li>
                                    <li><Link href="#"><i className="fi fi-brands-twitter" /></Link></li>
                                    <li><Link href="#"><i className="fi fi-brands-linkedin" /></Link></li>
                                    <li><Link href="#"><i className="fi fi-brands-youtube" /></Link></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </>
    )
}
