import { NextResponse } from "next/server"

// Nonce-based CSP (see ~/.claude/rules/ecc/web/security.md) rather than a
// static 'unsafe-inline' policy. Built from an actual audit of this app's
// resources, not copied from a template:
//   - No third-party scripts, CDNs, or trackers anywhere in the codebase.
//   - next/font/google (app/layout.js) self-hosts the font at build time —
//     no runtime request to Google, so no fonts.googleapis.com/gstatic.com
//     exception is needed.
//   - No blob:/data: image usage (no client-side file preview); no data:
//     URIs in the vendored CSS. img-src still allows `data:` as a narrow,
//     script-incapable fallback rather than assuming the audit is exhaustive.
//   - style="" attributes ARE used (inline `style={{...}}` props compile to
//     them), so style-src needs 'unsafe-inline' — CSS injection can't
//     execute script, which is the threat this header is primarily for.
//   - connect-src must explicitly allow the backend API origin, since it's
//     typically a different origin than the frontend.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
const IS_DEV = process.env.NODE_ENV !== "production"

function buildCsp(nonce) {
  const directives = [
    `default-src 'self'`,
    // 'unsafe-eval' is required for Next.js dev-mode HMR/refresh only.
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${IS_DEV ? " 'unsafe-eval'" : ""}`,
    `style-src 'self' 'unsafe-inline'`,
    `img-src 'self' data:`,
    `font-src 'self'`,
    `connect-src 'self' ${API_BASE_URL}`,
    `frame-src 'none'`,
    `frame-ancestors 'none'`,
    `object-src 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
  ]
  return directives.join("; ")
}

export function middleware(request) {
  const nonce = Buffer.from(crypto.randomUUID()).toString("base64")
  const csp = buildCsp(nonce)

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set("x-nonce", nonce)
  requestHeaders.set("Content-Security-Policy", csp)

  const response = NextResponse.next({ request: { headers: requestHeaders } })
  response.headers.set("Content-Security-Policy", csp)
  return response
}

export const config = {
  matcher: [
    // Skip static assets and image optimization requests — CSP is only
    // meaningful on documents/API routes that return HTML or drive script execution.
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
}
