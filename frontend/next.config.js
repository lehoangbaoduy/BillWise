// PRD §22.2 / production security posture. Content-Security-Policy is set
// separately in middleware.js (needs a per-request nonce, which can't be
// generated from this static config).
const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
]

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produces a minimal, self-contained server bundle (only the deps each
  // page actually needs) instead of requiring the full node_modules tree in
  // the production image — see frontend/Dockerfile's runtime stage.
  output: "standalone",
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }]
  },
}

module.exports = nextConfig
