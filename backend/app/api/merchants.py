import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import (
    get_current_user,
    household_owner_id,
    require_can_add_transactions,
    require_owner_or_co_owner,
)
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.merchant import Merchant
from app.models.user import User, UserRole
from app.schemas.merchant import MerchantCreate, MerchantPublic, MerchantSharingUpdate, MerchantUpdate

router = APIRouter(prefix="/merchants", tags=["merchants"])


async def _get_owned_or_404(session: AsyncSession, owner_id: uuid.UUID, merchant_id: uuid.UUID) -> Merchant:
    merchant = await session.get(Merchant, merchant_id)
    if merchant is None or merchant.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")
    return merchant


@router.get("", response_model=list[MerchantPublic])
async def list_merchants(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> list[Merchant]:
    if user.role == UserRole.PARTNER:
        statement = select(Merchant).where(
            Merchant.user_id == user.invited_by_user_id,
            Merchant.is_shared == True,  # noqa: E712
            Merchant.is_active == True,  # noqa: E712
        )
    else:
        statement = select(Merchant).where(Merchant.user_id == user.id, Merchant.is_active == True)  # noqa: E712
    statement = statement.order_by(Merchant.name)
    return (await session.exec(statement)).all()


@router.post("", response_model=MerchantPublic, status_code=status.HTTP_201_CREATED)
async def create_merchant(
    body: MerchantCreate,
    user: User = Depends(require_can_add_transactions),
    session: AsyncSession = Depends(get_session),
) -> Merchant:
    """Idempotent get-or-create by case-insensitive name -- shared by the
    dedicated Merchant tab's create form and the inline "Add '<query>'" quick
    add in the transaction/cashback-rule merchant picker (MerchantInput.js),
    so a permitted partner can introduce a brand new merchant while entering
    their own transaction without needing owner-or-co-owner management
    access. Re-submitting an existing name returns that row untouched rather
    than erroring or overwriting its already-filled-in type/city/state."""
    owner_id = household_owner_id(user)
    normalized_name = body.name.strip()
    existing = (
        await session.exec(
            select(Merchant).where(
                Merchant.user_id == owner_id,
                Merchant.is_active == True,  # noqa: E712
                func.lower(Merchant.name) == normalized_name.lower(),
            )
        )
    ).first()
    if existing is not None:
        return existing

    merchant = Merchant(
        user_id=owner_id,
        name=normalized_name,
        type=body.type,
        city=body.city,
        state=body.state,
        notes=body.notes,
    )
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant


@router.patch("/{merchant_id}", response_model=MerchantPublic)
async def update_merchant(
    merchant_id: uuid.UUID,
    body: MerchantUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Merchant:
    merchant = await _get_owned_or_404(session, household_owner_id(user), merchant_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(merchant, field, value)
    merchant.updated_at = utcnow()
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant


@router.patch("/{merchant_id}/sharing", response_model=MerchantPublic)
async def update_merchant_sharing(
    request: Request,
    merchant_id: uuid.UUID,
    body: MerchantSharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Merchant:
    merchant = await _get_owned_or_404(session, household_owner_id(user), merchant_id)
    merchant.is_shared = body.is_shared
    merchant.updated_at = utcnow()
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    await log_audit_event(
        session, "merchant.sharing_changed", user_id=user.id, entity_type="merchant", entity_id=merchant.id,
        metadata={"is_shared": body.is_shared}, request=request,
    )
    return merchant


@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_merchant(
    merchant_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    merchant = await _get_owned_or_404(session, household_owner_id(user), merchant_id)
    merchant.is_active = False
    merchant.updated_at = utcnow()
    session.add(merchant)
    await session.commit()
