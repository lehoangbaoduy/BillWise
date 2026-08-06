"""Default category tree seeded for every new owner account (PRD §10).

Every category has category_type expense|income. Categories are always shared
across the household -- unlike Wallets/Budgets/Goals/RecurringBills, there is
no private/shared distinction for categories, so is_shared is always True.
"""

import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.category import Category, CategoryType

# (name, emoji, [(child_name, child_emoji, [grandchild_names...]), ...])
_EXPENSE_TREE: list[tuple[str, str, list]] = [
    ("Housing", "🏠", [("Rent", None, []), ("Utilities", "🛠", ["Electric", "Water", "Gas", "Wifi"])]),
    ("Food", "🍔", [("Grocery", None, []), ("Restaurant", None, [])]),
    ("Car", "🚗", [("Insurance", None, []), ("Gas", None, [])]),
    ("Shopping", "🛍️", []),
    ("Health & Personal", "💊", []),
    ("Subscription", "📱", []),
    ("Saving", "💰", []),
    ("Family & Support", "👨‍👩‍👧", []),
]

_INCOME_TREE: list[tuple[str, str, list]] = [
    ("Income", "💼", [("Paycheck", None, []), ("Other Income", None, [])]),
]


async def _create(session: AsyncSession, user_id: uuid.UUID, name: str, emoji: str | None,
                   category_type: CategoryType, parent_id: uuid.UUID | None) -> Category:
    category = Category(
        user_id=user_id,
        name=name,
        emoji=emoji,
        parent_category_id=parent_id,
        category_type=category_type,
        is_shared=True,
        is_default=True,
        is_active=True,
    )
    session.add(category)
    await session.flush()
    return category


async def _seed_tree(session: AsyncSession, user_id: uuid.UUID, tree: list[tuple[str, str, list]],
                      category_type: CategoryType) -> None:
    for name, emoji, children in tree:
        parent = await _create(session, user_id, name, emoji, category_type, None)
        for child_name, child_emoji, grandchildren in children:
            child = await _create(session, user_id, child_name, child_emoji, category_type, parent.id)
            for grandchild_name in grandchildren:
                await _create(session, user_id, grandchild_name, None, category_type, child.id)


async def seed_default_categories(session: AsyncSession, user_id: uuid.UUID) -> None:
    await _seed_tree(session, user_id, _EXPENSE_TREE, CategoryType.EXPENSE)
    await _seed_tree(session, user_id, _INCOME_TREE, CategoryType.INCOME)
