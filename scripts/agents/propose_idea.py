#!/usr/bin/env python3
"""Extract actionable meeting ideas, create proposal notes, and notify users.

Ref: codex/tasks/008-agent-brainstorming.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    from scripts.notify.notifier import Notifier
except ImportError:  # pragma: no cover - direct execution from scripts/agents.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.notify.notifier import Notifier

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        VaultNote,
        cli_main_error,
        existing_created_at,
        read_note,
        require_text,
        safe_slug,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        VaultNote,
        cli_main_error,
        existing_created_at,
        read_note,
        require_text,
        safe_slug,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )


IDEA_TYPES = {
    "new_niche",
    "new_category",
    "search_keyword",
    "content_angle",
    "timing_change",
    "scoring_change",
    "workflow_change",
}
_IDEA_SECTION_RE = re.compile(
    r"(?ms)^###\s+(?:\d+\.\s*)?(?P<title>[^\n]+)\n(?P<body>.*?)(?=^###\s+|^##\s+|\Z)"
)
_FIELD_RE = re.compile(r"(?m)^-\s+([^:]+):\s*(.*)$")


def _normalise_idea(raw: Mapping[str, Any]) -> dict[str, Any]:
    idea_type = str(raw.get("idea_type", "workflow_change")).strip().lower()
    idea_type = idea_type.replace("-", "_").replace(" ", "_")
    if idea_type not in IDEA_TYPES:
        idea_type = "workflow_change"
    proposed_action = str(raw.get("proposed_action", raw.get("next_action", ""))).strip()
    expected_impact = str(raw.get("expected_impact", "")).strip() or proposed_action
    values = raw.get("product_ids", [])
    if isinstance(values, str):
        product_ids = re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]*", values.replace("`", ""))
    elif isinstance(values, Sequence):
        product_ids = [sanitize_text(item) for item in values if sanitize_text(item)]
    else:
        product_ids = []
    idea = {
        "idea_type": idea_type,
        "title": require_text(raw, "title"),
        "rationale": require_text(raw, "rationale"),
        "expected_impact": sanitize_text(expected_impact),
        "proposed_action": sanitize_text(proposed_action),
        "target_niche": sanitize_text(raw.get("target_niche", "")),
        "target_keyword": sanitize_text(raw.get("target_keyword", "")),
        "product_ids": product_ids,
        "requires_user_approval": True,
    }
    if not idea["expected_impact"]:
        raise ValueError(f"Idea {idea['title']!r} is missing expected_impact")
    if not idea["proposed_action"]:
        raise ValueError(f"Idea {idea['title']!r} is missing proposed_action")
    if idea_type in {"new_niche", "new_category"} and not idea["target_niche"]:
        raise ValueError(f"Scope idea {idea['title']!r} is missing target_niche")
    if idea_type == "search_keyword" and not idea["target_keyword"]:
        raise ValueError(f"Keyword idea {idea['title']!r} is missing target_keyword")
    return sanitize_data(idea)


def _ideas_from_body(body: str) -> list[dict[str, Any]]:
    ideas: list[dict[str, Any]] = []
    for match in _IDEA_SECTION_RE.finditer(body):
        fields = {
            key.strip().lower().replace(" ", "_"): value.strip()
            for key, value in _FIELD_RE.findall(match.group("body"))
        }
        if "rationale" not in fields:
            continue
        products = fields.get("products", "")
        raw = {
            "title": match.group("title").strip(),
            "idea_type": fields.get("type", "workflow_change").strip("`"),
            "rationale": fields["rationale"],
            "expected_impact": fields.get("expected_impact", fields.get("next_action", "")),
            "proposed_action": fields.get("proposed_action", fields.get("next_action", "")),
            "target_niche": fields.get("target_niche", "").removesuffix("None"),
            "target_keyword": fields.get("target_keyword", "").removesuffix("None"),
            "product_ids": re.findall(r"`([^`]+)`", products),
        }
        ideas.append(_normalise_idea(raw))
    return ideas


def extract_ideas(meeting: Path | VaultNote) -> list[dict[str, Any]]:
    """Extract validated ideas from an ``agent_meeting`` note."""

    note = read_note(meeting) if isinstance(meeting, Path) else meeting
    if note.frontmatter.get("type") != "agent_meeting":
        raise ValueError(f"Expected agent_meeting note: {note.path}")
    raw_ideas = note.frontmatter.get("ideas")
    if isinstance(raw_ideas, list):
        ideas = [_normalise_idea(raw) for raw in raw_ideas if isinstance(raw, Mapping)]
    else:
        ideas = _ideas_from_body(note.body)
    if not ideas:
        raise ValueError(f"No actionable ideas found in meeting note: {note.path}")
    return ideas


def _proposal_id(meeting_id: str, index: int, title: str) -> str:
    digest = hashlib.sha256(f"{meeting_id}\0{index}\0{title}".encode()).hexdigest()[:12]
    return f"proposal-{safe_slug(title)[:48]}-{digest}"


def _notification_details(results: Any) -> list[dict[str, Any]]:
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        return []
    details: list[dict[str, Any]] = []
    for result in results:
        details.append(
            {
                "channel": sanitize_text(getattr(result, "channel", "unknown")),
                "success": bool(getattr(result, "success", False)),
                "skipped": bool(getattr(result, "skipped", False)),
            }
        )
    return details


def propose_ideas(
    meeting_path: Path,
    *,
    vault_root: Path | None = None,
    notifier: Any | None = None,
) -> list[Path]:
    """Create pending proposal notes and attempt notification for each idea."""

    meeting = read_note(Path(meeting_path))
    ideas = extract_ideas(meeting)
    root = Path(vault_root) if vault_root is not None else meeting.path.parent.parent
    meeting_id = require_text(meeting.frontmatter, "meeting_id")
    timestamp = utc_now()
    active_notifier = notifier or Notifier()
    paths: list[Path] = []

    for index, idea in enumerate(ideas, 1):
        proposal_id = _proposal_id(meeting_id, index, idea["title"])
        output_path = root / "proposals" / f"{proposal_id}.md"
        frontmatter = {
            "type": "idea_proposal",
            "proposal_id": proposal_id,
            "meeting_id": meeting_id,
            "idea_type": idea["idea_type"],
            "title": idea["title"],
            "product_ids": idea["product_ids"],
            "target_niche": idea["target_niche"],
            "target_keyword": idea["target_keyword"],
            "rationale": idea["rationale"],
            "expected_impact": idea["expected_impact"],
            "proposed_action": idea["proposed_action"],
            "requires_user_approval": True,
            "approval_status": "pending",
            "notification_status": "pending",
            "created_at": existing_created_at(output_path, timestamp),
            "updated_at": timestamp,
            "status": "pending_review",
        }
        body = "\n".join(
            (
                f"# Idea Proposal: {idea['title']}",
                "",
                "## Rationale",
                "",
                idea["rationale"],
                "",
                "## Expected Impact",
                "",
                idea["expected_impact"],
                "",
                "## Proposed Action",
                "",
                idea["proposed_action"],
                "",
                "## Required Approval",
                "",
                "Explicit user approval is required before this idea enters the next "
                "nightly configuration.",
                "New niches also remain constrained by `learning.yaml` allowlists and "
                "niche limits.",
            )
        )
        write_note(root, output_path, frontmatter, body)

        try:
            results = active_notifier.send_all(
                "idea_proposal",
                {
                    "title": idea["title"],
                    "rationale": idea["rationale"],
                    "expected_impact": idea["expected_impact"],
                    "next_steps": idea["proposed_action"],
                    "proposal_id": proposal_id,
                    "approval_required": True,
                },
            )
            details = _notification_details(results)
            frontmatter["notification_results"] = details
            if not details or any(item["success"] for item in details):
                frontmatter["notification_status"] = "sent"
            elif all(item["skipped"] for item in details):
                frontmatter["notification_status"] = "skipped"
            else:
                frontmatter["notification_status"] = "failed"
        except Exception as exc:  # The durable proposal remains available for retry.
            frontmatter["notification_status"] = "failed"
            frontmatter["notification_error"] = sanitize_text(exc)
        frontmatter["updated_at"] = utc_now()
        paths.append(write_note(root, output_path, frontmatter, body))
    return paths


run = propose_ideas


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and notify idea proposals.")
    parser.add_argument("--meeting", type=Path, required=True)
    parser.add_argument("--vault-root", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        paths = propose_ideas(args.meeting, vault_root=args.vault_root)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "proposals": [str(path) for path in paths]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
