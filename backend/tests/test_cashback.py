from datetime import date
from decimal import Decimal

from sqlmodel import select

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.cashback import CashbackRecord, CashbackRecordStatus, CashbackRule
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.user import User, UserRole
from app.services.cashback_service import resolve_cashback_rate

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


async def _make_payment_method(session, user, **kwargs):
    pm = PaymentMethod(user_id=user.id, name="Rewards Card", type=PaymentMethodType.CREDIT_CARD, **kwargs)
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


async def _make_rule(session, user, pm, category_id=None, **kwargs):
    defaults = dict(
        user_id=user.id,
        payment_method_id=pm.id,
        category_id=category_id,
        cashback_rate=Decimal("2.00"),
        start_date=date(2026, 1, 1),
    )
    defaults.update(kwargs)
    rule = CashbackRule(**defaults)
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return rule


class TestListCashbackRules:
    async def test_requires_authentication(self, client):
        response = await client.get("/cashback-rules")
        assert response.status_code == 401

    async def test_lists_only_own_rules(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        await _make_rule(session, user, pm)
        await _make_rule(session, user, pm, cashback_rate=Decimal("3.00"))

        other = await _create_verified_owner(session, "other-" + unique_email)
        other_pm = await _make_payment_method(session, other)
        await _make_rule(session, other, other_pm)

        await _login(client, unique_email)
        response = await client.get("/cashback-rules")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert all(row["payment_method_id"] == str(pm.id) for row in body)

    async def test_empty_when_no_rules(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/cashback-rules")
        assert response.status_code == 200
        assert response.json() == []


class TestCreateCashbackRule:
    async def test_requires_authentication(self, client):
        response = await client.post("/cashback-rules", json={})
        assert response.status_code == 401

    async def test_creates_default_rule(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        response = await client.post(
            "/cashback-rules",
            json={"payment_method_id": str(pm.id), "cashback_rate": "1.50", "start_date": "2026-01-01"},
        )
        assert response.status_code == 201
        assert response.json()["category_id"] is None

    async def test_creates_category_specific_rule(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        response = await client.post(
            "/cashback-rules",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "cashback_rate": "5.00",
                "start_date": "2026-01-01",
            },
        )
        assert response.status_code == 201
        assert response.json()["category_id"] == str(category.id)

    async def test_rejects_invalid_payment_method(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/cashback-rules",
            json={
                "payment_method_id": "00000000-0000-0000-0000-000000000000",
                "cashback_rate": "1.00",
                "start_date": "2026-01-01",
            },
        )
        assert response.status_code == 422

    async def test_rejects_rate_over_100(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        response = await client.post(
            "/cashback-rules",
            json={"payment_method_id": str(pm.id), "cashback_rate": "150", "start_date": "2026-01-01"},
        )
        assert response.status_code == 422


class TestUpdateDeleteCashbackRule:
    async def test_updates_rate(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        rule = await _make_rule(session, user, pm)
        response = await client.patch(f"/cashback-rules/{rule.id}", json={"cashback_rate": "3.00"})
        assert response.status_code == 200
        assert response.json()["cashback_rate"] == "3.00"

    async def test_404_for_other_users_rule(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        rule = await _make_rule(session, user, pm)
        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        response = await client.patch(f"/cashback-rules/{rule.id}", json={"cashback_rate": "3.00"})
        assert response.status_code == 404

    async def test_deletes_rule(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        rule = await _make_rule(session, user, pm)
        response = await client.delete(f"/cashback-rules/{rule.id}")
        assert response.status_code == 204


class TestResolveCashbackRate:
    async def test_no_rule_returns_zero(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 6, 1))
        assert rate == Decimal("0")

    async def test_default_rule_applies_to_any_category(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=None, cashback_rate=Decimal("1.00"))
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 6, 1))
        assert rate == Decimal("1.00")

    async def test_category_specific_rule_wins_over_default(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=None, cashback_rate=Decimal("1.00"))
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("5.00"))
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 6, 1))
        assert rate == Decimal("5.00")

    async def test_most_recent_start_date_wins_among_same_specificity(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"), start_date=date(2026, 1, 1))
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("4.00"), start_date=date(2026, 6, 1))
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 7, 1))
        assert rate == Decimal("4.00")

    async def test_expired_rule_does_not_apply(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("5.00"), end_date=date(2026, 3, 31))
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 6, 1))
        assert rate == Decimal("0")

    async def test_future_rule_does_not_apply_yet(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("5.00"), start_date=date(2026, 12, 1))
        rate = await resolve_cashback_rate(session, user.id, pm.id, category.id, date(2026, 6, 1))
        assert rate == Decimal("0")


