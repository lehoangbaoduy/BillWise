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

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!response.ok) {
    let detail = null
    try {
      const body = await response.json()
      detail = body.detail
    } catch {
      // Non-JSON error body — fall back to the generic status message.
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) return null
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
