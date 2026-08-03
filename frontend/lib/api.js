const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

/**
 * ApiError carries the HTTP status alongside the backend's `detail` message so
 * callers can branch on status (e.g. 403 "email not verified" vs 401 "invalid
 * credentials") without re-parsing the response.
 */
export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed with status ${status}`)
    this.status = status
  }
}

// FastAPI's `detail` is either a plain string (explicit HTTPException(detail=...))
// or a Pydantic validation array of {loc, msg, type} objects (422s raised by
// schema validation itself). Without this, the array case reaches the Error
// constructor as-is and stringifies to the useless "[object Object]".
function formatDetail(detail) {
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || String(item)).join("; ")
  }
  return null
}

async function throwIfError(response) {
  if (response.ok) return
  let detail = null
  try {
    const body = await response.json()
    detail = formatDetail(body.detail)
  } catch {
    // Non-JSON error body — fall back to the generic status message.
  }
  throw new ApiError(response.status, detail)
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  await throwIfError(response)
  const data = response.status === 204 ? null : await response.json()
  return options.includeHeaders ? { data, headers: response.headers } : data
}

// No Content-Type header here — the browser sets the multipart boundary itself
// when the body is a FormData instance.
async function requestMultipart(path, formData) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    credentials: "include",
    body: formData,
  })

  await throwIfError(response)
  return response.json()
}

export const authApi = {
  register: (email, password, displayName) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName }),
    }),
  verifyEmail: (token) =>
    request("/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request("/auth/logout", { method: "POST" }),
  me: () => request("/auth/me"),
  updateProfile: (displayName) =>
    request("/auth/me", { method: "PATCH", body: JSON.stringify({ display_name: displayName }) }),
  changePassword: (currentPassword, newPassword) =>
    request("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),
  requestPasswordReset: (email) =>
    request("/auth/password-reset/request", { method: "POST", body: JSON.stringify({ email }) }),
  confirmPasswordReset: (token, newPassword) =>
    request("/auth/password-reset/confirm", {
      method: "POST",
      body: JSON.stringify({ token, new_password: newPassword }),
    }),
}

export const categoriesApi = {
  list: () => request("/categories"),
  create: (data) => request("/categories", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/categories/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  updateSharing: (id, isShared) =>
    request(`/categories/${id}/sharing`, { method: "PATCH", body: JSON.stringify({ is_shared: isShared }) }),
  remove: (id) => request(`/categories/${id}`, { method: "DELETE" }),
}

export const paymentMethodsApi = {
  list: () => request("/payment-methods"),
  create: (data) => request("/payment-methods", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/payment-methods/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/payment-methods/${id}`, { method: "DELETE" }),
}

function buildTransactionsQuery(params) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") search.set(key, value)
  })
  return search.toString()
}

export const transactionsApi = {
  list: (params = {}) => {
    const query = buildTransactionsQuery(params)
    return request(`/transactions${query ? `?${query}` : ""}`)
  },
  // Same filters as list(), plus limit/offset -- returns { items, total } by
  // reading the X-Total-Count header the backend only sends when limit is set.
  listPage: (params = {}, { limit, offset = 0 } = {}) => {
    const query = buildTransactionsQuery({ ...params, limit, offset })
    return request(`/transactions${query ? `?${query}` : ""}`, { includeHeaders: true }).then(({ data, headers }) => ({
      items: data,
      total: Number(headers.get("X-Total-Count") ?? data.length),
    }))
  },
  get: (id) => request(`/transactions/${id}`),
  create: (data) => request("/transactions", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/transactions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/transactions/${id}`, { method: "DELETE" }),
  merchants: () => request("/transactions/merchants"),
}

export const budgetsApi = {
  list: (month, year) => request(`/budgets?month=${month}&year=${year}`),
  create: (data) => request("/budgets", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/budgets/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/budgets/${id}`, { method: "DELETE" }),
}

export const goalsApi = {
  list: () => request("/goals"),
  create: (data) => request("/goals", { method: "POST", body: JSON.stringify(data) }),
  get: (id) => request(`/goals/${id}`),
  update: (id, data) => request(`/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  updateSharing: (id, isShared) =>
    request(`/goals/${id}/sharing`, { method: "PATCH", body: JSON.stringify({ is_shared: isShared }) }),
  remove: (id) => request(`/goals/${id}`, { method: "DELETE" }),
  addFunds: (id, data) => request(`/goals/${id}/add-funds`, { method: "POST", body: JSON.stringify(data) }),
}

export const recurringBillsApi = {
  list: () => request("/recurring-bills"),
  create: (data) => request("/recurring-bills", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/recurring-bills/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/recurring-bills/${id}`, { method: "DELETE" }),
  markPaid: (id, data) => request(`/recurring-bills/${id}/mark-paid`, { method: "POST", body: JSON.stringify(data) }),
}

