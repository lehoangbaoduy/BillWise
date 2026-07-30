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


async def _make_payment_method(session, user, type_=PaymentMethodType.CASH):
    pm = PaymentMethod(user_id=user.id, name="Cash Wallet", type=type_)
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
