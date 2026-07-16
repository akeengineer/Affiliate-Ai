#!/usr/bin/env python3
"""Vote Chairman agent: aggregate votes and write a guarded decision note.

Ref: codex/tasks/005-agent-ai-runtime.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        VaultNote,
        cli_main_error,
        discover_notes,
        existing_created_at,
        load_product_candidate,
        load_prompt,
        markdown_bullets,
        note_context,
        product_context,
        require_score,
        require_text,
        safe_slug,
        text_list,
        utc_now,
        write_note,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        VaultNote,
        cli_main_error,
        discover_notes,
        existing_created_at,
        load_product_candidate,
        load_prompt,
        markdown_bullets,
        note_context,
        product_context,
        require_score,
        require_text,
        safe_slug,
        text_list,
        utc_now,
        write_note,
    )


AGENT_NAME = "Vote Chairman Agent"
PROMPT_FILE = "vote-chairman-agent.md"
DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
COMPONENT_SCORE_FIELDS = (
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_score",
)
OUTPUT_SCHEMA = {
    "final_decision": "launch, small_batch_test, watchlist, or reject",
    "decision_summary": "string explaining score, votes, conflicts, and compliance",
    "required_actions": ["string"],
}


def _validate_scored(candidate: VaultNote) -> None:
    for field in COMPONENT_SCORE_FIELDS:
        require_score(candidate.frontmatter, field)
    status = str(candidate.frontmatter.get("status", "")).strip().lower()
    if status != "scored" and candidate.frontmatter.get("product_opportunity_score") in (None, ""):
        raise AgentOutputError(
            "Vote Chairman requires status=scored or a product_opportunity_score"
        )


def _validate_votes(votes: list[VaultNote]) -> None:
    if len(votes) < 3:
        raise AgentOutputError("Vote Chairman requires at least three agent_vote notes")
    for vote_note in votes:
        vote = require_text(vote_note.frontmatter, "vote")
        if vote not in DECISIONS:
            raise AgentOutputError(f"Invalid agent vote {vote!r} in {vote_note.path.name}")
        require_score(vote_note.frontmatter, "confidence_score")
        require_text(vote_note.frontmatter, "agent_name")


def _select_compliance(notes: list[VaultNote]) -> VaultNote:
    if not notes:
        raise AgentOutputError("Vote Chairman requires a compliance_result note")
    live_notes = [note for note in notes if "samples" not in note.path.parts]
    selected = max(
        live_notes or notes,
        key=lambda note: (str(note.frontmatter.get("updated_at", "")), str(note.path)),
    )
    status = require_text(selected.frontmatter, "compliance_status")
    if status not in {"approved", "needs_review", "blocked"}:
        raise AgentOutputError(f"Invalid compliance status {status!r}")
    return selected


def _safe_decision(requested: str, compliance_status: str) -> str:
    if compliance_status == "blocked":
        return "reject"
    if compliance_status == "needs_review" and requested in {"launch", "small_batch_test"}:
        return "watchlist"
    return requested


def run_vote_chairman(
    vault_root: Path,
    product_id: str,
    *,
    runner: AgentRunner | None = None,
) -> Path:
    candidate = load_product_candidate(vault_root, product_id)
    _validate_scored(candidate)
    votes = discover_notes(vault_root, "agent_vote", product_id=product_id)
    _validate_votes(votes)
    compliance = _select_compliance(
        discover_notes(vault_root, "compliance_result", product_id=product_id)
    )
    context: dict[str, Any] = product_context(vault_root, candidate)
    context["votes"] = [note_context(note) for note in votes]
    context["selected_compliance"] = note_context(compliance)

    active_runner = runner or AgentRunner.for_agent("vote_chairman")
    data = active_runner.run(
        AGENT_NAME,
        load_prompt(PROMPT_FILE),
        context,
        OUTPUT_SCHEMA,
    )
    requested = require_text(data, "final_decision").lower()
    if requested not in DECISIONS:
        raise AgentOutputError(f"Invalid final decision {requested!r}")
    decision_summary = require_text(data, "decision_summary")
    required_actions = text_list(data, "required_actions")
    compliance_status = require_text(compliance.frontmatter, "compliance_status")
    final_decision = _safe_decision(requested, compliance_status)
    if final_decision != requested:
        required_actions.insert(
            0,
            f"Resolve compliance status `{compliance_status}` before considering `{requested}`.",
        )
        decision_summary = (
            f"Safety gate changed the proposed `{requested}` decision to `{final_decision}`. "
            f"{decision_summary}"
        )

    timestamp = utc_now()
    slug = safe_slug(product_id)
    decision_id = f"decision-{slug}-vote-chairman"
    output_path = Path(vault_root) / "decisions" / f"{decision_id}.md"
    frontmatter = {
        "type": "decision",
        "decision_id": decision_id,
        "product_id": product_id,
        "final_decision": final_decision,
        "vote_count": len(votes),
        "compliance_status": compliance_status,
        "required_actions": required_actions,
        "decision_summary": decision_summary,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    vote_lines = [
        f"- {require_text(note.frontmatter, 'agent_name')}: "
        f"{require_text(note.frontmatter, 'vote')} "
        f"(confidence {require_score(note.frontmatter, 'confidence_score')})"
        for note in votes
    ]
    body = "\n".join(
        (
            "# Vote Chairman Decision",
            "",
            "## Objective",
            "",
            f"Aggregate validated votes for `{product_id}`.",
            "",
            "## Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            f"- Agent votes: {len(votes)}",
            f"- Compliance result: `{compliance.path.name}`",
            "",
            "## Score summary",
            "",
            "- Product opportunity score: "
            f"{candidate.frontmatter.get('product_opportunity_score', 'recorded as scored')}",
            f"- Score decision: {candidate.frontmatter.get('score_decision', 'not recorded')}",
            "",
            "## Votes",
            "",
            *vote_lines,
            "",
            "## Decision",
            "",
            f"**{final_decision}** — {decision_summary}",
            "",
            "## Required next actions",
            "",
            markdown_bullets(required_actions),
        )
    )
    return write_note(vault_root, output_path, frontmatter, body)


run = run_vote_chairman


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a guarded decision with Claude CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_vote_chairman(args.vault_root, args.product_id)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
