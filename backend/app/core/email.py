"""Email delivery abstraction.

Falls back to a console backend (logs the link instead of sending real email)
when RESEND_API_KEY isn't set, which keeps local dev working with zero signup.
Set RESEND_API_KEY to send real email via Resend's HTTP API.
"""

import asyncio
import html
import logging
from typing import Protocol

import httpx

from app.core.config import settings

logger = logging.getLogger("billwise.email")

_RESEND_API_URL = "https://api.resend.com/emails"


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class ConsoleEmailSender:
    def send(self, to: str, subject: str, body: str) -> None:
        logger.info("EMAIL to=%s subject=%r\n%s", to, subject, body)


class ResendEmailSender:
    """A failed send must never break the caller (registration/login/etc.
    already succeeded by the time an email goes out) — errors are logged, not
    raised. See DEPLOYMENT.md for the resend.dev sandbox-domain restriction
    (testing only; only deliverable to the Resend account's own address until
    a custom domain is verified)."""

    def send(self, to: str, subject: str, body: str) -> None:
        # Callers (send_verification_email et al.) are plain sync functions
        # invoked from async route handlers without awaiting — a blocking
        # httpx.post() here would stall the whole event loop for up to the
        # request timeout. Offload to a thread when a loop is running; fall
        # back to an inline call otherwise (scripts, tests).
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self._send_sync(to, subject, body)
            return
        loop.run_in_executor(None, self._send_sync, to, subject, body)

    def _send_sync(self, to: str, subject: str, body: str) -> None:
        try:
            response = httpx.post(
                _RESEND_API_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.resend_from_email,
                    "to": [to],
                    "subject": subject,
                    "html": f"<p>{html.escape(body).replace(chr(10), '<br>')}</p>",
                },
                timeout=10,
            )
            response.raise_for_status()
        except Exception:
            logger.exception("Resend email send failed to=%s subject=%r", to, subject)


def get_email_sender() -> EmailSender:
    if settings.resend_api_key:
        return ResendEmailSender()
    return ConsoleEmailSender()


def send_verification_email(to: str, verify_url: str) -> None:
    get_email_sender().send(
        to=to,
        subject="Verify your BillWise email",
        body=f"Click to verify your email: {verify_url}",
    )


def send_password_reset_email(to: str, reset_url: str) -> None:
    get_email_sender().send(
        to=to,
        subject="Reset your BillWise password",
        body=f"Click to reset your password: {reset_url}",
    )


def send_partner_invite_email(to: str, accept_url: str) -> None:
    get_email_sender().send(
        to=to,
        subject="You've been invited to a BillWise household",
        body=f"Click to accept and set your password: {accept_url}",
    )


def send_account_deletion_email(to: str, confirm_url: str) -> None:
    get_email_sender().send(
        to=to,
        subject="Confirm BillWise account deletion",
        body=f"Click to confirm deleting your BillWise account and household: {confirm_url}",
    )
