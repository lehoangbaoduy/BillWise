from unittest.mock import AsyncMock, patch

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.partner_permission import PartnerPermission
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.user import User, UserRole

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


async def _login(client, email):
    return await client.post("/auth/login", json={"email": email, "password": VALID_PASSWORD})


async def _authed_client(client, session, unique_email):
    user = await _create_verified_owner(session, unique_email)
    await _login(client, unique_email)
    return user


async def _make_payment_method(session, user):
    pm = PaymentMethod(user_id=user.id, name="Test Card", type=PaymentMethodType.CREDIT_CARD)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, is_shared=False):
    category = Category(user_id=user.id, name="Grocery", category_type=CategoryType.EXPENSE, is_shared=is_shared)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _make_partner(session, owner, unique_email):
    partner = User(
        email=f"partner-{unique_email}",
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Partner User",
        role=UserRole.PARTNER,
        invited_by_user_id=owner.id,
        email_verified_at=utcnow(),
    )
    session.add(partner)
    await session.flush()
    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=True))
    await session.commit()
    return partner


async def _create_transaction(client, pm_id, category_id, amount="25.00"):
    response = await client.post(
        "/transactions",
        json={
            "payment_method_id": str(pm_id),
            "date": "2026-07-01",
            "merchant": "Costco",
            "total_amount": amount,
            "transaction_type": "Expense",
            "line_items": [{"category_id": str(category_id), "item_name": "Receipt", "amount": amount}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


class TestUploadReceiptImage:
    async def test_uploads_and_sets_receipt_image_key(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        with patch("app.api.transactions.upload_receipt_image", new_callable=AsyncMock) as mock_upload:
            response = await client.post(
                f"/transactions/{transaction_id}/receipt-image",
                files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
            )
        assert response.status_code == 200, response.text
        mock_upload.assert_called_once()
        body = response.json()
        assert body["id"] == transaction_id

        get_response = await client.get(f"/transactions/{transaction_id}")
        assert get_response.json()["receipt_image_key"] is not None

    async def test_404_for_transaction_not_owned_by_caller(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_owner = await _create_verified_owner(session, f"other-{unique_email}")
        other_pm = PaymentMethod(user_id=other_owner.id, name="Other Card", type=PaymentMethodType.CREDIT_CARD)
        session.add(other_pm)
        await session.commit()
        await session.refresh(other_pm)
        other_category = Category(user_id=other_owner.id, name="Grocery", category_type=CategoryType.EXPENSE)
        session.add(other_category)
        await session.commit()
        await session.refresh(other_category)

        from app.models.transaction import Transaction, TransactionSource, TransactionType

        other_transaction = Transaction(
            user_id=other_owner.id,
            payment_method_id=other_pm.id,
            date="2026-07-01",
            merchant="Costco",
            total_amount="10.00",
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
        )
        session.add(other_transaction)
        await session.commit()
        await session.refresh(other_transaction)

        response = await client.post(
            f"/transactions/{other_transaction.id}/receipt-image",
            files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
        )
        assert response.status_code == 404

    async def test_rejects_oversized_file(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        response = await client.post(
            f"/transactions/{transaction_id}/receipt-image",
            files={"file": ("receipt.jpg", b"x" * (10 * 1024 * 1024 + 1), "image/jpeg")},
        )
        assert response.status_code == 413

    async def test_rejects_unsupported_content_type(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        response = await client.post(
            f"/transactions/{transaction_id}/receipt-image",
            files={"file": ("receipt.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 415

    async def test_transaction_kept_when_r2_upload_fails(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        with patch(
            "app.api.transactions.upload_receipt_image", new_callable=AsyncMock, side_effect=Exception("R2 down")
        ):
            response = await client.post(
                f"/transactions/{transaction_id}/receipt-image",
                files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
            )
        assert response.status_code == 502

        get_response = await client.get(f"/transactions/{transaction_id}")
        assert get_response.status_code == 200
        assert get_response.json()["receipt_image_key"] is None


class TestGetReceiptImage:
    async def test_streams_image_bytes_for_owner(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        with patch("app.api.transactions.upload_receipt_image", new_callable=AsyncMock):
            await client.post(
                f"/transactions/{transaction_id}/receipt-image",
                files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
            )

        with patch(
            "app.api.transactions.get_receipt_image",
            new_callable=AsyncMock,
            return_value=(b"fake-image-bytes", "image/jpeg"),
        ) as mock_get:
            response = await client.get(f"/transactions/{transaction_id}/receipt-image")
        assert response.status_code == 200
        assert response.content == b"fake-image-bytes"
        assert response.headers["content-type"] == "image/jpeg"
        mock_get.assert_called_once()

    async def test_404_when_no_image_attached(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        response = await client.get(f"/transactions/{transaction_id}/receipt-image")
        assert response.status_code == 404

    async def test_plain_partner_cannot_see_image_on_private_category_transaction(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        private_category = await _make_category(session, owner, is_shared=False)
        transaction_id = await _create_transaction(client, pm.id, private_category.id)

        with patch("app.api.transactions.upload_receipt_image", new_callable=AsyncMock):
            await client.post(
                f"/transactions/{transaction_id}/receipt-image",
                files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
            )

        partner = await _make_partner(session, owner, unique_email)
        await _login(client, partner.email)

        response = await client.get(f"/transactions/{transaction_id}/receipt-image")
        assert response.status_code == 404


class TestDeleteTransactionCascadesReceiptImage:
    async def test_deletes_r2_object_when_transaction_deleted(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        with patch("app.api.transactions.upload_receipt_image", new_callable=AsyncMock):
            await client.post(
                f"/transactions/{transaction_id}/receipt-image",
                files={"file": ("receipt.jpg", b"fake-image-bytes", "image/jpeg")},
            )

        with patch("app.api.transactions.delete_receipt_image", new_callable=AsyncMock) as mock_delete:
            response = await client.delete(f"/transactions/{transaction_id}")
        assert response.status_code == 204
        mock_delete.assert_called_once()

    async def test_does_not_call_delete_when_no_image_attached(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        transaction_id = await _create_transaction(client, pm.id, category.id)

        with patch("app.api.transactions.delete_receipt_image", new_callable=AsyncMock) as mock_delete:
            response = await client.delete(f"/transactions/{transaction_id}")
        assert response.status_code == 204
        mock_delete.assert_not_called()
