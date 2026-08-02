import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_insight import AIInsightType


class AIInsightPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    insight_type: AIInsightType
    message: str = Field(max_length=1000)
    supporting_data: dict
    is_dismissed: bool
    generated_at: datetime


class AIInsightUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_dismissed: bool
