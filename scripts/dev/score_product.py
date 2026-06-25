#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


REQUIRED_PRODUCT_FIELDS = (
    "type",
    "product_id",
    "product_name",
    "marketplace",
    "currency",
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_score",
    "created_at",
    "updated_at",
    "status",
)

COMPONENT_SCORE_FIELDS = (
    "demand_score",
    "trend_velocity_score",
    "marketplace_rank_score",
    "commission_score",
    "content_fit_score",
    "competition_gap_score",
    "risk_score",
)

NOTE_REF_FIELDS = (
    "trend_signal_note",
    "marketplace_signal_note",
    "commission_signal_note",
    "compliance_result_note",
)

CONFIDENCE_PENALTIES = {
    "trend_signal_note": 20,
    "marketplace_signal_note": 20,
    "commission_signal_note": 20,
    "compliance_result_note": 10,
}


def read_frontmatter(note_path: Path) -> tuple[dict[str, Any], str]:
    text = note_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"{note_path}: markdown frontmatter fences are missing or malformed")

    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"{note_path}: frontmatter must decode to a mapping")
    return frontmatter, match.group(2)


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _require_score(frontmatter: dict[str, Any], field_name: str) -> float:
    if field_name not in frontmatter or frontmatter[field_name] in ("", None):
        raise ValueError(f"Missing required field: {field_name}")

    value = frontmatter[field_name]
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric 0-100")

    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric 0-100") from exc

    if not 0 <= score <= 100:
        raise ValueError(f"{field_name} must be within 0-100")
    return score


def _decision_for_score(score: float) -> str:
    if score >= 85:
        return "launch"
    if score >= 75:
        return "small_batch_test"
    if score >= 65:
        return "watchlist"
    return "reject"


def score_product_note(note_path: Path) -> dict[str, Any]:
    frontmatter, _body = read_frontmatter(note_path)

    missing_fields = [
        field_name
        for field_name in REQUIRED_PRODUCT_FIELDS
        if field_name not in frontmatter or frontmatter[field_name] in ("", None)
    ]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    if frontmatter["type"] != "product_candidate":
        raise ValueError(f"{note_path}: expected type=product_candidate")

    component_scores = {
        field_name: _require_score(frontmatter, field_name) for field_name in COMPONENT_SCORE_FIELDS
    }
    note_refs = {field_name: _clean_string(frontmatter.get(field_name)) for field_name in NOTE_REF_FIELDS}

    missing_signals = [field_name for field_name, value in note_refs.items() if value is None]
    confidence_score = max(
        0,
        100 - sum(CONFIDENCE_PENALTIES[field_name] for field_name in missing_signals),
    )

    product_opportunity_score = round(
        (0.25 * component_scores["demand_score"])
        + (0.20 * component_scores["trend_velocity_score"])
        + (0.15 * component_scores["marketplace_rank_score"])
        + (0.15 * component_scores["commission_score"])
        + (0.10 * component_scores["content_fit_score"])
        + (0.10 * component_scores["competition_gap_score"])
        + (0.05 * (100 - component_scores["risk_score"])),
        2,
    )

    return {
        "input_path": str(note_path),
        "product_id": str(frontmatter["product_id"]),
        "product_name": str(frontmatter["product_name"]),
        "marketplace": str(frontmatter["marketplace"]),
        "currency": str(frontmatter["currency"]),
        "product_opportunity_score": product_opportunity_score,
        "score_decision": _decision_for_score(product_opportunity_score),
        "confidence_score": confidence_score,
        "missing_signal_count": len(missing_signals),
        "missing_signals": missing_signals,
        "component_scores": component_scores,
        "note_refs": note_refs,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score a product_candidate Markdown note.")
    parser.add_argument("note_path", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = score_product_note(args.note_path)
    except Exception as exc:  # ponytail: CLI error path, keep one clear message for scripts/tests.
        print(str(exc), file=sys.stderr)
        return 1

    indent = 2 if args.pretty else None
    print(json.dumps(payload, indent=indent, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
