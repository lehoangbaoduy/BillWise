# Deploying BillWise

This covers two paths:

- **Path A — Self-hosted** (a VPS, Oracle Cloud's Always Free tier, any bare Docker host): uses `docker-compose.prod.yml`, which also runs a Caddy reverse proxy (automatic TLS) and a cron container for the account hard-delete sweep. You manage everything yourself; it's the lowest-cost option.
- **Path B — Managed platforms** (Vercel + Render + Neon, or Railway): each platform builds `backend/Dockerfile` / `frontend/Dockerfile` directly. Less to manage, but TLS, cron, and Postgres are each a separate platform feature you configure instead of code you run.

Do the **manual pre-deployment steps** below regardless of which path you choose — they're not automatable and skipping them is the difference between "deployed" and "deployed safely."

---

## 1. Manual pre-deployment steps (do these first, every deployment)

These cannot be fixed in code — they're per-deployment values only you can set.

### 1.1 Generate a real `SECRET_KEY`

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Every session token is forged-signable by anyone who has this value — and the checked-in placeholder in `backend/.env.example` is public (it's in this repo). The app logs a startup warning if it ever detects that placeholder is still in use; treat that warning as a hard stop, not a nice-to-know.

Store the generated value as `SECRET_KEY` in your backend's environment (`backend/.env` for Path A, your platform's secret/env var UI for Path B). **Never commit it.**

### 1.2 Decide your domain(s)

- Path A needs **two subdomains** pointing at your server's IP (e.g. `app.example.com` for the frontend, `api.example.com` for the backend) — Caddy issues a separate TLS cert per domain automatically. Add both as `A` records in your DNS provider before starting Caddy, or cert issuance will fail.
- Path B: each platform gives you a domain (or lets you attach your own).

### 1.3 Get an Anthropic API key (optional)

Only needed for receipt OCR (PRD M5). Without it, `POST /ocr/receipt` returns 503 and the frontend falls back to manual transaction entry — the rest of the app works fine. Get one at https://console.anthropic.com/ if you want OCR live.

### 1.4 Generate a Postgres password

Any strong random string. Used identically in Path A's root `.env` and Path B's managed-Postgres provisioning step.

---

## 2. Path A: Self-hosted with Docker Compose + Caddy

### 2.1 Server prerequisites

- A Linux host with Docker and the Docker Compose plugin installed, reachable on ports 80 and 443.
- DNS for both subdomains (§1.2) already pointing at the server's IP — verify with `dig app.example.com` / `dig api.example.com` before continuing.

### 2.2 Clone and configure

```bash
git clone <your-repo-url> billwise && cd billwise
```

Create the **project-root** `.env` (read by `docker-compose.prod.yml` for variable substitution):

```bash
cat > .env <<'EOF'
POSTGRES_PASSWORD=<from step 1.4>
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
FRONTEND_DOMAIN=app.example.com
BACKEND_DOMAIN=api.example.com
CADDY_EMAIL=you@example.com
EOF
```

`NEXT_PUBLIC_API_BASE_URL` must match `BACKEND_DOMAIN` with `https://` — this gets baked into the frontend's client-side JS at build time (see §5.2), so it can't be a placeholder.

Create `backend/.env` (read by the backend and cron containers — **do not** put `DATABASE_URL` here, it's derived automatically from `POSTGRES_PASSWORD` above):

```bash
cat > backend/.env <<'EOF'
SECRET_KEY=<from step 1.1>
COOKIE_SECURE=true
FRONTEND_BASE_URL=https://app.example.com
ANTHROPIC_API_KEY=<from step 1.3, optional>
EOF
```

### 2.3 Build and start

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This builds both images, starts Postgres, runs `alembic upgrade head` automatically (via `backend/entrypoint.sh`) before the backend starts serving, starts the cron container (first run 30s after boot, then every 24h), and starts Caddy — which will request Let's Encrypt certificates for both domains on first start. Watch it happen:

```bash
docker compose -f docker-compose.prod.yml logs -f caddy
```

Look for `certificate obtained successfully` for both domains. If it fails, it's almost always DNS not yet propagated — recheck `dig`, wait, and Caddy will retry automatically (no restart needed).

### 2.4 Verify

```bash
curl -sI https://api.example.com/health   # expect: {"status":"ok"}
curl -sI https://app.example.com/signin   # expect: 200, and a content-security-policy header
```

Then open `https://app.example.com` in a browser and confirm you can register/sign in.

### 2.5 Updating a live deployment

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Migrations re-run automatically on the backend/cron containers' next start (idempotent — a no-op if already current).

---

## 3. Path B: Managed platforms (recommended for lowest cost / least ops)

**Vercel (frontend) + Render (backend) + Neon (Postgres)** — all have genuinely free tiers with no payment method required. (Fly.io was the original recommendation here, but as of this writing it requires a card on file before provisioning *any* machine, even within its free monthly allowance — a real blocker if you want zero-card hosting. Render's free web-service tier does cold-start after ~15 minutes of inactivity, so the first request after idle takes 30-50s; for a personal/household app that's a minor UX cost, not a blocker.)

### 3.1 Database — Neon

1. Create a project at https://neon.tech (free tier).
2. Copy the connection string it gives you and convert it to this app's driver format:
   `postgresql+psycopg://<user>:<password>@<host>/<db>?sslmode=require`
   (Neon gives you a `postgresql://` string — just add `+psycopg` after `postgresql`.)
3. Keep this — it's your `DATABASE_URL`.

### 3.2 Backend — Render

1. Push this repo to GitHub (Render deploys from a connected repo — it doesn't take a local CLI push).
2. In the Render dashboard: **New → Web Service**, connect the repo.
3. **Root Directory**: `backend`. Render auto-detects `backend/Dockerfile` and uses it directly — no extra config needed there.
4. **Instance Type**: Free.
5. Under **Environment**, add:
   ```
   DATABASE_URL=postgresql+psycopg://...from Neon...
   SECRET_KEY=<generate per §1.1>
   COOKIE_SECURE=true
   FRONTEND_BASE_URL=https://your-app.vercel.app
   ANTHROPIC_API_KEY=...   # optional
   ```
6. Deploy. Migrations run automatically — `backend/entrypoint.sh` calls `alembic upgrade head` before uvicorn starts on every boot, so there's no separate "release command" step to configure.
7. Render gives you a URL like `https://billwise-backend.onrender.com` with TLS already handled.

**Cron on Render**: Render's Cron Jobs product is not part of its free plan. Since the account hard-delete script (`scripts/hard_delete_expired_accounts.py`) only needs `DATABASE_URL` and the repo's code — not anything running *inside* the Render container specifically — the genuinely free option is a **GitHub Actions scheduled workflow** that checks out the repo and runs the script directly against your Neon database. This repo includes `.github/workflows/hard-delete-expired-accounts.yml` for exactly this. To enable it:

1. In your GitHub repo settings → **Secrets and variables → Actions**, add:
   - `DATABASE_URL` — the same Neon connection string as above
   - `SECRET_KEY` — the same value as set on Render (the script imports app config, which requires this field to be present, even though the script itself doesn't use it)
2. That's it — it runs daily on GitHub's schedule automatically. Trigger it manually anytime from the Actions tab (`workflow_dispatch`) to verify it works before waiting for the schedule.

If you're on a platform that *does* offer free cron (or you're on Path A), you don't need this workflow — disable it or ignore it.

### 3.3 Frontend — Vercel

```bash
cd frontend
npx vercel
```

In the Vercel dashboard, set the environment variable:

```
NEXT_PUBLIC_API_BASE_URL=https://billwise-backend.onrender.com
```

Vercel rebuilds the frontend when you change this (remember: it's baked in at build time, see §5.2). Vercel handles TLS and the production Next.js build automatically — it does not use `frontend/Dockerfile` at all (that Dockerfile matters for Path A / other Docker-based hosts, not Vercel).

Set `FRONTEND_BASE_URL` back on the **backend** (Render environment variable) to your real Vercel URL once you have it, so CORS allows it.

### 3.4 Alternative: Railway (single provider, simplest wiring)

If you'd rather not coordinate three separate providers: Railway hosts backend + frontend + Postgres together from the same Dockerfiles, has a built-in Cron Jobs product for the hard-delete script, and TLS is automatic. No longer has an unlimited free tier, but the usage-based hobby pricing is low for an app this size. Push the repo, add a Postgres plugin, create two services from `backend/` and `frontend/` (Railway auto-detects each Dockerfile), and set the same environment variables as above through its dashboard.

---

## 4. Environment variable reference

| Variable | Where | Required | Notes |
|---|---|---|---|
| `DATABASE_URL` | backend | yes | `postgresql+psycopg://user:pass@host:5432/db`. Path A derives this automatically from `POSTGRES_PASSWORD` — don't set it in `backend/.env` there. |
| `SECRET_KEY` | backend | yes | Generate per §1.1. Rotating it invalidates all existing sessions. |
| `COOKIE_SECURE` | backend | yes in prod | Must be `true` once served over HTTPS (default is already `true`; only `false` for plain-HTTP local dev). |
| `FRONTEND_BASE_URL` | backend | yes | Exact origin of your frontend (e.g. `https://app.example.com`). Used for CORS — must not be a wildcard. |
| `ANTHROPIC_API_KEY` | backend | no | Enables receipt OCR. Omit to disable that feature gracefully. |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | yes | Backend's public URL. **Build-time**, not runtime — see §5.2. |
| `POSTGRES_PASSWORD` | Path A root `.env` only | yes | Feeds both the `db` service and `DATABASE_URL`. |
| `FRONTEND_DOMAIN` / `BACKEND_DOMAIN` / `CADDY_EMAIL` | Path A root `.env` only | yes | Used by Caddy for TLS cert issuance. |

---

## 5. Things that will bite you if skipped

### 5.1 The frontend and backend are different origins

BillWise's frontend calls the backend at an absolute URL (not a same-origin `/api/*` proxy path). That means:
- `FRONTEND_BASE_URL` (backend) and `NEXT_PUBLIC_API_BASE_URL` (frontend) must point at each other's *real* deployed URLs, not `localhost`, or auth and every API call will fail with CORS errors.
- The auth cookie is `SameSite=Lax`, host-only (no explicit `Domain=`). This works correctly across subdomains of the *same* registrable domain (e.g. `app.example.com` calling `api.example.com`) without any extra config. It will **not** work if frontend and backend end up on entirely unrelated domains (e.g. `billwise.vercel.app` calling `random-name.fly.dev`) in a way that breaks your mental model of "same site" — Vercel/Fly's auto-generated domains ARE unrelated registrable domains from each other, which is still fine for SameSite=Lax purposes (cross-site GET/XHR-with-credentials still works under Lax — Lax's restriction is specifically about top-level cross-site navigations, not fetch calls), but double-check by actually testing sign-in end to end after deploying, not just trusting this paragraph.

### 5.2 `NEXT_PUBLIC_*` variables are baked in at build time

Setting `NEXT_PUBLIC_API_BASE_URL` as a runtime environment variable on an already-built container does **nothing** — Next.js inlines it into the client JS bundle during `next build`. If you change it, you must rebuild (Path A: `docker compose -f docker-compose.prod.yml up -d --build frontend`; Path B: trigger a new Vercel deploy).

### 5.3 Static prerendering is off

`frontend/app/layout.js` reads a per-request nonce (required for the CSP to work — see the comment in that file), which forces every page to render dynamically per-request instead of being statically prerendered. For this app (a behind-auth dashboard, not a marketing site), that's a fine trade-off — just don't be surprised that `next build`'s route table shows `λ` (dynamic) instead of `○` (static) for every page; that's expected, not a bug.

### 5.4 Rate limiting doesn't cover every read endpoint

Four dashboard endpoints (`monthly`, `category-breakdown`, `payment-method-breakdown`, `net-worth`) are deliberately left without the new rate limit — they're reused as plain internal functions by the export-report feature, and slowapi's decorator requires a real per-request object that direct function calls don't have. They're still behind normal authentication. See the comments in `backend/app/api/dashboard.py`.

---

## 6. Post-deploy checklist

- [ ] `curl https://<your-api-domain>/health` returns `{"status":"ok"}`
- [ ] Sign up a real account through the actual frontend URL and confirm the verification email flow works (or check `backend` logs if you haven't wired a real email provider — this app's email sending config is a separate thing to verify per your provider)
- [ ] Confirm `SECRET_KEY` warning is **gone** from backend startup logs
- [ ] Confirm the account hard-delete cron is actually running (Path A: check `docker compose -f docker-compose.prod.yml logs cron` 24h after deploy; Path B/Render: manually trigger the GitHub Actions workflow once from the Actions tab and confirm it succeeds, then check back after the first scheduled run)
- [ ] Confirm `Strict-Transport-Security` and `content-security-policy` headers are present on the live frontend (`curl -sI https://<your-app-domain>/`)
- [ ] Bookmark `docker compose -f docker-compose.prod.yml logs -f` (Path A) or your platform's log viewer (Path B) — you'll want it the first time something goes wrong
