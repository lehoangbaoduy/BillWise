import uuid
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.net_worth import NetWorthAccountType


class NetWorthAccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    type: NetWorthAccountType


class NetWorthAccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    type: NetWorthAccountType | None = None


class NetWorthAccountPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: NetWorthAccountType
    is_active: bool


class NetWorthBalanceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: uuid.UUID
    balance: Decimal


class NetWorthSnapshotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_date: date_type
    notes: str | None = Field(default=None, max_length=1000)
    balances: list[NetWorthBalanceInput] = Field(min_length=1)


class NetWorthBalancePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: uuid.UUID
    account_name: str
    account_type: NetWorthAccountType
    balance: Decimal


class NetWorthSnapshotPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    snapshot_date: date_type
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    notes: str | None
    balances: list[NetWorthBalancePublic]


class NetWorthDashboard(BaseModel):
    current_net_worth: Decimal | None
    total_assets: Decimal | None
    total_liabilities: Decimal | None
    change_vs_previous: Decimal | None
    breakdown: list[NetWorthBalancePublic]
    history: list[NetWorthSnapshotPublic]
