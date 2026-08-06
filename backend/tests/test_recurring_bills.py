from datetime import date, timedelta
from decimal import Decimal

from sqlmodel import select

from app.core.security import hash_password
from app.models._common import utcnow
from app.models.category import Category, CategoryType
from app.models.partner_permission import PartnerPermission
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.recurring_bill import RecurringBill, RecurringBillPayment, RecurringBillPaymentStatus, RecurringFrequency
from app.models.user import User, UserRole
from app.services.recurring_bill_service import next_due_date, resolve_card_payment_due_date

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


async def _make_payment_method(session, user, **kwargs):
    pm = PaymentMethod(user_id=user.id, name="Test Card", type=PaymentMethodType.CREDIT_CARD, **kwargs)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


async def _make_category(session, user, category_type=CategoryType.EXPENSE, name="Subscription"):
    category = Category(user_id=user.id, name=name, category_type=category_type)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _make_bill(session, user, payment_method, category, **kwargs):
    defaults = dict(
        user_id=user.id,
        payment_method_id=payment_method.id,
        category_id=category.id,
        name="Netflix",
        amount=Decimal("15.99"),
        frequency=RecurringFrequency.MONTHLY,
        due_date=date.today(),
    )
    defaults.update(kwargs)
    bill = RecurringBill(**defaults)
    session.add(bill)
    await session.flush()
    session.add(RecurringBillPayment(recurring_bill_id=bill.id, due_date=bill.due_date, amount_due=bill.amount, status=RecurringBillPaymentStatus.UPCOMING))
    await session.commit()
    await session.refresh(bill)
    return bill


class TestCreateRecurringBill:
    async def test_requires_authentication(self, client):
        response = await client.post("/recurring-bills", json={})
        assert response.status_code == 401

    async def test_creates_bill_with_first_upcoming_period(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)

        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": "2026-08-01",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Netflix"
        assert body["current_period"]["status"] == "upcoming"
        assert body["current_period"]["due_date"] == "2026-08-01"
        assert len(body["payments"]) == 1

    async def test_rejects_invalid_payment_method(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        category = await _make_category(session, user)
        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": "00000000-0000-0000-0000-000000000000",
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": "2026-08-01",
            },
        )
        assert response.status_code == 422

    async def test_rejects_income_category(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user, category_type=CategoryType.INCOME, name="Salary")
        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": "2026-08-01",
            },
        )
        assert response.status_code == 422

    async def test_auto_populates_due_date_from_payment_method_due_day(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user, due_day_optional=25)
        category = await _make_category(session, user)
        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Card Payment",
                "amount": "100.00",
                "frequency": "monthly",
            },
        )
        assert response.status_code == 201
        assert response.json()["due_date"].endswith("-25")

    async def test_rejects_missing_due_date_without_card_payment_info(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
            },
        )
        assert response.status_code == 422


