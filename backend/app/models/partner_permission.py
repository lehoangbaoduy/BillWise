import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models._common import required_timestamp_field


class PartnerPermission(SQLModel, table=True):
    __tablename__ = "partner_permissions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    partner_user_id: uuid.UUID = Field(foreign_key="users.id", unique=True, nullable=False)
    can_add_transactions: bool = False
    created_at: datetime = required_timestamp_field(default_now=True)
    updated_at: datetime = required_timestamp_field(default_now=True)
