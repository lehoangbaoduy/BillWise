import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from app.models._common import required_timestamp_field


class SavingsGoal(SQLModel, table=True):
    __tablename__ = "savings_goals"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str
    target_amount: Decimal
    target_date: date_type | None = None
    icon: str | None = None
    color: str | None = None
    is_shared: bool = False
    is_active: bool = True
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
