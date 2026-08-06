// Wallets/Budgets/Goals/RecurringBills all use the same private/shared model:
// created_by_user_id is null when the household owner created the item (see
// e.g. PaymentMethod.created_by_user_id's docstring server-side), so a plain
// partner is never the "owner" -- only an actual owner user can be the
// implicit creator of a null-created_by_user_id item.
export function isItemCreator(user, item) {
  if (!user || !item) return false
  return item.created_by_user_id ? item.created_by_user_id === user.id : user.role === "owner"
}
