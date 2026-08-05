import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models._common import required_timestamp_field


class Merchant(SQLModel, table=True):
    __tablename__ = "merchants"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str = Field(index=True)
    # Free-text, same convention as Category.name -- not a fixed enum. The
    # transaction/cashback-rule merchant pickers group by whatever distinct
    # values exist; null buckets under "Other".
    type: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    # Defaults True, unlike every other shareable resource in this codebase
    # (Category/PaymentMethod/Budget/Goal/RecurringBill all default False) --
    # a merchant name is low-sensitivity shared reference data, not a
    # financial instrument, and a quick-added merchant should show up in the
    # picker for both household members immediately rather than needing an
    # extra sharing-toggle click for something this low-stakes.
    is_shared: bool = True
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
