import uuid
from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, optional_timestamp_field, required_timestamp_field


class UserRole(StrEnum):
    OWNER = "owner"
    PARTNER = "partner"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str
    display_name: str
    role: UserRole = enum_field(UserRole)
    invited_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    email_verified_at: datetime | None = optional_timestamp_field()
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
    last_login_at: datetime | None = optional_timestamp_field()


class EmailVerificationToken(SQLModel, table=True):
    __tablename__ = "email_verification_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    token_hash: str = Field(unique=True, nullable=False)
    expires_at: datetime = required_timestamp_field()
    used_at: datetime | None = optional_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    token_hash: str = Field(unique=True, nullable=False)
    expires_at: datetime = required_timestamp_field()
    used_at: datetime | None = optional_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)
