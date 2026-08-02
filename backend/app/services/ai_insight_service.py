"""Generates AI Insights (PRD §19) from backend-computed aggregates via Anthropic
Claude Haiku. Only the aggregate JSON built by insight_aggregation.py is ever sent
here — never raw transaction rows (PRD §19.3/§29.3). Kept independent of
app.services.ai_structuring_service (OCR structuring) — different feature, different
prompt/failure-handling needs; not worth coupling two unrelated call sites together."""

import json
import logging

from anthropic import AsyncAnthropic
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.ai_insight import AIInsightType

logger = logging.getLogger("billwise.ai_insight")

_MODEL = "claude-haiku-4-5-20251001"
_CLIENT_TIMEOUT_SECONDS = 20.0
_MAX_INSIGHTS = 6
_MAX_MESSAGE_LENGTH = 1000
# Guards against a malformed/oversized AI response bloating the JSON column —
# the AI is semi-trusted input (its output isn't attacker-controlled the way
# direct user input is, but this app doesn't control what Anthropic returns).
_MAX_SUPPORTING_DATA_JSON_LENGTH = 4000

_SYSTEM_PROMPT = f"""You are a personal finance insight generator. You will be given a JSON
object of pre-computed spending aggregates for one user — totals, category breakdowns, budget
status, cashback, recurring bills, and savings goal progress. You do not have access to any
other data.

Generate up to {_MAX_INSIGHTS} short, concrete insights a person would find useful. Rules:
- Use ONLY the numbers given to you. Never invent or estimate a number not present in the input.
- Never give investment advice or recommend specific financial products.
- Each insight must explain *why* it's being shown, referencing the specific numbers behind it.
- Skip categories of insight where the input data doesn't support one (e.g. no budgets set,
  fewer than 2 months of trend data) rather than inventing something.

Respond with ONLY a JSON object matching this exact shape — no prose, no markdown fences:
{{
  "insights": [
    {{
      "insight_type": string, one of {sorted(t.value for t in AIInsightType)},
      "message": string,
      "supporting_data": object, a small object copied from the numbers you used, not new ones
    }}
  ]
}}"""


_client_cache: AsyncAnthropic | None = None


def _client() -> AsyncAnthropic:
    global _client_cache
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI Insights are not configured")
    if _client_cache is None:
        _client_cache = AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=_CLIENT_TIMEOUT_SECONDS)
    return _client_cache


def _parse_json_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").strip()
    if text.endswith("```"):
        text = text.removesuffix("```").strip()
    return json.loads(text)


def _coerce_insight(item: dict) -> dict | None:
    insight_type = item.get("insight_type")
    message = item.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > _MAX_MESSAGE_LENGTH:
        return None
    if insight_type not in {t.value for t in AIInsightType}:
        return None
    supporting_data = item.get("supporting_data")
    if not isinstance(supporting_data, dict) or len(json.dumps(supporting_data)) > _MAX_SUPPORTING_DATA_JSON_LENGTH:
        supporting_data = {}
    return {"insight_type": insight_type, "message": message, "supporting_data": supporting_data}


async def generate_insights(aggregates: dict) -> list[dict]:
    """Returns a list of {insight_type, message, supporting_data} dicts, already
    filtered to well-formed entries. Raises HTTPException(503/502) if the AI call
    itself is unavailable or fails — callers decide whether to degrade gracefully."""
    client = _client()
    try:
        response = await client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": json.dumps(aggregates, default=str)},
                {"role": "assistant", "content": "{"},
            ],
        )
    except Exception as exc:
        logger.warning("Anthropic insight generation call failed: %s", type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI Insight generation failed") from exc

    raw = "{" + "".join(block.text for block in response.content if block.type == "text")
    try:
        parsed = _parse_json_response(raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Anthropic returned non-JSON insight output (%d chars)", len(raw))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI Insight generation failed") from None

    raw_items = parsed.get("insights", [])
    if not isinstance(raw_items, list):
        return []
    coerced = [_coerce_insight(item) for item in raw_items[:_MAX_INSIGHTS]]
    return [item for item in coerced if item is not None]
