"""Tests for Phase 4 multi-channel notifications.

All HTTP calls are mocked; these tests never contact notification vendors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.notify.discord_webhook import DiscordWebhookClient  # noqa: E402
from scripts.notify.formatters import (
    format_discord_message,
    format_line_message,
    format_telegram_message,
)  # noqa: E402
from scripts.notify.line_notify import LineNotifyClient  # noqa: E402
from scripts.notify.notifier import Notifier, load_config  # noqa: E402
from scripts.notify.telegram_bot import TelegramBotClient  # noqa: E402


class FakeResponse:
    """Small context-managed urllib response used by client tests."""

    def __init__(self, status: int, body: str = "") -> None:
        self.status = status
        self._body = body.encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def read(self) -> bytes:
        return self._body


TEST_CONFIG = {
    "channels": {
        "line": {"enabled": True, "message_limit": 1_000},
        "telegram": {"enabled": True, "message_limit": 4_096},
        "discord": {"enabled": True, "message_limit": 4_096},
    }
}


def test_line_notify_send(monkeypatch) -> None:
    monkeypatch.setenv("LINE_NOTIFY_TOKEN", "line-test-token")

    with patch("scripts.notify.line_notify.urlopen", return_value=FakeResponse(200, '{"status": 200}')) as post:
        status = LineNotifyClient().send("Morning summary")

    assert status == 200
    request = post.call_args.args[0]
    assert request.full_url == "https://notify-api.line.me/api/notify"
    assert request.get_header("Authorization") == "Bearer line-test-token"
    assert parse_qs(request.data.decode("utf-8")) == {"message": ["Morning summary"]}


def test_telegram_bot_send(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "telegram-test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")

    with patch("scripts.notify.telegram_bot.urlopen", return_value=FakeResponse(200, '{"ok": true}')) as post:
        status = TelegramBotClient().send("*Morning Report*")

    assert status == 200
    request = post.call_args.args[0]
    assert request.full_url == "https://api.telegram.org/bottelegram-test-token/sendMessage"
    payload = json.loads(request.data)
    assert payload == {
        "chat_id": "123456",
        "text": "*Morning Report*",
        "parse_mode": "MarkdownV2",
        "link_preview_options": {"is_disabled": True},
    }


def test_discord_webhook_send(monkeypatch) -> None:
    webhook_url = "https://discord.com/api/webhooks/test/id"
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", webhook_url)
    payload = {"embeds": [{"title": "Morning Report", "description": "All systems nominal"}]}

    with patch("scripts.notify.discord_webhook.urlopen", return_value=FakeResponse(204)) as post:
        status = DiscordWebhookClient().send(payload)

    assert status == 204
    request = post.call_args.args[0]
    assert request.full_url == webhook_url
    assert json.loads(request.data) == payload


def test_unified_notifier_all_channels() -> None:
    clients = {
        "line": MagicMock(),
        "telegram": MagicMock(),
        "discord": MagicMock(),
    }
    clients["line"].send.return_value = 200
    clients["telegram"].send.return_value = 200
    clients["discord"].send.return_value = 204
    content = {
        "summary": {"candidates": 8, "launch": 2},
        "top_products": [
            {"name": "Product A", "score": 91},
            {"name": "Product B", "score": 87},
            {"name": "Product C", "score": 84},
            {"name": "Product D", "score": 80},
        ],
        "decisions": ["Launch Product A", "Test Product B"],
        "errors": [],
    }

    results = Notifier(config=TEST_CONFIG, clients=clients).send_all("morning_report", content)

    assert [result.channel for result in results] == ["line", "telegram", "discord"]
    assert [result.status_code for result in results] == [200, 200, 204]
    assert all(result.success for result in results)
    assert all(client.send.call_count == 1 for client in clients.values())
    assert "Product D" not in clients["line"].send.call_args.args[0]
    assert isinstance(clients["telegram"].send.call_args.args[0], str)
    assert "embeds" in clients["discord"].send.call_args.args[0]


def test_notifier_partial_failure() -> None:
    clients = {
        "line": MagicMock(),
        "telegram": MagicMock(),
        "discord": MagicMock(),
    }
    clients["line"].send.side_effect = RuntimeError("LINE unavailable")
    clients["telegram"].send.return_value = 200
    clients["discord"].send.return_value = 204

    results = Notifier(config=TEST_CONFIG, clients=clients).send_all(
        "error_alert",
        {"error": "Scraper timed out", "stage": "scrape"},
    )

    by_channel = {result.channel: result for result in results}
    assert not by_channel["line"].success
    assert by_channel["line"].error == "LINE unavailable"
    assert by_channel["telegram"].success
    assert by_channel["discord"].success
    clients["telegram"].send.assert_called_once()
    clients["discord"].send.assert_called_once()


def test_message_formatting_morning_report() -> None:
    content = {
        "summary": {"candidates": 5, "launch": 1},
        "top_products": [
            {"name": "Desk Lamp", "score": 90, "decision": "launch"},
            {"name": "Travel Mug", "score": 83, "decision": "small_batch_test"},
        ],
        "decisions": {"launch": 1, "small_batch_test": 1},
    }

    line_message = format_line_message("morning_report", content)
    telegram_message = format_telegram_message("morning_report", content)
    discord_payload = format_discord_message("morning_report", content)

    assert line_message.startswith("☀️ MORNING REPORT")
    assert "Top 3 products" in line_message
    assert "Desk Lamp | launch | 90" in line_message
    assert telegram_message.startswith("*☀️ Morning Report*")
    assert "Top 3 products" in telegram_message
    assert discord_payload["embeds"][0]["title"] == "☀️ Morning Report"
    assert discord_payload["embeds"][0]["color"] == 0x2ECC71


def test_morning_report_markdown_is_condensed_to_top_three() -> None:
    report = """---
