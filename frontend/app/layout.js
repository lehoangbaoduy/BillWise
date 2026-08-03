import { headers } from 'next/headers'
import { Rubik } from 'next/font/google'
import 'react-perfect-scrollbar/dist/css/styles.css'
import "/public/css/style.css"
import "/public/css/notifications.css"

const rubik = Rubik({
    weight: ['400', '500', '700'],
    subsets: ['latin'],
    display: 'swap',
})

export const metadata = {
    title: 'BillWise',
    description: 'Personal expense tracking for BillWise households',
}



export default function RootLayout({ children }) {
    // DO NOT REMOVE, even though the return value is unused: reading the
    // per-request nonce here (set by middleware.js) is what makes Next.js
    // attach it to its own injected script/hydration tags — the CSP response
    // header alone isn't enough, and script-src silently blocks every page
    // without this call. Verified empirically (Playwright): omitting it
    // reintroduces 17 CSP violations and a fully broken app. This also opts
    // every page into dynamic (per-request) rendering instead of static
    // prerendering, since the nonce genuinely differs per request; an
    // accepted trade-off for a behind-auth app where CDN-cached static pages
    // aren't the priority.
    headers().get('x-nonce')

    return (
        <html lang="en">
            <link rel="icon" href="/images/favicon.png" sizes="16" />
            <body className={rubik.className}>
                {children}
            </body>
        </html>
    )
}
