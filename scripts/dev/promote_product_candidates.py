#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEST_DIR = REPO_ROOT / "vault" / "products"
AUDIT_DIR = REPO_ROOT / "tmp" / "phase2g-approval-promote"
SAFE_SOURCE_ROOT = REPO_ROOT / "tmp"

REQUIRED_FIELDS = (
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

SCORE_FIELDS = (
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

PRODUCT_ID_RE = re.compile(r"^[a-z0-9-]+$")

AFFILIATE_URL_RE = re.compile(
    r"[?&]aff=|[?&]affiliate=|[?&]tag=|[?&]partner=|[?&]sp_atk="
    r"|[?&]ref=affiliate|bit\.ly/|amzn\.to/|shopee\.link/|s\.lazada\.com/",
    re.IGNORECASE,
)

SECRETS_RE = re.compile(
    r"sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|Bearer [A-Za-z0-9\-_]{20,}",
)


@dataclass(frozen=True)
class PromotionCandidate:
    source_path: Path
    product_id: str
    frontmatter: dict[str, Any]
    body: str
    score_data: dict[str, Any]
    dest_path: Path


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_frontmatter(note_path: Path) -> tuple[dict[str, Any], str]:
    text = note_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
    if not match:
        raise ValueError(f"{note_path.name}: frontmatter fences missing or malformed")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"{note_path.name}: frontmatter must be a mapping")
    return frontmatter, match.group(2)


def _check_affiliate_and_secrets(frontmatter: dict[str, Any], note_name: str) -> None:
    for key, value in frontmatter.items():
        text = str(value) if value is not None else ""
        if SECRETS_RE.search(text):
            raise ValueError(f"{note_name}: field '{key}' contains a secret pattern")
        if key == "product_url" and AFFILIATE_URL_RE.search(text):
            raise ValueError(
                f"{note_name}: product_url contains an affiliate tracking pattern"
            )


def _validate_candidate(
    source_path: Path,
    scores_dir: Path,
    dest_dir: Path,
) -> PromotionCandidate:
    frontmatter, body = _read_frontmatter(source_path)
    name = source_path.name

    if frontmatter.get("type") != "product_candidate":
        raise ValueError(
            f"{name}: type must be product_candidate, got {frontmatter.get('type')!r}"
        )

    missing = [
        f for f in REQUIRED_FIELDS
        if f not in frontmatter or frontmatter[f] in ("", None)
    ]
    if missing:
        raise ValueError(f"{name}: missing required fields: {', '.join(missing)}")

    product_id = str(frontmatter["product_id"])
    if not PRODUCT_ID_RE.fullmatch(product_id):
        raise ValueError(f"{name}: product_id must match ^[a-z0-9-]+$")

    for field in SCORE_FIELDS:
        raw = frontmatter[field]
        try:
            score = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name}: {field} must be numeric") from exc
        if not 0 <= score <= 100:
            raise ValueError(f"{name}: {field} out of range 0-100, got {raw}")

    _check_affiliate_and_secrets(frontmatter, name)

    score_path = scores_dir / f"{product_id}.json"
    if not score_path.is_file():
        raise ValueError(
            f"{name}: score JSON not found at {score_path.relative_to(REPO_ROOT)}"
            " — run Phase 2E first"
        )

    score_data: dict[str, Any] = json.loads(score_path.read_text(encoding="utf-8"))

    if score_data.get("score_decision") == "reject":
        pos = score_data.get("product_opportunity_score", "?")
        raise ValueError(
            f"{name}: score_decision is 'reject' (score={pos})"
            " — resolve product issues before promoting"
        )

    dest_path = dest_dir / source_path.name
    if dest_path.exists():
        raise ValueError(
            f"{name}: destination already exists: {dest_path.relative_to(REPO_ROOT)}"
        )

    return PromotionCandidate(
        source_path=source_path,
        product_id=product_id,
        frontmatter=frontmatter,
        body=body,
        score_data=score_data,
        dest_path=dest_path,
    )


