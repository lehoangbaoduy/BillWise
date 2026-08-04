from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.partner_permission import PartnerPermission
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
    await session.refresh(user)
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


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Saving"):
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


class TestCreateGoal:
    async def test_requires_authentication(self, client):
        response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        assert response.status_code == 401

    async def test_creates_goal_with_zero_current_amount(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Emergency Fund"
        assert body["current_amount"] == "0"
        assert body["is_active"] is True

    async def test_rejects_oversized_icon(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/goals", json={"name": "Emergency Fund", "target_amount": "1000.00", "icon": "x" * 21}
        )
        assert response.status_code == 422


class TestListGoals:
    async def test_only_returns_own_active_goals(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})

        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        session.add(SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00"))
        await session.commit()

        response = await client.get("/goals")
        assert response.status_code == 200
        names = {g["name"] for g in response.json()}
        assert names == {"Emergency Fund"}

    async def test_plain_partner_forbidden(self, client, session, unique_email):
        """Goals are owner-or-co-owner only, same gate as Wallets/Recurring
        Bills/Budgets -- a plain (non-co-owner) partner never reaches
        list_goals at all, regardless of sharing."""
        owner = await _authed_client(client, session, unique_email)
        await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "500.00"})

        partner_email = f"partner-{unique_email}"
        await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
        await _login(client, partner_email)

        response = await client.get("/goals")
        assert response.status_code == 403

    async def test_co_owner_sees_shared_goal_but_not_owners_private_goal(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        await client.post("/goals", json={"name": "Private Goal", "target_amount": "500.00"})
        created = await client.post("/goals", json={"name": "Shared Goal", "target_amount": "1000.00"})
        await client.patch(f"/goals/{created.json()['id']}/sharing", json={"is_shared": True})

        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        await _login(client, co_owner.email)

        response = await client.get("/goals")
        assert response.status_code == 200
        names = {g["name"] for g in response.json()}
        assert names == {"Shared Goal"}

    async def test_owner_does_not_see_co_owners_private_goal(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        await _login(client, co_owner.email)
        await client.post("/goals", json={"name": "Co-Owner's Private Goal", "target_amount": "200.00"})

        await _login(client, owner.email)
        response = await client.get("/goals")
        assert response.status_code == 200
        assert response.json() == []


class TestAddFunds:
    async def test_add_funds_creates_linked_transaction_and_updates_current_amount(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.post(
            f"/goals/{goal_id}/add-funds",
            json={
                "amount": "150.00",
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "date": "2026-07-30",
            },
        )
        assert response.status_code == 201
        assert response.json()["current_amount"] == "150.00"

        second = await client.post(
            f"/goals/{goal_id}/add-funds",
            json={
                "amount": "50.00",
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "date": "2026-07-30",
            },
        )
        assert second.json()["current_amount"] == "200.00"

    async def test_created_transaction_is_linked_and_listed(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        await client.post(
            f"/goals/{goal_id}/add-funds",
            json={"amount": "150.00", "payment_method_id": str(pm.id), "category_id": str(category.id), "date": "2026-07-30"},
        )

        transactions_response = await client.get("/transactions")
        transactions = transactions_response.json()
        assert len(transactions) == 1
        assert transactions[0]["goal_id"] == goal_id
        assert transactions[0]["transaction_type"] == "Saving expense"

    async def test_rejects_invalid_payment_method(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.post(
            f"/goals/{goal_id}/add-funds",
            json={
                "amount": "150.00",
                "payment_method_id": "00000000-0000-0000-0000-000000000000",
                "category_id": str(category.id),
                "date": "2026-07-30",
            },
        )
        assert response.status_code == 422

    async def test_404_for_other_users_goal(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        other_goal = SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00")
        session.add(other_goal)
        await session.commit()
        await session.refresh(other_goal)

        response = await client.post(
            f"/goals/{other_goal.id}/add-funds",
            json={"amount": "50.00", "payment_method_id": str(pm.id), "category_id": str(category.id), "date": "2026-07-30"},
        )
        assert response.status_code == 404


class TestGetGoal:
    async def test_includes_contributing_transactions(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]
        await client.post(
            f"/goals/{goal_id}/add-funds",
            json={"amount": "150.00", "payment_method_id": str(pm.id), "category_id": str(category.id), "date": "2026-07-30"},
        )

        response = await client.get(f"/goals/{goal_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["current_amount"] == "150.00"
        assert len(body["contributing_transactions"]) == 1
        assert body["contributing_transactions"][0]["total_amount"] == "150.00"


class TestUpdateGoal:
    async def test_updates_fields(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.patch(f"/goals/{goal_id}", json={"name": "Rainy Day Fund", "target_amount": "1500.00"})
        assert response.status_code == 200
        assert response.json()["name"] == "Rainy Day Fund"
        assert response.json()["target_amount"] == "1500.00"

    async def test_404_for_other_users_goal(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        other_goal = SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00")
        session.add(other_goal)
        await session.commit()
        await session.refresh(other_goal)

        response = await client.patch(f"/goals/{other_goal.id}", json={"name": "Hijacked"})
        assert response.status_code == 404


class TestGoalSharing:
    async def test_toggles_sharing(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.patch(f"/goals/{goal_id}/sharing", json={"is_shared": True})
        assert response.status_code == 200
        assert response.json()["is_shared"] is True

    async def test_404_for_other_users_goal(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        other_goal = SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00")
        session.add(other_goal)
        await session.commit()
        await session.refresh(other_goal)

        response = await client.patch(f"/goals/{other_goal.id}/sharing", json={"is_shared": True})
        assert response.status_code == 404


class TestDeleteGoal:
    async def test_deactivates_and_unlinks_transactions(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]
        await client.post(
            f"/goals/{goal_id}/add-funds",
            json={"amount": "150.00", "payment_method_id": str(pm.id), "category_id": str(category.id), "date": "2026-07-30"},
        )

        response = await client.delete(f"/goals/{goal_id}")
        assert response.status_code == 204

        get_response = await client.get(f"/goals/{goal_id}")
        assert get_response.status_code == 404

        transactions_response = await client.get("/transactions")
        transactions = transactions_response.json()
        assert len(transactions) == 1
        assert transactions[0]["goal_id"] is None

    async def test_404_for_other_users_goal(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        other_goal = SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00")
        session.add(other_goal)
        await session.commit()
        await session.refresh(other_goal)

        response = await client.delete(f"/goals/{other_goal.id}")
        assert response.status_code == 404


class TestTransactionGoalLinking:
    async def test_rejects_goal_id_on_expense_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user, name="Grocery")
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "goal_id": goal_id,
                "date": "2026-07-30",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_allows_goal_id_on_saving_expense_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        goal_response = await client.post("/goals", json={"name": "Emergency Fund", "target_amount": "1000.00"})
        goal_id = goal_response.json()["id"]

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "goal_id": goal_id,
                "date": "2026-07-30",
                "merchant": "Manual Saving",
                "total_amount": "10.00",
                "transaction_type": "Saving expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 201
        assert response.json()["goal_id"] == goal_id

    async def test_rejects_other_users_goal(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        from app.models.goal import SavingsGoal

        other_goal = SavingsGoal(user_id=other_user.id, name="Other's Goal", target_amount="500.00")
        session.add(other_goal)
        await session.commit()
        await session.refresh(other_goal)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "goal_id": str(other_goal.id),
                "date": "2026-07-30",
                "merchant": "Manual Saving",
                "total_amount": "10.00",
                "transaction_type": "Saving expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422
