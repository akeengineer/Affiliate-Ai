#!/usr/bin/env python3
"""Demand Intelligence agent: create a trend signal for one candidate.

Ref: codex/tasks/005-agent-ai-runtime.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    from .agent_runner import (
        DEFAULT_VAULT_ROOT,
        AgentRunner,
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


AGENT_NAME = "Demand Intelligence Agent"
PROMPT_FILE = "demand-intelligence-agent.md"
OUTPUT_SCHEMA = {
    "demand_score": "number 0-100",
    "trend_velocity_score": "number 0-100",
    "source": "string naming supplied evidence",
    "signal_date": "YYYY-MM-DD",
    "demand_findings": "string",
    "trend_findings": "string",
    "evidence_summary": "string",
    "source_url": "string or null; never an affiliate URL",
    "missing_signals": ["string"],
}


def _signal_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError("Demand agent signal_date must use YYYY-MM-DD") from exc


def run_demand_intel(
    vault_root: Path,
    product_id: str,
    *,
    runner: AgentRunner | None = None,
) -> Path:
    candidate = load_product_candidate(vault_root, product_id)
    active_runner = runner or AgentRunner.for_agent("demand_intel")
    data = active_runner.run(
        AGENT_NAME,
        load_prompt(PROMPT_FILE),
        product_context(vault_root, candidate),
        OUTPUT_SCHEMA,
    )

    demand_score = require_score(data, "demand_score")
    trend_score = require_score(data, "trend_velocity_score")
    source = require_text(data, "source")
    signal_date = _signal_date(require_text(data, "signal_date"))
    demand_findings = require_text(data, "demand_findings")
    trend_findings = require_text(data, "trend_findings")
    evidence_summary = require_text(data, "evidence_summary")
    source_url = optional_text(data, "source_url")
    missing = text_list(data, "missing_signals")

    timestamp = utc_now()
    slug = safe_slug(product_id)
    signal_id = f"trend-{slug}-demand-intel"
    output_path = Path(vault_root) / "trends" / f"{signal_id}.md"
    frontmatter = {
        "type": "trend_signal",
        "signal_id": signal_id,
        "product_id": product_id,
        "source": source,
        "signal_date": signal_date,
        "trend_velocity_score": trend_score,
        "evidence_summary": evidence_summary,
        "source_url": source_url,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    body = "\n".join(
        (
            "# Demand Intelligence Signal",
            "",
            "## Objective",
            "",
            f"Assess demand and trend momentum for `{product_id}`.",
            "",
            "## Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            f"- Evidence source: {source}",
            "",
            "## Demand findings",
            "",
            demand_findings,
            "",
            "## Trend findings",
            "",
            trend_findings,
            "",
            "## Score updates",
            "",
            f"- Demand score: {demand_score}",
            f"- Trend velocity score: {trend_score}",
            "",
            "## Missing signals",
            "",
            markdown_bullets(missing),
        )
    )
    written = write_note(vault_root, output_path, frontmatter, body)
    update_candidate(
        vault_root,
        candidate,
        {
            "demand_score": demand_score,
            "trend_velocity_score": trend_score,
            "trend_signal_note": note_reference(vault_root, written),
        },
        timestamp=timestamp,
    )
    return written


run = run_demand_intel


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a demand trend_signal with Claude CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_demand_intel(args.vault_root, args.product_id)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
