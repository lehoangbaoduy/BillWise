from datetime import date as date_type
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class OcrStatus(StrEnum):
    SUCCESS = "success"
    LOW_CONFIDENCE = "low_confidence"


class ReceiptExtractionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    amount: Decimal
    suggested_category: str
    suggested_subcategory: str | None = None
    confidence: float = Field(ge=0, le=1)


class ReceiptExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ocr_status: OcrStatus
    merchant: str | None = None
    date: date_type | None = None
    total: Decimal | None = None
    tax: Decimal | None = None
    items: list[ReceiptExtractionItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StatementExtractionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    amount: Decimal


class StatementExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ocr_status: OcrStatus
    statement_balance: Decimal | None = None
    statement_date: date_type | None = None
    due_date: date_type | None = None
    minimum_payment: Decimal | None = None
    items: list[StatementExtractionItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
