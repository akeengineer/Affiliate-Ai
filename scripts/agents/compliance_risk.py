#!/usr/bin/env python3
"""Compliance Risk agent: create a compliance result with AGY CLI.

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
        AgentOutputError,
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
        AgentOutputError,
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


AGENT_NAME = "Compliance Risk Agent"
PROMPT_FILE = "compliance-risk-agent.md"
ALLOWED_STATUSES = {"approved", "needs_review", "blocked"}
OUTPUT_SCHEMA = {
    "compliance_status": "approved, needs_review, or blocked",
    "disclosure_required": "boolean",
    "risk_score": "number 0-100",
    "compliance_findings": "string",
    "blocked_reasons": ["string"],
    "required_disclosures": ["string"],
    "notes": "string or null",
}


def _required_boolean(data: dict[str, object], field: str) -> bool:
    value = data.get(field)
    if not isinstance(value, bool):
        raise AgentOutputError(f"Agent output field {field!r} must be a boolean")
    return value


def run_compliance_risk(
    vault_root: Path,
    product_id: str,
    *,
    runner: AgentRunner | None = None,
) -> Path:
    candidate = load_product_candidate(vault_root, product_id)
    active_runner = runner or AgentRunner.for_agent("compliance_risk")
    data = active_runner.run(
        AGENT_NAME,
        load_prompt(PROMPT_FILE),
        product_context(vault_root, candidate),
        OUTPUT_SCHEMA,
    )

    status = require_text(data, "compliance_status").lower()
    if status not in ALLOWED_STATUSES:
        raise AgentOutputError(
            "Compliance status must be approved, needs_review, or blocked"
        )
    disclosure_required = _required_boolean(data, "disclosure_required")
    risk_score = require_score(data, "risk_score")
    findings = require_text(data, "compliance_findings")
    blocked_reasons = text_list(data, "blocked_reasons")
    disclosures = text_list(data, "required_disclosures")
    notes = optional_text(data, "notes")
    if status == "blocked" and not blocked_reasons:
        raise AgentOutputError("Blocked compliance output must include blocked_reasons")
    if status == "approved" and disclosure_required and not disclosures:
        raise AgentOutputError("Approved output requiring disclosure must name the disclosure")

    timestamp = utc_now()
    slug = safe_slug(product_id)
    compliance_id = f"compliance-{slug}-risk-agent"
    output_path = Path(vault_root) / "compliance" / f"{compliance_id}.md"
    frontmatter = {
        "type": "compliance_result",
        "compliance_id": compliance_id,
        "product_id": product_id,
        "compliance_status": status,
        "disclosure_required": disclosure_required,
        "risk_score": risk_score,
        "blocked_reasons": blocked_reasons,
        "notes": notes,
        "created_at": existing_created_at(output_path, timestamp),
        "updated_at": timestamp,
        "status": "complete",
    }
    body = "\n".join(
        (
            "# Compliance Result",
            "",
            "## Objective",
            "",
            f"Assess compliance and platform risk for `{product_id}`.",
            "",
            "## Inputs read",
            "",
            f"- Product candidate: `{candidate.path.name}`",
            "",
            "## Compliance findings",
            "",
            findings,
            "",
            "## Blocked claims or risks",
            "",
            markdown_bullets(blocked_reasons),
            "",
            "## Required disclosures",
            "",
            markdown_bullets(disclosures),
            "",
            "## Score updates",
            "",
            f"- Risk score: {risk_score}",
            f"- Compliance status: {status}",
        )
    )
    written = write_note(vault_root, output_path, frontmatter, body)
    update_candidate(
        vault_root,
        candidate,
        {
            "risk_score": risk_score,
            "compliance_result_note": note_reference(vault_root, written),
        },
        timestamp=timestamp,
    )
    return written


run = run_compliance_risk


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a compliance_result with AGY CLI.")
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--product-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = run_compliance_risk(args.vault_root, args.product_id)
    except Exception as exc:
        print(cli_main_error(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
