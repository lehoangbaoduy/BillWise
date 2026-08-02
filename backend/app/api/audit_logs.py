from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.db import get_session
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogPublic

router = APIRouter(tags=["audit-logs"])

_DEFAULT_LIMIT = 50
_MAX_LIMIT = 200


@router.get("/audit-logs", response_model=list[AuditLogPublic])
async def list_audit_logs(
    action: str | None = None,
    entity_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[AuditLogPublic]:
    """Owner-only, whole-household visibility — includes the owner's own
    actions and every partner's, since this is an owner-facing oversight
    feature (PRD §22.3/§25.12), not a personal activity log."""
    partner_ids = (
        await session.exec(select(User.id).where(User.invited_by_user_id == user.id, User.role == UserRole.PARTNER))
    ).all()
    household_user_ids = [user.id, *partner_ids]

    conditions = [AuditLog.user_id.in_(household_user_ids)]  # type: ignore[union-attr]
    if action is not None:
        conditions.append(AuditLog.action == action)
    if entity_type is not None:
        conditions.append(AuditLog.entity_type == entity_type)
    if start_date is not None:
        conditions.append(AuditLog.created_at >= start_date)
    if end_date is not None:
        conditions.append(AuditLog.created_at <= end_date)

    statement = (
        select(AuditLog)
        .where(*conditions)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = (await session.exec(statement)).all()
    # Built explicitly rather than relying on FastAPI's attribute-based
    # response_model serialization: AuditLog's Python attribute is
    # audit_metadata (not metadata — that name is reserved by SQLAlchemy's
    # own declarative-model machinery), but the public field is the nicer
    # "metadata" per PRD §22.3's literal field name.
    return [
        AuditLogPublic(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            metadata=log.audit_metadata,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
        )
        for log in logs
    ]
