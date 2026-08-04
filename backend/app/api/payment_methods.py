import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import household_owner_id, require_owner_or_co_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.payment_method import PaymentMethod
from app.models.user import User
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodPublic,
    PaymentMethodSharingUpdate,
    PaymentMethodUpdate,
)
from app.services.item_visibility import user_can_access_item, visibility_condition

router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])


async def _get_owned_or_404(session: AsyncSession, user: User, payment_method_id: uuid.UUID) -> PaymentMethod:
    payment_method = await session.get(PaymentMethod, payment_method_id)
    owner_id = household_owner_id(user)
    if (
        payment_method is None
        or payment_method.user_id != owner_id
        or not user_can_access_item(payment_method.is_shared, payment_method.created_by_user_id, owner_id, user)
    ):
        # A private wallet belonging to someone else must 404, not 403 -- 403 would
        # confirm it exists, which is exactly the leak "completely invisible" rules out.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
    return payment_method


@router.get("", response_model=list[PaymentMethodPublic])
async def list_payment_methods(
    user: User = Depends(require_owner_or_co_owner), session: AsyncSession = Depends(get_session)
) -> list[PaymentMethod]:
    owner_id = household_owner_id(user)
    statement = select(PaymentMethod).where(
        PaymentMethod.user_id == owner_id,
        PaymentMethod.is_active == True,  # noqa: E712
        visibility_condition(PaymentMethod, owner_id, user),
    )
    return (await session.exec(statement)).all()


@router.post("", response_model=PaymentMethodPublic, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    request: Request,
    body: PaymentMethodCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> PaymentMethod:
    owner_id = household_owner_id(user)
    payment_method = PaymentMethod(
        user_id=owner_id,
        created_by_user_id=user.id if user.id != owner_id else None,
        **body.model_dump(),
    )
    session.add(payment_method)
    await session.commit()
    await session.refresh(payment_method)
    await log_audit_event(
        session, "payment_method.created", user_id=user.id, entity_type="payment_method", entity_id=payment_method.id,
        metadata={"name": payment_method.name}, request=request,
    )
    return payment_method


@router.get("/{payment_method_id}", response_model=PaymentMethodPublic)
async def get_payment_method(
    payment_method_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> PaymentMethod:
    return await _get_owned_or_404(session, user, payment_method_id)


@router.patch("/{payment_method_id}", response_model=PaymentMethodPublic)
async def update_payment_method(
    request: Request,
    payment_method_id: uuid.UUID,
    body: PaymentMethodUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> PaymentMethod:
    payment_method = await _get_owned_or_404(session, user, payment_method_id)
    updated_fields = body.model_dump(exclude_unset=True)
    for field, value in updated_fields.items():
        setattr(payment_method, field, value)
    payment_method.updated_at = utcnow()
    session.add(payment_method)
    await session.commit()
    await session.refresh(payment_method)
    await log_audit_event(
        session, "payment_method.updated", user_id=user.id, entity_type="payment_method", entity_id=payment_method.id,
        metadata={"fields": list(updated_fields.keys())}, request=request,
    )
    return payment_method


@router.patch("/{payment_method_id}/sharing", response_model=PaymentMethodPublic)
async def update_payment_method_sharing(
    request: Request,
    payment_method_id: uuid.UUID,
    body: PaymentMethodSharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> PaymentMethod:
    payment_method = await _get_owned_or_404(session, user, payment_method_id)
    payment_method.is_shared = body.is_shared
    payment_method.updated_at = utcnow()
    session.add(payment_method)
    await session.commit()
    await session.refresh(payment_method)
    await log_audit_event(
        session, "payment_method.updated", user_id=user.id, entity_type="payment_method", entity_id=payment_method.id,
        metadata={"fields": ["is_shared"], "is_shared": body.is_shared}, request=request,
    )
    return payment_method


@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_payment_method(
    request: Request,
    payment_method_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    payment_method = await _get_owned_or_404(session, user, payment_method_id)
    payment_method.is_active = False
    payment_method.updated_at = utcnow()
    session.add(payment_method)
    await session.commit()
    await log_audit_event(
        session, "payment_method.deactivated", user_id=user.id, entity_type="payment_method",
        entity_id=payment_method_id, request=request,
    )
