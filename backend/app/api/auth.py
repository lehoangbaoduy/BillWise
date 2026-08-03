from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.audit import log_audit_event
from app.core.config import settings
from app.core.db import get_session
from app.core.email import send_password_reset_email, send_verification_email
from app.core.rate_limit import limiter
from app.core.security import (
    create_session_token,
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models._common import utcnow
from app.models.user import EmailVerificationToken, PasswordResetToken, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequestRequest,
    RegisterRequest,
    UserPublic,
    VerifyEmailRequest,
)
from app.seed.default_categories import seed_default_categories

router = APIRouter(prefix="/auth", tags=["auth"])


def to_user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        role=user.role,
        display_name=user.display_name,
        email_verified=user.email_verified_at is not None,
    )


def _set_session_cookie(response: Response, user: User) -> None:
    token = create_session_token(user.id, user.role)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(request: Request, body: RegisterRequest, session: AsyncSession = Depends(get_session)) -> UserPublic:
    if body.invite_token is not None:
        # Partner acceptance is its own endpoint (PRD §25.13: POST
        # /household/accept-invite, app/api/household.py) rather than a branch of
        # this one — a partner isn't an owner-with-categories-seeded, and PRD's own
        # endpoint list names a distinct path. Reject explicitly rather than
        # silently ignoring the field if a client still sends it here.
        raise HTTPException(status_code=400, detail="Use POST /household/accept-invite to accept a partner invite")

    existing = (await session.exec(select(User).where(User.email == body.email))).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
        role=UserRole.OWNER,
    )
    session.add(user)
    await session.flush()

    await seed_default_categories(session, user.id)

    token = generate_token()
    session.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + timedelta(hours=settings.email_verification_token_expire_hours),
        )
    )
    try:
        await session.commit()
    except IntegrityError:
        # The existence pre-check above is a fast path, not the source of truth —
        # it can't close the race between two concurrent registrations for the same
        # email (both pass the check before either commits). The unique constraint
        # on users.email is what actually prevents the duplicate; this just turns
        # that into a clean 409 instead of an unhandled 500.
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    await session.refresh(user)

    verify_url = f"{settings.frontend_base_url}/verify-email?token={token}"
    send_verification_email(user.email, verify_url)

    await log_audit_event(
        session, "user.registered", user_id=user.id, entity_type="user", entity_id=user.id,
        metadata={"email": user.email}, request=request,
    )
    return to_user_public(user)


@router.post("/verify-email")
async def verify_email(request: Request, body: VerifyEmailRequest, session: AsyncSession = Depends(get_session)) -> dict:
    token_hash = hash_token(body.token)
    record = (
        await session.exec(select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash))
    ).first()

    now = utcnow()
    if record is None or record.used_at is not None or record.expires_at < now:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = await session.get(User, record.user_id)
    user.email_verified_at = now
    user.updated_at = now
    record.used_at = now
    session.add(user)
    session.add(record)
    await session.commit()

    await log_audit_event(session, "user.email_verified", user_id=user.id, entity_type="user", entity_id=user.id, request=request)
    return {"verified": True}


@router.post("/login", response_model=UserPublic)
@limiter.limit(settings.login_rate_limit_window)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> UserPublic:
    user = (await session.exec(select(User).where(User.email == body.email))).first()
    if user is None or not verify_password(body.password, user.password_hash):
        await log_audit_event(
            session, "user.login_failed", user_id=user.id if user else None,
            metadata={"email": body.email}, request=request,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if user.email_verified_at is None:
        await log_audit_event(
            session, "user.login_failed", user_id=user.id,
            metadata={"reason": "email_not_verified"}, request=request,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    if not user.is_active:
        await log_audit_event(
            session, "user.login_failed", user_id=user.id, metadata={"reason": "inactive"}, request=request,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user.last_login_at = utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    _set_session_cookie(response, user)
    await log_audit_event(session, "user.login_succeeded", user_id=user.id, entity_type="user", entity_id=user.id, request=request)
    return to_user_public(user)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    response.delete_cookie(
        key=settings.cookie_name,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    await log_audit_event(
        session, "user.logout", user_id=current_user.id, entity_type="user", entity_id=current_user.id, request=request,
    )
    return {"ok": True}


@router.get("/me", response_model=UserPublic)
async def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return to_user_public(current_user)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.password_reset_rate_limit_window)
async def request_password_reset(
    request: Request,
    body: PasswordResetRequestRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    user = (await session.exec(select(User).where(User.email == body.email))).first()
    if user is not None:
        token = generate_token()
        session.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=utcnow() + timedelta(minutes=settings.password_reset_token_expire_minutes),
            )
        )
        await session.commit()
        reset_url = f"{settings.frontend_base_url}/reset-password?token={token}"
        send_password_reset_email(user.email, reset_url)
        await log_audit_event(
            session, "user.password_reset_requested", user_id=user.id,
            entity_type="user", entity_id=user.id, request=request,
        )

    # Always 202, whether or not the email exists — avoids account enumeration.
    return {"accepted": True}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: Request, body: PasswordResetConfirmRequest, session: AsyncSession = Depends(get_session)
) -> dict:
    token_hash = hash_token(body.token)
    record = (
        await session.exec(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))
    ).first()

    now = utcnow()
    if record is None or record.used_at is not None or record.expires_at < now:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = await session.get(User, record.user_id)
    user.password_hash = hash_password(body.new_password)
    user.updated_at = now
    record.used_at = now
    session.add(user)
    session.add(record)
    await session.commit()

    await log_audit_event(
        session, "user.password_reset_completed", user_id=user.id, entity_type="user", entity_id=user.id, request=request,
    )
    return {"ok": True}
