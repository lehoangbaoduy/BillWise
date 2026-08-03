import asyncio
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.core.config import settings
from app.core.email import ConsoleEmailSender, ResendEmailSender, get_email_sender


class TestGetEmailSender:
    def test_returns_console_sender_when_no_api_key(self):
        with patch.object(settings, "resend_api_key", ""):
            assert isinstance(get_email_sender(), ConsoleEmailSender)

    def test_returns_resend_sender_when_api_key_set(self):
        with patch.object(settings, "resend_api_key", "re_test_key"):
            assert isinstance(get_email_sender(), ResendEmailSender)


class TestResendEmailSender:
    def test_sends_via_resend_api(self):
        mock_response = MagicMock(status_code=200)
        mock_response.raise_for_status.return_value = None
        with patch.object(settings, "resend_api_key", "re_test_key"), \
                patch.object(settings, "resend_from_email", "BillWise <onboarding@resend.dev>"), \
                patch("httpx.post", return_value=mock_response) as mock_post:
            ResendEmailSender().send(to="user@example.com", subject="Hi", body="Click: https://x.test/y")

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer re_test_key"
        assert kwargs["json"]["to"] == ["user@example.com"]
        assert kwargs["json"]["subject"] == "Hi"
        assert "https://x.test/y" in kwargs["json"]["html"]

    def test_escapes_html_special_characters_in_body(self):
        mock_response = MagicMock(status_code=200)
        mock_response.raise_for_status.return_value = None
        with patch.object(settings, "resend_api_key", "re_test_key"), \
                patch("httpx.post", return_value=mock_response) as mock_post:
            ResendEmailSender().send(to="user@example.com", subject="Hi", body="<script>alert(1)</script>")

        assert "<script>" not in mock_post.call_args.kwargs["json"]["html"]

    def test_swallows_http_errors_instead_of_raising(self):
        with patch.object(settings, "resend_api_key", "re_test_key"), \
                patch("httpx.post", side_effect=httpx.ConnectError("boom")):
            # Must not raise — a failed send happens after the caller (e.g.
            # registration) already committed its own success.
            ResendEmailSender().send(to="user@example.com", subject="Hi", body="body")

    def test_swallows_non_2xx_response_instead_of_raising(self):
        mock_response = MagicMock(status_code=403)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "403", request=MagicMock(), response=mock_response
        )
        with patch.object(settings, "resend_api_key", "re_test_key"), \
                patch("httpx.post", return_value=mock_response):
            ResendEmailSender().send(to="user@example.com", subject="Hi", body="body")

    def test_offloads_to_executor_instead_of_blocking_event_loop(self):
        # send() is called synchronously (not awaited) from async route
        # handlers — a blocking httpx.post() there would stall every other
        # concurrent request. Inside a running event loop, it must hand off
        # to a thread instead of calling httpx.post() inline.
        with patch.object(settings, "resend_api_key", "re_test_key"), \
                patch("httpx.post") as mock_post:
            async def run():
                ResendEmailSender().send(to="user@example.com", subject="Hi", body="body")
                # Give the executor thread a moment to run.
                await asyncio.sleep(0.2)

            asyncio.run(run())

        mock_post.assert_called_once()
