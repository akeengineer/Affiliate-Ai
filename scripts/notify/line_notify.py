"""Legacy LINE Notify API client.

LINE terminated this API on 2025-03-31. The client remains here to satisfy
task 007's interface and fails cleanly so other configured channels can send.
"""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class LineNotifyError(RuntimeError):
    """Raised when LINE Notify cannot accept a message."""


class LineNotifyClient:
    """Send already-formatted text through the legacy LINE Notify endpoint."""

    DEFAULT_API_URL = "https://notify-api.line.me/api/notify"

    def __init__(
        self,
        token: str | None = None,
        *,
        token_env: str = "LINE_NOTIFY_TOKEN",
        api_url: str = DEFAULT_API_URL,
        timeout: float = 10.0,
    ) -> None:
        self.token = token if token is not None else os.getenv(token_env)
        self.api_url = api_url
        self.timeout = timeout

    def send(self, message: str) -> int:
        """Send one message and return the successful HTTP status code."""
        if not self.token:
            raise LineNotifyError("LINE Notify is not configured")
        if not message.strip():
            raise LineNotifyError("LINE Notify message cannot be empty")

        request = Request(
            self.api_url,
            data=urlencode({"message": message}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - fixed/configured HTTPS API
                status = int(response.status)
                body = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise LineNotifyError(f"LINE Notify request failed with HTTP status {exc.code}") from None
        except (URLError, TimeoutError):
            raise LineNotifyError("LINE Notify request could not be completed") from None

        if not 200 <= status < 300:
            raise LineNotifyError(f"LINE Notify request failed with HTTP status {status}")
        if body:
            try:
                response_data = json.loads(body)
            except json.JSONDecodeError:
                response_data = {}
            if response_data.get("status", status) != 200:
                raise LineNotifyError("LINE Notify rejected the message")
        return status

    def send_message(self, message: str) -> int:
        """Compatibility alias for callers that use ``send_message``."""
        return self.send(message)


def send_line_notification(message: str) -> int:
    """Send a LINE notification using ``LINE_NOTIFY_TOKEN``."""
    return LineNotifyClient().send(message)
