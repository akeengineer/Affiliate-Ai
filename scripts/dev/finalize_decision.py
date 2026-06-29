#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_DECISIONS_DIR = REPO_ROOT / "vault" / "decisions"
AUDIT_DIR = REPO_ROOT / "tmp" / "phase2i-decision-finalization"

VALID_DECISIONS = ("launch", "small_batch_test", "watchlist", "reject")
FINALIZABLE_COMPLIANCE = "approved"

REQUIRED_FIELDS = (
    "decision_id",
    "product_id",
    "final_decision",
    "score_decision",
    "product_opportunity_score",
    "confidence_score",
    "missing_signal_count",
    "compliance_status",
    "status",
    "created_at",
    "updated_at",
)

DECISION_ID_RE = re.compile(r"^dec-[a-z0-9-]+-\d{4}-W\d{2}$")

# Frontmatter fences. The closing fence consumes its own trailing newline only,
# so the markdown body (everything after match.end()) is preserved byte-for-byte.
FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\r?\n", re.DOTALL)

AFFILIATE_URL_RE = re.compile(
    r"[?&]aff=|[?&]affiliate=|[?&]tag=|[?&]partner=|[?&]sp_atk="
    r"|[?&]ref=affiliate|bit\.ly/|amzn\.to/|shopee\.link/|s\.lazada\.com/",
    re.IGNORECASE,
)

SECRETS_RE = re.compile(
    r"sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|Bearer [A-Za-z0-9\-_]{20,}",
)


class FinalizeError(Exception):
    """Raised for any validation failure; message is printed to stderr."""


def _now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _check_finalization_reason(reason: str) -> None:
    if not reason.strip():
        raise FinalizeError("finalization_reason is required and must not be empty")
    if AFFILIATE_URL_RE.search(reason):
        raise FinalizeError("finalization_reason contains an affiliate tracking pattern")
    if SECRETS_RE.search(reason):
        raise FinalizeError("finalization_reason contains a secret pattern")


def _split_note(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body) where body is preserved byte-for-byte."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise FinalizeError("frontmatter fences missing or malformed")
    fm = yaml.safe_load(match.group(1)) or {}
    if not isinstance(fm, dict):
        raise FinalizeError("frontmatter must be a mapping")
    body = text[match.end():]
    return fm, body


def _load_and_validate(decision_id: str) -> tuple[Path, dict[str, Any], str]:
    note_path = VAULT_DECISIONS_DIR / f"{decision_id}.md"
    if not note_path.is_file():
        raise FinalizeError(
            f"decision note not found: vault/decisions/{decision_id}.md"
        )

    fm, body = _split_note(note_path.read_text(encoding="utf-8"))

    if fm.get("type") != "decision":
        raise FinalizeError(f"type must be decision, got {fm.get('type')!r}")

    if fm.get("status") != "draft":
        raise FinalizeError(
            f"status must be draft to finalize, got {fm.get('status')!r}"
            " — already finalized or not a draft"
        )

    missing = [f for f in REQUIRED_FIELDS if f not in fm or fm[f] in ("", None)]
    if missing:
        raise FinalizeError(f"missing required field(s): {', '.join(missing)}")

    if str(fm["decision_id"]) != decision_id:
        raise FinalizeError(
            f"frontmatter decision_id {fm['decision_id']!r} does not match"
            f" --decision-id {decision_id!r}"
        )

    final_decision = str(fm["final_decision"])
    if final_decision not in VALID_DECISIONS:
        raise FinalizeError(
            f"final_decision must be one of {VALID_DECISIONS}, got {final_decision!r}"
        )

    try:
        pos = float(fm["product_opportunity_score"])
    except (TypeError, ValueError) as exc:
        raise FinalizeError("product_opportunity_score must be numeric") from exc
    if not 0 <= pos <= 100:
        raise FinalizeError("product_opportunity_score out of range 0-100")

    if str(fm["compliance_status"]) != FINALIZABLE_COMPLIANCE:
        raise FinalizeError(
            f"compliance_status must be {FINALIZABLE_COMPLIANCE!r} to finalize,"
            f" got {fm['compliance_status']!r}"
        )

    return note_path, fm, body


