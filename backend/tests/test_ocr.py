from decimal import Decimal

import pytest
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.transaction import Transaction, TransactionSource, TransactionType
from app.models.user import User, UserRole
from app.schemas.ocr import OcrStatus, ReceiptExtractionItem, ReceiptExtractionResult
from app.services import ai_structuring_service, ocr_service

VALID_PASSWORD = "StrongPass123"


async def _create_verified_owner(session, email):
    user = User(
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Jamie Owner",
        role=UserRole.OWNER,
        email_verified_at=utcnow(),
    )
    session.add(user)
    await session.flush()
    await session.commit()
    return user


async def _authed_client(client, session, unique_email):
    user = await _create_verified_owner(session, unique_email)
    await client.post("/auth/login", json={"email": unique_email, "password": VALID_PASSWORD})
    return user


async def _make_payment_method(session, user, type_=PaymentMethodType.CASH):
    pm = PaymentMethod(user_id=user.id, name="Cash Wallet", type=type_)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Grocery"):
    category = Category(user_id=user.id, name=name, category_type=category_type)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


_SUCCESSFUL_EXTRACTION = ReceiptExtractionResult(
    ocr_status=OcrStatus.SUCCESS,
    merchant="Costco",
    date="2026-07-05",
    total=Decimal("90.00"),
    tax=Decimal("5.20"),
    items=[
        ReceiptExtractionItem(
            name="Chicken",
            amount=Decimal("20.00"),
            suggested_category="Food",
            suggested_subcategory="Grocery",
            confidence=0.92,
        )
    ],
    warnings=[],
)


class TestScanReceipt:
    async def test_requires_authentication(self, client):
        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"fake-bytes", "image/jpeg")})
        assert response.status_code == 401

    async def test_rejects_empty_file(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"", "image/jpeg")})
        assert response.status_code == 422

    async def test_rejects_oversized_file(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)
        monkeypatch.setattr(settings, "ocr_max_upload_bytes", 10)
        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"x" * 100, "image/jpeg")})
        assert response.status_code == 413

    async def test_rejects_unsupported_file_type(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post("/ocr/receipt", files={"file": ("receipt.txt", b"not an image", "text/plain")})
        assert response.status_code == 415

    async def test_successful_scan_returns_structured_extraction(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)
        monkeypatch.setattr("app.services.ocr_service.extract_text", lambda *a, **k: "Costco\nChicken $20.00")

        async def _fake_structure(raw_text: str) -> ReceiptExtractionResult:
            assert raw_text == "Costco\nChicken $20.00"
            return _SUCCESSFUL_EXTRACTION

        monkeypatch.setattr("app.services.ai_structuring_service.structure_receipt_text", _fake_structure)

        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"fake-bytes", "image/jpeg")})
        assert response.status_code == 200
        body = response.json()
        assert body["ocr_status"] == "success"
        assert body["merchant"] == "Costco"
        assert body["items"][0]["suggested_category"] == "Food"

    async def test_unreadable_image_falls_back_to_manual_entry(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)

        def _raise_unreadable(*a, **k):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="unreadable")

        monkeypatch.setattr("app.services.ocr_service.extract_text", _raise_unreadable)
        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"fake-bytes", "image/jpeg")})
        assert response.status_code == 422

    async def test_malformed_pdf_bytes_return_422_not_500(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        # Starts with the PDF magic bytes so it's routed to the PDF parser, but the
        # rest is garbage — pymupdf.open must fail cleanly, not raise unhandled.
        response = await client.post(
            "/ocr/receipt", files={"file": ("receipt.pdf", b"%PDF-1.4\ngarbage not a real pdf", "application/pdf")}
        )
        assert response.status_code == 422

    async def test_routes_by_magic_bytes_not_spoofed_content_type(self, client, session, unique_email, monkeypatch):
        # Content-Type claims PDF but the bytes are plain text — should be treated as
        # an (unreadable) image rather than handed to the PDF parser, and fail cleanly.
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/ocr/receipt", files={"file": ("receipt.pdf", b"not a pdf or an image", "application/pdf")}
        )
        assert response.status_code == 422

    async def test_timeout_falls_back_to_manual_entry(self, client, session, unique_email, monkeypatch):
        import asyncio

        await _authed_client(client, session, unique_email)
        monkeypatch.setattr(settings, "ocr_timeout_seconds", 0.05)

        def _slow_extract(*a, **k):
            import time

            time.sleep(0.3)
            return "text"

        monkeypatch.setattr("app.services.ocr_service.extract_text", _slow_extract)
        response = await client.post("/ocr/receipt", files={"file": ("receipt.jpg", b"fake-bytes", "image/jpeg")})
        assert response.status_code == 504


