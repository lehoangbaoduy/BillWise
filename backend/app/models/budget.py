import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel, UniqueConstraint

from app.models._common import required_timestamp_field


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_category_period"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    category_id: uuid.UUID = Field(foreign_key="categories.id", nullable=False)
    month: int
    year: int
    budget_amount: Decimal
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
