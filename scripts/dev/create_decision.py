#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_PRODUCTS_DIR = REPO_ROOT / "vault" / "products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault" / "decisions"
REVIEW_DIR = REPO_ROOT / "tmp" / "phase2h-decision-review"

VALID_DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
VALID_COMPLIANCE = ("pending", "approved", "needs_review", "blocked")
DECISION_LEVEL = {"launch": 4, "small_batch_test": 3, "watchlist": 2, "reject": 1}

ENRICHED_FIELDS = (
    "product_opportunity_score",
    "score_decision",
    "confidence_score",
    "missing_signal_count",
    "last_scored_at",
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
class ProductNote:
    product_id: str
    product_name: str
    note_path: Path
    frontmatter: dict[str, Any]
    score_decision: str
    product_opportunity_score: float
    confidence_score: float
    missing_signal_count: int


def _now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_frontmatter(note_path: Path) -> dict[str, Any]:
    text = note_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        raise ValueError(f"{note_path.name}: frontmatter fences missing or malformed")
    fm = yaml.safe_load(match.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError(f"{note_path.name}: frontmatter must be a mapping")
    return fm


def _load_product_note(product_id: str) -> ProductNote:
    note_path = VAULT_PRODUCTS_DIR / f"{product_id}.md"
    if not note_path.is_file():
        raise ValueError(
            f"Product note not found: vault/products/{product_id}.md"
            " — run Phase 2G --approve first"
        )

    fm = _read_frontmatter(note_path)

    if fm.get("type") != "product_candidate":
        raise ValueError(
            f"{note_path.name}: type must be product_candidate, got {fm.get('type')!r}"
        )

    if fm.get("status") != "scored":
        raise ValueError(
            f"{note_path.name}: status must be scored, got {fm.get('status')!r}"
            " — promote via Phase 2G first"
        )

    missing = [f for f in ENRICHED_FIELDS if f not in fm or fm[f] in ("", None)]
    if missing:
        raise ValueError(
            f"{note_path.name}: missing enriched fields: {', '.join(missing)}"
            " — was this note promoted with Phase 2G --approve?"
        )

    try:
        pos = float(fm["product_opportunity_score"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{note_path.name}: product_opportunity_score must be numeric"
        ) from exc
    if not 0 <= pos <= 100:
        raise ValueError(
            f"{note_path.name}: product_opportunity_score out of range 0-100"
        )

    score_decision = str(fm["score_decision"])
    if score_decision not in VALID_DECISIONS:
        raise ValueError(
            f"{note_path.name}: score_decision must be one of {VALID_DECISIONS},"
            f" got {score_decision!r}"
        )

    return ProductNote(
        product_id=product_id,
        product_name=str(fm.get("product_name", product_id)),
        note_path=note_path,
        frontmatter=fm,
        score_decision=score_decision,
        product_opportunity_score=pos,
        confidence_score=float(fm.get("confidence_score", 0)),
        missing_signal_count=int(fm.get("missing_signal_count", 0)),
    )


def _check_override_reason(override_reason: str) -> None:
    if AFFILIATE_URL_RE.search(override_reason):
        raise ValueError("override_reason contains an affiliate tracking pattern")
    if SECRETS_RE.search(override_reason):
        raise ValueError("override_reason contains a secret pattern")


def _build_decision_summary(
    final_decision: str,
    score_decision: str,
    override_reason: str,
) -> str:
    if final_decision == score_decision:
        return f"score_decision={score_decision} confirmed as final_decision={final_decision}"
    level_f = DECISION_LEVEL[final_decision]
    level_s = DECISION_LEVEL[score_decision]
    if level_f < level_s:
        return (
            f"final_decision={final_decision} is more conservative"
            f" than score_decision={score_decision}"
        )
    return (
        f"final_decision={final_decision} overrides score_decision={score_decision}"
        f" with reason: {override_reason[:80]}"
    )


def _build_artifact(
    *,
    product: ProductNote,
    decision_id: str,
    final_decision: str,
    compliance_status: str,
    vote_count: int,
    override_reason: str,
    timestamp: str,
) -> str:
    fm: dict[str, Any] = {
        "type": "decision",
        "decision_id": decision_id,
        "product_id": product.product_id,
        "final_decision": final_decision,
        "score_decision": product.score_decision,
        "product_opportunity_score": product.product_opportunity_score,
        "confidence_score": product.confidence_score,
        "missing_signal_count": product.missing_signal_count,
        "vote_count": vote_count,
        "compliance_status": compliance_status,
        "override_reason": override_reason if override_reason else None,
        "decision_summary": _build_decision_summary(
            final_decision, product.score_decision, override_reason
        ),
        "required_actions": [],
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()

    src_fm = product.frontmatter
    score_lines = "\n".join([
        f"- demand_score: {src_fm.get('demand_score', '?')}",
        f"- trend_velocity_score: {src_fm.get('trend_velocity_score', '?')}",
        f"- marketplace_rank_score: {src_fm.get('marketplace_rank_score', '?')}",
        f"- commission_score: {src_fm.get('commission_score', '?')}",
        f"- content_fit_score: {src_fm.get('content_fit_score', '?')}",
        f"- competition_gap_score: {src_fm.get('competition_gap_score', '?')}",
        f"- risk_score: {src_fm.get('risk_score', '?')}",
    ])

    override_section = override_reason if override_reason else "(none)"

    return "\n".join([
        "---",
        fm_text,
        "---",
        "",
        f"# Decision — {product.product_id}",
        "",
        "## Summary",
        "",
        f"Product: {product.product_id}",
        f"Final decision: {final_decision}",
        f"Score decision: {product.score_decision}",
        f"Product opportunity score: {product.product_opportunity_score}",
        f"Confidence: {product.confidence_score} | Missing signals: {product.missing_signal_count}",
        "",
        "## Score Context",
        "",
        score_lines,
        "",
        "## Override Reason",
        "",
        override_section,
        "",
        "## Required Actions",
        "",
        "(none)",
        "",
        "## Notes",
        "",
        "(empty)",
        "",
    ])


def _write_audit(
    *,
    product_id: str,
    decision_id: str,
    final_decision: str,
    score_decision: str,
    mode: str,
    report_week: str,
    artifact_path: Path,
    timestamp: str,
) -> Path:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = REVIEW_DIR / f"audit-{report_week}.md"

    fm: dict[str, Any] = {
        "type": "phase2h_audit",
        "report_week": report_week,
        "mode": mode,
        "product_id": product_id,
        "decision_id": decision_id,
        "final_decision": final_decision,
        "score_decision": score_decision,
        "artifact_path": str(artifact_path.relative_to(REPO_ROOT)),
        "created_at": timestamp,
        "status": "complete",
    }

    status_label = "success" if mode == "approved" else "dry_run_complete"

    lines = [
        "---",
        yaml.safe_dump(fm, sort_keys=False).strip(),
        "---",
        "",
        f"# Phase 2H Decision Review Audit — {report_week}",
        "",
        f"## Mode: {mode}",
        "",
        f"- product_id: {product_id}",
        f"- decision_id: {decision_id}",
        f"- final_decision: {final_decision}",
        f"- score_decision: {score_decision}",
        f"- artifact_path: {artifact_path.relative_to(REPO_ROOT)}",
        "",
        "## Status",
        "",
        f"phase2h_status: {status_label}",
        "",
    ]

    audit_path.write_text("\n".join(lines), encoding="utf-8")
    return audit_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a decision artifact for a scored product_candidate in vault/products/."
            " Default mode is dry-run."
        )
    )
    parser.add_argument("--product-id", required=True, help="product_id of the promoted note")
    parser.add_argument(
        "--decision",
        required=True,
        choices=list(VALID_DECISIONS),
        help="Final decision: launch | small_batch_test | watchlist | reject",
    )
    parser.add_argument("--report-week", required=True, help="ISO week label, e.g. 2026-W26")
    parser.add_argument("--override-reason", default="", help="Required when upgrading score_decision")
    parser.add_argument(
        "--compliance-status",
        default="pending",
        choices=list(VALID_COMPLIANCE),
        help="Compliance status (default: pending)",
    )
    parser.add_argument("--vote-count", type=int, default=0, help="Agent vote count (default: 0)")
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Write decision artifact to vault/decisions/. Default is dry-run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    product_id = args.product_id
    if not PRODUCT_ID_RE.fullmatch(product_id):
        print(
            f"product_id must match ^[a-z0-9-]+$, got {product_id!r}",
            file=sys.stderr,
        )
        return 1

    try:
        product = _load_product_note(product_id)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    final_decision = args.decision
    score_decision = product.score_decision
    override_reason = args.override_reason.strip()

    # Compatibility check
    if final_decision != "reject":
        level_f = DECISION_LEVEL[final_decision]
        level_s = DECISION_LEVEL[score_decision]
        if level_f > level_s:
            if not override_reason:
                print(
                    f"final_decision={final_decision!r} upgrades"
                    f" score_decision={score_decision!r}:"
                    " --override-reason is required",
                    file=sys.stderr,
                )
                return 1

    if override_reason:
        try:
            _check_override_reason(override_reason)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    decision_id = f"dec-{product_id}-{args.report_week}"
    timestamp = _now_utc()

    if args.approve:
        dest_path = VAULT_DECISIONS_DIR / f"{decision_id}.md"
    else:
        dest_path = REVIEW_DIR / f"{decision_id}.md"

    if dest_path.exists():
        print(
            f"destination already exists: {dest_path.relative_to(REPO_ROOT)}"
            " — remove it first or use a different --report-week",
            file=sys.stderr,
        )
        return 1

    artifact_text = _build_artifact(
        product=product,
        decision_id=decision_id,
        final_decision=final_decision,
        compliance_status=args.compliance_status,
        vote_count=args.vote_count,
        override_reason=override_reason,
        timestamp=timestamp,
    )

    if args.approve:
        VAULT_DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    else:
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    dest_path.write_text(artifact_text, encoding="utf-8")

    audit_path = _write_audit(
        product_id=product_id,
        decision_id=decision_id,
        final_decision=final_decision,
        score_decision=score_decision,
        mode="approved" if args.approve else "dry_run",
        report_week=args.report_week,
        artifact_path=dest_path,
        timestamp=timestamp,
    )

    print(f"product_id: {product_id}")
    print(f"final_decision: {final_decision}")
    print(f"score_decision: {score_decision}")
    print(f"product_opportunity_score: {product.product_opportunity_score}")
    print(f"decision_artifact: {dest_path.relative_to(REPO_ROOT)}")
    print(f"audit_path: {audit_path.relative_to(REPO_ROOT)}")
    if args.approve:
        print("phase2h_status: success")
    else:
        print("phase2h_status: dry_run_complete")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
