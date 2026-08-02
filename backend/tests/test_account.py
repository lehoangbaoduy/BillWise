from datetime import timedelta

from sqlmodel import select

from app.core.security import generate_token, hash_password, hash_token
from app.models._common import utcnow
from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.user import AccountDeletionToken, User, UserRole
from app.services.account_deletion_service import hard_delete_expired_accounts

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
    await session.refresh(user)
    return user


async def _login(client, email, password=VALID_PASSWORD):
    return await client.post("/auth/login", json={"email": email, "password": password})


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


async def _issue_deletion_token(session, user, *, expires_in=timedelta(minutes=30), used=False):
    token = generate_token()
    session.add(
        AccountDeletionToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + expires_in,
            used_at=utcnow() if used else None,
        )
    )
    await session.commit()
    return token


class TestDeleteRequest:
    async def test_requires_authentication(self, client):
        response = await client.post("/account/delete-request", json={"password": VALID_PASSWORD})
        assert response.status_code == 401

    async def test_partner_forbidden(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_partner(session, owner, unique_email)
        await _login(client, partner.email)

        response = await client.post("/account/delete-request", json={"password": VALID_PASSWORD})
        assert response.status_code == 403

    async def test_wrong_password_rejected(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post("/account/delete-request", json={"password": "WrongPassword123"})
        assert response.status_code == 401

    async def test_correct_password_creates_pending_token(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        response = await client.post("/account/delete-request", json={"password": VALID_PASSWORD})
        assert response.status_code == 202

        tokens = (
            await session.exec(select(AccountDeletionToken).where(AccountDeletionToken.user_id == owner.id))
        ).all()
        assert len(tokens) == 1
        assert tokens[0].used_at is None


class TestDeleteConfirm:
    async def test_invalid_token_rejected(self, client):
        response = await client.post(
            "/account/delete-confirm", json={"token": "not-a-real-token", "confirmation_email": "a@b.com"}
        )
        assert response.status_code == 400

    async def test_expired_token_rejected(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = await _issue_deletion_token(session, owner, expires_in=timedelta(minutes=-5))

        response = await client.post(
            "/account/delete-confirm", json={"token": token, "confirmation_email": owner.email}
        )
        assert response.status_code == 400

    async def test_already_used_token_rejected(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = await _issue_deletion_token(session, owner, used=True)

        response = await client.post(
            "/account/delete-confirm", json={"token": token, "confirmation_email": owner.email}
        )
        assert response.status_code == 400

    async def test_wrong_confirmation_email_rejected(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = await _issue_deletion_token(session, owner)

        response = await client.post(
            "/account/delete-confirm", json={"token": token, "confirmation_email": "someone-else@example.com"}
        )
        assert response.status_code == 400

        await session.refresh(owner)
        assert owner.is_active is True

    async def test_valid_confirm_deactivates_owner_and_partners_and_schedules_hard_delete(
        self, client, session, unique_email
    ):
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_partner(session, owner, unique_email)
        token = await _issue_deletion_token(session, owner)

        response = await client.post(
            "/account/delete-confirm", json={"token": token, "confirmation_email": owner.email.upper()}
        )
        assert response.status_code == 200

        await session.refresh(owner)
        await session.refresh(partner)
        assert owner.is_active is False
        assert partner.is_active is False
        assert owner.hard_delete_at is not None
        expected = utcnow() + timedelta(days=30)
        assert abs((owner.hard_delete_at - expected).total_seconds()) < 60

    async def test_deactivated_owner_cannot_log_in_after_confirm(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = await _issue_deletion_token(session, owner)
        await client.post("/account/delete-confirm", json={"token": token, "confirmation_email": owner.email})

        response = await _login(client, unique_email)
        assert response.status_code == 401

    async def test_deactivated_partner_cannot_log_in_after_owners_confirm(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_partner(session, owner, unique_email)
        token = await _issue_deletion_token(session, owner)
        await client.post("/account/delete-confirm", json={"token": token, "confirmation_email": owner.email})

        response = await _login(client, partner.email)
        assert response.status_code == 401


class TestDeleteCancel:
    async def test_requires_authentication(self, client):
        response = await client.post("/account/delete-cancel")
        assert response.status_code == 401

    async def test_partner_forbidden(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner = await _make_partner(session, owner, unique_email)
        await _login(client, partner.email)

        response = await client.post("/account/delete-cancel")
        assert response.status_code == 403

    async def test_cancel_invalidates_pending_token(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        token = await _issue_deletion_token(session, owner)

        response = await client.post("/account/delete-cancel")
        assert response.status_code == 200

        confirm_response = await client.post(
            "/account/delete-confirm", json={"token": token, "confirmation_email": owner.email}
        )
        assert confirm_response.status_code == 400

        await session.refresh(owner)
        assert owner.is_active is True


class TestHardDeleteExpiredAccounts:
    async def _make_category(self, session, user, name="Grocery"):
        category = Category(user_id=user.id, name=name, category_type=CategoryType.EXPENSE)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    async def test_purges_data_and_anonymizes_audit_logs_for_expired_account(self, session, unique_email):
        from app.core.audit import log_audit_event
        from app.models.audit_log import AuditLog

        owner = await _create_verified_owner(session, unique_email)
        owner.is_active = False
        owner.hard_delete_at = utcnow() - timedelta(days=1)
        session.add(owner)
        await session.commit()

        pm = PaymentMethod(user_id=owner.id, name="Cash", type=PaymentMethodType.CASH)
        session.add(pm)
        category = await self._make_category(session, owner)
        session.add(Budget(user_id=owner.id, category_id=category.id, month=7, year=2026, budget_amount="100.00"))
        await session.commit()

        await log_audit_event(
            session, "transaction.created", user_id=owner.id, entity_type="transaction", metadata={}, request=None
        )

        deleted_ids = await hard_delete_expired_accounts(session)
        assert owner.id in deleted_ids

        remaining_budgets = (await session.exec(select(Budget).where(Budget.user_id == owner.id))).all()
        remaining_pms = (await session.exec(select(PaymentMethod).where(PaymentMethod.user_id == owner.id))).all()
        assert remaining_budgets == []
        assert remaining_pms == []

        audit_rows = (await session.exec(select(AuditLog).where(AuditLog.action == "transaction.created"))).all()
        assert len(audit_rows) == 1
        assert audit_rows[0].user_id is None
        assert audit_rows[0].ip_address is None

        still_exists = await session.get(User, owner.id)
        assert still_exists is not None
        assert still_exists.is_active is False

    async def test_ignores_accounts_still_within_grace_period(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        owner.is_active = False
        owner.hard_delete_at = utcnow() + timedelta(days=10)
        session.add(owner)
        await session.commit()

        pm = PaymentMethod(user_id=owner.id, name="Cash", type=PaymentMethodType.CASH)
        session.add(pm)
        await session.commit()

        deleted_ids = await hard_delete_expired_accounts(session)
        assert owner.id not in deleted_ids

        remaining_pms = (await session.exec(select(PaymentMethod).where(PaymentMethod.user_id == owner.id))).all()
        assert len(remaining_pms) == 1

    async def test_ignores_still_active_accounts(self, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        owner.hard_delete_at = utcnow() - timedelta(days=1)
        session.add(owner)
        await session.commit()

        deleted_ids = await hard_delete_expired_accounts(session)
        assert owner.id not in deleted_ids
