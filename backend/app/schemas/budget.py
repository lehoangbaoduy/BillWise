import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: uuid.UUID
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    budget_amount: Decimal = Field(ge=0)
    is_shared: bool = False


class BudgetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget_amount: Decimal = Field(ge=0)


class BudgetSharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class BudgetPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    month: int
    year: int
    budget_amount: Decimal
    is_shared: bool
    created_by_user_id: uuid.UUID | None
