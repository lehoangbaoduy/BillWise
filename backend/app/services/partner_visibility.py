import uuid

from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from app.models.category import Category
from app.models.transaction import Transaction, TransactionLineItem
from app.models.user import User, UserRole


def shared_category_ids_subquery(owner_id: uuid.UUID) -> SelectOfScalar:
    return select(Category.id).where(Category.user_id == owner_id, Category.is_shared == True)  # noqa: E712


def _private_touching_transaction_ids_subquery(owner_id: uuid.UUID) -> SelectOfScalar:
    private_category_ids = select(Category.id).where(Category.user_id == owner_id, Category.is_shared == False)  # noqa: E712
    return select(TransactionLineItem.transaction_id).where(TransactionLineItem.category_id.in_(private_category_ids))


def apply_partner_transaction_visibility(conditions: list, user: User, owner_id: uuid.UUID) -> None:
    """Appends a condition excluding any transaction that touches a private
    category, in place, when the user is a partner. A transaction is excluded
    outright rather than partially redacted, since showing a subset of line
    items under the real total_amount would itself leak that a hidden
    private-category amount exists. Shared across transactions.py and
    dashboard.py to keep the visibility rule from drifting between the
    transaction list and dashboard/budget aggregates."""
    if user.role == UserRole.PARTNER:
        conditions.append(Transaction.id.not_in(_private_touching_transaction_ids_subquery(owner_id)))
