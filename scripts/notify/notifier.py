#!/usr/bin/env python3
"""Unified LINE, Telegram, and Discord notification dispatcher.

Usage:
    python scripts/notify/notifier.py --type morning_report --input report.md
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

try:
    from .discord_webhook import DiscordWebhookClient
    from .formatters import MESSAGE_TYPES, extract_full_report_url, format_message
    from .line_notify import LineNotifyClient
    from .telegram_bot import TelegramBotClient
except ImportError:  # Support direct execution: python scripts/notify/notifier.py
    from discord_webhook import DiscordWebhookClient
    from formatters import MESSAGE_TYPES, extract_full_report_url, format_message
    from line_notify import LineNotifyClient
    from telegram_bot import TelegramBotClient


LOGGER = logging.getLogger(__name__)
CONFIG_PATH = Path(__file__).with_name("config.yaml")
CHANNEL_ORDER = ("line", "telegram", "discord")
_EXPLICIT_SECRET_ENV_VARS = {
    "LINE_NOTIFY_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "DISCORD_WEBHOOK_URL",
}
_SECRET_ENV_MARKERS = ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "WEBHOOK_URL")


@dataclass(frozen=True)
class DeliveryResult:
    """Outcome for one channel delivery attempt."""

    channel: str
    success: bool
    status_code: int | None = None
    error: str | None = None
    skipped: bool = False


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Load non-secret notification settings from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Notification config not found: {path}")
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    channels = config.get("channels")
    if not isinstance(channels, Mapping):
        raise ValueError("Notification config must define a channels mapping")
    missing = [channel for channel in CHANNEL_ORDER if channel not in channels]
    if missing:
        raise ValueError(f"Notification config is missing channels: {', '.join(missing)}")
    return config


class Notifier:
    """Format and deliver a notification independently to every channel."""

    def __init__(
        self,
        *,
        config: Mapping[str, Any] | None = None,
        clients: Mapping[str, Any] | None = None,
    ) -> None:
        self.config = dict(config) if config is not None else load_config()
        self.clients = dict(clients) if clients is not None else self._build_clients()

    def send_all(
        self,
        message_type: str,
        content: str | Mapping[str, Any],
        *,
        full_report_url: str | None = None,
    ) -> list[DeliveryResult]:
        """Attempt all enabled channels, returning one result per channel."""
        if message_type not in MESSAGE_TYPES:
            supported = ", ".join(sorted(MESSAGE_TYPES))
            raise ValueError(f"Unsupported message type: {message_type}. Expected one of: {supported}")

        safe_content = redact_secrets(content)
        report_url = full_report_url or extract_full_report_url(safe_content)
        safe_report_url = redact_secrets(report_url) if report_url else None
        results: list[DeliveryResult] = []
        channels_config = self.config.get("channels", {})

        for channel in CHANNEL_ORDER:
            channel_config = channels_config.get(channel, {})
            if not channel_config.get("enabled", True):
                results.append(DeliveryResult(channel=channel, success=False, skipped=True))
                continue

            client = self.clients.get(channel)
            if client is None:
                results.append(
                    DeliveryResult(channel=channel, success=False, error=f"{channel.title()} client is unavailable")
                )
                continue

            try:
                payload = format_message(
                    channel,
                    message_type,
                    safe_content,
                    full_report_url=safe_report_url,
                    max_length=int(channel_config.get("message_limit", 0)) or None,
                )
                status_code = client.send(payload)
                results.append(DeliveryResult(channel=channel, success=True, status_code=status_code))
            except Exception as exc:  # Continue so a failed channel cannot block the rest.
                error = str(redact_secrets(str(exc))) or f"{channel.title()} delivery failed"
                LOGGER.warning("%s delivery failed: %s", channel, error)
                results.append(DeliveryResult(channel=channel, success=False, error=error))

        return results

    def send(
        self,
        message_type: str,
        content: str | Mapping[str, Any],
        *,
        full_report_url: str | None = None,
    ) -> list[DeliveryResult]:
        """Alias for ``send_all``."""
        return self.send_all(message_type, content, full_report_url=full_report_url)

    def _build_clients(self) -> dict[str, Any]:
        channels = self.config["channels"]
        line_config = channels["line"]
        telegram_config = channels["telegram"]
        discord_config = channels["discord"]
        return {
            "line": LineNotifyClient(
                token_env=line_config.get("token_env", "LINE_NOTIFY_TOKEN"),
                api_url=line_config.get("api_url", LineNotifyClient.DEFAULT_API_URL),
                timeout=float(line_config.get("timeout_seconds", 10)),
            ),
            "telegram": TelegramBotClient(
                token_env=telegram_config.get("token_env", "TELEGRAM_BOT_TOKEN"),
                chat_id_env=telegram_config.get("chat_id_env", "TELEGRAM_CHAT_ID"),
                api_base_url=telegram_config.get("api_base_url", TelegramBotClient.DEFAULT_API_BASE_URL),
                timeout=float(telegram_config.get("timeout_seconds", 10)),
            ),
            "discord": DiscordWebhookClient(
                webhook_url_env=discord_config.get("webhook_url_env", "DISCORD_WEBHOOK_URL"),
                timeout=float(discord_config.get("timeout_seconds", 10)),
            ),
        }


def redact_secrets(value: Any) -> Any:
    """Recursively replace configured secret values before sending or logging."""
    secrets = _secret_values()
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, Mapping):
        return {key: redact_secrets(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_secrets(item) for item in value]
    return value


def _secret_values() -> list[str]:
    values: set[str] = set()
    for key, value in os.environ.items():
        if not value or len(value) < 4:
            continue
        if key in _EXPLICIT_SECRET_ENV_VARS or any(marker in key.upper() for marker in _SECRET_ENV_MARKERS):
            values.add(value)
    return sorted(values, key=len, reverse=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send a notification to LINE, Telegram, and Discord.")
    parser.add_argument("--type", required=True, choices=sorted(MESSAGE_TYPES), dest="message_type")
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 Markdown or text input file")
    parser.add_argument(
        "--full-report-url",
        help="HTTP(S) link appended when the message is truncated (or declared in input frontmatter)",
    )
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Notification YAML config")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        content = args.input.read_text(encoding="utf-8")
        notifier = Notifier(config=load_config(args.config))
        results = notifier.send_all(
            args.message_type,
            content,
            full_report_url=args.full_report_url,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "error", "error": str(redact_secrets(str(exc)))}), file=sys.stderr)
        return 2

    print(json.dumps({"results": [asdict(result) for result in results]}, ensure_ascii=False))
    return 0 if all(result.success or result.skipped for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
