from datetime import timedelta

from app.core.security import generate_token, hash_password, hash_token
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.export import ExportToken, ExportType
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


async def _create_verified_user(session, email, role=UserRole.OWNER, invited_by_user_id=None):
    user = User(
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Test User",
        role=role,
        invited_by_user_id=invited_by_user_id,
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
    pm = PaymentMethod(user_id=user.id, name="Cash Wallet", type=PaymentMethodType.CASH)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, name="Grocery", category_type=CategoryType.EXPENSE):
    category = Category(user_id=user.id, name=name, category_type=category_type)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _make_transaction(client, pm_id, category_id, date="2026-07-01", amount="25.00", merchant="Costco"):
    response = await client.post(
        "/transactions",
        json={
            "payment_method_id": str(pm_id),
            "date": date,
            "merchant": merchant,
            "total_amount": amount,
            "transaction_type": "Expense",
            "line_items": [{"category_id": str(category_id), "item_name": "Groceries", "amount": amount}],
        },
    )
    assert response.status_code == 201
    return response.json()


class TestExportTransactionsCsv:
    async def test_requires_authentication(self, client):
        response = await client.get("/exports/transactions.csv")
        assert response.status_code == 401

    async def test_partner_forbidden(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner_email = f"partner-{unique_email}"
        await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
        await _login(client, partner_email)

        response = await client.get("/exports/transactions.csv")
        assert response.status_code == 403

    async def test_generates_downloadable_csv(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        await _make_transaction(client, pm.id, category.id)

        response = await client.get("/exports/transactions.csv")
        assert response.status_code == 200
        body = response.json()
        assert body["download_url"].startswith("/exports/download/")
        assert "expires_at" in body

        download = await client.get(body["download_url"])
        assert download.status_code == 200
        assert download.headers["content-type"].startswith("text/csv")
        assert "attachment" in download.headers["content-disposition"]
        content = download.text
        assert "Costco" in content
        assert "Grocery" in content
        assert "25.00" in content
        # utf-8-sig strips the BOM on decode via `.text` (httpx uses the
        # charset the server declares); assert the raw bytes carry a real BOM
        # and that decoding it as utf-8-sig (not plain utf-8) yields a clean
        # first cell, guarding against the BOM leaking into "Date" as a
        # literal character.
        assert download.content.startswith(b"\xef\xbb\xbf")
        assert download.content.decode("utf-8-sig").startswith("Date,")


class TestExportMonthlyReportXlsx:
    async def test_requires_authentication(self, client):
        response = await client.get("/exports/monthly-report.xlsx", params={"month": 7, "year": 2026})
        assert response.status_code == 401

    async def test_generates_downloadable_xlsx(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        await _make_transaction(client, pm.id, category.id)

        response = await client.get("/exports/monthly-report.xlsx", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        body = response.json()

        download = await client.get(body["download_url"])
        assert download.status_code == 200
        assert download.headers["content-type"] == (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert download.content[:2] == b"PK"  # xlsx is a zip archive


class TestExportMonthlyReportPdf:
    async def test_requires_authentication(self, client):
        response = await client.get("/exports/monthly-report.pdf", params={"month": 7, "year": 2026})
        assert response.status_code == 401

    async def test_generates_downloadable_pdf(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)
        await _make_transaction(client, pm.id, category.id)

        response = await client.get("/exports/monthly-report.pdf", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        body = response.json()

        download = await client.get(body["download_url"])
        assert download.status_code == 200
        assert download.headers["content-type"] == "application/pdf"
        assert download.content[:4] == b"%PDF"

    async def test_generates_password_protected_pdf(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)

        unprotected = await client.get("/exports/monthly-report.pdf", params={"month": 7, "year": 2026})
        protected = await client.get(
            "/exports/monthly-report.pdf", params={"month": 7, "year": 2026, "password": "secret123"}
        )
        assert unprotected.status_code == 200
        assert protected.status_code == 200

        unprotected_download = await client.get(unprotected.json()["download_url"])
        protected_download = await client.get(protected.json()["download_url"])
        assert unprotected_download.content[:4] == b"%PDF"
        assert protected_download.content[:4] == b"%PDF"
        # An encrypted PDF's bytes differ from the unencrypted version of the
        # identical content — not a rigorous decryption test, but confirms the
        # password parameter actually changes the generated file.
        assert unprotected_download.content != protected_download.content


class TestDownloadExport:
    async def test_download_does_not_require_authentication(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = generate_token()
        session.add(
            ExportToken(
                user_id=owner.id,
                export_type=ExportType.CSV,
                filename="test.csv",
                content_type="text/csv",
                content=b"a,b\n1,2\n",
                token_hash=hash_token(token),
                expires_at=utcnow() + timedelta(minutes=15),
            )
        )
        await session.commit()

        response = await client.post("/auth/logout")
        assert response.status_code == 200

        download = await client.get(f"/exports/download/{token}")
        assert download.status_code == 200
        assert download.text == "a,b\n1,2\n"

    async def test_rejects_unknown_token(self, client):
        response = await client.get("/exports/download/not-a-real-token")
        assert response.status_code == 404

    async def test_rejects_expired_token(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = generate_token()
        session.add(
            ExportToken(
                user_id=owner.id,
                export_type=ExportType.CSV,
                filename="test.csv",
                content_type="text/csv",
                content=b"a,b\n1,2\n",
                token_hash=hash_token(token),
                expires_at=utcnow() - timedelta(minutes=1),
            )
        )
        await session.commit()

        response = await client.get(f"/exports/download/{token}")
        assert response.status_code == 404

    async def test_reusable_within_expiry_window(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = generate_token()
        session.add(
            ExportToken(
                user_id=owner.id,
                export_type=ExportType.CSV,
                filename="test.csv",
                content_type="text/csv",
                content=b"a,b\n1,2\n",
                token_hash=hash_token(token),
                expires_at=utcnow() + timedelta(minutes=15),
            )
        )
        await session.commit()

        first = await client.get(f"/exports/download/{token}")
        second = await client.get(f"/exports/download/{token}")
        assert first.status_code == 200
        assert second.status_code == 200
