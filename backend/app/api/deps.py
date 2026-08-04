import uuid

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_session_token
from app.models.partner_permission import PartnerPermission
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


async def require_household_member(user: User = Depends(get_current_user)) -> User:
    """Accepts either an owner or an active partner — get_current_user's
    is_active check already ensures a revoked partner never reaches here, so no
    additional role check is needed at this layer. Callers must scope their own
    queries via household_owner_id(user); this dependency only establishes that
    the caller belongs to *some* household."""
    return user


def household_owner_id(user: User) -> uuid.UUID:
    """The user id that all of a household's owned data (categories, goals,
    transactions, payment methods) is scoped under — the owner's own id for an
    owner, or the inviting owner's id for a partner.

    invited_by_user_id is nullable at the schema level (no DB constraint ties it
    to role=partner — application code, via household.accept_invite, is what
    always sets it for a partner), so a None here would be a data integrity
    violation, not a normal request path. Failing loudly avoids the alternative:
    every SQLAlchemy `== owner_id` comparison silently degrading to `IS NULL`
    and returning empty results instead of surfacing the corruption."""
    if user.role == UserRole.PARTNER:
        if user.invited_by_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Partner account missing household owner"
            )
        return user.invited_by_user_id
    return user.id


async def _partner_permission(user: User, session: AsyncSession) -> PartnerPermission | None:
    return (
        await session.exec(select(PartnerPermission).where(PartnerPermission.partner_user_id == user.id))
    ).first()


async def is_owner_or_co_owner(user: User, session: AsyncSession) -> bool:
    """Non-DI boolean counterpart to require_owner_or_co_owner, for call sites
    that need to branch behavior rather than reject the request outright --
    e.g. the Private/Shared wallet model only distinguishes owner vs co-owner
    identity; a plain (non-co-owner) partner was never able to create a
    Wallet/Budget/Goal/RecurringBill in the first place, so private-item
    checks against those entities should never apply to them."""
    if user.role == UserRole.OWNER:
        return True
    permission = await _partner_permission(user, session)
    return permission is not None and permission.is_co_owner


async def require_owner_or_co_owner(
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Gates financial-data management (budgets, goals, categories, payment
    methods, recurring bills, cashback, transactions, exports, net worth, AI
    insights, receipt scanning) to the owner or a partner explicitly promoted
    to co-owner. Deliberately narrower than require_owner's other callers:
    household administration (inviting/removing partners, the audit log,
    account deletion) stays require_owner-only, since a co-owner managing
    finances is a different privilege than a co-owner controlling who's in
    the household or seeing its security trail."""
    if user.role == UserRole.OWNER:
        return user
    permission = await _partner_permission(user, session)
    if permission is None or not permission.is_co_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or co-owner access required")
    return user


async def require_can_add_transactions(
    user: User = Depends(require_household_member),
    session: AsyncSession = Depends(get_session),
) -> User:
    """PRD §21.3: an owner invites a partner with either view-only or
    can-add-transactions permission. Owners always pass; a partner must have an
    explicit PartnerPermission row with can_add_transactions=True. A co-owner
    always passes too -- it would be incoherent for someone with full
    financial-data management access to be blocked from adding a transaction."""
    if user.role != UserRole.PARTNER:
        return user
    permission = await _partner_permission(user, session)
    if permission is None or not (permission.can_add_transactions or permission.is_co_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted to add transactions")
    return user
