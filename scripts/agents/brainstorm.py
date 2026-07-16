#!/usr/bin/env python3
"""Run a sequential Claude brainstorming discussion and persist its synthesis.

The chairman poses a question, each specialist responds in order with the
transcript so far, and the chairman performs one final synthesis.  Models
return JSON only; Python validates and renders the Obsidian note.

Ref: codex/tasks/008-agent-brainstorming.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        cli_main_error,
        discover_notes,
        existing_created_at,
        note_context,
        require_text,
        safe_slug,
        sanitize_data,
        sanitize_text,
        text_list,
        write_note,
    )
except ImportError:  # pragma: no cover - supports direct script execution.
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        cli_main_error,
        discover_notes,
        existing_created_at,
        note_context,
        require_text,
        safe_slug,
        sanitize_data,
        sanitize_text,
        text_list,
        write_note,
    )


DEFAULT_QUESTION = (
    "What evidence, search, scoring, or workflow improvement should we test in "
    "the next product-intelligence cycle?"
)
CHAIRMAN_NAME = "Brainstorm Chairman"
DISCUSSION_AGENTS: tuple[tuple[str, str], ...] = (
    (
        "Product Miner Agent",
        "Find bounded discovery opportunities and better search inputs within configured niches.",
    ),
    (
        "Demand Intelligence Agent",
        "Assess demand evidence, trend timing, missing signals, and prediction quality.",
    ),
    (
        "Commission Economics Agent",
        "Assess economic evidence and ways to improve commission-quality predictions.",
    ),
    (
        "Content Virality Agent",
        "Assess researchable content-fit signals without drafting promotional content.",
    ),
    (
        "Compliance Risk Agent",
        "Identify compliance risks, approval gates, and safe evidence-gathering actions.",
    ),
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

QUESTION_SCHEMA = {"question": "one focused, non-publishing discussion question"}
RESPONSE_SCHEMA = {
    "analysis": "evidence-based specialist response",
    "ideas": [
        {
            "idea_type": (
                "search_keyword, content_angle, timing_change, scoring_change, "
                "workflow_change, new_niche, or new_category"
            ),
            "title": "short string",
            "rationale": "evidence-based string",
            "expected_impact": "measurable expected impact",
            "proposed_action": "bounded, non-publishing action",
            "target_niche": "configured or proposed niche, or empty string",
            "target_keyword": "keyword, or empty string",
            "product_ids": ["product_id from context"],
        }
    ],
}
SYNTHESIS_SCHEMA = {
    "summary": "short synthesis of agreements, disagreements, and evidence limits",
    "ideas": RESPONSE_SCHEMA["ideas"],
}

CHAIRMAN_QUESTION_INSTRUCTIONS = """Pose one focused question for a specialist discussion.
Keep the operator's requested topic intact. The discussion may improve evidence collection,
search keywords, scoring emphasis, timing, or workflow. It must not create affiliate content,
publish, authorize a new niche, or silently expand scope."""
SPECIALIST_INSTRUCTIONS = """Respond to the chairman using only supplied vault evidence and
the transcript so far. Suggest at most three actionable ideas. A new niche must be explicitly
typed new_niche and described as requiring user approval. Do not vote, decide, write affiliate
content, publish, or treat another agent's statement as evidence."""
SYNTHESIS_INSTRUCTIONS = """Synthesize the sequential specialist discussion into a concise
meeting result. Preserve material disagreement and missing evidence. Deduplicate ideas, make
expected impact and proposed action concrete, and mark every scope-expanding niche idea as
new_niche. Do not approve ideas, change configuration, create content, or publish."""


