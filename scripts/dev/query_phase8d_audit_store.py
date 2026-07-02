#!/usr/bin/env python3
"""Phase 8D read-only query CLI over the Phase 8B JSONL audit store.

Reads the Phase 8B local append-only JSONL audit store (or any caller-
provided JSONL path), filters/sorts/limits records, computes a best-effort
per-record hash status, and writes a read-only query result under
tmp/phase8d-audit-query/. This script never appends to or otherwise mutates
the source JSONL store, never executes an approval primitive, never calls
the Phase 7D wrapper, the Phase 8B ingest writer, or the Phase 8C verifier,
never reads or writes the vault, and never makes a network, backend, API, or
database call. Python standard library only.
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
DEFAULT_REPORT_DIR = "tmp/phase8d-audit-query"
GUARDED_REPORT_ROOT = (REPO_ROOT / DEFAULT_REPORT_DIR).resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PHASE8D_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "jsonl_query_cli"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"

ALLOWED_GATES = ("promote", "decision", "finalization")
ALLOWED_HASH_STATUSES = ("valid", "invalid", "unknown")
ALLOWED_SORT_FIELDS = ("created_at", "phase8b_ingested_at")

FILTER_FIELDS = (
    "product_id",
    "report_week",
    "selected_gate",
    "operator",
    "primitive_outcome",
    "manual_review_status",
    "incident_id",
    "hash_status",
)

DEFAULT_LIMIT = 100
MIN_LIMIT = 1
MAX_LIMIT = 1000


class QueryPathError(Exception):
    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _canonical_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_status(record: dict[str, Any]) -> str:
    record_hash = record.get("record_hash")
    if not record_hash:
        return "unknown"
    stripped = {k: v for k, v in record.items() if k not in ("record_hash", "audit_record_id")}
    recomputed = hashlib.sha256(_canonical_json(stripped).encode("utf-8")).hexdigest()
    return "valid" if recomputed == record_hash else "invalid"


def _validate_store_path(raw: str) -> Path | None:
    """Return the resolved store path, or None if it is safely absent."""
    if not raw:
        raise QueryPathError("store path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise QueryPathError("path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise QueryPathError("symlinked store paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise QueryPathError("store path must resolve inside the repository", "outside_repo") from None

    rel_parts = rel.parts
    if rel_parts and rel_parts[0] in REJECTED_ROOTS:
        raise QueryPathError(f"store path must not resolve under {rel_parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise QueryPathError(f"store path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_report_dir(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if resolved != GUARDED_REPORT_ROOT and GUARDED_REPORT_ROOT not in resolved.parents:
        raise QueryPathError(f"report dir must resolve under {DEFAULT_REPORT_DIR}", "report_dir_rejected")
    return resolved


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT.resolve()).as_posix()


def _read_store(store_file: Path) -> tuple[int, int, list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (total_lines, invalid_line_count, warnings, records)."""
    total_lines = 0
    invalid_line_count = 0
    warnings: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for line_number, line in enumerate(store_file.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        total_lines += 1
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            invalid_line_count += 1
            warnings.append(
                {"line_number": line_number, "issue_type": "invalid_json", "message": "line is not valid JSON"}
            )
            continue
        if not isinstance(obj, dict):
            invalid_line_count += 1
            warnings.append(
                {"line_number": line_number, "issue_type": "not_object", "message": "line is not a JSON object"}
            )
            continue
        records.append(obj)

    return total_lines, invalid_line_count, warnings, records


def _matches(record: dict[str, Any], hash_status: str, filters: dict[str, str | None]) -> bool:
    for field in FILTER_FIELDS:
        value = filters.get(field)
        if value is None:
            continue
        actual = hash_status if field == "hash_status" else record.get(field)
        if actual != value:
            return False
    return True


def _sort_key(record: dict[str, Any], sort_by: str) -> str:
    value = record.get(sort_by)
    return value if isinstance(value, str) else ""


def _safety_statement() -> str:
    return (
        "Phase 8D query is read-only against the source JSONL audit store. "
        "It never appends to or otherwise mutates audit-records.jsonl, "
        "executes no primitive, calls no Phase 7D wrapper, calls no Phase 8B "
        "ingest writer, calls no Phase 8C verifier automatically, performs no "
        "vault read/write, and makes no network, backend, API, or database "
        "call."
    )


def _limitations() -> list[str]:
    return [
        "local tmp query report only",
        "no SQLite index",
        "no S3/DynamoDB",
        "no backend/API",
        "no authenticated identity",
        "no production deployment",
        "no retention enforcement",
        "no full-text search",
        "no pagination cursor",
        "no automatic remediation",
    ]


def _base_report(
    *,
    query_status: str,
    store_path_ref: str | None,
    report_dir: Path,
    filters: dict[str, str | None],
    sort_by: str,
    descending: bool,
    limit: int,
    total_lines: int,
    total_records_read: int,
    invalid_line_count: int,
    warnings: list[dict[str, Any]],
    matched_records: int,
    returned: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "phase8d_status": PHASE8D_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "query_status": query_status,
        "store_path": store_path_ref,
        "report_dir": _rel(report_dir),
        "filters": filters,
        "sort_by": sort_by,
        "descending": descending,
        "limit": limit,
        "total_lines": total_lines,
        "total_records_read": total_records_read,
        "invalid_line_count": invalid_line_count,
        "warning_count": len(warnings),
        "matched_records": matched_records,
        "returned_records": len(returned),
        "warnings": warnings,
        "records": returned,
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 8D Audit Store Query Result",
        "",
        f"phase8d_status: {report['phase8d_status']}",
        f"durable_audit_store_status: {report['durable_audit_store_status']}",
        f"phase7d_runtime_readiness: {report['phase7d_runtime_readiness']}",
        "",
        f"- query status: {report['query_status']}",
        f"- store path: {report['store_path']}",
        f"- filters: {json.dumps(report['filters'], sort_keys=True)}",
        f"- total records read: {report['total_records_read']}",
        f"- matched records: {report['matched_records']}",
        f"- returned records: {report['returned_records']}",
        f"- warning count: {report['warning_count']}",
        "",
        "## Result",
        "",
    ]
    if report["records"]:
        lines.append("| audit_record_id | product_id | report_week | selected_gate | operator | primitive_outcome | hash_status |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for entry in report["records"]:
            rec = entry["record"]
            lines.append(
                f"| {rec.get('audit_record_id')} | {rec.get('product_id')} | {rec.get('report_week')} | "
                f"{rec.get('selected_gate')} | {rec.get('operator')} | {rec.get('primitive_outcome')} | "
                f"{entry.get('hash_status')} |"
            )
    else:
        lines.append("No matching records")
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


def _write_report(report_dir: Path, report: dict[str, Any]) -> None:
    json_path = report_dir / "audit-query-result.json"
    md_path = report_dir / "audit-query-result.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_md(report), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    report_dir = _validate_report_dir(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    filters: dict[str, str | None] = {field: getattr(args, field.replace("-", "_")) for field in FILTER_FIELDS}

    store_file = _validate_store_path(args.store_path)
    if store_file is None:
        report = _base_report(
            query_status="empty",
            store_path_ref=args.store_path,
            report_dir=report_dir,
            filters=filters,
            sort_by=args.sort_by,
            descending=args.descending,
            limit=args.limit,
            total_lines=0,
            total_records_read=0,
            invalid_line_count=0,
            warnings=[],
            matched_records=0,
            returned=[],
        )
        _write_report(report_dir, report)
        return report

    total_lines, invalid_line_count, warnings, records = _read_store(store_file)
    total_records_read = len(records)

    if total_records_read == 0:
        report = _base_report(
            query_status="empty",
            store_path_ref=_rel(store_file),
            report_dir=report_dir,
            filters=filters,
            sort_by=args.sort_by,
            descending=args.descending,
            limit=args.limit,
            total_lines=total_lines,
            total_records_read=0,
            invalid_line_count=invalid_line_count,
            warnings=warnings,
            matched_records=0,
            returned=[],
        )
        _write_report(report_dir, report)
        return report

    annotated = [{"record": record, "hash_status": _hash_status(record)} for record in records]
    matched = [entry for entry in annotated if _matches(entry["record"], entry["hash_status"], filters)]
    matched.sort(key=lambda entry: _sort_key(entry["record"], args.sort_by), reverse=args.descending)
    returned = matched[: args.limit]

    if invalid_line_count > 0:
        query_status = "warning"
    elif not matched:
        query_status = "no_matches"
    else:
        query_status = "success"

    report = _base_report(
        query_status=query_status,
        store_path_ref=_rel(store_file),
        report_dir=report_dir,
        filters=filters,
        sort_by=args.sort_by,
        descending=args.descending,
        limit=args.limit,
        total_lines=total_lines,
        total_records_read=total_records_read,
        invalid_line_count=invalid_line_count,
        warnings=warnings,
        matched_records=len(matched),
        returned=returned,
    )
    _write_report(report_dir, report)
    return report


def _limit_type(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid limit: {value}") from None
    if parsed < MIN_LIMIT or parsed > MAX_LIMIT:
        raise argparse.ArgumentTypeError(f"limit must be between {MIN_LIMIT} and {MAX_LIMIT}: {parsed}")
    return parsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8D read-only query CLI over the Phase 8B JSONL audit store."
    )
    parser.add_argument("--store-path", default=DEFAULT_STORE_PATH, dest="store_path")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR, dest="report_dir")
    parser.add_argument("--product-id", default=None, dest="product_id")
    parser.add_argument("--report-week", default=None, dest="report_week")
    parser.add_argument("--selected-gate", default=None, dest="selected_gate", choices=ALLOWED_GATES)
    parser.add_argument("--operator", default=None, dest="operator")
    parser.add_argument("--primitive-outcome", default=None, dest="primitive_outcome")
    parser.add_argument("--manual-review-status", default=None, dest="manual_review_status")
    parser.add_argument("--incident-id", default=None, dest="incident_id")
    parser.add_argument("--hash-status", default=None, dest="hash_status", choices=ALLOWED_HASH_STATUSES)
    parser.add_argument("--limit", default=DEFAULT_LIMIT, dest="limit", type=_limit_type)
    parser.add_argument("--sort-by", default="phase8b_ingested_at", dest="sort_by", choices=ALLOWED_SORT_FIELDS)
    parser.add_argument("--descending", action="store_true", dest="descending")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = run(args)
    except QueryPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"query_status: {report['query_status']}")
    print(f"matched_records: {report['matched_records']}")
    print(f"returned_records: {report['returned_records']}")
    print(f"warning_count: {report['warning_count']}")
    print(f"phase8d_status: {report['phase8d_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
