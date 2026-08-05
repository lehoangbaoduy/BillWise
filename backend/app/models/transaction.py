import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, optional_timestamp_field, required_timestamp_field


class TransactionType(StrEnum):
    EXPENSE = "Expense"
    INCOME = "Income"
    SAVING_EXPENSE = "Saving expense"
    ADJUSTMENT = "Adjustment"
    REIMBURSEMENT = "Reimbursement"


class ReimbursementStatus(StrEnum):
    UNPAID = "unpaid"
    PAID = "paid"


class TransactionSource(StrEnum):
    MANUAL = "Manual"
    RECEIPT_OCR = "Receipt OCR"
    STATEMENT_OCR = "Statement OCR"
    ADJUSTMENT = "Adjustment"
    RECURRING_BILL = "Recurring Bill"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    # The household this transaction's data belongs to (owner's id, always — see
    # app.api.deps.household_owner_id). created_by_user_id separately records who
    # actually entered it: null for the owner, the partner's own id for a
    # partner-entered transaction. PRD §21.3: revoking a partner's access doesn't
    # remove or reassign their past transactions — this column is what lets that
    # attribution survive the revoke.
    created_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    payment_method_id: uuid.UUID = Field(foreign_key="payment_methods.id", nullable=False)
    goal_id: uuid.UUID | None = Field(default=None, foreign_key="savings_goals.id", index=True)
    date: date_type
    merchant: str
    description: str | None = None
    total_amount: Decimal
    transaction_type: TransactionType = enum_field(TransactionType)
    source: TransactionSource = enum_field(TransactionSource)
    notes: str | None = None
    # Only meaningful when transaction_type == REIMBURSEMENT; unused/default
    # otherwise. Plain string rather than enum_field's native Postgres ENUM —
    # this only ever has two fixed values, so a check-constraint-free VARCHAR
    # avoids the ALTER TYPE ADD VALUE migration class of bug entirely.
    reimbursement_status: str = Field(default=ReimbursementStatus.UNPAID.value)
    reimbursement_paid_by: str | None = None
    reimbursement_paid_at: datetime | None = optional_timestamp_field()
    # PRD v2 §7.2: set only for a transaction saved via the OCR-fail fallback
    # that successfully uploaded its receipt image to R2 -- null for every
    # other transaction, including successfully-OCR'd ones (explicit scope
    # decision: retention is failure-path-only, not applied to the success
    # path). References receipt_storage_service's object key, never a URL.
    receipt_image_key: str | None = None
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
