import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserRole


async def household_member_ids(session: AsyncSession, owner_id: uuid.UUID) -> set[uuid.UUID]:
    """The owner plus their active partners -- the pool of people a
    transaction cost-split (PRD v2 §7.5) can be shared with, since split
    recipients are scoped to "owner/partner(s), not arbitrary external
    users" per §3's non-goals."""
    partners = (
        await session.exec(
            select(User.id).where(
                User.invited_by_user_id == owner_id, User.role == UserRole.PARTNER, User.is_active == True  # noqa: E712
            )
        )
    ).all()
    return {owner_id, *partners}
