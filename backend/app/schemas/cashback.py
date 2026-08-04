import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cashback import CashbackRecordStatus


class CashbackRuleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID
    category_id: uuid.UUID | None = None
    # min_length=2: cashback_service.resolve_cashback_rate now matches a rule's
    # merchant as a substring of the transaction's merchant rather than an exact
    # match (so "Costco" matches "COSTCO WHSE #1234") -- a 1-character merchant
    # would then match almost any transaction, silently misapplying its rate.
    merchant: str | None = Field(default=None, min_length=2, max_length=200)
    cashback_rate: Decimal = Field(ge=0, le=100)
    start_date: date_type
    end_date: date_type | None = None
    notes: str | None = Field(default=None, max_length=1000)


class CashbackRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: uuid.UUID | None = None
    # min_length=2: cashback_service.resolve_cashback_rate now matches a rule's
    # merchant as a substring of the transaction's merchant rather than an exact
    # match (so "Costco" matches "COSTCO WHSE #1234") -- a 1-character merchant
    # would then match almost any transaction, silently misapplying its rate.
    merchant: str | None = Field(default=None, min_length=2, max_length=200)
    cashback_rate: Decimal | None = Field(default=None, ge=0, le=100)
    start_date: date_type | None = None
    end_date: date_type | None = None
    notes: str | None = Field(default=None, max_length=1000)


class CashbackRulePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_method_id: uuid.UUID
    category_id: uuid.UUID | None
    merchant: str | None
    cashback_rate: Decimal
    start_date: date_type
    end_date: date_type | None
    notes: str | None
    # Derived from the linked payment method, not its own stored field -- a
    # cashback rule tied to a private wallet is automatically private, since
    # nobody but that wallet's creator could ever earn against it anyway.
    is_shared: bool


class CashbackRecordUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estimated_amount: Decimal | None = Field(default=None, ge=0)
    redeemed_amount: Decimal | None = Field(default=None, ge=0)
    status: CashbackRecordStatus | None = None


class CashbackRecordPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    transaction_id: uuid.UUID
    line_item_id: uuid.UUID
    payment_method_id: uuid.UUID
    category_id: uuid.UUID
    estimated_amount: Decimal
    redeemed_amount: Decimal
    status: CashbackRecordStatus
    # Derived from the linked payment method -- see CashbackRulePublic.is_shared.
    is_shared: bool


class CashbackCardSummary(BaseModel):
    payment_method_id: uuid.UUID
    name: str
    estimated: Decimal
    redeemed: Decimal


class CashbackCategorySummary(BaseModel):
    category_id: uuid.UUID
    name: str
    estimated: Decimal
    redeemed: Decimal


class CashbackSummary(BaseModel):
    year: int
    month: int | None
    total_estimated: Decimal
    total_redeemed: Decimal
    total_unredeemed: Decimal
    by_card: list[CashbackCardSummary]
    by_category: list[CashbackCategorySummary]
    records: list[CashbackRecordPublic]
