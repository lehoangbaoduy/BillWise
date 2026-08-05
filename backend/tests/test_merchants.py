from app.core.security import hash_password
from app.models._common import utcnow
from app.models.merchant import Merchant
from app.models.partner_permission import PartnerPermission
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


async def _make_partner(session, owner, unique_email, can_add_transactions=False):
    partner_email = f"partner-{unique_email}"
    partner = await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=can_add_transactions))
    await session.commit()
    return partner, partner_email


async def _create_merchant(session, user_id, name, is_shared=True, type_=None):
    merchant = Merchant(user_id=user_id, name=name, is_shared=is_shared, type=type_)
    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant


class TestListMerchants:
    async def test_requires_authentication(self, client):
        response = await client.get("/merchants")
        assert response.status_code == 401

    async def test_owner_sees_own_merchants(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _create_merchant(session, owner.id, "Costco", is_shared=False)
        await _create_merchant(session, owner.id, "Target", is_shared=True)
        await _login(client, unique_email)

        response = await client.get("/merchants")
        assert response.status_code == 200
        names = {m["name"] for m in response.json()}
        assert names == {"Costco", "Target"}

    async def test_partner_sees_only_shared_merchants(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _create_merchant(session, owner.id, "Costco", is_shared=False)
        await _create_merchant(session, owner.id, "Target", is_shared=True)
        _, partner_email = await _make_partner(session, owner, unique_email)
        await _login(client, partner_email)

        response = await client.get("/merchants")
        assert response.status_code == 200
        names = {m["name"] for m in response.json()}
        assert names == {"Target"}

    async def test_excludes_deactivated_merchants(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _login(client, unique_email)
        create_response = await client.post("/merchants", json={"name": "Old Shop"})
        await client.delete(f"/merchants/{create_response.json()['id']}")

        response = await client.get("/merchants")
        assert response.json() == []


class TestCreateMerchant:
    async def test_owner_can_create_merchant(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post(
            "/merchants", json={"name": "Costco", "type": "Whole sale", "city": "Seattle", "state": "WA"}
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Costco"
        assert body["type"] == "Whole sale"
        assert body["is_shared"] is True

    async def test_partner_with_permission_can_create_merchant(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        response = await client.post("/merchants", json={"name": "New Store"})
        assert response.status_code == 201

    async def test_partner_without_permission_cannot_create_merchant(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=False)
        await _login(client, partner_email)

        response = await client.post("/merchants", json={"name": "New Store"})
        assert response.status_code == 403

    async def test_create_is_idempotent_case_insensitive(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        first = await client.post("/merchants", json={"name": "Costco", "city": "Seattle"})
        second = await client.post("/merchants", json={"name": "COSTCO"})

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["id"] == second.json()["id"]
        # Existing row's fields aren't overwritten by the second, field-less call.
        assert second.json()["city"] == "Seattle"

        list_response = await client.get("/merchants")
        assert len(list_response.json()) == 1

    async def test_rejects_unknown_fields(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post("/merchants", json={"name": "Costco", "is_active": False})
        assert response.status_code == 422


class TestUpdateMerchant:
    async def test_owner_can_update_merchant(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        merchant = await _create_merchant(session, owner.id, "Costco")
        await _login(client, unique_email)

        response = await client.patch(f"/merchants/{merchant.id}", json={"type": "Whole sale", "state": "WA"})
        assert response.status_code == 200
        assert response.json()["type"] == "Whole sale"
        assert response.json()["state"] == "WA"

    async def test_partner_cannot_update_merchant(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        merchant = await _create_merchant(session, owner.id, "Costco")
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        response = await client.patch(f"/merchants/{merchant.id}", json={"type": "Whole sale"})
        assert response.status_code == 403

    async def test_404_for_other_owners_merchant(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        other_owner = await _create_verified_user(session, f"other-{unique_email}")
        other_merchant = await _create_merchant(session, other_owner.id, "Other's Shop")
        await _login(client, unique_email)

        response = await client.patch(f"/merchants/{other_merchant.id}", json={"type": "Restaurant"})
        assert response.status_code == 404


class TestMerchantSharing:
    async def test_owner_can_toggle_sharing(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        merchant = await _create_merchant(session, owner.id, "Costco", is_shared=True)
        await _login(client, unique_email)

        response = await client.patch(f"/merchants/{merchant.id}/sharing", json={"is_shared": False})
        assert response.status_code == 200
        assert response.json()["is_shared"] is False

    async def test_partner_cannot_toggle_sharing(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        merchant = await _create_merchant(session, owner.id, "Costco")
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        response = await client.patch(f"/merchants/{merchant.id}/sharing", json={"is_shared": False})
        assert response.status_code == 403


class TestDeleteMerchant:
    async def test_deactivates_rather_than_hard_deletes(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        merchant = await _create_merchant(session, owner.id, "Costco")
        await _login(client, unique_email)

        response = await client.delete(f"/merchants/{merchant.id}")
        assert response.status_code == 204

        list_response = await client.get("/merchants")
        names = {m["name"] for m in list_response.json()}
        assert "Costco" not in names
