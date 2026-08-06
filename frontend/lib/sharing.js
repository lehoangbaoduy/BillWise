// Wallets/Budgets/Goals/RecurringBills all use the same private/shared model:
// created_by_user_id is null when the household owner created the item (see
// e.g. PaymentMethod.created_by_user_id's docstring server-side), so a plain
// partner is never the "owner" -- only an actual owner user can be the
// implicit creator of a null-created_by_user_id item.
export function isItemCreator(user, item) {
  if (!user || !item) return false
  return item.created_by_user_id ? item.created_by_user_id === user.id : user.role === "owner"
}

export const VISIBILITY_TABS = [
  { value: "all", label: "All" },
  { value: "shared", label: "Shared" },
  { value: "private", label: "Private" },
]

// "All" sorts shared items first, then private -- Array.prototype.sort is
// stable in every JS engine this app runs on, so within each group the
// original (API) order is preserved rather than getting shuffled.
export function filterByVisibility(items, filter) {
  const sorted = [...items].sort((a, b) => Number(b.is_shared) - Number(a.is_shared))
  if (filter === "shared") return sorted.filter((item) => item.is_shared)
  if (filter === "private") return sorted.filter((item) => !item.is_shared)
  return sorted
}
