import json
from datetime import date, timedelta

import pytest
from fastapi import HTTPException, status

from app.api import ai_insights as ai_insights_api
from app.core.config import settings
from app.core.security import hash_password
from app.models._common import utcnow
from app.models.ai_insight import AIInsight
from app.models.category import Category, CategoryType
from app.models.payment_method import PaymentMethod, PaymentMethodType
from app.models.user import User, UserRole
from app.services import ai_insight_service

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
    pm = PaymentMethod(user_id=user.id, name="Everyday Card", type=PaymentMethodType.CREDIT_CARD, **kwargs)
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


def _fake_insights(count=2):
    return [
        {
            "insight_type": "cash_flow_change",
            "message": f"Insight {i}",
            "supporting_data": {"n": i},
        }
        for i in range(count)
    ]


class TestGetAIInsights:
    async def test_requires_authentication(self, client):
        response = await client.get("/dashboard/ai-insights")
        assert response.status_code == 401

    async def test_generates_and_persists_on_first_call(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)
        calls = []

        async def _fake_generate(aggregates):
            calls.append(aggregates)
            return _fake_insights(2)

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate)

        response = await client.get("/dashboard/ai-insights")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 2
        assert len(calls) == 1
        # Aggregates handed to the AI are backend-computed numbers only.
        assert "income_expense" in calls[0]
        assert "category_spend_current" in calls[0]

    async def test_second_call_within_a_day_uses_cached_batch(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)
        call_count = 0

        async def _fake_generate(aggregates):
            nonlocal call_count
            call_count += 1
            return _fake_insights(1)

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate)

        first = await client.get("/dashboard/ai-insights")
        second = await client.get("/dashboard/ai-insights")
        assert first.status_code == 200
        assert second.status_code == 200
        assert call_count == 1

    async def test_regenerates_after_the_cache_window_expires(self, client, session, unique_email, monkeypatch):
        user = await _authed_client(client, session, unique_email)
        session.add(
            AIInsight(
                user_id=user.id,
                insight_type="cash_flow_change",
                message="Stale insight",
                supporting_data={},
                generated_at=utcnow() - timedelta(hours=25),
            )
        )
        await session.commit()

        async def _fake_generate(aggregates):
            return _fake_insights(1)

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate)

        response = await client.get("/dashboard/ai-insights")
        assert response.status_code == 200
        assert response.json()[0]["message"] == "Insight 0"

    async def test_dismissed_insights_are_excluded(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)

        async def _fake_generate(aggregates):
            return _fake_insights(2)

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate)

        first_response = await client.get("/dashboard/ai-insights")
        insight_id = first_response.json()[0]["id"]

        dismiss_response = await client.patch(f"/ai-insights/{insight_id}", json={"is_dismissed": True})
        assert dismiss_response.status_code == 200

        second_response = await client.get("/dashboard/ai-insights")
        assert insight_id not in [row["id"] for row in second_response.json()]

    async def test_generation_failure_degrades_gracefully(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)

        async def _fake_generate_failure(aggregates):
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="down")

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate_failure)

        response = await client.get("/dashboard/ai-insights")
        assert response.status_code == 200
        assert response.json() == []

    async def test_audit_log_called_on_generation(self, client, session, unique_email, monkeypatch):
        await _authed_client(client, session, unique_email)
        logged = []

        async def _fake_log_audit_event(session, action, *, user_id, entity_type=None, entity_id=None, metadata=None, request=None):
            logged.append((action, user_id, metadata))

        monkeypatch.setattr(ai_insights_api, "log_audit_event", _fake_log_audit_event)

        async def _fake_generate(aggregates):
            return _fake_insights(3)

        monkeypatch.setattr(ai_insights_api, "generate_insights", _fake_generate)

        await client.get("/dashboard/ai-insights")
        assert len(logged) == 1
        assert logged[0][0] == "ai_insight.generated"
        assert logged[0][2] == {"count": 3}


