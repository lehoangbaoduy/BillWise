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


async def _login(client, email):
    return await client.post("/auth/login", json={"email": email, "password": VALID_PASSWORD})


async def _authed_client(client, session, unique_email):
    user = await _create_verified_owner(session, unique_email)
    await _login(client, unique_email)
    return user


async def _make_payment_method(session, user, type_=PaymentMethodType.CASH):
    pm = PaymentMethod(user_id=user.id, name="Cash Wallet", type=type_)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Grocery", is_shared=False):
    category = Category(user_id=user.id, name=name, category_type=category_type, is_shared=is_shared)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


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


async def _make_partner(session, owner, unique_email, can_add_transactions=False):
    partner_email = f"partner-{unique_email}"
    partner = await _create_verified_user(session, partner_email, role=UserRole.PARTNER, invited_by_user_id=owner.id)
    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=can_add_transactions))
    await session.commit()
    return partner, partner_email


class TestCreateTransaction:
    async def test_requires_authentication(self, client):
        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": "00000000-0000-0000-0000-000000000000",
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": "00000000-0000-0000-0000-000000000000", "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 401

    async def test_creates_single_line_item_expense(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "45.50",
                "transaction_type": "Expense",
                "line_items": [
                    {"category_id": str(category.id), "item_name": "Groceries", "amount": "45.50"},
                ],
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["merchant"] == "Costco"
        assert body["total_amount"] == "45.50"
        assert len(body["line_items"]) == 1
        assert body["possible_duplicate"] is False
        assert body["source"] == "Manual"

    async def test_creates_multi_category_split_receipt(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "100.00",
                "transaction_type": "Expense",
                "line_items": [
                    {"category_id": str(grocery.id), "item_name": "Food", "amount": "60.00"},
                    {"category_id": str(shopping.id), "item_name": "Household", "amount": "40.00"},
                ],
            },
        )
        assert response.status_code == 201
        assert len(response.json()["line_items"]) == 2

    async def test_rejects_line_item_sum_mismatch(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "45.50"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_negative_amount_for_expense(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "-10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "-10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_allows_negative_amount_for_adjustment(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Correction",
                "total_amount": "-10.00",
                "transaction_type": "Adjustment",
                "line_items": [{"category_id": str(category.id), "item_name": "Correction", "amount": "-10.00"}],
            },
        )
        assert response.status_code == 201

    async def test_rejects_income_category_on_expense_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        income_category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Paycheck")

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(income_category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_other_users_payment_method(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        other_pm = await _make_payment_method(session, other_user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(other_pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_other_users_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        other_category = await _make_category(session, other_user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(other_category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_inactive_payment_method(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await client.delete(f"/payment-methods/{pm.id}")

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_inactive_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await client.delete(f"/categories/{category.id}")

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_accepts_explicit_quantity(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "15.00",
                "transaction_type": "Expense",
                "line_items": [
                    {"category_id": str(category.id), "item_name": "Apples", "amount": "15.00", "quantity": "3"}
                ],
            },
        )
        assert response.status_code == 201
        assert response.json()["line_items"][0]["quantity"] == "3"

    async def test_rejects_forbidden_extra_field(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_rejects_oversized_notes(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "notes": "x" * 1001,
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_flags_possible_duplicate_non_blocking(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        payload = {
            "payment_method_id": str(pm.id),
            "date": "2026-07-01",
            "merchant": "Costco",
            "total_amount": "10.00",
            "transaction_type": "Expense",
            "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
        }

        first = await client.post("/transactions", json=payload)
        assert first.json()["possible_duplicate"] is False

        second = await client.post("/transactions", json=payload)
        assert second.status_code == 201
        assert second.json()["possible_duplicate"] is True


class TestListTransactions:
    async def test_only_returns_own_transactions(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        other_pm = await _make_payment_method(session, other_user)
        other_category = await _make_category(session, other_user)
        from app.models.transaction import Transaction, TransactionSource, TransactionType

        other_txn = Transaction(
            user_id=other_user.id,
            payment_method_id=other_pm.id,
            date="2026-07-01",
            merchant="Other's Purchase",
            total_amount="5.00",
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
        )
        session.add(other_txn)
        await session.commit()

        response = await client.get("/transactions")
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Costco"}

    async def test_filters_by_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        for date in ("2026-06-15", "2026-07-15"):
            await client.post(
                "/transactions",
                json={
                    "payment_method_id": str(pm.id),
                    "date": date,
                    "merchant": f"Purchase-{date}",
                    "total_amount": "10.00",
                    "transaction_type": "Expense",
                    "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
                },
            )

        response = await client.get("/transactions", params={"month": "2026-07"})
        assert response.status_code == 200
        dates = {t["date"] for t in response.json()}
        assert dates == {"2026-07-15"}

    async def test_filters_by_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Grocery Run",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(grocery.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Mall Trip",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(shopping.id), "item_name": "x", "amount": "10.00"}],
            },
        )

        response = await client.get("/transactions", params={"category_id": str(grocery.id)})
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Grocery Run"}

    async def test_filters_by_amount_range(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        for amount in ("5.00", "50.00", "500.00"):
            await client.post(
                "/transactions",
                json={
                    "payment_method_id": str(pm.id),
                    "date": "2026-07-01",
                    "merchant": f"Purchase-{amount}",
                    "total_amount": amount,
                    "transaction_type": "Expense",
                    "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": amount}],
                },
            )

        response = await client.get("/transactions", params={"amount_min": "10.00", "amount_max": "100.00"})
        assert response.status_code == 200
        amounts = {t["total_amount"] for t in response.json()}
        assert amounts == {"50.00"}

    async def test_filters_by_multiple_transaction_types(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        income_category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Salary")

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id), "date": "2026-07-01", "merchant": "Groceries",
                "total_amount": "10.00", "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id), "date": "2026-07-01", "merchant": "Paycheck",
                "total_amount": "1000.00", "transaction_type": "Income",
                "line_items": [{"category_id": str(income_category.id), "item_name": "x", "amount": "1000.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id), "date": "2026-07-01", "merchant": "Team lunch",
                "total_amount": "20.00", "transaction_type": "Reimbursement",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "20.00"}],
            },
        )

        response = await client.get(
            "/transactions", params=[("transaction_type", "Expense"), ("transaction_type", "Reimbursement")]
        )
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Groceries", "Team lunch"}

    async def test_type_filter_composes_with_category_filter(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        grocery = await _make_category(session, user, name="Grocery")
        shopping = await _make_category(session, user, name="Shopping")

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id), "date": "2026-07-01", "merchant": "Grocery Run",
                "total_amount": "10.00", "transaction_type": "Expense",
                "line_items": [{"category_id": str(grocery.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id), "date": "2026-07-01", "merchant": "Mall Trip",
                "total_amount": "10.00", "transaction_type": "Expense",
                "line_items": [{"category_id": str(shopping.id), "item_name": "x", "amount": "10.00"}],
            },
        )

        response = await client.get(
            "/transactions", params=[("category_id", str(grocery.id)), ("transaction_type", "Expense")]
        )
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Grocery Run"}

    async def test_search_matches_merchant(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco Wholesale",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Target",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )

        response = await client.get("/transactions", params={"search": "costco"})
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Costco Wholesale"}

    async def test_partner_only_sees_transactions_fully_in_shared_categories(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        shared_category = await _make_category(session, owner, name="Shared Cat", is_shared=True)
        private_category = await _make_category(session, owner, name="Private Cat", is_shared=False)

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Shared Purchase",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(shared_category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Private Purchase",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(private_category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Mixed Purchase",
                "total_amount": "20.00",
                "transaction_type": "Expense",
                "line_items": [
                    {"category_id": str(shared_category.id), "item_name": "x", "amount": "10.00"},
                    {"category_id": str(private_category.id), "item_name": "y", "amount": "10.00"},
                ],
            },
        )

        _, partner_email = await _make_partner(session, owner, unique_email)
        await _login(client, partner_email)

        response = await client.get("/transactions")
        assert response.status_code == 200
        merchants = {t["merchant"] for t in response.json()}
        assert merchants == {"Shared Purchase"}


class TestPartnerCreateTransaction:
    async def test_partner_without_permission_is_forbidden(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner, is_shared=True)
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=False)
        await _login(client, partner_email)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 403

    async def test_partner_with_permission_creates_transaction_attributed_to_them(
        self, client, session, unique_email
    ):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner, is_shared=True)
        partner, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["created_by_user_id"] == str(partner.id)

        from app.models.transaction import Transaction

        stored = await session.get(Transaction, body["id"])
        assert stored.user_id == owner.id
        assert stored.created_by_user_id == partner.id

    async def test_partner_cannot_use_unshared_category(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        private_category = await _make_category(session, owner, is_shared=False)
        _, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(private_category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422

    async def test_revoked_partner_transaction_survives_with_attribution_intact(
        self, client, session, unique_email
    ):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner, is_shared=True)
        partner, partner_email = await _make_partner(session, owner, unique_email, can_add_transactions=True)
        await _login(client, partner_email)

        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        transaction_id = create_response.json()["id"]

        partner.is_active = False
        session.add(partner)
        await session.commit()

        await _login(client, unique_email)
        response = await client.get("/transactions")
        assert response.status_code == 200
        matching = [t for t in response.json() if t["id"] == transaction_id]
        assert len(matching) == 1
        assert matching[0]["created_by_user_id"] == str(partner.id)


class TestGetTransaction:
    async def test_404_for_other_users_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        other_pm = await _make_payment_method(session, other_user)
        from app.models.transaction import Transaction, TransactionSource, TransactionType

        other_txn = Transaction(
            user_id=other_user.id,
            payment_method_id=other_pm.id,
            date="2026-07-01",
            merchant="Other's Purchase",
            total_amount="5.00",
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
        )
        session.add(other_txn)
        await session.commit()
        await session.refresh(other_txn)

        response = await client.get(f"/transactions/{other_txn.id}")
        assert response.status_code == 404


class TestUpdateTransaction:
    async def test_updates_top_level_fields(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        response = await client.patch(f"/transactions/{txn_id}", json={"merchant": "Costco Wholesale", "notes": "bulk buy"})
        assert response.status_code == 200
        body = response.json()
        assert body["merchant"] == "Costco Wholesale"
        assert body["notes"] == "bulk buy"

    async def test_replacing_line_items_revalidates_sum(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        response = await client.patch(
            f"/transactions/{txn_id}",
            json={"line_items": [{"category_id": str(category.id), "item_name": "y", "amount": "5.00"}]},
        )
        assert response.status_code == 422

    async def test_replacing_line_items_with_matching_sum_succeeds(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        response = await client.patch(
            f"/transactions/{txn_id}",
            json={"line_items": [{"category_id": str(category.id), "item_name": "y", "amount": "10.00"}]},
        )
        assert response.status_code == 200
        assert response.json()["line_items"][0]["item_name"] == "y"

    async def test_updating_total_amount_alone_revalidates_against_existing_line_items(
        self, client, session, unique_email
    ):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        mismatched = await client.patch(f"/transactions/{txn_id}", json={"total_amount": "20.00"})
        assert mismatched.status_code == 422

        unchanged = await client.get(f"/transactions/{txn_id}")
        assert unchanged.json()["total_amount"] == "10.00"

    async def test_updating_transaction_type_alone_revalidates_amount_sign(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Correction",
                "total_amount": "-10.00",
                "transaction_type": "Adjustment",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "-10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        response = await client.patch(f"/transactions/{txn_id}", json={"transaction_type": "Expense"})
        assert response.status_code == 422


class TestDeleteTransaction:
    async def test_deletes_transaction_and_line_items(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "x", "amount": "10.00"}],
            },
        )
        txn_id = create_response.json()["id"]

        from sqlmodel import select as sqlmodel_select

        from app.models.transaction import TransactionLineItem

        line_items_before = (
            await session.exec(
                sqlmodel_select(TransactionLineItem).where(TransactionLineItem.transaction_id == txn_id)
            )
        ).all()
        assert len(line_items_before) == 1

        response = await client.delete(f"/transactions/{txn_id}")
        assert response.status_code == 204

        get_response = await client.get(f"/transactions/{txn_id}")
        assert get_response.status_code == 404

        line_items_after = (
            await session.exec(
                sqlmodel_select(TransactionLineItem).where(TransactionLineItem.transaction_id == txn_id)
            )
        ).all()
        assert line_items_after == []

    async def test_404_deleting_other_users_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)

        other_email = f"other-{unique_email}"
        other_user = await _create_verified_owner(session, other_email)
        other_pm = await _make_payment_method(session, other_user)
        from app.models.transaction import Transaction, TransactionSource, TransactionType

        other_txn = Transaction(
            user_id=other_user.id,
            payment_method_id=other_pm.id,
            date="2026-07-01",
            merchant="Other's Purchase",
            total_amount="5.00",
            transaction_type=TransactionType.EXPENSE,
            source=TransactionSource.MANUAL,
        )
        session.add(other_txn)
        await session.commit()
        await session.refresh(other_txn)

        response = await client.delete(f"/transactions/{other_txn.id}")
        assert response.status_code == 404


class TestReimbursementTransactions:
    async def _create_reimbursement(self, client, pm_id, category_id, amount="45.50", tx_date="2026-07-01"):
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

    async def test_creates_reimbursement_transaction_defaults_to_unpaid(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        body = await self._create_reimbursement(client, pm.id, category.id)
        assert body["transaction_type"] == "Reimbursement"
        assert body["reimbursement_status"] == "unpaid"
        assert body["reimbursement_paid_by"] is None
        assert body["reimbursement_paid_at"] is None

    async def test_mark_paid_requires_non_empty_paid_by_and_is_one_way(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        transaction_id = (await self._create_reimbursement(client, pm.id, category.id))["id"]

        empty = await client.post(f"/transactions/{transaction_id}/mark-reimbursement-paid", json={"paid_by": ""})
        assert empty.status_code == 422

        mark_paid = await client.post(f"/transactions/{transaction_id}/mark-reimbursement-paid", json={"paid_by": "Alex"})
        assert mark_paid.status_code == 200
        body = mark_paid.json()
        assert body["reimbursement_status"] == "paid"
        assert body["reimbursement_paid_by"] == "Alex"
        assert body["reimbursement_paid_at"] is not None

        already_paid = await client.post(
            f"/transactions/{transaction_id}/mark-reimbursement-paid", json={"paid_by": "Sam"}
        )
        assert already_paid.status_code == 422

    async def test_mark_paid_rejects_non_reimbursement_transaction(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "45.50",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "45.50"}],
            },
        )
        transaction_id = response.json()["id"]

        mark_paid = await client.post(
            f"/transactions/{transaction_id}/mark-reimbursement-paid", json={"paid_by": "Alex"}
        )
        assert mark_paid.status_code == 422

    async def test_editing_type_away_from_reimbursement_clears_payment_fields(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        transaction_id = (await self._create_reimbursement(client, pm.id, category.id))["id"]
        await client.post(f"/transactions/{transaction_id}/mark-reimbursement-paid", json={"paid_by": "Alex"})

        response = await client.patch(f"/transactions/{transaction_id}", json={"transaction_type": "Expense"})
        assert response.status_code == 200
        body = response.json()
        assert body["transaction_type"] == "Expense"
        assert body["reimbursement_status"] == "unpaid"
        assert body["reimbursement_paid_by"] is None
        assert body["reimbursement_paid_at"] is None

    async def test_editing_type_to_reimbursement_resets_payment_fields(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "45.50",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "45.50"}],
            },
        )
        transaction_id = create_response.json()["id"]

        response = await client.patch(f"/transactions/{transaction_id}", json={"transaction_type": "Reimbursement"})
        assert response.status_code == 200
        body = response.json()
        assert body["transaction_type"] == "Reimbursement"
        assert body["reimbursement_status"] == "unpaid"
        assert body["reimbursement_paid_by"] is None
        assert body["reimbursement_paid_at"] is None


