from app.core.security import hash_password
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.partner_permission import PartnerPermission
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


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Grocery"):
    category = Category(user_id=user.id, name=name, category_type=category_type)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _make_co_owner(session, owner, email):
    co_owner = User(
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Co-Owner User",
        role=UserRole.PARTNER,
        invited_by_user_id=owner.id,
        email_verified_at=utcnow(),
    )
    session.add(co_owner)
    await session.flush()
    session.add(PartnerPermission(partner_user_id=co_owner.id, is_co_owner=True))
    await session.commit()
    await session.refresh(co_owner)
    return co_owner


async def _make_budget(session, owner, category, created_by_user_id=None, is_shared=False, month=7, year=2026):
    budget = Budget(
        user_id=owner.id,
        created_by_user_id=created_by_user_id,
        category_id=category.id,
        month=month,
        year=year,
        budget_amount="100.00",
        is_shared=is_shared,
    )
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    return budget


class TestCreateBudget:
    async def test_requires_authentication(self, client):
        response = await client.post(
            "/budgets", json={"category_id": "00000000-0000-0000-0000-000000000000", "month": 7, "year": 2026, "budget_amount": "100.00"}
        )
        assert response.status_code == 401

    async def test_creates_budget(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)

        response = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        assert response.status_code == 201
        body = response.json()
        assert body["budget_amount"] == "300.00"
        assert body["month"] == 7
        assert body["year"] == 2026

    async def test_rejects_duplicate_category_month_year(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"})

        response = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "500.00"}
        )
        assert response.status_code == 422

    async def test_rejects_income_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        income_category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Paycheck")

        response = await client.post(
            "/budgets", json={"category_id": str(income_category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        assert response.status_code == 422

    async def test_rejects_other_users_category(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_category = await _make_category(session, other_user)

        response = await client.post(
            "/budgets", json={"category_id": str(other_category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        assert response.status_code == 422

    async def test_rejects_negative_amount(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)

        response = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "-1.00"}
        )
        assert response.status_code == 422


class TestListBudgets:
    async def test_only_returns_own_budgets_for_the_period(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"})

        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_category = await _make_category(session, other_user)
        from app.models.budget import Budget

        session.add(Budget(user_id=other_user.id, category_id=other_category.id, month=7, year=2026, budget_amount="999.00"))
        await session.commit()

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        amounts = {b["budget_amount"] for b in response.json()}
        assert amounts == {"300.00"}

    async def test_get_no_longer_auto_creates_rows_for_a_new_month(self, client, session, unique_email):
        # PRD v2 §8.2: the old lazy/reactive rollover-on-GET is removed in
        # favor of the scheduled renew_monthly_budgets job (see
        # test_budget_renewal.py) -- viewing a new, unbudgeted month must not
        # create any rows as a side effect of reading.
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "250.00"})

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        assert response.json() == []

        source = await client.get("/budgets", params={"month": 6, "year": 2026})
        assert source.json()[0]["budget_amount"] == "250.00"

    async def test_plain_partner_forbidden(self, client, session, unique_email):
        """Budgets are owner-or-co-owner only, same gate as Wallets/Recurring
        Bills -- a plain (non-co-owner) partner never reaches list_budgets at
        all, regardless of sharing."""
        owner = await _authed_client(client, session, unique_email)
        category = await _make_category(session, owner)
        await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )

        partner = User(
            email=f"partner-{unique_email}",
            password_hash=hash_password(VALID_PASSWORD),
            display_name="Partner User",
            role=UserRole.PARTNER,
            invited_by_user_id=owner.id,
            email_verified_at=utcnow(),
        )
        session.add(partner)
        await session.commit()
        await _login(client, partner.email)

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 403

    async def test_co_owner_sees_own_private_budget_but_not_owners(self, client, session, unique_email):
        """Each household member's private budget target is invisible to
        everyone else, including the owner -- see item_visibility.py."""
        owner = await _authed_client(client, session, unique_email)
        category = await _make_category(session, owner, name="Groceries")
        await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )

        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        await _login(client, co_owner.email)
        await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "150.00"}
        )

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        amounts = {b["budget_amount"] for b in response.json()}
        assert amounts == {"150.00"}

    async def test_co_owner_sees_shared_budget_created_by_owner(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        category = await _make_category(session, owner, name="Rent")
        created = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "1500.00"}
        )
        budget_id = created.json()["id"]
        await client.patch(f"/budgets/{budget_id}/sharing", json={"is_shared": True})

        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        await _login(client, co_owner.email)

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        amounts = {b["budget_amount"] for b in response.json()}
        assert amounts == {"1500.00"}

