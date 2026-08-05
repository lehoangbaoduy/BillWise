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
    # Free-text merchant name (not a foreign key -- merchants aren't a managed
    # entity, just whatever string a transaction's merchant field holds). A
    # merchant-specific rule outranks a category-specific one when resolving a
    # rate, since "this exact merchant" is more specific than "this category."
    merchant: str | None = Field(default=None, max_length=200, index=True)
    # Alternative to `merchant`, mutually exclusive with it (enforced in the
    # schema + update endpoint): targets every merchant of a given Merchant.type
    # (backend/app/models/merchant.py) rather than one specific merchant name.
    # Resolved at match time via a case-insensitive Merchant.name lookup against
    # the transaction's merchant string -- no FK, since Transaction.merchant
    # stays a plain string. Outranks a category rule but not a merchant-name
    # rule, on the same "more specific wins" principle.
    merchant_type: str | None = Field(default=None, max_length=100, index=True)
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
    # Null when no rule matched (rate defaulted to 0), distinct from matching a
    # rule whose own rate happens to be 0 -- lets the frontend show a "no
    # matching cashback rule" hint only in the former case (PRD v2 §5.4).
    cashback_rule_id: uuid.UUID | None = Field(default=None, foreign_key="cashback_rules.id", ondelete="SET NULL")
    estimated_amount: Decimal
    redeemed_amount: Decimal = Decimal("0")
    status: CashbackRecordStatus = enum_field(CashbackRecordStatus)
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
