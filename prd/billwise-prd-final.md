# BillWise — Personal Expense Tracking System PRD

## 1. Product Overview

**Product Name:** BillWise
**Product Type:** Personal expense tracking web application, built on the client-provided **Ekash** Next.js admin dashboard template
**Primary Users:** Owner (full control) and one or more Partners (invited, permissioned, scoped to shared categories) — a single household per deployment
**Currency:** USD only
**Core Purpose:** Help a household manually track monthly expenses across multiple payment methods, categories, budgets, recurring bills, savings goals, and cashback/rewards, without connecting to banks or storing sensitive credit-card information.

BillWise is not a banking app and not a credit-card management platform. The frontend must visually match the Ekash template exactly — its layout, components, colors, and typography are the design system for this product. Where the template has no equivalent screen (receipt OCR review, recurring bills, cashback, net worth, household sharing), new screens are designed to feel native to that same visual language rather than introducing a different style.

---

## 2. Background and Source Requirements

The original need was for a personal finance web app that could track spending from user-defined credit/debit cards, record monthly expenses across customizable categories, scan receipts to reduce manual entry (with user confirmation before saving), and show dashboard summaries for spending, card usage, cash flow, budgets, and net worth.

The client has since supplied a purchased frontend template — **Ekash: Personal Finance Management Admin Dashboard (Next.js)** — with an explicit requirement that the shipped UI look exactly like it. The template ships with a full set of demo pages built around hardcoded mock data, some of which model features and data collection BillWise must not have (real bank linking, full card numbers, identity verification). Reconciling the two is the core of this document.

Finalized MVP scope:

