import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, SQLModel

from app.models._common import required_timestamp_field


class AuditLog(SQLModel, table=True):
    """PRD §22.3/§23.17 persisted audit trail. user_id is nullable — a failed
    login with an unrecognized email has no known user to attribute it to,
    but the attempt itself is still worth recording."""

    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_user_id_created_at", "user_id", "created_at"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", nullable=True, index=True)
    action: str = Field(nullable=False, index=True)
    entity_type: str | None = Field(default=None, nullable=True)
    entity_id: str | None = Field(default=None, nullable=True)
    audit_metadata: dict = Field(sa_column=Column("metadata", JSON, nullable=False))
    ip_address: str | None = Field(default=None, nullable=True)
    user_agent: str | None = Field(default=None, nullable=True)
    created_at: datetime = required_timestamp_field(default_now=True)
