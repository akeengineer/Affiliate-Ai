#!/usr/bin/env python3
"""Phase 3A CLI Dashboard Summary.

Read-only operator view of a single product's lifecycle state, joined across
existing Phase 2 artifacts (and optional, gitignored vault business memory).

This tool never writes to the vault, never calls external APIs, and never
generates affiliate content. It prints a dashboard to stdout and, only with
--write, also emits a tmp artifact.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from score_product import read_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE2E_ROOT = REPO_ROOT / "tmp" / "phase2e-import-score-report"
SCORES_DIR = PHASE2E_ROOT / "scores"
HERMES_DIR = REPO_ROOT / "tmp" / "phase2f-hermes"
GOVERNANCE_DIR = REPO_ROOT / "tmp" / "phase2j-hermes-governance"
VAULT_PRODUCTS_DIR = REPO_ROOT / "vault" / "products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault" / "decisions"
DASHBOARD_DIR = REPO_ROOT / "tmp" / "phase3a-dashboard"

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")
WEEK_RE = re.compile(r"^[0-9]{4}-W[0-9]{2}$")

# ── Scrubbing patterns (output must never contain any of these) ───────────────
PRIVATE_VAULT_PATHS = (
    "vault/products",
    "vault/trends",
    "vault/marketplace-signals",
    "vault/commissions",
    "vault/meetings",
    "vault/decisions",
    "vault/contents",
    "vault/compliance",
    "vault/reports",
    "vault/.obsidian",
)
AFFILIATE_URL_PATTERNS = (
    "aff=",
    "affiliate=",
    "tag=",
    "partner=",
    "sp_atk=",
    "bit.ly",
    "amzn.to",
    "shopee.link",
)
CONTENT_MARKERS = (
    "content_draft",
    "campaign_copy",
    "tiktok_script",
    "hook_text",
    "blog_post",
    "autopublish",
)
SECRET_RES = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"Bearer [A-Za-z0-9]{20,}"),
)

STDOUT_FIELDS = (
    "product_id",
    "product_name",
    "product_opportunity_score",
    "score_decision",
    "confidence_score",
    "report_status",
    "hermes_summary_status",
    "governance_summary_status",
    "promote_status",
    "decision_status",
    "finalization_status",
    "next_allowed_action",
)


class DashboardError(Exception):
    """Raised for any validation failure; message is printed to stderr."""


def _now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_frontmatter(path: Path) -> dict[str, Any] | None:
    """Return frontmatter dict for an optional artifact, or None if absent/malformed."""
    if not path.is_file():
        return None
    try:
        frontmatter, _body = read_frontmatter(path)
    except (ValueError, yaml.YAMLError):
        return None
    return frontmatter if isinstance(frontmatter, dict) else None


def _fm_str(frontmatter: dict[str, Any] | None, key: str) -> str | None:
    """Return a stripped, non-empty string for a frontmatter field, else None."""
    if not frontmatter:
        return None
    value = frontmatter.get(key)
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _check_guardrails() -> None:
    if os.environ.get("ENABLE_AUTOPUBLISH") == "true":
        raise DashboardError("ENABLE_AUTOPUBLISH=true is not allowed")
    if os.environ.get("ENABLE_OPENAI_API_DIRECT") == "true":
        raise DashboardError("ENABLE_OPENAI_API_DIRECT=true is not allowed")


def _validate_inputs(product_id: str, week: str) -> None:
    if not PRODUCT_ID_RE.match(product_id):
        raise DashboardError(f"product-id must match ^[a-z0-9-]+$, got: {product_id!r}")
    if not WEEK_RE.match(week):
        raise DashboardError(f"week must match ^[0-9]{{4}}-W[0-9]{{2}}$, got: {week!r}")


def _read_anchor(product_id: str) -> dict[str, Any]:
    score_path = SCORES_DIR / f"{product_id}.json"
    if not score_path.is_file():
        rel = score_path.relative_to(REPO_ROOT)
        raise DashboardError(
            f"score JSON not found for product-id '{product_id}': expected {rel}"
        )
    try:
        data = json.loads(score_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DashboardError(f"score JSON is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise DashboardError("score JSON must decode to an object")
    json_product_id = str(data.get("product_id", "")).strip()
    if json_product_id != product_id:
        raise DashboardError(
            f"score JSON product_id {json_product_id!r} does not match CLI product-id {product_id!r}"
        )
    return data


def build_dashboard(product_id: str, week: str) -> dict[str, Any]:
    """Join Phase 2 artifacts (+ optional vault state) into a dashboard record."""
    anchor = _read_anchor(product_id)

    # ── Pipeline statuses from tmp artifacts ─────────────────────────────────
    weekly_fm = _safe_frontmatter(PHASE2E_ROOT / f"weekly-report-{week}.md")
    report_status = "generated" if weekly_fm and weekly_fm.get("type") == "weekly_report" else "missing"

    hermes_fm = _safe_frontmatter(HERMES_DIR / f"operational-summary-{week}.md")
    hermes_summary_status = "complete" if _fm_str(hermes_fm, "status") == "complete" else "missing"

    gov_fm = _safe_frontmatter(GOVERNANCE_DIR / f"governance-summary-{week}.md")
    governance_summary_status = "complete" if _fm_str(gov_fm, "status") == "complete" else "missing"
    gov_promoted = _fm_str(gov_fm, "promoted_status")
    gov_decision = _fm_str(gov_fm, "decision_status")
    gov_finalization = _fm_str(gov_fm, "finalization_status")
    gov_next_action = _fm_str(gov_fm, "next_allowed_action")

    # ── Optional vault business memory (existence + status only) ──────────────
    vault_product_fm = _safe_frontmatter(VAULT_PRODUCTS_DIR / f"{product_id}.md")
    vault_product_has_status = _fm_str(vault_product_fm, "status") is not None

    vault_decision_fm = _safe_frontmatter(VAULT_DECISIONS_DIR / f"dec-{product_id}-{week}.md")
    vault_decision_status = _fm_str(vault_decision_fm, "status")

    # ── Derivations ──────────────────────────────────────────────────────────
    if vault_product_has_status:
        promote_status = "promoted"
    elif gov_promoted:
        promote_status = gov_promoted
    else:
        promote_status = "unknown"

    if vault_decision_status == "complete":
        decision_status = "complete"
    elif vault_decision_status == "draft":
        decision_status = "draft"
    elif gov_decision:
        decision_status = gov_decision
    else:
        decision_status = "unknown"

    if vault_decision_status == "complete":
        finalization_status = "finalized"
    elif gov_finalization:
        finalization_status = gov_finalization
    else:
        finalization_status = "unknown"

    if gov_next_action:
        next_allowed_action = gov_next_action
    elif promote_status != "promoted":
        next_allowed_action = "Promote candidate through Phase 2G approval gate"
    elif decision_status in ("unknown", "not_executed"):
        next_allowed_action = "Create decision through Phase 2H approval gate"
    elif decision_status == "draft":
        next_allowed_action = "Finalize decision through Phase 2I approval gate"
    elif finalization_status == "finalized":
        next_allowed_action = "Ready for Phase 3/4 planning; no campaign launch yet"
    else:
        next_allowed_action = "Review governance artifacts"

    return {
        "report_week": week,
        "product_id": product_id,
        "product_name": str(anchor.get("product_name", "")).strip(),
        "product_opportunity_score": anchor.get("product_opportunity_score"),
        "score_decision": str(anchor.get("score_decision", "")).strip(),
        "confidence_score": anchor.get("confidence_score"),
        "report_status": report_status,
        "hermes_summary_status": hermes_summary_status,
        "governance_summary_status": governance_summary_status,
        "promote_status": promote_status,
        "decision_status": decision_status,
        "finalization_status": finalization_status,
        "next_allowed_action": next_allowed_action,
    }


def render_stdout(record: dict[str, Any], *, write: bool, dashboard_path: str | None) -> str:
    lines = [f"{field}: {record[field]}" for field in STDOUT_FIELDS]
    if write:
        lines.append(f"dashboard_path: {dashboard_path}")
    lines.append("phase3a_status: success")
    return "\n".join(lines)


def render_artifact(record: dict[str, Any], generated_at: str) -> str:
    frontmatter = [
        "---",
        "type: phase3a_dashboard_summary",
        f"report_week: {record['report_week']}",
        f"product_id: {record['product_id']}",
        f"product_name: {record['product_name']}",
        f"product_opportunity_score: {record['product_opportunity_score']}",
        f"score_decision: {record['score_decision']}",
        f"confidence_score: {record['confidence_score']}",
        f"report_status: {record['report_status']}",
        f"hermes_summary_status: {record['hermes_summary_status']}",
        f"governance_summary_status: {record['governance_summary_status']}",
        f"promote_status: {record['promote_status']}",
        f"decision_status: {record['decision_status']}",
        f"finalization_status: {record['finalization_status']}",
        f'next_allowed_action: "{record["next_allowed_action"]}"',
        f'generated_at: "{generated_at}"',
        "status: complete",
        "---",
    ]
    body = [
        "",
        f"# Phase 3A Dashboard — {record['product_id']} {record['report_week']}",
        "",
        "## Scoring",
        "",
        f"- product_id: {record['product_id']}",
        f"- product_name: {record['product_name']}",
        f"- product_opportunity_score: {record['product_opportunity_score']}",
        f"- score_decision: {record['score_decision']}",
        f"- confidence_score: {record['confidence_score']}",
        "",
        "## Pipeline status",
        "",
        f"- report_status: {record['report_status']}",
        f"- hermes_summary_status: {record['hermes_summary_status']}",
        f"- governance_summary_status: {record['governance_summary_status']}",
        f"- promote_status: {record['promote_status']}",
        "",
        "## Business memory state",
        "",
        f"- decision_status: {record['decision_status']}",
        f"- finalization_status: {record['finalization_status']}",
        "",
        "## Next allowed action",
        "",
        f"- {record['next_allowed_action']}",
        "",
        "## Status",
        "",
        "phase3a_status: success",
        "",
    ]
    return "\n".join(frontmatter + body)


def assert_clean(text: str) -> None:
    """Defense-in-depth: refuse to emit anything matching a forbidden pattern."""
    for pattern in PRIVATE_VAULT_PATHS:
        if pattern in text:
            raise DashboardError(f"output contains private vault path: {pattern}")
    for pattern in AFFILIATE_URL_PATTERNS:
        if pattern in text:
            raise DashboardError(f"output contains affiliate tracking pattern: {pattern}")
    for pattern in CONTENT_MARKERS:
        if pattern in text:
            raise DashboardError(f"output contains affiliate content marker: {pattern}")
    for regex in SECRET_RES:
        if regex.search(text):
            raise DashboardError("output contains a secret pattern")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 3A CLI Dashboard Summary (read-only).",
    )
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--week", required=True)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Also write tmp/phase3a-dashboard/dashboard-<product_id>-<week>.md",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        _validate_inputs(args.product_id, args.week)
        record = build_dashboard(args.product_id, args.week)

        generated_at = _now_utc()
        artifact_text = render_artifact(record, generated_at)
        dashboard_rel = f"tmp/phase3a-dashboard/dashboard-{args.product_id}-{args.week}.md"
        stdout_text = render_stdout(record, write=args.write, dashboard_path=dashboard_rel)

        # Scrub both surfaces before anything is emitted or persisted.
        assert_clean(stdout_text)
        assert_clean(artifact_text)

        if args.write:
            DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
            (DASHBOARD_DIR / f"dashboard-{args.product_id}-{args.week}.md").write_text(
                artifact_text, encoding="utf-8"
            )
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(stdout_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
