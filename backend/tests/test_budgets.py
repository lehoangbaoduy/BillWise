import asyncio

from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession as RawAsyncSession

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.user import User, UserRole
from app.services.budget_rollover import ensure_budget_rollover
from tests.conftest import async_engine

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

    async def test_rolls_over_from_most_recent_earlier_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "250.00"})

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["budget_amount"] == "250.00"
        assert body[0]["month"] == 7

    async def test_rollover_does_not_affect_source_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "250.00"})

        rolled_over = await client.get("/budgets", params={"month": 7, "year": 2026})
        budget_id = rolled_over.json()[0]["id"]
        await client.patch(f"/budgets/{budget_id}", json={"budget_amount": "400.00"})

        source = await client.get("/budgets", params={"month": 6, "year": 2026})
        assert source.json()[0]["budget_amount"] == "250.00"

    async def test_no_rollover_when_no_earlier_month_exists(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/budgets", params={"month": 1, "year": 2026})
        assert response.status_code == 200
        assert response.json() == []

    async def test_partner_only_sees_budgets_on_shared_categories(self, client, session, unique_email):
        """PRD §21.4: partner budgets view is filtered to shared categories only."""
        owner = await _authed_client(client, session, unique_email)
        shared_category = await _make_category(session, owner, name="Shared Grocery")
        shared_category.is_shared = True
        session.add(shared_category)
        await session.commit()
        private_category = await _make_category(session, owner, name="Private Gambling")

        await client.post(
            "/budgets", json={"category_id": str(shared_category.id), "month": 7, "year": 2026, "budget_amount": "300.00"}
        )
        await client.post(
            "/budgets", json={"category_id": str(private_category.id), "month": 7, "year": 2026, "budget_amount": "999.00"}
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
        assert response.status_code == 200
        amounts = {b["budget_amount"] for b in response.json()}
        assert amounts == {"300.00"}

    async def test_partner_read_does_not_trigger_rollover_under_partner_id(self, client, session, unique_email):
        """ensure_budget_rollover writes rows scoped to user_id — must never run
        as the partner, or it would create owner-domain budget rows misattributed
        to the partner's own id."""
        owner = await _authed_client(client, session, unique_email)
        shared_category = await _make_category(session, owner, name="Shared")
        shared_category.is_shared = True
        session.add(shared_category)
        await session.commit()
        await client.post(
            "/budgets", json={"category_id": str(shared_category.id), "month": 6, "year": 2026, "budget_amount": "150.00"}
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
        assert response.status_code == 200
        assert response.json() == []

        partner_scoped_rows = (await session.exec(select(Budget).where(Budget.user_id == partner.id))).all()
        assert partner_scoped_rows == []


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


class TestBudgetRolloverEdgeCases:
    async def test_rollover_copies_multiple_categories(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")
        await client.post("/budgets", json={"category_id": str(grocery.id), "month": 6, "year": 2026, "budget_amount": "250.00"})
        await client.post("/budgets", json={"category_id": str(shopping.id), "month": 6, "year": 2026, "budget_amount": "100.00"})

        response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        amounts_by_category = {b["category_id"]: b["budget_amount"] for b in response.json()}
        assert amounts_by_category == {str(grocery.id): "250.00", str(shopping.id): "100.00"}

    async def test_rollover_across_year_boundary(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 12, "year": 2026, "budget_amount": "275.00"})

        response = await client.get("/budgets", params={"month": 1, "year": 2027})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["budget_amount"] == "275.00"
        assert body[0]["month"] == 1
        assert body[0]["year"] == 2027

    async def test_rollover_is_safe_under_concurrent_callers(self, unique_email):
        """Regression test for a real bug caught via Playwright: the Budgets frontend
        fires GET /budgets and GET /dashboard/category-breakdown in parallel for the
        same period, and both call ensure_budget_rollover. Each gets its own DB
        connection/session in production (unlike this suite's other tests, which share
        one connection via the `session` fixture and so can't reproduce a real
        cross-connection race), so two callers can both pass the "no rows yet" check
        before either commits, then race to INSERT the same rolled-over row and hit
        the unique constraint. This test uses genuinely independent, really-committed
        connections/sessions (bypassing the shared-session fixture entirely, with
        manual cleanup) to reproduce that race and assert it no longer raises."""
        setup_conn = await async_engine.connect()
        setup_session = RawAsyncSession(bind=setup_conn, expire_on_commit=False)
        user = User(
            email=unique_email,
            password_hash=hash_password(VALID_PASSWORD),
            display_name="Concurrency Tester",
            role=UserRole.OWNER,
            email_verified_at=utcnow(),
        )
        setup_session.add(user)
        await setup_session.flush()
        category = Category(user_id=user.id, name="Concurrent Rollover", category_type=CategoryType.EXPENSE)
        setup_session.add(category)
        await setup_session.flush()
        setup_session.add(Budget(user_id=user.id, category_id=category.id, month=6, year=2026, budget_amount="250.00"))
        await setup_session.commit()

        try:
            async with async_engine.connect() as conn_a, async_engine.connect() as conn_b:
                session_a = RawAsyncSession(bind=conn_a, expire_on_commit=False)
                session_b = RawAsyncSession(bind=conn_b, expire_on_commit=False)
                try:
                    await asyncio.gather(
                        ensure_budget_rollover(session_a, user, 7, 2026),
                        ensure_budget_rollover(session_b, user, 7, 2026),
                    )
                finally:
                    await session_a.close()
                    await session_b.close()

            rolled_over = (
                await setup_session.exec(
                    select(Budget).where(Budget.user_id == user.id, Budget.month == 7, Budget.year == 2026)
                )
            ).all()
            assert len(rolled_over) == 1
            assert rolled_over[0].budget_amount == 250
        finally:
            await setup_session.exec(delete(Budget).where(Budget.user_id == user.id))
            await setup_session.exec(delete(Category).where(Category.user_id == user.id))
            await setup_session.exec(delete(User).where(User.id == user.id))
            await setup_session.commit()
            await setup_session.close()
            await setup_conn.close()
