# BillWise Implementation Plan

Source of truth: [prd/billwise-prd-final.md](prd/billwise-prd-final.md)
Governance: harness-os (Constitution → Spec → Test → Code → Review). Specs registered
via `mcp__harness-os__create_spec`; workflow driven via `mcp__harness-os__run_workflow`.

This file is updated after every significant step. Each milestone section tracks
status, what's built, and design decisions made along the way (with rationale) that
aren't already obvious from the code or the PRD.

## Status Legend
`[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

## Milestones (PRD §33)

- [x] **M1: Foundation** — backend (auth, payment methods, categories) DONE,
      security-reviewed, verified end-to-end against real Postgres AND through a
      real Chrome browser via Playwright (register → verify → login → dashboard).
      All decisions human-acked via `harness approve`.
- [x] **M2: Template Integration** — port Ekash template, strip mock data, rebrand,
      remove §9.5 screens. DONE for everything with a real backend or a defined
      empty-state target (§9.1, §9.2, §9.5, §9.6 — see "Milestone 2 Detail" below).
      §9.3 net-new screens deliberately deferred to their owning backend milestones
      (M3/M4/M6/M7) rather than built against nonexistent APIs — documented scoping
      decision, not a gap. Security- and React-reviewed across 5 slices, all
      Playwright-verified. All decisions human-acked via `harness approve`.
- [x] **M3: Transaction Core** — manual transaction CRUD, line items, filters. Backend
      (transactions + transaction_line_items, full CRUD, history filters) and
      frontend (Add/Edit Transaction, Transactions History) both built, tested,
      security- and code-reviewed across 2 governed slices — see "Milestone 3
      Detail" below. Formally `pending_approval` pending human-ack (decisions 31-34).
- [x] **M4: Dashboard, Budgets & Goals** — all 4 slices DONE. Backend: Budgets +
      Savings Goals (incl. the deferred `transactions.goal_id` and an add-funds money
      flow), and Dashboard aggregation (monthly/yearly overviews, category and
      payment-method breakdowns, cash flow) — 118 passing backend tests. Frontend:
      real Budgets + Goals screens (replacing M2's EmptyState placeholders, including
      a real concurrency bug caught via live Playwright testing and fixed), and a real
      Dashboard screen (stat widgets, real spend-trend/category charts, condensed
      budget/goal widgets, recent transactions) — see "Milestone 4 Detail" below.
      All decisions (37-44) human-acked via `harness approve` 2026-07-31.
- [x] **M5: OCR Flow** — all 3 slices DONE. Backend: receipt OCR + confirm-transaction
      and statement OCR (local Tesseract extraction, Claude Haiku structuring, 22
      backend tests, 140 total passing). Frontend: Receipt Review screen + Scan
      Receipt entry point on the existing Add Transaction screen, Playwright-verified
      end-to-end against a real receipt image (backend leg) and a mocked successful
      extraction (review/confirm leg). Live-API-verified after the user populated a
      real `ANTHROPIC_API_KEY` — this surfaced and fixed a real markdown-fence
      JSON-parsing bug in Claude Haiku's response (decision 71, see "Post-M5 bugfix"
      below); confirmed working end-to-end against the live API afterward. Statement-import
      frontend UI now also built (decisions 72-73), closing the last queued follow-up.
      Formally `pending_approval` pending human-ack (decisions 53-58, 71-73).
- [x] **M6: Recurring Bills & Cashback** — all 4 slices DONE. Backend (1-2):
      Recurring Bills (new tables, full CRUD + mark-paid with optional
      auto-created linked transactions, lazy overdue/next-period
      reconciliation) and Cashback (new tables, rules CRUD + a PRD-gap-filled
      GET list route, per-line-item auto-computation on every
      transaction-creation path, manual override, monthly/yearly summary
      dashboard data) — 56 new tests, 196 total passing. Frontend (3-4):
      Recurring Bills and Cashback screens, both net-new UI with no template
      equivalent — see "Milestone 6 Detail" for two instances of the same
      shared-error-state bug class caught (once by hand after the
      react-reviewer agent hit a usage-limit wall, once by the agent itself
      once it recovered) and fixed, plus the Cashback-rules
      GET-endpoint gap-fill. Formally `pending_approval` pending human-ack
      (decisions 76-82).
- [~] **M7: Net Worth, AI Insights, Household & Exports** — slice 1 of 8 DONE.
      Backend: Net Worth (new tables, full CRUD gap-filled from the PRD's
      §24.11 requirement since §25 has no dedicated Net Worth CRUD section,
      complete-snapshot validation rule, dashboard aggregation reusing a
      shared batch-loading helper) — 23 new tests, 219 total passing. See
      "Milestone 7 Detail" below. Formally `pending_approval` pending
      human-ack (decisions 83-84). Remaining slices (frontend Net Worth, AI
      Insights, Household, Exports) not yet started.
- [ ] **M8: Mobile Layout**
- [ ] **M9: Security Hardening**

## Environment Notes

- Found stale `billwise-backend-1` / `billwise-db-1` containers on session start,
  bind-mounted to `backend/` and `docker/postgres-init/` paths that did not exist on
  disk (leftover from an earlier, since-wiped session). Removed with user confirmation
  before scaffolding fresh (2026-07-30).
- `.claude/harness.config.json` `gatedGlobs` only covers `src/**/*.ts(x)`. The actual
  stack is Python (backend) and plain JSX (frontend, per PRD §7.1 — template is
  untyped), so the mechanical CONST-CORE-001/002 gate does not cover either. Rather
  than touch the checksummed config (CONST-CORE-004 fails closed on drift and
  reconciling requires a human-run `harness reconcile-config`), we follow the
  spec→test→code discipline manually via the harness-os MCP tools and pytest, and
  flag this mismatch here for a human to decide whether to reconcile the config later.
- Related: `harness.config.json`'s `testCommands` maps `**/*.py` → `pytest`, but the
  backend only has a toolchain inside its Docker image (no local pip/venv on the host
  sandbox), so enforce-gate.sh's host-side RED/GREEN auto-recording (which runs the
  configured command directly on the host) can't execute bare `pytest` and won't fire
  for the `docker compose run --rm backend pytest` command we actually use. A human
  could point `testCommands` at the docker-wrapped command instead (host has docker,
  even though it doesn't have Python) and run `harness reconcile-config` — deliberately
  not done automatically here since CONST-CORE-004 reserves that step for a human.
  Real RED→GREEN verification still happened for every endpoint below, just via
  `docker compose run --rm backend pytest` directly rather than the mechanically
  recorded path.

## Design Decisions

(Running log — newest first.)

- **2026-07-30**: Backend is fully async (FastAPI `async def` endpoints,
  SQLAlchemy async engine via psycopg3, `sqlmodel.ext.asyncio.session.AsyncSession`).
  Rationale: user's global `python/fastapi.md` rule requires async endpoints/DB
  access for I/O-bound FastAPI work; started sync for simplicity (single-household,
  low-traffic MVP) and converted before building payment-methods/categories on top
  of the same pattern, to avoid a larger rewrite later. Tests use
  `httpx.AsyncClient` + `ASGITransport` (not Starlette's `TestClient`) specifically
  because `TestClient` runs the ASGI app on its own thread/event-loop portal, which
  conflicts with an async DB session fixture created on the test's own
  pytest-asyncio loop — `AsyncClient` calls the app coroutine directly on the same
  loop, avoiding cross-loop errors.
- **2026-07-30**: Dropped `citext` from `users.email` (data spec originally called
  for it) in favor of a Pydantic `field_validator` that lowercases/strips email at
  every request-schema boundary (register/login/password-reset). Avoids depending
  on a Postgres extension for something app-layer normalization handles just as
  correctly, at MVP scale. `BIW-DATA-001` was not re-superseded for this since it's
  a storage-detail simplification, not a contract change — noting it here instead.
- **2026-07-30**: Payment method type and category type are stored as native
  Postgres enums with `values_callable` forcing lowercase `.value` storage (see
  "Bugs caught and fixed" above) rather than SQLAlchemy's default of storing the
  Python member name.
- **2026-07-30**: ORM = SQLModel (Pydantic + SQLAlchemy 2.0 core) with Alembic for
  migrations. Rationale: PRD §7.4 leaves the choice open between SQLAlchemy/SQLModel;
  SQLModel cuts the duplication between ORM models and Pydantic request/response
  schemas across ~17 entities, while Alembic (usable with SQLModel's underlying
  SQLAlchemy metadata) gives real migration history, which a schema this size needs.
- **2026-07-30**: Auth = JWT access token in an httpOnly, Secure, SameSite=Lax cookie,
  verified server-side on every request (per CONST-SEC-004 — no localStorage-only
  auth). No refresh-token rotation in MVP; short-lived access token + re-login on
  expiry, matching PRD §21.1's "intentionally simple" MVP auth.
- **2026-07-30**: Stale Docker containers removed (see Environment Notes) after user
  confirmation.

## Process Note: harness-os discipline gap on M2 (caught by user, corrected)

Started M2 (auth guard + shared-chrome de-mock) by implementing directly —
no `create_spec`/`assess_risk` before writing code, breaking the
Constitution→Spec→Test→Code→Review discipline that M1 followed throughout.
User caught this mid-session and asked that harness-os be used consistently
for the rest of the project, not just M1. Corrected by:
1. Registering `BIW-INFRA-002` (retroactively, describing the already-written
   components — not ideal, but honest about the ordering).
2. Running `assess_risk` (Critical again — keyword match on "financial" this
   time) and `record_decision`.
3. Running both required/relevant reviews (`security-reviewer` per the
   harness's required-gates list, `react-reviewer` per this codebase's own
   standing rule for React changes) before doing any further M2 work.

**Going forward for the rest of M2 (and M3-M9): spec → risk → tests → code →
review happens in that order, every slice, not after the fact.** Sliced by
logical unit of work (e.g. "the Payment Methods screen rework," not "all of
M2") so the spec stays meaningful and reviewable rather than one giant
after-the-fact umbrella covering 40+ screens.

### M2 slice 1 review outcome (`BIW-INFRA-002`, decision 9 → remediation decision 11)

Both required reviews (`security-reviewer`, `react-reviewer`) completed
against `useAuth.js`, `AuthGuard.js`, `Layout.js`, `Header1.js`,
`Breadcrumb.js`, `app/page.js`. react-reviewer's verdict: *"Approve? No.
CRITICAL memory leak in Layout.js must be fixed before merge."* All findings
fixed except one backlogged infra item:

- **CRITICAL** (`Layout.js`): scroll `useEffect` added a
  `document.addEventListener("scroll", ...)` with no cleanup — leaked a new
  listener on every client-side navigation across the app's 40+ routes.
  Pre-existing in the Ekash template, surfaced because this slice's
  `AuthGuard` wrap touched the file. **Fixed**: named `handleScroll` +
  `removeEventListener` cleanup on unmount.
- **HIGH** (`Layout.js`): the same handler's `scrollCheck !== scroll` compared
  against the effect's stale, mount-time `scroll` value (worse, a boolean vs.
  the initial numeric `0` — never strictly equal), so `setScroll` fired on
  every scroll tick instead of only threshold crossings. **Fixed**: direct
  `setScroll(window.scrollY > 100)`, letting React dedupe re-renders.
- **HIGH** (`Header1.js`): search input had no `aria-label`. **Fixed.**
- **HIGH**: no ESLint config with `eslint-plugin-react-hooks` to catch
  hook-cleanup bugs like the above mechanically. **Backlogged, not fixed** —
  installing `eslint`/`eslint-config-next` is a separate infra change
  (new devDependencies + config), out of scope for a review-fix slice.
- **MEDIUM** (security-reviewer, `Header1.js`): `handleLogout` silently
  swallowed `authApi.logout()` errors while always redirecting — risked a
  stale session cookie with no signal. **Fixed**: catch + `console.error`,
  still redirects in `finally` (losing the redirect on failure would strand
  the user in an authenticated-looking UI with a possibly-dead session,
  judged worse than a logged-but-silent failure).
- **MEDIUM** (`Header1.js`): redundant `href="/signin"` alongside an
  `onClick` handler. **Fixed**: converted to a semantic `<button type="button">`.
- **MEDIUM** (`app/page.js`): unnecessary `<>...</>` Fragment wrapper around
  the single `<Layout>` child. **Fixed.**
- **MEDIUM** (`Layout.js`): stray-space typo `< Footer1 />`. **Fixed.**
- **LOW** (`Breadcrumb.js`): current-page crumb used a dead `href="#"`.
  **Fixed**: `<span aria-current="page">`.

Re-verified via Playwright against the live stack (docker compose
backend+db, native `npm run dev` frontend): registered a fresh user,
verified email (confirmed the `verify-email` `useRef` double-invoke fix
from M1 groundwork still holds), logged in, confirmed the dashboard renders
its de-mocked empty states with zero console errors, confirmed the search
input's `aria-label`, scrolled and navigated across pages with zero console
errors, clicked the new logout `<button>` and confirmed correct sign-out +
redirect to `/signin`, confirmed `AuthGuard` still blocks direct dashboard
access post-logout. `npm run build` (production) completes cleanly — all 48
routes generated, zero compile errors. Recorded as harness-os decision 11
(linked to decision 9, still `pending_approval` — critical risk per
CONST-ARCH-001's keyword match, needs human-ack via `harness approve`
before this slice is gate-complete).

## Milestone 2 Detail (checklist from PRD §9)

### Prerequisite (blocking, do first)
- [x] Frontend auth guard: any authenticated-area page must check
      `GET /auth/me` and redirect to `/signin` on 401, before real user data
      gets wired into any of these screens. Implemented via
      `hooks/useAuth.js` (SWR-backed) + `components/auth/AuthGuard.js`,
      wired into the shared `Layout.js` so every screen using `Layout` is
      guarded from one place. Verified via Playwright.

### 9.1 Direct reskin (de-mock, keep structure)
- [x] Sign in / Sign up (OTP step removed) — done in M1 groundwork
- [x] Email verification (link-based) — done in M1 groundwork
- [x] Dashboard (`/`) — de-mocked, real empty states, reviewed and fixed per above
- [x] Yearly/Monthly Analytics (`/analytics*`, all 6 routes) — de-mocked to EmptyState
      (BIW-INFRA-003; no backend yet, Transactions lands in M3)
- [x] Transactions History (`/analytics-transaction-history`) — de-mocked to EmptyState;
      search/filter/edit/delete additions deferred to M3 when the Transactions backend exists
- [x] Budgets (`/budgets`) — collapsed the fake tabbed category UI to a single EmptyState;
      real budgets land in M4
- [x] Savings Goals (`/goals`) — same treatment as Budgets; real goals land in M4
- [x] Categories (`/settings-categories`) — real SWR-backed CRUD against the M1 categories
      API (BIW-INFRA-004): create form (name/type/emoji), live income/expense lists, working
      delete. Owner-only create/delete; partner role sees the list read-only. Type/shared-private
      toggle UI not yet added (sharing endpoint exists on the backend — `PATCH
      /categories/{id}/sharing` — but no frontend control yet; small follow-up, not blocking)
- [x] Notifications (`/notifications`) — de-mocked to EmptyState. Repurposing for
      bills/insights/partner activity deferred until those event sources exist (M5/M6/M7)
- [x] Profile / General / Security settings (BIW-INFRA-006) — real user data from `/auth/me`
      throughout; General collapsed to an honest EmptyState (no preferences backend exists);
      Security shows real email-verification status and links to a newly-wired password reset
      flow (see below).
- [x] Privacy policy, 404 (BIW-INFRA-006) — privacy content rewritten to describe what
      BillWise actually does (was fake Binance/Poloniex cash-exchange copy); 404's dead
      `/index` link fixed to `/`.

### Functional gap found and fixed while de-mocking Settings (BIW-INFRA-006)
Linking Settings-Security's "Change password" to the existing `/reset` route would have
shipped a new dead end: the backend's `/auth/password-reset/request` and `/confirm` endpoints
(built and reviewed in M1) had **no working frontend at all** — `/reset` was an inert template
form (`action="#"`), and `/reset-password` (the exact path the backend emails) didn't exist as
a route. Added `authApi.requestPasswordReset`/`confirmPasswordReset` to `lib/api.js`, wired
`/reset` to the request endpoint (with a deliberately unconditional success message regardless
of whether the email matched an account, to avoid user enumeration — security-reviewer
confirmed this holds), and built `/reset-password` to consume the emailed token. Verified
end-to-end via Playwright: request → grab link from backend logs → confirm → sign in with the
new password.

### 9.2 Reworked (strip forbidden data collection)
- [x] Payment Methods & Tracked Balances (`/wallets`) — real SWR-backed CRUD against the M1
      payment_methods API (BIW-INFRA-005): create form (name/type/issuer/masked-last-4/balance),
      live list, working delete. Never renders a full card number — only the optional masked
      last-4 the backend stores.
- [x] Add Card (`/add-card`) — retired. Collected full card number + CVC + postal code
      (forbidden, PRD §11.1). Now a one-line redirect to `/wallets`, which owns the one real
      creation form.
- [x] Add Tracked Card or Savings (`/add-bank`) — retired. Collected bank routing/account
      number (forbidden). Redirects to `/wallets`.
- [x] Add New Account chooser (`/add-new-account`) — retired. Investment-app-styled
      ("invest large amount"/"invest small amount") chooser that only routed to the two
      retired forms above. Redirects to `/wallets`.
- [x] `/settings-bank` — retired. Duplicate fake "Bank of America"/"Master Card" bank-linking
      UI. Redirects to `/wallets`. Dead "Add Bank" link removed from SettingsMenu.js.

### 9.3 Net new (no template equivalent) — scoping decision
These screens have no template equivalent **and no backend yet** — Add Transaction/OCR is M3,
Recurring Bills is M6, Cashback/Net Worth are M7, Household & Partner Sharing needs new backend
endpoints beyond the M1 `partner_permissions` model. Building real UI against a nonexistent
backend would mean either shipping fake data (violates the project's no-mock-data principle,
already fixed once in M1/M2) or a dead-end form that saves nothing. **Decision: build each of
these alongside its owning backend milestone, not now.** Tracked here for visibility, not as
M2 scope:
- [ ] Add Transaction (manual entry) — M3
- [ ] Receipt Review / OCR Confirmation — M3
- [ ] Recurring Bills — M6
- [ ] Cashback — M7
- [ ] Net Worth — M7
- [ ] Household & Partner Sharing — needs new backend (invite flow), TBD milestone
- [ ] Account Deletion flow (in Settings) — needs a new backend endpoint, not yet built
- [ ] Mobile bottom-nav layout (§9.4 — M8 per milestone list; may land earlier if time allows)

### harness-os trail for slices 2-4
Each slice: `assess_risk` → `create_spec` → `record_decision` (pending) → implement →
Playwright-verify → `security-reviewer` + `react-reviewer` (parallel background agents) →
apply fixes → re-verify → `record_decision` (remediation, linked via `related_decision_id`).
- Slice 2 (`BIW-INFRA-003`, decisions 13/15): Analytics×6/Budgets/Goals/Notifications de-mock.
  security-reviewer: clean. react-reviewer: fixed a pre-existing template typo
  ("Banalce"→"Balance") and 6 reintroduced Fragment wrappers; declined the 'use client'
  suggestion as a non-functional style preference that contradicts the template's own
  convention.
- Slice 3 (`BIW-INFRA-004`, decisions 14/17): Categories real CRUD wiring.
  security-reviewer: clean (one non-blocking fix applied — handleDelete lacked try/catch).
  react-reviewer: fixed a HIGH keyboard-accessibility bug (delete was `<span role="button">`,
  not focusable/activatable — now a real `<button>`, which required a matching SCSS selector
  update in `_settings-categories.scss`) and a MEDIUM double-delete race (added a `deletingId`
  in-flight guard).
- Slice 4 (`BIW-INFRA-005`, decisions 16/18): Payment Methods rework (Wallets +
  retire add-card/add-bank/add-new-account/settings-bank, all of which collected PRD
  §11.1-forbidden fields). security-reviewer: clean — confirmed the new form only ever
  collects schema-allowed fields, never a full card/account number. react-reviewer: fixed
  missing label/input associations (HIGH, WCAG 2.1 Level A — same gap existed unflagged in
  the Categories form from slice 3, fixed there too for consistency), missing `role="alert"`
  on error text (HIGH), stale error state after a successful action (MEDIUM), and an
  unnecessary Fragment in `SettingsMenu.js` (MEDIUM).

- Slice 5 (`BIW-INFRA-006`, decisions 19/20): Profile/Settings/Privacy/404 reskin, password
  reset flow, ESLint tooling. security-reviewer: clean — confirmed the enumeration-prevention
  pattern in the reset request flow, confirmed the reset token is never logged/exposed.
  Flagged a HIGH `brace-expansion` dev-dependency advisory (dev-only, not fixed). react-reviewer:
  fixed an unnecessary Fragment in `not-found.js` (HIGH) and a missing `Suspense` `fallback`
  prop in `reset-password/page.js` (HIGH, React 18 requirement) — also proactively fixed the
  same pre-existing gap in `verify-email/page.js` for consistency. Backlogged a MEDIUM
  suggestion to add Error Boundaries above Suspense boundaries site-wide (architectural, not
  slice-specific).

All five slice decisions (11, 15, 17, 18, 20) remain `pending_approval` pending human-ack via
`harness approve`, consistent with every prior critical/high-risk decision in this project.

### Security debt found, deferred to M9 (not silently ignored)
Investigating a lint-flagged `brace-expansion` dev-dependency advisory led to running a full
`npm audit`, which surfaced a **pre-existing critical-severity vulnerability**: this project's
`next@14.0.4` (pinned since the original Ekash template, not introduced this session) has a
known SSRF-via-rewrites CVE and an unauthenticated internal Server Function endpoint disclosure
CVE. The fix (`next@14.2.35`) is outside the current package.json range and would need its own
dedicated verification pass across all ~48 routes before shipping — too large to fold into a
screen-reskin slice. **Deferred to M9 (Security Hardening)**, tracked here so it isn't lost.

### ESLint added (closes a backlog item from slice 2's review)
`react-reviewer` flagged in slice 2 that there was no ESLint config to mechanically catch hook
bugs like the Layout.js memory leak found in M2 slice 1. A `next build` run later auto-generated
a `.eslintrc.json` (`extends: next/core-web-vitals`) but it was non-functional — `eslint` itself
was never an actual devDependency. Installed `eslint@8` + `eslint-config-next@14.0.4` (pinned to
match this project's Next.js version) for real. This immediately surfaced 3 real, previously
build-blocking `react/no-unescaped-entities` errors that had been silently passing before
because eslint wasn't actually running — fixed in `app/demo/page.js`, `app/otp-phone/page.js`,
`app/settings-session/page.js`. `npm run build` and `npx next lint` are both clean now.

### 9.5 Remove entirely from nav/routing (keep files, per PRD — don't delete)
- [x] `/id-front-and-back-upload`, `/verify-id`, `/verifying-id`, `/verified-id` (KYC) — no
      remaining nav entry point; their only inbound link (Settings-Security's SSN-card section)
      was already stripped in BIW-INFRA-006.
- [x] `/otp-code`, `/otp-phone` (OTP/2FA) — same: only inbound link (phone-verification section)
      already stripped in BIW-INFRA-006.
- [x] `/affiliates` (referral) — removed from `Sidebar.js`.
- [x] `/support*` (ticketing) — removed from `Sidebar.js` and `SettingsMenu.js`.
- [x] `/settings-api` (dev API keys) — removed from `SettingsMenu.js`.
- [x] `/settings-currencies` (multi-currency) — removed from `SettingsMenu.js`.
- [x] `/bank-add-successful` — no remaining inbound link outside the standalone demo page.
- [x] `/settings-session`, `/locked`, `/blank` — `settings-session` removed from
      `SettingsMenu.js`; `locked`/`blank` had no inbound nav links to begin with.

### 9.6 Mock data sweep
- [x] Every §9.1/§9.2 screen (the full set actually reachable via nav after the §9.5 removal)
      now pulls real backend data or shows a defined empty state — zero leftover hardcoded
      balances/names/avatars/chart data. Verified via `grep` for known template mock strings
      (`12.12.2023`, `Grocery Items and Beverage`, hardcoded `$1200`-style figures) returning
      no matches across every edited file, plus Playwright console-error checks on every route.
- [ ] §9.3 net-new screens are explicitly out of this sweep's scope — they have no template
      mock data to remove in the first place (no template equivalent existed) and will get
      real data wiring alongside their owning backend milestone, not fake placeholder data now.
- [ ] §9.5-removed screens (KYC/OTP/support/etc.) still contain their original template mock
      data internally, but are no longer reachable from any nav — PRD says keep the files, not
      clean them, so this is intentionally left alone.

M2's screen-level de-mock work is now complete for everything in scope. What's left before M2
can be called fully done: `/wallets`, `/settings-categories`, and the reworked settings screens
should get one more look once M3/M4 land real backends, since some of the "empty state" screens
here will need to flip over to real data wiring at that point — tracked per-milestone above,
not re-litigated here.

**Follow-up: Wallets visual restyle — DONE** (`BIW-INFRA-008`, decisions 35 → 36). The user
pointed out mid-M3 that `/wallets` lost the original template's styled `.credit-card`/`.wallet-nav`
visual chrome when M2 slice 4 rewrote it — that rewrite correctly stripped the forbidden fields
the original template hardcoded (a fake full 16-digit card number, cardholder name, expiry date —
none of which PRD §11.1 allows storing) but overcorrected by dropping the visual styling along
with the data. Confirmed via `git show 7e37aa3:frontend/app/wallets/page.js` (the pre-M2
original). Rebuilt `/wallets` after M3 finished (per the user's explicit choice not to interrupt
M3's in-flight critical-risk review): left-column `.wallet-nav` list of real payment methods
(click to select, real `<button>` with `aria-pressed`, not a div+role reimplementation), a
toggleable "Add new wallet" panel reusing the unchanged create-form fields, and a right-column
detail view showing the original `.credit-card` gradient visual for Credit Card/Debit Card types
(masked `•••• •••• •••• 1234` instead of a fake full number, alias name instead of a fake
cardholder, no expiry field, optional cashback rate) or a simpler balance card for Cash/Tracked
Savings/Other. security-reviewer and react-reviewer both clean (one MEDIUM style note on
h4/h5/h6 usage in the credit-card visual, intentionally left as-is since those are the exact
selectors `_credit-card.scss` targets — changing them would break the template-matched visual).
`npm run build` clean, Playwright-verified end-to-end (Cash + a newly-created Credit Card both
render correctly, nav selection/active-state, create/delete cycle).

## Milestone 3 Detail (Transaction Core)

### Scope decisions (documented up front, per harness-os decision 31/33 rationale)
- **`goal_id`, tags, recurring-flag, cashback-eligible-flag** — PRD §12.1 lists these as
  manual-entry fields, but §23.5's actual DB schema for `transactions` has none of them (no
  other section references them either). Deferred to their owning milestones: `goal_id` to M4
  (the `goals` table doesn't exist yet — nothing to foreign-key against), tags/recurring/cashback
  to M6. Schema-is-authoritative precedent, same as M1/M2.
- **Every line item requires `category_id`** (no type-conditional required/optional split) —
  matches §23.6's schema (no nullable marker), naturally satisfies §12.4's "category required for
  expenses" without extra logic.
- **Hard delete, no soft-delete/`is_active`** — §23.5's `transactions` table has no `is_active`
  column (unlike `payment_methods`/`categories`, which do and are soft-deleted) — schema signal
  followed directly.
- **"Export filtered data"** (§24.6) deferred to M7, which already owns CSV/Excel/PDF export as a
  milestone deliverable.
- **Receipt scan / statement import** (§24.4) not built — both require the OCR pipeline, which is
  M5. Only manual entry is in scope for M3, consistent with the milestone's own PRD description
  ("manual transaction CRUD").

### Backend (`BIW-DATA-002`, `BIW-API-002`, decisions 31 → 32)
- `transactions` + `transaction_line_items` tables (SQLModel), full CRUD router
  (`GET/POST /transactions`, `GET/PATCH/DELETE /transactions/{id}`), filters on the list endpoint
  (month, category_id, payment_method_id, amount_min/max, free-text search).
- Server-side validation: line-item amounts must sum to the transaction total (Decimal, quantized
  to cents, `ROUND_HALF_UP`); amount sign enforced per PRD §12.4 (only `Adjustment` may be
  negative); payment method and category ownership + active-status checked on every write;
  non-blocking duplicate-transaction detection (same merchant/date/amount/payment method) surfaced
  as a `possible_duplicate` flag on the create response, never blocking the write.
- Real TDD: wrote `tests/test_transactions.py` alongside the implementation, ran against the live
  docker-compose Postgres via `docker compose run --rm backend pytest`; 62 passing initially, grew
  to **67 passing** after the fastapi-reviewer's test-gap findings were closed (inactive
  payment-method/category rejection, explicit `quantity`, PATCH revalidation when only
  `total_amount`/`transaction_type` changes without new line items, DB-level cascade-delete
  verification).
- security-reviewer: clean, no findings (IDOR-proof ownership checks, no SQL injection, mass
  assignment blocked by `extra="forbid"`, correct Decimal rounding, no data leakage in errors).
- fastapi-reviewer: 2 HIGH (N+1 query in `list_transactions` — fixed by batch-loading all line
  items for the fetched transaction_ids in one query instead of one query per transaction; the
  `category_id` filter was filtering an already-fetched Python list in memory instead of pushing
  into SQL — fixed with an `id.in_(select(...))` subquery condition), 2 MEDIUM (missing index on
  `transaction_line_items.category_id` — added; test coverage gaps — closed, see above).
- Live smoke-tested end-to-end via curl against the running backend (register → verify via direct
  DB flip, since dev has no SMTP → login → create payment method/category/transaction → filter by
  category) before and after the review fixes.

### Frontend (`BIW-INFRA-007`, decision 33 → 34)
- `transactionsApi` added to `lib/api.js` (list with query-param filters, create, get, update,
  remove), following the established per-domain API-object pattern.
- `/add-transaction` (net-new route, deferred out of M2 §9.3 specifically until this backend
  existed): manual entry form with dynamic multi-category line-item splitting (PRD §12.3's
  Costco-across-Grocery/Shopping example), reused for edit via `?edit=<id>` (loads via
  `transactionsApi.get`, PATCHes instead of POSTs) rather than a separate edit implementation.
- `/analytics-transaction-history` rewritten from its M2 EmptyState placeholder to a real
  filterable/searchable table (month/category/payment-method/amount-range/search) with inline
  edit/delete; shows a non-blocking duplicate-warning banner (`?duplicate=1` redirect flag) rather
  than blocking the Add form, since by the time `possible_duplicate` is known the transaction is
  already saved — blocking there would risk a real double-submit on resubmit.
- Sidebar gained a "Transactions" entry (deliberately left out in M2 since no transaction backend
  existed yet).
- security-reviewer: clean, no findings.
- react-reviewer: 2 HIGH (SWR cache key was a freshly-constructed object every render on the
  History page, defeating dedup/caching — fixed with a `JSON.stringify(filters)` stable key; line
  items used array index as React key while supporting removal from any row, risking state
  misattachment on a middle-row removal — fixed with a `crypto.randomUUID()`-based stable key per
  line item), 1 MEDIUM (an awkwardly-worded but harmless `useEffect` guard condition — tightened).
- Full interactive Playwright pass (both before and after the review-fix round): single-category
  create, two-category split create, edit with pre-filled multi-line-item state, search filter,
  delete with `window.confirm`, and the duplicate-warning banner end-to-end — zero console errors
  throughout. `npm run build` clean, 50/50 routes, after fixing one build-blocking
  `react/no-unescaped-entities` lint error the build itself caught before review started.

## Milestone 4 Detail (Dashboard, Budgets & Goals)

### Backend slice 1 — Budgets + Savings Goals (`BIW-DATA-003`, `BIW-API-003`, decisions 37 → 38)
- `budgets` table (per-category monthly amounts, unique on `user_id`+`category_id`+`month`+`year`)
  and `savings_goals` table (name/target/target_date/icon/color/sharing/is_active), plus the
  `transactions.goal_id` nullable FK deferred from M3 (§23.5's `savings_goals` table didn't exist
  yet when the transactions schema was built).
- Scope decisions documented up front in decision 37: (1) goal `current_amount` computed live via
  `SUM(total_amount) WHERE goal_id = ...` rather than stored-and-synced, matching the schema's own
  "derived from linked transactions" annotation and avoiding a cross-cutting sync mechanism across
  every transaction write path. (2) `goal_id` only valid on Saving expense/Adjustment transactions
  (PRD §12.1), enforced in `transactions.py`'s `_validate_goal`. (3) Goal delete is soft
  (deactivate + null out `goal_id` on referencing transactions), matching PRD §27.4 verbatim.
  (4) Budget rollover (PRD §14.4) implemented as an auto-copy-on-read side effect of `GET /budgets`
  when the requested month is empty but an earlier month has rows — new independent rows, source
  month untouched. (5) Budgets hard-deleted (no `is_active` in §23.7's schema, same signal used
  for transactions in M3).
- Real TDD: 100 passing backend tests (grew from an initial 95 after the fastapi-reviewer's
  coverage-gap findings were closed).
- security-reviewer: clean, no CRITICAL/HIGH — explicitly verified the add-funds money flow
  validates payment_method/category against the *authenticated* user (not just any UUID), IDOR-safe
  across all 11 new endpoints, goal-deactivation's bulk `goal_id`-nulling correctly scoped.
- fastapi-reviewer: HIGH (budget rollover loaded the user's entire budget history unfiltered just
  to find the most recent earlier month — fixed by pushing the earlier-period comparison into SQL),
  2 MEDIUM (goals.py imported "private" underscore-prefixed validators directly from
  transactions.py — fixed by promoting `validate_payment_method`/`validate_line_items`/`quantize`
  to a new `app/services/transaction_validation.py` module both routers import publicly, per the
  project's FastAPI rules on keeping routers thin; test coverage gaps — closed with 6 new tests
  covering budget-delete/goal-update/goal-sharing 404s and rollover edge cases including a
  Dec→Jan year boundary).
- Live smoke-tested end-to-end via curl against the running backend both before and after the
  refactor (goal create → add-funds → current_amount updates correctly; budget create → rollover
  into the next month) — service hot-reloaded cleanly post-refactor with no import errors.

### Backend slice 2 — Dashboard aggregation (`BIW-API-004`, decisions 39 → 40)
- 5 read-only GET endpoints under `/dashboard`: `/monthly` (income/expenses/net cash flow, top
  category, top payment method, per-category budget status, comparison vs previous month —
  correctly handles the January→December-of-prior-year boundary), `/yearly` (12-entry monthly
  trend, spend by category/payment method, average/highest/lowest month, YTD savings total),
  `/category-breakdown` (per-category % of total + budget comparison for a period),
  `/payment-method-breakdown` (spend/count/average/tracked balance per method), `/cash-flow`
  (income vs expenses view per PRD §18.6). No new tables — pure aggregation over
  transactions/transaction_line_items/budgets/categories/payment_methods, scoped to the owner.
- Scope decisions documented up front in decision 39: (1) "spend"/"expenses" aggregations use
  `TransactionType.EXPENSE` only, excluding Saving expense and Adjustment — matches how Budgets are
  scoped to expense-type categories (`transaction_validation.py`'s `EXPENSE_LIKE_TYPES` distinction
  carried into the dashboard's category/payment-method rollups). (2) `ytd_savings_total` on the
  yearly endpoint separately sums Saving-expense transactions rather than folding them into
  "spending". (3) `/dashboard/net-worth` and `/dashboard/ai-insights` explicitly out of scope,
  deferred to M7/M9 per PRD. (4) `average_month` divides by a fixed 12, not by months-with-data.
  (5) `/dashboard/monthly`'s `budget_status` reuses the exact rollover-aware view `GET /budgets`
  would show for that period — the rollover helper was promoted from budgets.py's private
  `_rollover_if_needed` to a public `app/services/budget_rollover.py::ensure_budget_rollover`,
  shared by both routers (same "extract shared logic to services/" pattern used for
  `transaction_validation.py` in slice 1, applied proactively this time instead of waiting for a
  reviewer finding).
- Real TDD: 115 passing backend tests (14 written up front for the slice, +1 added post-review to
  close a leak-coverage gap).
- security-reviewer: no CRITICAL/HIGH. 1 MEDIUM (payment-method spend aggregation relied only on
  `Transaction.user_id` for scoping, no explicit `PaymentMethod.user_id` check — defense-in-depth
  gap, not an exploitable leak given the FK's referential integrity, but fixed anyway) — added
  explicit ownership filters to every joined query (`Category.user_id`/`PaymentMethod.user_id`) in
  both the monthly and yearly endpoints. 1 LOW (budget category-name lookup had no ownership check)
  — resolved by the same fix. Added a test creating real second-user transaction data and asserting
  it never appears in the first user's totals, top-entries, or breakdowns.
- fastapi-reviewer: 1 HIGH (N+1 — `session.get(Category, ...)` once per budget inside the
  `budget_status` loop) — fixed by batch-fetching all budget categories in one `IN()` query
  (also closed a related LOW: budgeted categories with zero spend previously fell back to an empty
  name). 2 MEDIUM (three response fields — `comparison_vs_previous_month`, `highest_month`,
  `lowest_month` — were typed `Optional` but the endpoint logic always populates them, misleading to
  API clients; `PaymentMethodBreakdownItem.type` was a bare `str` instead of the `PaymentMethodType`
  enum, losing OpenAPI enum documentation) — both fixed.
- Live-verified via the running dev backend's OpenAPI schema that all 5 routes registered and
  hot-reloaded cleanly with no import errors after the refactor.

### Frontend slice 3 — Budgets + Goals screens (`BIW-INFRA-009`, decisions 41 → 42)
- Rewrote `frontend/app/budgets/page.js` (was M2's EmptyState) into a month/year-scoped
  budget-vs-actual screen: nav list of budgeted categories sourced from
  `GET /dashboard/category-breakdown` (spend, % used, over-budget flag), month
  prev/next navigation, create/edit/delete via `/budgets` CRUD, an "add budget" flow
  restricted to expense categories not yet budgeted for the selected period. Retains
  the Ekash template's `.budgets-nav`/`.budgets-tab-content` visual chrome, strips the
  template's fake Last-Month/Expenses/Taxes/Debt stat grid and fake Budget Period chart
  (no real data source for either).
- Rewrote `frontend/app/goals/page.js` (was M2's EmptyState) into a real goals screen:
  nav list with real `CircularProgress` (current/target %), create/edit/deactivate,
  an add-funds flow that creates a real linked transaction via
  `POST /goals/{id}/add-funds`, a real contributions history table sourced from
  `GoalDetail.contributing_transactions`, and a sharing toggle. Strips the template's
  fake "Available by Wallet" cross-wallet balances and fake history rows.
- Added `budgetsApi`/`goalsApi`/`dashboardApi` to `frontend/lib/api.js` following the
  existing `request()`-wrapper pattern.
- **Live Playwright testing caught a real production bug**, not just a static-review
  finding: the Budgets page's two parallel SWR fetches (`/budgets` and
  `/dashboard/category-breakdown`, same period) both independently call
  `ensure_budget_rollover`; each request gets its own DB session in production, so
  both can pass the "no rows yet" check before either commits, then race to insert the
  same rolled-over row and hit `uq_budget_category_period`, surfacing as an uncaught
  500/CORS error in the browser on month navigation. Fixed by catching the
  `IntegrityError` in `budget_rollover.py` and treating it as a no-op. Verified the fix
  is real (not a false-positive test) by writing a regression test using genuinely
  independent DB connections (bypassing the test suite's shared-session fixture, which
  cannot reproduce true cross-connection races), reverting the fix to confirm the test
  fails with the exact error seen in the browser, then restoring the fix and
  reconfirming green.
- `/dashboard/category-breakdown` also gained: (1) budgeted categories with zero spend
  now appear (previously only categories with actual expense line items did — a gap
  that would have hidden newly-budgeted categories from the Budgets screen), (2) the
  same `ensure_budget_rollover` call `/dashboard/monthly` already had, for consistency
  with `GET /budgets`.
- security-reviewer: 1 HIGH on the concurrency fix itself — catching bare
  `IntegrityError` risked masking unrelated integrity violations — narrowed to check
  `error.orig.diag.constraint_name == "uq_budget_category_period"`, re-raising
  anything else. No frontend vulnerabilities found (React auto-escaping, no
  `dangerouslySetInnerHTML`, all IDs server-sourced and owner-enforced backend-side,
  proper `credentials: "include"` usage).
- react-reviewer: approved, no CRITICAL/HIGH. 3 MEDIUM polish items applied: `useMemo`
  on the category→budget-id `Map` rebuilt each render, an explicit `<label>` for the
  edit-budget-amount input (was `aria-label` only), resetting the add-funds date field
  after successful submission (previously stayed stale across repeat contributions).
- Backend suite: 118 passing (115 → +3: two `category-breakdown` tests for the
  zero-spend/rollover-consistency fixes, one true-concurrency regression test).
  Frontend production build clean. Manually walked both screens end-to-end via
  Playwright against the live dev stack: budget create/edit/delete, over-budget
  styling, month navigation with rollover (including the race-condition scenario,
  confirmed fixed), goal creation, add-funds → real transaction → progress update,
  sharing toggle, contribution history.
- **Mid-slice environment incident**: Docker Desktop's WSL integration dropped
  mid-session (lost `docker` binary and all running containers, including
  `harness_gate_daemon`); required the user to restart Docker Desktop and reconnect
  the Claude Code session for the `harness-os` MCP connection to come back before
  decision 42 could be recorded. No code or data was lost — this was purely a local
  dev-environment interruption, not a project issue.

### Frontend slice 4 — Dashboard screen (`BIW-INFRA-010`, decisions 43 → 44)
- Rewrote `frontend/app/page.js` (was M2's fully-empty-state placeholder — the last
  screen in the app still fully mocked) into a real Dashboard now that every
  prerequisite backend exists: stat widgets (Total Balance = live sum of
  `payment_methods.current_balance`, Total Period Change/Expenses/Income from
  `GET /dashboard/monthly`), a real category-spend donut and a real 12-month
  spend-trend bar chart, a condensed Monthly Budgets progress list, a condensed
  Saving Goals list (reusing `CircularProgress` from the Goals screen), and a recent
  Transaction History table.
- Two new parameterized Chart.js components (`DashboardCategoryDonut`,
  `DashboardSpendTrendChart`) built from scratch rather than reusing the Ekash
  template's existing `ChartjsDonut`/`ChartjsIncomeVsExpense` components, which have
  hardcoded fake data baked in with no data props — consistent with the no-fake-data
  discipline applied throughout M2-M4.
- Weekly Expenses and Recurring Bills cards deliberately remain honest empty states
  (no weekly-granularity aggregation endpoint exists, and M6/Recurring Bills isn't
  built yet) rather than approximated with misleading data. "Balance Trends" relabeled
  "Monthly Spending Trend" since the schema has no balance-snapshot-over-time data —
  the yearly spend-by-month figures are what's actually available and honest to show.
- security-reviewer: approved outright, no findings — confirmed all 6 endpoints used
  are the same owner-scoped ones already reviewed in prior slices, no new backend
  surface, no XSS vectors.
- react-reviewer: 2 HIGH (both accessibility) — the two chart components had no ARIA
  description on their canvases, and three progress bars had `role="progressbar"`
  with no `aria-valuenow`/`min`/`max`/`label` — both fixed. 2 MEDIUM — `topCategories`
  sort/slice wasn't memoized (now `useMemo`, matching the pattern from
  `budgets/page.js`), an inline width calculation extracted to a named variable.
  Also fixed the donut chart's `responsive: false`, which conflicted with its
  Bootstrap-responsive parent column.
- Backend unchanged this slice (no new endpoints needed) — 118 tests still passing.
  Frontend production build clean. Playwright-verified end-to-end against real seeded
  data (a wallet, two categories, an over-budget budget, a goal with a real
  contribution, two transactions) with a full-page screenshot confirming every widget
  renders real numbers with no console errors.
- **This closes M4.** All four slices (backend Budgets+Goals, backend Dashboard
  aggregation, frontend Budgets+Goals, frontend Dashboard) are implemented, tested,
  reviewed, and committed — see decisions 37-44 in "Outstanding human actions".

### Wallets enhancement — DONE (BIW-INFRA-013, decisions 74-75)
Per user request 2026-07-30, built 2026-07-31 (after M5, before M6): extended the
Wallets page (`frontend/app/wallets/page.js`) with a total-balance summary (client-side
sum of `current_balance` across active payment methods, shown above the wallet nav
list), this-month's-spending for the active wallet (existing, unchanged
`GET /dashboard/payment-method-breakdown`, matched by `payment_method_id`), and a
per-wallet recent-transactions list (existing, unchanged
`GET /transactions?payment_method_id=`, newest-10 shown, no edit/delete — full
management stays on the Transaction History page). No backend changes; all three
reuse already-reviewed, owner-scoped endpoints. "Available balance"
(`credit_limit - current_balance`) explicitly descoped by the user 2026-07-31: it
needs a new `credit_limit` field not in the current `PaymentMethod` data model / PRD.

`assess_risk` auto-critical (financial keyword match: payment, wallet) →
`create_spec` (`BIW-INFRA-013`) → `record_decision` (74, pending).
**security-reviewer**: clean, no findings — total balance is a local sum of the
user's own data; month-spend/history fetches match by id against owner-scoped
endpoints; SWR cache keys correctly scoped by month/year and wallet id.
**react-reviewer**: APPROVE with 1 MEDIUM (unnecessary `useMemo` on a trivial
reduce feeding one text node) — fixed by computing `totalBalance` directly;
conditional SWR key pattern, cache-key primitives, and stale-data-on-switch
handling were all already correct. Remediation recorded as decision 75, linked
to 74.

**Verification**: ESLint clean, production build clean. Playwright-verified
end-to-end: created two wallets ($300 + $200) → total balance summed to $500;
added a real $45.50 transaction against one wallet via Add Transaction → that
wallet's month spend showed $45.50 and recent transactions listed it, while the
other wallet correctly showed $0/empty. Test data cleaned up from the dev DB
afterward.

## Milestone 5 Detail (OCR Flow)

### Scope decision (confirmed with user 2026-07-30, before implementation)
PRD §7.5 reads as internally contradictory in isolation — point 1 suggests sending
the receipt image itself to Claude Haiku for OCR, point 2 forbids ever sending the
image to any third party. Resolved with the user: **local OCR extracts text entirely
within the backend process (Tesseract via pytesseract — the image bytes never leave
the process, satisfying point 2); only the extracted plain text is sent to Claude
Haiku for structuring into the §29.1 JSON schema** (satisfying point 1's "AI does the
receipt-understanding work" intent without violating point 2's privacy constraint).
User confirmed this interpretation and confirmed they will add a real
`ANTHROPIC_API_KEY` to `backend/.env` themselves (not pasted into chat) — live
end-to-end verification with a real receipt image is pending that key being added;
until then the flow is verified against 134 passing tests with the Anthropic SDK
mocked at its client boundary.

### Slice 1: Backend receipt OCR + confirm-transaction (BIW-API-005, decisions 53-54)
- `POST /ocr/receipt` — multipart upload (jpg/png/heic/single-page PDF, 10MB max).
  Local Tesseract extraction (`app/services/ocr_service.py`) runs via
  `asyncio.to_thread` so it doesn't block the event loop; PDF pages are rasterized
  via PyMuPDF at 300dpi. Extracted text is sent to Claude Haiku
  (`app/services/ai_structuring_service.py`, `anthropic.AsyncAnthropic`) to
  structure into the §29.1 schema (merchant/date/total/tax/items/warnings), with a
  30→40s end-to-end timeout (widened during review — see below) falling back to a
  clean 504 so the client can drop to manual entry. Stateless: no DB writes, no file
  ever touches disk — image bytes live only in the request's local scope.
  Category suggestions are constrained server-side to the §29.2 allowlist plus
  "Uncategorized" (confidence < 0.6 forced to Uncategorized regardless of what the
  model returns) — defense-in-depth against a prompt-injection receipt image trying
  to make the AI emit an arbitrary category string.
- `POST /ocr/confirm-transaction` — creates the real `Transaction`
  (`source='Receipt OCR'`) from the user-reviewed/edited data. Never called
  automatically. Reuses the exact same ownership/validation path as manual entry
  (`POST /transactions`) — see the DRY refactor below — so a client that skips the
  actual OCR step and calls this directly with arbitrary data gets identical
  ownership, category-type, line-item-sum, and duplicate-detection enforcement.
- **Proactive DRY refactor**: `_validate_goal`/`_detect_duplicate` (previously
  private helpers in `app/api/transactions.py`) plus a new
  `create_transaction_record`/`load_line_items`/`to_transaction_public` were
  promoted to `app/services/transaction_validation.py` so both the manual-entry
  router and the new OCR router share one code path for transaction creation and
  serialization — same pattern established in M4 slice 1 (`budget_rollover.py`) and
  M3 (`transaction_validation.py` itself). `app/api/transactions.py` shrank
  accordingly with no behavior change (132/132 pre-existing tests unaffected).
- Dockerfile: added `tesseract-ocr` system package. requirements.txt: `pytesseract`,
  `Pillow`, `pillow-heif` (HEIC support), `pymupdf` (PDF rasterization, no extra
  system deps needed), `anthropic`, `python-multipart` (required for FastAPI file
  uploads — build failed without it, caught immediately by the test run).

### Security review (security-reviewer agent) — fixed immediately
- **Memory-exhaustion DoS**: file was read fully into memory before the size check.
  Fixed — reject early from the `Content-Length` header before buffering the body.
- **Missing rate limit on `/ocr/confirm-transaction`**: added (matches
  `/ocr/receipt`'s window) — it creates real financial records and the security
  checklist requires rate limiting on all endpoints.
- **API-key/PII leakage risk in logs**: exception objects and raw AI-response text
  were logged directly, which could echo SDK internals or receipt PII (merchant
  names, item text) into application logs. Fixed — log only exception type and
  response length, never content.
- **PDF resource exhaustion**: no bound on rendered-page pixel count before 300dpi
  rasterization — a malicious PDF declaring huge page dimensions could force a
  massive allocation. Fixed — bounded to ~40MP before calling `get_pixmap`.
- **Content-Type spoofing**: PDF-vs-image parsing was routed by the client-supplied
  `Content-Type` header, which is trivially spoofable. Fixed — routing now sniffs
  the `%PDF-` magic bytes instead. This also surfaced a real bug the security
  review didn't originally flag as such: `pymupdf.open()` on malformed PDF bytes
  raised an **unhandled** `pymupdf.FileDataError` (would have been a raw 500, not a
  clean 422) — wrapped in try/except. Verified this wasn't a paper finding by
  reverting the fix and re-running the new regression test
  (`test_malformed_pdf_bytes_return_422_not_500`): it failed with exactly that
  unhandled exception, then passed again once restored.
- Deferred as documented, accepted residual risk (not fixed): `asyncio.to_thread`
  cannot forcibly kill the underlying OS thread if the route's `asyncio.wait_for`
  times out — the Tesseract process keeps running to completion in the background.
  Not fixable without a killable worker-process pool, judged over-engineering at
  this MVP's single-instance, 20/hour-rate-limited scale.

### FastAPI review (fastapi-reviewer agent) — fixed immediately
- Async correctness (blocking Tesseract via `asyncio.to_thread`, `AsyncAnthropic`
  properly awaited, `response_model` Decimal handling matching the existing
  `TransactionPublic` convention), error-status-code choices, router organization,
  and the transactions.py refactor were all confirmed correct/idiomatic outright.
- **Anthropic client reconstructed per-request**: not idiomatic (new httpx
  connection pool every call, never closed). Fixed — cached as a module-level
  singleton (`_client_cache`), same pattern as `app.core.db`'s module-level
  `engine`. Tests reset the cache explicitly via monkeypatch to keep isolation
  between tests that swap in different fake clients.
- **Timeout margin too tight**: AI client timeout (25s) left only 5s of the 30s
  route budget for Tesseract + thread-scheduling overhead. Fixed — route budget
  widened to 40s, client timeout brought down to 20s, leaving a comfortable margin.

### Verification
16 new tests in `backend/tests/test_ocr.py` (auth requirements, file-size/type
rejection, successful structured extraction, unreadable-image and timeout
fallback-to-manual paths, magic-byte PDF routing + malformed-PDF regression,
confirm-transaction creation/duplicate-detection/validation, and AI-structuring
unit tests mocked at the Anthropic SDK boundary for low-confidence coercion,
malformed-JSON handling, and missing-API-key handling). Full backend suite:
134/134 passing, no regressions. Not yet Playwright-verified end-to-end (no
frontend UI exists yet — that's slice 3 — and live Anthropic calls are pending the
user adding a real API key).

### Post-M5 bugfix: markdown-fence JSON parsing (decision 71, related to 54)
The user populated a real `ANTHROPIC_API_KEY` and the first-ever live call to
`POST /ocr/receipt` returned 502. Root cause: Claude Haiku wraps its structuring
response in ` ```json ... ``` ` markdown fences despite the system prompt
explicitly forbidding it — a real-world model behavior no mocked unit test could
have caught, since every existing test fed clean JSON straight to `json.loads`.
Confirmed via `docker compose logs` (Anthropic call succeeded, `json.loads` failed)
and a standalone diagnostic script hitting the live API directly.
Fix in `app/services/ai_structuring_service.py`, shared by both receipt and
statement structuring (`_call_and_parse_json`):
- **Primary defense**: seed the `messages` array with a trailing
  `{"role": "assistant", "content": "{"}` entry (Anthropic's standard "assistant-turn
  prefill" technique) so the response continues an already-opened JSON object —
  structurally very unlikely to be preceded by a fence. The prefilled `{` is
  manually prepended back onto the response text before parsing.
- **Belt-and-braces**: `_parse_json_response` strips leading and trailing markdown
  fences independently. A first draft only stripped the trailing fence when a
  leading fence was also present — dead code once the prefill guarantees no leading
  fence can appear at position 0 — caught by re-reading the logic before commit and
  fixed to strip each independently.
- Added `test_strips_markdown_fences_before_parsing`, simulating the realistic
  post-prefill shape (a stray trailing ``` after otherwise-valid JSON). Verified it
  actually catches the regression by temporarily reverting the trailing-fence fix,
  confirming the test failed with the exact original 502, then restoring and
  reconfirming green.
- Full backend suite: 140/140 passing. Re-ran the original live curl call
  post-fix: `200` with a correctly structured Costco receipt extraction (merchant,
  items, categories, confidence scores, and a mismatched-total warning all correct).
- Also required discovering that `docker compose restart` does **not** pick up
  `.env` changes — only `docker compose up -d --force-recreate` does, since
  `env_file` values are baked into the container at creation, not re-read on
  restart. Noted here since it'll bite again if any other secret is rotated.
- harness-os: `assess_risk` → medium (gated-path, no security/financial keyword
  match) → `record_decision` (decision 71, `pending_approval`, linked to decision
  54 as a remediation of that slice's implementation — no new spec needed, same
  endpoints/schema/behavior).

### Slice 2: Backend statement OCR (BIW-API-006, decisions 55-56)
- `POST /ocr/statement` (PRD §11.4 — credit card statement/bill OCR). Reuses slice
  1's `ocr_service.extract_text` unchanged (same local-Tesseract, magic-byte-routed,
  10MB/40s-bounded path) and a new `ai_structuring_service.structure_statement_text`
  with a statement-specific Claude Haiku prompt, extracting balance, statement/due
  dates, minimum payment, and line items for the user's reference.
- **Deliberately stateless, no confirm endpoint**: unlike receipt OCR, this slice
  adds no `/ocr/statement/confirm` — the PRD requires the extracted balance to
  always be a suggested update the user must explicitly confirm, and BillWise
  already has an endpoint that does exactly that (`PATCH /payment-methods/{id}`,
  which already supports `current_balance` and already validates ownership). The
  frontend (slice 3+, not yet built) will call that existing endpoint directly
  after the user reviews/edits the suggestion — no new write path was needed.
  Verified statelessness with a dedicated test (`test_never_writes_to_payment_methods`)
  confirming a payment method's `current_balance` is untouched by the scan call.
- **Proactive DRY refactor**: extracted `_read_and_validate_upload`/
  `_run_with_ocr_timeout` in `app/api/ocr.py` and `_call_and_parse_json` in
  `app/services/ai_structuring_service.py` out of the receipt path so both
  endpoints share the Content-Length pre-check, size/type validation, timeout
  wrapping, and sanitized-logging discipline instead of duplicating it.
- Security review: clean — confirmed all 5 of slice 1's fixes carry over correctly
  through the new shared helpers, confirmed statelessness. FastAPI review: two
  minor fixes — `_call_and_parse_json`'s bare `dict` return type tightened to
  `dict[str, Any]`; shared error-message wording ("enter this transaction
  manually") was misleading for the statement flow (which suggests a balance
  update, not a transaction) — reworded to caller-agnostic phrasing ("try again or
  enter this manually").
- 21/21 OCR tests passing (17 receipt+confirm, 4 statement), 139/139 full suite.

### Slice 3: Frontend Receipt Review screen + Scan Receipt entry point (BIW-INFRA-011, decisions 57-58)
- Extended the existing M3 Add Transaction screen (`frontend/app/add-transaction/page.js`)
  with a Manual Entry / Scan Receipt mode toggle rather than building a separate
  screen — PRD §24.4 frames manual/scan/statement-import as entry paths into one
  Add Transaction screen, not three screens. Scan mode: `ReceiptUploadPanel`
  (new, `frontend/components/receipt/ReceiptUploadPanel.js`) uploads a file to
  `POST /ocr/receipt`; on success the SAME form fields used for manual entry
  (date, merchant, total, payment method, line items) are pre-filled from the
  extraction and the screen enters a "scan-review" state — a warnings/status
  banner, per-line-item confidence badges, and every field stays editable before
  confirming (PRD §13.2). Confirming calls `POST /ocr/confirm-transaction`
  instead of `POST /transactions`. OCR failure/timeout shows an inline error with
  a link back to Manual Entry (PRD §13.3).
- AI-suggested category labels (plain text, e.g. "Food"/"Grocery") are resolved
  against the user's real category tree by case-insensitive name match
  (`resolveCategoryId`, subcategory match preferred); unmatched or "Uncategorized"
  items are left for manual selection (PRD §29.2).
- `frontend/lib/api.js`: added `ocrApi.scanReceipt`/`ocrApi.confirmTransaction`;
  refactored the shared error-handling logic into `throwIfError`, and added
  `requestMultipart` for the file-upload call (deliberately omits the JSON
  `Content-Type` header so the browser sets the multipart boundary itself).
- Security review: clean — confirmed OCR-derived data (an AI-derived, technically
  attacker-influenceable source since it comes from a user-uploaded image) only
  ever flows through auto-escaping JSX interpolation, never `dangerouslySetInnerHTML`;
  confirmed the new multipart upload path has the same same-origin/credentialed
  CSRF posture as the existing JSON path.
- React review: no blocking issues; fixed accessibility findings — `aria-pressed`
  on the mode-toggle buttons, `role="alert"` (was `role="status"`) on the
  one-time warnings banner, and a text qualifier ("— needs review") added to
  low-confidence badges so the signal isn't color-only (WCAG 1.4.1). Also fixed a
  robustness edge case: if the categories SWR fetch resolves after a fast scan
  completes, a new `useEffect` re-resolves any still-unmatched OCR line-item
  categories once categories arrive (previously the AI's suggested labels were
  used transiently and discarded, so nothing was left to re-resolve against —
  now `suggestedCategory`/`suggestedSubcategory` are stored on each line item).
- **Verified end-to-end via live Playwright** against the real dev server (not
  just unit-level): mode switching; a real upload hitting the real backend with
  no Anthropic key configured correctly surfaced the backend's graceful 503 and
  the frontend's fallback-to-manual link worked; a mocked successful extraction
  correctly pre-filled all fields, showed a 92%-match badge with auto-resolved
  category on a high-confidence item, left a 40%-confidence/"Uncategorized" item
  unselected requiring manual choice, and displayed the warnings banner;
  confirming created a real `Transaction` with `source='Receipt OCR'` and correct
  line items (checked directly via `psql`); a repeat scan of the same receipt
  correctly redirected with `?duplicate=1`, matching the manual-entry path's
  existing behavior. Manual-entry regression re-verified end-to-end (unaffected
  by the shared-form refactor). ESLint clean, production build clean. Test
  fixtures (payment method, transactions) cleaned up from the dev DB afterward.
- **This closes M5's originally-scoped work** (backend receipt OCR, backend
  statement OCR, frontend receipt scan/review). Statement-import frontend
  (PRD §11.4/§24.4 — a suggested-balance review UI calling the existing
  `PATCH /payment-methods/{id}`) remains PRD scope but is not yet slotted into a
  slice; flagged as queued follow-up below, not a gap in M5 itself.

### Statement-import frontend UI — DONE (BIW-INFRA-012, decisions 72-73)
Closes the queued follow-up from slice 2. A review screen on the Wallets page
(`frontend/app/wallets/page.js` + new `frontend/components/statement/StatementUploadPanel.js`):
an "Import statement" action on the active wallet opens an upload panel
(mirrors `ReceiptUploadPanel.js`'s pattern — file picker, 10MB client pre-check,
loading/error state), calls the new `ocrApi.scanStatement` → the existing,
unchanged `POST /ocr/statement` (BIW-API-006). On success, shows a review
screen: `statement_balance` as a pre-filled, user-editable number input (the
only field ever written back), `statement_date`/`due_date`/`minimum_payment`/
`items` shown read-only for reference (no matching `PaymentMethod` columns
exist for them), and a warnings banner shown verbatim when non-empty.
Confirming calls the existing, unchanged `PATCH /payment-methods/{id}`
(BIW-API-001) with only `{ current_balance: <edited value> }` — never
auto-applied. Cancel closes the panel with no write. `assess_risk` auto-critical
(financial keyword match: payment, wallet) → `create_spec` (`BIW-INFRA-012`) →
`record_decision` (72, pending).

**security-reviewer**: clean, no critical/high findings — XSS-safe (JSX
auto-escaping on OCR-extracted text), confirm requires a genuine user click,
client validation correctly non-load-bearing (backend owns real
validation/ownership).
**react-reviewer**: 2 HIGH (unstable list keys — warnings keyed by string text,
not guaranteed unique; items keyed by name+index) — fixed by switching both to
plain index keys (both arrays are immutable single-shot snapshots from one OCR
response, never reordered/filtered/mutated after render, so index keys are
safe here) with an explanatory comment. 1 MEDIUM (file input missing a visible
label) declined — consistent with the existing, already-reviewed
`ReceiptUploadPanel.js` convention (aria-label only).
Remediation recorded as decision 73, linked to 72.

**Verification**: ESLint clean, production build clean. Playwright-verified
end-to-end against the live Anthropic API with a real synthetic statement
image: uploaded → extraction shown (balance $842.15, dates, $35.00 minimum
payment, 3 items, and a due-date-anomaly warning correctly surfaced by the
model) → confirmed → `PATCH /payment-methods/{id}` fired → wallet balance
updated in the UI ($500.00 → $842.15) and confirmed directly via `psql`. Test
payment method cleaned up from the dev DB afterward.

## Milestone 6 Detail (Recurring Bills & Cashback)

### Slice 1: Backend Recurring Bills (BIW-DATA-004, BIW-API-007, decisions 76-77)
New `recurring_bills` and `recurring_bill_payments` tables (PRD §23.9-10) via
Alembic autogenerate + apply, migration `110bd6d5da2f`. `RecurringBill` holds
the bill definition (name/amount/frequency/category/payment method/toggles);
`RecurringBillPayment` holds each generated period instance (own due_date,
status, paid_date, optional linked `transaction_id`) — PRD §16.3's "real
multi-month payment history" requirement. Added `TransactionSource.RECURRING_BILL`
("Recurring Bill") enum value.

Endpoints (`app/api/recurring_bills.py`): `GET/POST /recurring-bills`,
`PATCH/DELETE /recurring-bills/{id}`, `POST /recurring-bills/{id}/mark-paid` —
exactly PRD §25.8's list, no extra endpoints added.

**Design interpretations made where the PRD is silent** (no contradiction, just
gaps — documented here for visibility, not blocking):
1. **Custom frequency never auto-generates** its next period — §16.2 lists
   'Custom' as a frequency option but §23.9's schema has no interval field to
   compute a next date from. The owner manually rolls it forward by editing
   `due_date`. Covered by `test_custom_frequency_does_not_auto_generate`.
2. **'overdue' is a real stored status** (matching §23.10's declared enum),
   materialized lazily by `ensure_recurring_bill_state` — same pattern as the
   existing `ensure_budget_rollover` in `budget_rollover.py` — run on every
   `GET /recurring-bills` and again after mark-paid. No background job/scheduler
   introduced anywhere in this project.
3. **No separate 'skip' endpoint** — §25.8 only lists mark-paid. `skipped` exists
   in the schema (schema-complete, matching §23.10) but has no PRD-specified
   trigger, so it isn't yet reachable via the API. Documented gap, not silently
   dropped.
4. **No separate recurring-bills dashboard endpoint** — `GET /recurring-bills`
   embeds each bill's `current_period` (nearest upcoming/overdue) plus its full
   `payments` history, so the frontend can aggregate "due this week/month, total
   obligation, missed/overdue" (§16.4) client-side — matching the Budgets/Goals
   precedent of client-side aggregation over a list endpoint.
5. **Card Payment Bills** (§16.5): `due_date` auto-populates from the linked
   payment method's `due_day_optional`/`statement_day_optional` only when the
   client omits `due_date` at creation (`resolve_card_payment_due_date`) — no
   new boolean flag added to the schema; the day is clamped to the target
   month's actual length and rolled to next month if already passed.
6. **mark-paid targets the bill's earliest non-terminal period** (upcoming or
   overdue) rather than a specific period id, since §25.8's endpoint is
   parameterized by bill id, not period id. Returns 409 if none exists (e.g.
   already paid, or custom-frequency bill with nothing left to pay).
7. Recurring bills require an **expense-type category** (`_validate_expense_category`)
   — no income/saving recurring inflows in scope, matching the feature's framing
   throughout §16.

`mark_bill_paid` optionally creates a real `Transaction` (source='Recurring
Bill') via the existing shared `create_transaction_record` service (same DRY
path used by OCR confirm and goal add-funds) when `auto_create_transaction` is
set, and links it back via the period's `transaction_id`.

### Security review (security-reviewer agent)
Clean — no critical/high findings. Ownership scoping correct on all 5 routes;
`auto_create_transaction` path re-validates payment-method/category ownership
via the existing `create_transaction_record`/`_validate_expense_category`
(can't be exploited to write transactions against another user's data);
amounts constrained `gt=0`; no injection risk (`.in_()` built from
already-owner-filtered ids); rate-limiting absence confirmed consistent with
`budgets.py`/`goals.py`/`transactions.py` (not a gap specific to this router).
One MINOR: `RecurringBillUpdate`'s NOT-NULL FK fields technically accepted an
explicit JSON `null`. Fixed — the router now rejects explicit `null` on any
not-nullable field (`payment_method_id`, `category_id`, `name`, `amount`,
`frequency`, `due_date`) with a clear 422, plus a regression test.

### FastAPI review (fastapi-reviewer agent) — fixed immediately
- **N+1 query in `list_recurring_bills`** (HIGH): payments were loaded per-bill
  in a loop. Fixed — batch-load all payments for the user's bills in one query,
  group in memory, matching the existing `transactions.py` pattern.
- **Redundant `session.refresh`** (MEDIUM) in `mark_bill_paid`: called again
  after `ensure_recurring_bill_state`, which never touches the just-paid
  period. Removed.
- **Missing `from_attributes` config** (LOW) on `RecurringBillPublic` for
  consistency with peer response schemas. Added.
- Confirmed correct outright: async session semantics throughout
  `ensure_recurring_bill_state` (single batched commit, no stale reads, no
  hidden N+1 in the reconciliation loop itself), Decimal serialization, the
  three-commit composition in `mark_bill_paid` (transaction creation → period
  update → state reconciliation) judged consistent with how this codebase
  already composes shared service calls elsewhere.

### Verification
28 new tests in `backend/tests/test_recurring_bills.py`: bill CRUD + ownership
404s, expense-category/payment-method validation, card-payment due-date
auto-population, `next_due_date` unit tests covering month-end clamping
(Jan 31 monthly → Feb 28) and leap-year yearly rollover (Feb 29 2028 → Feb 28
2029), lazy overdue-flip and next-period-generation on list, custom-frequency
non-generation, mark-paid with/without `auto_create_transaction` (including
confirming the linked transaction's `source`/amount via a follow-up
`GET /transactions`), 409 on an already-resolved bill, and the explicit-null
rejection added during remediation. Full backend suite: 168/168 passing, no
regressions.

### Slice 2: Backend Cashback (BIW-DATA-005, BIW-API-008, decision 78)
New `cashback_rules` and `cashback_records` tables (PRD §23.11-12), migration
`7241b1a664f5`. `CashbackRule.category_id` is nullable — null means "the
payment method's default rate" (§17.2), set means a category-specific
override that takes precedence when both are in effect for the same date;
among rules of equal specificity, the most recent `start_date` wins (§27.5:
"Rule changes mid-month → new rate applies going forward only"). No matching
rule → 0 (§27.5). Deliberately does **not** fall back to the pre-existing
`payment_methods.default_cashback_rate` column — that field stays display-only
(the Wallets card visual badge from M1); §27.5 is explicit that estimation
looks at rules alone.

Cashback is computed **per line item** (§17.3) and materialized into
`cashback_records` by `record_cashback_for_line_items`
(`app/services/cashback_service.py`), called explicitly from all three
existing `create_transaction_record` call sites — manual entry
(`POST /transactions`), OCR confirm (`POST /ocr/confirm-transaction`), and
recurring-bill mark-paid — plus `PATCH /transactions/{id}` when line items are
wholesale-replaced. Deliberately **not** baked into `create_transaction_record`
itself, keeping that shared foundational helper feature-agnostic rather than
reaching into a specific feature's concerns. **Not wired into Goal add-funds**,
which doesn't go through `create_transaction_record` at all (pre-existing M4
architecture) — documented gap, not silently dropped.

**Manual overrides persist correctly** (§27.5: "Manual override persists, not
overwritten by recalculation") without needing an extra override-tracking
field: `PATCH /cashback-records/{id}` writes directly, and nothing
recomputes an existing record unless its underlying `TransactionLineItem` is
wholesale-replaced (in which case the old record cascade-deletes via
`ondelete="CASCADE"` along with the line item, and a fresh one is computed for
the new item — no stale override can survive against a line item that no
longer exists). Editing a transaction's other fields (date, payment method,
total amount alone) leaves existing cashback records — including overrides —
untouched.

**Bug caught and fixed before review**: an initial attempt to reorder
`update_transaction`'s logic (to have `transaction.payment_method_id`/`date`
current before recomputing cashback) accidentally moved a `setattr` +
`session.add` ahead of a validation branch. A failed PATCH (422) could then
leak a partial write via SQLAlchemy's autoflush before the exception was ever
raised to the client. Caught immediately by
`test_updating_total_amount_alone_revalidates_against_existing_line_items`
failing; fixed by restoring validation-strictly-before-mutation ordering and
computing cashback only after the (unconditional, already-correct) final
commit+refresh.

`GET /cashback` (single flexible endpoint per §25.9's list — no separate
`/monthly`/`/yearly` variants unlike the Dashboard section) accepts
`year` + optional `month`, joins through `Transaction` (since
`CashbackRecord` has no date column) and aggregates by card/category in
Python — judged fine at this app's personal-finance scale rather than pushed
into a SQL `GROUP BY`.

**security-reviewer**: clean, no findings — ownership scoping correct on all 5
routes, rule creation validates payment-method/category ownership, no way to
smuggle unvalidated ids into a `CashbackRecord`, amounts/rate correctly bounded.
**fastapi-reviewer**: 1 MEDIUM — `record_cashback_for_line_items` commits in a
separate DB transaction from the one it computes cashback for (each call site
already committed the transaction before calling it). Accepted as a documented
residual risk rather than restructuring `create_transaction_record`'s commit
boundary across its 3 already-shipped call sites: the failure window is a rare
mid-request DB failure between two back-to-back commits, and the worst case is
a missing/zero cashback estimate, not corrupted financial data. 1 LOW — the
Python-side aggregation noted above, explicitly not worth fixing at this scale.

**Verification**: 25 new tests in `backend/tests/test_cashback.py` — rule CRUD
+ ownership 404s, rate-resolution edge cases (default vs. category-specific,
most-recent-wins, expired/future rules), auto-computation on transaction
create (including a zero-record case for Income and a zero-estimate case with
no matching rule), recompute-on-line-item-replacement, the manual-override-
persists-on-unrelated-edit case, record update, and summary aggregation by
month vs. year. Full backend suite: 193/193 passing, no regressions.

### Slice 3: Frontend Recurring Bills screen (BIW-INFRA-014, decisions 79-80)
New `frontend/app/recurring-bills/page.js` (net-new UI, no template equivalent
per PRD §9's screen inventory) — mirrors the existing `goals/page.js`
two-column nav+detail layout for visual consistency with the Ekash-derived
design system. `recurringBillsApi` added to `lib/api.js`; `remove()` maps to
the backend's soft-deactivate `DELETE` (no hard delete, no reactivate
endpoint) — presented in the UI as a confirmed, semi-irreversible action
rather than a reversible toggle. Sidebar nav entry added between Goals and
Profile.

Covers create/edit (pre-filled), the backend's not-nullable-field guard
surfacing cleanly as a 422, mark-paid (optional paid-date/amount overrides,
correctly re-rendering the lazily-generated next period), full per-period
payment history table, and deactivate with a `window.confirm` dialog
(matching the existing `goals`/`wallets` pages' pattern for destructive
actions).

**Two real bugs caught during my own live Playwright verification** (not by
a review agent — the react-reviewer subagent hit a weekly usage-limit wall on
both the initial attempt and a retry, so this slice's UI-correctness pass was
done by hand instead of delegated):
1. The create-form and detail-panel error banners shared one `formError`
   state, but the two panels render **simultaneously** (side-by-side columns,
   not toggled views) — an error from a detail-panel action (edit/mark-paid/
   deactivate) would leak into the create-form panel if it happened to be
   open at the same time, and vice versa. Fixed by splitting into `createError`
   and `detailError`, each cleared independently when its own panel is
   opened/reset.
2. Discovered while re-testing fix #1: FastAPI's Pydantic-validation 422
   `detail` is an array of `{loc, msg, type}` objects, not a string. The
   shared `ApiError` in `lib/api.js` passed that array straight to `Error`'s
   constructor, which stringifies it to the literal text `"[object Object]"`
   — a pre-existing, **app-wide** bug (every page using `error.message`
   inherits it for any raw Pydantic 422, as opposed to hand-written
   `HTTPException(detail="...")` strings, which were already fine). Fixed
   with a `formatDetail()` helper in `lib/api.js` that joins array-of-`msg`
   into a readable string; string details pass through unchanged. This is a
   shared-file fix with app-wide effect, scoped narrowly (one function, no
   behavior change for the already-working string case) — not deferred to a
   separate slice since it directly affects the correctness of the error
   surfacing this slice depends on.

**security-reviewer**: 1 CRITICAL (missing CSRF tokens on state-changing
requests), 1 MEDIUM (inconsistent URL query-param encoding in
`budgetsApi.list()`). Both assessed as out-of-scope/pre-existing, not new
gaps from this slice: the session cookie is already `set-cookie:
billwise_session=...; SameSite=lax` (set at login, app-wide, predates this
slice) — `SameSite=Lax` blocks cookies on cross-site fetch/XHR regardless of
method, which is the standard CSRF mitigation for cookie-auth SPAs and
already covers `recurringBillsApi`'s POST/PATCH/DELETE calls. The
query-param finding doesn't apply to this slice's new code either —
`recurringBillsApi` uses only path-segment UUIDs and POST/PATCH bodies, no
query strings. Neither finding blocks this slice; both are pre-existing,
app-wide, and out of scope for a targeted fix here.

**react-reviewer**: agent unavailable (weekly usage limit hit on two
consecutive attempts). Reviewed the diff by hand instead — hook usage,
`bill.id`/`period.id` list keys (no index-key usage anywhere), label/input
`htmlFor`/`id` pairing, and the `window.confirm` pattern (matches existing
`goals`/`wallets` precedent) all checked clean. The two bugs above were found
this way, not by an automated pass — recorded here as a known gap in this
slice's review coverage until harness-os/react-reviewer capacity resets.

**Verification**: `eslint` clean, production `npm run build` clean, live
Playwright pass covering create (including the empty-form and missing-due-
date 422 paths), select, edit pre-fill and 422 surfacing, mark-paid
(including auto-generated next-period re-render), payment history rendering,
and deactivate with confirm-dialog handling — all exercised against the real
backend, not mocked.

### Slice 4: Frontend Cashback screen (BIW-INFRA-015, decisions 81-82)
New `frontend/app/cashback/page.js` (net-new UI, no template equivalent).
Unlike the nav+detail layout used by goals/budgets/recurring-bills, this is a
dashboard-style page (matches PRD §17.4/§24.10's framing: "monthly/yearly
earned, by card, by category, redeemed, unredeemed estimate" — a summary
view, not a CRUD-per-item screen): a month/year period selector with a
monthly↔yearly toggle (reusing budgets/page.js's `changePeriod` pattern),
three stat tiles reusing the existing `.analytics-widget` class from
`app/analytics/page.js`, side-by-side by-card/by-category breakdown lists, a
by-transaction records table with inline manual-override editing (PATCH
`/cashback-records/{id}`), and a cashback-rules management section
(create/edit/delete).

**Backend gap found and filled**: PRD §25.9 lists 5 Cashback endpoints (`GET
/cashback`, `POST/PATCH/DELETE /cashback-rules`, `PATCH
/cashback-records/{id}`) but — unlike every other resource section in §25
(payment methods, categories, budgets, goals, recurring bills all have a GET
list route) — has no `GET /cashback-rules`. Without it, the already-built
PATCH/DELETE-by-id rule endpoints are unreachable from any UI: there's no way
to discover a rule's id. Added `GET /cashback-rules` to
`backend/app/api/cashback.py` (owner-scoped, mirrors `list_recurring_bills`'s
pattern exactly) — a pure additive gap-fill matching this app's established
REST shape, not scope creep or a PRD contradiction. 3 new backend tests
(`TestListCashbackRules`: auth required, lists only own rules, empty case).
196/196 backend tests passing (was 193; +3 for this endpoint, no regressions).

`cashbackApi` added to `lib/api.js` (`listRules/createRule/updateRule/
removeRule/updateRecord/summary`); `summary()` uses `URLSearchParams` rather
than the string-interpolation pattern security flagged as MEDIUM in the
pre-existing `budgetsApi.list()` (unrelated code, not touched here — but this
new method avoids replicating that pattern). Sidebar nav entry added between
Recurring Bills and Profile.

**Same bug class caught again, fixed before commit**: initially wrote a
single shared `ruleError` state rendered both inside the "Add rule" create
panel and inside whichever rule's inline edit view was open — but
`isRuleFormOpen` and `editingRuleId` are independent state, so both panels
can be on screen at once (verified live: opened the create form, then opened
an existing rule's edit form — both rendered simultaneously). An error from
either action would leak into the other panel. This is the identical mistake
made and fixed in M6 slice 3 (Recurring Bills' `formError` split) — caught
this time by the react-reviewer agent (which was unavailable for slice 3 due
to a usage-limit wall, but ran successfully here) rather than by my own
manual testing. Fixed by splitting into `createRuleError`/`editRuleError`,
each cleared when its own panel opens or is cancelled. Also fixed a smaller
related gap the reviewer flagged: `recordError` (for the by-transaction
inline override form — only one record can be in edit mode at a time here,
so no cross-panel leak was possible, but the error banner could persist with
no attached form after clicking Cancel) — now cleared on cancel too.
Re-verified live post-fix: reproduced the exact concurrent-panel scenario
(create form open + a rule's edit form open, edit form's rate pushed to 150%
via bypassing the `max="100"` HTML constraint to reach the real backend 422)
and confirmed the error now renders only in the edit panel, never in the
create panel.

**security-reviewer**: clean, no findings on either the new backend endpoint
(ownership scoping verified) or the frontend (React auto-escaping covers all
user-controlled rendering; `cashbackApi.summary()`'s `URLSearchParams` usage
called out as the preferred pattern; no client-side trust of ids; amount
bounds enforced server-side via existing `ge=0` schema constraints).

**Verification**: `eslint` clean, production `npm run build` clean, live
Playwright pass covering rule create/edit(payment-method-locked during
edit)/delete-with-confirm-cancel, a real transaction generating a correctly-
computed cashback record end-to-end through the existing auto-computation
service, the manual-override flow updating the record and all three
aggregates (stat tiles, by-card, by-category) together, the monthly/yearly
toggle, and the error-isolation fix described above — all exercised against
the real backend, not mocked.

## Milestone 7 Detail (Net Worth, AI Insights, Household & Exports)

### Slice 1: Backend Net Worth (BIW-DATA-006, BIW-API-009, decisions 83-84)

**PRD gap found and filled**: PRD §25 has no dedicated Net Worth CRUD
section — only `GET /dashboard/net-worth` is listed under §25.10 — despite
§24.11 explicitly requiring "manual asset/liability entry" and a "monthly
snapshot". Designed the full CRUD API from scratch by pattern-matching every
other resource's shape in §25 (payment methods, categories, budgets, goals,
recurring bills): `GET/POST /net-worth-accounts`, `PATCH/DELETE
/net-worth-accounts/{id}`, `POST/GET /net-worth-snapshots`. This is a
gap-fill, not scope creep — same category as M6's `GET /cashback-rules` fill.

New tables (`backend/app/models/net_worth.py`): `net_worth_accounts`
(user-owned, `asset`/`liability` type, soft-deactivate via `is_active`),
`net_worth_snapshots` (point-in-time `total_assets`/`total_liabilities`/
`net_worth` + optional notes), `net_worth_balances` (per-account balance
within a snapshot, cascade-deletes with either parent). Plain `Decimal`
fields, no explicit precision — matches `budget.py`/`recurring_bill.py`
convention (initially over-specified with `max_digits`/`decimal_places`,
corrected before running anything).

**Design decision**: `POST /net-worth-snapshots` requires the submitted
`balances` list to *exactly* match the user's currently-active accounts —
every active account must have a balance entry, and no unknown/inactive
account IDs are accepted — returning 422 otherwise with a detail message
listing which accounts are missing/unknown. Rationale: a partial snapshot
would silently understate net worth, which the PRD's simple
Total-Assets-minus-Total-Liabilities framing (§18.7) doesn't intend.
Deactivating an account removes it from the required set for future
snapshots (a closed account shouldn't block snapshotting going forward).

`GET /dashboard/net-worth` added to the existing `backend/app/api/dashboard.py`
(consistent with that file's other aggregation endpoints): returns current
net worth, total assets/liabilities, change vs. the previous snapshot
(`None` if fewer than 2 snapshots exist), a breakdown of the latest
snapshot's per-account balances, and the full snapshot history. Shares a
`load_balances_by_snapshot()` batch-loading helper with
`GET /net-worth-snapshots` (in `net_worth.py`) to avoid N+1 queries and to
avoid duplicating the snapshot-to-schema conversion logic between the two
routers.

23 new tests (`backend/tests/test_net_worth.py`): auth-required on every
endpoint, account CRUD (create asset/liability, reject invalid type, list
excludes deactivated, update rejects clearing required fields, 404 for
other users' accounts and for deactivated accounts), snapshot validation
(no active accounts → 422, missing account → 422 naming it, unknown account
→ 422 naming it, deactivated accounts excluded from the required set),
correct asset/liability aggregation math, snapshot listing ordered by date
and scoped to the owner, and dashboard aggregation (empty state, two-snapshot
change calculation, single-snapshot `null` change). 219/219 backend tests
passing (was 196; +23 for this slice, no regressions).

**Security review (security-reviewer agent)**: raised one HIGH finding —
`NetWorthBalanceInput.balance: Decimal` has no explicit constraint, and
Pydantic's `Decimal` type was claimed to accept `"Infinity"`/`"NaN"` string
input, which could corrupt snapshot totals. Verified empirically against
this app's actual Pydantic version (2.13) with a throwaway script: `Decimal`
fields already reject non-finite values by default via Pydantic's built-in
`finite_number` validator (`Infinity`, `-Infinity`, `NaN`, `inf` all raise a
422 validation error out of the box). False positive — no code change
needed; documented rather than blindly patched.

**FastAPI review (fastapi-reviewer agent) — fixed immediately**: MEDIUM —
`dashboard.py` was importing an underscore-prefixed "private" helper
(`_to_snapshot_public`) from `net_worth.py`, breaking that module's privacy
convention and creating a hidden cross-module dependency (no other router in
this codebase imports from another router's internals). Fixed by renaming
to a public `to_snapshot_public`, since the cross-module reuse itself is
legitimate here (it avoids duplicating snapshot-to-schema conversion logic
between the snapshot-list and dashboard endpoints) — the fix was to make the
already-intentional sharing explicit, not to eliminate it. Re-ran the full
suite after the rename: 219/219 still passing.

Formally `pending_approval` pending human-ack (decisions 83-84).

### Remaining M7 slices (not yet started)
- Slice 2: Frontend Net Worth screen
- Slices 3-4: AI Insights backend + frontend
- Slices 5-6: Household backend + frontend (partner invite/accept/revoke/
  permissions endpoints; every existing endpoint in this codebase is
  currently `require_owner`-only, so a household-scoping auth dependency
  plus partner-scoped read filtering will be needed for the already-built
  `is_shared` toggles on Category/SavingsGoal to have any effect — full
  adversarial authorization testing is explicit M9 scope per the PRD's own
  milestone split, not M7's)
- Slices 7-8: Export backend + frontend (CSV/Excel/PDF via short-lived
  signed URLs per PRD §20.4)

## Milestone 1 Detail

### Specs registered
- `BIW-PROD-001` (product) — BillWise MVP
- `BIW-DOM-001` (domain) — Auth, Household & Payment Method Aliases, incl.
  `UserEmailVerification` and `UserAccountLifecycle` state machines
- `BIW-DATA-001` v2 (data) — users, partner_permissions, payment_methods,
  categories, email_verification_tokens, password_reset_tokens
- `BIW-API-001` (api) — auth (7 endpoints), payment-methods (5), categories (5)
- harness-os `new-feature` workflow run id 1: spec → risk (critical, CONST-ARCH-001
  keyword match on "payment") → tests. `assess_risk` decision recorded as
  `pending_approval` (id 1) — **needs a human `harness approve` / ack**, see
  "Outstanding human actions" below.

### Backend — DONE
- [x] FastAPI app skeleton (`backend/app`), async throughout (SQLAlchemy async
      engine + `sqlmodel.ext.asyncio.session.AsyncSession`) — see design decision below
- [x] SQLModel models: User, EmailVerificationToken, PasswordResetToken,
      PartnerPermission, PaymentMethod, Category
- [x] Alembic migration `d314e6dcf34f_init_schema` — applied to real Postgres via
      `docker compose run --rm backend alembic upgrade head`
- [x] Auth endpoints: register, verify-email, login, logout, me,
      password-reset/request, password-reset/confirm — all cookie-session based
- [x] Password hashing (argon2), slowapi rate limiting on login (5/min) and
      password-reset/request (3/hour)
- [x] Default category seed (PRD §10), seeded on register
- [x] Payment-methods CRUD (owner-only per §21.4), extra="forbid" schemas enforce
      PRD §11.1's forbidden-fields list mechanically (422 on cvv/card_number/etc.)
- [x] Categories CRUD + sharing toggle; partner list view filtered to
      `is_shared=true` scoped to their inviting owner
- [x] pytest integration tests, real Postgres via docker-compose (not mocked):
      38 passing (16 auth, 11 payment-methods, 11 categories)
- [x] Manually verified end-to-end via curl against the live `backend` service +
      real `db` container: register → console-logged verify link → verify-email →
      login (session cookie set) → /auth/me → /categories (22 seeded rows) →
      confirmed `role`/`category_type` persisted as lowercase values matching the
      data spec's check-constraint values, not enum member names (see below)

### Frontend — auth pages done, rest is M2
- [x] `frontend/` copied from `template/ekash` (unmodified template preserved
      separately under `template/` for reference)
- [x] `lib/api.js` — thin fetch wrapper (`credentials: "include"` for the
      httpOnly session cookie, `ApiError` carrying HTTP status + backend detail)
- [x] `/signin` rewired to real `POST /auth/login` (also fixed a template bug:
      password `<input>` was `type="text"`, now `type="password"`)
- [x] `/signup` rewired to real `POST /auth/register`, redirects to
      `/verify-email?email=...` on success
- [x] `/verify-email` rewired to consume `?token=` and call
      `POST /auth/verify-email`, with pending/verifying/verified/failed states
      (previously a fully static page)
- [x] Rebrand pass — started: `layout.js` metadata (title/description), "Welcome
      to Ekash" → "Welcome to BillWise" on signin/signup, root link `/index` →
      `/`. **Not done**: the other ~40 template screens (dashboard mock data,
      sidebar branding/logo image, favicon, the rest of §9 template mapping) —
      that's the bulk of M2, out of scope for this pass.
- [ ] Everything else in PRD §9 (de-mock dashboard, remove §9.5 forbidden
      screens, mobile bottom-nav, full rebrand) — M2 proper, not started

### Infra — DONE for M1, frontend Dockerfile added but unverified
- [x] `docker-compose.yml`: postgres (`db`), `backend` — both verified working
- [x] `frontend` service added to `docker-compose.yml` + `frontend/Dockerfile`
      for deployment parity (PRD §7.7), but **not yet built/run** — this session
      iterated on the frontend via native `npm run dev` for faster reload cycles
      during Playwright verification; the Docker path should get a real build
      check before anyone relies on it
- [x] `backend/.env.example` (committed) + `backend/.env` (gitignored, local dev
      values only); same pattern for `frontend/.env.example` + `frontend/.env.local`
- [x] `docker/postgres-init/01-create-test-db.sql` creates `billwise_test` so the
      integration suite never touches dev data

### Verification — DONE for M1 backend, frontend partially verified
- [x] `docker compose run --rm backend pytest` → 40 passed (38 + 2 added for the
      password-complexity rule from the security review)
- [x] Real end-to-end curl flow against `docker compose up backend` + real
      Postgres (register → verify → login → me → categories, all the way down
      to confirming correct lowercase enum values via raw `psql`)
- [x] Frontend dev server boots (`npm run dev`, port 3000), `/signin` returns 200
- [x] **Playwright browser verification — DONE** (user installed Chrome via
      `sudo env "PATH=$PATH" npx playwright install --with-deps chrome`). Full
      flow driven through real Chrome: signup form (rebrand text confirmed:
      "Welcome to BillWise") → real `POST /auth/register` → redirected to
      `/verify-email` → grabbed the console-logged link → verify-email page →
      "Your email is verified." → signin → real `POST /auth/login` →
      **landed on `/` (dashboard shell)**, screenshotted
      (`dashboard-after-login.png`). Zero console errors throughout.
- [x] **Cross-origin cookie behavior — confirmed working** in a real browser:
      `fetch(..., {credentials:"include"})` from `localhost:3000` to
      `localhost:8000` with the `SameSite=Lax` httpOnly cookie round-tripped
      correctly (login → landed authenticated on `/`, no manual cookie
      handling needed). The earlier open question is resolved.

### Bug found and fixed via Playwright (verification loop caught a real bug)
4. **Duplicate email-verification call raced its own success** — React 18
   Strict Mode double-invokes effects in dev, so `/verify-email`'s
   `useEffect` fired `POST /auth/verify-email` twice for the same token. The
   backend correctly accepted the first call (200, token marked used) and
   rejected the second (400, already used) — but the *second* response resolved
   after the first and overwrote React state, so the UI showed "invalid or
   expired" even though verification had genuinely succeeded. Caught by
   comparing the backend audit log (`user.email_verified` fired once, 200 OK)
   against what Playwright saw on screen (a "failed" state) — the two
   disagreed, which is what exposed it. Fixed with a `useRef` guard so the
   verify call only ever fires once per token
   (`frontend/app/verify-email/page.js`), regardless of how many times the
   effect re-runs. Re-verified with a fresh registration: exactly one
   `POST /auth/verify-email` in the logs, UI correctly showed "Your email is
   verified."

### Known gap surfaced by verification, not yet fixed (real, not hypothetical)
- **No frontend auth guard on `/` (dashboard)** — confirmed via
  `curl localhost:3000/` returning 200 with no session cookie at all. Harmless
  *today* only because the page still renders 100% hardcoded Ekash template
  mock data (nothing real is fetched client-side yet). This becomes a real
  unauthenticated data-exposure bug the moment M2 wires real user data into
  this page — an auth guard (redirect-to-`/signin`-on-401, checked via
  `GET /auth/me`) must land *before* or *alongside* that, not after. Tracked
  as a hard prerequisite at the top of the M2 checklist below, not just a
  footnote.

### Bugs caught and fixed during this milestone (verification loop working as intended)
1. **Naive vs. aware datetime comparison** (`TypeError` on token expiry checks) —
   SQLModel defaulted timestamp columns to non-tz `DATETIME` instead of the
   `timestamptz` the data spec calls for. Fixed via a shared
   `required_timestamp_field`/`optional_timestamp_field` helper
   (`app/models/_common.py`) using `sa_column=Column(DateTime(timezone=True))`.
2. **Enum values stored as Python member names, not values** — SQLAlchemy's default
   native-enum behavior stores `.name` (`'OWNER'`) unless told otherwise, which
   silently diverged from `BIW-DATA-001`'s declared check-constraint values
   (`'owner'`). Tests didn't catch it (Pydantic serializes enums by `.value`
   regardless of what's in the DB) — only caught by inspecting the autogenerated
   Alembic migration and confirming with a raw `psql` query post-apply. Fixed via
   `enum_field()` helper using `values_callable`.
3. **TOCTOU race in `/auth/register`** (found in a post-hoc staff-engineer-style
   self-review, not by a failing test) — the duplicate-email pre-check and the
   insert weren't atomic, so two concurrent registrations for the same email
   could both pass the check and the second would hit an unhandled
   `IntegrityError` (500) instead of a clean 409. Fixed by catching
   `IntegrityError` around the commit and translating it to 409 — the unique
   constraint on `users.email` is the real source of truth; the pre-check is
   just a fast path. Deliberately did not add a dedicated concurrency test: the
   test suite's session fixture shares one `AsyncSession`/transaction across the
   whole test for fast rollback-based isolation, which can't faithfully
   simulate two independent concurrent DB connections racing — doing so properly
   would mean diverging from that fixture for one low-probability MVP-scale
   edge case, judged not worth it right now.
4. **Stale Docker state** (containers + a named volume) left over from a prior,
   already-wiped session — blocked fresh `docker-compose up` on port and
   credential conflicts. Removed with explicit user confirmation before
   proceeding (see Environment Notes).

### Security review (security-reviewer agent, 2026-07-30)
Full review against the CONST-ARCH-001 required gate. All 38 (now 40) tests still
green after fixes. Summary — fixed immediately vs. deferred:

**Fixed now:**
- JWT algorithm hardcoded to `HS256` as a module constant (`core/security.py`)
  instead of a settings-driven value — removes an unnecessary injection surface.
- Password complexity: require ≥1 letter and ≥1 digit (`schemas/auth.py`), with
  tests for both missing-digit and missing-letter cases.
- CORS/`FRONTEND_BASE_URL` startup validation — rejects empty/`*` origin, since
  CORS here is credentialed (`allow_credentials=True`).
- Startup warning (not hard fail — stays dev-friendly) when `SECRET_KEY` matches
  the checked-in placeholder value, so a forgeable-token deployment is loud, not
  silent.
- Lightweight structured audit logging (`core/audit.py`, logger
  `billwise.audit`) for register/verify/login success+failure/logout/password-reset
  request+confirm — not the persisted `audit_logs` table from PRD §22.3 (that's
  explicitly M9 scope) but nothing security-relevant is unobserved in the meantime.

**Deferred to M9 (Security Hardening) with rationale, not silently dropped:**
- Persisted `audit_logs` table + query/export UI (PRD §22.3, §25 — full milestone).
- Session/token revocation (blacklist) — MVP's 7-day JWT expiry is an accepted
  MVP tradeoff; single-household risk profile.
- Rate-limiter's `X-Forwarded-For` trust — irrelevant until behind a real proxy.
- Password-reset timing side-channel — negligible with the console email backend;
  revisit once real SMTP is wired up.
- Partner `invited_by_user_id` assumes exactly one inviter — fine until M7's
  actual invite flow exists to test against.

**Not applicable / already mitigated:** IDOR (owned-or-404 pattern already
correct — reviewer confirmed), SQL injection (parameterized via SQLAlchemy
throughout), UUID enumeration (128-bit space, already low risk).

### Outstanding human actions
- **`harness.config.json` reconciliation** (optional): see Environment Notes — the
  mechanical CONST-CORE-001/002 gate doesn't currently cover `backend/**/*.py` or
  any frontend path, and the host-side test-run recorder can't execute the
  Docker-wrapped pytest command. A human can update `testCommands`/`gatedGlobs`
  and run `harness reconcile-config` if tighter mechanical enforcement is wanted.
- **M4 (all 4 slices) approved 2026-07-31** via `harness approve` — decisions 37-44
  all have matching `approve_decision` log entries. ✅
- **M3 + Wallets-restyle decisions still awaiting human-ack**: decisions 31
  (M3 backend assess_risk+spec), 32 (M3 backend review remediation — N+1 fix,
  category filter pushed into SQL, missing index, 5 new tests), 33 (M3 frontend
  assess_risk+spec), 34 (M3 frontend review remediation — SWR cache-key fix, stable
  line-item keys), 35 (Wallets restyle assess_risk+spec), 36 (Wallets restyle review
  remediation — both reviews clean) are still `pending_approval` under
  CONST-ARCH-001. Required reviews have already run for every one of these and all
  findings are fixed and re-verified. Not blocking further work, just outstanding.
- **M5 (all 3 slices + bugfix + statement-import UI) decisions awaiting human-ack**:
  decision 53 (backend receipt OCR + confirm-transaction assess_risk+spec), 54
  (slice 1 review remediation), 55 (backend statement OCR assess_risk+spec), 56
  (slice 2 review remediation), 57 (frontend Receipt Review screen
  assess_risk+spec), 58 (slice 3 review remediation), 71 (markdown-fence
  JSON-parsing bugfix, linked to 54), 72 (statement-import UI assess_risk+spec),
  73 (statement-import UI review remediation, linked to 72) — see "Milestone 5
  Detail" above for the full list of security/fastapi/react findings fixed,
  "Post-M5 bugfix" for decision 71, and "Statement-import frontend UI" for
  decisions 72-73 — are all `pending_approval` under
  CONST-ARCH-001.
- **Wallets enhancement decisions awaiting human-ack**: decision 74 (assess_risk+spec,
  `BIW-INFRA-013`), 75 (review remediation, linked to 74) — see "Wallets enhancement"
  above — are `pending_approval` under CONST-ARCH-001.
- **M6 slices 1-4 (backend Recurring Bills + Cashback, frontend Recurring
  Bills + Cashback) decisions awaiting human-ack**: decision 76
  (assess_risk+spec, `BIW-DATA-004`/`BIW-API-007`), 77 (slice 1 review
  remediation, linked to 76), 78 (slice 2 — assess_risk+spec
  `BIW-DATA-005`/`BIW-API-008` + review remediation combined), 79 (slice 3 —
  assess_risk+spec `BIW-INFRA-014`), 80 (slice 3 review remediation, linked
  to 79 — the react-reviewer agent hit its weekly usage limit on both
  attempts during this slice, so the two bugs it would likely have caught
  were instead found and fixed via manual Playwright verification; this
  decision was recorded retroactively after the harness-os MCP server
  reconnected mid-session), 81 (slice 4 — assess_risk+spec `BIW-INFRA-015`,
  also recorded retroactively since the server was disconnected for this
  slice's entire implementation), 82 (slice 4 review remediation, linked to
  81 — react-reviewer was available again this slice and caught the
  identical shared-error-state bug class as slice 3's decision 80) — see
  "Milestone 6 Detail" above — are `pending_approval` under CONST-ARCH-001.
- **M7 slice 1 (backend Net Worth) decisions awaiting human-ack**: decision 83
  (assess_risk+spec, `BIW-DATA-006`/`BIW-API-009` — assess_risk returned
  `critical` on a false-positive keyword match, "payment" appearing in an
  unrelated clause of the risk description) and 84 (slice 1 review
  remediation, linked to 83 — security-reviewer's one HIGH finding was a
  verified false positive, fastapi-reviewer's one MEDIUM finding was fixed)
  — see "Milestone 7 Detail" above — are `pending_approval` under
  CONST-ARCH-001.
- Run `docker exec -it harness_gate_daemon node cli/dist/approve.js <id>` for each
  outstanding decision, or batch through them — M1, M2, and M4's decisions were all
  approved this way already.