type: weekly_report
---

# Weekly Report

## Summary

- Candidates scored: 4
- Launch: 2

## Launch

- Product A | Score: 92
- Product B | Score: 88

## Small Batch Test

- Product C | Score: 81
- Product D | Score: 78

## Errors

- One optional signal was unavailable
"""

    message = format_line_message("morning_report", report)

    assert "Candidates scored: 4" in message
    assert "[Launch] Product A" in message
    assert "[Small Batch Test] Product C" in message
    assert "Product D" not in message
    assert "Launch: 2" in message
    assert "One optional signal was unavailable" in message


def test_message_formatting_error_alert() -> None:
    content = {
        "error": "Shopee request failed",
        "stage": "product_scan",
        "run_id": "run-007",
        "details": "Retry budget exhausted",
    }

    line_message = format_line_message("error_alert", content)
    telegram_message = format_telegram_message("error_alert", content)
    discord_payload = format_discord_message("error_alert", content)

    assert line_message.startswith("🚨 ERROR ALERT")
    assert "Stage: product_scan" in line_message
    assert telegram_message.startswith("*🚨 Error Alert*")
    assert r"Run: run\-007" in telegram_message
    assert discord_payload["embeds"][0]["color"] == 0xE74C3C


def test_message_formatting_idea_proposal() -> None:
    content = {
        "title": "Test ergonomic desk products",
        "rationale": "Demand increased this week",
        "expected_impact": "Two new small-batch candidates",
    }

    line_message = format_line_message("idea_proposal", content)
    discord_payload = format_discord_message("idea_proposal", content)

    assert line_message.startswith("💡 IDEA PROPOSAL")
    assert "Rationale: Demand increased this week" in line_message
    assert discord_payload["embeds"][0]["title"] == "💡 Idea Proposal"


def test_message_truncation() -> None:
    content = "A" * 1_000
    report_url = "https://reports.example.test/morning/007"

    line_message = format_line_message(
        "morning_report",
        content,
        full_report_url=report_url,
        max_length=140,
    )
    telegram_message = format_telegram_message(
        "morning_report",
        content,
        full_report_url=report_url,
        max_length=160,
    )
    discord_payload = format_discord_message(
        "morning_report",
        content,
        full_report_url=report_url,
        max_length=150,
    )

    assert len(line_message) <= 140
    assert report_url in line_message
    assert len(telegram_message) <= 160
    assert report_url in telegram_message
    embed = discord_payload["embeds"][0]
    assert len(embed["description"]) <= 150
    assert report_url in embed["description"]
    assert embed["url"] == report_url


def test_notifier_redacts_environment_secrets(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "do-not-send-this-token")
    clients = {channel: MagicMock() for channel in ("line", "telegram", "discord")}
    for client in clients.values():
        client.send.return_value = 200

    Notifier(config=TEST_CONFIG, clients=clients).send_all(
        "error_alert",
        {"error": "Leaked do-not-send-this-token in subprocess output"},
    )

    assert "do-not-send-this-token" not in clients["line"].send.call_args.args[0]
    assert "do-not-send-this-token" not in clients["telegram"].send.call_args.args[0]
    assert "do-not-send-this-token" not in json.dumps(clients["discord"].send.call_args.args[0])


def test_notification_config_references_environment_variables() -> None:
    channels = load_config()["channels"]

    assert channels["line"]["token_env"] == "LINE_NOTIFY_TOKEN"
    assert channels["telegram"]["token_env"] == "TELEGRAM_BOT_TOKEN"
    assert channels["telegram"]["chat_id_env"] == "TELEGRAM_CHAT_ID"
    assert channels["discord"]["webhook_url_env"] == "DISCORD_WEBHOOK_URL"
