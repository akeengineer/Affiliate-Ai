"""Telegram Bot API notification client."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramBotError(RuntimeError):
    """Raised when Telegram cannot accept a message."""


class TelegramBotClient:
    """Send already-formatted MarkdownV2 messages with Telegram Bot API."""

    DEFAULT_API_BASE_URL = "https://api.telegram.org"

    def __init__(
        self,
        token: str | None = None,
        chat_id: str | None = None,
        *,
        token_env: str = "TELEGRAM_BOT_TOKEN",
        chat_id_env: str = "TELEGRAM_CHAT_ID",
        api_base_url: str = DEFAULT_API_BASE_URL,
        timeout: float = 10.0,
    ) -> None:
        self.token = token if token is not None else os.getenv(token_env)
        self.chat_id = chat_id if chat_id is not None else os.getenv(chat_id_env)
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout = timeout

    def send(self, message: str) -> int:
        """Send one MarkdownV2 message and return its HTTP status code."""
        if not self.token or not self.chat_id:
            raise TelegramBotError("Telegram bot is not configured")
        if not message.strip():
            raise TelegramBotError("Telegram message cannot be empty")

        payload = json.dumps(
            {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "MarkdownV2",
                "link_preview_options": {"is_disabled": True},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        url = f"{self.api_base_url}/bot{self.token}/sendMessage"
        request = Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - configured HTTPS API
                status = int(response.status)
                body = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise TelegramBotError(f"Telegram request failed with HTTP status {exc.code}") from None
        except (URLError, TimeoutError):
            raise TelegramBotError("Telegram request could not be completed") from None

        if not 200 <= status < 300:
            raise TelegramBotError(f"Telegram request failed with HTTP status {status}")
        try:
            response_data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            response_data = {}
        if response_data.get("ok") is False:
            raise TelegramBotError("Telegram rejected the message")
        return status

    def send_message(self, message: str) -> int:
        """Compatibility alias for callers that use ``send_message``."""
        return self.send(message)


def send_telegram_message(message: str) -> int:
    """Send with ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID``."""
    return TelegramBotClient().send(message)