class TestCostSplit:
    async def test_creates_transaction_with_even_split(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert len(body["shares"]) == 1
        assert body["shares"][0]["shared_with_user_id"] == str(partner.id)
        assert body["shares"][0]["share_amount"] == "30.00"
        assert body["shares"][0]["status"] == "pending"

    async def test_rejects_shares_exceeding_total(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "40.00"}],
            },
        )
        assert response.status_code == 422

    async def test_allows_shares_summing_to_less_than_total(self, client, session, unique_email):
        # $90 dinner split 3 ways: only the partner's $30 is listed as a share,
        # leaving the remaining $60 as the payer's own implicit share.
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Dinner",
                "total_amount": "90.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Food", "amount": "90.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        assert response.status_code == 201, response.text

    async def test_rejects_recipient_outside_household(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        other_email = "stranger-" + unique_email
        stranger = await _create_verified_owner(session, other_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(stranger.id), "share_amount": "30.00"}],
            },
        )
        assert response.status_code == 422

    async def test_split_moves_spend_from_payer_to_recipient(self, client, session, unique_email):
        # Whole amount given away: payer's own net spend drops to $0, and the
        # recipient's own spend gains the full $30 instead.
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        owner_view = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert owner_view.json()["total_expenses"] == "0.00"

        await _login(client, partner_email)
        partner_view = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert partner_view.json()["total_expenses"] == "30.00"

    async def test_partial_split_leaves_remainder_on_payer_own_spend(self, client, session, unique_email):
        # $90 dinner, $30 split to the partner -> payer keeps $60 of their own
        # spend, partner gains $30 of their own.
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Dinner",
                "total_amount": "90.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Food", "amount": "90.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        owner_view = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert owner_view.json()["total_expenses"] == "60.00"

        await _login(client, partner_email)
        partner_view = await client.get("/dashboard/monthly", params={"month": 7, "year": 2026})
        assert partner_view.json()["total_expenses"] == "30.00"

    async def test_split_prorates_across_categories(self, client, session, unique_email):
        # A two-category $100 transaction split 50/50 should attribute each
        # side's category spend proportionally to how the line items break down
        # (80/20 grocery/restaurant), not just at the transaction-total level.
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        grocery = await _make_category(session, owner, name="Grocery")
        restaurant = await _make_category(session, owner, name="Restaurant")

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "100.00",
                "transaction_type": "Expense",
                "line_items": [
                    {"category_id": str(grocery.id), "item_name": "Food", "amount": "80.00"},
                    {"category_id": str(restaurant.id), "item_name": "Snack", "amount": "20.00"},
                ],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "50.00"}],
            },
        )
        owner_breakdown = await client.get("/dashboard/category-breakdown", params={"month": 7, "year": 2026})
        owner_amounts = {row["name"]: row["amount"] for row in owner_breakdown.json()}
        assert owner_amounts["Grocery"] == "40.00"
        assert owner_amounts["Restaurant"] == "10.00"

        await _login(client, partner_email)
        partner_breakdown = await client.get("/dashboard/category-breakdown", params={"month": 7, "year": 2026})
        partner_amounts = {row["name"]: row["amount"] for row in partner_breakdown.json()}
        assert partner_amounts["Grocery"] == "40.00"
        assert partner_amounts["Restaurant"] == "10.00"

    async def test_settle_requires_settled_by_and_is_one_way(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        create = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        transaction_id = create.json()["id"]
        share_id = create.json()["shares"][0]["id"]

        empty = await client.post(
            f"/transactions/{transaction_id}/shares/{share_id}/settle", json={"settled_by": ""}
        )
        assert empty.status_code == 422

        settled = await client.post(
            f"/transactions/{transaction_id}/shares/{share_id}/settle", json={"settled_by": "Partner Pat"}
        )
        assert settled.status_code == 200
        body = settled.json()
        assert body["status"] == "settled"
        assert body["settled_by"] == "Partner Pat"
        assert body["settled_at"] is not None

        already_settled = await client.post(
            f"/transactions/{transaction_id}/shares/{share_id}/settle", json={"settled_by": "Someone Else"}
        )
        assert already_settled.status_code == 422

    async def test_recipient_cannot_settle_their_own_share(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner, partner_email = await _make_partner(session, owner, unique_email)
        pm = await _make_payment_method(session, owner)
        category = await _make_category(session, owner)

        create = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "30.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "30.00"}],
                "shares": [{"shared_with_user_id": str(partner.id), "share_amount": "30.00"}],
            },
        )
        transaction_id = create.json()["id"]
        share_id = create.json()["shares"][0]["id"]

        await _login(client, partner_email)
        response = await client.post(
            f"/transactions/{transaction_id}/shares/{share_id}/settle", json={"settled_by": "Partner Pat"}
        )
        assert response.status_code == 403