* Owner + partner system, both fully functional — one household, one owner account, one or more invited partner logins
* USD only
* No third-party bank or credit-card integration, ever
* No storage of full credit-card information, ever
* Manual transaction entry plus OCR-assisted receipt scan (cloud AI allowed for structuring/categorization)
* Category-level sharing between owner and partner — no expense-splitting or settlement workflow yet
* No reimbursement math — the category exists as a label only
* Savings goals (adopted from the template's Goals feature)
* Expense tracking, not full accounting
* Savings is treated as an expense category
* Frontend built on the Ekash template — desktop sidebar layout as designed, plus a separate bottom-nav layout for mobile. Alsok, when logged in, the system will ask which platform the user is logging in as (PC or Mobile), then it will show the appropriate platform view
* Simple email/password authentication, JWT security,etc to prevent URL hacking or injection — no OTP, no phone verification, no multi-factor login
* Encryption, audit logs, and privacy-conscious architecture throughout
* Export to CSV, Excel, and a PDF monthly report
* AI-generated spending insights
* No hardcoded/demo data in the shipped product — every number, name, and list must come from real data or a defined empty state

---

## 3. Goals

### 3.1 Product Goals

1. Let the owner and any invited partner track expenses clearly across multiple cards and categories, with the owner controlling exactly what the partner can see.
2. Make transaction entry fast through manual input and OCR-assisted receipt parsing.
3. Support monthly and category-specific budgeting, plus savings goals.
4. Provide dashboards for monthly spending, yearly spending, category breakdowns, card breakdowns, cash flow, net worth, recurring bills, and cashback/rewards.
5. Avoid direct bank integrations for privacy and safety.
6. Never store sensitive card details such as full card numbers, CVV, or online banking credentials.
7. Provide insights that help the user understand spending trends.
8. Support a second household member (partner) from day one.
9. Deliver a frontend visually identical to the approved Ekash template, with zero leftover demo data.

### 3.2 User Goals

The owner (and, where shared, the partner) wants to answer questions such as: How much did I spend this month? Which category or card dominates? Am I over budget? How much did I spend this year? How much cashback did I earn? What bills are coming up? What's my cash flow? Is my net worth growing? How close am I to my savings goals? What changed vs. last month? What has my partner added, and what am I sharing with them?

---

## 4. Non-Goals

1. No Plaid, bank API, credit-card API, or third-party financial account integration.
2. No login to credit-card websites, and no "connect your bank" flow of any kind — even though the template's UI was originally built around one.
3. No storage of full credit-card numbers or CVV.
4. No automatic bank synchronization or real-time balance pulling.
5. No complex reimbursement math.
6. No expense-splitting or settlement workflow — distinct from partner login, which is in MVP.
7. No payment processing or bill payment through the app.
8. No investment trading, multi-currency support, tax filing, or enterprise accounting features. (The template's currency-exchange screen is explicitly excluded for this reason.)
9. No support for multiple, unrelated households on one deployment.
10. No identity/KYC verification (government ID upload) — the template includes this flow; BillWise does not need it and it is dropped entirely.
11. No OTP or multi-factor authentication in MVP — simple email/password login only, despite the template including ready-made OTP screens.
12. No referral/affiliate program and no support-ticket system — present in the template, not part of this product.
13. No public developer API / API key management — present in the template's settings, not part of this product.

---

## 5. Target Users

### 5.1 Owner
Full control: creates the household, invites/removes the partner, sets category sharing, manages payment methods, tracked balances, budgets, savings goals, recurring bills, cashback rules, net worth, exports, and can delete the household account.

### 5.2 Partner
Own email/password login, invited by the owner. Sees dashboards, budgets, and reports filtered to **shared categories only**. Can add transactions only if the owner has granted that permission, and only into shared categories. Cannot see private categories, private payment methods, net worth, cashback data, or savings goals unless the owner shares them. Cannot invite further users or delete the household account.

### 5.3 Admin/System Owner
The owner also acts as admin: manages the partner's access, reviews audit logs, exports data, configures categories and payment methods, and can delete the household account.

---

## 6. MVP Scope

1. Authentication (email/password only)
2. User profile
3. Household & partner invite flow
4. Category-level sharing controls
5. Payment method aliases (cards) and tracked savings/bank balances
6. Categories and subcategories
7. Manual transaction entry
8. Receipt OCR import
9. Transaction review and confirmation
10. Monthly dashboard
11. Yearly dashboard
12. Category breakdown
13. Card/payment-method breakdown
14. Monthly and category-specific budgets
15. Savings goals
16. Recurring bills
17. Cashback/rewards tracking
18. Cash flow view
19. Net worth tracking
20. AI insights
21. Export reports
22. Audit logs
23. Account deletion flow
24. Security and encryption foundation
25. Frontend built on the Ekash template (desktop sidebar + mobile bottom-nav), fully de-mocked

---

## 7. Tech Stack

Determined by the supplied template, not chosen independently:

### 7.1 Frontend

* **Next.js 14 (App Router)**, matching the template exactly
* **Plain JavaScript (JSX), not TypeScript** — the template itself is untyped (`jsconfig.json`, no `tsconfig.json`), and per your direction we're building with whatever is most compatible with it rather than introducing a TypeScript conversion layer
* **Bootstrap 5 + custom SCSS** for styling, exactly as the template ships it — no Tailwind migration
* **Chart.js** (via `react-chartjs-2`) for charts, **react-circular-progressbar** for progress rings (budgets, goals), **react-perfect-scrollbar** for scrollable lists, **@headlessui/react** for accessible dropdowns/menus
* Icon font: Flaticon "uicons" (`fi fi-rr-*`, `fi fi-ss-*` classes) — confirm the project has a valid commercial license for this icon set's continued use, separate from the ThemeForest template license itself

### 7.2 Backend
Python FastAPI — clean API structure, good fit for the OCR/AI workflow, clean separation from the frontend.

### 7.3 Database
PostgreSQL — relational structure for users, transactions, categories, budgets, goals, bills, and audit logs.

### 7.4 ORM
SQLAlchemy or SQLModel.

### 7.5 OCR and AI

1. **OCR text extraction - Claude Haiku or any model that is good enough for OCR receipt scannning and most cost effective** 
2. **The receipt image is never sent to any third party** and is deleted immediately after extraction — only extracted *text* is eligible to leave the local process.
3. **Structuring/categorization uses a cloud AI API**, which turns the extracted text into structured JSON (merchant, date, total, line items, suggested categories).

Choose a cloud AI provider with a clear no-training-on-API-data policy.

### 7.6 File Storage
Receipt images are never permanently stored — deleted after confirmation, cancellation, OCR failure, or timeout.

### 7.7 Deployment
Frontend on Vercel/Netlify/Docker; backend as a Docker container (Render/Railway/AWS/VPS); managed or self-hosted PostgreSQL. Single-household product — no dedicated GPU/AI server needed since cloud AI handles structuring.

---

## 8. Design System & Visual Identity

Pulled directly from the template's SCSS variables — this is the source of truth for every screen, existing or new:

| Token | Value |
|---|---|
| Primary | `#2F2CD8` |
| Secondary | `#050505` |
| Success | `#12A347` |
| Info | `#0E7CEB` |
| Warning | `#FBA801` |
| Danger | `#DC2626` |
| Dark (sidebar bg) | `#0F172A` |
| Body background | `#F6F9FC` |
| Body text | `#7184AD` |
| Headings color | `#1F2C73` |
| Font family | Rubik (Google Font) |
| Base font size | 0.875rem |
| Border radius | 6px |
| Sidebar width | 80px (icon rail) |
| Card shadow | `rgba(145,158,171,.3) 0 0 2px, rgba(145,158,171,.12) 0 12px 24px -4px` |

Category and chart color accents (orange/amber/yellow/lime/green/cyan/stone scale) carry over unchanged for category breakdowns, budget bars, and chart series.

**Rebranding:** every instance of the template's "Ekash" name, logo, and copyright footer is replaced with BillWise branding. Template social-media footer links (Facebook/Twitter/LinkedIn/YouTube) are removed unless the client has real accounts to link.

**Dark mode:** the template includes a working theme switcher (`ThemeSwitch.js`). Optional to enable — not required for MVP, but effectively free since the component already exists.

---

## 9. Frontend Template Mapping

Every template page is classified into one of four buckets. This is the master reference for frontend implementation.

### 9.1 Direct reskin (structure and components stay, mock data is replaced)

| BillWise Screen | Template Source |
|---|---|
| Dashboard | `/` |
| Yearly/Monthly Analytics | `/analytics`, `/analytics-balance`, `/analytics-expenses`, `/analytics-income`, `/analytics-income-vs-expenses` |
| Transactions History | `/analytics-transaction-history` (search, filter-by-month/category/payment-method/amount-range, edit, delete are added — the template's version doesn't have them) |
| Budgets | `/budgets` |
| Savings Goals | `/goals` |
| Categories | `/settings-categories` (category type and shared/private toggle are added) |
| Notifications | `/notifications` (repurposed for bill reminders, AI insights, partner activity) |
| Profile / General / Security settings | `/settings-profile`, `/settings-general`, `/settings-security` |
| Sign in / Sign up | `/signin`, `/signup` (OTP step removed) |
| Email verification | `/verify-email` (link-based only, no code entry) |
| Privacy policy | `/privacy` |
| 404 | `/404` |

### 9.2 Reworked (visual treatment kept, fields/behavior changed to remove forbidden data collection)

| BillWise Screen | Template Source | Change |
|---|---|---|
| Add Card | `/add-card` | Drop card type and last 4 digits. Keep the card-mockup visual, masked to the last 4 digits the user enters. Collect: display name, last 4 (optional), issuer/type, default cashback rate. |
| Add Tracked Card or Savings | `/add-bank` | Becomes a chooser: "Track a new card" (routes to the redesigned Add Card flow) or "Track a new savings/bank balance" (name, account type, current balance — manual entry, no routing or account numbers, ever). |
| Payment Methods & Tracked Balances | `/wallets`, `/settings-bank`, `/add-new-account` | Strip all "connect your bank/wallet" language and provider logos. Becomes a management list of the owner's card aliases and manually tracked savings/bank balances. No real linking, no live balance pulls. |

### 9.3 Net new (no template equivalent — designed fresh using the template's existing component language: cards, modals, form inputs, color palette, spacing)

* Add Transaction (manual entry)
* Receipt Review / OCR Confirmation screen
* Recurring Bills screen
* Cashback screen
* Net Worth screen
* Household & Partner Sharing screen
* Account Deletion flow (added into Settings)
* Mobile bottom-navigation layout (see §9.4)

### 9.4 Layout: dual implementation

The template is a desktop admin-dashboard layout (fixed icon sidebar, top header). Per your direction:

* **Desktop/tablet (≥768px):** the template's sidebar layout, unchanged.
* **Mobile (<768px):** a separate bottom-navigation layout is built — bottom nav bar (Dashboard, Transactions, Add, Budgets, More), large tap targets, floating quick-add button, swipe-friendly transaction rows. This reuses the same cards, colors, and components as the desktop version; only the navigation chrome differs.
* 768px is the template's own existing breakpoint convention (Bootstrap `md`) — flag if you'd prefer a different cutoff.

### 9.5 Removed entirely (present in the template, not part of BillWise)

* Identity verification: `/id-front-and-back-upload`, `/verify-id`, `/verifying-id`, `/verified-id`
* OTP/2FA flow: `/otp-code`, `/otp-phone`
* Referral program: `/affiliates`
* Support ticketing: `/support`, `/support-create-ticket`, `/support-ticket-details`, `/support-tickets`
* Developer API keys: `/settings-api`
* Multi-currency: `/settings-currencies`
* Bank-linking success page (tied to the removed real-linking flow): `/bank-add-successful`
* Session/device management: `/settings-session` — not requested; simple login only per your direction
* Idle screen lock: `/locked` — not requested; keeping auth simple per your direction
* `/blank` — dev scaffold page, not used

These pages exist in the template files but are not routed to, not linked from navigation, and not part of any acceptance criteria. If a future phase wants any of them (session management and the idle lock in particular are low-effort, low-risk additions since the UI is already built), the groundwork is already there.

### 9.6 Mock Data & Empty States

The template hardcodes every number, name, and avatar directly in JSX (fake balances, fake transaction rows, "Carla Pascle," placeholder avatars, static chart data). None of this ships. Every screen must:

* Pull real values from the backend, or
* Show a defined empty state ("No transactions yet — add your first one," "No budgets set for this month," "No savings goals yet") rather than leftover template placeholder content.

This is called out explicitly in the acceptance criteria (§31) so it isn't missed during a straight component port.

---

## 10. Core Categories and Subcategories

Every category has a `category_type` of `expense` or `income`, and an `is_shared` flag the owner controls (default: private).

### 10.1 Housing (expense) — Rent, Utilities (Electric, Water, Gas, Wifi)
### 10.2 Food (expense) — Grocery, Restaurant
### 10.3 Car (expense) — Insurance, Gas
### 10.4 Shopping (expense) — subcategories added later
### 10.5 Health & Personal (expense) — subcategories added later
### 10.6 Subscription (expense) — subcategories added later
### 10.7 Saving (expense)
Treated as an expense category, since the goal is simple expense tracking, not full accounting. Savings goals (§15) can optionally link transactions in this category to a specific goal.
### 10.8 Family & Support (expense) — subcategories added later
### 10.9 Reimbursement (expense)
Labeling only — no repayment tracking. Still counted as a normal expense in cash flow, which is a known MVP limitation until a real reimbursement workflow exists.
### 10.10 Income (income) — Paycheck, Other Income

The owner can add custom categories of either type.

---

## 11. Payment Method Requirements

### 11.1 Payment Method Aliases (Cards)

Allowed fields: display name, payment method type (Credit Card / Debit Card / Cash / Other), issuer (Discover, Amex, Chase, Citi, etc.), last four digits (optional, for the owner's own identification — the redesigned Add Card screen's masked card visual uses this), statement day / due day (optional, feeds the recurring "card payment" bill), default cashback rate (optional).

Forbidden fields, always: full card number, CVV, online banking username/password, card PIN, security questions, bank API tokens.

### 11.2 Tracked Savings / Bank Balances

A second alias type for manually tracked cash-equivalent balances (checking, savings, or similar), created via the repurposed Add Bank flow. Fields: display name, account type, current balance (manual entry, updated by the owner over time). No routing number, no account number, no live connection of any kind — this feeds the Net Worth view (§18.7) as an asset.

### 11.3 Payment Method Types
Credit Card, Debit Card, Cash, Other — display/reporting classification only.

### 11.4 Credit Card Balance Import
Manual entry or OCR-assisted import of a statement/bill screenshot or PDF, with AI extraction of the balance and line items, always requiring user confirmation. An extracted balance can pre-fill a suggested update to the corresponding tracked balance or net-worth liability — never auto-saved without confirmation.

---

## 12. Transaction Requirements

### 12.1 Manual Transaction Entry
Date, merchant, description, total amount, category, subcategory, payment method, notes, tags, recurring flag, cashback-eligible flag, optional linked savings goal (only relevant for Saving-category expenses).

### 12.2 Transaction Types
Expense, Income, Saving expense, Adjustment.

### 12.3 Multi-Category Receipt Support
One receipt can span multiple categories via a parent transaction + line items, e.g. a Costco receipt split across Grocery, Health & Personal, and Shopping. Line item sum must equal the transaction total before confirmation, unless a tax/rounding adjustment is added.

### 12.4 Validation Rules
* Expense / Income / Saving expense: amount ≥ 0.
* Adjustment: may be negative or positive (corrects a prior entry).
* Date, category (for expenses), and payment method are required.
* OCR-imported transactions always require explicit confirmation.
* Duplicate detection (same merchant, date, amount, payment method) shows a non-blocking warning — never silently blocks or merges.

---

## 13. Receipt OCR Requirements

### 13.1 Flow
Add Transaction → Scan Receipt → upload/capture (jpg/png/heic/single-page PDF, 10MB max) → OCR (30s timeout, falls back to manual entry) → extraction (merchant, date, total, tax, items, prices) → AI category suggestions (below 0.6 confidence defaults to "Uncategorized") → user review → user edits → confirm → structured data stored → temporary image deleted.

### 13.2 Confirmation Requirement
OCR results are never saved automatically. Review screen shows extracted fields, suggested line items, confidence indicator, edit controls, confirm/cancel.

### 13.3 Error Handling
Blurry/cropped/handwritten receipt, missing or multiple totals, duplicate receipt, unrecognized merchant, tax/item mismatch, unsupported file type, oversized file, timeout — all fall back to manual entry.

---

## 14. Budget Requirements

### 14.1 Monthly Budgets
Owner sets a monthly budget per category.

### 14.2 Category-Specific Budgets
Dashboard shows budget amount, actual spending, remaining, percentage used, over-budget warning.

### 14.3 Budget Alerts
Normal (<75%), Warning (75–99%), Over budget (100%+).

### 14.4 Budget Rollover
A new month's budget auto-copies the previous month's amounts per category by default; editable per month without affecting prior months' stored figures.

---

## 15. Savings Goals

Adopted from the template's Goals feature.

### 15.1 Goal Fields
Name, target amount, current amount, target date (optional), icon, color, shared/private flag, active/inactive.

### 15.2 How Progress Is Tracked
A goal's `current_amount` is the sum of Saving-category transactions linked to it via an optional `goal_id` on the transaction. The owner can also log an `Adjustment` transaction against the same goal to correct the figure — reusing the same adjustment mechanism as regular transactions rather than introducing a separate manual-override system.

### 15.3 Goals Screen
List of goals with a progress ring (reusing the template's existing circular-progress component), saved/target amounts, percentage complete, a contributing-transactions list, and an "Add Funds" action that creates a linked Saving-category transaction.

### 15.4 Goals Dashboard Widget
Monthly overview optionally surfaces top goal progress alongside budget status.

---

## 16. Recurring Bills Requirements

### 16.1 Fields
Name, category, subcategory, amount, frequency, due date, payment method, auto-create-transaction toggle, reminder toggle, notes, active/inactive.

### 16.2 Frequency Options
Weekly, Biweekly, Monthly, Quarterly, Yearly, Custom.

### 16.3 Recurring Bill Payment History
Each bill generates period instances (own due date, status: upcoming/paid/overdue/skipped, paid date, optional linked transaction) — enabling real multi-month payment history rather than a single mutable "next due" field.

### 16.4 Recurring Bill Dashboard
Upcoming, due this week/month, total recurring obligation, missed/overdue, paid/unpaid — backed by the per-period history above.

### 16.5 Card Payment Bills
A "Credit Card Payment" bill linked to a payment method with a statement/due day set auto-populates its due date from that record.

### 16.6 Reminder Delivery
In-app plus an optional daily/weekly email digest. Push notifications need a native wrapper and are a later-phase item.

---

## 17. Cashback and Rewards Requirements

### 17.1 Tracking Scope
By card/payment method, issuer, transaction, month; estimated and redeemed amounts.

### 17.2 Cashback Rules
Default and category-specific percentages per payment method, with effective date ranges and notes.

### 17.3 Cashback Calculation
Computed **per line item**, so split-category receipts calculate correctly against different card rates:

```md
Estimated Cashback (per line item) = Line Item Amount × Cashback Rate for that item's category
Transaction Estimated Cashback = Sum of line item estimated cashback
```

Manually overridable at the line-item or transaction level.

### 17.4 Cashback Dashboard
Monthly/yearly earned, by card, by category, redeemed, unredeemed estimate.

---

## 18. Dashboard Requirements

### 18.1 Required Views
Monthly overview, yearly overview, category breakdown, card/payment method breakdown, budget vs. actual, savings goals, recurring bills, cashback/rewards, net worth, cash flow, AI insights.

### 18.2 Monthly Overview
Total income, total expenses, net cash flow, top category, top payment method, budget status, upcoming bills, cashback earned, spending comparison vs. previous month.

### 18.3 Yearly Overview
Total yearly spending, spend by month/category/payment method, average/highest/lowest month, year-to-date cashback and savings total.

### 18.4 Category Breakdown
Category and subcategory totals, percentage of total spend, monthly trend, budget comparison, over-budget warning.

### 18.5 Card/Payment Method Breakdown
Spend by alias, transaction count, average transaction, cashback estimate, tracked/statement balance if entered, due date if configured. No full card details, ever.

### 18.6 Cash Flow View
Income (Paycheck, Other income) minus Expenses (all expense categories, including Reimbursement — which overstates net cash flow for anyone fronting money they expect back; a known, intentional MVP limitation).

### 18.7 Net Worth View
Manual assets (Checking, Savings, Investment, tracked balances from §11.2, Other) and liabilities (Credit-card balance, Car loan, Other debt). `Net Worth = Total Assets − Total Liabilities`. Shows current net worth, monthly history, breakdowns, change vs. previous month.

---

## 19. AI Insight Requirements

### 19.1 Example Insights
Category spending changes, over-budget alerts, multi-month trends, top cashback card, recurring-bill share of monthly spend, cash flow changes, savings category or goal-progress changes.

### 19.2 Rules
Use only stored transaction data, avoid investment-advice framing, explain why an insight is shown, link to supporting data, be dismissible/editable with that state persisted, never require bank data.

### 19.3 Privacy
Only backend-computed aggregates are sent to the AI, never raw transaction dumps. Every insight-generation event is audit logged. Receipt OCR structuring may use a cloud AI provider — only extracted text is sent, never the image.

---

## 20. Export Requirements

### 20.1 CSV
Transactions, Categories, Budgets, Payment method breakdown, Cashback summary, Recurring bills, Goals.

### 20.2 Excel
Multi-sheet: Summary, Transactions, Category Breakdown, Budget vs Actual, Payment Methods, Cashback, Recurring Bills, Net Worth, Goals.

### 20.3 PDF Monthly Report
Month/year, income/expenses/net cash flow, category chart, budget vs actual, payment method breakdown, cashback summary, recurring bills summary, goals progress, AI insights, net worth snapshot.

### 20.4 Export Security
Short-lived signed download URLs (15-minute default expiry), not permanent links. PDF reports support an optional owner-set password.

---

## 21. Authentication and Authorization

### 21.1 MVP Authentication — kept intentionally simple

* Email/password signup
* Email verification via a link sent to the user's inbox (not a code) — before first login
* Email/password login
* Password hashing (bcrypt or argon2)
* Password reset via email link
* Session expiration, logout
* Rate limiting / lockout on repeated failed logins and reset requests

**No OTP, no phone verification, no multi-factor login** — per your direction, this is simple email/password only. The template's OTP UI (`/otp-code`, `/otp-phone`) is not used. This can be revisited in a later phase if ever needed; nothing here blocks adding it.

### 21.2 User Roles
Owner, Partner.

### 21.3 Partner Invite Flow
Owner enters partner email + permissions (view-only vs. can-add-transactions) → time-limited invite link sent → partner accepts, sets their own password, logs in independently. Owner can revoke access at any time, immediately invalidating active sessions; the partner's previously-added transactions remain, attributed to them.

### 21.4 Category Sharing
Every category has an owner-controlled `is_shared` flag (default private). Partner dashboards/budgets/reports are filtered to shared categories only; if permitted, the partner can add transactions only into shared categories. Net worth, cashback rules, and payment methods stay owner-only regardless of sharing. Savings goals follow the same `is_shared` pattern as categories.

---

## 22. Security and Privacy Requirements

### 22.1 Sensitive Data Rules
Never store: full credit-card number, CVV, bank login credentials, credit-card website credentials, card PIN, security answers, bank API tokens, routing/account numbers.

### 22.2 Encryption
TLS 1.2+ everywhere; bcrypt/argon2 password hashing; provider-managed encryption at rest as baseline; application-layer AES-256-GCM specifically for auth/reset tokens with keys in a secrets manager; no secrets committed to source.

### 22.3 Audit Logs
Login/failed login, transaction create/update/delete, receipt OCR processed, budget changed, payment method created/updated, export generated, AI insight generated, partner invited/revoked, category sharing changed, goal created/updated, account deletion requested/completed.

Fields: User ID, Action, Entity type, Entity ID, Timestamp, IP address (if available), User agent (if available), Metadata JSON.

### 22.4 Data Retention
Receipt images deleted after confirmation, cancellation, OCR failure, or timeout — never stored.

### 22.5 Data Ownership
Export data, delete transactions, delete payment aliases, at any time.

### 22.6 Account Deletion
Owner initiates from Settings, re-enters password, confirms via explicit typed confirmation → immediate soft-delete (account inactive, all sessions revoked) → 30-day grace period (owner can contact support to restore) → hard-delete of transactions/budgets/bills/cashback/net-worth/goals/payment methods after the grace period, with audit log entries retained but anonymized. Deleting the owner account deletes the whole household, including partner access and partner-added data. A partner can independently deactivate only their own login.

---

## 23. Data Model

### 23.1 Users
```sql
users
- id
- email
- password_hash
- display_name
- role                    -- 'owner' | 'partner'
- invited_by_user_id
- email_verified_at
- is_active
- created_at
- updated_at
- last_login_at
```

### 23.2 Partner Permissions
```sql
partner_permissions
- id
- partner_user_id
- can_add_transactions
- created_at
- updated_at
```

### 23.3 Payment Methods
```sql
payment_methods
- id
- user_id
- name
- type                    -- 'Credit Card' | 'Debit Card' | 'Cash' | 'Other' | 'Tracked Savings'
- issuer
- last_four_optional
- due_day_optional
- statement_day_optional
- default_cashback_rate
- current_balance          -- used only for 'Tracked Savings' type, manually updated
- is_active
- created_at
- updated_at
```

### 23.4 Categories
```sql
categories
- id
- user_id
- name
- emoji
- parent_category_id
- category_type           -- 'expense' | 'income'
- is_shared
- is_default
- is_active
- created_at
- updated_at
```

### 23.5 Transactions
```sql
transactions
- id
- user_id
- payment_method_id
- goal_id                 -- nullable, set when a Saving-type transaction contributes to a goal
- date
- merchant
- description
- total_amount             -- negative only when transaction_type = 'Adjustment'
- transaction_type
- source                   -- 'Manual' | 'Receipt OCR' | 'Statement OCR' | 'Adjustment'
- notes
- created_at
- updated_at
```

### 23.6 Transaction Line Items
```sql
transaction_line_items
- id
- transaction_id
- category_id
- item_name
- amount
- quantity
- notes
- created_at
- updated_at
```

### 23.7 Budgets
```sql
budgets
- id
- user_id
- category_id
- month
- year
- budget_amount
- created_at
- updated_at
```

### 23.8 Savings Goals
```sql
savings_goals
- id
- user_id
- name
- target_amount
- current_amount           -- derived from linked transactions
- target_date
- icon
- color
- is_shared
- is_active
- created_at
- updated_at
```

### 23.9 Recurring Bills
```sql
recurring_bills
- id
- user_id
- payment_method_id
- category_id
- name
- amount
- frequency
- due_date
- auto_create_transaction
- reminder_enabled
- is_active
- notes
- created_at
- updated_at
```

### 23.10 Recurring Bill Payments
```sql
recurring_bill_payments
- id
- recurring_bill_id
- due_date
- amount_due
- status                  -- 'upcoming' | 'paid' | 'overdue' | 'skipped'
- paid_date
- transaction_id
- created_at
- updated_at
```

### 23.11 Cashback Rules
```sql
cashback_rules
- id
- user_id
- payment_method_id
- category_id
- cashback_rate
- start_date
- end_date
- notes
- created_at
- updated_at
```

### 23.12 Cashback Records
```sql
cashback_records
- id
- user_id
- transaction_id
- line_item_id
- payment_method_id
- category_id
- estimated_amount
- redeemed_amount
- status
- created_at
- updated_at
```

### 23.13 Net Worth Accounts
```sql
net_worth_accounts
- id
- user_id
- name
- type                    -- 'Asset' | 'Liability'
- is_active
- created_at
- updated_at
```

### 23.14 Net Worth Balances
```sql
net_worth_balances
- id
- account_id
- snapshot_id
- balance
- created_at
```

### 23.15 Net Worth Snapshots
```sql
net_worth_snapshots
- id
- user_id
- snapshot_date
- total_assets
- total_liabilities
- net_worth
- notes
- created_at
- updated_at
```

### 23.16 AI Insights
```sql
ai_insights
- id
- user_id
- insight_type
- message
- supporting_data
- is_dismissed
- generated_at
- created_at
```

### 23.17 Audit Logs
```sql
audit_logs
- id
- user_id
- action
- entity_type
- entity_id
- metadata
- ip_address
- user_agent
- created_at
```

---

## 24. Main Screens

Each screen notes its template origin per §9.

### 24.1 Login / Sign Up
Email/password only. No OTP step.

### 24.2 Email Verification
Link-based confirmation screen.

### 24.3 Dashboard
Stat cards (balance, income, expenses, net change), balance trend chart, category breakdown, budget summary, upcoming bills, cashback earned, AI insights — all real data, no leftover mock widgets.

### 24.4 Add Transaction
Manual entry, scan receipt, import statement/bill.

### 24.5 Receipt Review Screen
Extracted fields, line items, category suggestions, confidence indicator, edit controls, confirm/cancel.

### 24.6 Transactions History
Search, filter by month/category/payment method/amount range, edit, delete, export filtered data.

### 24.7 Budgets
Category budget setup, progress bars, over-budget warnings, month selector.

### 24.8 Savings Goals
Goal list with progress rings, saved/target amounts, add-funds action, contributing transactions.

### 24.9 Recurring Bills
Upcoming list, add/edit, mark paid, create transaction from bill, active toggle.

### 24.10 Cashback
By card, by category, by transaction, estimated/redeemed, manual override.

### 24.11 Net Worth
Manual asset/liability entry, monthly snapshot, trend, breakdown.

### 24.12 Payment Methods & Tracked Balances
List of card aliases and tracked savings/bank balances, add/edit/deactivate, no real linking.

### 24.13 Household
Invite partner, pending invite status, revoke access, category and goal sharing toggles.

### 24.14 Settings
Profile, General, Security, Categories, Payment Methods, Household, Exports, Audit Logs, Account Deletion.

### 24.15 Notifications
Bill reminders, AI insights, partner activity.

---

## 25. API Requirements

### 25.1 Authentication
```http
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/verify-email
POST /auth/password-reset/request
POST /auth/password-reset/confirm
GET /auth/me
```

### 25.2 Payment Methods
```http
GET /payment-methods
POST /payment-methods
GET /payment-methods/{id}
PATCH /payment-methods/{id}
DELETE /payment-methods/{id}
```

### 25.3 Categories
```http
GET /categories
POST /categories
PATCH /categories/{id}
DELETE /categories/{id}
PATCH /categories/{id}/sharing
```

### 25.4 Transactions
```http
GET /transactions
POST /transactions
GET /transactions/{id}
PATCH /transactions/{id}
DELETE /transactions/{id}
```

### 25.5 OCR
```http
POST /ocr/receipt
POST /ocr/statement
POST /ocr/confirm-transaction
```

### 25.6 Budgets
```http
GET /budgets
POST /budgets
PATCH /budgets/{id}
DELETE /budgets/{id}
```

### 25.7 Savings Goals
```http
GET /goals
POST /goals
GET /goals/{id}
PATCH /goals/{id}
DELETE /goals/{id}
POST /goals/{id}/add-funds
PATCH /goals/{id}/sharing
```

### 25.8 Recurring Bills
```http
GET /recurring-bills
POST /recurring-bills
PATCH /recurring-bills/{id}
DELETE /recurring-bills/{id}
POST /recurring-bills/{id}/mark-paid
```

### 25.9 Cashback
```http
GET /cashback
POST /cashback-rules
PATCH /cashback-rules/{id}
DELETE /cashback-rules/{id}
PATCH /cashback-records/{id}
```

### 25.10 Dashboard
```http
GET /dashboard/monthly
GET /dashboard/yearly
GET /dashboard/category-breakdown
GET /dashboard/payment-method-breakdown
GET /dashboard/cash-flow
GET /dashboard/net-worth
GET /dashboard/ai-insights
```

### 25.11 Export
```http
GET /exports/transactions.csv
GET /exports/monthly-report.xlsx
GET /exports/monthly-report.pdf
```

### 25.12 Audit Log
```http
GET /audit-logs
```

### 25.13 Household
```http
POST /household/invite-partner
POST /household/accept-invite
DELETE /household/partner/{id}
PATCH /household/partner/{id}/permissions
```

### 25.14 Account Deletion
```http
POST /account/delete-request
POST /account/delete-confirm
POST /account/delete-cancel
```

---

## 26. Business Logic

```md
Monthly Spending = Sum of all expense transactions in selected month
Category Spending = Sum of transaction line items assigned to category
Budget Usage % = Actual Category Spending / Category Budget × 100
Net Cash Flow = Total Income - Total Expenses
Estimated Cashback (per line item) = Line Item Amount × Cashback Rate for that item's category
Transaction Estimated Cashback = Sum of line item estimated cashback
Net Worth = Total Assets - Total Liabilities
Goal Progress % = Goal Current Amount / Goal Target Amount × 100
```

---

## 27. Edge Cases

### 27.1 Receipt
OCR failure → manual entry fallback. Total/item mismatch → flagged before confirmation. Multi-category receipt → parent + line items. Duplicate → non-blocking warning. Oversized/unsupported file → rejected with a clear message (10MB max, jpg/png/heic/single-page PDF). No date/merchant → user fills in before confirming. Multiple payment methods on one receipt → not supported, split into separate transactions.

### 27.2 Transaction
Negative amount allowed only for Adjustment type. Category/payment method deletion blocked while referenced by transactions — deactivation only. Category change recomputes budgets live. Duplicate entry → warned, not blocked. Month-crossing edits recompute both months.

### 27.3 Budget
No budget set → shown as "no budget set," not a false 0%/100%. Category deleted after a budget exists → historical budget rows remain, category deactivated not deleted. Mid-month change applies going forward only. Each month's budget is stored independently of rollover.

### 27.4 Goals
Goal deleted while linked transactions exist → transactions remain, unlinked (`goal_id` set to null), goal itself is soft-deleted (deactivated) rather than hard-deleted, preserving transaction history integrity. Target date passed without reaching target → dashboard shows "past target date" state, not an error.

### 27.5 Cashback
No rule → $0 estimated. Rule changes mid-month → new rate applies going forward only. Manual override persists, not overwritten by recalculation. Different cards/categories handled correctly since cashback is computed per line item.

### 27.6 Security
Failed logins/reset requests rate-limited. Cross-user data access prevented via `user_id` scoping plus partner category-level filtering, tested explicitly. Receipt image deleted immediately post-OCR regardless of content; failure to delete is an alertable backend error. Export files protected via signed URLs and optional PDF password. Partner revoked mid-session → immediate invalidation. Un-shared category with a partner's pending transaction → stays visible to the partner until confirmed, then follows current sharing state. Household deletion while partner is logged in → partner session ends immediately with a clear message.

### 27.7 Frontend / Template
A screen ported from the template but not yet wired to real data must show a defined empty state, never leftover mock content. Desktop-to-mobile viewport transition at the 768px breakpoint must not lose in-progress form state (e.g. mid-entry Add Transaction). Template components requiring data the new schema doesn't provide (e.g. `/wallets`' live "connected wallet" balance) are not ported as-is — only the repurposed versions defined in §9.2 are built.

---

## 28. UX Requirements

### 28.1 Design Principles
Visually identical to the Ekash template's design language. Fast to use, privacy-focused, dashboard-driven, easy to correct when OCR makes mistakes, clear about what is manually entered vs. AI/OCR suggested.

### 28.2 Desktop/Tablet (≥768px)
Template's icon sidebar (80px, expandable), top header with search, notifications, and profile — as designed, unmodified.

### 28.3 Mobile (<768px)
Bottom navigation (Dashboard, Transactions, Add, Budgets, More), large tap targets, floating quick-add button, camera upload for receipt scan, month/year/card/category selectors, search and filters, swipe-friendly transaction list — built fresh, using the same visual language (colors, cards, typography) as the desktop version.

### 28.4 Navigation

**Sidebar (desktop):** Dashboard, Payment Methods, Budgets, Goals, Recurring Bills, Cashback, Net Worth, Transactions, Household, Settings.

**Bottom nav (mobile):** Dashboard, Transactions, Add, Budgets, More.
**More menu (mobile):** Savings Goals, Recurring Bills, Cashback, Net Worth, Payment Methods, Categories, Household, Exports, Settings, Audit Logs.

---

## 29. AI/OCR Prompting Requirements

### 29.1 Receipt Extraction
```json
{
  "merchant": "Costco",
  "date": "2026-07-05",
  "total": 90.00,
  "tax": 5.20,
  "items": [
    {
      "name": "Chicken",
      "amount": 20.00,
      "suggested_category": "Food",
      "suggested_subcategory": "Grocery",
      "confidence": 0.92
    }
  ],
  "warnings": []
}
```

### 29.2 Category Suggestion Rules
Classifies only into: Housing, Food, Car, Shopping, Health & Personal, Subscription, Saving, Family & Support, Reimbursement, Income. Below 0.6 confidence → `"Uncategorized"`, user selects manually.

### 29.3 AI Insight Prompt Goal
Backend computes totals/trends first; AI explains them — never calculates from raw untrusted text.

---

## 30. Success Metrics

* Manual transaction entry in under 30 seconds; receipt scan + confirm in under 2 minutes
* OCR-confirmed transactions store the correct total, date, merchant, category, payment method
* Category-specific budgets and goal progress viewable at a glance
* Monthly PDF report exportable
* No full card number, CVV, routing number, or account number ever stored
* All create/update/delete actions audit logged
* Partner can accept an invite and log in within 5 minutes
* Partner dashboard never shows a private category or goal, verified by automated test
* Desktop and mobile layouts both fully functional at the 768px breakpoint
* Zero hardcoded/demo values present in the shipped build, verified by an explicit QA pass against the template's original mock content

---

## 31. MVP Acceptance Criteria

**Authentication** — Register/login/logout with email+password only (no OTP); email verified via link; passwords hashed; rate-limited login/reset; users cannot access another user's data.

**Household & Sharing** — Owner can invite a partner; partner accepts and sets their own password; owner marks categories and goals shared/private; partner's views are scoped accordingly; owner can revoke access anytime, invalidating sessions immediately; owner can delete the household account with confirmation and a 30-day grace period.

**Payment Methods** — Owner can create card aliases (no full number/CVV collected, ever) and tracked savings/bank balances (no routing/account numbers collected, ever); can deactivate without losing historical transaction data.

**Transactions** — Full CRUD; category/subcategory/payment method assignment; multi-category receipt splitting; dashboards update after changes.

**OCR** — Upload → extract → AI-suggest → user confirms before save; receipt image never persisted.

**Budgets** — Monthly category budgets that roll forward by default; actual vs. budget shown; over-budget warnings.

**Savings Goals** — Create/edit/delete goals; progress tracked via linked transactions; add-funds action creates a linked transaction; goal sharing follows the category-sharing model.

**Recurring Bills** — Create/edit; upcoming list; mark paid with full per-period history; create transaction from bill.

**Cashback** — Rules by card/category; per-line-item estimates; manual override; monthly/yearly dashboard.

**Net Worth** — Manual asset/liability entry, including tracked balances; monthly snapshots; trend view.

**Exports** — CSV, Excel, and PDF (via signed short-lived link).

**Security** — No bank integration; no full card/account data stored anywhere; audit logs generated for sensitive actions.

**Frontend** — Every screen in §24 implemented; desktop sidebar and mobile bottom-nav both functional; visual match to the Ekash template's design tokens (§8); zero leftover mock/demo data or placeholder names/avatars anywhere in the shipped build.

---

## 32. Future Phase Features

### Phase 2
* Expense splitting/settlement (50/50, custom, percentage; partner balance; settlement history)
* Reimbursement workflow (owed tracking, partial repayment, settled/unsettled status)
* Multi-factor authentication (the template's OTP screens are already built if this becomes a priority)
* Session/device management screen and idle-lock screen (also already built in the template, currently unused)
* Push notifications for bill reminders (needs a native mobile wrapper)
* Per-transaction sharing overrides (finer-grained than category-level)

### Phase 3
Full reimbursement workflow: owed-from tracking, partial repayment, settled/unsettled status, separate cash-flow treatment.

### Phase 4
Advanced AI: merchant normalization, anomaly detection, subscription detection, budget recommendations, natural-language transaction queries.

### Phase 5
Optional import tools without direct bank integration: CSV/PDF statement import, duplicate matching, reconciliation.

### Explicitly not planned, but available in the template if priorities ever change
Multi-currency support, developer API key management, referral/affiliate program, support ticket system, identity/KYC verification. None of these have a current product rationale; they're noted only because the underlying screens already exist in the template source.

---

## 33. Implementation Milestones

### Milestone 1: Foundation
Project setup, database schema, authentication (email/password + link verification, role-based auth from day one), user profile, payment method aliases, default categories.

### Milestone 2: Template Integration
Port the Ekash template into the project exactly as designed for desktop/tablet; strip all hardcoded mock data and replace with empty states; rebrand from Ekash to BillWise; remove the screens listed in §9.5 from navigation and routing.

### Milestone 3: Transaction Core
Manual transaction CRUD, line items, category/payment-method assignment, transaction history filters.

### Milestone 4: Dashboard, Budgets & Goals
Monthly/yearly dashboard, category/payment-method breakdown, budget setup and rollover, savings goals.

### Milestone 5: OCR Flow
Receipt upload, local OCR extraction, cloud AI structuring, review/confirmation screen (net-new UI), temporary file deletion.

### Milestone 6: Recurring Bills & Cashback
Recurring bill CRUD with per-period history, mark-paid, cashback rules, per-line-item estimates, cashback dashboard.

### Milestone 7: Net Worth, AI Insights, Household & Exports
Net worth accounts/balances/snapshots, AI insights, partner invite flow, category/goal sharing, CSV/Excel/PDF export.

### Milestone 8: Mobile Layout
Bottom-navigation layout for <768px viewports, built against the same component library and design tokens as the desktop build.

### Milestone 9: Security Hardening
Audit logs, authorization testing (including automated verification that a partner cannot see unshared data), data validation, upload security, encryption review, account deletion flow, production deployment checklist, final mock-data QA sweep.

---

## 34. Final MVP Definition

BillWise MVP is complete when the owner can:

1. Log in securely with email and password (no OTP)
2. Invite a partner, who can log in independently
3. Control exactly which categories and goals the partner can see
4. Revoke partner access at any time
5. Create card aliases and tracked savings/bank balances, with no sensitive card or bank data ever collected
6. Add expenses manually
7. Scan receipts and confirm OCR results
8. Categorize transactions, including splitting one receipt across multiple categories
9. View monthly and yearly dashboards
10. View category and payment method breakdowns
11. Set monthly category budgets that roll forward automatically
12. Create and track savings goals
13. Track recurring bills with full per-period payment history
14. Track cashback accurately per line item, manually and by rule
15. View cash flow
16. Track manual net worth snapshots
17. Receive AI spending insights
18. Export CSV, Excel, and PDF reports securely
19. Delete the household account through a confirmed, grace-period flow
20. Use the app on both desktop (template sidebar) and mobile (bottom nav) with a fully consistent visual identity
21. Trust that nothing in the shipped product is leftover template demo data
