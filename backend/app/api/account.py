from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.config import settings
from app.core.db import get_session
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.account import AccountDeletionConfirmRequest, AccountDeletionRequestRequest
from app.services.account_deletion_service import (
    cancel_account_deletion,
    confirm_account_deletion,
    request_account_deletion,
)

router = APIRouter(prefix="/account", tags=["account"])


@router.post("/delete-request", status_code=202)
@limiter.limit(settings.account_deletion_rate_limit_window)
async def delete_request(
    request: Request,
    body: AccountDeletionRequestRequest,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> dict:
    await request_account_deletion(session, user, body.password, request)
    return {"requested": True}


@router.post("/delete-confirm")
async def delete_confirm(
    request: Request,
    body: AccountDeletionConfirmRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """No auth dependency — token-based, mirrors /auth/password-reset/confirm.
    Must keep working even after the session this action revokes."""
    await confirm_account_deletion(session, body.token, body.confirmation_email, request)
    return {"deleted": True}


@router.post("/delete-cancel")
async def delete_cancel(
    request: Request,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> dict:
    await cancel_account_deletion(session, user, request)
    return {"cancelled": True}
