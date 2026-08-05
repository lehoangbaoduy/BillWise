from datetime import date, timedelta
from decimal import Decimal

from app.core.security import hash_password
from app.models._common import utcnow
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


class TestDuplicateTransactionNotifications:
    async def test_flags_same_merchant_amount_and_date(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today()
        await _create_expense(client, pm.id, category.id, "42.00", today.isoformat(), merchant="Costco")
        await _create_expense(client, pm.id, category.id, "42.00", today.isoformat(), merchant="Costco")

        response = await client.get("/notifications")
        assert response.status_code == 200
        matching = [item for item in response.json() if item["type"] == "duplicate_transaction"]
        assert len(matching) == 1
        assert matching[0]["severity"] == "warning"
        assert "2 transactions" in matching[0]["message"]

    async def test_no_notification_for_single_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_expense(client, pm.id, category.id, "42.00", date.today().isoformat(), merchant="Costco")

        response = await client.get("/notifications")
        assert not any(item["type"] == "duplicate_transaction" for item in response.json())

    async def test_different_merchant_not_flagged_as_duplicate(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today().isoformat()
        await _create_expense(client, pm.id, category.id, "42.00", today, merchant="Costco")
        await _create_expense(client, pm.id, category.id, "42.00", today, merchant="Target")

        response = await client.get("/notifications")
        assert not any(item["type"] == "duplicate_transaction" for item in response.json())

    async def test_outside_window_not_flagged(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        old_date = (date.today() - timedelta(days=30)).isoformat()
        await _create_expense(client, pm.id, category.id, "42.00", old_date, merchant="Costco")
        await _create_expense(client, pm.id, category.id, "42.00", old_date, merchant="Costco")

        response = await client.get("/notifications")
        assert not any(item["type"] == "duplicate_transaction" for item in response.json())

    async def test_different_payment_method_not_flagged_as_duplicate(self, client, session, unique_email):
        # Matches detect_duplicate's stricter signature (transaction_validation.py):
        # merchant + date + amount + payment method must all match, not just
        # merchant + date + amount — paying the same amount to the same
        # merchant on the same day with two different cards is not unusual.
        user = await _authed_client(client, session, unique_email)
        cash = await _make_payment_method(session, user, name="Cash", type_=PaymentMethodType.CASH)
        card = await _make_payment_method(session, user, name="Visa", type_=PaymentMethodType.CREDIT_CARD)
        category = await _make_category(session, user)
        today = date.today().isoformat()
        await _create_expense(client, cash.id, category.id, "42.00", today, merchant="Costco")
        await _create_expense(client, card.id, category.id, "42.00", today, merchant="Costco")

        response = await client.get("/notifications")
        assert not any(item["type"] == "duplicate_transaction" for item in response.json())


async def _create_reimbursement(client, pm_id, category_id, tx_date, amount="45.50"):
    response = await client.post(
        "/transactions",
        json={
            "payment_method_id": str(pm_id),
            "date": tx_date,
            "merchant": "Costco",
            "total_amount": amount,
            "transaction_type": "Reimbursement",
            "line_items": [{"category_id": str(category_id), "item_name": "Team lunch", "amount": amount}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestReimbursementNotifications:
    async def test_flags_unpaid_reimbursement_from_a_closed_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        prior_month_date = (date.today().replace(day=1) - timedelta(days=1)).isoformat()
        await _create_reimbursement(client, pm.id, category.id, prior_month_date)

        response = await client.get("/notifications")
        matching = [item for item in response.json() if item["type"] == "reimbursement_unpaid"]
        assert len(matching) == 1
        assert matching[0]["severity"] == "warning"

    async def test_no_notification_for_reimbursement_from_current_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_reimbursement(client, pm.id, category.id, date.today().isoformat())

        response = await client.get("/notifications")
        assert not any(item["type"] == "reimbursement_unpaid" for item in response.json())

    async def test_no_notification_once_marked_paid(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        prior_month_date = (date.today().replace(day=1) - timedelta(days=1)).isoformat()
        transaction = await _create_reimbursement(client, pm.id, category.id, prior_month_date)
        await client.post(f"/transactions/{transaction['id']}/mark-reimbursement-paid", json={"paid_by": "Alex"})

        response = await client.get("/notifications")
        assert not any(item["type"] == "reimbursement_unpaid" for item in response.json())


class TestPartnerNotificationVisibility:
    """PRD §21.4: partners only see budget/goal alerts for shared categories
    and shared goals; recurring bills stay owner-only."""

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
        await _create_expense(client, pm.id, private_category.id, "75.00", today.isoformat())

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
        assert any(item["type"] == "duplicate_transaction" for item in owner_items)

        partner = await _make_partner(session, owner, unique_email)
        await _login(client, partner.email)

        response = await client.get("/notifications")
        assert response.status_code == 200
        items = response.json()
        assert any(item["category_id"] == str(shared_category.id) for item in items)
        assert not any(item["category_id"] == str(private_category.id) for item in items)
        assert not any(item["type"] in ("recurring_bill_overdue", "recurring_bill_due_soon") for item in items)
        assert not any(item["entity_id"] == private_goal_id for item in items)
        assert not any(item["type"] == "duplicate_transaction" for item in items)


class TestTransactionShareNotifications:
    async def test_recipient_sees_pending_share_notification(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        create = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": date.today().isoformat(),
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        assert create.status_code == 201, create.text
        transaction_id = create.json()["id"]
        share_id = create.json()["shares"][0]["id"]

        await _login(client, partner.email)
        response = await client.get("/notifications")
        items = response.json()
        matching = [item for item in items if item["type"] == "transaction_share_pending"]
        assert len(matching) == 1
        assert matching[0]["severity"] == "warning"

        await _login(client, unique_email)
        await client.post(
            f"/transactions/{transaction_id}/shares/{share_id}/settle", json={"settled_by": "Partner User"}
        )

        await _login(client, partner.email)
        response = await client.get("/notifications")
        items = response.json()
        assert not any(item["type"] == "transaction_share_pending" for item in items)
