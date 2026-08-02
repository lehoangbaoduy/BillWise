import logging

from pydantic import field_validator
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


settings = Settings()
