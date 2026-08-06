from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
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


async def _create_category(session, user_id, name, is_shared=False, category_type=CategoryType.EXPENSE):
    # is_shared defaults to False here specifically to prove list_categories no
    # longer filters on it at all -- a category is visible to every household
    # member regardless of what's persisted in this now-vestigial column.
    category = Category(user_id=user_id, name=name, category_type=category_type, is_shared=is_shared)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _create_partner(session, owner_id, email):
    return await _create_verified_user(session, email, role=UserRole.PARTNER, invited_by_user_id=owner_id)


class TestListCategories:
    async def test_requires_authentication(self, client):
        response = await client.get("/categories")
        assert response.status_code == 401

    async def test_owner_sees_own_categories(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _create_category(session, owner.id, "Housing")
        await _create_category(session, owner.id, "Food", is_shared=True)
        await _login(client, unique_email)

        response = await client.get("/categories")
        assert response.status_code == 200
        names = {c["name"] for c in response.json()}
        assert names == {"Housing", "Food"}

    async def test_partner_sees_all_household_categories(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _create_category(session, owner.id, "Housing", is_shared=False)
        await _create_category(session, owner.id, "Food", is_shared=True)
        partner = await _create_partner(session, owner.id, f"partner-{unique_email}")
        await _login(client, partner.email)

        response = await client.get("/categories")
        assert response.status_code == 200
        names = {c["name"] for c in response.json()}
        assert names == {"Housing", "Food"}


class TestCreateCategory:
    async def test_owner_can_create_custom_category(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post(
            "/categories", json={"name": "Pet Care", "category_type": "expense", "emoji": "🐶"}
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Pet Care"
        assert response.json()["is_default"] is False

    async def test_new_category_is_always_shared(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post("/categories", json={"name": "Pet Care", "category_type": "expense"})
        assert response.status_code == 201
        assert response.json()["is_shared"] is True

    async def test_partner_can_create_category(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        partner = await _create_partner(session, owner.id, f"partner-{unique_email}")
        await _login(client, partner.email)

        response = await client.post("/categories", json={"name": "Pet Care", "category_type": "expense"})
        assert response.status_code == 201
        assert response.json()["is_shared"] is True

    async def test_partner_created_category_belongs_to_household_owner(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        partner = await _create_partner(session, owner.id, f"partner-{unique_email}")
        await _login(client, partner.email)

        await client.post("/categories", json={"name": "Pet Care", "category_type": "expense"})
        await _login(client, owner.email)
        response = await client.get("/categories")
        names = {c["name"] for c in response.json()}
        assert "Pet Care" in names

    async def test_rejects_unknown_fields(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post(
            "/categories", json={"name": "Pet Care", "category_type": "expense", "is_default": True}
        )
        assert response.status_code == 422

    async def test_rejects_is_shared_field(self, client, session, unique_email):
        # is_shared is no longer client-settable -- every category is shared,
        # full stop, so accepting the field would silently no-op instead of
        # surfacing the caller's outdated assumption.
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post(
            "/categories", json={"name": "Pet Care", "category_type": "expense", "is_shared": False}
        )
        assert response.status_code == 422


class TestUpdateCategory:
    async def test_updates_own_category(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Pet Care")
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{category.id}", json={"name": "Pets"})
        assert response.status_code == 200
        assert response.json()["name"] == "Pets"

    async def test_partner_can_update_household_category(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Pet Care")
        partner = await _create_partner(session, owner.id, f"partner-{unique_email}")
        await _login(client, partner.email)

        response = await client.patch(f"/categories/{category.id}", json={"name": "Pets", "emoji": "🐾"})
        assert response.status_code == 200
        assert response.json()["name"] == "Pets"
        assert response.json()["emoji"] == "🐾"

    async def test_404_for_other_owners_category(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        other_owner = await _create_verified_user(session, f"other-{unique_email}")
        other_category = await _create_category(session, other_owner.id, "Other's Category")
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{other_category.id}", json={"name": "Hacked"})
        assert response.status_code == 404

    async def test_rejects_is_shared_field(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Pet Care")
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{category.id}", json={"is_shared": False})
        assert response.status_code == 422


class TestDeleteCategory:
    async def test_deactivates_rather_than_hard_deletes(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Pet Care")
        await _login(client, unique_email)

        response = await client.delete(f"/categories/{category.id}")
        assert response.status_code == 204

        list_response = await client.get("/categories")
        names = {c["name"] for c in list_response.json()}
        assert "Pet Care" not in names

    async def test_partner_can_delete_household_category(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Pet Care")
        partner = await _create_partner(session, owner.id, f"partner-{unique_email}")
        await _login(client, partner.email)

        response = await client.delete(f"/categories/{category.id}")
        assert response.status_code == 204


class TestCategorySharingRouteRemoved:
    async def test_sharing_endpoint_no_longer_exists(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Housing", is_shared=False)
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{category.id}/sharing", json={"is_shared": True})
        assert response.status_code == 404
