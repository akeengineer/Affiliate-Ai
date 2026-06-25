#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from score_product import read_frontmatter, score_product_note


DECISION_ORDER = ("launch", "small_batch_test", "watchlist", "reject")
DECISION_HEADINGS = {
    "launch": "Launch",
    "small_batch_test": "Small Batch Test",
    "watchlist": "Watchlist",
    "reject": "Reject",
}


def collect_notes(input_dir: Path) -> tuple[list[Path], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    product_paths: list[Path] = []
    votes_by_product: dict[str, list[dict[str, Any]]] = defaultdict(list)
    compliance_by_product: dict[str, dict[str, Any]] = {}

    for note_path in sorted(input_dir.rglob("*.md")):
        frontmatter, _body = read_frontmatter(note_path)
        note_type = frontmatter.get("type")
        product_id = str(frontmatter.get("product_id", "")).strip()

        if note_type == "product_candidate":
            product_paths.append(note_path)
        elif note_type == "agent_vote" and product_id:
            votes_by_product[product_id].append(frontmatter)
        elif note_type == "compliance_result" and product_id:
            compliance_by_product[product_id] = frontmatter

    return product_paths, votes_by_product, compliance_by_product


def render_product_section(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- None"]

    lines: list[str] = []
    for row in rows:
        missing_signals = ", ".join(row["missing_signals"]) if row["missing_signals"] else "none"
        lines.append(
            f"- {row['product_name']} ({row['product_id']}) | "
            f"Score: {row['product_opportunity_score']:.2f} | "
            f"Confidence: {row['confidence_score']} | "
            f"Votes: {row['vote_count']} | "
            f"Compliance: {row['compliance_status']}"
        )
        lines.append(f"  Missing signals: {missing_signals}")
    return lines


def build_report(input_dir: Path, report_week: str) -> str:
    product_paths, votes_by_product, compliance_by_product = collect_notes(input_dir)
    scored_rows: list[dict[str, Any]] = []

    for product_path in product_paths:
        score_payload = score_product_note(product_path)
        product_id = score_payload["product_id"]
        votes = votes_by_product.get(product_id, [])
        compliance = compliance_by_product.get(product_id)

        scored_rows.append(
            {
                **score_payload,
                "vote_count": len(votes),
                "compliance_status": compliance.get("compliance_status", "missing")
                if compliance
                else "missing",
            }
        )

    grouped_rows = {decision: [] for decision in DECISION_ORDER}
    for row in scored_rows:
        grouped_rows[row["score_decision"]].append(row)

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    frontmatter = {
        "type": "weekly_report",
        "report_id": f"weekly-report-{report_week}",
        "report_week": report_week,
        "generated_at": now,
        "candidate_count": len(scored_rows),
        "launch_count": len(grouped_rows["launch"]),
        "small_batch_test_count": len(grouped_rows["small_batch_test"]),
        "watchlist_count": len(grouped_rows["watchlist"]),
        "reject_count": len(grouped_rows["reject"]),
        "source_root": str(input_dir),
        "status": "generated",
        "created_at": now,
        "updated_at": now,
    }

    lines = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", "", "# Weekly Report", ""]
    lines.extend(
        [
            "## Summary",
            "",
            f"- Candidates scored: {frontmatter['candidate_count']}",
            f"- Launch: {frontmatter['launch_count']}",
            f"- Small batch test: {frontmatter['small_batch_test_count']}",
            f"- Watchlist: {frontmatter['watchlist_count']}",
            f"- Reject: {frontmatter['reject_count']}",
            "",
        ]
    )

    for decision in DECISION_ORDER:
        lines.append(f"## {DECISION_HEADINGS[decision]}")
        lines.append("")
        lines.extend(render_product_section(grouped_rows[decision]))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Markdown weekly report from sample notes.")
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--report-week", required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = build_report(args.input_dir, args.report_week)
    except Exception as exc:  # ponytail: keep report CLI failures as one-line stderr for automation.
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
