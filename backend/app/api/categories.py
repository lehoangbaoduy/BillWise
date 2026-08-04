import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user, household_owner_id, require_owner_or_co_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.category import Category
from app.models.user import User, UserRole
from app.schemas.category import (
    CategoryCreate,
    CategoryPublic,
    CategorySharingUpdate,
    CategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["categories"])


async def _get_owned_or_404(session: AsyncSession, owner_id: uuid.UUID, category_id: uuid.UUID) -> Category:
    category = await session.get(Category, category_id)
    if category is None or category.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryPublic])
async def list_categories(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> list[Category]:
    if user.role == UserRole.PARTNER:
        statement = select(Category).where(
            Category.user_id == user.invited_by_user_id,
            Category.is_shared == True,  # noqa: E712
            Category.is_active == True,  # noqa: E712
        )
    else:
        statement = select(Category).where(
            Category.user_id == user.id, Category.is_active == True  # noqa: E712
        )
    return (await session.exec(statement)).all()


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Category:
    category = Category(user_id=household_owner_id(user), is_default=False, **body.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryPublic)
async def update_category(
    category_id: uuid.UUID,
    body: CategoryUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Category:
    category = await _get_owned_or_404(session, household_owner_id(user), category_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    category.updated_at = utcnow()
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_category(
    category_id: uuid.UUID,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    category = await _get_owned_or_404(session, household_owner_id(user), category_id)
    category.is_active = False
    category.updated_at = utcnow()
    session.add(category)
    await session.commit()


@router.patch("/{category_id}/sharing", response_model=CategoryPublic)
async def update_category_sharing(
    request: Request,
    category_id: uuid.UUID,
    body: CategorySharingUpdate,
    user: User = Depends(require_owner_or_co_owner),
    session: AsyncSession = Depends(get_session),
) -> Category:
    category = await _get_owned_or_404(session, household_owner_id(user), category_id)
    category.is_shared = body.is_shared
    category.updated_at = utcnow()
    session.add(category)
    await session.commit()
    await session.refresh(category)
    await log_audit_event(
        session, "category.sharing_changed", user_id=user.id, entity_type="category", entity_id=category.id,
        metadata={"is_shared": body.is_shared}, request=request,
    )
    return category
