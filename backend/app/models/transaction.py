import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class TransactionType(StrEnum):
    EXPENSE = "Expense"
    INCOME = "Income"
    SAVING_EXPENSE = "Saving expense"
    ADJUSTMENT = "Adjustment"


class TransactionSource(StrEnum):
    MANUAL = "Manual"
    RECEIPT_OCR = "Receipt OCR"
    STATEMENT_OCR = "Statement OCR"
    ADJUSTMENT = "Adjustment"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    payment_method_id: uuid.UUID = Field(foreign_key="payment_methods.id", nullable=False)
    date: date_type
    merchant: str
    description: str | None = None
    total_amount: Decimal
    transaction_type: TransactionType = enum_field(TransactionType)
    source: TransactionSource = enum_field(TransactionSource)
    notes: str | None = None
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class TransactionLineItem(SQLModel, table=True):
    __tablename__ = "transaction_line_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_id: uuid.UUID = Field(foreign_key="transactions.id", nullable=False, index=True, ondelete="CASCADE")
    category_id: uuid.UUID = Field(foreign_key="categories.id", nullable=False, index=True)
    item_name: str
    amount: Decimal
    quantity: Decimal | None = Decimal("1")
    notes: str | None = None
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
