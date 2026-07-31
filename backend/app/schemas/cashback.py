import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cashback import CashbackRecordStatus


class CashbackRuleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_method_id: uuid.UUID
    category_id: uuid.UUID | None = None
    cashback_rate: Decimal = Field(ge=0, le=100)
    start_date: date_type
    end_date: date_type | None = None
    notes: str | None = None


class CashbackRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: uuid.UUID | None = None
    cashback_rate: Decimal | None = Field(default=None, ge=0, le=100)
    start_date: date_type | None = None
    end_date: date_type | None = None
    notes: str | None = None


class CashbackRulePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_method_id: uuid.UUID
    category_id: uuid.UUID | None
    cashback_rate: Decimal
    start_date: date_type
    end_date: date_type | None
    notes: str | None


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
