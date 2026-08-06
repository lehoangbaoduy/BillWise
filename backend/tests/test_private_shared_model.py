"""Creator-based Private/Shared model: Wallet/Budget/Goal/RecurringBill each
get a created_by_user_id + is_shared pair (item_visibility.py). Only an
owner and a co-owner ever have distinct "creator" identities for these
entities -- a plain (non-co-owner) partner can never create one, so the
model must be a no-op for them (PRD §21.4's pre-existing behavior stays
intact). Cashback and Transaction privacy is derived from the linked
PaymentMethod rather than stored independently.
"""
from datetime import date

from app.core.security import hash_password
from app.models._common import utcnow
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


async def _make_plain_partner(session, owner, email, can_add_transactions=True):
    partner = User(
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        display_name="Plain Partner",
        role=UserRole.PARTNER,
        invited_by_user_id=owner.id,
        email_verified_at=utcnow(),
    )
    session.add(partner)
    await session.flush()
    session.add(PartnerPermission(partner_user_id=partner.id, can_add_transactions=can_add_transactions))
    await session.commit()
    await session.refresh(partner)
    return partner


async def _make_payment_method(session, owner, is_shared=False, name="Cash Wallet"):
    pm = PaymentMethod(user_id=owner.id, name=name, type=PaymentMethodType.CASH, is_shared=is_shared)
    session.add(pm)
    await session.commit()
    await session.refresh(pm)
    return pm


class TestWalletPrivacy:
    async def test_co_owner_private_wallet_invisible_to_owner(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"partner-{unique_email}")
        await _login(client, co_owner.email)
        created = await client.post("/payment-methods", json={"name": "Co-owner card", "type": "Cash"})
        assert created.status_code == 201
        pm_id = created.json()["id"]
        assert created.json()["is_shared"] is False

        await _login(client, unique_email)
        owner_list = await client.get("/payment-methods")
        assert all(pm["id"] != pm_id for pm in owner_list.json())
        owner_get = await client.get(f"/payment-methods/{pm_id}")
        assert owner_get.status_code == 404

    async def test_shared_wallet_visible_to_both(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"partner-{unique_email}")
        pm = await _make_payment_method(session, owner, is_shared=True, name="Joint Checking")

        await _login(client, co_owner.email)
        co_owner_get = await client.get(f"/payment-methods/{pm.id}")
        assert co_owner_get.status_code == 200

    async def test_plain_partner_can_still_spend_on_owners_private_wallet(self, client, session, unique_email):
        """Regression guard: validate_payment_method must stay a no-op for a
        plain (non-co-owner) partner. The private/shared model only ever
        distinguishes owner vs co-owner identity -- a plain partner can never
        create a wallet, so blocking them from the owner's default (private)
        wallet would just be a functional regression from PRD §21.4."""
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_plain_partner(session, owner, f"partner-{unique_email}")
        # Categories are always shared/visible to every household member --
        # the wallet itself stays private here, which is exactly the case
        # this test is guarding.
        category_response = await client.post("/categories", json={"name": "Grocery", "category_type": "expense"})
        category_id = category_response.json()["id"]
        pm = await _make_payment_method(session, owner, is_shared=False)

        await _login(client, partner.email)
        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": category_id, "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 201, response.text

    async def test_co_owner_cannot_spend_on_others_private_wallet(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"partner-{unique_email}")
        category_response = await client.post("/categories", json={"name": "Grocery", "category_type": "expense"})
        category_id = category_response.json()["id"]
        pm = await _make_payment_method(session, owner, is_shared=False)

        await _login(client, co_owner.email)
        response = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": category_id, "item_name": "x", "amount": "10.00"}],
            },
        )
        assert response.status_code == 422


