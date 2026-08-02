import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.models._common import enum_field, required_timestamp_field


class AIInsightType(StrEnum):
    CATEGORY_SPENDING_CHANGE = "category_spending_change"
    OVER_BUDGET_ALERT = "over_budget_alert"
    MULTI_MONTH_TREND = "multi_month_trend"
    TOP_CASHBACK_CARD = "top_cashback_card"
    RECURRING_BILL_SHARE = "recurring_bill_share"
    CASH_FLOW_CHANGE = "cash_flow_change"
    GOAL_PROGRESS = "goal_progress"


class AIInsight(SQLModel, table=True):
    __tablename__ = "ai_insights"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    insight_type: AIInsightType = enum_field(AIInsightType)
    message: str
    supporting_data: dict = Field(sa_column=Column(JSON, nullable=False))
    is_dismissed: bool = False
    generated_at: datetime = required_timestamp_field(default_now=True)
    created_at: datetime = required_timestamp_field(default_now=True)
