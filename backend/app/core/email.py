"""Email delivery abstraction.

MVP ships a console backend (logs the link instead of sending real email) since no
SMTP/SES credentials are configured for this environment. Swapping to a real provider
is a one-file change: implement EmailSender and wire it in via an env-driven factory
here, without touching callers in app/api/auth.py.
"""

import logging
from typing import Protocol

logger = logging.getLogger("billwise.email")


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class ConsoleEmailSender:
    def send(self, to: str, subject: str, body: str) -> None:
        logger.info("EMAIL to=%s subject=%r\n%s", to, subject, body)


def get_email_sender() -> EmailSender:
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