export const cashbackApi = {
  listRules: () => request("/cashback-rules"),
  createRule: (data) => request("/cashback-rules", { method: "POST", body: JSON.stringify(data) }),
  updateRule: (id, data) => request(`/cashback-rules/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  removeRule: (id) => request(`/cashback-rules/${id}`, { method: "DELETE" }),
  updateRecord: (id, data) => request(`/cashback-records/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  summary: (year, month) => {
    const search = new URLSearchParams({ year: String(year) })
    if (month) search.set("month", String(month))
    return request(`/cashback?${search.toString()}`)
  },
}

export const ocrApi = {
  scanReceipt: (file) => {
    const formData = new FormData()
    formData.append("file", file)
    return requestMultipart("/ocr/receipt", formData)
  },
  scanStatement: (file) => {
    const formData = new FormData()
    formData.append("file", file)
    return requestMultipart("/ocr/statement", formData)
  },
  confirmTransaction: (data) =>
    request("/ocr/confirm-transaction", { method: "POST", body: JSON.stringify(data) }),
}

export const dashboardApi = {
  monthly: (month, year) => request(`/dashboard/monthly?month=${month}&year=${year}`),
  yearly: (year) => request(`/dashboard/yearly?year=${year}`),
  categoryBreakdown: (month, year) => request(`/dashboard/category-breakdown?month=${month}&year=${year}`),
  paymentMethodBreakdown: (month, year) => request(`/dashboard/payment-method-breakdown?month=${month}&year=${year}`),
  cashFlow: (month, year) => request(`/dashboard/cash-flow?month=${month}&year=${year}`),
  aiInsights: () => request("/dashboard/ai-insights"),
}

export const aiInsightsApi = {
  dismiss: (id) => request(`/ai-insights/${id}`, { method: "PATCH", body: JSON.stringify({ is_dismissed: true }) }),
}

export const notificationsApi = {
  list: () => request("/notifications"),
  acknowledge: (key) => request("/notifications/acknowledge", { method: "POST", body: JSON.stringify({ key }) }),
}

export const householdApi = {
  get: () => request("/household"),
  invitePartner: (email, canAddTransactions) =>
    request("/household/invite-partner", {
      method: "POST",
      body: JSON.stringify({ email, can_add_transactions: canAddTransactions }),
    }),
  acceptInvite: (token, password, displayName) =>
    request("/household/accept-invite", {
      method: "POST",
      body: JSON.stringify({ token, password, display_name: displayName }),
    }),
  removePartner: (id) => request(`/household/partner/${id}`, { method: "DELETE" }),
  updatePermissions: (id, canAddTransactions) =>
    request(`/household/partner/${id}/permissions`, {
      method: "PATCH",
      body: JSON.stringify({ can_add_transactions: canAddTransactions }),
    }),
}

export const exportsApi = {
  transactionsCsv: () => request("/exports/transactions.csv"),
  monthlyReportXlsx: (month, year) => request(`/exports/monthly-report.xlsx?month=${month}&year=${year}`),
  monthlyReportPdf: (month, year, password) => {
    const search = new URLSearchParams({ month: String(month), year: String(year) })
    if (password) search.set("password", password)
    return request(`/exports/monthly-report.pdf?${search.toString()}`)
  },
  // The download link's `download_url` is a short-lived signed backend path
  // (PRD §20.4), not an already-absolute URL — resolve it against the same
  // API origin every other request in this file uses.
  downloadUrl: (path) => `${API_BASE_URL}${path}`,
}

export const netWorthApi = {
  listAccounts: () => request("/net-worth-accounts"),
  createAccount: (data) => request("/net-worth-accounts", { method: "POST", body: JSON.stringify(data) }),
  updateAccount: (id, data) => request(`/net-worth-accounts/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  removeAccount: (id) => request(`/net-worth-accounts/${id}`, { method: "DELETE" }),
  listSnapshots: () => request("/net-worth-snapshots"),
  createSnapshot: (data) => request("/net-worth-snapshots", { method: "POST", body: JSON.stringify(data) }),
}
