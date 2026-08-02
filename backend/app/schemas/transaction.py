import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionSource, TransactionType


class TransactionLineItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: uuid.UUID
    item_name: str = Field(min_length=1, max_length=200)
    amount: Decimal
    quantity: Decimal | None = Decimal("1")
    notes: str | None = Field(default=None, max_length=1000)


class TransactionLineItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    item_name: str
    amount: Decimal
    quantity: Decimal | None
    notes: str | None


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID
    goal_id: uuid.UUID | None = None
    date: date_type
    merchant: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    total_amount: Decimal
    transaction_type: TransactionType
    notes: str | None = Field(default=None, max_length=1000)
    line_items: list[TransactionLineItemCreate] = Field(min_length=1)


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID | None = None
    goal_id: uuid.UUID | None = None
    date: date_type | None = None
    merchant: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    total_amount: Decimal | None = None
    transaction_type: TransactionType | None = None
    notes: str | None = Field(default=None, max_length=1000)
    line_items: list[TransactionLineItemCreate] | None = Field(default=None, min_length=1)


class TransactionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_method_id: uuid.UUID
    goal_id: uuid.UUID | None
    date: date_type
    merchant: str
    description: str | None
    total_amount: Decimal
    transaction_type: TransactionType
    source: TransactionSource
    notes: str | None
    line_items: list[TransactionLineItemPublic]
    possible_duplicate: bool = False
    created_by_user_id: uuid.UUID | None = None