class TestUpdateBudget:
    async def test_updates_amount(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        budget_id = create_response.json()["id"]

        response = await client.patch(f"/budgets/{budget_id}", json={"budget_amount": "450.00"})
        assert response.status_code == 200
        assert response.json()["budget_amount"] == "450.00"

    async def test_404_for_other_users_budget(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_category = await _make_category(session, other_user)
        from app.models.budget import Budget

        other_budget = Budget(user_id=other_user.id, category_id=other_category.id, month=7, year=2026, budget_amount="100.00")
        session.add(other_budget)
        await session.commit()
        await session.refresh(other_budget)

        response = await client.patch(f"/budgets/{other_budget.id}", json={"budget_amount": "1.00"})
        assert response.status_code == 404


class TestDeleteBudget:
    async def test_deletes_budget(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        budget_id = create_response.json()["id"]

        response = await client.delete(f"/budgets/{budget_id}")
        assert response.status_code == 204

        listing = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert listing.json() == []

    async def test_404_for_other_users_budget(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_category = await _make_category(session, other_user)
        from app.models.budget import Budget

        other_budget = Budget(user_id=other_user.id, category_id=other_category.id, month=7, year=2026, budget_amount="100.00")
        session.add(other_budget)
        await session.commit()
        await session.refresh(other_budget)
        response = await client.delete(f"/budgets/{other_budget.id}")
        assert response.status_code == 404


class TestUpdateBudgetSharing:
    """Only the creator can toggle a budget's own sharing state -- a co-owner
    flipping something they didn't create from Shared to Private silently
    disappears it for whoever relied on seeing it, with no warning to either
    side. Restricting the action to the creator means the only person who can
    ever cause that surprise is the person who made the choice to hide their
    own item."""

    async def test_owner_can_toggle_own_created_budget(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        category = await _make_category(session, owner)
        budget = await _make_budget(session, owner, category, created_by_user_id=None, is_shared=True)

        response = await client.patch(f"/budgets/{budget.id}/sharing", json={"is_shared": False})
        assert response.status_code == 200
        assert response.json()["is_shared"] is False

    async def test_co_owner_can_toggle_own_created_budget(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-{unique_email}")
        category = await _make_category(session, owner)
        budget = await _make_budget(session, owner, category, created_by_user_id=co_owner.id, is_shared=True)
        await _login(client, co_owner.email)

        response = await client.patch(f"/budgets/{budget.id}/sharing", json={"is_shared": False})
        assert response.status_code == 200

    async def test_co_owner_cannot_toggle_owner_created_budget(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-{unique_email}")
        category = await _make_category(session, owner)
        budget = await _make_budget(session, owner, category, created_by_user_id=None, is_shared=True)
        await _login(client, co_owner.email)

        response = await client.patch(f"/budgets/{budget.id}/sharing", json={"is_shared": False})
        assert response.status_code == 403

    async def test_owner_cannot_toggle_co_owner_created_budget(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-{unique_email}")
        category = await _make_category(session, owner)
        budget = await _make_budget(session, owner, category, created_by_user_id=co_owner.id, is_shared=True)

        response = await client.patch(f"/budgets/{budget.id}/sharing", json={"is_shared": False})
        assert response.status_code == 403
