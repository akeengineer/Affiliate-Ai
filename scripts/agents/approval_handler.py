#!/usr/bin/env python3
"""Record a user's idea decision and stage approvals for the next nightly run.

Ref: codex/tasks/008-agent-brainstorming.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

try:
    from .agent_runner import (
        cli_main_error,
        note_reference,
        read_note,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )
    from .learn_from_results import (
        DEFAULT_CONFIG_PATH,
        load_learning_config,
        load_nightly_config,
        write_nightly_config,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        cli_main_error,
        note_reference,
        read_note,
        sanitize_data,
        sanitize_text,
        utc_now,
        write_note,
    )
    from learn_from_results import (  # type: ignore
        DEFAULT_CONFIG_PATH,
        load_learning_config,
        load_nightly_config,
        write_nightly_config,
    )


APPROVAL_MARKER_START = "<!-- phase5-approval:start -->"
APPROVAL_MARKER_END = "<!-- phase5-approval:end -->"


def _normalise_decision(decision: str) -> str:
    value = str(decision).strip().lower()
    aliases = {
        "approve": "approved",
        "approved": "approved",
        "reject": "rejected",
        "rejected": "rejected",
    }
    try:
        return aliases[value]
    except KeyError as exc:
        raise ValueError("decision must be approve or reject") from exc


def _approval_body(body: str, decision: str, timestamp: str) -> str:
    section = "\n".join(
        (
            APPROVAL_MARKER_START,
            "## User Decision",
            "",
            f"- Decision: **{decision}**",
            f"- Recorded at: `{timestamp}`",
            "- Actor: user",
            APPROVAL_MARKER_END,
        )
    )
    pattern = re.compile(
        rf"\n?{re.escape(APPROVAL_MARKER_START)}.*?{re.escape(APPROVAL_MARKER_END)}",
        re.DOTALL,
    )
    base = pattern.sub("", body).rstrip()
    return f"{base}\n\n{section}" if base else section


def _append_unique(values: Any, value: str) -> list[str]:
    current = list(values) if isinstance(values, list) else []
    if value not in current:
        current.append(value)
    return current


def _stage_approved_idea(
    state: dict[str, Any],
    proposal: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    proposal_id = str(proposal["proposal_id"])
    idea_type = str(proposal.get("idea_type", "workflow_change"))
    target_niche = sanitize_text(proposal.get("target_niche", "")).lower()
    target_keyword = sanitize_text(proposal.get("target_keyword", ""))
    active_niches = list(state.get("active_niches", []))
    niche_limits = config["niche_limits"]

    if idea_type in {"new_niche", "new_category"}:
        if not target_niche:
            raise ValueError("Approved new-niche proposal is missing target_niche")
        if target_niche not in set(niche_limits["allowed_niches"]):
            raise ValueError(
                f"Niche {target_niche!r} is outside learning.yaml allowed_niches; "
                "update the allowlist before approval"
            )
        if target_niche not in active_niches:
            if len(active_niches) >= int(niche_limits["max_active_niches"]):
                raise ValueError("Cannot approve niche: max_active_niches would be exceeded")
            active_niches.append(target_niche)

    if target_niche and target_niche not in active_niches:
        raise ValueError(
            f"Proposal targets inactive niche {target_niche!r}; approve its new-niche "
            "proposal first"
        )

    search_keywords = state.get("search_keywords", {})
    if not isinstance(search_keywords, Mapping):
        search_keywords = {}
    search_keywords = {str(niche): list(values) for niche, values in search_keywords.items()}
    niche_priorities = state.get("niche_priorities", {})
    if not isinstance(niche_priorities, Mapping):
        niche_priorities = {}
    niche_priorities = dict(niche_priorities)
    for niche in active_niches:
        search_keywords.setdefault(niche, [])
        niche_priorities.setdefault(niche, 1.0)

    if idea_type == "search_keyword":
        if not target_niche or not target_keyword:
            raise ValueError(
                "Approved search_keyword proposal needs target_niche and target_keyword"
            )
        keywords = search_keywords[target_niche]
        maximum = int(config["keyword_limits"]["max_keywords_per_niche"])
        if target_keyword not in keywords:
            if len(keywords) >= maximum:
                raise ValueError(f"Keyword limit reached for niche {target_niche!r}")
            keywords.append(target_keyword)

    approved_ideas = list(state.get("approved_ideas", []))
    if not any(
        isinstance(item, Mapping) and item.get("proposal_id") == proposal_id
        for item in approved_ideas
    ):
        approved_ideas.append(
            {
                "proposal_id": proposal_id,
                "idea_type": idea_type,
                "title": sanitize_text(proposal.get("title", proposal_id)),
                "target_niche": target_niche,
                "target_keyword": target_keyword,
                "rationale": sanitize_text(proposal.get("rationale", "")),
                "expected_impact": sanitize_text(proposal.get("expected_impact", "")),
                "proposed_action": sanitize_text(proposal.get("proposed_action", "")),
            }
        )
    state.update(
        {
            "active_niches": active_niches,
            "search_keywords": search_keywords,
            "niche_priorities": niche_priorities,
            "approved_proposal_ids": _append_unique(
                state.get("approved_proposal_ids"), proposal_id
            ),
            "approved_ideas": approved_ideas,
        }
    )
    return state


def handle_approval(
    proposal_path: Path,
    decision: str,
    *,
    vault_root: Path | None = None,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> Path:
    """Mark one proposal and, only on approval, update next-nightly state."""

    path = Path(proposal_path)
    note = read_note(path)
    if note.frontmatter.get("type") != "idea_proposal":
        raise ValueError(f"Expected idea_proposal note: {path}")
    root = Path(vault_root) if vault_root is not None else path.parent.parent
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"Proposal path escapes vault root: {path}")
    resolved_decision = _normalise_decision(decision)
    prior = str(note.frontmatter.get("approval_status", "pending"))
    if prior in {"approved", "rejected"} and prior != resolved_decision:
        raise ValueError(f"Proposal already has final decision {prior!r}")

    timestamp = utc_now()
    frontmatter = dict(note.frontmatter)
    frontmatter.update(
        {
            "approval_status": resolved_decision,
            "approval_actor": "user",
            "decided_at": timestamp,
            "updated_at": timestamp,
            "status": resolved_decision,
        }
    )
    if resolved_decision == "approved":
        config = load_learning_config(config_path)
        nightly_path, state = load_nightly_config(root, config, timestamp=timestamp)
        state = _stage_approved_idea(state, frontmatter, config)
        state["updated_at"] = timestamp
        state["status"] = "active"
        write_nightly_config(
            root,
            nightly_path,
            state,
            reason=f"User approved proposal {frontmatter['proposal_id']} for the next nightly run.",
            config=config,
        )
        frontmatter["nightly_config_note"] = note_reference(root, nightly_path)

    body = _approval_body(note.body, resolved_decision, timestamp)
    return write_note(root, path, sanitize_data(frontmatter), body)


process_approval = handle_approval
run = handle_approval


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Approve or reject one idea proposal.")
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    parser.add_argument("--vault-root", type=Path, default=None)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = handle_approval(
            args.proposal,
            args.decision,
            vault_root=args.vault_root,
            config_path=args.config,
        )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