class TestRecurringBillSharingConstraint:
    async def test_cannot_share_bill_paid_from_private_wallet(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner, is_shared=False)
        category_response = await client.post("/categories", json={"name": "Streaming", "category_type": "expense"})
        category_id = category_response.json()["id"]

        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": category_id,
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": "2026-08-01",
            },
        )
        assert create_response.status_code == 201
        assert create_response.json()["is_shared"] is False
        bill_id = create_response.json()["id"]

        share_response = await client.patch(f"/recurring-bills/{bill_id}/sharing", json={"is_shared": True})
        assert share_response.status_code == 422

    async def test_can_share_bill_paid_from_shared_wallet(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, owner, is_shared=True)
        category_response = await client.post("/categories", json={"name": "Streaming", "category_type": "expense"})
        category_id = category_response.json()["id"]

        create_response = await client.post(
            "/recurring-bills",
            json={
                "payment_method_id": str(pm.id),
                "category_id": category_id,
                "name": "Netflix",
                "amount": "15.99",
                "frequency": "monthly",
                "due_date": "2026-08-01",
                "is_shared": True,
            },
        )
        assert create_response.status_code == 201
        assert create_response.json()["is_shared"] is True


class TestCashbackDerivedPrivacy:
    async def test_rule_is_shared_derives_from_payment_method(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        private_pm = await _make_payment_method(session, owner, is_shared=False, name="Private Card")
        shared_pm = await _make_payment_method(session, owner, is_shared=True, name="Shared Card")

        private_rule = await client.post(
            "/cashback-rules",
            json={"payment_method_id": str(private_pm.id), "cashback_rate": "2.00", "start_date": "2026-01-01"},
        )
        assert private_rule.status_code == 201
        assert private_rule.json()["is_shared"] is False

        shared_rule = await client.post(
            "/cashback-rules",
            json={"payment_method_id": str(shared_pm.id), "cashback_rate": "3.00", "start_date": "2026-01-01"},
        )
        assert shared_rule.status_code == 201
        assert shared_rule.json()["is_shared"] is True

    async def test_co_owner_cannot_see_others_private_wallet_cashback_rule(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"partner-{unique_email}")
        private_pm = await _make_payment_method(session, owner, is_shared=False)
        rule_response = await client.post(
            "/cashback-rules",
            json={"payment_method_id": str(private_pm.id), "cashback_rate": "2.00", "start_date": "2026-01-01"},
        )
        rule_id = rule_response.json()["id"]

        await _login(client, co_owner.email)
        list_response = await client.get("/cashback-rules")
        assert all(rule["id"] != rule_id for rule in list_response.json())
        delete_response = await client.delete(f"/cashback-rules/{rule_id}")
        assert delete_response.status_code == 404


class TestTransactionDerivedPrivacy:
    async def test_transaction_is_shared_derives_from_payment_method(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        private_pm = await _make_payment_method(session, owner, is_shared=False)
        category_response = await client.post("/categories", json={"name": "Grocery", "category_type": "expense"})
        category_id = category_response.json()["id"]

        created = await client.post(
            "/transactions",
            json={
                "payment_method_id": str(private_pm.id),
                "date": "2026-07-01",
                "merchant": "Costco",
                "total_amount": "10.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": category_id, "item_name": "x", "amount": "10.00"}],
            },
        )
        assert created.status_code == 201
        assert created.json()["is_shared"] is False

        list_response = await client.get("/transactions")
        listed = next(t for t in list_response.json() if t["id"] == created.json()["id"])
        assert listed["is_shared"] is False

        get_response = await client.get(f"/transactions/{created.json()['id']}")
        assert get_response.json()["is_shared"] is False


class TestDashboardOwnerCoOwnerPaymentMethodVisibility:
    """Regression guard: top_payment_method / spend_by_payment_method used to
    gate on `user.role != UserRole.PARTNER`, which incorrectly excluded a
    co-owner (a PARTNER-role user with full financial-data access) too. Both
    must now gate on owner-or-co-owner identity instead."""

    async def test_co_owner_sees_top_payment_method_in_monthly_overview(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        co_owner = await _make_co_owner(session, owner, f"partner-{unique_email}")
        pm = await _make_payment_method(session, owner, is_shared=True)
        category_response = await client.post("/categories", json={"name": "Grocery", "category_type": "expense"})
        category_id = category_response.json()["id"]
        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": date.today().isoformat(),
                "merchant": "Costco",
                "total_amount": "50.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": category_id, "item_name": "x", "amount": "50.00"}],
            },
        )

        await _login(client, co_owner.email)
        today = date.today()
        response = await client.get("/dashboard/monthly", params={"month": today.month, "year": today.year})
        assert response.status_code == 200
        assert response.json()["top_payment_method"] is not None