class TestConfirmTransaction:
    async def test_requires_authentication(self, client):
        response = await client.post(
            "/ocr/confirm-transaction",
            json={
                "payment_method_id": "00000000-0000-0000-0000-000000000000",
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": "00000000-0000-0000-0000-000000000000", "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 401

    async def test_creates_transaction_with_receipt_ocr_source(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/ocr/confirm-transaction",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-05",
                "merchant": "Costco",
                "total_amount": "20.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Chicken", "amount": "20.00"}],
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["source"] == "Receipt OCR"
        assert body["possible_duplicate"] is False

    async def test_flags_possible_duplicate(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        existing = Transaction(
            user_id=user.id,
            payment_method_id=pm.id,
            date="2026-07-05",
            merchant="Costco",
            total_amount=Decimal("20.00"),
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
        )
        session.add(existing)
        await session.commit()

        response = await client.post(
            "/ocr/confirm-transaction",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-05",
                "merchant": "Costco",
                "total_amount": "20.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Chicken", "amount": "20.00"}],
            },
        )
        assert response.status_code == 201
        assert response.json()["possible_duplicate"] is True

    async def test_rejects_line_items_not_summing_to_total(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/ocr/confirm-transaction",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-05",
                "merchant": "Costco",
                "total_amount": "20.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Chicken", "amount": "15.00"}],
            },
        )
        assert response.status_code == 422


class TestAiStructuringService:
    """Unit-level tests against the Anthropic call boundary, mocked at the SDK client."""

    class _FakeTextBlock:
        type = "text"

        def __init__(self, text):
            self.text = text

    class _FakeResponse:
        def __init__(self, text):
            self.content = [TestAiStructuringService._FakeTextBlock(text)]

    class _FakeMessages:
        def __init__(self, response_text):
            self._response_text = response_text

        async def create(self, **kwargs):
            return TestAiStructuringService._FakeResponse(self._response_text)

    class _FakeAsyncAnthropic:
        def __init__(self, response_text):
            self.messages = TestAiStructuringService._FakeMessages(response_text)

    async def test_raises_503_when_api_key_not_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "")
        with pytest.raises(HTTPException) as exc_info:
            await ai_structuring_service.structure_receipt_text("some text")
        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    async def test_coerces_low_confidence_items_to_uncategorized(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        monkeypatch.setattr(ai_structuring_service, "_client_cache", None)
        response_json = (
            '{"merchant": "Costco", "date": "2026-07-05", "total": 20.00, "tax": null, '
            '"items": [{"name": "Chicken", "amount": 20.00, "suggested_category": "Food", '
            '"suggested_subcategory": "Grocery", "confidence": 0.3}], "warnings": []}'
        )
        monkeypatch.setattr(
            ai_structuring_service,
            "AsyncAnthropic",
            lambda **kwargs: TestAiStructuringService._FakeAsyncAnthropic(response_json),
        )
        result = await ai_structuring_service.structure_receipt_text("Costco\nChicken $20.00")
        assert result.items[0].suggested_category == "Uncategorized"
        assert result.ocr_status == OcrStatus.LOW_CONFIDENCE

    async def test_raises_502_on_malformed_json_response(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        monkeypatch.setattr(ai_structuring_service, "_client_cache", None)
        monkeypatch.setattr(
            ai_structuring_service,
            "AsyncAnthropic",
            lambda **kwargs: TestAiStructuringService._FakeAsyncAnthropic("not json at all"),
        )
        with pytest.raises(HTTPException) as exc_info:
            await ai_structuring_service.structure_receipt_text("Costco\nChicken $20.00")
        assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
