"""Structures raw OCR text into the receipt-extraction schema (PRD §29.1) via
Anthropic Claude Haiku. Only extracted text is ever sent here — never the original
receipt image (PRD §7.5). Anthropic's data-usage policy does not train on API
inputs, satisfying the PRD's no-training-on-API-data requirement."""

import json
import logging

from anthropic import AsyncAnthropic
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.ocr import OcrStatus, ReceiptExtractionItem, ReceiptExtractionResult

logger = logging.getLogger("billwise.ai_structuring")

_MODEL = "claude-haiku-4-5-20251001"
_LOW_CONFIDENCE_THRESHOLD = 0.6
# Leaves a wide margin under settings.ocr_timeout_seconds (40s) for asyncio.to_thread
# scheduling overhead plus the local Tesseract pass that runs before this call.
_CLIENT_TIMEOUT_SECONDS = 20.0
_ALLOWED_CATEGORIES = {
    "Housing",
    "Food",
    "Car",
    "Shopping",
    "Health & Personal",
    "Subscription",
    "Saving",
    "Family & Support",
    "Reimbursement",
    "Income",
}

_SYSTEM_PROMPT = f"""You extract structured data from OCR text of a retail receipt.
Respond with ONLY a JSON object matching this exact shape — no prose, no markdown fences:
{{
  "merchant": string or null,
  "date": "YYYY-MM-DD" or null,
  "total": number or null,
  "tax": number or null,
  "items": [
    {{"name": string, "amount": number, "suggested_category": string, "suggested_subcategory": string or null, "confidence": number between 0 and 1}}
  ],
  "warnings": [string, ...]
}}
suggested_category must be exactly one of: {sorted(_ALLOWED_CATEGORIES)}, or "Uncategorized" if you
are not confident. If the item amounts do not sum to the total, still return your best-effort items
and add a warning describing the mismatch. If you cannot determine a field, use null rather than
guessing — never invent a merchant, date, or amount that is not supported by the text."""


# Cached like app.core.db's module-level `engine` — avoids re-establishing a fresh
# httpx connection pool on every receipt scan. Tests reset this via monkeypatch when
# they need to swap in a fake client.
_client_cache: AsyncAnthropic | None = None


def _client() -> AsyncAnthropic:
    global _client_cache
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Receipt structuring is not configured — enter this transaction manually",
        )
    if _client_cache is None:
        _client_cache = AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=_CLIENT_TIMEOUT_SECONDS)
    return _client_cache


def _coerce_low_confidence(item: dict) -> dict:
    try:
        confidence = float(item.get("confidence", 0) or 0)
    except (TypeError, ValueError):
        confidence = 0.0
    category = item.get("suggested_category")
    if confidence < _LOW_CONFIDENCE_THRESHOLD or category not in _ALLOWED_CATEGORIES:
        return {**item, "confidence": confidence, "suggested_category": "Uncategorized", "suggested_subcategory": None}
    return {**item, "confidence": confidence}


async def structure_receipt_text(raw_text: str) -> ReceiptExtractionResult:
    client = _client()
    try:
        response = await client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_text}],
        )
    except Exception as exc:
        # Log only the exception type, not its message — the Anthropic SDK's error
        # text can echo request/response details and must never reach application logs.
        logger.warning("Anthropic structuring call failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Receipt structuring failed — enter this transaction manually",
        ) from exc

    raw = "".join(block.text for block in response.content if block.type == "text")
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Length only, never content — `raw` is structured from receipt text and may
        # carry merchant names, addresses, or other user financial/PII data.
        logger.warning("Anthropic returned non-JSON structuring output (%d chars)", len(raw))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Receipt structuring failed — enter this transaction manually",
        ) from None

    items_raw = [_coerce_low_confidence(item) for item in parsed.get("items", [])]
    warnings = list(parsed.get("warnings", []))

    try:
        items = [ReceiptExtractionItem(**item) for item in items_raw]
    except Exception as exc:
        # Pydantic validation errors echo the offending field values, which here are
        # receipt line items (merchant/item names) — log only the exception type.
        logger.warning("Anthropic structuring output failed schema validation: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Receipt structuring failed — enter this transaction manually",
        ) from exc

    has_low_confidence = any(item.confidence < _LOW_CONFIDENCE_THRESHOLD for item in items)
    ocr_status = OcrStatus.LOW_CONFIDENCE if (warnings or has_low_confidence or not items) else OcrStatus.SUCCESS

    return ReceiptExtractionResult(
        ocr_status=ocr_status,
        merchant=parsed.get("merchant"),
        date=parsed.get("date"),
        total=parsed.get("total"),
        tax=parsed.get("tax"),
        items=items,
        warnings=warnings,
    )
