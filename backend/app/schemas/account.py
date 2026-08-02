from pydantic import BaseModel, EmailStr, Field, field_validator


def _normalize_email(value: str) -> str:
    return value.strip().lower()


class AccountDeletionRequestRequest(BaseModel):
    password: str = Field(max_length=128)


class AccountDeletionConfirmRequest(BaseModel):
    token: str
    confirmation_email: EmailStr

    _normalize_email = field_validator("confirmation_email")(_normalize_email)
