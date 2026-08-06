from datetime import timedelta

from sqlmodel import select

from app.core.security import generate_token, hash_token
from app.models._common import utcnow
from app.models.category import Category
from app.models.user import EmailVerificationToken, PasswordResetToken, User

VALID_PASSWORD = "StrongPass123"


async def _register(client, email, password=VALID_PASSWORD, display_name="Jamie Owner"):
    return await client.post(
        "/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )


async def _verify(session, client, email):
    user = (await session.exec(select(User).where(User.email == email))).one()
    token = generate_token()
    session.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=utcnow() + timedelta(hours=1),
        )
    )
    await session.commit()
    return await client.post("/auth/verify-email", json={"token": token})


async def _register_and_verify(client, session, email, password=VALID_PASSWORD):
    await _register(client, email, password=password)
    await _verify(session, client, email)


class TestRegister:
    async def test_creates_unverified_owner(self, client, session, unique_email):
        response = await _register(client, unique_email)
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == unique_email
        assert body["role"] == "owner"
        assert "password_hash" not in body
        assert "password" not in body

        user = (await session.exec(select(User).where(User.email == unique_email))).one()
        assert user.email_verified_at is None

    async def test_seeds_default_categories_for_new_owner(self, client, session, unique_email):
        await _register(client, unique_email)
        user = (await session.exec(select(User).where(User.email == unique_email))).one()
        categories = (await session.exec(select(Category).where(Category.user_id == user.id))).all()
        names = {c.name for c in categories}
        assert "Housing" in names
        assert "Income" in names
        assert all(c.is_default for c in categories)
        assert all(c.is_shared is True for c in categories)

    async def test_duplicate_email_rejected(self, client, unique_email):
        first = await _register(client, unique_email)
        assert first.status_code == 201
        second = await _register(client, unique_email)
        assert second.status_code == 409

    async def test_weak_password_rejected(self, client, unique_email):
        response = await _register(client, unique_email, password="short")
        assert response.status_code == 422

    async def test_password_without_digit_rejected(self, client, unique_email):
        response = await _register(client, unique_email, password="alllettersnodigits")
        assert response.status_code == 422

    async def test_password_without_letter_rejected(self, client, unique_email):
        response = await _register(client, unique_email, password="12345678")
        assert response.status_code == 422

    async def test_invite_token_registration_not_yet_available(self, client, unique_email):
        response = await client.post(
            "/auth/register",
            json={
                "email": unique_email,
                "password": VALID_PASSWORD,
                "display_name": "Partner",
                "invite_token": "whatever",
            },
        )
        assert response.status_code == 400


class TestVerifyEmail:
    async def test_valid_token_marks_verified(self, client, session, unique_email):
        await _register(client, unique_email)
        response = await _verify(session, client, unique_email)
        assert response.status_code == 200
        assert response.json()["verified"] is True

        user = (await session.exec(select(User).where(User.email == unique_email))).one()
        assert user.email_verified_at is not None

    async def test_invalid_token_rejected(self, client, unique_email):
        await _register(client, unique_email)
        response = await client.post("/auth/verify-email", json={"token": "not-a-real-token"})
        assert response.status_code == 400


class TestLogin:
    async def test_unverified_user_cannot_login(self, client, unique_email):
        await _register(client, unique_email)
        response = await client.post("/auth/login", json={"email": unique_email, "password": VALID_PASSWORD})
        assert response.status_code == 403

    async def test_correct_credentials_set_session_cookie(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        response = await client.post("/auth/login", json={"email": unique_email, "password": VALID_PASSWORD})
        assert response.status_code == 200
        assert "billwise_session" in response.cookies
        assert "password" not in response.text

    async def test_wrong_password_rejected(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        response = await client.post("/auth/login", json={"email": unique_email, "password": "WrongPass123"})
        assert response.status_code == 401

    async def test_rate_limited_after_repeated_failures(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        for _ in range(5):
            await client.post("/auth/login", json={"email": unique_email, "password": "WrongPass123"})
        response = await client.post("/auth/login", json={"email": unique_email, "password": "WrongPass123"})
        assert response.status_code == 429


class TestMe:
    async def test_requires_authentication(self, client):
        response = await client.get("/auth/me")
        assert response.status_code == 401

    async def test_returns_current_user_when_logged_in(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        await client.post("/auth/login", json={"email": unique_email, "password": VALID_PASSWORD})
        response = await client.get("/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == unique_email


class TestLogout:
    async def test_clears_session_cookie(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        await client.post("/auth/login", json={"email": unique_email, "password": VALID_PASSWORD})
        response = await client.post("/auth/logout")
        assert response.status_code == 200
        me_response = await client.get("/auth/me")
        assert me_response.status_code == 401


class TestPasswordReset:
    async def test_request_always_returns_202_even_for_unknown_email(self, client):
        response = await client.post("/auth/password-reset/request", json={"email": "nobody@example.com"})
        assert response.status_code == 202

    async def test_confirm_with_valid_token_changes_password(self, client, session, unique_email):
        await _register_and_verify(client, session, unique_email)
        user = (await session.exec(select(User).where(User.email == unique_email))).one()

        token = generate_token()
        session.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=utcnow() + timedelta(minutes=30),
            )
        )
        await session.commit()

        response = await client.post(
            "/auth/password-reset/confirm", json={"token": token, "new_password": "NewStrongPass123"}
        )
        assert response.status_code == 200

        login_response = await client.post(
            "/auth/login", json={"email": unique_email, "password": "NewStrongPass123"}
        )
        assert login_response.status_code == 200
