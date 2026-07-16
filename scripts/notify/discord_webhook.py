"""Discord incoming-webhook notification client."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class DiscordWebhookError(RuntimeError):
    """Raised when Discord cannot accept a webhook payload."""


class DiscordWebhookClient:
    """Send a preformatted embed payload to a Discord webhook."""

    def __init__(
        self,
        webhook_url: str | None = None,
        *,
        webhook_url_env: str = "DISCORD_WEBHOOK_URL",
        timeout: float = 10.0,
    ) -> None:
        self.webhook_url = webhook_url if webhook_url is not None else os.getenv(webhook_url_env)
        self.timeout = timeout

    def send(self, payload: Mapping[str, Any]) -> int:
        """Send one webhook payload and return its HTTP status code."""
        if not self.webhook_url:
            raise DiscordWebhookError("Discord webhook is not configured")
        parsed_url = urlparse(self.webhook_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise DiscordWebhookError("Discord webhook URL is invalid")
        if not payload:
            raise DiscordWebhookError("Discord webhook payload cannot be empty")

        request = Request(
            self.webhook_url,
            data=json.dumps(dict(payload), ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - env-provided webhook URL
                status = int(response.status)
                response.read()
        except HTTPError as exc:
            raise DiscordWebhookError(f"Discord request failed with HTTP status {exc.code}") from None
        except (URLError, TimeoutError):
            raise DiscordWebhookError("Discord request could not be completed") from None

        if not 200 <= status < 300:
            raise DiscordWebhookError(f"Discord request failed with HTTP status {status}")
        return status

    def send_message(self, payload: Mapping[str, Any]) -> int:
        """Compatibility alias for callers that use ``send_message``."""
        return self.send(payload)


def send_discord_webhook(payload: Mapping[str, Any]) -> int:
    """Send a Discord payload using ``DISCORD_WEBHOOK_URL``."""
    return DiscordWebhookClient().send(payload)
