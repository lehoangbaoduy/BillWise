import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _require_letter_and_digit(value: str) -> str:
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one digit")
    return value


class InvitePartnerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    can_add_transactions: bool = False

    _normalize_email = field_validator("email")(_normalize_email)


class AcceptInviteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)

    _validate_password = field_validator("password")(_require_letter_and_digit)


class UpdatePartnerPermissionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    can_add_transactions: bool


class PartnerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str
    can_add_transactions: bool
    is_active: bool
    joined_at: datetime


class PendingInvitePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    can_add_transactions: bool
    expires_at: datetime


class HouseholdSummary(BaseModel):
    partners: list[PartnerPublic]
    pending_invites: list[PendingInvitePublic]