class TestUpdateAIInsight:
    async def test_requires_authentication(self, client):
        response = await client.patch("/ai-insights/00000000-0000-0000-0000-000000000000", json={"is_dismissed": True})
        assert response.status_code == 401

    async def test_dismisses_and_undismisses(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        insight = AIInsight(user_id=user.id, insight_type="cash_flow_change", message="Test", supporting_data={})
        session.add(insight)
        await session.commit()
        await session.refresh(insight)

        dismiss = await client.patch(f"/ai-insights/{insight.id}", json={"is_dismissed": True})
        assert dismiss.status_code == 200
        assert dismiss.json()["is_dismissed"] is True

        undismiss = await client.patch(f"/ai-insights/{insight.id}", json={"is_dismissed": False})
        assert undismiss.status_code == 200
        assert undismiss.json()["is_dismissed"] is False

    async def test_404_for_other_users_insight(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        insight = AIInsight(user_id=user.id, insight_type="cash_flow_change", message="Test", supporting_data={})
        session.add(insight)
        await session.commit()
        await session.refresh(insight)

        await _create_verified_owner(session, "other-" + unique_email)
        await _login(client, "other-" + unique_email)
        response = await client.patch(f"/ai-insights/{insight.id}", json={"is_dismissed": True})
        assert response.status_code == 404

    async def test_404_for_nonexistent_insight(self, client, session, unique_email):
        await _authed_client(client, session, unique_email)
        response = await client.patch("/ai-insights/00000000-0000-0000-0000-000000000000", json={"is_dismissed": True})
        assert response.status_code == 404


class TestGatherInsightInputs:
    async def test_aggregates_reflect_real_transactions(self, client, session, unique_email):
        user = await _authed_client(client, session, unique_email)
        pm = await _make_payment_method(session, user)
        category = await _make_category(session, user)
        today = date.today()

        await client.post(
            "/transactions",
            json={
                "payment_method_id": str(pm.id),
                "date": today.isoformat(),
                "merchant": "Whole Foods",
                "total_amount": "75.00",
                "transaction_type": "Expense",
                "line_items": [{"category_id": str(category.id), "item_name": "Groceries", "amount": "75.00"}],
            },
        )

        from app.services.insight_aggregation import gather_insight_inputs

        aggregates = await gather_insight_inputs(session, user, today.month, today.year)
        assert aggregates["income_expense"]["current"]["expenses"] == 75.0
        assert any(row["name"] == "Grocery" and row["amount"] == 75.0 for row in aggregates["category_spend_current"])
        assert len(aggregates["monthly_expense_trend"]) == 3


class TestAiInsightService:
    """Unit-level tests against the Anthropic call boundary, mocked at the SDK client."""

    class _FakeTextBlock:
        type = "text"

        def __init__(self, text):
            self.text = text

    class _FakeResponse:
        def __init__(self, text):
            self.content = [TestAiInsightService._FakeTextBlock(text)]

    class _FakeMessages:
        def __init__(self, response_text):
            self._response_text = response_text

        async def create(self, **kwargs):
            return TestAiInsightService._FakeResponse(self._response_text)

    class _FakeAsyncAnthropic:
        def __init__(self, response_text):
            self.messages = TestAiInsightService._FakeMessages(response_text)

    async def test_raises_503_when_api_key_not_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "")
        with pytest.raises(HTTPException) as exc_info:
            await ai_insight_service.generate_insights({})
        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    async def test_filters_out_malformed_insights(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        monkeypatch.setattr(ai_insight_service, "_client_cache", None)
        # No leading "{" — the real call prefills the assistant turn with "{".
        response_json = (
            '"insights": ['
            '{"insight_type": "cash_flow_change", "message": "Valid", "supporting_data": {}},'
            '{"insight_type": "not_a_real_type", "message": "Bad type", "supporting_data": {}},'
            '{"insight_type": "goal_progress", "message": "", "supporting_data": {}}'
            "]}"
        )
        monkeypatch.setattr(
            ai_insight_service,
            "AsyncAnthropic",
            lambda **kwargs: TestAiInsightService._FakeAsyncAnthropic(response_json),
        )
        result = await ai_insight_service.generate_insights({"some": "data"})
        assert len(result) == 1
        assert result[0]["message"] == "Valid"

    async def test_drops_oversized_message_and_caps_oversized_supporting_data(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        monkeypatch.setattr(ai_insight_service, "_client_cache", None)
        oversized_message = "x" * 1500
        oversized_supporting_data = {"padding": "y" * 5000}
        response_json = json.dumps(
            {
                "insights": [
                    {"insight_type": "cash_flow_change", "message": oversized_message, "supporting_data": {}},
                    {
                        "insight_type": "goal_progress",
                        "message": "Fine message",
                        "supporting_data": oversized_supporting_data,
                    },
                ]
            }
        )[1:]  # strip the leading "{" the prefill already supplies
        monkeypatch.setattr(
            ai_insight_service,
            "AsyncAnthropic",
            lambda **kwargs: TestAiInsightService._FakeAsyncAnthropic(response_json),
        )
        result = await ai_insight_service.generate_insights({"some": "data"})
        # Oversized message → whole insight dropped.
        assert not any(item["message"] == oversized_message for item in result)
        # Oversized supporting_data → insight kept, supporting_data reset to {}.
        kept = next(item for item in result if item["message"] == "Fine message")
        assert kept["supporting_data"] == {}

    async def test_raises_502_on_malformed_json_response(self, monkeypatch):
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        monkeypatch.setattr(ai_insight_service, "_client_cache", None)
        monkeypatch.setattr(
            ai_insight_service,
            "AsyncAnthropic",
            lambda **kwargs: TestAiInsightService._FakeAsyncAnthropic("not json at all"),
        )
        with pytest.raises(HTTPException) as exc_info:
            await ai_insight_service.generate_insights({"some": "data"})
        assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
