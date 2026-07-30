import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    target_amount: Decimal = Field(ge=0)
    target_date: date_type | None = None
    icon: str | None = None
    color: str | None = None
    is_shared: bool = False


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    target_amount: Decimal | None = Field(default=None, ge=0)
    target_date: date_type | None = None
    icon: str | None = None
    color: str | None = None


class GoalSharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class AddFundsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0)
    payment_method_id: uuid.UUID
    category_id: uuid.UUID
    date: date_type
    merchant: str = Field(default="Goal contribution", min_length=1, max_length=200)
    notes: str | None = None


class GoalPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date_type | None
    icon: str | None
    color: str | None
    is_shared: bool
    is_active: bool


class GoalContributionPublic(BaseModel):
    id: uuid.UUID
    date: date_type
    merchant: str
    total_amount: Decimal
    transaction_type: TransactionType


class GoalDetail(GoalPublic):
    contributing_transactions: list[GoalContributionPublic]
