import uuid

from sqlmodel import and_, or_
from sqlmodel.sql.expression import ColumnElement

from app.models.user import User


def effective_creator_id(item_created_by_user_id: uuid.UUID | None, owner_id: uuid.UUID) -> uuid.UUID:
    """created_by_user_id is null when the household owner created the item (see
    e.g. PaymentMethod.created_by_user_id's docstring) -- resolve that back to the
    owner's id so callers always have a concrete user to compare against."""
    return item_created_by_user_id if item_created_by_user_id is not None else owner_id


def user_can_access_item(
    is_shared: bool, item_created_by_user_id: uuid.UUID | None, owner_id: uuid.UUID, user: User
) -> bool:
    """Applies to Wallets (PaymentMethod), Budgets, Goals, and RecurringBills.
    A private item is visible and usable only by the household member who
    created it -- not even the owner can see a co-owner's private item, and
    vice versa. A shared item is visible to any owner/co-owner household
    member. Category deliberately keeps its own, separate is_shared semantics
    (plain-partner-visible vs not) and is not part of this model."""
    if is_shared:
        return True
    return effective_creator_id(item_created_by_user_id, owner_id) == user.id


def visibility_condition(model, owner_id: uuid.UUID, user: User) -> ColumnElement:
    """SQL-level equivalent of user_can_access_item, for filtering list queries.
    `model` must be a SQLModel class with is_shared and created_by_user_id columns."""
    is_creator = or_(
        model.created_by_user_id == user.id,
        and_(model.created_by_user_id.is_(None), user.id == owner_id),
    )
    return or_(model.is_shared == True, is_creator)  # noqa: E712
