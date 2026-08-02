import uuid

from pydantic import BaseModel


class NotificationItem(BaseModel):
    type: str
    severity: str
    title: str
    message: str
    category_id: uuid.UUID | None = None
    entity_id: uuid.UUID | None = None
