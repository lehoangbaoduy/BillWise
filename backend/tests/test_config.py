import pytest
from pydantic import ValidationError

from app.core.config import Settings

_REQUIRED = {"database_url": "postgresql+psycopg://x:x@x/x", "secret_key": "test-secret"}


class TestCookieSamesite:
    def test_defaults_to_lax(self):
        settings = Settings(**_REQUIRED)
        assert settings.cookie_samesite == "lax"

    @pytest.mark.parametrize("value", ["lax", "strict", "none", "LAX", " None "])
    def test_accepts_known_values_case_and_whitespace_insensitive(self, value):
        settings = Settings(**_REQUIRED, cookie_samesite=value, cookie_secure=True)
        assert settings.cookie_samesite == value.strip().lower()

    def test_rejects_unknown_value(self):
        with pytest.raises(ValidationError, match="COOKIE_SAMESITE must be one of"):
            Settings(**_REQUIRED, cookie_samesite="invalid")

    def test_rejects_none_without_secure(self):
        with pytest.raises(ValidationError, match="COOKIE_SAMESITE=none requires COOKIE_SECURE=true"):
            Settings(**_REQUIRED, cookie_samesite="none", cookie_secure=False)

    def test_allows_none_with_secure(self):
        settings = Settings(**_REQUIRED, cookie_samesite="none", cookie_secure=True)
        assert settings.cookie_samesite == "none"
        assert settings.cookie_secure is True
