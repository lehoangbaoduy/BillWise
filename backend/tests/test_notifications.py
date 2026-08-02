from datetime import date, timedelta
from decimal import Decimal

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.ai_insight import AIInsight, AIInsightType
from app.models.category import Category, CategoryType
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
    await session.commit()
    await session.refresh(partner)
    return partner


async def _make_payment_method(session, user, name="Cash Wallet", type_=PaymentMethodType.CASH):
    pm = PaymentMethod(user_id=user.id, name=name, type=type_)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, name="Grocery", is_shared=False):
    category = Category(user_id=user.id, name=name, category_type=CategoryType.EXPENSE, is_shared=is_shared)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _create_expense(client, pm_id, category_id, amount, tx_date, merchant="Costco"):
    response = await client.post(
        "/transactions",
        json={
            "payment_method_id": str(pm_id),
            "date": tx_date,
            "merchant": merchant,
            "total_amount": amount,
            "transaction_type": "Expense",
            "line_items": [{"category_id": str(category_id), "item_name": "item", "amount": amount}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_budget(client, category_id, month, year, amount):
    response = await client.post(
        "/budgets", json={"category_id": str(category_id), "month": month, "year": year, "budget_amount": amount}
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestBudgetNotifications:
    async def test_requires_authentication(self, client):
        response = await client.get("/notifications")
        assert response.status_code == 401

    async def test_flags_over_budget_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today()
        await _create_budget(client, category.id, today.month, today.year, "50.00")
        await _create_expense(client, pm.id, category.id, "75.00", today.isoformat())

        response = await client.get("/notifications")
        assert response.status_code == 200
        items = response.json()
        matching = [item for item in items if item["type"] == "budget_exceeded"]
        assert len(matching) == 1
        assert matching[0]["severity"] == "critical"
        assert matching[0]["category_id"] == str(category.id)

    async def test_flags_near_limit_category_without_exceeding(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today()
        await _create_budget(client, category.id, today.month, today.year, "100.00")
        await _create_expense(client, pm.id, category.id, "95.00", today.isoformat())

        response = await client.get("/notifications")
        items = response.json()
        assert any(item["type"] == "budget_near_limit" for item in items)
        assert not any(item["type"] == "budget_exceeded" for item in items)

    async def test_no_notification_when_under_budget(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today()
        await _create_budget(client, category.id, today.month, today.year, "100.00")
        await _create_expense(client, pm.id, category.id, "10.00", today.isoformat())

        response = await client.get("/notifications")
        assert response.json() == []


class TestRecurringBillNotifications:
    async def test_flags_overdue_bill_with_reminders_enabled(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        overdue_date = date.today() - timedelta(days=3)

        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": overdue_date.isoformat(),
                "reminder_enabled": True,
            },
        )
        assert response.status_code == 201, response.text

        response = await client.get("/notifications")
        items = response.json()
        matching = [item for item in items if item["type"] == "recurring_bill_overdue"]
        assert len(matching) == 1
        assert matching[0]["severity"] == "critical"

    async def test_ignores_bill_with_reminders_disabled(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        overdue_date = date.today() - timedelta(days=3)

        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": overdue_date.isoformat(),
                "reminder_enabled": False,
            },
        )
        assert response.status_code == 201, response.text

        response = await client.get("/notifications")
        assert response.json() == []

    async def test_flags_bill_due_soon(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        due_soon_date = date.today() + timedelta(days=2)

        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Rent",
                "amount": "1200.00",
                "frequency": "monthly",
                "due_date": due_soon_date.isoformat(),
                "reminder_enabled": True,
            },
        )
        assert response.status_code == 201, response.text

        response = await client.get("/notifications")
        items = response.json()
        assert any(item["type"] == "recurring_bill_due_soon" for item in items)


class TestGoalNotifications:
    async def test_flags_goal_past_target_date_and_underfunded(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        create_response = await client.post(
            "/goals",
            json={
                "name": "Emergency Fund",
                "target_amount": "1000.00",
                "target_date": (date.today() - timedelta(days=1)).isoformat(),
            },
        )
        assert create_response.status_code == 201, create_response.text

        response = await client.get("/notifications")
        items = response.json()
        matching = [item for item in items if item["type"] == "goal_target_date_passed"]
        assert len(matching) == 1

    async def test_no_notification_when_goal_already_funded(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user, name="Savings")
        create_response = await client.post(
            "/goals",
            json={
                "name": "Emergency Fund",
                "target_amount": "100.00",
                "target_date": (date.today() - timedelta(days=1)).isoformat(),
            },
        )
        goal_id = create_response.json()["id"]

        response = await client.post(
            f"/goals/{goal_id}/add-funds",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "amount": "100.00",
                "date": date.today().isoformat(),
            },
        )
        assert response.status_code == 201, response.text

        response = await client.get("/notifications")
        assert not any(item["type"] == "goal_target_date_passed" for item in response.json())


class TestAIInsightNotifications:
    async def test_flags_undismissed_insight(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        session.add(
            AIInsight(
                user_id=user.id,
                insight_type=AIInsightType.OVER_BUDGET_ALERT,
                message="You're spending more on Grocery than usual.",
                supporting_data={},
                generated_at=utcnow(),
            )
        )
        await session.commit()

        response = await client.get("/notifications")
        items = response.json()
        matching = [item for item in items if item["type"] == "ai_insight"]
        assert len(matching) == 1
        assert matching[0]["message"] == "You're spending more on Grocery than usual."

    async def test_dismissed_insight_excluded(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        session.add(
            AIInsight(
                user_id=user.id,
                insight_type=AIInsightType.OVER_BUDGET_ALERT,
                message="Already handled.",
                supporting_data={},
                generated_at=utcnow(),
                is_dismissed=True,
            )
        )
        await session.commit()

        response = await client.get("/notifications")
        assert not any(item["type"] == "ai_insight" for item in response.json())


class TestPartnerNotificationVisibility:
    """PRD §21.4: partners only see budget/goal alerts for shared categories
    and shared goals; recurring bills and AI insights stay owner-only."""

    async def test_partner_sees_shared_budget_but_not_owner_only_types(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        shared_category = await _make_category(session, owner, name="Shared Grocery", is_shared=True)
        private_category = await _make_category(session, owner, name="Private Hobbies", is_shared=False)
        today = date.today()
        await _create_budget(client, shared_category.id, today.month, today.year, "50.00")
        await _create_budget(client, private_category.id, today.month, today.year, "50.00")
        await _create_expense(client, pm.id, shared_category.id, "75.00", today.isoformat())
        await _create_expense(client, pm.id, private_category.id, "75.00", today.isoformat())

        session.add(
            AIInsight(
                user_id=owner.id,
                insight_type=AIInsightType.OVER_BUDGET_ALERT,
                message="Owner-only insight.",
                supporting_data={},
                generated_at=utcnow(),
            )
        )
        await session.commit()

        bill_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(shared_category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": (today - timedelta(days=3)).isoformat(),
                "reminder_enabled": True,
            },
        )
        assert bill_response.status_code == 201, bill_response.text

        goal_response = await client.post(
            "/goals",
            json={
                "name": "Private Goal",
                "target_amount": "1000.00",
                "target_date": (today - timedelta(days=1)).isoformat(),
            },
        )
        assert goal_response.status_code == 201, goal_response.text
        private_goal_id = goal_response.json()["id"]

        # Sanity check: the owner does see both owner-only notifications, proving
        # their absence for the partner below is due to role scoping, not setup error.
        owner_items = (await client.get("/notifications")).json()
        assert any(item["type"] == "recurring_bill_overdue" for item in owner_items)
        assert any(item["entity_id"] == private_goal_id for item in owner_items)

        partner = await _make_partner(session, owner, unique_email)
        await _login(client, partner.email)

        response = await client.get("/notifications")
        assert response.status_code == 200
        items = response.json()
        assert any(item["category_id"] == str(shared_category.id) for item in items)
        assert not any(item["category_id"] == str(private_category.id) for item in items)
        assert not any(item["type"] == "ai_insight" for item in items)
        assert not any(item["type"] in ("recurring_bill_overdue", "recurring_bill_due_soon") for item in items)
        assert not any(item["entity_id"] == private_goal_id for item in items)