def _selected_products(vault_root: Path, product_ids: Sequence[str] | None) -> list[Any]:
    candidates = discover_notes(vault_root, "product_candidate")
    by_id: dict[str, Any] = {}
    for note in candidates:
        product_id = str(note.frontmatter.get("product_id", "")).strip()
        if not product_id:
            continue
        current = by_id.get(product_id)
        if current is None or (
            "samples" in current.path.parts and "samples" not in note.path.parts
        ):
            by_id[product_id] = note

    if product_ids is None:
        return [by_id[key] for key in sorted(by_id)]
    requested = {str(value).strip() for value in product_ids if str(value).strip()}
    unknown = requested - set(by_id)
    if unknown:
        raise ValueError(f"Unknown product_id(s): {', '.join(sorted(unknown))}")
    return [by_id[key] for key in sorted(requested)]


def _validated_response(data: Mapping[str, Any], known_ids: set[str]) -> dict[str, Any]:
    analysis = require_text(data, "analysis")
    raw_ideas = data.get("ideas", [])
    if not isinstance(raw_ideas, list):
        raise AgentOutputError("Specialist ideas must be a list")
    return {"analysis": analysis, "ideas": _validated_ideas(raw_ideas, known_ids)}


def _validated_ideas(raw_ideas: Any, known_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(raw_ideas, list):
        raise AgentOutputError("Brainstorm synthesis must include ideas as a list")
    ideas: list[dict[str, Any]] = []
    for raw in raw_ideas:
        if not isinstance(raw, Mapping):
            raise AgentOutputError("Each brainstorm idea must be an object")
        idea_type = require_text(raw, "idea_type").lower().replace("-", "_").replace(" ", "_")
        if idea_type not in IDEA_TYPES:
            raise AgentOutputError(f"Unsupported brainstorm idea_type={idea_type!r}")
        product_ids = text_list(raw, "product_ids")
        unknown = set(product_ids) - known_ids
        if unknown:
            raise AgentOutputError(
                f"Brainstorm idea referenced unknown product_id(s): {', '.join(sorted(unknown))}"
            )
        target_niche = str(raw.get("target_niche", "") or "").strip()
        target_keyword = str(raw.get("target_keyword", "") or "").strip()
        idea = {
            "idea_type": idea_type,
            "title": require_text(raw, "title"),
            "rationale": require_text(raw, "rationale"),
            "expected_impact": require_text(raw, "expected_impact"),
            "proposed_action": require_text(raw, "proposed_action"),
            "target_niche": sanitize_text(target_niche),
            "target_keyword": sanitize_text(target_keyword),
            "product_ids": product_ids,
            "requires_user_approval": True,
        }
        if idea_type in {"new_niche", "new_category"} and not idea["target_niche"]:
            raise AgentOutputError(f"A {idea_type} idea must include target_niche")
        if idea_type == "search_keyword" and not idea["target_keyword"]:
            raise AgentOutputError("A search_keyword idea must include target_keyword")
        ideas.append(idea)
    return sanitize_data(ideas)


def _idea_sections(ideas: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for index, idea in enumerate(ideas, 1):
        product_ids = idea.get("product_ids", [])
        products = ", ".join(f"`{value}`" for value in product_ids) or "None"
        lines.extend(
            (
                f"### {index}. {sanitize_text(idea['title'])}",
                "",
                f"- Type: `{sanitize_text(idea['idea_type'])}`",
                f"- Rationale: {sanitize_text(idea['rationale'])}",
                f"- Expected impact: {sanitize_text(idea['expected_impact'])}",
                f"- Proposed action: {sanitize_text(idea['proposed_action'])}",
                f"- Target niche: {sanitize_text(idea.get('target_niche', '')) or 'None'}",
                f"- Target keyword: {sanitize_text(idea.get('target_keyword', '')) or 'None'}",
                f"- Products: {products}",
                "- Approval: User approval required before configuration changes.",
                "",
            )
        )
    return lines or ["No actionable ideas were synthesized.", ""]


def run_brainstorm(
    vault_root: Path = DEFAULT_VAULT_ROOT,
    question: str = DEFAULT_QUESTION,
    *,
    product_ids: Sequence[str] | None = None,
    runner: AgentRunner | None = None,
    discussion_agents: Sequence[tuple[str, str]] = DISCUSSION_AGENTS,
) -> Path:
    """Run all Claude calls sequentially and write one ``agent_meeting`` note."""

    clean_question = sanitize_text(question)
    if not clean_question:
        raise ValueError("question must be a non-empty string")
    if not discussion_agents:
        raise ValueError("At least one discussion agent is required")

    products = _selected_products(Path(vault_root), product_ids)
    known_ids = {require_text(note.frontmatter, "product_id") for note in products}
    base_context = {
        "operator_topic": clean_question,
        "products": [note_context(note) for note in products],
        "guardrails": {
            "new_niches_require_user_approval": True,
            "publishing_allowed": False,
        },
    }
    active_runner = runner or AgentRunner("claude")
    opened = active_runner.run(
        CHAIRMAN_NAME,
        CHAIRMAN_QUESTION_INSTRUCTIONS,
        base_context,
        QUESTION_SCHEMA,
    )
    chairman_question = require_text(opened, "question")

    transcript: list[dict[str, Any]] = []
    for agent_name, viewpoint in discussion_agents:
        data = active_runner.run(
            agent_name,
            f"{SPECIALIST_INSTRUCTIONS}\n\nSPECIALIST VIEWPOINT:\n{viewpoint}",
            {
                **base_context,
                "chairman_question": chairman_question,
                "prior_responses": list(transcript),
            },
            RESPONSE_SCHEMA,
        )
        response = _validated_response(data, known_ids)
        transcript.append({"agent_name": agent_name, **response})

    synthesized = active_runner.run(
        CHAIRMAN_NAME,
        SYNTHESIS_INSTRUCTIONS,
        {
            **base_context,
            "chairman_question": chairman_question,
            "transcript": list(transcript),
        },
        SYNTHESIS_SCHEMA,
    )
    summary = require_text(synthesized, "summary")
    ideas = _validated_ideas(synthesized.get("ideas"), known_ids)

    instant = datetime.now(UTC)
    now = instant.replace(microsecond=0)
    timestamp = now.isoformat().replace("+00:00", "Z")
    meeting_id = f"agent-brainstorm-{instant.strftime('%Y%m%dT%H%M%S%fZ')}"
    output_path = Path(vault_root) / "meetings" / f"{safe_slug(meeting_id)}.md"
    frontmatter = {
        "type": "agent_meeting",
        "meeting_id": meeting_id,
        "meeting_date": now.date().isoformat(),
        "product_ids": sorted(known_ids),
        "discussion_agents": [name for name, _viewpoint in discussion_agents],
        "idea_count": len(ideas),
        "ideas": ideas,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    transcript_lines: list[str] = []
    for response in transcript:
        transcript_lines.extend(
            (
                f"### {sanitize_text(response['agent_name'])}",
                "",
                sanitize_text(response["analysis"]),
                "",
            )
        )
    body = "\n".join(
        (
            "# Agent Brainstorm Meeting",
            "",
            "## Chairman Question",
            "",
            chairman_question,
            "",
            "## Sequential Discussion",
            "",
            *transcript_lines,
            "## Chairman Synthesis",
            "",
            summary,
            "",
            "## Actionable Ideas",
            "",
            *_idea_sections(ideas),
            "## Approval Gate",
            "",
            "- These ideas are proposals only. They do not authorize scope expansion, "
            "content creation, or publishing.",
            "- Every new niche requires explicit user approval and must remain within "
            "configured niche limits.",
        )
    )
    return write_note(Path(vault_root), output_path, frontmatter, body)


brainstorm = run_brainstorm
run = run_brainstorm


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a sequential Claude agent brainstorm.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--product-id", action="append", dest="product_ids")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_brainstorm(
            args.vault_root,
            args.question,
            product_ids=args.product_ids,
        )
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
