import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class RecurringFrequency(StrEnum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurringBillPaymentStatus(StrEnum):
    UPCOMING = "upcoming"
    PAID = "paid"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class RecurringBill(SQLModel, table=True):
    __tablename__ = "recurring_bills"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    # user_id is always the household owner's id (see app.api.deps.household_owner_id).
    # created_by_user_id separately records which household member actually created
    # this bill -- null when the owner created it, set to the acting user's id when a
    # co-owner did. Private-item visibility is scoped to this creator, not to user_id.
    created_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    payment_method_id: uuid.UUID = Field(foreign_key="payment_methods.id", nullable=False)
    category_id: uuid.UUID = Field(foreign_key="categories.id", nullable=False)
    name: str
    amount: Decimal
    frequency: RecurringFrequency = enum_field(RecurringFrequency)
    due_date: date_type
    auto_create_transaction: bool = False
    reminder_enabled: bool = False
    is_shared: bool = False
    is_active: bool = True
    notes: str | None = None
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class RecurringBillPayment(SQLModel, table=True):
    __tablename__ = "recurring_bill_payments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    recurring_bill_id: uuid.UUID = Field(foreign_key="recurring_bills.id", nullable=False, index=True)
    due_date: date_type
    amount_due: Decimal
    status: RecurringBillPaymentStatus = enum_field(RecurringBillPaymentStatus)
    paid_date: date_type | None = None
    transaction_id: uuid.UUID | None = Field(default=None, foreign_key="transactions.id")
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
