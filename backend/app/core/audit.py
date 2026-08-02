"""Structured + persisted audit logging (PRD §22.3/§23.17).

Every call both emits a structured log line (parseable by any log
aggregator, kept from the original M1-era implementation) and persists a
row to the audit_logs table via GET /audit-logs. Called strictly after the
caller's own primary commit at every call site, so this commits its own row
independently rather than trying to share the caller's transaction.
"""

import logging
import uuid

from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit_log import AuditLog

audit_logger = logging.getLogger("billwise.audit")


async def log_audit_event(
    session: AsyncSession,
    action: str,
    *,
    user_id: uuid.UUID | str | None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | str | None = None,
    metadata: dict | None = None,
    request: Request | None = None,
) -> None:
    audit_logger.info("action=%s user_id=%s metadata=%s", action, user_id, metadata or {})
    session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            audit_metadata=metadata or {},
            ip_address=request.client.host if request is not None and request.client else None,
            user_agent=request.headers.get("user-agent") if request is not None else None,
        )
    )
    await session.commit()
