import uuid

from pydantic import BaseModel


class NotificationItem(BaseModel):
    key: str
    type: str
    severity: str
    title: str
    message: str
    category_id: uuid.UUID | None = None
    entity_id: uuid.UUID | None = None
    is_acknowledged: bool = False


class NotificationAcknowledgeRequest(BaseModel):
    key: str
