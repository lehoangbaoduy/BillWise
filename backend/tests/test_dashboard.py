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


async def _make_payment_method(session, user, name="Cash Wallet", type_=PaymentMethodType.CASH, current_balance=None):
    pm = PaymentMethod(user_id=user.id, name=name, type=type_, current_balance=current_balance)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Grocery"):
    category = Category(user_id=user.id, name=name, category_type=category_type)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _create_transaction(client, pm_id, category_id, amount, date, transaction_type="Expense", merchant="Costco"):
    response = await client.post(
        "/transactions",
        json={
            "payment_method_id": str(pm_id),
            "date": date,
            "merchant": merchant,
            "total_amount": amount,
            "transaction_type": transaction_type,
            "line_items": [{"category_id": str(category_id), "item_name": "item", "amount": amount}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestMonthlyOverview:
    async def test_requires_authentication(self, client):
        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert response.status_code == 401

    async def test_computes_totals_and_net_cash_flow(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        expense_category = await _make_category(session, user, name="Grocery")
        income_category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Salary")

        await _create_transaction(client, pm.id, expense_category.id, "60.00", "2026-07-05")
        await _create_transaction(client, pm.id, income_category.id, "1000.00", "2026-07-01", transaction_type="Income")

        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        body = response.json()
        assert body["total_income"] == "1000.00"
        assert body["total_expenses"] == "60.00"
        assert body["net_cash_flow"] == "940.00"

    async def test_top_category_and_top_payment_method(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        cash = await _make_payment_method(session, user, name="Cash")
        card = await _make_payment_method(session, user, name="Visa", type_=PaymentMethodType.CREDIT_CARD)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")

        await _create_transaction(client, cash.id, grocery.id, "30.00", "2026-07-01")
        await _create_transaction(client, card.id, shopping.id, "90.00", "2026-07-02")

        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        body = response.json()
        assert body["top_category"]["name"] == "Shopping"
        assert body["top_category"]["amount"] == "90.00"
        assert body["top_payment_method"]["name"] == "Visa"
        assert body["top_payment_method"]["amount"] == "90.00"

    async def test_no_data_returns_nulls_and_zeros(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        body = response.json()
        assert body["total_income"] == "0"
        assert body["total_expenses"] == "0"
        assert body["top_category"] is None
        assert body["top_payment_method"] is None
        assert body["budget_status"] == []

    async def test_budget_status_reflects_actual_spend(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user, name="Grocery")
        await client.post("/budgets", json={"category_id": str(category.id), "month": 7, "year": 2026, "budget_amount": "100.00"})
        await _create_transaction(client, pm.id, category.id, "120.00", "2026-07-05")

        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        body = response.json()
        assert len(body["budget_status"]) == 1
        status_item = body["budget_status"][0]
        assert status_item["budget_amount"] == "100.00"
        assert status_item["actual_amount"] == "120.00"
        assert status_item["is_over_budget"] is True
        assert status_item["percentage_used"] == "120.00"

    async def test_comparison_vs_previous_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_transaction(client, pm.id, category.id, "50.00", "2026-06-10")
        await _create_transaction(client, pm.id, category.id, "75.00", "2026-07-10")

        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        comparison = response.json()["comparison_vs_previous_month"]
        assert comparison["previous_month"] == 6
        assert comparison["previous_year"] == 2026
        assert comparison["previous_total_expenses"] == "50.00"
        assert comparison["change_amount"] == "25.00"

    async def test_comparison_handles_january_year_boundary(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/dashboard/monthly", params={"month": 1, "year": 2026})
        comparison = response.json()["comparison_vs_previous_month"]
        assert comparison["previous_month"] == 12
        assert comparison["previous_year"] == 2025

    async def test_only_includes_own_transactions(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_transaction(client, pm.id, category.id, "40.00", "2026-07-01")

        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_pm = await _make_payment_method(session, other_user, name="Other Cash")
        other_category = await _make_category(session, other_user)
        other_pm_id, other_category_id = other_pm.id, other_category.id

        await _login(client, unique_email)
        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert response.json()["total_expenses"] == "40.00"

    async def test_does_not_leak_other_users_spend_into_totals_or_top_entries(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_user = await _create_verified_owner(session, f"other-{unique_email}")
        other_pm = await _make_payment_method(session, other_user, name="Other User Cash")
        other_category = await _make_category(session, other_user, name="Other User Category")
        await _login(client, f"other-{unique_email}")
        await _create_transaction(client, other_pm.id, other_category.id, "999.00", "2026-07-01")

        await _login(client, unique_email)
        response = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        body = response.json()
        assert body["total_expenses"] == "0"
        assert body["top_category"] is None
        assert body["top_payment_method"] is None

        breakdown = await client.get("/dashboard/payment-method-breakdown", params={"month": 7, "year": 2026})
        assert breakdown.json() == []


class TestYearlyOverview:
    async def test_spend_by_month_and_highest_lowest(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_transaction(client, pm.id, category.id, "100.00", "2026-01-15")
        await _create_transaction(client, pm.id, category.id, "300.00", "2026-03-15")

        response = await client.get("/dashboard/yearly", params={"year": 2026})
        assert response.status_code == 200
        body = response.json()
        assert len(body["spend_by_month"]) == 12
        assert body["total_yearly_spending"] == "400.00"
        assert body["highest_month"]["month"] == 3
        assert body["highest_month"]["total"] == "300.00"
        assert body["lowest_month"]["total"] == "0"

    async def test_ytd_savings_total(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _create_transaction(client, pm.id, category.id, "50.00", "2026-02-01", transaction_type="Saving expense")

        response = await client.get("/dashboard/yearly", params={"year": 2026})
        assert response.json()["ytd_savings_total"] == "50.00"


class TestCategoryBreakdown:
    async def test_percentage_and_budget_comparison(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")
        await client.post("/budgets", json={"category_id": str(grocery.id), "month": 7, "year": 2026, "budget_amount": "50.00"})
        await _create_transaction(client, pm.id, grocery.id, "75.00", "2026-07-01")
        await _create_transaction(client, pm.id, shopping.id, "25.00", "2026-07-02")

        response = await client.get("/dashboard/category-breakdown", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        by_name = {item["name"]: item for item in response.json()}
        assert by_name["Grocery"]["amount"] == "75.00"
        assert by_name["Grocery"]["percentage_of_total"] == "75.00"
        assert by_name["Grocery"]["is_over_budget"] is True
        assert by_name["Shopping"]["budget_amount"] is None
        assert by_name["Shopping"]["is_over_budget"] is False

    async def test_includes_budgeted_categories_with_zero_spend(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        entertainment = await _make_category(session, user, name="Entertainment")
        await client.post(
            "/budgets", json={"category_id": str(entertainment.id), "month": 7, "year": 2026, "budget_amount": "80.00"}
        )

        response = await client.get("/dashboard/category-breakdown", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["name"] == "Entertainment"
        assert items[0]["amount"] == "0"
        assert items[0]["budget_amount"] == "80.00"
        assert items[0]["is_over_budget"] is False

    async def test_rolls_over_budget_for_consistency_with_budgets_endpoint(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        await client.post("/budgets", json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "150.00"})

        response = await client.get("/dashboard/category-breakdown", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["budget_amount"] == "150.00"

        budgets_response = await client.get("/budgets", params={"month": 7, "year": 2026})
        assert budgets_response.json()[0]["budget_amount"] == "150.00"


class TestPaymentMethodBreakdown:
    async def test_amount_count_and_average(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user, name="Cash", current_balance="200.00")
        category = await _make_category(session, user)
        await _create_transaction(client, pm.id, category.id, "30.00", "2026-07-01")
        await _create_transaction(client, pm.id, category.id, "70.00", "2026-07-02")

        response = await client.get("/dashboard/payment-method-breakdown", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["amount"] == "100.00"
        assert items[0]["transaction_count"] == 2
        assert items[0]["average_transaction"] == "50.00"
        assert items[0]["current_balance"] == "200.00"

    async def test_excludes_methods_with_no_expenses_in_period(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        await _make_payment_method(session, user, name="Unused")

        response = await client.get("/dashboard/payment-method-breakdown", params={"month": 7, "year": 2026})
        assert response.json() == []


class TestCashFlow:
    async def test_income_expenses_and_net(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        expense_category = await _make_category(session, user)
        income_category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Salary")
        await _create_transaction(client, pm.id, expense_category.id, "40.00", "2026-07-01")
        await _create_transaction(client, pm.id, income_category.id, "500.00", "2026-07-01", transaction_type="Income")

        response = await client.get("/dashboard/cash-flow", params={"month": 7, "year": 2026})
        assert response.status_code == 200
        body = response.json()
        assert body["income"] == "500.00"
        assert body["expenses"] == "40.00"
        assert body["net"] == "460.00"
