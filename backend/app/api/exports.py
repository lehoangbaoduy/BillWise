from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.config import settings
from app.core.db import get_session
from app.core.security import generate_token, hash_token
from app.models._common import utcnow
from app.models.export import ExportToken, ExportType
from app.models.user import User
from app.schemas.export import ExportLinkPublic
from app.services.export_service import build_monthly_report_pdf, build_monthly_report_xlsx, build_transactions_csv

router = APIRouter(prefix="/exports", tags=["exports"])

_CONTENT_TYPES = {
    ExportType.CSV: "text/csv",
    ExportType.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ExportType.PDF: "application/pdf",
}


async def _issue_link(
    session: AsyncSession, user: User, export_type: ExportType, filename: str, content: bytes
) -> ExportLinkPublic:
    # No background sweep job exists in this codebase for any table, so rather
    # than introduce new scheduler infra just for this, each new export
    # opportunistically clears its own owner's past-expiry rows — bounds
    # per-user accumulation as a side effect of normal usage instead of
    # leaving expired report bytes to build up indefinitely.
    await session.exec(delete(ExportToken).where(ExportToken.user_id == user.id, ExportToken.expires_at < utcnow()))

    token = generate_token()
    expires_at = utcnow() + timedelta(minutes=settings.export_token_expire_minutes)
    session.add(
        ExportToken(
            user_id=user.id,
            export_type=export_type,
            filename=filename,
            content_type=_CONTENT_TYPES[export_type],
            content=content,
            token_hash=hash_token(token),
            expires_at=expires_at,
        )
    )
    await session.commit()
    return ExportLinkPublic(download_url=f"/exports/download/{token}", expires_at=expires_at)


@router.get("/transactions.csv", response_model=ExportLinkPublic)
async def export_transactions_csv(
    user: User = Depends(require_owner), session: AsyncSession = Depends(get_session)
) -> ExportLinkPublic:
    content = await build_transactions_csv(session, user)
    return await _issue_link(session, user, ExportType.CSV, "transactions.csv", content)


@router.get("/monthly-report.xlsx", response_model=ExportLinkPublic)
async def export_monthly_report_xlsx(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> ExportLinkPublic:
    content = await build_monthly_report_xlsx(session, user, month, year)
    return await _issue_link(session, user, ExportType.XLSX, f"billwise-report-{year}-{month:02d}.xlsx", content)


@router.get("/monthly-report.pdf", response_model=ExportLinkPublic)
async def export_monthly_report_pdf(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=2100),
    password: str | None = Query(default=None, min_length=4, max_length=128),
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> ExportLinkPublic:
    content = await build_monthly_report_pdf(session, user, month, year, password)
    return await _issue_link(session, user, ExportType.PDF, f"billwise-report-{year}-{month:02d}.pdf", content)


@router.get("/download/{token}")
async def download_export(token: str, session: AsyncSession = Depends(get_session)) -> Response:
    """Public — no session auth required. The opaque token itself is the
    credential (PRD §20.4's "short-lived signed download URL"), matching this
    app's other token-gated public endpoints (verify-email, accept-invite).
    Reusable (not single-use) until expires_at, same as a typical presigned
    URL."""
    record = (await session.exec(select(ExportToken).where(ExportToken.token_hash == hash_token(token)))).first()
    if record is None or record.expires_at < utcnow():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This download link is invalid or has expired")
    return Response(
        content=record.content,
        media_type=record.content_type,
        headers={"Content-Disposition": f'attachment; filename="{record.filename}"'},
    )
