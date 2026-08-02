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
    # PRD §22.6: set at delete-confirm time (immediate soft-delete), read by the
    # hard-delete purge job once this timestamp has passed. Never set for partners
    # — only an owner's own account deletion schedules a hard-delete; a partner
    # being deactivated (household removal or riding along with the owner's
    # deletion) never gets its own hard_delete_at, since partner rows are never
    # hard-deleted, only deactivated.
    hard_delete_at: datetime | None = optional_timestamp_field()


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


class AccountDeletionToken(SQLModel, table=True):
    __tablename__ = "account_deletion_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    token_hash: str = Field(unique=True, nullable=False)
    expires_at: datetime = required_timestamp_field()
    used_at: datetime | None = optional_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)
