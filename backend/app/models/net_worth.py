import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class NetWorthAccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"


class NetWorthAccount(SQLModel, table=True):
    __tablename__ = "net_worth_accounts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str
    type: NetWorthAccountType = enum_field(NetWorthAccountType)
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class NetWorthSnapshot(SQLModel, table=True):
    __tablename__ = "net_worth_snapshots"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    snapshot_date: date_type
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    notes: str | None = None
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)


class NetWorthBalance(SQLModel, table=True):
    __tablename__ = "net_worth_balances"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    account_id: uuid.UUID = Field(foreign_key="net_worth_accounts.id", nullable=False, index=True, ondelete="CASCADE")
    snapshot_id: uuid.UUID = Field(foreign_key="net_worth_snapshots.id", nullable=False, index=True, ondelete="CASCADE")
    balance: Decimal
    created_at: datetime = required_timestamp_field(default_now=True)
