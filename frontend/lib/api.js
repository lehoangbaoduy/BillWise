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

async function throwIfError(response) {
  if (response.ok) return
  let detail = null
  try {
    const body = await response.json()
    detail = body.detail
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
  if (response.status === 204) return null
  return response.json()
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
  remove: (id) => request(`/categories/${id}`, { method: "DELETE" }),
}

export const paymentMethodsApi = {
  list: () => request("/payment-methods"),
  create: (data) => request("/payment-methods", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/payment-methods/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/payment-methods/${id}`, { method: "DELETE" }),
}

export const transactionsApi = {
  list: (params = {}) => {
    const search = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== "") search.set(key, value)
    })
    const query = search.toString()
    return request(`/transactions${query ? `?${query}` : ""}`)
  },
  get: (id) => request(`/transactions/${id}`),
  create: (data) => request("/transactions", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/transactions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id) => request(`/transactions/${id}`, { method: "DELETE" }),
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
}
