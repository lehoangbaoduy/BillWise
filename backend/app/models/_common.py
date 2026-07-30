from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def enum_field(enum_cls: type[Enum], *, nullable: bool = False) -> Field:
    """Native Postgres enum storing each member's .value (BIW-DATA-001's lowercase
    check-constraint values, e.g. 'owner'/'partner') rather than SQLAlchemy's default
    of the Python member .name (e.g. 'OWNER')."""
    column = Column(
        SAEnum(enum_cls, name=enum_cls.__name__.lower(), values_callable=lambda members: [m.value for m in members]),
        nullable=nullable,
    )
    return Field(sa_column=column)


def required_timestamp_field(*, default_now: bool = False) -> Field:
    """timestamptz column (BIW-DATA-001) that defaults to now() when created."""
    return Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=utcnow if default_now else None))


def optional_timestamp_field() -> Field:
    """Nullable timestamptz column (BIW-DATA-001)."""
    return Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
