import uuid

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_session_token
from app.models.user import User, UserRole


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    session_cookie: str | None = Cookie(default=None, alias=settings.cookie_name),
) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if session_cookie is None:
        raise unauthorized

    payload = decode_session_token(session_cookie)
    if payload is None:
        raise unauthorized

    user = await session.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise unauthorized

    return user


async def require_owner(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return user