class TestAutoComputationOnTransactionCreate:
    async def test_creates_cashback_record_for_expense(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        assert response.status_code == 201
        transaction_id = response.json()["id"]

        records = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).all()
        assert len(records) == 1
        assert records[0].estimated_amount == Decimal("1.00")
        assert records[0].status == CashbackRecordStatus.ESTIMATED

    async def test_no_cashback_record_for_income(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Salary")
        await _make_rule(session, user, pm, category_id=None, cashback_rate=Decimal("2.00"))

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Employer",
                "total_amount": "1000.00",
                "transaction_type": "Income",
                "line_items": [{"category_id": str(category.id), "item_name": "Paycheck", "amount": "1000.00"}],
            },
        )
        assert response.status_code == 201
        transaction_id = response.json()["id"]
        records = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).all()
        assert len(records) == 0

    async def test_zero_estimated_when_no_rule(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        transaction_id = response.json()["id"]
        records = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).all()
        assert records[0].estimated_amount == Decimal("0.00")


class TestUpdateTransactionRecomputesCashback:
    async def test_replacing_line_items_recomputes_cashback(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        transaction_id = create_response.json()["id"]

        response = await client.patch(
            f"/transactions/{transaction_id}",
            json={
                "total_amount": "80.00",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "80.00"}],
            },
        )
        assert response.status_code == 200

        records = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).all()
        assert len(records) == 1
        assert records[0].estimated_amount == Decimal("1.60")

    async def test_manual_override_persists_when_line_items_untouched(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        transaction_id = create_response.json()["id"]
        record = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).first()

        override_response = await client.patch(f"/cashback-records/{record.id}", json={"estimated_amount": "9.99"})
        assert override_response.status_code == 200

        # Editing a field without touching line_items must not clobber the override.
        edit_response = await client.patch(f"/transactions/{transaction_id}", json={"merchant": "Whole Foods Market"})
        assert edit_response.status_code == 200

        await session.refresh(record)
        assert record.estimated_amount == Decimal("9.99")


class TestUpdateCashbackRecord:
    async def test_sets_redeemed_amount_and_status(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        transaction_id = create_response.json()["id"]
        record = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).first()

        response = await client.patch(f"/cashback-records/{record.id}", json={"redeemed_amount": "1.00", "status": "redeemed"})
        assert response.status_code == 200
        body = response.json()
        assert body["redeemed_amount"] == "1.00"
        assert body["status"] == "redeemed"

    async def test_404_for_other_users_record(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))
        create_response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )
        transaction_id = create_response.json()["id"]
        record = (await session.exec(select(CashbackRecord).where(CashbackRecord.transaction_id == transaction_id))).first()

        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        response = await client.patch(f"/cashback-records/{record.id}", json={"redeemed_amount": "1.00"})
        assert response.status_code == 404


class TestCashbackSummary:
    async def test_requires_authentication(self, client):
        response = await client.get("/cashback?year=2026")
        assert response.status_code == 401

    async def test_aggregates_by_card_and_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-06-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )

        response = await client.get(f"/cashback?year=2026&month=6")
        assert response.status_code == 200
        body = response.json()
        assert body["total_estimated"] == "1.00"
        assert body["total_redeemed"] == "0"
        assert body["total_unredeemed"] == "1.00"
        assert len(body["by_card"]) == 1
        assert body["by_card"][0]["payment_method_id"] == str(pm.id)
        assert len(body["by_category"]) == 1

    async def test_excludes_records_outside_the_month(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-05-15",
                "merchant": "Whole Foods",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
            },
        )

        response = await client.get(f"/cashback?year=2026&month=6")
        assert response.status_code == 200
        assert response.json()["total_estimated"] == "0"

    async def test_year_only_aggregates_whole_year(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_rule(session, user, pm, category_id=category.id, cashback_rate=Decimal("2.00"))

        for month_date in ("2026-01-15", "2026-06-15"):
            await client.post(
                "/transactions",
                json={
                    "payment_method_id": str(pm.id),
                    "date": month_date,
                    "merchant": "Whole Foods",
                    "total_amount": "50.00",
                    "transaction_type": "Expense",
                    "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "50.00"}],
                },
            )

        response = await client.get(f"/cashback?year=2026")
        assert response.status_code == 200
        assert response.json()["total_estimated"] == "2.00"
