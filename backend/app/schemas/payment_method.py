import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment_method import PaymentMethodType


class PaymentMethodCreate(BaseModel):
    # extra="forbid" is the actual enforcement of PRD §11.1's forbidden-fields list
    # (full card number, CVV, PIN, routing/account number, banking credentials, ...):
    # since none of those are declared fields below, sending them is a 422, not a
    # silently-dropped no-op.
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    type: PaymentMethodType
    issuer: str | None = Field(default=None, max_length=100)
    last_four_optional: str | None = Field(default=None, max_length=4, min_length=4)
    due_day_optional: int | None = Field(default=None, ge=1, le=31)
    statement_day_optional: int | None = Field(default=None, ge=1, le=31)
    default_cashback_rate: Decimal | None = Field(default=None, ge=0, le=100)
    current_balance: Decimal | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_shared: bool = False


class PaymentMethodUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    issuer: str | None = Field(default=None, max_length=100)
    last_four_optional: str | None = Field(default=None, max_length=4, min_length=4)
    due_day_optional: int | None = Field(default=None, ge=1, le=31)
    statement_day_optional: int | None = Field(default=None, ge=1, le=31)
    default_cashback_rate: Decimal | None = Field(default=None, ge=0, le=100)
    current_balance: Decimal | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class PaymentMethodSharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class PaymentMethodPublic(BaseModel):
    id: uuid.UUID
    name: str
    type: PaymentMethodType
    issuer: str | None
    last_four_optional: str | None
    due_day_optional: int | None
    statement_day_optional: int | None
    default_cashback_rate: Decimal | None
    current_balance: Decimal | None
    color: str | None
    is_shared: bool
    is_active: bool