class TestListRecurringBills:
    async def test_only_returns_own_active_bills(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_bill(session, user, pm, category)

        other = await _create_verified_owner(session, "other-" + unique_email)
        other_pm = await _make_payment_method(session, other)
        other_category = await _make_category(session, other)
        await _make_bill(session, other, other_pm, other_category)

        response = await client.get("/recurring-bills")
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_flips_upcoming_to_overdue_when_due_date_passed(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        await _make_bill(session, user, pm, category, due_date=date.today() - timedelta(days=3))

        response = await client.get("/recurring-bills")
        assert response.status_code == 200
        assert response.json()[0]["current_period"]["status"] == "overdue"

    async def test_generates_next_period_after_latest_is_paid(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, due_date=date(2026, 1, 1), frequency=RecurringFrequency.MONTHLY)

        payment = (await session.exec(
            select(RecurringBillPayment).where(RecurringBillPayment.recurring_bill_id == bill.id)
        )).first()
        payment.status = RecurringBillPaymentStatus.PAID
        payment.paid_date = date(2026, 1, 1)
        session.add(payment)
        await session.commit()

        response = await client.get("/recurring-bills")
        assert response.status_code == 200
        body = response.json()[0]
        assert len(body["payments"]) == 2
        assert body["current_period"]["due_date"] == "2026-02-01"

    async def test_custom_frequency_does_not_auto_generate(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, due_date=date(2026, 1, 1), frequency=RecurringFrequency.CUSTOM)

        payment = (await session.exec(
            select(RecurringBillPayment).where(RecurringBillPayment.recurring_bill_id == bill.id)
        )).first()
        payment.status = RecurringBillPaymentStatus.PAID
        payment.paid_date = date(2026, 1, 1)
        session.add(payment)
        await session.commit()

        response = await client.get("/recurring-bills")
        assert response.status_code == 200
        body = response.json()[0]
        assert len(body["payments"]) == 1
        assert body["current_period"] is not None
        assert body["current_period"]["status"] == "paid"


class TestUpdateRecurringBill:
    async def test_updates_fields(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category)

        response = await client.patch(f"/recurring-bills/{bill.id}", json={"amount": "20.00", "name": "Netflix Premium"})
        assert response.status_code == 200
        body = response.json()
        assert body["amount"] == "20.00"
        assert body["name"] == "Netflix Premium"

    async def test_rejects_explicit_null_on_required_field(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category)

        response = await client.patch(f"/recurring-bills/{bill.id}", json={"category_id": None})
        assert response.status_code == 422

    async def test_404_for_other_users_bill(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category)

        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)

        response = await client.patch(f"/recurring-bills/{bill.id}", json={"amount": "20.00"})
        assert response.status_code == 404


class TestDeactivateRecurringBill:
    async def test_deactivates_and_hides_from_list(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category)

        response = await client.delete(f"/recurring-bills/{bill.id}")
        assert response.status_code == 204

        response = await client.get("/recurring-bills")
        assert response.json() == []


class TestMarkPaid:
    async def test_marks_paid_without_creating_transaction_by_default(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, auto_create_transaction=False)

        response = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={})
        assert response.status_code == 200
        body = response.json()
        assert body["current_period"]["status"] in ("paid", "upcoming")
        paid_period = next(p for p in body["payments"] if p["status"] == "paid")
        assert paid_period["transaction_id"] is None

    async def test_creates_linked_transaction_when_auto_create_enabled(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, auto_create_transaction=True)

        response = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={"amount_paid": "15.99"})
        assert response.status_code == 200
        body = response.json()
        paid_period = next(p for p in body["payments"] if p["status"] == "paid")
        assert paid_period["transaction_id"] is not None

        transactions_response = await client.get("/transactions")
        transactions = transactions_response.json()
        matching = [t for t in transactions if t["id"] == paid_period["transaction_id"]]
        assert len(matching) == 1
        assert matching[0]["source"] == "Recurring Bill"
        assert matching[0]["total_amount"] == "15.99"

    async def test_409_when_no_open_period(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, frequency=RecurringFrequency.CUSTOM)

        first = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={})
        assert first.status_code == 200

        second = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={})
        assert second.status_code == 409

    async def test_404_for_other_users_bill(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category)

        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)

        response = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={})
        assert response.status_code == 404


