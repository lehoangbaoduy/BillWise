import logging

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("billwise.config")

_KNOWN_DEV_SECRET = "local-dev-only-secret-3f8a9c2e1b7d4f60a5c9e2b1d8f74a30"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60 * 24 * 7
    email_verification_token_expire_hours: int = 48
    password_reset_token_expire_minutes: int = 30
    partner_invite_token_expire_hours: int = 24 * 7
    export_token_expire_minutes: int = 15
    cookie_name: str = "billwise_session"
    cookie_secure: bool = True
    # "lax" works for local dev (localhost:3000 <-> localhost:8000 are same-site)
    # and same-registrable-domain deployments. Cross-site deployments (e.g.
    # Vercel frontend + Render backend, different registrable domains) need
    # "none" — browsers never attach a Lax cookie to cross-site fetch/XHR
    # (only to top-level navigations), so auth would silently fail past login.
    cookie_samesite: str = "lax"
    frontend_base_url: str = "http://localhost:3000"
    login_rate_limit_window: str = "5/minute"
    password_reset_rate_limit_window: str = "3/hour"
    anthropic_api_key: str = ""
    ocr_rate_limit_window: str = "20/hour"
    ocr_timeout_seconds: int = 40
    ocr_max_upload_bytes: int = 10 * 1024 * 1024
    account_deletion_token_expire_minutes: int = 30
    account_deletion_rate_limit_window: str = "3/hour"
    account_deletion_grace_period_days: int = 30
    # Defense-in-depth for the dashboard/notifications read endpoints, which
    # were previously unthrottled. Generous relative to real usage (the
    # notifications header badge polls once/minute); this is a ceiling
    # against abuse, not a UX-affecting limit.
    read_rate_limit_window: str = "120/minute"
    # Empty by default -> app/core/email.py falls back to logging the email
    # instead of sending it (fine for local dev). Set to send real email via
    # Resend's HTTP API.
    resend_api_key: str = ""
    resend_from_email: str = "BillWise <onboarding@resend.dev>"
    # Empty by default -> receipt_storage_service raises a 503 at first use
    # (same lazy-validation pattern as anthropic_api_key) rather than blocking
    # app startup for households that haven't provisioned R2 yet.
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""

    @field_validator("frontend_base_url")
    @classmethod
    def _reject_wildcard_origin(cls, value: str) -> str:
        # CORS below is credentialed (allow_credentials=True) — a wildcard origin
        # combined with credentials would let any site read authenticated responses.
        if value.strip() in ("", "*"):
            raise ValueError("FRONTEND_BASE_URL must be a specific origin, not empty or '*'")
        return value

    @field_validator("secret_key")
    @classmethod
    def _warn_on_known_dev_secret(cls, value: str) -> str:
        if value == _KNOWN_DEV_SECRET:
            logger.warning(
                "SECRET_KEY is the checked-in dev placeholder — every session token is "
                "forgeable by anyone who has read this repo. Fine for local dev; "
                "generate a real value (see backend/.env.example) before any shared or "
                "internet-facing deployment."
            )
        return value

    @field_validator("cookie_samesite")
    @classmethod
    def _validate_samesite(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ("lax", "strict", "none"):
            raise ValueError("COOKIE_SAMESITE must be one of: lax, strict, none")
        return normalized

    @model_validator(mode="after")
    def _reject_insecure_samesite_none(self) -> "Settings":
        # Browsers silently drop SameSite=None cookies that aren't also Secure.
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("COOKIE_SAMESITE=none requires COOKIE_SECURE=true")
        return self


settings = Settings()
