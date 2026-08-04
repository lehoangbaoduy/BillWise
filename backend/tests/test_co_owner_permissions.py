"""Co-owner partners get full financial-data privileges (budgets, goals, etc.)
but never household-admin powers (inviting/removing partners) — see PRD
discussion in household.py. These tests exercise that boundary end-to-end
through the invite -> accept -> authorize pipeline, rather than unit-testing
require_owner_or_co_owner in isolation, since the boundary is only meaningful
as observed through the actual endpoints."""
from app.core.security import generate_token, hash_password, hash_token
from app.models._common import utcnow
from app.models.category import Category, CategoryType
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


async def _make_category(session, owner):
    category = Category(user_id=owner.id, name="Grocery", category_type=CategoryType.EXPENSE)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def _invite_and_accept(client, session, owner, email, is_co_owner):
    token = generate_token()
    from app.models.partner_permission import PartnerInviteToken
    from datetime import timedelta

    invite = PartnerInviteToken(
        invited_by_user_id=owner.id,
        email=email,
        can_add_transactions=False,
        is_co_owner=is_co_owner,
        token_hash=hash_token(token),
        expires_at=utcnow() + timedelta(hours=1),
    )
    session.add(invite)
    await session.commit()

    response = await client.post(
        "/household/accept-invite",
        json={"token": token, "password": VALID_PASSWORD, "display_name": "Partner Pat"},
    )
    assert response.status_code == 201
    return response.json()["id"]


class TestCoOwnerFinancialAccess:
    async def test_co_owner_can_create_budget(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        partner_email = "partner-" + unique_email
        await _invite_and_accept(client, session, owner, partner_email, is_co_owner=True)

        await _login(client, partner_email)
        response = await client.post(
            "/budgets",
            json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "500.00"},
        )
        assert response.status_code == 201

    async def test_non_co_owner_partner_cannot_create_budget(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        partner_email = "partner-" + unique_email
        await _invite_and_accept(client, session, owner, partner_email, is_co_owner=False)

        await _login(client, partner_email)
        response = await client.post(
            "/budgets",
            json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "500.00"},
        )
        assert response.status_code == 403

    async def test_co_owner_budget_is_scoped_to_household_owner_not_partner(self, client, session, unique_email):
        """The budget row's user_id (the storage/scoping key) is always the
        household owner's id, never the co-owner's own id -- that part of
        "scoped to household owner" is unconditional. But *visibility* is
        creator-based (see item_visibility.py): a budget the co-owner creates
        without explicitly sharing it defaults private, so it's invisible to
        the owner until the co-owner marks it shared."""
        owner = await _create_verified_owner(session, unique_email)
        category = await _make_category(session, owner)
        partner_email = "partner-" + unique_email
        await _invite_and_accept(client, session, owner, partner_email, is_co_owner=True)

        await _login(client, partner_email)
        create_response = await client.post(
            "/budgets",
            json={"category_id": str(category.id), "month": 6, "year": 2026, "budget_amount": "500.00"},
        )
        assert create_response.status_code == 201
        budget_id = create_response.json()["id"]

        await _login(client, unique_email)
        owner_view = await client.get("/budgets?month=6&year=2026")
        assert owner_view.status_code == 200
        assert owner_view.json() == []

        await _login(client, partner_email)
        share_response = await client.patch(f"/budgets/{budget_id}/sharing", json={"is_shared": True})
        assert share_response.status_code == 200

        await _login(client, unique_email)
        owner_view_after_share = await client.get("/budgets?month=6&year=2026")
        assert owner_view_after_share.status_code == 200
        assert len(owner_view_after_share.json()) == 1
        assert owner_view_after_share.json()[0]["id"] == budget_id


class TestCoOwnerCannotAdministerHousehold:
    async def test_co_owner_cannot_invite_partners(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        await _invite_and_accept(client, session, owner, partner_email, is_co_owner=True)

        await _login(client, partner_email)
        response = await client.post(
            "/household/invite-partner", json={"email": "someone-else-" + unique_email, "can_add_transactions": False}
        )
        assert response.status_code == 403

    async def test_co_owner_cannot_remove_partners(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        partner_id = await _invite_and_accept(client, session, owner, partner_email, is_co_owner=True)

        await _login(client, partner_email)
        response = await client.delete(f"/household/partner/{partner_id}")
        assert response.status_code == 403

    async def test_co_owner_cannot_view_household_summary(self, client, session, unique_email):
        owner = await _create_verified_owner(session, unique_email)
        partner_email = "partner-" + unique_email
        await _invite_and_accept(client, session, owner, partner_email, is_co_owner=True)

        await _login(client, partner_email)
        response = await client.get("/household")
        assert response.status_code == 403
