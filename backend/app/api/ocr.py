import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_owner
from app.core.config import settings
from app.core.db import get_session
from app.core.rate_limit import limiter
from app.models.transaction import TransactionSource
from app.models.user import User
from app.schemas.ocr import ReceiptExtractionResult
from app.schemas.transaction import TransactionCreate, TransactionPublic
from app.services import ai_structuring_service, ocr_service
from app.services.transaction_validation import create_transaction_record, to_transaction_public

router = APIRouter(prefix="/ocr", tags=["ocr"])


async def _extract_and_structure(file_bytes: bytes, content_type: str) -> ReceiptExtractionResult:
    # asyncio.to_thread cannot forcibly kill the underlying OS thread: if the
    # wait_for below times out, Tesseract keeps running in the thread pool until
    # it finishes on its own. Acceptable at this MVP's single-instance, 20/hour-
    # rate-limited scale; would need a killable worker process pool to fully close.
    raw_text = await asyncio.to_thread(ocr_service.extract_text, file_bytes, content_type)
    return await ai_structuring_service.structure_receipt_text(raw_text)


@router.post("/receipt", response_model=ReceiptExtractionResult)
@limiter.limit(settings.ocr_rate_limit_window)
async def scan_receipt(
    request: Request,
    file: UploadFile,
    user: User = Depends(require_owner),
) -> ReceiptExtractionResult:
    # Reject oversized uploads from the Content-Length header before buffering the
    # body into memory, so an attacker can't force a full-size read of a huge file
    # just to have it rejected afterward.
    content_length = request.headers.get("content-length")
    if content_length is not None and int(content_length) > settings.ocr_max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 10MB limit — enter this transaction manually",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is empty")
    if len(file_bytes) > settings.ocr_max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 10MB limit — enter this transaction manually",
        )

    content_type = file.content_type or ""
    try:
        return await asyncio.wait_for(
            _extract_and_structure(file_bytes, content_type), timeout=settings.ocr_timeout_seconds
        )
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Receipt scanning timed out — enter this transaction manually",
        ) from exc


@router.post("/confirm-transaction", response_model=TransactionPublic, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.ocr_rate_limit_window)
async def confirm_transaction(
    request: Request,
    body: TransactionCreate,
    user: User = Depends(require_owner),
    session: AsyncSession = Depends(get_session),
) -> TransactionPublic:
    """Creates the real Transaction from the user-reviewed/edited OCR extraction.
    Never called automatically — the client only sends this after the user confirms
    on the Receipt Review screen (PRD §13.2)."""
    transaction, possible_duplicate = await create_transaction_record(
        session, user, body, TransactionSource.RECEIPT_OCR
    )
    return await to_transaction_public(session, transaction, possible_duplicate=possible_duplicate)
