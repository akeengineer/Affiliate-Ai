#!/usr/bin/env python3
"""Commission Economics agent: create a commission signal with Codex CLI.

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
        cli_main_error,
        existing_created_at,
        load_product_candidate,
        load_prompt,
        markdown_bullets,
        note_reference,
        optional_text,
        product_context,
        require_nonnegative_int,
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
        require_nonnegative_int,
        require_score,
        require_text,
        safe_slug,
        text_list,
        update_candidate,
        utc_now,
        write_note,
    )


AGENT_NAME = "Commission Economics Agent"
PROMPT_FILE = "commission-economics-agent.md"
OUTPUT_SCHEMA = {
    "program_name": "string from supplied evidence",
    "network": "string or null",
    "commission_rate_text": "string or null",
    "commission_score": "number 0-100",
    "payout_window_days": "non-negative integer or null when evidence is missing",
    "commission_findings": "string",
    "payout_risk_findings": "string",
    "evidence_summary": "string",
    "source_url": "string or null; never an affiliate URL",
    "missing_signals": ["string"],
}


def run_commission_econ(
    vault_root: Path,
    product_id: str,
    *,
    runner: AgentRunner | None = None,
) -> Path:
    candidate = load_product_candidate(vault_root, product_id)
    active_runner = runner or AgentRunner.for_agent("commission_econ")
    data = active_runner.run(
        AGENT_NAME,
        load_prompt(PROMPT_FILE),
        product_context(vault_root, candidate),
        OUTPUT_SCHEMA,
    )

    program_name = require_text(data, "program_name")
    network = optional_text(data, "network")
    rate_text = optional_text(data, "commission_rate_text")
    commission_score = require_score(data, "commission_score")
    raw_payout_days = data.get("payout_window_days")
    payout_days = (
        None
        if raw_payout_days in (None, "", "unknown")
        else require_nonnegative_int(data, "payout_window_days")
    )
    commission_findings = require_text(data, "commission_findings")
    payout_findings = require_text(data, "payout_risk_findings")
    evidence_summary = require_text(data, "evidence_summary")
    source_url = optional_text(data, "source_url")
    missing = text_list(data, "missing_signals")

    timestamp = utc_now()
    slug = safe_slug(product_id)
    signal_id = f"commission-{slug}-commission-econ"
    output_path = Path(vault_root) / "commissions" / f"{signal_id}.md"
    frontmatter = {
        "type": "commission_signal",
        "signal_id": signal_id,
        "product_id": product_id,
        "program_name": program_name,
        "commission_score": commission_score,
        "payout_window_days": payout_days,
        "commission_rate_text": rate_text,
        "network": network,
        "evidence_summary": evidence_summary,
        "source_url": source_url,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    body = "\n".join(
        (
            "# Commission Economics Signal",
            "",
            "## Objective",
            "",
            f"Evaluate commission economics for `{product_id}`.",
            "",
            "## Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            f"- Program: {program_name}",
            "",
            "## Commission findings",
            "",
            commission_findings,
            "",
            "## Payout and risk findings",
            "",
            payout_findings,
            "",
            "## Score updates",
            "",
            f"- Commission score: {commission_score}",
            f"- Payout window: {f'{payout_days} days' if payout_days is not None else 'unknown'}",
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
            "commission_score": commission_score,
            "commission_signal_note": note_reference(vault_root, written),
        },
        timestamp=timestamp,
    )
    return written


run = run_commission_econ


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a commission_signal with Codex CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_commission_econ(args.vault_root, args.product_id)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
