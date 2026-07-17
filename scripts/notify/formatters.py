"""Channel-specific formatting for outbound notifications."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse


MESSAGE_TYPES = frozenset({"morning_report", "error_alert", "idea_proposal"})
DEFAULT_LIMITS = {
    "line": 1_000,
    "telegram": 4_096,
    "discord": 4_096,
}

_TYPE_DETAILS = {
    "morning_report": {
        "title": "Morning Report",
        "icon": "☀️",
        "color": 0x2ECC71,
    },
    "error_alert": {
        "title": "Error Alert",
        "icon": "🚨",
        "color": 0xE74C3C,
    },
    "idea_proposal": {
        "title": "Idea Proposal",
        "icon": "💡",
        "color": 0xF1C40F,
    },
}


def extract_full_report_url(content: str | Mapping[str, Any]) -> str | None:
    """Return an explicitly declared HTTP(S) report URL, if present."""
    if isinstance(content, Mapping):
        for key in ("full_report_url", "report_url", "source_url"):
            value = content.get(key)
            if isinstance(value, str) and _is_http_url(value):
                return value.strip()
        return None

    match = re.search(
        r"(?im)^\s*(?:full_report_url|report_url|source_url)\s*:\s*[\"']?(https?://[^\s\"']+)",
        content,
    )
    if match and _is_http_url(match.group(1)):
        return match.group(1).rstrip(")],.")
    return None


def format_line_message(
    message_type: str,
    content: str | Mapping[str, Any],
    *,
    full_report_url: str | None = None,
    max_length: int = DEFAULT_LIMITS["line"],
) -> str:
    """Format a plain-text LINE Notify message."""
    details = _message_details(message_type)
    max_length = min(max_length, DEFAULT_LIMITS["line"])
    body = _to_plain_text(_render_body(message_type, content))
    title = f"{details['icon']} {str(details['title']).upper()}"
    suffix = f"\n\nFull report: {full_report_url}" if _is_http_url(full_report_url) else ""
    return _truncate(f"{title}\n\n{body}", max_length, suffix)


def format_telegram_message(
    message_type: str,
    content: str | Mapping[str, Any],
    *,
    full_report_url: str | None = None,
    max_length: int = DEFAULT_LIMITS["telegram"],
) -> str:
    """Format a Telegram MarkdownV2 message."""
    details = _message_details(message_type)
    max_length = min(max_length, DEFAULT_LIMITS["telegram"])
    title = escape_markdown_v2(f"{details['icon']} {details['title']}")
    body = escape_markdown_v2(_render_body(message_type, content))
    message = f"*{title}*\n\n{body}"
    suffix = ""
    if _is_http_url(full_report_url):
        suffix = f"\n\n[View full report]({_escape_markdown_url(full_report_url)})"
    return _truncate(message, max_length, suffix)


def format_discord_message(
    message_type: str,
    content: str | Mapping[str, Any],
    *,
    full_report_url: str | None = None,
    max_length: int = DEFAULT_LIMITS["discord"],
) -> dict[str, Any]:
    """Format a Discord webhook payload using a rich embed."""
    details = _message_details(message_type)
    max_length = min(max_length, DEFAULT_LIMITS["discord"])
    body = _render_body(message_type, content)
    suffix = ""
    if _is_http_url(full_report_url):
        suffix = f"\n\n[View full report]({full_report_url})"

    embed: dict[str, Any] = {
        "title": f"{details['icon']} {details['title']}",
        "description": _truncate(body, max_length, suffix),
        "color": details["color"],
        "footer": {"text": "Affiliate Product Intelligence OS"},
    }
    if _is_http_url(full_report_url):
        embed["url"] = full_report_url

    return {
        "embeds": [embed],
        # Prevent report text from pinging Discord users or roles.
        "allowed_mentions": {"parse": []},
    }


def format_message(
    channel: str,
    message_type: str,
    content: str | Mapping[str, Any],
    *,
    full_report_url: str | None = None,
    max_length: int | None = None,
) -> str | dict[str, Any]:
    """Dispatch formatting to a supported channel."""
    normalized_channel = channel.lower()
    if normalized_channel not in DEFAULT_LIMITS:
        raise ValueError(f"Unsupported notification channel: {channel}")
    limit = max_length or DEFAULT_LIMITS[normalized_channel]

    formatters = {
        "line": format_line_message,
        "telegram": format_telegram_message,
        "discord": format_discord_message,
    }
    return formatters[normalized_channel](
        message_type,
        content,
        full_report_url=full_report_url,
        max_length=limit,
    )


def escape_markdown_v2(value: str) -> str:
    """Escape Telegram MarkdownV2 control characters."""
    return re.sub(r"([_\*\[\]\(\)~`>#+\-=|{}.!\\])", r"\\\1", value)


def _message_details(message_type: str) -> dict[str, str | int]:
    try:
        return _TYPE_DETAILS[message_type]
    except KeyError as exc:
        supported = ", ".join(sorted(MESSAGE_TYPES))
        raise ValueError(f"Unsupported message type: {message_type}. Expected one of: {supported}") from exc


def _render_body(message_type: str, content: str | Mapping[str, Any]) -> str:
    _message_details(message_type)
    if not isinstance(content, Mapping):
        body = _strip_frontmatter(str(content)).strip()
        if message_type == "morning_report":
            body = _render_morning_markdown(body)
        return body or "No details provided."

    if message_type == "morning_report":
        return _render_morning_report(content)
    if message_type == "error_alert":
        return _render_error_alert(content)
    return _render_idea_proposal(content)


def _render_morning_report(content: Mapping[str, Any]) -> str:
    sections: list[str] = []
    summary = content.get("summary")
    if summary:
        sections.append("Summary\n" + _render_value(summary))

    products = content.get("top_products", content.get("products", []))
    if _is_sequence(products):
        rendered_products = [f"{index}. {_render_item(item)}" for index, item in enumerate(products[:3], 1)]
        if rendered_products:
            sections.append("Top 3 products\n" + "\n".join(rendered_products))

    decisions = content.get("decisions")
    if decisions:
        sections.append("Decisions\n" + _render_value(decisions))

    errors = content.get("errors")
    if errors:
        sections.append("Errors\n" + _render_value(errors))

    return "\n\n".join(sections) or _render_mapping(content)


def _render_morning_markdown(content: str) -> str:
    """Condense a generated Markdown report into its notification sections."""
    sections = _markdown_h2_sections(content)
    if not sections:
        return content

    output: list[str] = []
    summary = sections.get("summary", [])
    if _has_content(summary):
        output.append("Summary\n" + "\n".join(_nonempty_lines(summary)))

    explicit_products = sections.get("top 3 products", sections.get("top products", []))
    top_products = _bullet_lines(explicit_products)[:3]
    decision_headings = ("launch", "small batch test", "watchlist", "reject")
    if not top_products:
        for heading in decision_headings:
            for product in _bullet_lines(sections.get(heading, [])):
                if product.lower() != "- none":
                    top_products.append(f"- [{heading.title()}] {product[2:].strip()}")
                if len(top_products) == 3:
                    break
            if len(top_products) == 3:
                break
    if top_products:
        output.append("Top 3 products\n" + "\n".join(top_products))

    decisions = sections.get("decisions", [])
    if _has_content(decisions):
        output.append("Decisions\n" + "\n".join(_nonempty_lines(decisions)))
    else:
        decision_counts = []
        for heading in decision_headings:
            products = [line for line in _bullet_lines(sections.get(heading, [])) if line.lower() != "- none"]
            if heading in sections:
                decision_counts.append(f"- {heading.title()}: {len(products)}")
        if decision_counts:
            output.append("Decisions\n" + "\n".join(decision_counts))

    errors = sections.get("errors", [])
    if _has_content(errors):
        output.append("Errors\n" + "\n".join(_nonempty_lines(errors)))
    return "\n\n".join(output) or content


def _markdown_h2_sections(content: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in content.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip().lower()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def _bullet_lines(lines: Sequence[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip().startswith("- ")]


def _nonempty_lines(lines: Sequence[str]) -> list[str]:
    return [line.rstrip() for line in lines if line.strip()]


def _has_content(lines: Sequence[str]) -> bool:
    meaningful = [line.strip().lower() for line in lines if line.strip()]
    return bool(meaningful) and meaningful not in (["none"], ["- none"])


def _render_error_alert(content: Mapping[str, Any]) -> str:
    error = content.get("error", content.get("message", "Unknown error"))
    lines = [f"Error: {_render_item(error)}"]
    for key, label in (("stage", "Stage"), ("run_id", "Run"), ("timestamp", "Time"), ("details", "Details")):
        if content.get(key) not in (None, ""):
            lines.append(f"{label}: {_render_item(content[key])}")
    return "\n".join(lines)


def _render_idea_proposal(content: Mapping[str, Any]) -> str:
    title = content.get("title", content.get("idea", "Untitled idea"))
    lines = [f"Idea: {_render_item(title)}"]
    for key, label in (
        ("summary", "Summary"),
        ("rationale", "Rationale"),
        ("expected_impact", "Expected impact"),
        ("next_steps", "Next steps"),
    ):
        if content.get(key) not in (None, ""):
            lines.append(f"{label}: {_render_value(content[key])}")
    return "\n".join(lines)


def _render_mapping(value: Mapping[str, Any]) -> str:
    excluded = {"full_report_url", "report_url", "source_url"}
    return "\n".join(
        f"{str(key).replace('_', ' ').title()}: {_render_value(item)}"
        for key, item in value.items()
        if key not in excluded
    )


def _render_value(value: Any) -> str:
    if isinstance(value, Mapping):
        return "\n".join(f"- {str(key).replace('_', ' ').title()}: {_render_item(item)}" for key, item in value.items())
    if _is_sequence(value):
        return "\n".join(f"- {_render_item(item)}" for item in value)
    return str(value)


def _render_item(value: Any) -> str:
    if not isinstance(value, Mapping):
        return str(value)
    preferred = ("name", "product_name", "title", "decision", "score", "status")
    parts = [str(value[key]) for key in preferred if value.get(key) not in (None, "")]
    if parts:
        return " | ".join(parts)
    return ", ".join(f"{key}={item}" for key, item in value.items())


def _strip_frontmatter(value: str) -> str:
    lines = value.splitlines()
    if not lines or lines[0].strip() != "---":
        return value
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :])
    return value


def _to_plain_text(value: str) -> str:
    value = re.sub(r"\[([^\]]+)]\((https?://[^)]+)\)", r"\1: \2", value)
    value = re.sub(r"(?m)^\s*#{1,6}\s*", "", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    return value.strip()


def _truncate(value: str, max_length: int, suffix: str = "") -> str:
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    combined = value + suffix
    if len(combined) <= max_length:
        return combined

    marker = "\n\n…"
    reserved = marker + suffix
    if len(reserved) >= max_length:
        # An unusually long URL must not make the API payload invalid.
        return (value[: max_length - 1].rstrip() + "…")[:max_length]
    return value[: max_length - len(reserved)].rstrip() + reserved


def _escape_markdown_url(value: str) -> str:
    return value.replace("\\", "\\\\").replace(")", "\\)")


def _is_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))