def _write_finalized(
    note_path: Path,
    fm: dict[str, Any],
    body: str,
    finalization_reason: str,
    timestamp: str,
) -> None:
    """Update frontmatter in place, preserving body byte-for-byte, atomically."""
    fm["status"] = "complete"
    fm["finalized_at"] = timestamp
    fm["finalization_reason"] = finalization_reason
    fm["updated_at"] = timestamp

    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    new_text = f"---\n{fm_text}\n---\n{body}"

    fd, tmp_name = tempfile.mkstemp(dir=str(note_path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(new_text)
        os.replace(tmp_name, note_path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def _write_audit(
    *,
    decision_id: str,
    product_id: str,
    final_decision: str,
    mode: str,
    finalized_at: str,
    note_path: Path,
    timestamp: str,
) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = AUDIT_DIR / f"audit-{decision_id}.md"

    fm: dict[str, Any] = {
        "type": "phase2i_audit",
        "decision_id": decision_id,
        "product_id": product_id,
        "final_decision": final_decision,
        "compliance_status": "approved",
        "mode": mode,
        "finalized_at": finalized_at,
        "artifact_path": str(note_path.relative_to(REPO_ROOT)),
        "created_at": timestamp,
        "status": "complete",
    }

    status_label = "success" if mode == "approved" else "dry_run_complete"

    lines = [
        "---",
        yaml.safe_dump(fm, sort_keys=False).strip(),
        "---",
        "",
        f"# Phase 2I Decision Finalization Audit — {decision_id}",
        "",
        f"## Mode: {mode}",
        "",
        f"- decision_id: {decision_id}",
        f"- product_id: {product_id}",
        f"- final_decision: {final_decision}",
        f"- compliance_status: approved",
        f"- artifact_path: {note_path.relative_to(REPO_ROOT)}",
        "",
        "## Status",
        "",
        f"phase2i_status: {status_label}",
        "",
    ]

    audit_path.write_text("\n".join(lines), encoding="utf-8")
    return audit_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize an approved draft decision note in vault/decisions/."
            " Default mode is dry-run."
        )
    )
    parser.add_argument("--decision-id", required=True, help="decision_id, e.g. dec-foo-2026-W26")
    parser.add_argument(
        "--finalization-reason",
        required=True,
        help="Reason recorded on the finalized note (required, non-empty)",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Update the vault decision in place. Default is dry-run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    decision_id = args.decision_id
    if not DECISION_ID_RE.fullmatch(decision_id):
        print(
            f"decision-id must match ^dec-[a-z0-9-]+-\\d{{4}}-W\\d{{2}}$,"
            f" got {decision_id!r}",
            file=sys.stderr,
        )
        return 1

    finalization_reason = args.finalization_reason

    try:
        _check_finalization_reason(finalization_reason)
        note_path, fm, body = _load_and_validate(decision_id)
    except FinalizeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    product_id = str(fm["product_id"])
    final_decision = str(fm["final_decision"])
    timestamp = _now_utc()

    if args.approve:
        try:
            _write_finalized(note_path, dict(fm), body, finalization_reason, timestamp)
        except OSError as exc:
            print(f"failed to write finalized note: {exc}", file=sys.stderr)
            return 1
        finalized_at = timestamp
        mode = "approved"
    else:
        finalized_at = "(dry-run)"
        mode = "dry_run"

    audit_path = _write_audit(
        decision_id=decision_id,
        product_id=product_id,
        final_decision=final_decision,
        mode=mode,
        finalized_at=finalized_at,
        note_path=note_path,
        timestamp=timestamp,
    )

    print(f"decision_id: {decision_id}")
    print(f"final_decision: {final_decision}")
    print("compliance_status: approved")
    if args.approve:
        print(f"decision_artifact: {note_path.relative_to(REPO_ROOT)}")
    print(f"audit_path: {audit_path.relative_to(REPO_ROOT)}")
    if args.approve:
        print("phase2i_status: success")
    else:
        print("phase2i_status: dry_run_complete")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
