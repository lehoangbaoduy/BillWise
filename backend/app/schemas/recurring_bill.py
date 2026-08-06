import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.recurring_bill import RecurringBillPaymentStatus, RecurringFrequency


class RecurringBillCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID
    category_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0)
    frequency: RecurringFrequency
    due_date: date_type | None = None
    auto_create_transaction: bool = False
    reminder_enabled: bool = False
    is_shared: bool = False
    notes: str | None = Field(default=None, max_length=1000)


class RecurringBillUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0)
    frequency: RecurringFrequency | None = None
    due_date: date_type | None = None
    auto_create_transaction: bool | None = None
    reminder_enabled: bool | None = None
    notes: str | None = Field(default=None, max_length=1000)


class RecurringBillSharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class MarkPaidRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paid_date: date_type | None = None
    amount_paid: Decimal | None = Field(default=None, gt=0)


class RecurringBillPaymentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    due_date: date_type
    amount_due: Decimal
    status: RecurringBillPaymentStatus
    paid_date: date_type | None
    transaction_id: uuid.UUID | None


class RecurringBillPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_method_id: uuid.UUID
    category_id: uuid.UUID
    name: str
    amount: Decimal
    frequency: RecurringFrequency
    due_date: date_type
    auto_create_transaction: bool
    reminder_enabled: bool
    is_shared: bool
    is_active: bool
    notes: str | None
    created_by_user_id: uuid.UUID | None
    current_period: RecurringBillPaymentPublic | None
    payments: list[RecurringBillPaymentPublic]
