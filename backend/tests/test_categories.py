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
    category = Category(user_id=user_id, name=name, category_type=category_type, is_shared=is_shared)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


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

    async def test_partner_sees_only_shared_categories(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        await _create_category(session, owner.id, "Housing", is_shared=False)
        await _create_category(session, owner.id, "Food", is_shared=True)

        partner_email = f"partner-{unique_email}"
        await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
        await _login(client, partner_email)

        response = await client.get("/categories")
        assert response.status_code == 200
        names = {c["name"] for c in response.json()}
        assert names == {"Food"}


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

    async def test_partner_cannot_create_category(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        partner_email = f"partner-{unique_email}"
        await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
        await _login(client, partner_email)

        response = await client.post("/categories", json={"name": "Pet Care", "category_type": "expense"})
        assert response.status_code == 403

    async def test_rejects_unknown_fields(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        await _login(client, unique_email)

        response = await client.post(
            "/categories", json={"name": "Pet Care", "category_type": "expense", "is_default": True}
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

    async def test_404_for_other_owners_category(self, client, session, unique_email):
        await _create_verified_user(session, unique_email)
        other_owner = await _create_verified_user(session, f"other-{unique_email}")
        other_category = await _create_category(session, other_owner.id, "Other's Category")
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{other_category.id}", json={"name": "Hacked"})
        assert response.status_code == 404


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


class TestCategorySharing:
    async def test_owner_can_toggle_sharing(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Housing", is_shared=False)
        await _login(client, unique_email)

        response = await client.patch(f"/categories/{category.id}/sharing", json={"is_shared": True})
        assert response.status_code == 200
        assert response.json()["is_shared"] is True

    async def test_partner_cannot_toggle_sharing(self, client, session, unique_email):
        owner = await _create_verified_user(session, unique_email)
        category = await _create_category(session, owner.id, "Housing", is_shared=False)
        partner_email = f"partner-{unique_email}"
        await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
        await _login(client, partner_email)

        response = await client.patch(f"/categories/{category.id}/sharing", json={"is_shared": True})
        assert response.status_code == 403
