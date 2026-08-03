import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint

from app.models._common import required_timestamp_field


class AcknowledgedNotification(SQLModel, table=True):
    __tablename__ = "acknowledged_notifications"
    __table_args__ = (UniqueConstraint("user_id", "notification_key", name="uq_acknowledged_notification_user_key"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    notification_key: str = Field(max_length=200, index=True)
    acknowledged_at: datetime = required_timestamp_field(default_now=True)
