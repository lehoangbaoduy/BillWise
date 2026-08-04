# BillWise — Post-Launch Fixes & Feature Batch PRD (v2)

## 1. Purpose & Relationship to the MVP PRD

This is a **separate, standalone PRD** — it does not edit or get appended to `prd/billwise-prd-final.md`. That document remains the historical record of the MVP as originally specified and shipped. This document governs the next batch of work: bug fixes and new features requested **after** the product was delivered to clients and is in real use.

Where an item here changes or reverses a decision from the original PRD, that is called out explicitly as **Supersedes §X** so the two documents don't silently disagree with each other over time.

This batch was scoped through direct codebase investigation (not assumptions) plus a clarifying-question pass with the product owner. Every technical claim below is grounded in the actual current code — file paths and line references are given throughout so implementation can start without re-discovery.

---

## 2. Scope Summary

| # | Item | Area | Phase | Type |
|---|------|------|-------|------|
| 1 | Categories trash icon red-square overflow | Frontend/CSS | 0 | Bug |
| 2 | Transaction History delete modal positioning | Frontend/CSS | 0 | Bug |
| 3 | Recurring bill "Mark Paid" → "Failed to fetch" (**confirmed: CORS**) | Infra/Deployment | 0 | Bug |
| 4 | Cashback doesn't auto-apply for matching merchant | Backend | 0 | Bug |
| 4b | Monthly Expenses Breakdown chart doesn't clear after all transactions deleted | Frontend | 0 | Bug |
| 5 | Invited partner cannot log in (**likely same root cause as #3**) | Infra/Deployment | 0 | Bug |
| 6 | Sign-in redirects back to login (**likely same root cause as #3**) | Infra/Deployment | 0 | Bug |
| 6b | Inline delete (trash icon) on Budget/Goal/Recurring Bill list rows | Frontend | 0 | Feature (UX) |
| 7 | Private data model for Wallet/Budget/Goal/Recurring Bill | Full-stack | 1 | Architecture change |
| 8 | Mobile native camera capture for receipt scan | Frontend | 2 | Feature |
| 9 | OCR-fail fallback: retain receipt image, minimal manual entry, thumbnail + modal in Transaction History | Full-stack | 2 | Feature |
| 10 | Reimbursement transaction type + "mark paid by" + notification | Full-stack | 2 | Feature |
| 11 | Transaction cost-split ("Share") feature | Full-stack | 2 | Feature |
| 12 | "Type" filter on Transaction History | Frontend | 2 | Feature |
| 13 | OCR: exclude discounts/credits from line items | Backend | 2 | Bug/Feature |
| 14 | Budget list shows usage/total (like Goals) | Frontend | 3 | Feature |
| 15 | Budget auto-renewal on the 1st of the month | Backend/Infra | 3 | Feature (behavior change) |
| 16 | Remove AI Insights | Full-stack | 4 | Removal |
| 17 | PWA "Add to Home Screen" icon | Frontend | 5 | Bug |

Phases are ordered by dependency and risk, not necessarily by calendar priority — see §18.

---

## 3. Non-Goals (this batch)

* No redesign of the household/partner model beyond what §7 requires (owner/partner roles, invite flow shape, and `PartnerPermission` stay as-is).
* No offline support, service worker, or install-prompt banner for the PWA fix (§10) — icon only, per explicit decision.
* No multi-currency, no bank-sync/Plaid-style live account linking — unchanged from the original PRD's non-goals.
* No general-purpose notification infrastructure overhaul — the new reimbursement notification (§7.4) reuses the existing computed-on-request pattern plus a scheduled job, not a new subsystem.
* The cost-split "Share" feature (§7.5) is scoped to owner + partner(s) already in the household — it does **not** introduce arbitrary external "users" to share with.

---

## 4. Governance & Implementation Process

Per direction: all work in this batch is to be executed through the **harness-os MCP workflow** — Constitution → Specification → Test Suite → Generate Code → Code Review — rather than ad hoc implementation, using the `mcp__harness-os__*` tools already available in this environment (`create_spec`, `validate_spec`, `generate_tests`, `run_workflow`, `request_review`, `impact_analysis`, `record_decision`, `trace_artifact`, `audit_report`, `assess_risk`).

**Current state (checked before writing this PRD):** this project has **no constitution registered yet** — neither a project-local one under `.claude/constitution/*.md` nor a global one. `get_constitution` currently returns nothing to enforce. This means:

1. **Step 0, before any feature work in this batch starts:** establish a project-local constitution for BillWise (`.claude/constitution/*.md`) that encodes, at minimum, the standards already implicitly enforced in this codebase — the household-scoping/authorization pattern (`household_owner_id`, `require_owner_or_co_owner`), the "no forbidden financial fields" rule (§22.1 of the original PRD), the receipt-image never-persisted rule (§22.4), and the ECC rules already governing this session (test coverage, no hardcoded secrets, etc.). Without this, "Constitution → Specification" has no constitution to start from.
2. **Per feature/phase**, register a spec via `create_spec` (type `domain`, `api`, or `data` as appropriate — e.g. a `data` spec for the private-flag schema change in §7, an `api` spec for the new Reimbursement endpoints in §7.4) before writing code, and `validate_spec` it.
3. Use `generate_tests` against the registered spec to produce the test suite **before** implementation (this repo already has a `backend/tests/` suite per feature area — `test_budgets.py`, `test_cashback.py`, etc. — new specs should extend that pattern, not replace it).
4. Only then generate/write code, and close the loop with `request_review` before merge. `impact_analysis` should be run before touching the private-data model in §7 specifically, given how many existing endpoints read through `household_owner_id`.

This section is process guidance for whoever implements this PRD — it does not change any of the functional requirements below.

---

## 5. Phase 0 — Bug Fixes

These are independent, low-risk, and should ship first since none of them depend on the architecture change in Phase 1.

### 5.1 Categories trash icon overflow

**File:** `frontend/app/settings-categories/page.js` (delete button, ~lines 33–41), likely combined with `frontend/components/elements/ConfirmButton.js`'s `confirm-popover-anchor` wrapper span.

**Current behavior:** the delete button uses Bootstrap's `btn-outline-danger` with a `fi fi-rr-trash` icon. The button's red background/hover state visually extends past the rounded border, producing a squared-off red overflow instead of staying contained within the button's rounded corners.

**Requirement:** the red hover/active background must respect `border-radius` and `overflow: hidden` (or equivalent) so the fill never extends past the button's visible border, at all viewport widths and in both light/dark themes.

**Acceptance criteria:**
* Hover, focus, and active states on the trash icon button stay fully inside the button's rounded border in both themes.
* No regression to `ConfirmButton`'s popover positioning (§5.2 covers that separately).

### 5.2 Transaction History delete modal positioning

**File:** `frontend/components/elements/ConfirmButton.js`, used from `frontend/app/analytics-transaction-history/page.js` (~lines 46–54).

**Confirmed via clarifying question:** this is a **visual/positioning bug**, not a functional/data bug — the underlying delete call and state reset are correct.

**Requirement:** audit `ConfirmButton`'s popover anchoring across breakpoints (320/768/1024/1440px per the standard test set) for:
* Clipping at the edges of the viewport or the table's scroll container (a likely cause on the Transaction History page specifically, since it's the one wide-table context in the app).
* Overlap with adjacent table rows/action buttons when triggered from rows near the top or bottom of the visible table.
* Incorrect anchor point on mobile widths where the row layout differs from desktop.

**Acceptance criteria:**
* Popover stays fully visible (never clipped by table overflow or viewport edges) at 320, 768, 1024, and 1440px, for rows at the top, middle, and bottom of the visible table.
* Popover closes correctly on outside click/Escape without a layout jump (existing behavior — must not regress).

### 5.3 Recurring bill "Mark Paid" → "Failed to fetch" — CONFIRMED: CORS misconfiguration

**Files:** `frontend/app/recurring-bills/page.js` (~line 269) → `frontend/lib/api.js` (~line 163, `markPaid`) → `backend/app/api/recurring_bills.py` (~lines 207–218, `mark-paid` route) → CORS middleware in `backend/app/main.py` (~lines 34–43) → `settings.frontend_base_url` in `backend/app/core/config.py` (~line 27).

**Root cause confirmed** by the actual browser console error captured in production:

```
Access to fetch at 'https://billwise-1et2.onrender.com/recurring-bills/10c767f2-3a45-4bae-ba8e-aa26c3b39e59/mark-paid'
from origin 'https://bill-wise-alpha.vercel.app' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

This is a **deployment configuration bug, not a code bug.** The backend's CORS middleware is configured as:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_base_url],
    allow_credentials=True,
    ...
)
```

`frontend_base_url` defaults to `http://localhost:3000` and must be set via the `FRONTEND_BASE_URL` environment variable in the Render deployment. The error confirms the Render backend is not currently sending an `Access-Control-Allow-Origin` header for `https://bill-wise-alpha.vercel.app` — meaning the deployed `FRONTEND_BASE_URL` on Render either isn't set, is stale, or doesn't exactly match the live Vercel origin (protocol, host, and no trailing slash must match exactly; CORS is not a prefix or substring match).

**There is a second, compounding risk in the same deployment pair.** This codebase's own config comment (`backend/app/core/config.py`, `cookie_samesite` field) already documents the exact gotcha at play here:

> "Cross-site deployments (e.g. Vercel frontend + Render backend, different registrable domains) need `'none'` — browsers never attach a Lax cookie to cross-site fetch/XHR (only to top-level navigations), so auth would silently fail past login."

`bill-wise-alpha.vercel.app` and `billwise-1et2.onrender.com` are exactly this case — different registrable domains, i.e. a cross-site deployment. `cookie_samesite` defaults to `"lax"`. **Both `COOKIE_SAMESITE=none` and `COOKIE_SECURE=true` must be explicitly set in the Render production environment** for session cookies to be sent on any cross-site API call at all — independent of the CORS fix above, and required together (the app's own validator rejects `SameSite=None` without `Secure=true`).

**Fix (infrastructure/config, not application code):**
1. In the Render backend's environment configuration, set `FRONTEND_BASE_URL=https://bill-wise-alpha.vercel.app` exactly (verify protocol and no trailing slash), and redeploy/restart so the process picks up the new value (`Settings` is read once at process startup).
2. In the same environment, explicitly set `COOKIE_SAMESITE=none` and confirm `COOKIE_SECURE=true` (already the default).
3. If more than one frontend origin needs access (e.g. a Vercel preview-deployment domain in addition to production), `allow_origins=[settings.frontend_base_url]` only supports a single hardcoded origin today — extend `Settings`/CORS setup to accept a comma-separated list of allowed origins if that's needed, rather than working around it with a wildcard (incompatible with `allow_credentials=True` per the existing validator's own comment).

**Acceptance criteria:** the exact CORS error above no longer occurs for mark-paid from `https://bill-wise-alpha.vercel.app`; verified against the live Render/Vercel deployment (not just localhost, which would never have reproduced this class of bug).

### 5.3b Monthly Expenses Breakdown chart doesn't clear after all transactions are deleted

**File:** `frontend/app/page.js` (dashboard), `Monthly Expenses Breakdown` card (~line 220 heading, chart render ~lines 222–226), backed by `GET /dashboard/category-breakdown` (`backend/app/api/dashboard.py`, ~lines 326–350).

**Root cause confirmed by reading both sides:** the donut chart's empty-state check is:

```javascript
{topCategories.length > 0 ? (
    <DashboardCategoryDonut ... />
) : (
    <EmptyState ... />
)}
```

`topCategories` is derived from `categoryBreakdown`, the response of `/dashboard/category-breakdown`. That endpoint deliberately includes **budgeted categories with zero actual spend** as zero-amount rows — by design, so a "$0 spent of $50 budgeted" comparison is possible elsewhere on the page:

```python
zero_spend_budgeted_ids = set(budget_by_category) - set(spend_by_category)
```

So after every transaction is deleted, any category that still has a Budget row for the current month keeps producing a row in `categoryBreakdown` with `amount = 0`, keeping `topCategories.length > 0` true and the chart rendered — instead of falling back to `EmptyState`, unlike the neighboring **Monthly Spending Trend** chart on the same page, which correctly checks a real spend total (`yearly.total_yearly_spending > 0`) rather than row count.

**Requirement:** change the Monthly Expenses Breakdown's empty-state condition from "are there any category rows at all" to "is there any actual spend this month" — e.g. check that the sum of `topCategories` amounts (or `monthly.total_expenses`, if already available from `/dashboard/monthly`) is greater than zero, matching the pattern already used correctly by the Monthly Spending Trend chart directly above it. Do **not** change the backend `/dashboard/category-breakdown` endpoint itself — its zero-spend-budgeted-category rows are intentional and used elsewhere (budget-vs-actual comparisons); this is a frontend-only fix.

**Acceptance criteria:** after deleting every transaction for the current month (including in households with active budgets for that month), the Monthly Expenses Breakdown card shows the same "will appear once you add transactions" empty state as the Monthly Spending Trend chart, not a stale or all-zero chart.

### 5.4 Cashback doesn't auto-apply for matching merchant

**Files:** `backend/app/services/cashback_service.py` (`resolve_cashback_rate`, `record_cashback_for_line_items`), wired into `backend/app/api/transactions.py` (create, OCR-confirm, and recurring-bill-mark-paid call sites).

**Code-level finding:** cashback computation **is** already wired into transaction creation automatically — this is not a case of the hook being missing. The likely defect is in the **merchant matching**, which requires an **exact match** (case-insensitive, trimmed) between `CashbackRule.merchant` and `Transaction.merchant`:

```python
merchant_condition = or_(merchant_condition, func.lower(CashbackRule.merchant) == merchant.strip().lower())
```

The rule-creation UI (`frontend/app/cashback/page.js`, merchant field placeholder `"e.g. Costco"`) invites the user to enter a short, clean merchant name. Real transaction merchants — especially OCR-extracted ones — are frequently longer/messier (e.g. `"COSTCO WHSE #1234"` vs. a rule set for `"Costco"`), which would never satisfy an exact match and silently fall back to the category-level rule (or $0 if none exists) with no error shown anywhere.

**Requirement:**
* Change merchant matching from exact match to normalized substring/contains match (e.g. rule merchant `"costco"` matches transaction merchant `"costco whse #1234"`), still case-insensitive and trimmed.
* Add a visible signal when a transaction's cashback estimate is $0 specifically because no rule matched (vs. because the category has a 0% rate) — a small "no matching cashback rule" hint on the transaction or in the cashback dashback, so this class of bug is discoverable by the user next time rather than silent.
* Re-verify the existing specificity ordering (merchant > category > default, latest `start_date` wins ties) still holds correctly after loosening the match — do not weaken specificity resolution while fixing the match itself.

**Acceptance criteria:** a transaction whose merchant contains (not just exactly equals) a configured rule's merchant string earns cashback at that rule's rate at creation time, with `backend/tests/test_cashback.py` extended to cover the substring-match case explicitly.

### 5.5 Invited partner cannot log in / Sign-in redirects back to login on mobile

**Update: §5.3's confirmed CORS finding materially changes the confidence ranking here.** These were written up as two hypotheses before any hard evidence existed. Now that a sibling endpoint (recurring-bill mark-paid) on this *exact* production deployment (`bill-wise-alpha.vercel.app` → `billwise-1et2.onrender.com`) is confirmed CORS-blocked, the leading explanation for both of these is the **same infrastructure misconfiguration**, not a code-level bug — both `POST /auth/login` (or the invite-accept POST) and `GET /auth/me` are cross-site credentialed requests from the same frontend origin to the same backend, subject to the exact same `FRONTEND_BASE_URL`/`COOKIE_SAMESITE` misconfiguration described in §5.3.

**Relevant code:**
* Invite/accept flow: `backend/app/api/household.py` (invite ~lines 82–126, accept ~lines 129–165+), `frontend/app/accept-invite/page.js`.
* Sign-in: `frontend/app/signin/page.js`, `frontend/hooks/useAuth.js` (wraps `GET /auth/me` via SWR), `components/auth/AuthGuard.js`.
* Cookie config: `backend/app/core/config.py` (`cookie_name = "billwise_session"`, `cookie_samesite = "lax"`, `cookie_secure`), set in `backend/app/api/auth.py` (~lines 50–55, 185–187).
* CORS: `backend/app/main.py` (~lines 34–43), same middleware §5.3 found misconfigured.

**Confirmed via clarifying question:** both happen in a **regular mobile browser** (Safari/Chrome on phone), not inside an installed PWA or an in-app browser. Note this doesn't imply the cause is mobile-specific — CORS and cookie-attribute failures are not device-dependent, they'd reproduce identically on desktop hitting the same origin pair. It most likely means these were simply the surfaces where testing happened to occur, not a symptom exclusive to mobile. **Verifying this fix on desktop against the same production URLs is a useful, cheap sanity check.**

**Ranked hypotheses (updated):**

1. **Same root cause as §5.3 (now the leading hypothesis, not a guess):** the CORS misconfiguration confirmed for mark-paid would identically block the invite-accept POST and/or the login POST from the same origin — a blocked POST would throw before any response is parsed, which the frontend may be surfacing as a generic "something went wrong" rather than the raw browser CORS error, explaining the invite-login symptom.
2. **Cookie `SameSite`/`Secure` attribute mismatch (best explanation specifically for "sign-in succeeds, then redirects back to login"):** `bill-wise-alpha.vercel.app` and `billwise-1et2.onrender.com` are different registrable domains — a genuinely cross-site deployment. If `COOKIE_SAMESITE` is still at its `"lax"` default in the Render production environment (rather than the `"none"` the codebase's own config comment says this exact deployment shape requires), the browser accepts the `Set-Cookie` from the login response (so login *appears* to succeed) but never attaches that cookie to the subsequent cross-site `GET /auth/me` call, which then 401s and `AuthGuard` bounces back to `/signin` — matching the reported symptom exactly. This is a distinct, compounding issue from CORS and must be fixed alongside it (§5.3's fix already covers setting `COOKIE_SAMESITE=none`).

**Required investigation before fixing:**
1. Apply the `FRONTEND_BASE_URL` and `COOKIE_SAMESITE`/`COOKIE_SECURE` fixes from §5.3 first — re-test both of these bugs afterward, since there's a real chance both are fully resolved as a side effect with zero additional code changes.
2. If either still reproduces after that, inspect the actual `Set-Cookie` response header from a real login attempt (via remote debugging) for `Secure`, `SameSite`, and `Domain` values as a second pass.
3. Confirm whether the invited partner's `email_verified_at` is set on account creation (`backend/app/api/household.py` accept-invite handler) — if login additionally requires email verification and invited/partner accounts aren't auto-verified, that's an independent, additive cause worth ruling out on the invite side specifically, separate from the infra issue above.

**Acceptance criteria:** both bugs reproduced and root-caused with evidence (network trace / cookie header inspection), not fixed speculatively; fix verified on an actual mobile device against the target deployment (not just localhost desktop, which would not surface either hypothesis).

### 5.6 Inline delete on Budgets, Goals, and Recurring Bills list rows

**Files:** `frontend/app/budgets/page.js` (`BudgetNavItem`, ~line 30; single delete `ConfirmButton` today lives in the detail panel, ~line 278), `frontend/app/goals/page.js` (`GoalNavItem`, ~line 39; delete `ConfirmButton` in the detail panel, ~lines 298–304), `frontend/app/recurring-bills/page.js` (`BillNavItem`, ~line 47; delete/deactivate `ConfirmButton` in the detail panel, ~lines 373–379).

**Current behavior (confirmed):** all three pages use the same master-detail layout — a left-hand list (`BudgetNavItem`/`GoalNavItem`/`BillNavItem`, one row per item) and a right-hand detail panel that only renders for whichever item is currently selected (`activeGoal`/`activeBudget`/`activeBill`). The delete `ConfirmButton` exists exactly once per page, inside that detail panel — so deleting anything today requires first clicking the item to select it, then finding the trash icon in the (now-open) detail view.

**Requirement:** add a trash icon directly on each row of the three list components (`BudgetNavItem`, `GoalNavItem`, `BillNavItem`), using the same `ConfirmButton` inline-popover pattern already used in the detail panels (and once §5.1/§5.2's icon-overflow and popover-positioning fixes land, reuse that corrected version rather than the pre-fix styling). Clicking the row's trash icon must delete that item directly from the list, without first navigating into its detail panel — and must not also trigger `onSelect` for that row (the delete click needs to stop propagation so it doesn't simultaneously open the detail panel for the item being deleted).

**Acceptance criteria:**
* Each row in the Budgets, Goals, and Recurring Bills lists shows its own delete affordance, usable without selecting the row first.
* Clicking a row's trash icon does not also select/open that row's detail panel.
* If the deleted row was the currently active/selected item, the detail panel falls back cleanly (e.g. to the next remaining item, or an empty state if the list is now empty) rather than showing a stale detail view for a deleted item.
* The existing detail-panel delete button is unaffected — this adds a second entry point, it doesn't replace the first.

---

## 6. Phase 1 — Private Household Data Model

This is the architecturally significant item flagged for discussion, now resolved through clarifying questions. It should land before any of the Phase 2 features that touch these same resources.

### 6.1 Current state (confirmed by reading the models and `app/api/deps.py`)

There is **no household entity** in this codebase and **no per-creator ownership** on financial data today. `Wallet` (→ `PaymentMethod`), `Budget`, `SavingsGoal`, `Category`, and `RecurringBill` all have a single `user_id` column, and every read/write for these resources is scoped through:

```python
def household_owner_id(user: User) -> uuid.UUID:
    if user.role == UserRole.PARTNER:
        return user.invited_by_user_id
    return user.id
```

In practice this means **a partner has no rows of their own at all** for any of these five resources — everything a partner creates (where permitted) is written under the owner's `user_id`. `SavingsGoal.is_shared` and `Category.is_shared` already exist, but they gate *visibility of the owner's data to the partner* — they do not give the partner their own private data, because the partner never had rows to begin with.

### 6.2 Decision (from clarifying question)

> **When a partner marks an item private, it is hidden from literally everyone else, including the household owner.**

This is the harder of the two options discussed, and it requires the structural change described below — a simple boolean flag alone cannot deliver it, because today's authorization model has no concept of "this row belongs to the partner, not the owner."

### 6.3 Required change

For **Wallet (PaymentMethod), Budget, SavingsGoal, RecurringBill** (Category is explicitly excluded — categories are structural/taxonomic and already have their own `is_shared` sharing model per §21.4 of the original PRD, which is left as-is):

1. Add a real per-creator ownership column, distinct from the household bucket:
   ```sql
   ALTER TABLE payment_methods  ADD COLUMN owner_user_id  UUID NOT NULL REFERENCES users(id);
   ALTER TABLE budgets          ADD COLUMN owner_user_id  UUID NOT NULL REFERENCES users(id);
   ALTER TABLE savings_goals    ADD COLUMN owner_user_id  UUID NOT NULL REFERENCES users(id);
   ALTER TABLE recurring_bills  ADD COLUMN owner_user_id  UUID NOT NULL REFERENCES users(id);
   ```
   Backfill: `owner_user_id = user_id` for all existing rows (today's `user_id` is always the household owner, so this is a safe, lossless backfill — no existing data becomes newly visible or hidden by this step alone).

2. Add the private flag, **default `TRUE`** per the explicit instruction:
   ```sql
   ALTER TABLE payment_methods  ADD COLUMN is_private BOOLEAN NOT NULL DEFAULT TRUE;
   ALTER TABLE budgets          ADD COLUMN is_private BOOLEAN NOT NULL DEFAULT TRUE;
   ALTER TABLE savings_goals    ADD COLUMN is_private BOOLEAN NOT NULL DEFAULT TRUE;
   ALTER TABLE recurring_bills  ADD COLUMN is_private BOOLEAN NOT NULL DEFAULT TRUE;
   ```
   **Migration-time exception:** existing rows (created before this feature existed, under the old fully-shared-by-default model) must be backfilled to `is_private = FALSE`, not `TRUE` — flipping every pre-existing wallet/budget/goal/bill to suddenly-invisible on deploy would be a silent, unannounced data-visibility regression for every current household. `TRUE` is the default for **newly created** rows going forward only.

3. Update every read path for these four resources (list/detail endpoints, dashboard aggregations, notification computations in `backend/app/services/notification_service.py`, budget rollover in `budget_rollover.py`) to filter by:
   ```
   owner_user_id == current_user.id  OR  (owner_user_id != current_user.id AND is_private = FALSE)
   ```
   scoped within the household (i.e. `owner_user_id` must still be the requesting user or another member of the same household — an owner and their partner, resolved the same way `household_owner_id` resolves membership today).

4. Update the corresponding create/update endpoints to accept `owner_user_id = current_user.id` (not the household owner) and `is_private` (defaulting `True`) on these four resource types specifically.

5. **Cross-cutting totals must still work correctly.** Dashboard/budget/net-worth aggregations that sum across "the household's" data must now sum only what the requesting user is entitled to see (their own rows + others' non-private rows) — this is a real behavior change from today's "everyone sees everything" aggregation and must be applied consistently everywhere these four resources are aggregated, not just in their own list views.

### 6.4 What stays unchanged

* **Transactions** are explicitly out of scope for this private-flag mechanism — the reimbursement (§7.4) and cost-split (§7.5) features handle transaction-level visibility/ownership on their own terms. Do not add `is_private` to `Transaction`.
* **Category** sharing keeps its existing `is_shared` model (§21.4 of the original PRD) — not touched by this change.
* Net worth, cashback rules, and payment-method management stay owner-only per §21.4 of the original PRD, **except** that a partner can now have their own private wallets/budgets/goals/bills under this change — "owner-only" there referred to *managing the household's shared financial configuration*, which this doesn't reopen.

### 6.5 Edge cases

* An owner revoking a partner's household access (existing flow) must decide what happens to that partner's private rows — recommend: they follow the same soft-delete/deactivation path as the partner's own transactions today (data retained but inaccessible, not hard-deleted), consistent with §22.6 of the original PRD.
* Un-privating an item (`is_private: true → false`) must be an explicit, visible action — no auto-un-privating on any trigger (e.g. don't silently share a budget just because a linked transaction becomes shared).
* A private budget's spend total must only include transactions the private-budget-owner can see — do not let a private budget's "amount used" leak spend information from another household member's private transactions.

---

## 7. Phase 2 — Transaction Enhancements

### 7.1 Mobile native camera capture for receipt scan

**Decision (from clarifying question):** native camera picker, not a custom in-app live viewfinder.

**Requirement:** on the "Scan Receipt" step of Add Transaction, when on a mobile viewport/platform (reuse the existing `frontend/hooks/usePlatformView.js` platform detection), the file input used for receipt upload gets `capture="environment"` in addition to `accept="image/*"`, so tapping it opens the phone's native camera directly rather than a generic file picker. Desktop/tablet behavior (file picker only) is unchanged.

**Acceptance criteria:** on a mobile browser, tapping "Scan Receipt" opens the device camera directly; the captured photo flows through the existing OCR pipeline (`POST /ocr/receipt`) unchanged.

### 7.2 OCR-fail fallback: retain receipt image, minimal manual entry, thumbnail + modal in Transaction History

**Current behavior (confirmed):** OCR failure/timeout already falls back to manual entry per §13.3 of the original PRD, but that's full manual entry (every field), and the receipt image is discarded — §13.1/§22.4 of the original PRD are explicit and deliberate that receipt images are "never permanently stored," deleted after confirmation, cancellation, OCR failure, or timeout. `backend/app/services/ocr_service.py` reflects this today by design: its own docstring states image bytes are "processed entirely within this process and are never written to disk."

**Supersedes §13.1, §13.3, and §22.4 of the original PRD — for the specific case of a failed-OCR fallback transaction only.** The new requirement, from direct instruction, reverses the "never stored" decision for this one path:

1. When OCR extraction fails (timeout, unreadable image, or the user dismisses a low-confidence result) but a receipt image was successfully uploaded, the image must now be **retained permanently**, attached to whatever transaction the user ultimately saves via the reduced-entry fallback below — not discarded.
2. The fallback entry form requires only:
   * Total amount
   * Merchant
   * Payment method

   All other fields (category/line items, date, notes) become optional at save time, with sensible defaults (date = today, category = Uncategorized) rather than blocking submission.
3. **New persistent storage is required** — this project currently has no blob/object storage of any kind (OCR processing is deliberately in-memory-only, per the docstring above); a receipt image that must outlive the request needs a real storage backend (e.g. S3-compatible object storage) plus a reference column on `Transaction` (§11).
4. **Transaction History gets a new column** (`frontend/app/analytics-transaction-history/page.js`) showing a small thumbnail preview for any transaction with a retained receipt image (blank/no icon for transactions without one). Clicking the thumbnail opens a modal displaying the full-size image.
5. **If the user abandons the fallback form without saving a transaction**, the uploaded image must still be discarded — retention is tied to a transaction actually being saved, not to the upload step in isolation. This preserves the original privacy intent for every path that doesn't end in a saved transaction.

**Acceptance criteria:**
* A transaction saved via the OCR-fail fallback (amount/merchant/payment method only) retains its receipt image permanently.
* The Transaction History table shows a thumbnail for any transaction with a retained image; clicking it opens the full image in a modal.
* Abandoning the fallback flow without saving leaves no orphaned stored image.
* A transaction with a retained image, when deleted, also deletes its stored image (no orphaned files) — see §11/§13 for the cascade requirement.

### 7.3 OCR: exclude discounts/credits from line items

**Files:** `backend/app/api/ocr.py` (extraction schema, line items ~13–32), `ai_structuring_service.structure_receipt_text()`.

**Requirement:** the AI structuring prompt and/or post-processing step must identify line items that are discounts, coupons, credits, or negative-amount adjustments (not real purchased items) and exclude them from the line-item list shown for category assignment — they should still net into the correct total (so line items + tax still reconcile to the receipt total per §12.3/§12.4 of the original PRD), but must not appear as a "purchased item" requiring its own category.

**Acceptance criteria:** a receipt containing a discount line (e.g. `"Member Discount -$5.00"`) does not produce a line item requiring category assignment, while the transaction total still reconciles correctly against the sum of real line items minus the discount.

### 7.4 Reimbursement transaction type

**Naming note — resolve before implementation:** the original PRD already defines a **Category** called "Reimbursement" (§10.9), explicitly scoped as "labeling only — no repayment tracking... a known MVP limitation until a real reimbursement workflow exists." This feature is that real workflow, but as a **transaction type**, not a category — the two are different concepts that happen to share a name. Recommend renaming the existing category (e.g. to "Reimbursable Expense" or folding its intent into the new type entirely) to avoid a confusing UI where both a category and a type are called "Reimbursement." This needs a product decision at implementation time if not resolved here.

**Requirement:**
1. Add `REIMBURSEMENT` to `TransactionType` (`backend/app/models/transaction.py`), alongside `EXPENSE, INCOME, SAVING_EXPENSE, ADJUSTMENT`.
2. Add fields to `Transaction`:
   ```sql
   ALTER TABLE transactions ADD COLUMN reimbursement_status VARCHAR NOT NULL DEFAULT 'unpaid'; -- 'unpaid' | 'paid'
   ALTER TABLE transactions ADD COLUMN reimbursement_paid_by VARCHAR NULL;   -- free-text name entered at confirm time
   ALTER TABLE transactions ADD COLUMN reimbursement_paid_at TIMESTAMPTZ NULL;
   ```
   (Only meaningful when `transaction_type = 'reimbursement'`; NULL/unused otherwise.)
3. **Exclusion scope (decision from clarifying question):** a Reimbursement transaction is excluded from spend totals, budget usage (§6/§14 logic), and analytics aggregations that represent "your spending" — **but still earns cashback**, since the card/payment method was actually charged. This means `record_cashback_for_line_items` (§5.4) keeps running for Reimbursement transactions, while `category_expense_spend` (used by budgets/notifications) and cash-flow/dashboard totals must add `transaction_type != 'reimbursement'` to their filters. This also directly resolves the "known MVP limitation" called out in §18.6 of the original PRD (Reimbursement overstating net cash flow) — that limitation is retired by this change.
4. **Transaction History table:** add an "Action" column, visible only for rows where `transaction_type = 'reimbursement'` and `reimbursement_status = 'unpaid'`. The action is a "Mark Paid" button that opens an inline confirmation (reuse the `ConfirmButton` pattern from §5.2, once its positioning bug is fixed) asking "Paid by who?" — a required free-text name field — then sets `reimbursement_status = 'paid'`, `reimbursement_paid_by`, `reimbursement_paid_at = now()`.
5. **End-of-month unpaid reimbursement notification:** extend `backend/app/services/notification_service.py` with a new notification type, following the existing pattern in that file (computed live per-request, not persisted — consistent with how budget/recurring-bill notifications already work there). Additionally, since the requirement is specifically "at the end of every month" (a proactive check, not just "whenever the user happens to open the app"), add a **scheduled job** following the exact precedent already in this repo (`.github/workflows/hard-delete-expired-accounts.yml` + `backend/scripts/hard_delete_expired_accounts.py`): a new workflow running on/near the last day of each month (or first day of the next, checking the prior month) that finds all `reimbursement_status = 'unpaid'` transactions from the closed month and triggers the existing email-notification mechanism (reuse whatever channel `RecurringBill` reminders already use — §16.6 of the original PRD, "in-app plus an optional daily/weekly email digest").

**Acceptance criteria:**
* A Reimbursement transaction does not affect any budget's "spend" figure or the dashboard's spending totals, but does produce a cashback record when a matching rule applies.
* Marking a Reimbursement transaction "Paid" requires a non-empty "paid by" name and is irreversible through the UI (no un-mark — matches the audit-log style pattern used elsewhere; a correction would be a new Adjustment transaction, consistent with how goal corrections work per §15.2 of the original PRD).
* An unpaid reimbursement from a closed month surfaces both in-app and via the scheduled job/email at month-end.
* `backend/tests/test_transactions.py` and `backend/tests/test_notifications.py` extended to cover all of the above.

### 7.5 Transaction cost-split ("Share") feature

**Decision (from clarifying question):** this is a **distinct feature from Reimbursement** — a real cost-split (Splitwise-style) mechanism, not just visibility sharing.

**Requirement:**
1. New table:
   ```sql
   CREATE TABLE transaction_shares (
     id UUID PRIMARY KEY,
     transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
     shared_with_user_id UUID NOT NULL REFERENCES users(id),
     share_amount DECIMAL NOT NULL,       -- that user's portion
     status VARCHAR NOT NULL DEFAULT 'pending',  -- 'pending' | 'settled'
     created_at TIMESTAMPTZ NOT NULL,
     updated_at TIMESTAMPTZ NOT NULL
   );
   ```
2. On Add Transaction, an optional "Split this transaction" control lets the creator select one or more other household members (owner/partner(s) — per the non-goal in §3, not arbitrary external users) and either an even split or custom per-person amounts, which must sum to the transaction's total (same reconciliation rule already used for line items, §12.3/§12.4 of the original PRD).
3. Each `shared_with_user_id`'s portion appears in *their* view as a distinct "owed" item (surfaced wherever Reimbursement's unpaid items are surfaced — reuse that UI/notification surface rather than building a second one) until marked settled by the transaction's creator, using the same "who/when" confirmation pattern as §7.4.
4. A split transaction's full amount still counts toward the creator's own spend/budget totals by default (they paid it) — splitting is about *tracking who owes what*, not removing the expense from the payer's books. (This is a design default, not confirmed via clarifying question — flag for a quick confirm at implementation time if it matters to the product owner, since it's the one sub-decision in this batch not explicitly settled.)

**Acceptance criteria:** a transaction can be split among household members with amounts reconciling to the total; each recipient sees their owed portion; settling a split share is tracked with who/when, independent of the Reimbursement mechanism.

### 7.6 "Type" filter on Transaction History

**File:** `frontend/app/analytics-transaction-history/page.js`.

**Requirement:** add a filter control (consistent with existing filters already on this page — date range, category, payment method) for `transaction_type`, covering all current and new values: Expense, Income, Saving expense, Adjustment, Reimbursement. Multi-select, combinable with existing filters (AND semantics, matching existing filter behavior on this page).

**Acceptance criteria:** filtering by one or more types narrows the table correctly and composes with existing filters without resetting them.

---

## 8. Phase 3 — Budgets

### 8.1 Budget list shows usage/total (like Goals)

**File:** `frontend/app/budgets/page.js`.

**Current behavior:** the sidebar (`BudgetNavItem`, ~lines 30–49) shows the budget amount and an "over budget" status flag, but not a "spent / total" figure the way the Goals list shows "saved / target."

**Requirement:** each budget list entry displays `{spend} / {budget_amount}` (matching the Goals screen's existing progress presentation, §15.3 of the original PRD, for visual consistency) in addition to the existing over-budget indicator. Respect the exclusion rules from §7.4 (Reimbursement transactions excluded from `spend`) and the visibility rules from §6.3 (a private budget's spend reflects only what its owner can see).

**Acceptance criteria:** every budget row shows current spend against its total at a glance, consistent with how Goals already presents saved-vs-target.

### 8.2 Budget auto-renewal on the 1st of the month

**Current behavior (confirmed by reading `backend/app/services/budget_rollover.py`):** rollover already exists today, but works differently from what's being asked for — it's **lazy** (triggered reactively the first time a user views Budgets or the Dashboard in a new month, not on a schedule) and it **copies forward the previous month's dollar amounts** rather than resetting to zero.

**Decision (from clarifying question) — this changes both of those:**
1. **Timing:** move from lazy/reactive to a real scheduled job, following the exact precedent already in this repo (`.github/workflows/hard-delete-expired-accounts.yml` pattern) — a new workflow scheduled for 00:05 UTC on the 1st of each month, calling a new `backend/scripts/renew_monthly_budgets.py`.
2. **Amount:** **Supersedes §14.4 of the original PRD.** The new month's budget rows are created automatically, but with `budget_amount` reset to `$0` (or omitted/unset, whichever the schema prefers) rather than copied forward — the user re-enters each category's amount for the new month, but doesn't have to manually re-create the rows/categories themselves.

**Note:** the existing lazy rollover (`ensure_budget_rollover_as_owner`, called from the Budgets and Dashboard routers) should be removed or reduced to a safety-net no-op once the scheduled job is in place, to avoid the two mechanisms disagreeing (e.g. the lazy path re-copying a nonzero amount forward before the scheduled job runs, on a household that opens Budgets on the 1st before 00:05 UTC has executed).

**Acceptance criteria:** on the 1st of a new month, every category that had a budget in the prior month gets a new `$0` row automatically, without the user needing to open any page first; `backend/tests/test_budgets.py` covers the new scheduled path, and the old lazy-copy-forward behavior is removed from test coverage rather than left contradicting it.

---

## 9. Phase 4 — Remove AI Insights

**Decision (from clarifying question):** full removal, not a feature flag.

**Files to delete/modify:**
* Backend: `backend/app/api/ai_insights.py` (routes: `GET /dashboard/ai-insights`, `PATCH /ai-insights/{insight_id}`), `backend/app/models/ai_insight.py`, `backend/app/services/ai_insight_service.py`, `backend/app/services/insight_aggregation.py`, `backend/app/schemas/ai_insight.py`.
* A migration dropping the `ai_insights` table.
* Frontend: the AI Insights widget/section on the dashboard, and any nav entry pointing to it.
* `backend/app/services/notification_service.py` currently imports `AIInsight` (per the file's own docstring reference to "bill reminders, AI insights, and partner activity") — remove that notification source cleanly rather than leaving a dangling import.
* Remove the associated LLM API key from `.env.example` and deployment secrets if it was dedicated solely to this feature (confirm nothing else — e.g. the OCR structuring service, §7.3 — shares the same key/provider before removing infra, since `ai_structuring_service.structure_receipt_text()` also does AI/LLM work and must keep working).
* `backend/tests/test_ai_insights.py` removed.
* §19 and the AI-Insights references in §18.1/§29.3 of the original PRD become historical-only (not edited there, since that document isn't touched — but implementers should know those sections describe a feature that no longer exists).

**Acceptance criteria:** no route, model, table, UI element, or scheduled/triggered call related to AI Insights remains; the receipt-OCR AI pipeline (unrelated feature) is unaffected and verified still working after removal.

---

## 10. Phase 5 — PWA "Add to Home Screen" Icon

**Confirmed absent today:** no `manifest.json`/`site.webmanifest` anywhere under `frontend/public/`, no `apple-touch-icon` link in `frontend/app/layout.js` (only a 16px favicon), no manifest reference in `next.config.js`. This is why the home-screen shortcut currently falls back to the tiny favicon on both iOS and Android.

**Decision (from clarifying question):** icon fix only — no service worker, no offline support, no install-prompt banner.

**Requirement:**
1. Add `frontend/public/manifest.json` with `name`, `short_name`, `theme_color`/`background_color` (matching the current pastel-pink rebrand per the recent "redesign: rebrand theme color" commit), and an `icons` array including at minimum 192×192 and 512×512 PNGs.
2. Add a properly sized (180×180) `apple-touch-icon.png` and reference it via `<link rel="apple-touch-icon" href="/apple-touch-icon.png">` in `frontend/app/layout.js`.
3. Add `<link rel="manifest" href="/manifest.json">` in the same layout file.
4. New icon assets should be produced from the existing app icon/branding already used elsewhere in `frontend/public/icons` and `frontend/public/images/favicon.png`, not a new design.

**Acceptance criteria:** adding BillWise to the home screen on both iOS Safari and Android Chrome shows the proper app icon (not the favicon) and the correct app name under it.

---

## 11. Consolidated Data Model Changes

```sql
-- Phase 1 — private data model (§6)
ALTER TABLE payment_methods  ADD COLUMN owner_user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE payment_methods  ADD COLUMN is_private     BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE budgets          ADD COLUMN owner_user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE budgets          ADD COLUMN is_private     BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE savings_goals    ADD COLUMN owner_user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE savings_goals    ADD COLUMN is_private     BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE recurring_bills  ADD COLUMN owner_user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE recurring_bills  ADD COLUMN is_private     BOOLEAN NOT NULL DEFAULT TRUE;
-- Backfill note: set owner_user_id = user_id and is_private = FALSE for ALL pre-existing
-- rows in the same migration, before the DEFAULT TRUE applies to anything new.

-- Phase 2 — Reimbursement (§7.4)
-- TransactionType enum gains: REIMBURSEMENT
ALTER TABLE transactions ADD COLUMN reimbursement_status VARCHAR NOT NULL DEFAULT 'unpaid';
ALTER TABLE transactions ADD COLUMN reimbursement_paid_by VARCHAR NULL;
ALTER TABLE transactions ADD COLUMN reimbursement_paid_at TIMESTAMPTZ NULL;

-- Phase 2 — OCR-fail fallback receipt retention (§7.2)
-- Requires a new persistent object-storage backend (e.g. S3-compatible) —
-- none exists in this codebase today; OCR processing is deliberately in-memory-only.
ALTER TABLE transactions ADD COLUMN receipt_image_key VARCHAR NULL;

-- Phase 2 — Cost-split (§7.5)
CREATE TABLE transaction_shares (
  id UUID PRIMARY KEY,
  transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
  shared_with_user_id UUID NOT NULL REFERENCES users(id),
  share_amount DECIMAL NOT NULL,
  status VARCHAR NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

-- Phase 4 — AI Insights removal
DROP TABLE ai_insights;
```

---

## 12. API Changes (summary)

| Endpoint | Change |
|---|---|
| `POST/GET/PATCH /payment-methods`, `/budgets`, `/goals`, `/recurring-bills` | Add `is_private` to request/response schemas; scope reads per §6.3 |
| `POST /transactions` | Accept `transaction_type = "reimbursement"`; accept `shares[]` for cost-split |
| `POST /transactions/{id}/mark-reimbursement-paid` | **New** — body: `{ paid_by: string }` |
| `POST /transactions/{id}/shares/{share_id}/settle` | **New** |
| `GET /transactions` | Accept `transaction_type` as a multi-value filter param |
| `GET /transactions/{id}/receipt-image` | **New** — authenticated, authorized (owning household member only), streams the retained receipt image for a fallback-saved transaction (§7.2) |
| `GET /notifications` | New notification type for unpaid reimbursements past month-end |
| `POST /ocr/receipt` | Line-item extraction excludes discount/credit lines (§7.3) |
| `GET/PATCH /dashboard/ai-insights`, `/ai-insights/{id}` | **Removed** |
| `POST /cashback/rules` matching | Merchant match changes from exact to substring (§5.4) — no schema change, behavior only |

---

## 13. Security & Privacy Notes

* The private-data model (§6) is a genuine new privacy boundary — implementers must treat every existing endpoint touching Budget/PaymentMethod/SavingsGoal/RecurringBill as needing re-review, not just the obviously "list" endpoints. Dashboard aggregation, exports (§20 of the original PRD), and notifications all currently assume full household visibility and must be updated together, or a private item could leak through a secondary surface even after the primary list view is fixed correctly.
* Exports (CSV/Excel/PDF, §20 of the original PRD) must respect the same private/shared filtering as §6.3 — a household member exporting data must not receive another member's private wallets/budgets/goals/bills in the file.
* The audit log (§22.3 of the original PRD) should record `is_private` changes on these four resource types, consistent with how it already records category-sharing changes.
* Reimbursement's `reimbursement_paid_by` is free text (per the request) — treat it as untrusted display data (escape on render), not as a foreign key to a real user, since the payer may not be a BillWise user at all (e.g. a friend outside the household).
* **Retained receipt images (§7.2) are a deliberate reversal of a documented privacy commitment** (original PRD §13.1/§22.4, and `ocr_service.py`'s own "never written to disk" design comment) — treat the new storage path with the same care as the forbidden-fields list in §22.1 of the original PRD, since receipts frequently contain incidental sensitive data (partial card numbers, signatures, other purchased items unrelated to the transaction). Required safeguards: serve images only through the new authenticated `GET /transactions/{id}/receipt-image` endpoint (never a permanently public/unsigned URL), scope access to the transaction's owning household member using the same visibility rules as the transaction itself (respecting §6.3 if the transaction's budget/wallet context is private), encrypt at rest (provider-managed baseline per §22.2 of the original PRD is sufficient, consistent with how other stored data is handled), and cascade-delete the stored image when its transaction is deleted so nothing outlives the record it belongs to.
* The CORS/cookie deployment fix in §5.3 touches production authentication infrastructure directly — apply and verify it in a maintenance window with rollback awareness (a bad `FRONTEND_BASE_URL`/`COOKIE_SAMESITE` value can lock out all users, including the owner), even though the change itself is low-complexity.

---

## 14. Edge Cases

* **§6 Private data:** an owner deletes their own account (§22.6 of the original PRD) — what happens to a partner's private budgets/goals/etc.? Recommend: they survive independently of the owner's deletion, since they're now genuinely the partner's own data, not the owner's — this is a real behavior change from today (where deleting the owner deletes the whole household's data) and should be confirmed with the product owner before implementation, since it's not explicitly covered by this batch's clarifying questions.
* **§7.4 Reimbursement:** a Reimbursement transaction gets edited after creation to a different `transaction_type` — must clear `reimbursement_status`/`paid_by`/`paid_at`, and vice versa when a transaction is changed *to* Reimbursement.
* **§7.4 Reimbursement:** the end-of-month scheduled job runs but the household has zero unpaid reimbursements — must be a silent no-op, not an empty/broken notification.
* **§7.5 Cost-split:** a shared-with partner is removed from the household (existing invite-revoke flow) with pending unsettled shares — those shares should remain visible to the creator as "owed" but the removed partner naturally loses access to settle them themselves; the creator must still be able to mark them settled manually.
* **§8.2 Budget renewal:** a category is deleted mid-month — the scheduled job must skip categories that no longer exist rather than erroring the whole batch for one household.
* **§5.4 Cashback substring match:** loosening merchant matching to substring could cause a *short* rule merchant (e.g. `"A"`) to over-match unrelated transactions — validate/require a reasonable minimum merchant string length on rule creation, or normalize with word-boundary matching rather than raw substring, to avoid this footgun.
* **§5.3 CORS/cookie fix:** if a Vercel *preview* deployment (a different auto-generated origin per branch/commit) is ever used for testing or staging, it will reproduce the exact same CORS error against a `FRONTEND_BASE_URL` pinned to the production origin only — call this out to whoever tests the fix, so it isn't mistaken for a regression.
* **§5.3b Chart empty state:** a household with a budget for a category but genuinely $0 spend all month (never had a transaction, not just deleted ones) must also show the empty state, not a chart with a single invisible/zero-value slice — the fix should key off total spend being zero, which naturally covers both "never had transactions" and "had transactions, now deleted."
* **§5.6 Inline delete:** deleting the last remaining item in a list via the new row-level trash icon must leave the page in the same clean empty state as deleting via the detail panel today — verify both entry points converge on identical post-delete behavior.
* **§7.2 Receipt retention:** a transaction saved via the OCR-fail fallback is later edited or its category/line items filled in after the fact — the retained receipt image must stay attached throughout, not just at initial save.
* **§7.2 Receipt retention:** the receipt-image storage backend is unreachable/errors at save time — the transaction itself (amount/merchant/payment method) must still save successfully; a failed image upload should degrade to "no thumbnail" rather than blocking the whole save, consistent with how OCR failures already degrade to manual entry rather than blocking anything.

---

## 15. Acceptance Criteria (roll-up)

* [ ] All Phase 0 items (§5.1–§5.6) reproduced/verified with evidence, fixed, and covered by a regression test (backend) or a manual verification note with before/after screenshots at the standard breakpoints (frontend visual bugs). The CORS/cookie fix (§5.3) specifically verified against the live `bill-wise-alpha.vercel.app` / `billwise-1et2.onrender.com` deployment, not localhost.
* [ ] Phase 1 private-data model: every list/detail/aggregation endpoint for the four affected resources re-audited and passing new visibility tests (owner sees own + others' shared; partner sees own + others' shared; nobody sees another's private item).
* [ ] Phase 2: Reimbursement, cost-split, mobile camera capture, OCR-fail fallback, discount/credit exclusion, and Type filter each independently testable and tested.
* [ ] Phase 3: budget list shows usage/total; scheduled renewal job verified to run and produce `$0` rows for the new month without requiring a page visit.
* [ ] Phase 4: zero references to AI Insights remain in code, routes, nav, or `.env.example`; OCR structuring service confirmed unaffected.
* [ ] Phase 5: home-screen icon verified on both iOS and Android.
* [ ] Every phase implemented through the harness-os Constitution → Spec → Tests → Code → Review flow per §4, with the project constitution established before Phase 0 begins.

---

## 16. Open Risks / Not Fully Settled

* **§7.5.4** (whether a split transaction's full amount still counts toward the payer's own budget) is a design default proposed in this document, not an explicit product decision — confirm before implementation.
* **§14, account-deletion interaction with private partner data** — flagged as needing a product decision, not answered by this batch's clarifying questions.
* **§5.3 is now a confirmed root cause** (actual production CORS error captured), not a hypothesis — the fix itself (environment variables) is low-risk and can proceed directly. **§5.5 remains a strong-but-unconfirmed hypothesis** riding on §5.3's finding — re-test both bugs after applying §5.3's fix before writing any additional code for them, since they may already be resolved.
* **Reimbursement category vs. Reimbursement type naming collision (§7.4)** needs a explicit resolution (rename the existing category or merge intent) before implementation to avoid shipping a confusing duplicate name in the UI.
* **§7.2 receipt retention scope:** this batch only asked for retention on the OCR-*failure* fallback path. Whether successfully-OCR'd (and confirmed) transactions should also retain their receipt image and show the same Transaction History thumbnail — for consistency, since a user seeing thumbnails on some transactions but not others may be confusing — is a natural follow-on question this document deliberately does not assume an answer to. Confirm before implementation, since it changes the storage/cost footprint significantly (most receipts go through the success path, not the failure path).
* **§11 storage backend choice** (S3-compatible object storage vs. an alternative) is not specified — this document establishes that persistent storage is now required and what it must guarantee (§13), but the specific provider/service is an implementation decision for whoever picks up Phase 2, consistent with this deployment's existing Render/Vercel hosting choices.

---

## 17. Milestones / Rollout Plan

1. **Milestone 0 — Governance setup:** establish the project constitution (§4) before any other work.
2. **Milestone 0.5 — CORS/cookie production hotfix (§5.3):** this is a two-environment-variable config change with a confirmed root cause and no code required — it does not need to wait for the constitution/spec/test process in §4 given its urgency and near-zero implementation risk, and should ship as an immediate hotfix ahead of everything else in this document. Re-test §5.5 (invite login, sign-in redirect loop) immediately after, since both may already be resolved by this alone.
3. **Milestone 1 — Phase 0 bug fixes:** the rest of §5 (§5.1, §5.2, §5.3b, §5.4, §5.5 if still reproducing after Milestone 0.5, §5.6) — independent, ship as soon as each is root-caused and fixed; no need to batch them together.
4. **Milestone 2 — Phase 1 private data model:** the riskiest, most cross-cutting change in this batch; run `impact_analysis` first given how many endpoints read through `household_owner_id` today; land behind thorough test coverage before Phase 2 features build on top of it.
5. **Milestone 3 — Phase 2 transaction features:** Reimbursement and cost-split both depend on Phase 1's ownership model existing first (both introduce new per-user-visible data). Mobile camera capture, OCR-fail fallback (including receipt-image storage setup), Type filter, and OCR discount exclusion have no such dependency and can ship independently/earlier if useful.
6. **Milestone 4 — Phase 3 budgets:** usage/total display can ship any time; scheduled renewal should land after Phase 1 (a private budget's renewal must respect the same ownership rules).
7. **Milestone 5 — Phase 4 AI Insights removal:** independent, can happen any time, ideally early to stop cost accrual immediately.
8. **Milestone 6 — Phase 5 PWA icon:** independent, trivial to ship any time.
