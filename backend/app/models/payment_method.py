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
    name: str
    type: PaymentMethodType = enum_field(PaymentMethodType)
    issuer: str | None = None
    last_four_optional: str | None = Field(default=None, max_length=4)
    due_day_optional: int | None = None
    statement_day_optional: int | None = None
    default_cashback_rate: Decimal | None = None
    current_balance: Decimal | None = None
    color: str | None = Field(default=None, max_length=7)
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
