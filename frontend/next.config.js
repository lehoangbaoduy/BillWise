// PRD §22.2 / production security posture. No CSP here yet — a CSP is
// deliberately deferred rather than shipped hastily: getting it wrong (e.g.
// blocking Next.js's own inline bootstrap script) breaks the app outright,
// and it needs to be built against a real audit of every external resource
// this app loads, not guessed. Track that as a separate follow-up.
const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
]

/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }]
  },
}

module.exports = nextConfig
