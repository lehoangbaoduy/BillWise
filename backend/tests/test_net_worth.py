from decimal import Decimal

from app.core.security import hash_password
from app.models._common import utcnow
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


async def _make_account(client, name="Checking", type_="asset"):
    response = await client.post("/net-worth-accounts", json={"name": name, "type": type_})
    assert response.status_code == 201
    return response.json()


class TestListCreateNetWorthAccounts:
    async def test_requires_authentication(self, client):
        response = await client.get("/net-worth-accounts")
        assert response.status_code == 401

    async def test_creates_asset_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        body = await _make_account(client, name="Checking", type_="asset")
        assert body["name"] == "Checking"
        assert body["type"] == "asset"
        assert body["is_active"] is True

    async def test_creates_liability_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        body = await _make_account(client, name="Credit Card", type_="liability")
        assert body["type"] == "liability"

    async def test_rejects_invalid_type(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post("/net-worth-accounts", json={"name": "Mystery", "type": "gold"})
        assert response.status_code == 422

    async def test_lists_only_own_active_accounts(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        await _make_account(client, name="Checking")
        account_2 = await _make_account(client, name="Savings")
        await client.delete(f"/net-worth-accounts/{account_2['id']}")

        other = await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        await _make_account(client, name="Other's account")

        await _login(client, unique_email)
        response = await client.get("/net-worth-accounts")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "Checking"


class TestUpdateDeleteNetWorthAccount:
    async def test_updates_name(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        account = await _make_account(client)
        response = await client.patch(f"/net-worth-accounts/{account['id']}", json={"name": "Renamed"})
        assert response.status_code == 200
        assert response.json()["name"] == "Renamed"

    async def test_rejects_clearing_name(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        account = await _make_account(client)
        response = await client.patch(f"/net-worth-accounts/{account['id']}", json={"name": None})
        assert response.status_code == 422

    async def test_404_for_other_users_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        account = await _make_account(client)
        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        response = await client.patch(f"/net-worth-accounts/{account['id']}", json={"name": "Hijacked"})
        assert response.status_code == 404

    async def test_deactivates_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        account = await _make_account(client)
        response = await client.delete(f"/net-worth-accounts/{account['id']}")
        assert response.status_code == 204

        list_response = await client.get("/net-worth-accounts")
        assert list_response.json() == []

    async def test_404_when_updating_deactivated_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        account = await _make_account(client)
        await client.delete(f"/net-worth-accounts/{account['id']}")
        response = await client.patch(f"/net-worth-accounts/{account['id']}", json={"name": "Zombie"})
        assert response.status_code == 404


class TestCreateNetWorthSnapshot:
    async def test_requires_authentication(self, client):
        response = await client.post("/net-worth-snapshots", json={})
        assert response.status_code == 401

    async def test_rejects_snapshot_with_no_active_accounts(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.post(
            "/net-worth-snapshots", json={"snapshot_date": "2026-06-30", "balances": [{"account_id": "00000000-0000-0000-0000-000000000000", "balance": "1"}]}
        )
        assert response.status_code == 422

    async def test_rejects_incomplete_snapshot_missing_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        await _make_account(client, name="Checking", type_="asset")
        await _make_account(client, name="Credit Card", type_="liability")
        checking_only_response = await client.post("/net-worth-accounts", json={"name": "Savings", "type": "asset"})
        savings = checking_only_response.json()

        response = await client.post(
            "/net-worth-snapshots",
            json={"snapshot_date": "2026-06-30", "balances": [{"account_id": savings["id"], "balance": "100.00"}]},
        )
        assert response.status_code == 422
        assert "missing balances" in response.json()["detail"]

    async def test_rejects_snapshot_with_unknown_account(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        response = await client.post(
            "/net-worth-snapshots",
            json={
                "snapshot_date": "2026-06-30",
                "balances": [
                    {"account_id": checking["id"], "balance": "100.00"},
                    {"account_id": "00000000-0000-0000-0000-000000000000", "balance": "5.00"},
                ],
            },
        )
        assert response.status_code == 422
        assert "unknown or inactive accounts" in response.json()["detail"]

    async def test_computes_totals_from_asset_and_liability_accounts(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        credit_card = await _make_account(client, name="Credit Card", type_="liability")

        response = await client.post(
            "/net-worth-snapshots",
            json={
                "snapshot_date": "2026-06-30",
                "notes": "End of June",
                "balances": [
                    {"account_id": checking["id"], "balance": "5000.00"},
                    {"account_id": credit_card["id"], "balance": "1200.00"},
                ],
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["total_assets"] == "5000.00"
        assert body["total_liabilities"] == "1200.00"
        assert body["net_worth"] == "3800.00"
        assert body["notes"] == "End of June"
        assert len(body["balances"]) == 2

    async def test_deactivated_account_excluded_from_required_set(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        old_account = await _make_account(client, name="Old Wallet", type_="asset")
        await client.delete(f"/net-worth-accounts/{old_account['id']}")

        response = await client.post(
            "/net-worth-snapshots",
            json={"snapshot_date": "2026-06-30", "balances": [{"account_id": checking["id"], "balance": "500.00"}]},
        )
        assert response.status_code == 201


class TestListNetWorthSnapshots:
    async def test_requires_authentication(self, client):
        response = await client.get("/net-worth-snapshots")
        assert response.status_code == 401

    async def test_lists_only_own_snapshots_ordered_by_date(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        await client.post(
            "/net-worth-snapshots", json={"snapshot_date": "2026-06-30", "balances": [{"account_id": checking["id"], "balance": "5000"}]}
        )
        await client.post(
            "/net-worth-snapshots", json={"snapshot_date": "2026-05-31", "balances": [{"account_id": checking["id"], "balance": "4000"}]}
        )

        other = await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        other_account = await _make_account(client, name="Other Checking", type_="asset")
        await client.post(
            "/net-worth-snapshots", json={"snapshot_date": "2026-06-30", "balances": [{"account_id": other_account["id"], "balance": "1"}]}
        )

        await _login(client, unique_email)
        response = await client.get("/net-worth-snapshots")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert body[0]["snapshot_date"] == "2026-05-31"
        assert body[1]["snapshot_date"] == "2026-06-30"

    async def test_empty_when_no_snapshots(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/net-worth-snapshots")
        assert response.status_code == 200
        assert response.json() == []


class TestNetWorthDashboard:
    async def test_requires_authentication(self, client):
        response = await client.get("/dashboard/net-worth")
        assert response.status_code == 401

    async def test_empty_state_when_no_snapshots(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.get("/dashboard/net-worth")
        assert response.status_code == 200
        body = response.json()
        assert body["current_net_worth"] is None
        assert body["breakdown"] == []
        assert body["history"] == []

    async def test_change_vs_previous_with_two_snapshots(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        await client.post(
            "/net-worth-snapshots",
            json={"snapshot_date": "2026-05-31", "balances": [{"account_id": checking["id"], "balance": "4000.00"}]},
        )
        await client.post(
            "/net-worth-snapshots",
            json={"snapshot_date": "2026-06-30", "balances": [{"account_id": checking["id"], "balance": "5000.00"}]},
        )

        response = await client.get("/dashboard/net-worth")
        assert response.status_code == 200
        body = response.json()
        assert body["current_net_worth"] == "5000.00"
        assert body["change_vs_previous"] == "1000.00"
        assert len(body["history"]) == 2
        assert len(body["breakdown"]) == 1

    async def test_change_vs_previous_null_with_single_snapshot(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        checking = await _make_account(client, name="Checking", type_="asset")
        await client.post(
            "/net-worth-snapshots",
            json={"snapshot_date": "2026-06-30", "balances": [{"account_id": checking["id"], "balance": "5000.00"}]},
        )

        response = await client.get("/dashboard/net-worth")
        assert response.status_code == 200
        assert response.json()["change_vs_previous"] is None


class TestPartnerForbidden:
    """PRD §21.4: net worth stays owner-only regardless of sharing."""

    async def test_partner_cannot_list_net_worth_accounts(self, client, session, unique_email):
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

        response = await client.get("/net-worth-accounts")
        assert response.status_code == 403

    async def test_partner_cannot_view_net_worth_dashboard(self, client, session, unique_email):
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

        response = await client.get("/dashboard/net-worth")
        assert response.status_code == 403
