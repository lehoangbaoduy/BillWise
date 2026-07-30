
import Layout from "@/components/layout/Layout"
import Link from "next/link"
export default function Privacy() {

    return (
        <>
            <Layout breadcrumbTitle="Privacy">
                <div className="row">
                    <div className="col-xl-12">
                        <div className="card">
                            <div className="card-header">
                                <h4 className="card-title">Privacy and Poliicy </h4>
                            </div>
                            <div className="card-body">
                                <div className="privacy-content">
                                    <p>Ekash is an instant personal finance management that allows you to exchange cash
                                        fast and buy it with a bank card. The service provides the best cash-to-cash
                                        rates and supports over 140 currencies available for exchange
                                    </p>
                                </div>
                                <div className="privacy-content">
                                    <h5>How does Ekash work? </h5>
                                    <p>
                                        Ekash trading algorithm is integrated into the largest personal finance management
                                        platforms, including Binance, Poloniex, Bittrex, etc. In the span of milliseconds,
                                        Ekash makes bids and asks on the platforms, then selects and suggests the best
                                        available rate and displays the estimated rate on our site. The rates remain
                                        approximate until the transaction is actually made on the blockchain, which is why
                                        the exchange rate at the time of a transaction may differ slightly from the
                                        estimated rate that you see when you begin a transaction. To learn more about the
                                        process, see this <Link href="#">article</Link>
                                    </p>
                                </div>
                                <div className="privacy-content">
                                    <h5>Why should I trust you? </h5>
                                    <p>Ekash is one of the most prominent instant personal finance managements that has
                                        gained the trust of more than 2M users from all over the world. The service provides
                                        safe and fast transactions without revealing users identities. We provide the best
                                        possible rates by comparing a wide range of reliable trading platforms and work with
                                        a list of 140+ currencies that is constantly increasing.</p>
                                    <ul>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>No deposit storage. </p>
                                        </li>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>Instant exchange. </p>
                                        </li>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>Each account is protected with 2-factor authentication and an HTTPS protocol.
                                            </p>
                                        </li>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>More than 2 million satisfied users.</p>
                                        </li>
                                    </ul>
                                </div>
                                <div className="privacy-content">
                                    <h5>Does Ekash fix rates? </h5>
                                    <p>Ekash mobile app does! Mobile app users will no longer be affected by the risks
                                        associated with cash market fluctuations. Soon, the fixed-rate exchanges will also
                                        be implemented on the web version. To lock the current exchange rate, the user needs
                                        to click on the lock icon, which will result in them getting the exact same amount
                                        of cash as is displayed on the screen. The rate is fixed for 15 minutes, which
                                        should be more than enough to carry out the exchange.
                                    </p>
                                    <p> Alternatively, Ekash offers our lowest fee of 0.25% for all cash-to-cash
                                        exchanges made at a floating rate.</p>
                                </div>
                                <div className="privacy-content">
                                    <h5>No warranties : </h5>
                                    <p>Ekash is provided “as is” without any representations or warranties. Ekash.com
                                        makes no representations or warranties in relation to this website or the
                                        information and materials provided on this website.</p>
                                    <p>Ekash.com does not warrant that:</p>
                                    <ul>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>The website will be constantly available, or available at all moving forward.
                                            </p>
                                        </li>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>The information on this website is complete, true, or non-misleading.</p>
                                        </li>
                                    </ul>
                                </div>
                                <div className="privacy-content">
                                    <h5>Privacy : </h5>
                                    <p>For details about our privacy policy, please refer to the privacy policy section.</p>
                                </div>
                                <div className="privacy-content">
                                    <h5>Unenforceable provisions : </h5>
                                    <p>If any provision of this website disclaimer is, or is found to be, unenforceable
                                        under applicable law, that will not affect the enforceability of the other
                                        provisions of this website disclaimer.</p>
                                </div>
                                <div className="privacy-content">
                                    <h5>Links : </h5>
                                    <p>Responsibility for the content of external links (to web pages of third parties) lies
                                        solely with the operators of the linked pages.</p>
                                </div>
                                <div className="privacy-content">
                                    <h5>Modifications: </h5>
                                    <p>Ekash.com may revise these terms of use for its website at any time without notice.
                                        By using this web site you are agreeing to be bound by the then current version of
                                        these terms of service.</p>
                                </div>
                                <div className="privacy-content">
                                    <h5>Breaches of these terms and conditions: </h5>
                                    <ul>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>Ekash.com reserves the rights under these terms and conditions to take
                                                action if you breach these terms and conditions in any way. </p>
                                        </li>
                                        <li>
                                            <i className="fi fi-ss-circle" />
                                            <p>Ekash.com may take such action as seems appropriate to deal with the
                                                breach, including suspending your access to the website, suspending your
                                                earnings made trough Ekash.com,prohibiting you from accessing the
                                                website, or bringing court proceedings against you.</p>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </Layout>
        </>
    )
}