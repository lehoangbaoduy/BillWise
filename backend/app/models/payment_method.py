import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class PaymentMethodType(StrEnum):
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    CASH = "Cash"
    OTHER = "Other"
    TRACKED_SAVINGS = "Tracked Savings"


class PaymentMethod(SQLModel, table=True):
    __tablename__ = "payment_methods"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    # user_id is always the household owner's id (see app.api.deps.household_owner_id).
    # created_by_user_id separately records which household member actually created
    # this wallet -- null when the owner created it, set to the acting user's id
    # when a co-owner did. Private-item visibility is scoped to this creator, not
    # to user_id, since user_id is shared by every member of the household.
    created_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    name: str
    type: PaymentMethodType = enum_field(PaymentMethodType)
    issuer: str | None = None
    last_four_optional: str | None = Field(default=None, max_length=4)
    due_day_optional: int | None = None
    statement_day_optional: int | None = None
    default_cashback_rate: Decimal | None = None
    current_balance: Decimal | None = None
    color: str | None = Field(default=None, max_length=7)
    is_shared: bool = False
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
