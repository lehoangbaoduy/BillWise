from datetime import timedelta

from sqlmodel import select

from app.core.security import generate_token, hash_password, hash_token
from app.models._common import utcnow
from app.models.partner_permission import PartnerInviteToken, PartnerPermission
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


async def _login(client, email, password=VALID_PASSWORD):
    return await client.post("/auth/login", json={"email": email, "password": password})


async def _authed_client(client, session, unique_email):
    user = await _create_verified_owner(session, unique_email)
    await _login(client, unique_email)
    return user


async def _invite(client, email, can_add_transactions=False):
    return await client.post(
        "/household/invite-partner", json={"email": email, "can_add_transactions": can_add_transactions}
    )


async def _make_pending_invite(session, owner, email, can_add_transactions=False, **kwargs):
    defaults = dict(
        invited_by_user_id=owner.id,
        email=email,
        can_add_transactions=can_add_transactions,
        token_hash=hash_token(generate_token()),
        expires_at=utcnow() + timedelta(hours=1),
    )
    defaults.update(kwargs)
    invite = PartnerInviteToken(**defaults)
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite


async def _accept(client, token, email="partner-" + "x", password=VALID_PASSWORD, display_name="Partner Pat"):
    return await client.post(
        "/household/accept-invite", json={"token": token, "password": password, "display_name": display_name}
    )


