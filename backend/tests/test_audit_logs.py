from app.core.security import hash_password
from app.models._common import utcnow
from app.models.partner_permission import PartnerPermission
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.user import User, UserRole

VALID_PASSWORD = "StrongPass123"


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
    await session.refresh(user)
    return user


async def _login(client, email):
    return await client.post("/auth/login", json={"email": email, "password": VALID_PASSWORD})


async def _authed_client(client, session, unique_email):
    user = await _create_verified_user(session, unique_email)
    await _login(client, unique_email)
    return user


async def _make_partner(session, owner, unique_email, can_add_transactions=False):
    partner_email = f"partner-{unique_email}"
    partner = await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=can_add_transactions))
    await session.commit()
    return partner, partner_email


class TestListAuditLogs:
    async def test_requires_authentication(self, client):
        response = await client.get("/audit-logs")
        assert response.status_code == 401

    async def test_partner_forbidden(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        await _login(client, partner_email)

        response = await client.get("/audit-logs")
        assert response.status_code == 403

    async def test_login_generates_a_persisted_audit_row(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)

        response = await client.get("/audit-logs")
        assert response.status_code == 200
        actions = [row["action"] for row in response.json()]
        assert "user.login_succeeded" in actions
        assert "user.registered" not in actions  # this test creates the user directly, not via /auth/register

    async def test_transaction_create_is_audited_with_entity_reference(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = PaymentMethod(user_id=owner.id, name="Cash Wallet", type=PaymentMethodType.CASH)
        session.add(pm)
        await session.commit()
        await session.refresh(pm)

        from app.models.category import Category, CategoryType

        category = Category(user_id=owner.id, name="Grocery", category_type=CategoryType.EXPENSE)
        session.add(category)
        await session.commit()
        await session.refresh(category)

        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "25.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "25.00"}],
            },
        )
        assert create_response.status_code == 201
        transaction_id = create_response.json()["id"]

        response = await client.get("/audit-logs", params={"action": "transaction.created"})
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["entity_type"] == "transaction"
        assert rows[0]["entity_id"] == transaction_id
        assert rows[0]["user_id"] == str(owner.id)
        assert rows[0]["metadata"]["total_amount"] == "25.00"

    async def test_owner_sees_partner_actions_too(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)
        await client.post("/auth/logout")
        await _login(client, unique_email)  # back to owner for the query

        response = await client.get("/audit-logs", params={"action": "user.login_succeeded"})
        assert response.status_code == 200
        user_ids = {row["user_id"] for row in response.json()}
        assert str(owner.id) in user_ids
        assert str(partner.id) in user_ids

    async def test_filters_by_entity_type(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)

        response = await client.get("/audit-logs", params={"entity_type": "user"})
        assert response.status_code == 200
        assert all(row["entity_type"] == "user" for row in response.json())

    async def test_pagination_limit_and_offset(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        # Generate several more audit rows (repeated failed logins).
        for _ in range(3):
            await client.post("/auth/login", json={"email": owner.email, "password": "wrong-password"})

        first_page = await client.get("/audit-logs", params={"limit": 2, "offset": 0})
        second_page = await client.get("/audit-logs", params={"limit": 2, "offset": 2})
        assert first_page.status_code == 200
        assert second_page.status_code == 200
        assert len(first_page.json()) == 2
        first_ids = {row["id"] for row in first_page.json()}
        second_ids = {row["id"] for row in second_page.json()}
        assert first_ids.isdisjoint(second_ids)

    async def test_newest_first_ordering(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        await client.post("/auth/login", json={"email": owner.email, "password": "wrong-password"})

        response = await client.get("/audit-logs")
        rows = response.json()
        timestamps = [row["created_at"] for row in rows]
        assert timestamps == sorted(timestamps, reverse=True)
