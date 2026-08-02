import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogPublic(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    entity_type: str | None
    entity_id: str | None
    metadata: dict
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
