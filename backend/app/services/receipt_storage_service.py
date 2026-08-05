"""PRD v2 §7.2: the only path in this codebase that permanently stores a
receipt image (every other OCR path is deliberately in-memory-only, see
ocr_service.py's docstring). Backed by Cloudflare R2 (S3-compatible).

boto3 is a synchronous client -- every call here must run via
asyncio.to_thread from an async caller, same pattern already used for
pytesseract in ocr_service.py."""

import asyncio
import logging
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger("billwise.receipt_storage")

_client_cache = None


def _get_client():
    global _client_cache
    if not (settings.r2_account_id and settings.r2_access_key_id and settings.r2_secret_access_key and settings.r2_bucket_name):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Receipt image storage is not configured",
        )
    if _client_cache is None:
        _client_cache = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
    return _client_cache


def build_receipt_image_key(owner_id: uuid.UUID, transaction_id: uuid.UUID, content_type: str) -> str:
    extension = {"image/jpeg": "jpg", "image/png": "png", "image/heic": "heic", "image/heif": "heif"}.get(
        content_type, "bin"
    )
    return f"receipts/{owner_id}/{transaction_id}/{uuid.uuid4()}.{extension}"


def _upload(key: str, file_bytes: bytes, content_type: str) -> None:
    _get_client().put_object(Bucket=settings.r2_bucket_name, Key=key, Body=file_bytes, ContentType=content_type)


def _get(key: str) -> tuple[bytes, str]:
    response = _get_client().get_object(Bucket=settings.r2_bucket_name, Key=key)
    content_type = response.get("ContentType") or "application/octet-stream"
    return response["Body"].read(), content_type


def _delete(key: str) -> None:
    _get_client().delete_object(Bucket=settings.r2_bucket_name, Key=key)


async def upload_receipt_image(key: str, file_bytes: bytes, content_type: str) -> None:
    try:
        await asyncio.to_thread(_upload, key, file_bytes, content_type)
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not store the receipt image"
        ) from exc


async def get_receipt_image(key: str) -> tuple[bytes, str]:
    try:
        return await asyncio.to_thread(_get, key)
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt image not found") from exc


async def delete_receipt_image(key: str) -> None:
    """Best-effort: an orphaned blob in R2 is a cheaper failure mode than
    blocking (or failing) a transaction delete on a storage hiccup."""
    try:
        await asyncio.to_thread(_delete, key)
    except (BotoCoreError, ClientError):
        logger.warning("Failed to delete receipt image %s from R2 — leaving an orphaned object", key)