class TestDeleteLinkedTransaction:
    """Deleting a transaction that mark-paid auto-created must reopen the
    period it was linked to, not 500. recurring_bill_payments.transaction_id
    had no ON DELETE behavior, so Postgres raised a raw ForeignKeyViolation --
    which surfaces in the browser as a CORS error, since a 500 response never
    gets the CORS middleware's Access-Control-Allow-Origin header attached."""

    async def test_deleting_the_auto_created_transaction_reopens_the_period(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        bill = await _make_bill(session, user, pm, category, auto_create_transaction=True)

        mark_paid = await client.post(f"/recurring-bills/{bill.id}/mark-paid", json={"amount_paid": "15.99"})
        assert mark_paid.status_code == 200
        paid_period = next(p for p in mark_paid.json()["payments"] if p["status"] == "paid")
        transaction_id = paid_period["transaction_id"]
        assert transaction_id is not None

        delete_response = await client.delete(f"/transactions/{transaction_id}")
        assert delete_response.status_code == 204

        bills_response = await client.get("/recurring-bills")
        refreshed = next(b for b in bills_response.json() if b["id"] == str(bill.id))
        period = next(p for p in refreshed["payments"] if p["id"] == paid_period["id"])
        assert period["status"] in ("upcoming", "overdue")
        assert period["transaction_id"] is None


class TestNextDueDate:
    def test_weekly(self):
        assert next_due_date(RecurringFrequency.WEEKLY, date(2026, 1, 1)) == date(2026, 1, 8)

    def test_biweekly(self):
        assert next_due_date(RecurringFrequency.BIWEEKLY, date(2026, 1, 1)) == date(2026, 1, 15)

    def test_monthly_clamps_to_shorter_month(self):
        assert next_due_date(RecurringFrequency.MONTHLY, date(2026, 1, 31)) == date(2026, 2, 28)

    def test_quarterly(self):
        assert next_due_date(RecurringFrequency.QUARTERLY, date(2026, 1, 15)) == date(2026, 4, 15)

    def test_yearly_leap_day(self):
        assert next_due_date(RecurringFrequency.YEARLY, date(2028, 2, 29)) == date(2029, 2, 28)

    def test_custom_returns_none(self):
        assert next_due_date(RecurringFrequency.CUSTOM, date(2026, 1, 1)) is None


class TestResolveCardPaymentDueDate:
    async def test_uses_due_day_when_still_ahead_this_month(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user, due_day_optional=25)
        result = resolve_card_payment_due_date(pm, date(2026, 7, 10))
        assert result == date(2026, 7, 25)

    async def test_rolls_to_next_month_when_day_already_passed(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user, due_day_optional=5)
        result = resolve_card_payment_due_date(pm, date(2026, 7, 10))
        assert result == date(2026, 8, 5)

    async def test_none_when_no_day_configured(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user)
        result = resolve_card_payment_due_date(pm, date(2026, 7, 10))
        assert result is None

    async def test_prefers_due_day_over_statement_day(self, session, unique_email):
        user = await _create_verified_owner(session, unique_email)
        pm = await _make_payment_method(session, user, due_day_optional=20, statement_day_optional=1)
        result = resolve_card_payment_due_date(pm, date(2026, 7, 10))
        assert result == date(2026, 7, 20)


class TestUpdateRecurringBillSharing:
    async def test_owner_can_toggle_own_created_bill(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user, is_shared=True)
        category = await _make_category(session, user)
        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.00",
                "frequency": "monthly",
                "due_date": "2026-08-15",
            },
        )
        bill_id = create_response.json()["id"]

        response = await client.patch(f"/recurring-bills/{bill_id}/sharing", json={"is_shared": True})
        assert response.status_code == 200
        assert response.json()["is_shared"] is True

    async def test_co_owner_can_toggle_own_created_bill(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        pm = await _make_payment_method(session, owner, is_shared=True)
        category = await _make_category(session, owner)
        await _login(client, co_owner.email)
        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.00",
                "frequency": "monthly",
                "due_date": "2026-08-15",
            },
        )
        bill_id = create_response.json()["id"]

        response = await client.patch(f"/recurring-bills/{bill_id}/sharing", json={"is_shared": True})
        assert response.status_code == 200

    async def test_co_owner_cannot_toggle_owner_created_shared_bill(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner, is_shared=True)
        category = await _make_category(session, owner)
        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.00",
                "frequency": "monthly",
                "due_date": "2026-08-15",
                "is_shared": True,
            },
        )
        bill_id = create_response.json()["id"]
        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        await _login(client, co_owner.email)

        response = await client.patch(f"/recurring-bills/{bill_id}/sharing", json={"is_shared": False})
        assert response.status_code == 403

    async def test_owner_cannot_toggle_co_owner_created_shared_bill(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"co-owner-{unique_email}")
        pm = await _make_payment_method(session, owner, is_shared=True)
        category = await _make_category(session, owner)
        await _login(client, co_owner.email)
        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": str(category.id),
                "name": "Netflix",
                "amount": "15.00",
                "frequency": "monthly",
                "due_date": "2026-08-15",
                "is_shared": True,
            },
        )
        bill_id = create_response.json()["id"]
        await _login(client, owner.email)

        response = await client.patch(f"/recurring-bills/{bill_id}/sharing", json={"is_shared": False})
        assert response.status_code == 403


class TestPartnerForbidden:
    """PRD §21.4: recurring bills are not in the dashboards/budgets/reports
    sharing list, so they stay owner-only."""

    async def test_partner_cannot_list_recurring_bills(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
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

        response = await client.get("/recurring-bills")
        assert response.status_code == 403