class TestGetHousehold:
    async def test_requires_authentication(self, client):
        response = await client.get("/household")
        assert response.status_code == 401

    async def test_empty_household(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/household")
        assert response.status_code == 200
        body = response.json()
        assert body["partners"] == []
        assert body["pending_invites"] == []

    async def test_lists_pending_invite(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        await _invite(client, partner_email, can_add_transactions=True)

        response = await client.get("/household")
        body = response.json()
        assert len(body["pending_invites"]) == 1
        assert body["pending_invites"][0]["email"] == partner_email
        assert body["pending_invites"][0]["can_add_transactions"] is True

    async def test_lists_accepted_partner(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, can_add_transactions=True, token_hash=hash_token(token))
        await _accept(client, token, email=partner_email)

        await _login(client, unique_email)
        response = await client.get("/household")
        body = response.json()
        assert body["pending_invites"] == []
        assert len(body["partners"]) == 1
        assert body["partners"][0]["email"] == partner_email
        assert body["partners"][0]["can_add_transactions"] is True
        assert body["partners"][0]["is_active"] is True


class TestInvitePartner:
    async def test_requires_authentication(self, client):
        response = await client.post("/household/invite-partner", json={"email": "a@b.com"})
        assert response.status_code == 401

    async def test_creates_pending_invite(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await _invite(client, "partner-" + unique_email)
        assert response.status_code == 201
        assert response.json()["email"] == "partner-" + unique_email

    async def test_rejects_duplicate_pending_invite(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        await _invite(client, partner_email)
        response = await _invite(client, partner_email)
        assert response.status_code == 409

    async def test_does_not_leak_whether_email_already_registered(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        other_email = "other-" + unique_email
        await _create_verified_owner(session, other_email)
        response = await _invite(client, other_email)
        assert response.status_code == 201

    async def test_accept_still_blocks_duplicate_account_for_already_registered_email(
        self, client, session, unique_email
    ):
        owner = await _authed_client(client, session, unique_email)
        other_email = "other-" + unique_email
        await _create_verified_owner(session, other_email)
        token = generate_token()
        await _make_pending_invite(session, owner, other_email, token_hash=hash_token(token))

        response = await _accept(client, token, email=other_email)
        assert response.status_code == 409

    async def test_allows_reinvite_after_revoke(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        first = await _invite(client, partner_email)
        await client.delete(f"/household/partner/{first.json()['id']}")

        response = await _invite(client, partner_email)
        assert response.status_code == 201


class TestAcceptInvite:
    async def test_rejects_invalid_token(self, client):
        response = await _accept(client, "not-a-real-token")
        assert response.status_code == 400

    async def test_rejects_expired_token(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(
            session, owner, partner_email, token_hash=hash_token(token), expires_at=utcnow() - timedelta(hours=1)
        )
        response = await _accept(client, token, email=partner_email)
        assert response.status_code == 400

    async def test_rejects_already_accepted_token(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, token_hash=hash_token(token))
        first = await _accept(client, token, email=partner_email)
        assert first.status_code == 201

        second = await _accept(client, token, email="second-" + partner_email, display_name="Someone Else")
        assert second.status_code == 400

    async def test_rejects_revoked_token(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        invite = await _make_pending_invite(session, owner, partner_email, token_hash=hash_token(token))
        invite.revoked_at = utcnow()
        session.add(invite)
        await session.commit()

        response = await _accept(client, token, email=partner_email)
        assert response.status_code == 400

    async def test_creates_partner_with_permission_from_invite(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, can_add_transactions=True, token_hash=hash_token(token))

        response = await _accept(client, token, email=partner_email, display_name="Partner Pat")
        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "partner"
        assert body["email"] == partner_email

        partner = (await session.exec(select(User).where(User.email == partner_email))).one()
        assert partner.invited_by_user_id == owner.id
        assert partner.email_verified_at is not None

        permission = (
            await session.exec(select(PartnerPermission).where(PartnerPermission.partner_user_id == partner.id))
        ).one()
        assert permission.can_add_transactions is True

    async def test_accepted_partner_can_log_in(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, token_hash=hash_token(token))
        await _accept(client, token, email=partner_email, password="PartnerPass123")

        response = await _login(client, partner_email, password="PartnerPass123")
        assert response.status_code == 200
        assert response.json()["role"] == "partner"


class TestRemovePartner:
    async def test_requires_authentication(self, client):
        response = await client.delete("/household/partner/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 401

    async def test_404_for_nonexistent_id(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.delete("/household/partner/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_revokes_pending_invite(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        invite_response = await _invite(client, partner_email)
        invite_id = invite_response.json()["id"]

        response = await client.delete(f"/household/partner/{invite_id}")
        assert response.status_code == 204

        household = await client.get("/household")
        assert household.json()["pending_invites"] == []

    async def test_deactivates_accepted_partner_and_blocks_login(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, token_hash=hash_token(token))
        accept_response = await _accept(client, token, email=partner_email, password="PartnerPass123")
        partner_id = accept_response.json()["id"]

        await _login(client, unique_email)
        response = await client.delete(f"/household/partner/{partner_id}")
        assert response.status_code == 204

        login_response = await _login(client, partner_email, password="PartnerPass123")
        assert login_response.status_code == 401

    async def test_404_for_other_owners_partner(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, token_hash=hash_token(token))
        accept_response = await _accept(client, token, email=partner_email)
        partner_id = accept_response.json()["id"]

        other_owner_email = "other-" + unique_email
        await _create_verified_owner(session, other_owner_email)
        await _login(client, other_owner_email)

        response = await client.delete(f"/household/partner/{partner_id}")
        assert response.status_code == 404


class TestUpdatePartnerPermissions:
    async def test_requires_authentication(self, client):
        response = await client.patch(
            "/household/partner/00000000-0000-0000-0000-000000000000/permissions", json={"can_add_transactions": True}
        )
        assert response.status_code == 401

    async def test_updates_permission(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        partner_email = "partner-" + unique_email
        token = generate_token()
        await _make_pending_invite(session, owner, partner_email, can_add_transactions=False, token_hash=hash_token(token))
        accept_response = await _accept(client, token, email=partner_email)
        partner_id = accept_response.json()["id"]

        await _login(client, unique_email)
        response = await client.patch(f"/household/partner/{partner_id}/permissions", json={"can_add_transactions": True})
        assert response.status_code == 200
        assert response.json()["can_add_transactions"] is True

    async def test_404_for_nonexistent_partner(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.patch(
            "/household/partner/00000000-0000-0000-0000-000000000000/permissions", json={"can_add_transactions": True}
        )
        assert response.status_code == 404

    async def test_404_for_owner_id(self, client, session, unique_email):
        owner = await _authed_client(client, session, unique_email)
        response = await client.patch(f"/household/partner/{owner.id}/permissions", json={"can_add_transactions": True})
        assert response.status_code == 404
