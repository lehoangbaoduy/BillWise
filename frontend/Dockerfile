# Multi-stage build producing a minimal production server (next.config.js's
# `output: "standalone"` copies only each page's actual dependencies, not the
# full node_modules tree). NEXT_PUBLIC_* variables are inlined into the
# client bundle at build time, not read at container runtime — pass
# NEXT_PUBLIC_API_BASE_URL as a build arg, not a runtime env var. See
# DEPLOYMENT.md.

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN useradd --create-home --uid 1001 appuser

COPY --from=builder /app/public ./public
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static

USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
