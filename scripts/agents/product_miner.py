#!/usr/bin/env python3
"""Rank existing product candidates without scoring, voting, or drafting content.

Ref: codex/tasks/005-agent-ai-runtime.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

try:  # Support both package imports and direct script execution.
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        VaultNote,
        cli_main_error,
        discover_notes,
        load_prompt,
        markdown_bullets,
        note_context,
        product_context,
        require_score,
        require_text,
        sanitize_text,
        text_list,
        update_candidate,
        utc_now,
    )
except ImportError:  # pragma: no cover - exercised when invoked as a file.
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        AgentOutputError,
        AgentRunner,
        VaultNote,
        cli_main_error,
        discover_notes,
        load_prompt,
        markdown_bullets,
        note_context,
        product_context,
        require_score,
        require_text,
        sanitize_text,
        text_list,
        update_candidate,
        utc_now,
    )


AGENT_NAME = "Product Miner Agent"
PROMPT_FILE = "product-miner-agent.md"
_SECTION_START = "<!-- agent-runtime:product-miner:start -->"
_SECTION_END = "<!-- agent-runtime:product-miner:end -->"
OUTPUT_SCHEMA = {
    "ranked_candidates": [
        {
            "product_id": "string from context",
            "rank": "positive integer; every candidate appears exactly once",
            "interest_score": "number 0-100 based on supplied evidence",
            "rationale": "short evidence-based string",
            "missing_signals": ["string"],
        }
    ]
}


def _positive_rank(item: Mapping[str, Any]) -> int:
    value = item.get("rank")
    if isinstance(value, bool):
        raise AgentOutputError("Product Miner rank must be a positive integer")
    try:
        rank = int(value)
    except (TypeError, ValueError) as exc:
        raise AgentOutputError("Product Miner rank must be a positive integer") from exc
    if rank < 1 or str(value).strip() not in {str(rank), f"{rank}.0"}:
        raise AgentOutputError("Product Miner rank must be a positive integer")
    return rank


def _validate_rankings(
    data: Mapping[str, Any], candidates: list[VaultNote]
) -> list[dict[str, Any]]:
    raw_rankings = data.get("ranked_candidates")
    if not isinstance(raw_rankings, list):
        raise AgentOutputError("Product Miner output must include ranked_candidates as a list")

    known_ids = {require_text(note.frontmatter, "product_id") for note in candidates}
    rankings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_ranks: set[int] = set()
    for raw_item in raw_rankings:
        if not isinstance(raw_item, Mapping):
            raise AgentOutputError("Each Product Miner ranking must be an object")
        product_id = require_text(raw_item, "product_id")
        if product_id not in known_ids:
            raise AgentOutputError(f"Product Miner returned unknown product_id={product_id!r}")
        if product_id in seen_ids:
            raise AgentOutputError(f"Product Miner returned duplicate product_id={product_id!r}")
        rank = _positive_rank(raw_item)
        if rank in seen_ranks:
            raise AgentOutputError(f"Product Miner returned duplicate rank={rank}")
        rankings.append(
            {
                "product_id": product_id,
                "rank": rank,
                "interest_score": require_score(raw_item, "interest_score"),
                "rationale": require_text(raw_item, "rationale"),
                "missing_signals": text_list(raw_item, "missing_signals"),
            }
        )
        seen_ids.add(product_id)
        seen_ranks.add(rank)

    if seen_ids != known_ids:
        missing = ", ".join(sorted(known_ids - seen_ids))
        raise AgentOutputError(f"Product Miner omitted candidate(s): {missing}")
    expected_ranks = set(range(1, len(candidates) + 1))
    if seen_ranks != expected_ranks:
        raise AgentOutputError("Product Miner ranks must be contiguous starting at 1")
    return sorted(rankings, key=lambda item: item["rank"])


def _ranking_body(candidate: VaultNote, ranking: Mapping[str, Any]) -> str:
    section = "\n".join(
        (
            _SECTION_START,
            "## Product Miner Ranking",
            "",
            "### Objective",
            "",
            "Rank this existing candidate from supplied vault evidence without changing component scores.",
            "",
            "### Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            "",
            "### Candidate products",
            "",
            f"- Rank: {ranking['rank']}",
            f"- Evidence-based interest score: {ranking['interest_score']}",
            f"- Rationale: {sanitize_text(ranking['rationale'])}",
            "",
            "### Missing signals",
            "",
            markdown_bullets(ranking["missing_signals"]),
            "",
            "### Next note action",
            "",
            "- Gather the listed evidence, then run deterministic scoring before any vote or content work.",
            _SECTION_END,
        )
    )
    pattern = re.compile(
        rf"\n?{re.escape(_SECTION_START)}.*?{re.escape(_SECTION_END)}", re.DOTALL
    )
    base = pattern.sub("", candidate.body).rstrip()
    return f"{base}\n\n{section}" if base else section


def run_product_miner(
    vault_root: Path = DEFAULT_VAULT_ROOT,
    *,
    runner: AgentRunner | None = None,
) -> list[Path]:
    """Rank every candidate note and persist a managed ranking section."""

    discovered = discover_notes(vault_root, "product_candidate")
    candidates_by_id: dict[str, VaultNote] = {}
    for note in discovered:
        product_id = require_text(note.frontmatter, "product_id")
        existing = candidates_by_id.get(product_id)
        if existing is None or (
            "samples" in existing.path.parts and "samples" not in note.path.parts
        ):
            candidates_by_id[product_id] = note
    candidates = sorted(candidates_by_id.values(), key=lambda note: str(note.path))
    if not candidates:
        raise ValueError(f"No product_candidate notes found below {vault_root}")
    context = {
        "candidates": [note_context(note) for note in candidates],
        "candidate_evidence": [product_context(vault_root, note) for note in candidates],
    }
    active_runner = runner or AgentRunner.for_agent("product_miner")
    data = active_runner.run(AGENT_NAME, load_prompt(PROMPT_FILE), context, OUTPUT_SCHEMA)
    rankings = _validate_rankings(data, candidates)

    by_id = {require_text(note.frontmatter, "product_id"): note for note in candidates}
    timestamp = utc_now()
    written: list[Path] = []
    for ranking in rankings:
        candidate = by_id[ranking["product_id"]]
        written.append(
            update_candidate(
                vault_root,
                candidate,
                {},
                body=_ranking_body(candidate, ranking),
                timestamp=timestamp,
            )
        )
    return written


run = run_product_miner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank product_candidate notes with Claude CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        paths = run_product_miner(args.vault_root)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "ranked_candidates": [str(path) for path in paths]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
