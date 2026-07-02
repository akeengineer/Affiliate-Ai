#!/usr/bin/env python3
"""Phase 8B local append-only audit store ingest (read-only prototype).

Reads exactly one existing audit artifact (produced by the Phase 7D
single-gate wrapper, or any Phase 7D-compatible JSON object) and appends one
normalized, hash-chained durable audit record to a local, gitignored
append-only JSONL store under tmp/phase8b-audit-store/. This is an
ingest-only prototype: it never executes an approval primitive, never calls
the Phase 7D wrapper, never runs the Phase 7B verifier automatically, never
reads or writes the vault, and never makes a network, backend, API, or
database call. Python standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE_DIR = "tmp/phase8b-audit-store"
GUARDED_STORE_ROOT = (REPO_ROOT / DEFAULT_STORE_DIR).resolve()

REJECTED_INPUT_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PHASE8B_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "local_append_only_prototype"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"
STORE_VERSION = "phase8b-1"
SOURCE_PHASE = "phase7d_single_gate_wrapper"
DEFAULT_RETENTION_CLASS = "standard"

# Best-effort extraction: normalized field -> candidate source keys, in order.
FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "audit_schema_version": ("audit_schema_version",),
    "product_id": ("product_id",),
    "report_week": ("report_week",),
    "selected_gate": ("selected_gate",),
    "wrapper_version": ("wrapper_version",),
    "operator": ("operator",),
    "approval_reason": ("approval_reason",),
    "approval_intent": ("approval_intent", "gate_specific_approval_intent"),
    "execution_mode": ("execution_mode",),
    "emergency_stop_state": ("emergency_stop_state",),
    "mutation_attempted": ("mutation_attempted",),
    "primitive_name": ("primitive_name",),
    "primitive_outcome": ("primitive_outcome", "outcome"),
    "phase6b_packet_ref": ("phase6b_packet_ref", "source_packet_path"),
    "phase6c_verifier_ref": ("phase6c_verifier_ref", "verifier_path"),
    "phase6e_plan_ref": ("phase6e_plan_ref", "execution_plan_path"),
    "phase7b_verifier_ref": ("phase7b_verifier_ref",),
    "intent_audit_ref": ("intent_audit_ref",),
    "result_audit_ref": ("result_audit_ref",),
    "precondition_summary": ("precondition_summary",),
    "result_summary": ("result_summary",),
    "created_at": ("created_at", "timestamp"),
    "completed_at": ("completed_at",),
}

# Every field the normalized record must carry (see docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md).
REQUIRED_RECORD_FIELDS = (
    "audit_record_id",
    "audit_schema_version",
    "source_phase",
    "product_id",
    "report_week",
    "selected_gate",
    "wrapper_version",
    "operator",
    "approval_reason",
    "approval_intent",
    "execution_mode",
    "emergency_stop_state",
    "mutation_attempted",
    "primitive_name",
    "primitive_outcome",
    "phase6b_packet_ref",
    "phase6c_verifier_ref",
    "phase6e_plan_ref",
    "phase7b_verifier_ref",
    "intent_audit_ref",
    "result_audit_ref",
    "source_audit_artifact_ref",
    "precondition_summary",
    "result_summary",
    "manual_review_status",
    "incident_id",
    "created_at",
    "completed_at",
    "artifact_hash",
    "previous_record_hash",
    "record_hash",
    "retention_class",
    "phase8b_ingested_at",
    "phase8b_store_version",
)


class IngestError(Exception):
    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _extract(raw_audit: dict[str, Any], field: str) -> Any:
    for key in FIELD_ALIASES.get(field, (field,)):
        if key in raw_audit:
            return raw_audit[key]
    return None


def _validate_input_path(raw: str) -> Path:
    """Read-only path safety gate for the source audit artifact.

    Rejects missing/non-file/symlink/traversal/outside-repo paths and any
    path resolving under vault/, docs/, scripts/, tests/, or codex/. Hidden
    path segments are rejected unless the path is under tmp/.
    """
    if not raw:
        raise IngestError("audit artifact path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise IngestError("path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise IngestError("symlinked audit artifact paths are not allowed", "symlink_rejected")
    if not candidate.exists():
        raise IngestError(f"audit artifact does not exist: {raw}", "missing_file")
    if not candidate.is_file():
        raise IngestError(f"audit artifact is not a file: {raw}", "not_a_file")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise IngestError("audit artifact must resolve inside the repository", "outside_repo") from None

    rel_parts = rel.parts
    if rel_parts and rel_parts[0] in REJECTED_INPUT_ROOTS:
        raise IngestError(f"audit artifact must not resolve under {rel_parts[0]}/", "rejected_source_root")
    if not rel_parts or rel_parts[0] != "tmp":
        if any(part.startswith(".") for part in rel_parts):
            raise IngestError("hidden paths are not allowed outside tmp/", "hidden_path_rejected")

    return resolved


def _validate_store_dir(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if resolved != GUARDED_STORE_ROOT and GUARDED_STORE_ROOT not in resolved.parents:
        raise IngestError(f"store dir must resolve under {DEFAULT_STORE_DIR}", "store_path_rejected")
    return resolved


def _read_existing_records(store_file: Path) -> list[dict[str, Any]]:
    if not store_file.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in store_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            raise IngestError("audit store contains a corrupted record line", "hash_chain_read_failure") from None
        if not isinstance(obj, dict) or "record_hash" not in obj:
            raise IngestError("audit store contains a malformed record", "hash_chain_read_failure")
        records.append(obj)
    return records


def _build_record(
    raw_audit: dict[str, Any],
    source_ref: str,
    artifact_hash: str,
    previous_record_hash: str | None,
    operator_note: str | None,
) -> dict[str, Any]:
    """Build the normalized record and derive its hash-chain identity.

    record_hash is the sha256 of the canonical JSON of the record with
    `record_hash` and `audit_record_id` both excluded: audit_record_id is
    derived from record_hash, so it cannot be part of its own hash input.
    Verification recomputes the same canonical JSON (excluding both fields)
    from a stored record and compares the result to the stored record_hash.
    """
    record: dict[str, Any] = {
        "audit_schema_version": _extract(raw_audit, "audit_schema_version"),
        "source_phase": SOURCE_PHASE,
        "product_id": _extract(raw_audit, "product_id"),
        "report_week": _extract(raw_audit, "report_week"),
        "selected_gate": _extract(raw_audit, "selected_gate"),
        "wrapper_version": _extract(raw_audit, "wrapper_version"),
        "operator": _extract(raw_audit, "operator"),
        "approval_reason": _extract(raw_audit, "approval_reason"),
        "approval_intent": _extract(raw_audit, "approval_intent"),
        "execution_mode": _extract(raw_audit, "execution_mode"),
        "emergency_stop_state": _extract(raw_audit, "emergency_stop_state"),
        "mutation_attempted": _extract(raw_audit, "mutation_attempted"),
        "primitive_name": _extract(raw_audit, "primitive_name"),
        "primitive_outcome": _extract(raw_audit, "primitive_outcome"),
        "phase6b_packet_ref": _extract(raw_audit, "phase6b_packet_ref"),
        "phase6c_verifier_ref": _extract(raw_audit, "phase6c_verifier_ref"),
        "phase6e_plan_ref": _extract(raw_audit, "phase6e_plan_ref"),
        "phase7b_verifier_ref": _extract(raw_audit, "phase7b_verifier_ref"),
        "intent_audit_ref": _extract(raw_audit, "intent_audit_ref"),
        "result_audit_ref": _extract(raw_audit, "result_audit_ref"),
        "source_audit_artifact_ref": source_ref,
        "precondition_summary": _extract(raw_audit, "precondition_summary"),
        "result_summary": _extract(raw_audit, "result_summary"),
        "manual_review_status": None,
        "incident_id": None,
        "created_at": _extract(raw_audit, "created_at"),
        "completed_at": _extract(raw_audit, "completed_at"),
        "artifact_hash": artifact_hash,
        "previous_record_hash": previous_record_hash,
        "retention_class": DEFAULT_RETENTION_CLASS,
        "phase8b_ingested_at": _now_utc(),
        "phase8b_store_version": STORE_VERSION,
        "phase8b_operator_note": operator_note,
    }
    base_hash = hashlib.sha256(_canonical_json(record).encode("utf-8")).hexdigest()
    record["audit_record_id"] = "audit-" + base_hash[:16]
    record["record_hash"] = base_hash
    return record


def _build_summary(
    *,
    ingest_status: str,
    audit_record_id: str | None,
    source_ref: str,
    store_file: Path,
    summary_json_path: Path,
    artifact_hash: str,
    previous_record_hash: str | None,
    record_hash: str | None,
    duplicate: bool,
    appended: bool,
) -> dict[str, Any]:
    repo_root_resolved = REPO_ROOT.resolve()
    return {
        "phase8b_status": PHASE8B_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "ingest_status": ingest_status,
        "audit_record_id": audit_record_id,
        "source_audit_artifact_ref": source_ref,
        "store_path": store_file.relative_to(repo_root_resolved).as_posix(),
        "summary_path": summary_json_path.relative_to(repo_root_resolved).as_posix(),
        "artifact_hash": artifact_hash,
        "previous_record_hash": previous_record_hash,
        "record_hash": record_hash,
        "duplicate": duplicate,
        "appended": appended,
        "safety_statement": (
            "Phase 8B ingest is read-only over the source audit artifact and "
            "append-only over the local JSONL store. It executes no primitive, "
            "calls no Phase 7D wrapper, runs no Phase 7B verifier automatically, "
            "performs no vault read/write, and makes no network, backend, API, "
            "or database call."
        ),
        "limitations": [
            "local tmp prototype only",
            "JSONL only, no SQLite index",
            "no S3/DynamoDB backend",
            "no backend/API",
            "no authenticated operator identity",
            "no production deployment",
            "no automatic migration",
            "no retention enforcement",
            "no query/reporting command yet",
        ],
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 8B Local Append-only Audit Store - Ingest Summary",
        "",
        f"phase8b_status: {summary['phase8b_status']}",
        f"durable_audit_store_status: {summary['durable_audit_store_status']}",
        f"phase7d_runtime_readiness: {summary['phase7d_runtime_readiness']}",
        "",
        f"- ingest status: {summary['ingest_status']}",
        f"- audit record id: {summary['audit_record_id']}",
        f"- source artifact: {summary['source_audit_artifact_ref']}",
        f"- store path: {summary['store_path']}",
        f"- artifact hash: {summary['artifact_hash']}",
        f"- previous record hash: {summary['previous_record_hash']}",
        f"- record hash: {summary['record_hash']}",
        f"- duplicate: {summary['duplicate']}",
        f"- appended: {summary['appended']}",
        "",
        "## Safety statement",
        "",
        summary["safety_statement"],
        "",
        "## Known limitations",
        "",
    ]
    lines += [f"- {item}" for item in summary["limitations"]]
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    resolved_input = _validate_input_path(args.audit_artifact)
    store_dir = _validate_store_dir(args.store_dir)
    store_dir.mkdir(parents=True, exist_ok=True)

    store_file = store_dir / "audit-records.jsonl"
    summary_json_path = store_dir / "audit-ingest-summary.json"
    summary_md_path = store_dir / "audit-ingest-summary.md"

    raw_bytes = resolved_input.read_bytes()
    artifact_hash = hashlib.sha256(raw_bytes).hexdigest()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise IngestError("audit artifact is not valid utf-8 JSON", "invalid_json") from None
    try:
        raw_audit = json.loads(raw_text)
    except json.JSONDecodeError:
        raise IngestError("audit artifact is not valid JSON", "invalid_json") from None
    if not isinstance(raw_audit, dict):
        raise IngestError("audit artifact must be a JSON object", "invalid_json")

    source_ref = resolved_input.relative_to(REPO_ROOT.resolve()).as_posix()
    existing_records = _read_existing_records(store_file)
    duplicate_match = next(
        (r for r in existing_records if r.get("artifact_hash") == artifact_hash), None
    )

    if duplicate_match is not None:
        summary = _build_summary(
            ingest_status="duplicate_skipped",
            audit_record_id=duplicate_match.get("audit_record_id"),
            source_ref=source_ref,
            store_file=store_file,
            summary_json_path=summary_json_path,
            artifact_hash=artifact_hash,
            previous_record_hash=duplicate_match.get("previous_record_hash"),
            record_hash=duplicate_match.get("record_hash"),
            duplicate=True,
            appended=False,
        )
    else:
        previous_record_hash = existing_records[-1]["record_hash"] if existing_records else None
        record = _build_record(raw_audit, source_ref, artifact_hash, previous_record_hash, args.operator_note)
        with store_file.open("a", encoding="utf-8") as fh:
            fh.write(_canonical_json(record) + "\n")
        summary = _build_summary(
            ingest_status="appended",
            audit_record_id=record["audit_record_id"],
            source_ref=source_ref,
            store_file=store_file,
            summary_json_path=summary_json_path,
            artifact_hash=artifact_hash,
            previous_record_hash=previous_record_hash,
            record_hash=record["record_hash"],
            duplicate=False,
            appended=True,
        )

    summary_json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_md_path.write_text(_render_summary_md(summary), encoding="utf-8")
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8B local append-only audit store ingest (read-only prototype)."
    )
    parser.add_argument("--audit-artifact", required=True, dest="audit_artifact")
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR, dest="store_dir")
    parser.add_argument("--operator-note", default=None, dest="operator_note")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary = run(args)
    except IngestError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"ingest_status: {summary['ingest_status']}")
    print(f"audit_record_id: {summary['audit_record_id']}")
    print(f"store_path: {summary['store_path']}")
    print(f"summary_path: {summary['summary_path']}")
    print(f"phase8b_status: {summary['phase8b_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
