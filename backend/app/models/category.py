import uuid
from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class CategoryType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str
    emoji: str | None = None
    parent_category_id: uuid.UUID | None = Field(default=None, foreign_key="categories.id")
    category_type: CategoryType = enum_field(CategoryType)
    # Unlike Budget/Goal/PaymentMethod/RecurringBill, a Category has no real
    # private state anymore -- every category is visible and manageable by
    # every household member. The column stays (rather than being dropped)
    # so existing rows/migrations aren't disturbed, but it is always True.
    is_shared: bool = True
    is_default: bool = False
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
