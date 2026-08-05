import uuid

from sqlmodel import or_, select
from sqlmodel.sql.expression import SelectOfScalar

from app.models.category import Category
from app.models.transaction import Transaction, TransactionLineItem
from app.models.transaction_share import TransactionShare
from app.models.user import User, UserRole


def shared_category_ids_subquery(owner_id: uuid.UUID) -> SelectOfScalar:
    return select(Category.id).where(Category.user_id == owner_id, Category.is_shared == True)  # noqa: E712


def _private_touching_transaction_ids_subquery(owner_id: uuid.UUID) -> SelectOfScalar:
    private_category_ids = select(Category.id).where(Category.user_id == owner_id, Category.is_shared == False)  # noqa: E712
    return select(TransactionLineItem.transaction_id).where(TransactionLineItem.category_id.in_(private_category_ids))


def _shares_with_user_subquery(user_id: uuid.UUID) -> SelectOfScalar:
    return select(TransactionShare.transaction_id).where(TransactionShare.shared_with_user_id == user_id)


def apply_partner_transaction_visibility(conditions: list, user: User, owner_id: uuid.UUID) -> None:
    """Appends a condition excluding any transaction that touches a private
    category, in place, when the user is a partner. A transaction is excluded
    outright rather than partially redacted, since showing a subset of line
    items under the real total_amount would itself leak that a hidden
    private-category amount exists.

    Exception: a transaction the partner has been explicitly given a
    cost-split share on (PRD §7.5) stays visible regardless of the
    category's privacy -- naming someone as a split recipient is itself an
    explicit disclosure of that specific transaction to them, so hiding it
    would make their own share both unsettleable (no row to act on in
    Transaction History) and invisible from their own spend/budget totals.

    Shared across transactions.py and dashboard.py to keep the visibility
    rule from drifting between the transaction list and dashboard/budget
    aggregates."""
    if user.role == UserRole.PARTNER:
        conditions.append(
            or_(
                Transaction.id.not_in(_private_touching_transaction_ids_subquery(owner_id)),
                Transaction.id.in_(_shares_with_user_subquery(user.id)),
            )
        )
