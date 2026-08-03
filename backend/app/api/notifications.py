from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_household_member
from app.core.config import settings
from app.core.db import get_session
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.notification import NotificationAcknowledgeRequest, NotificationItem
from app.services.notification_service import acknowledge_notification, list_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationItem])
@limiter.limit(settings.read_rate_limit_window)
async def get_notifications(
    request: Request,
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> list[NotificationItem]:
    return await list_notifications(session, user)


@router.post("/acknowledge", status_code=status.HTTP_204_NO_CONTENT)
async def acknowledge(
    body: NotificationAcknowledgeRequest,
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> None:
    await acknowledge_notification(session, user, body.key)
