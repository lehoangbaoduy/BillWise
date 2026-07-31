import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class CashbackRecordStatus(StrEnum):
    ESTIMATED = "estimated"
    REDEEMED = "redeemed"


class CashbackRule(SQLModel, table=True):
    __tablename__ = "cashback_rules"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    payment_method_id: uuid.UUID = Field(foreign_key="payment_methods.id", nullable=False, index=True)
    # Null category_id = the payment method's default rate (PRD §17.2). A
    # category-specific rule (category_id set) takes precedence over the
    # default when both are in effect for the same date.
    category_id: uuid.UUID | None = Field(default=None, foreign_key="categories.id")
    cashback_rate: Decimal
    start_date: date_type
    end_date: date_type | None = None
    notes: str | None = None
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class CashbackRecord(SQLModel, table=True):
    __tablename__ = "cashback_records"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    transaction_id: uuid.UUID = Field(foreign_key="transactions.id", nullable=False, index=True, ondelete="CASCADE")
    line_item_id: uuid.UUID = Field(foreign_key="transaction_line_items.id", nullable=False, index=True, ondelete="CASCADE")
    payment_method_id: uuid.UUID = Field(foreign_key="payment_methods.id", nullable=False)
    category_id: uuid.UUID = Field(foreign_key="categories.id", nullable=False)
    estimated_amount: Decimal
    redeemed_amount: Decimal = Decimal("0")
    status: CashbackRecordStatus = enum_field(CashbackRecordStatus)
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
