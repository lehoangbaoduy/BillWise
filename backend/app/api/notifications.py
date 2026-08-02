from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_household_member
from app.core.db import get_session
from app.models.user import User
from app.schemas.notification import NotificationItem
from app.services.notification_service import list_notifications

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationItem])
async def get_notifications(
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> list[NotificationItem]:
    return await list_notifications(session, user)
