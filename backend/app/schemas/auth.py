import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _require_letter_and_digit(value: str) -> str:
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one digit")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)
    invite_token: str | None = None

    _normalize_email = field_validator("email")(_normalize_email)
    _validate_password = field_validator("password")(_require_letter_and_digit)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)

    _normalize_email = field_validator("email")(_normalize_email)


class VerifyEmailRequest(BaseModel):
    token: str


class PasswordResetRequestRequest(BaseModel):
    email: EmailStr

    _normalize_email = field_validator("email")(_normalize_email)


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    _validate_password = field_validator("new_password")(_require_letter_and_digit)


class UpdateProfileRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    _validate_password = field_validator("new_password")(_require_letter_and_digit)


class UserPublic(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    display_name: str
    email_verified: bool
    # True for an owner, or a partner explicitly promoted to co-owner -- lets
    # the frontend gate finance-management UI (e.g. the Merchants page) the
    # same way require_owner_or_co_owner gates the backend, without a partner
    # needing owner-only access to GET /household just to learn their own
    # permission level.
    can_manage_finances: bool
