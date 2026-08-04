import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel

from app.models._common import required_timestamp_field


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    # created_by_user_id is part of the key so an owner and a co-owner can each
    # keep their own private budget target for the same category/month -- see
    # created_by_user_id's docstring below for why user_id alone can't scope this.
    # A plain multi-column UniqueConstraint won't do here: created_by_user_id is
    # NULL for the owner, and standard SQL treats every NULL as distinct from
    # every other NULL, so two owner-created rows for the same category/month
    # wouldn't collide. COALESCE-ing NULL to user_id (the owner's own id) in an
    # expression index closes that gap.
    __table_args__ = (
        Index(
            "uq_budget_category_period",
            "user_id", "category_id", "month", "year",
            text("COALESCE(created_by_user_id, user_id)"),
            unique=True,
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    # user_id is always the household owner's id (see app.api.deps.household_owner_id).
    # created_by_user_id separately records which household member actually set this
    # budget target -- null when the owner set it, set to the acting user's id when a
    # co-owner did. A shared category can still carry two independent private budget
    # targets (one per household member), which user_id alone can't distinguish.
    created_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    category_id: uuid.UUID = Field(foreign_key="categories.id", nullable=False)
    month: int
    year: int
    budget_amount: Decimal
    is_shared: bool = False
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
