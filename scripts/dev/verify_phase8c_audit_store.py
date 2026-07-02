#!/usr/bin/env python3
"""Phase 8C read-only audit store verifier / reporting over Phase 8B JSONL.

Reads the Phase 8B local append-only JSONL audit store (or any caller-provided
JSONL path), verifies per-record hash integrity and hash-chain continuity,
detects duplicate identifiers and malformed lines, and writes a read-only
verification/reporting summary under tmp/phase8c-audit-report/. This script
never appends to or otherwise mutates the source JSONL store, never executes
an approval primitive, never calls the Phase 7D wrapper or the Phase 7B
verifier, never reads or writes the vault, and never makes a network,
backend, API, or database call. Python standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STORE_PATH = "tmp/phase8b-audit-store/audit-records.jsonl"
DEFAULT_REPORT_DIR = "tmp/phase8c-audit-report"
GUARDED_REPORT_ROOT = (REPO_ROOT / DEFAULT_REPORT_DIR).resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PHASE8C_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "jsonl_verifier_reporting"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"

REQUIRED_REPORT_FIELDS = (
    "audit_record_id",
    "audit_schema_version",
    "source_phase",
    "product_id",
    "report_week",
    "selected_gate",
    "operator",
    "primitive_outcome",
    "artifact_hash",
    "previous_record_hash",
    "record_hash",
    "manual_review_status",
    "created_at",
    "phase8b_ingested_at",
)

GROUP_FIELDS = (
    ("by_product_id", "product_id"),
    ("by_report_week", "report_week"),
    ("by_selected_gate", "selected_gate"),
    ("by_operator", "operator"),
    ("by_primitive_outcome", "primitive_outcome"),
    ("by_manual_review_status", "manual_review_status"),
)


class VerifierPathError(Exception):
    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _canonical_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _recompute_record_hash(record: dict[str, Any]) -> str:
    stripped = {k: v for k, v in record.items() if k not in ("record_hash", "audit_record_id")}
    return hashlib.sha256(_canonical_json(stripped).encode("utf-8")).hexdigest()


def _validate_store_path(raw: str) -> Path | None:
    """Return the resolved store path, or None if it is safely absent.

    Raises VerifierPathError for any unsafe path (traversal, symlink, outside
    the repository, resolving under a rejected root, or an existing
    non-file). A path that simply does not exist is not an error: it signals
    an empty store.
    """
    if not raw:
        raise VerifierPathError("store path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise VerifierPathError("path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise VerifierPathError("symlinked store paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise VerifierPathError("store path must resolve inside the repository", "outside_repo") from None

    rel_parts = rel.parts
    if rel_parts and rel_parts[0] in REJECTED_ROOTS:
        raise VerifierPathError(f"store path must not resolve under {rel_parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise VerifierPathError(f"store path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_report_dir(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if resolved != GUARDED_REPORT_ROOT and GUARDED_REPORT_ROOT not in resolved.parents:
        raise VerifierPathError(f"report dir must resolve under {DEFAULT_REPORT_DIR}", "report_dir_rejected")
    return resolved


def _verify_store(store_file: Path) -> dict[str, Any]:
    total_lines = 0
    record_count = 0
    invalid_line_count = 0
    issues: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    seen_audit_ids: set[Any] = set()
    seen_artifact_hashes: set[Any] = set()
    seen_record_hashes: set[Any] = set()
    dup_audit_id_count = 0
    dup_artifact_hash_count = 0
    dup_record_hash_count = 0

    hash_chain_valid = True
    first_record_seen = False
    prior_record_hash: Any = None

    for line_number, line in enumerate(store_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        total_lines += 1

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            invalid_line_count += 1
            issues.append(
                {"line_number": line_number, "issue_type": "invalid_json", "message": "line is not valid JSON", "audit_record_id": None}
            )
            continue
        if not isinstance(obj, dict):
            invalid_line_count += 1
            issues.append(
                {"line_number": line_number, "issue_type": "not_object", "message": "line is not a JSON object", "audit_record_id": None}
            )
            continue

        record_count += 1
        audit_id = obj.get("audit_record_id")

        missing = [field for field in REQUIRED_REPORT_FIELDS if field not in obj]
        if missing:
            issues.append(
                {
                    "line_number": line_number,
                    "issue_type": "missing_required_field",
                    "message": f"missing fields: {', '.join(missing)}",
                    "audit_record_id": audit_id,
                }
            )

        if audit_id is not None:
            if audit_id in seen_audit_ids:
                dup_audit_id_count += 1
                issues.append(
                    {
                        "line_number": line_number,
                        "issue_type": "duplicate_audit_record_id",
                        "message": f"duplicate audit_record_id: {audit_id}",
                        "audit_record_id": audit_id,
                    }
                )
            else:
                seen_audit_ids.add(audit_id)

        artifact_hash = obj.get("artifact_hash")
        if artifact_hash is not None:
            if artifact_hash in seen_artifact_hashes:
                dup_artifact_hash_count += 1
                issues.append(
                    {
                        "line_number": line_number,
                        "issue_type": "duplicate_artifact_hash",
                        "message": f"duplicate artifact_hash: {artifact_hash}",
                        "audit_record_id": audit_id,
                    }
                )
            else:
                seen_artifact_hashes.add(artifact_hash)

        record_hash = obj.get("record_hash")
        if record_hash is not None:
            if record_hash in seen_record_hashes:
                dup_record_hash_count += 1
                issues.append(
                    {
                        "line_number": line_number,
                        "issue_type": "duplicate_record_hash",
                        "message": f"duplicate record_hash: {record_hash}",
                        "audit_record_id": audit_id,
                    }
                )
            else:
                seen_record_hashes.add(record_hash)

        recomputed = _recompute_record_hash(obj)
        if record_hash != recomputed:
            hash_chain_valid = False
            issues.append(
                {
                    "line_number": line_number,
                    "issue_type": "hash_mismatch",
                    "message": "record_hash does not match recomputed hash",
                    "audit_record_id": audit_id,
                }
            )

        previous_record_hash = obj.get("previous_record_hash")
        if not first_record_seen:
            if previous_record_hash is not None:
                hash_chain_valid = False
                issues.append(
                    {
                        "line_number": line_number,
                        "issue_type": "previous_record_hash_mismatch",
                        "message": "first record must have previous_record_hash null",
                        "audit_record_id": audit_id,
                    }
                )
            first_record_seen = True
        elif previous_record_hash != prior_record_hash:
            hash_chain_valid = False
            issues.append(
                {
                    "line_number": line_number,
                    "issue_type": "previous_record_hash_mismatch",
                    "message": "previous_record_hash does not match the prior record's record_hash",
                    "audit_record_id": audit_id,
                }
            )
        prior_record_hash = record_hash

        records.append(obj)

    return {
        "total_lines": total_lines,
        "record_count": record_count,
        "invalid_line_count": invalid_line_count,
        "issues": issues,
        "hash_chain_valid": hash_chain_valid,
        "dup_audit_id_count": dup_audit_id_count,
        "dup_artifact_hash_count": dup_artifact_hash_count,
        "dup_record_hash_count": dup_record_hash_count,
        "records": records,
    }


def _build_group_summary(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = record.get(field)
        key = "null" if value is None else str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _safety_statement() -> str:
    return (
        "Phase 8C verification is read-only against the source JSONL audit "
        "store. It never appends to or otherwise mutates audit-records.jsonl, "
        "executes no primitive, calls no Phase 7D wrapper, runs no Phase 7B "
        "verifier automatically, performs no vault read/write, and makes no "
        "network, backend, API, or database call."
    )


def _limitations() -> list[str]:
    return [
        "local tmp report only",
        "no SQLite index",
        "no S3/DynamoDB",
        "no backend/API",
        "no authenticated identity",
        "no production deployment",
        "no retention enforcement",
        "no advanced query CLI",
        "no automatic remediation",
    ]


def _empty_report(store_path_ref: str | None, report_dir: Path) -> dict[str, Any]:
    return {
        "phase8c_status": PHASE8C_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "verification_status": "empty",
        "store_path": store_path_ref,
        "report_dir": _rel(report_dir),
        "total_lines": 0,
        "record_count": 0,
        "invalid_line_count": 0,
        "issue_count": 0,
        "hash_chain_valid": True,
        "duplicate_audit_record_id_count": 0,
        "duplicate_artifact_hash_count": 0,
        "duplicate_record_hash_count": 0,
        "summaries": {name: {} for name, _ in GROUP_FIELDS},
        "issues": [],
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _invalid_report(store_path_ref: str | None, report_dir: Path, category: str, message: str) -> dict[str, Any]:
    return {
        "phase8c_status": PHASE8C_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "verification_status": "invalid",
        "store_path": store_path_ref,
        "report_dir": _rel(report_dir),
        "total_lines": 0,
        "record_count": 0,
        "invalid_line_count": 0,
        "issue_count": 1,
        "hash_chain_valid": False,
        "duplicate_audit_record_id_count": 0,
        "duplicate_artifact_hash_count": 0,
        "duplicate_record_hash_count": 0,
        "summaries": {name: {} for name, _ in GROUP_FIELDS},
        "issues": [
            {"line_number": None, "issue_type": category, "message": message, "audit_record_id": None}
        ],
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT.resolve()).as_posix()


def _build_report(store_path_ref: str, report_dir: Path, verification: dict[str, Any]) -> dict[str, Any]:
    issue_count = len(verification["issues"])
    record_count = verification["record_count"]
    if verification["total_lines"] == 0:
        # Truly empty content (no non-blank lines at all), as opposed to
        # non-blank lines that failed to parse as records (which is a
        # warning: something was there, and it had a problem).
        verification_status = "empty"
    elif issue_count == 0 and verification["hash_chain_valid"]:
        verification_status = "valid"
    else:
        verification_status = "warning"

    summaries = {name: _build_group_summary(verification["records"], field) for name, field in GROUP_FIELDS}

    return {
        "phase8c_status": PHASE8C_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "verification_status": verification_status,
        "store_path": store_path_ref,
        "report_dir": _rel(report_dir),
        "total_lines": verification["total_lines"],
        "record_count": record_count,
        "invalid_line_count": verification["invalid_line_count"],
        "issue_count": issue_count,
        "hash_chain_valid": verification["hash_chain_valid"],
        "duplicate_audit_record_id_count": verification["dup_audit_id_count"],
        "duplicate_artifact_hash_count": verification["dup_artifact_hash_count"],
        "duplicate_record_hash_count": verification["dup_record_hash_count"],
        "summaries": summaries,
        "issues": verification["issues"],
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 8C Audit Store Verification / Reporting",
        "",
        f"phase8c_status: {report['phase8c_status']}",
        f"durable_audit_store_status: {report['durable_audit_store_status']}",
        f"phase7d_runtime_readiness: {report['phase7d_runtime_readiness']}",
        "",
        f"- verification status: {report['verification_status']}",
        f"- store path: {report['store_path']}",
        f"- record count: {report['record_count']}",
        f"- issue count: {report['issue_count']}",
        f"- hash-chain valid: {report['hash_chain_valid']}",
        "",
        "## Duplicate summary",
        "",
        f"- duplicate audit_record_id: {report['duplicate_audit_record_id_count']}",
        f"- duplicate artifact_hash: {report['duplicate_artifact_hash_count']}",
        f"- duplicate record_hash: {report['duplicate_record_hash_count']}",
        "",
        "## Reporting summaries",
        "",
    ]
    for name, _ in GROUP_FIELDS:
        lines.append(f"### {name}")
        lines.append("")
        group = report["summaries"].get(name, {})
        if group:
            for key, count in sorted(group.items()):
                lines.append(f"- {key}: {count}")
        else:
            lines.append("- none")
        lines.append("")

    lines.append("## Issues")
    lines.append("")
    if report["issues"]:
        lines.append("| line | type | audit_record_id | message |")
        lines.append("| --- | --- | --- | --- |")
        for issue in report["issues"]:
            lines.append(
                f"| {issue.get('line_number')} | {issue.get('issue_type')} | "
                f"{issue.get('audit_record_id')} | {issue.get('message')} |"
            )
    else:
        lines.append("No issues")
    lines.append("")

    lines += [
        "## Safety statement",
        "",
        report["safety_statement"],
        "",
        "## Known limitations",
        "",
    ]
    lines += [f"- {item}" for item in report["limitations"]]
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    """Return (report, ok) where ok is False only on a critical path/store failure."""
    report_dir = _validate_report_dir(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        store_file = _validate_store_path(args.store_path)
    except VerifierPathError as exc:
        report = _invalid_report(args.store_path, report_dir, exc.category, str(exc))
        _write_report(report_dir, report)
        return report, False

    if store_file is None:
        report = _empty_report(args.store_path, report_dir)
        _write_report(report_dir, report)
        return report, True

    verification = _verify_store(store_file)
    report = _build_report(_rel(store_file), report_dir, verification)
    _write_report(report_dir, report)
    return report, True


def _write_report(report_dir: Path, report: dict[str, Any]) -> None:
    json_path = report_dir / "audit-store-verification.json"
    md_path = report_dir / "audit-store-verification.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_md(report), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8C read-only audit store verifier / reporting over Phase 8B JSONL."
    )
    parser.add_argument("--store-path", default=DEFAULT_STORE_PATH, dest="store_path")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR, dest="report_dir")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report, ok = run(args)
    except VerifierPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"verification_status: {report['verification_status']}")
    print(f"record_count: {report['record_count']}")
    print(f"issue_count: {report['issue_count']}")
    print(f"hash_chain_valid: {report['hash_chain_valid']}")
    print(f"phase8c_status: {report['phase8c_status']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
