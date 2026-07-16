#!/usr/bin/env python3
"""Create a guarded multi-role brainstorming meeting note with Claude CLI.

The meeting produces research and workflow ideas for a future cycle.  It does
not draft affiliate content, vote, decide, publish, or autopublish.

Ref: codex/tasks/005-agent-ai-runtime.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        cli_main_error,
        discover_notes,
        existing_created_at,
        markdown_bullets,
        product_context,
        require_text,
        safe_slug,
        sanitize_text,
        text_list,
        write_note,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        cli_main_error,
        discover_notes,
        existing_created_at,
        markdown_bullets,
        product_context,
        require_text,
        safe_slug,
        sanitize_text,
        text_list,
        write_note,
    )


AGENT_NAME = "Agent Research Meeting Chair"
MEETING_INSTRUCTIONS = """Facilitate a research meeting using the viewpoints of Product Miner,
Demand Intelligence, Commission Economics, Content Virality, and Compliance Risk.
Propose only evidence-gathering, scoring-quality, risk-reduction, or workflow ideas for
future product-intelligence cycles. Do not produce agent votes or decisions. Do not
draft hooks, scripts, captions, blog posts, promotional copy, or affiliate links.
Every idea must cite one or more product IDs from the supplied context and identify
a concrete operator-reviewable next action."""
OUTPUT_SCHEMA = {
    "summary": "string",
    "agenda": ["string"],
    "ideas": [
        {
            "title": "string",
            "rationale": "evidence-based string",
            "product_ids": ["product_id from context"],
            "next_action": "non-publishing string",
        }
    ],
}


def _validate_ideas(data: Mapping[str, Any], known_ids: set[str]) -> list[dict[str, Any]]:
    raw_ideas = data.get("ideas")
    if not isinstance(raw_ideas, list) or not raw_ideas:
        raise AgentOutputError("Meeting output must include a non-empty ideas list")
    ideas: list[dict[str, Any]] = []
    for raw_idea in raw_ideas:
        if not isinstance(raw_idea, Mapping):
            raise AgentOutputError("Each meeting idea must be an object")
        product_ids = text_list(raw_idea, "product_ids")
        if not product_ids:
            raise AgentOutputError("Each meeting idea must reference at least one product_id")
        unknown = set(product_ids) - known_ids
        if unknown:
            raise AgentOutputError(
                f"Meeting idea referenced unknown product_id(s): {', '.join(sorted(unknown))}"
            )
        ideas.append(
            {
                "title": require_text(raw_idea, "title"),
                "rationale": require_text(raw_idea, "rationale"),
                "product_ids": product_ids,
                "next_action": require_text(raw_idea, "next_action"),
            }
        )
    return ideas


def run_meeting(
    vault_root: Path = DEFAULT_VAULT_ROOT,
    *,
    product_ids: Sequence[str] | None = None,
    runner: AgentRunner | None = None,
) -> Path:
    candidates = discover_notes(vault_root, "product_candidate")
    if product_ids:
        selected = set(product_ids)
        candidates = [
            note for note in candidates if str(note.frontmatter.get("product_id", "")) in selected
        ]
        found = {str(note.frontmatter.get("product_id", "")) for note in candidates}
        if found != selected:
            raise ValueError(
                f"Unknown product_id(s): {', '.join(sorted(selected - found))}"
            )
    if not candidates:
        raise ValueError(f"No product_candidate notes found below {vault_root}")

    known_ids = {require_text(note.frontmatter, "product_id") for note in candidates}
    context = {
        "meeting_purpose": "future-cycle product intelligence improvements",
        "products": [product_context(vault_root, note) for note in candidates],
    }
    active_runner = runner or AgentRunner.for_agent("meeting")
    data = active_runner.run(AGENT_NAME, MEETING_INSTRUCTIONS, context, OUTPUT_SCHEMA)
    summary = require_text(data, "summary")
    agenda = text_list(data, "agenda")
    if not agenda:
        raise AgentOutputError("Meeting output must include at least one agenda item")
    ideas = _validate_ideas(data, known_ids)

    now = datetime.now(UTC).replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")
    meeting_date = now.date().isoformat()
    meeting_id = f"meeting-agent-runtime-{now.strftime('%Y%m%dT%H%M%SZ')}"
    output_path = Path(vault_root) / "meetings" / f"{safe_slug(meeting_id)}.md"
    frontmatter = {
        "type": "agent_meeting",
        "meeting_id": meeting_id,
        "meeting_date": meeting_date,
        "product_ids": sorted(known_ids),
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    idea_sections: list[str] = []
    for index, idea in enumerate(ideas, start=1):
        idea_sections.extend(
            (
                f"### {index}. {sanitize_text(idea['title'])}",
                "",
                f"- Products: {', '.join(f'`{product_id}`' for product_id in idea['product_ids'])}",
                f"- Rationale: {sanitize_text(idea['rationale'])}",
                f"- Next action: {sanitize_text(idea['next_action'])}",
                "",
            )
        )
    body = "\n".join(
        (
            "# Agent Research Meeting",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Agenda",
            "",
            markdown_bullets(agenda),
            "",
            "## Ideas",
            "",
            *idea_sections,
            "## Notes",
            "",
            "- Ideas require operator review and do not authorize content creation or publishing.",
        )
    )
    return write_note(vault_root, output_path, frontmatter, body)


run = run_meeting


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create an agent_meeting note with Claude CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", action="append", dest="product_ids")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_meeting(args.vault_root, product_ids=args.product_ids)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
