#!/usr/bin/env python3
"""Content Virality agent: score fit and persist a marketplace signal.

The marketplace component score is copied from the candidate unchanged; this
agent only updates content-fit and competition-gap component fields.

Ref: codex/tasks/005-agent-ai-runtime.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentRunner,
        AgentOutputError,
        cli_main_error,
        existing_created_at,
        load_product_candidate,
        load_prompt,
        markdown_bullets,
        note_reference,
        optional_text,
        product_context,
        require_score,
        require_text,
        safe_slug,
        text_list,
        update_candidate,
        utc_now,
        write_note,
    )
except ImportError:  # pragma: no cover
    from agent_runner import (  # type: ignore
        DEFAULT_VAULT_ROOT,
        AgentRunner,
        AgentOutputError,
        cli_main_error,
        existing_created_at,
        load_product_candidate,
        load_prompt,
        markdown_bullets,
        note_reference,
        optional_text,
        product_context,
        require_score,
        require_text,
        safe_slug,
        text_list,
        update_candidate,
        utc_now,
        write_note,
    )


AGENT_NAME = "Content Virality Agent"
PROMPT_FILE = "content-virality-agent.md"
OUTPUT_SCHEMA = {
    "content_fit_score": "number 0-100",
    "competition_gap_score": "number 0-100",
    "category_rank": "string or integer from supplied marketplace evidence; use unknown if absent",
    "source": "string naming supplied marketplace evidence",
    "content_fit_findings": "string; analysis only, no hooks or drafts",
    "competition_gap_findings": "string",
    "evidence_summary": "string",
    "source_url": "string or null; never an affiliate URL",
    "risks_and_caveats": ["string"],
}


def _candidate_marketplace_score(candidate_frontmatter: dict[str, object]) -> int | float:
    if "marketplace_rank_score" not in candidate_frontmatter:
        raise AgentOutputError("Candidate is missing marketplace_rank_score")
    return require_score(candidate_frontmatter, "marketplace_rank_score")


def run_content_virality(
    vault_root: Path,
    product_id: str,
    *,
    runner: AgentRunner | None = None,
) -> Path:
    candidate = load_product_candidate(vault_root, product_id)
    active_runner = runner or AgentRunner.for_agent("content_virality")
    data = active_runner.run(
        AGENT_NAME,
        load_prompt(PROMPT_FILE),
        product_context(vault_root, candidate),
        OUTPUT_SCHEMA,
    )

    content_fit_score = require_score(data, "content_fit_score")
    competition_gap_score = require_score(data, "competition_gap_score")
    category_rank = require_text(data, "category_rank")
    source = require_text(data, "source")
    content_findings = require_text(data, "content_fit_findings")
    competition_findings = require_text(data, "competition_gap_findings")
    evidence_summary = require_text(data, "evidence_summary")
    source_url = optional_text(data, "source_url")
    risks = text_list(data, "risks_and_caveats")
    marketplace_score = _candidate_marketplace_score(candidate.frontmatter)
    marketplace = require_text(candidate.frontmatter, "marketplace")

    timestamp = utc_now()
    slug = safe_slug(product_id)
    signal_id = f"marketplace-{slug}-content-virality"
    output_path = Path(vault_root) / "marketplace-signals" / f"{signal_id}.md"
    frontmatter = {
        "type": "marketplace_signal",
        "signal_id": signal_id,
        "product_id": product_id,
        "marketplace": marketplace,
        "category_rank": category_rank,
        "marketplace_rank_score": marketplace_score,
        "source": source,
        "evidence_summary": evidence_summary,
        "source_url": source_url,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    body = "\n".join(
        (
            "# Content Virality Fit Signal",
            "",
            "## Objective",
            "",
            f"Evaluate repeatable content fit for `{product_id}` without drafting content.",
            "",
            "## Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            f"- Marketplace evidence source: {source}",
            "",
            "## Content fit findings",
            "",
            content_findings,
            "",
            "## Competition gap findings",
            "",
            competition_findings,
            "",
            "## Score updates",
            "",
            f"- Content fit score: {content_fit_score}",
            f"- Competition gap score: {competition_gap_score}",
            f"- Marketplace rank score: {marketplace_score} (preserved)",
            "",
            "## Risks and caveats",
            "",
            markdown_bullets(risks),
        )
    )
    written = write_note(vault_root, output_path, frontmatter, body)
    update_candidate(
        vault_root,
        candidate,
        {
            "content_fit_score": content_fit_score,
            "competition_gap_score": competition_gap_score,
            "marketplace_signal_note": note_reference(vault_root, written),
        },
        timestamp=timestamp,
    )
    return written


run = run_content_virality


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a fit marketplace_signal with Claude CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_content_virality(args.vault_root, args.product_id)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
