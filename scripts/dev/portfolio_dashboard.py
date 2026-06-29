#!/usr/bin/env python3
"""Phase 3B Portfolio CLI Dashboard.

Read-only, multi-product portfolio view for a report week. Reads every score
JSON under tmp/phase2e-import-score-report/scores/, groups and ranks them, and
reports portfolio-level counts plus optional vault/Phase-3A enrichment.

This tool never writes to the vault, never calls external APIs, and never
generates affiliate content. By default it prints to stdout; with --write it
also emits a tmp artifact.

Scrubbing, guardrails, frontmatter parsing, and timestamps are reused from the
Phase 3A dashboard module to keep a single source of truth.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from dashboard_summary import (  # noqa: F401  (constants reused indirectly via assert_clean)
    AFFILIATE_URL_PATTERNS,
    CONTENT_MARKERS,
    PRIVATE_VAULT_PATHS,
    SECRET_RES,
    WEEK_RE,
    DashboardError,
    _check_guardrails,
    _fm_str,
    _now_utc,
    _safe_frontmatter,
    assert_clean,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

SCORES_DIR = REPO_ROOT / "tmp" / "phase2e-import-score-report" / "scores"
PHASE3A_DIR = REPO_ROOT / "tmp" / "phase3a-dashboard"
VAULT_PRODUCTS_DIR = REPO_ROOT / "vault" / "products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault" / "decisions"
PORTFOLIO_DIR = REPO_ROOT / "tmp" / "phase3b-portfolio-dashboard"

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")
VALID_DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
DECISION_HEADINGS = {
    "launch": "Launch",
    "small_batch_test": "Small Batch Test",
    "watchlist": "Watchlist",
    "reject": "Reject",
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load_scores() -> tuple[list[dict[str, Any]], int]:
    """Return (valid product records, skipped_count). Reads all scores/*.json.

    Only whitelisted fields are kept; input_path/note_refs are never carried.
    """
    products: list[dict[str, Any]] = []
    skipped = 0

    if not SCORES_DIR.is_dir():
        return products, skipped

    for path in sorted(SCORES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"warning: skipping unreadable score file {path.name}: {exc}", file=sys.stderr)
            skipped += 1
            continue

        if not isinstance(data, dict):
            print(f"warning: skipping score file {path.name}: not a JSON object", file=sys.stderr)
            skipped += 1
            continue

        product_id = str(data.get("product_id", "")).strip()
        score_decision = str(data.get("score_decision", "")).strip()
        score = data.get("product_opportunity_score")

        if not PRODUCT_ID_RE.match(product_id):
            print(f"warning: skipping score file {path.name}: invalid product_id", file=sys.stderr)
            skipped += 1
            continue
        if score_decision not in VALID_DECISIONS:
            print(f"warning: skipping {product_id}: invalid score_decision {score_decision!r}", file=sys.stderr)
            skipped += 1
            continue
        if not _is_number(score):
            print(f"warning: skipping {product_id}: product_opportunity_score is not numeric", file=sys.stderr)
            skipped += 1
            continue

        products.append(
            {
                "product_id": product_id,
                "product_name": str(data.get("product_name", "")).strip(),
                "product_opportunity_score": score,
                "score_decision": score_decision,
                "confidence_score": data.get("confidence_score"),
            }
        )

    return products, skipped


def _rank(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda p: (-p["product_opportunity_score"], p["product_id"]),
    )


def build_portfolio(week: str, top_n: int) -> dict[str, Any]:
    products, skipped = load_scores()
    ranked = _rank(products)

    counts = {f"{decision}_count": 0 for decision in VALID_DECISIONS}
    for product in ranked:
        counts[f"{product['score_decision']}_count"] += 1

    phase3a_artifact_count = 0
    promoted_count = 0
    decision_draft_count = 0
    decision_complete_count = 0

    for product in ranked:
        product_id = product["product_id"]

        if (PHASE3A_DIR / f"dashboard-{product_id}-{week}.md").is_file():
            phase3a_artifact_count += 1

        vault_product_fm = _safe_frontmatter(VAULT_PRODUCTS_DIR / f"{product_id}.md")
        if vault_product_fm is not None and _fm_str(vault_product_fm, "status") is not None:
            promoted_count += 1

        vault_decision_fm = _safe_frontmatter(VAULT_DECISIONS_DIR / f"dec-{product_id}-{week}.md")
        decision_status = _fm_str(vault_decision_fm, "status")
        if decision_status == "draft":
            decision_draft_count += 1
        elif decision_status == "complete":
            decision_complete_count += 1

    return {
        "report_week": week,
        "total_products": len(ranked),
        "launch_count": counts["launch_count"],
        "small_batch_test_count": counts["small_batch_test_count"],
        "watchlist_count": counts["watchlist_count"],
        "reject_count": counts["reject_count"],
        "top_n": top_n,
        "skipped_count": skipped,
        "phase3a_artifact_count": phase3a_artifact_count,
        "promoted_count": promoted_count,
        "decision_draft_count": decision_draft_count,
        "decision_complete_count": decision_complete_count,
        "_ranked": ranked,
    }


COUNT_FIELDS = (
    "report_week",
    "total_products",
    "launch_count",
    "small_batch_test_count",
    "watchlist_count",
    "reject_count",
    "top_n",
    "skipped_count",
    "phase3a_artifact_count",
    "promoted_count",
    "decision_draft_count",
    "decision_complete_count",
)

TOP_HEADER = "rank | product_id | product_name | score | score_decision | confidence"


def _top_rows(record: dict[str, Any]) -> list[str]:
    top = record["_ranked"][: record["top_n"]]
    if not top:
        return ["(none)"]
    rows = [TOP_HEADER]
    for rank, product in enumerate(top, start=1):
        rows.append(
            f"{rank} | {product['product_id']} | {product['product_name']} | "
            f"{product['product_opportunity_score']} | {product['score_decision']} | "
            f"{product['confidence_score']}"
        )
    return rows


def render_stdout(record: dict[str, Any], *, write: bool, portfolio_path: str | None) -> str:
    lines = [f"{field}: {record[field]}" for field in COUNT_FIELDS]
    lines.append("")
    lines.append(f"Top {record['top_n']} products")
    lines.extend(_top_rows(record))
    lines.append("")
    if write:
        lines.append(f"portfolio_path: {portfolio_path}")
    lines.append("phase3b_status: success")
    return "\n".join(lines)


def render_artifact(record: dict[str, Any], generated_at: str) -> str:
    frontmatter = [
        "---",
        "type: phase3b_portfolio_dashboard",
        f"report_week: {record['report_week']}",
        f"total_products: {record['total_products']}",
        f"launch_count: {record['launch_count']}",
        f"small_batch_test_count: {record['small_batch_test_count']}",
        f"watchlist_count: {record['watchlist_count']}",
        f"reject_count: {record['reject_count']}",
        f"top_n: {record['top_n']}",
        f"skipped_count: {record['skipped_count']}",
        f"phase3a_artifact_count: {record['phase3a_artifact_count']}",
        f"promoted_count: {record['promoted_count']}",
        f"decision_draft_count: {record['decision_draft_count']}",
        f"decision_complete_count: {record['decision_complete_count']}",
        f'generated_at: "{generated_at}"',
        "status: complete",
        "---",
    ]

    body = [
        "",
        f"# Phase 3B Portfolio Dashboard — {record['report_week']}",
        "",
        "## Portfolio counts",
        "",
        f"- total_products: {record['total_products']}",
        f"- launch_count: {record['launch_count']}",
        f"- small_batch_test_count: {record['small_batch_test_count']}",
        f"- watchlist_count: {record['watchlist_count']}",
        f"- reject_count: {record['reject_count']}",
        f"- skipped_count: {record['skipped_count']}",
        "",
        "## Business memory state",
        "",
        f"- phase3a_artifact_count: {record['phase3a_artifact_count']}",
        f"- promoted_count: {record['promoted_count']}",
        f"- decision_draft_count: {record['decision_draft_count']}",
        f"- decision_complete_count: {record['decision_complete_count']}",
        "",
        f"## Top {record['top_n']} products",
        "",
    ]
    body.extend(_top_rows(record))
    body.append("")
    body.append("## By decision")
    for decision in VALID_DECISIONS:
        body.append("")
        body.append(f"### {DECISION_HEADINGS[decision]}")
        body.append("")
        members = [p for p in record["_ranked"] if p["score_decision"] == decision]
        if not members:
            body.append("- None")
            continue
        for product in members:
            body.append(
                f"- {product['product_id']} | {product['product_name']} | "
                f"{product['product_opportunity_score']} | confidence: {product['confidence_score']}"
            )
    body.extend(["", "## Status", "", "phase3b_status: success", ""])

    return "\n".join(frontmatter + body)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 3B Portfolio CLI Dashboard (read-only).",
    )
    parser.add_argument("--week", required=True)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Also write tmp/phase3b-portfolio-dashboard/portfolio-<week>.md",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        _check_guardrails()
        if not WEEK_RE.match(args.week):
            raise DashboardError(f"week must match ^[0-9]{{4}}-W[0-9]{{2}}$, got: {args.week!r}")
        if args.top < 1:
            raise DashboardError(f"--top must be an integer >= 1, got: {args.top}")

        record = build_portfolio(args.week, args.top)

        generated_at = _now_utc()
        artifact_text = render_artifact(record, generated_at)
        portfolio_rel = f"tmp/phase3b-portfolio-dashboard/portfolio-{args.week}.md"
        stdout_text = render_stdout(record, write=args.write, portfolio_path=portfolio_rel)

        assert_clean(stdout_text)
        assert_clean(artifact_text)

        if args.write:
            PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
            (PORTFOLIO_DIR / f"portfolio-{args.week}.md").write_text(artifact_text, encoding="utf-8")
    except DashboardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(stdout_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
