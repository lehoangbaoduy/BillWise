from pydantic import BaseModel, EmailStr, field_validator


def _normalize_email(value: str) -> str:
    return value.strip().lower()


class AccountDeletionRequestRequest(BaseModel):
    password: str


class AccountDeletionConfirmRequest(BaseModel):
    token: str
    confirmation_email: EmailStr

    _normalize_email = field_validator("confirmation_email")(_normalize_email)
