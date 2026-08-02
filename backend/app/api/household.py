import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.auth import to_user_public
from app.api.deps import require_owner
from app.core.audit import log_audit_event
from app.core.config import settings
from app.core.db import get_session
from app.core.email import send_partner_invite_email
from app.core.security import generate_token, hash_password, hash_token
from app.models._common import utcnow
from app.models.partner_permission import PartnerInviteToken, PartnerPermission
from app.models.user import User, UserRole
from app.schemas.auth import UserPublic
from app.schemas.household import (
    AcceptInviteRequest,
    HouseholdSummary,
    InvitePartnerRequest,
    PartnerPublic,
    PendingInvitePublic,
    UpdatePartnerPermissionsRequest,
)

router = APIRouter(tags=["household"])


def _is_pending(invite: PartnerInviteToken, now) -> bool:
    return invite.accepted_at is None and invite.revoked_at is None and invite.expires_at > now


@router.get("/household", response_model=HouseholdSummary)
async def get_household(
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> HouseholdSummary:
    """Not in PRD §25.13's literal endpoint list, but §24.13's screen requires
    showing the current partner list and pending invite status, and there's no
    other way to populate that screen — same gap-fill pattern as every other
    resource's missing GET list route this milestone."""
    partners = (
        await session.exec(select(User).where(User.invited_by_user_id == user.id, User.role == UserRole.PARTNER))
    ).all()
    partner_ids = [partner.id for partner in partners]
    permissions_by_partner: dict[uuid.UUID, PartnerPermission] = {}
    if partner_ids:
        rows = (
            await session.exec(select(PartnerPermission).where(PartnerPermission.partner_user_id.in_(partner_ids)))  # type: ignore[union-attr]
        ).all()
        permissions_by_partner = {row.partner_user_id: row for row in rows}

    partner_public = [
        PartnerPublic(
            id=partner.id,
            email=partner.email,
            display_name=partner.display_name,
            can_add_transactions=permissions_by_partner[partner.id].can_add_transactions
            if partner.id in permissions_by_partner
            else False,
            is_active=partner.is_active,
            joined_at=partner.created_at,
        )
        for partner in partners
    ]

    now = utcnow()
    invites = (
        await session.exec(select(PartnerInviteToken).where(PartnerInviteToken.invited_by_user_id == user.id))
    ).all()
    pending = [invite for invite in invites if _is_pending(invite, now)]

    return HouseholdSummary(partners=partner_public, pending_invites=[PendingInvitePublic.model_validate(i) for i in pending])


@router.post("/household/invite-partner", response_model=PendingInvitePublic, status_code=status.HTTP_201_CREATED)
async def invite_partner(
    body: InvitePartnerRequest,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> PartnerInviteToken:
    # Deliberately no existing_user check here (unlike accept_invite's, which is
    # safe because only the token holder sees it): an owner-visible 409 would let
    # any owner enumerate whether an arbitrary email has a BillWise account,
    # exactly what password-reset/request's always-202 response avoids. The invite
    # is created and "sent" the same way regardless; accept_invite's own check
    # backstops against actually creating a duplicate account.
    now = utcnow()
    existing_invites = (
        await session.exec(
            select(PartnerInviteToken).where(
                PartnerInviteToken.email == body.email, PartnerInviteToken.invited_by_user_id == user.id
            )
        )
    ).all()
    if any(_is_pending(invite, now) for invite in existing_invites):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An invite is already pending for this email")

    token = generate_token()
    invite = PartnerInviteToken(
        invited_by_user_id=user.id,
        email=body.email,
        can_add_transactions=body.can_add_transactions,
        token_hash=hash_token(token),
        expires_at=now + timedelta(hours=settings.partner_invite_token_expire_hours),
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)

    accept_url = f"{settings.frontend_base_url}/accept-invite?token={token}"
    send_partner_invite_email(body.email, accept_url)

    log_audit_event("partner.invited", user_id=user.id, metadata={"email": body.email})
    return invite


@router.post("/household/accept-invite", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def accept_invite(body: AcceptInviteRequest, session: AsyncSession = Depends(get_session)) -> UserPublic:
    token_hash = hash_token(body.token)
    invite = (await session.exec(select(PartnerInviteToken).where(PartnerInviteToken.token_hash == token_hash))).first()

    now = utcnow()
    if invite is None or not _is_pending(invite, now):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired invite")

    existing_user = (await session.exec(select(User).where(User.email == invite.email))).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    partner = User(
        email=invite.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        role=UserRole.PARTNER,
        invited_by_user_id=invite.invited_by_user_id,
        # Accepting a link only the invited address received is itself proof of
        # ownership — no separate verification email needed, unlike self-registration.
        email_verified_at=now,
    )
    session.add(partner)
    await session.flush()

    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=invite.can_add_transactions))
    invite.accepted_at = now
    session.add(invite)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from None
    await session.refresh(partner)

    log_audit_event("partner.invite_accepted", user_id=partner.id, metadata={"invited_by": str(invite.invited_by_user_id)})
    return to_user_public(partner)


@router.delete("/household/partner/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_partner(
    partner_id: uuid.UUID,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Handles both an already-accepted partner (deactivates the user — their
    next request 401s immediately via get_current_user's is_active check, which
    is this app's session model, so no separate session-invalidation step is
    needed) and a still-pending invite (revokes the token). PRD §25.13 lists one
    DELETE route for "partner", and §24.13's screen needs to cancel either kind
    from the same list, so this endpoint accepts either id type."""
    partner = await session.get(User, partner_id)
    if partner is not None and partner.invited_by_user_id == user.id and partner.role == UserRole.PARTNER:
        partner.is_active = False
        session.add(partner)
        await session.commit()
        log_audit_event("partner.revoked", user_id=user.id, metadata={"partner_id": str(partner_id)})
        return

    invite = await session.get(PartnerInviteToken, partner_id)
    now = utcnow()
    if invite is not None and invite.invited_by_user_id == user.id and _is_pending(invite, now):
        invite.revoked_at = now
        session.add(invite)
        await session.commit()
        log_audit_event("partner.invite_revoked", user_id=user.id, metadata={"invite_id": str(partner_id)})
        return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner or invite not found")


@router.patch("/household/partner/{partner_id}/permissions", response_model=PartnerPublic)
async def update_partner_permissions(
    partner_id: uuid.UUID,
    body: UpdatePartnerPermissionsRequest,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> PartnerPublic:
    partner = await session.get(User, partner_id)
    if partner is None or partner.invited_by_user_id != user.id or partner.role != UserRole.PARTNER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")

    permission = (
        await session.exec(select(PartnerPermission).where(PartnerPermission.partner_user_id == partner.id))
    ).first()
    if permission is None:
        permission = PartnerPermission(partner_user_id=partner.id, can_add_transactions=body.can_add_transactions)
    else:
        permission.can_add_transactions = body.can_add_transactions
        permission.updated_at = utcnow()
    session.add(permission)
    await session.commit()

    log_audit_event(
        "partner.permissions_updated",
        user_id=user.id,
        metadata={"partner_id": str(partner_id), "can_add_transactions": body.can_add_transactions},
    )
    return PartnerPublic(
        id=partner.id,
        email=partner.email,
        display_name=partner.display_name,
        can_add_transactions=permission.can_add_transactions,
        is_active=partner.is_active,
        joined_at=partner.created_at,
    )
