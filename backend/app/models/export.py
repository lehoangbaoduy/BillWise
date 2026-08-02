import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import LargeBinary
from sqlmodel import Column, Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class ExportType(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class ExportToken(SQLModel, table=True):
    """A generated export file plus the opaque, short-lived download token that
    guards it (PRD §20.4). Mirrors the established EmailVerificationToken /
    PasswordResetToken / PartnerInviteToken shape. The file content is stored
    inline (bytea) rather than in a blob store — this app has no S3/object
    storage integration to build on, and export files are small enough at this
    app's scale for Postgres to hold directly."""

    __tablename__ = "export_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    export_type: ExportType = enum_field(ExportType)
    filename: str
    content_type: str
    content: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    token_hash: str = Field(unique=True, nullable=False)
    expires_at: datetime = required_timestamp_field()
    created_at: datetime = required_timestamp_field(default_now=True)