def _build_enriched_frontmatter(
    original: dict[str, Any],
    score_data: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    enriched: dict[str, Any] = {}

    for field in ("type", "product_id", "product_name"):
        enriched[field] = original[field]

    # Optional identity + required marketplace/currency in template order
    for field in ("brand", "marketplace", "niche", "product_url", "currency"):
        if field in original:
            enriched[field] = original[field]

    for field in SCORE_FIELDS:
        enriched[field] = original[field]

    for field in NOTE_REF_FIELDS:
        if field in original:
            enriched[field] = original[field]

    enriched["product_opportunity_score"] = score_data["product_opportunity_score"]
    enriched["score_decision"] = score_data["score_decision"]
    enriched["confidence_score"] = score_data["confidence_score"]
    enriched["missing_signal_count"] = score_data["missing_signal_count"]
    enriched["last_scored_at"] = timestamp

    enriched["status"] = "scored"
    enriched["created_at"] = original["created_at"]
    enriched["updated_at"] = timestamp

    return enriched


def _build_note_text(frontmatter: dict[str, Any], body: str) -> str:
    return "\n".join([
        "---",
        yaml.safe_dump(frontmatter, sort_keys=False).strip(),
        "---",
        "",
        body.strip(),
        "",
    ])


def _write_audit(
    *,
    candidates: list[PromotionCandidate],
    rejected: list[tuple[Path, str]],
    mode: str,
    report_week: str,
    source_dir: Path,
    promoted: bool,
    timestamp: str,
) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = AUDIT_DIR / f"audit-{report_week}.md"

    promoted_count = len(candidates) if promoted else 0

    fm: dict[str, Any] = {
        "type": "phase2g_audit",
        "report_week": report_week,
        "mode": mode,
        "source_dir": str(source_dir.relative_to(REPO_ROOT)),
        "validated_count": len(candidates),
        "promoted_count": promoted_count,
        "rejected_count": len(rejected),
        "created_at": timestamp,
        "status": "complete",
    }

    lines = [
        "---",
        yaml.safe_dump(fm, sort_keys=False).strip(),
        "---",
        "",
        f"# Phase 2G Approval Promote Audit — {report_week}",
        "",
        f"## Mode: {mode}",
        "",
    ]

    if candidates:
        lines += ["## Validated notes", ""]
        for c in candidates:
            dec = c.score_data.get("score_decision", "unknown")
            conf = c.score_data.get("confidence_score", "?")
            lines.append(f"- {c.source_path.name} → score_decision: {dec}, confidence: {conf}")
        lines.append("")

    if candidates:
        header = "## Promoted notes" if promoted else "## Would promote (pending approval)"
        lines += [header, ""]
        for c in candidates:
            lines.append(f"- {c.dest_path.relative_to(REPO_ROOT)}")
        lines.append("")

    if rejected:
        lines += ["## Rejected notes", ""]
        for path, reason in rejected:
            lines.append(f"- {path.name}: {reason}")
        lines.append("")

    status_label = "success" if promoted else "dry_run_complete"
    lines += ["## Status", "", f"phase2g_status: {status_label}", ""]

    audit_path.write_text("\n".join(lines), encoding="utf-8")
    return audit_path


def _require_safe_source(source_dir: Path) -> Path:
    resolved = source_dir.expanduser().resolve(strict=False)
    if not _is_relative_to(resolved, SAFE_SOURCE_ROOT.resolve()):
        raise ValueError(
            f"source_dir must be under {SAFE_SOURCE_ROOT.relative_to(REPO_ROOT)},"
            f" got: {source_dir}"
        )
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and promote product_candidate notes from Phase 2E output"
            " into vault/products/. Default mode is dry-run."
        )
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        type=Path,
        help="Root of Phase 2E output (contains products/ and scores/ subdirs)",
    )
    parser.add_argument("--report-week", required=True, help="ISO week label, e.g. 2026-W26")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Write promoted notes to vault/products/. Default is dry-run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        source_dir = _require_safe_source(args.source_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    products_dir = source_dir / "products"
    scores_dir = source_dir / "scores"

    if not products_dir.is_dir():
        print(
            f"products/ dir not found under {source_dir.relative_to(REPO_ROOT)}"
            " — run Phase 2E first",
            file=sys.stderr,
        )
        return 1

    note_paths = sorted(products_dir.glob("*.md"))
    if not note_paths:
        print(
            f"No product notes found in {products_dir.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 1

    timestamp = _now_utc()
    candidates: list[PromotionCandidate] = []
    rejected: list[tuple[Path, str]] = []

    for note_path in note_paths:
        try:
            candidates.append(_validate_candidate(note_path, scores_dir, DEST_DIR))
        except ValueError as exc:
            rejected.append((note_path, str(exc)))

    mode = "approved" if args.approve else "dry_run"

    if rejected:
        print(f"Rejected {len(rejected)} note(s):", file=sys.stderr)
        for path, reason in rejected:
            print(f"  {reason}", file=sys.stderr)
        _write_audit(
            candidates=candidates,
            rejected=rejected,
            mode=mode,
            report_week=args.report_week,
            source_dir=source_dir,
            promoted=False,
            timestamp=timestamp,
        )
        return 1

    if not args.approve:
        audit_path = _write_audit(
            candidates=candidates,
            rejected=rejected,
            mode="dry_run",
            report_week=args.report_week,
            source_dir=source_dir,
            promoted=False,
            timestamp=timestamp,
        )
        print(f"validated_count: {len(candidates)}")
        print("promoted_count: 0")
        print(f"audit_path: {audit_path}")
        print("phase2g_status: dry_run_complete")
        return 0

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    for candidate in candidates:
        enriched_fm = _build_enriched_frontmatter(
            candidate.frontmatter, candidate.score_data, timestamp
        )
        candidate.dest_path.write_text(
            _build_note_text(enriched_fm, candidate.body), encoding="utf-8"
        )

    audit_path = _write_audit(
        candidates=candidates,
        rejected=rejected,
        mode="approved",
        report_week=args.report_week,
        source_dir=source_dir,
        promoted=True,
        timestamp=timestamp,
    )

    print(f"validated_count: {len(candidates)}")
    print(f"promoted_count: {len(candidates)}")
    print(f"audit_path: {audit_path}")
    for c in candidates:
        print(f"promoted: {c.dest_path.relative_to(REPO_ROOT)}")
    print("phase2g_status: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
