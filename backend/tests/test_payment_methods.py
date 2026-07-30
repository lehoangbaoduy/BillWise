from app.core.security import hash_password
from app.models._common import utcnow
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
    await _create_verified_owner(session, unique_email)
    await _login(client, unique_email)
    return client


class TestCreatePaymentMethod:
    async def test_requires_authentication(self, client):
        response = await client.post(
            "/payment-methods", json={"name": "Chase Sapphire", "type": "Credit Card"}
        )
        assert response.status_code == 401

    async def test_creates_card_alias(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/payment-methods",
            json={
                "name": "Chase Sapphire",
                "type": "Credit Card",
                "issuer": "Chase",
                "last_four_optional": "4242",
                "default_cashback_rate": "2.00",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Chase Sapphire"
        assert body["last_four_optional"] == "4242"
        assert "id" in body

    async def test_creates_tracked_savings_balance(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/payment-methods",
            json={"name": "Ally Savings", "type": "Tracked Savings", "current_balance": "5000.00"},
        )
        assert response.status_code == 201
        assert response.json()["current_balance"] == "5000.00"

    async def test_rejects_forbidden_card_number_field(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/payment-methods",
            json={"name": "Chase Sapphire", "type": "Credit Card", "card_number": "4111111111111111"},
        )
        assert response.status_code == 422

    async def test_rejects_forbidden_cvv_field(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/payment-methods", json={"name": "Chase Sapphire", "type": "Credit Card", "cvv": "123"}
        )
        assert response.status_code == 422


class TestListPaymentMethods:
    async def test_only_returns_own_active_methods(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        await client.post("/payment-methods", json={"name": "Cash Wallet", "type": "Cash"})

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        from app.models.payment_method import PaymentMethod, PaymentMethodType

        session.add(PaymentMethod(user_id=other_user.id, name="Other's Card", type=PaymentMethodType.CASH))
        await session.commit()

        response = await client.get("/payment-methods")
        assert response.status_code == 200
        names = {pm["name"] for pm in response.json()}
        assert names == {"Cash Wallet"}

    async def test_excludes_deactivated_methods(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        create_response = await client.post("/payment-methods", json={"name": "Old Card", "type": "Credit Card"})
        pm_id = create_response.json()["id"]

        await client.delete(f"/payment-methods/{pm_id}")

        response = await client.get("/payment-methods")
        assert response.json() == []


class TestGetPaymentMethod:
    async def test_404_for_other_users_method(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        from app.models.payment_method import PaymentMethod, PaymentMethodType

        other_pm = PaymentMethod(user_id=other_user.id, name="Other's Card", type=PaymentMethodType.CASH)
        session.add(other_pm)
        await session.commit()
        await session.refresh(other_pm)

        response = await client.get(f"/payment-methods/{other_pm.id}")
        assert response.status_code == 404


class TestUpdatePaymentMethod:
    async def test_updates_own_method(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        create_response = await client.post("/payment-methods", json={"name": "Chase Sapphire", "type": "Credit Card"})
        pm_id = create_response.json()["id"]

        response = await client.patch(f"/payment-methods/{pm_id}", json={"name": "Chase Sapphire Reserve"})
        assert response.status_code == 200
        assert response.json()["name"] == "Chase Sapphire Reserve"

    async def test_rejects_forbidden_fields_on_update(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        create_response = await client.post("/payment-methods", json={"name": "Chase Sapphire", "type": "Credit Card"})
        pm_id = create_response.json()["id"]

        response = await client.patch(f"/payment-methods/{pm_id}", json={"routing_number": "123456789"})
        assert response.status_code == 422


class TestDeletePaymentMethod:
    async def test_deactivates_rather_than_hard_deletes(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        create_response = await client.post("/payment-methods", json={"name": "Chase Sapphire", "type": "Credit Card"})
        pm_id = create_response.json()["id"]

        response = await client.delete(f"/payment-methods/{pm_id}")
        assert response.status_code == 204

        get_response = await client.get(f"/payment-methods/{pm_id}")
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] is False
