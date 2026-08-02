import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.audit import log_audit_event
from app.core.db import get_session
from app.models._common import utcnow
from app.models.ai_insight import AIInsight
from app.models.user import User
from app.schemas.ai_insight import AIInsightPublic, AIInsightUpdate
from app.services.ai_insight_service import generate_insights
from app.services.insight_aggregation import gather_insight_inputs

router = APIRouter(tags=["ai-insights"])

# PRD §19.3 requires every generation event to be audit logged, so generation is
# capped to once per day per user rather than on every dashboard load — both to
# respect that as a discrete, meaningful event and to avoid unnecessary AI-provider
# calls/cost on repeated page views.
_REGENERATION_INTERVAL = timedelta(hours=24)


async def _latest_generated_at(session: AsyncSession, user: User):
    return (await session.exec(select(func.max(AIInsight.generated_at)).where(AIInsight.user_id == user.id))).one()


async def _generate_and_persist(session: AsyncSession, user: User, request: Request | None) -> None:
    today = utcnow().date()
    aggregates = await gather_insight_inputs(session, user, today.month, today.year)
    try:
        items = await generate_insights(aggregates)
    except HTTPException:
        # AI Insights are a supplementary dashboard widget — a provider outage
        # shouldn't break the whole dashboard load. Fall through to returning
        # whatever (possibly empty) insights already exist.
        return

    generated_at = utcnow()
    for item in items:
        session.add(
            AIInsight(
                user_id=user.id,
                insight_type=item["insight_type"],
                message=item["message"],
                supporting_data=item["supporting_data"],
                generated_at=generated_at,
            )
        )
    await session.commit()
    await log_audit_event(session, "ai_insight.generated", user_id=user.id, metadata={"count": len(items)}, request=request)


@router.get("/dashboard/ai-insights", response_model=list[AIInsightPublic])
async def get_ai_insights(
    request: Request,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> list[AIInsight]:
    latest_generated_at = await _latest_generated_at(session, user)
    if latest_generated_at is None or utcnow() - latest_generated_at > _REGENERATION_INTERVAL:
        await _generate_and_persist(session, user, request)
        latest_generated_at = await _latest_generated_at(session, user)

    if latest_generated_at is None:
        return []

    statement = select(AIInsight).where(
        AIInsight.user_id == user.id,
        AIInsight.generated_at == latest_generated_at,
        AIInsight.is_dismissed == False,  # noqa: E712
    )
    return (await session.exec(statement)).all()


@router.patch("/ai-insights/{insight_id}", response_model=AIInsightPublic)
async def update_ai_insight(
    insight_id: uuid.UUID,
    body: AIInsightUpdate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> AIInsight:
    insight = await session.get(AIInsight, insight_id)
    if insight is None or insight.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")
    insight.is_dismissed = body.is_dismissed
    session.add(insight)
    await session.commit()
    await session.refresh(insight)
    return insight
