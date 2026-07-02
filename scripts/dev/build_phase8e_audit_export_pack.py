#!/usr/bin/env python3
"""Phase 8E read-only audit export pack over Phase 8B/8C/8D local evidence.

Reads the Phase 8B JSONL audit store, the optional Phase 8C verification
report (JSON/Markdown), and the optional Phase 8D query result (JSON/
Markdown), then writes a read-only export manifest and Markdown summary
under tmp/phase8e-audit-export/. Optionally copies the source evidence files
byte-identical into tmp/phase8e-audit-export/evidence/. This script never
appends to or otherwise mutates any source evidence file, never executes an
approval primitive, never calls the Phase 7D wrapper, the Phase 8B ingest
writer, the Phase 8C verifier, or the Phase 8D query CLI, never reads or
writes the vault, and never makes a network, backend, API, or database call.
Python standard library only.
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

DEFAULT_STORE_PATH = "tmp/phase8b-audit-store/audit-records.jsonl"
DEFAULT_VERIFICATION_JSON = "tmp/phase8c-audit-report/audit-store-verification.json"
DEFAULT_VERIFICATION_MD = "tmp/phase8c-audit-report/audit-store-verification.md"
DEFAULT_QUERY_JSON = "tmp/phase8d-audit-query/audit-query-result.json"
DEFAULT_QUERY_MD = "tmp/phase8d-audit-query/audit-query-result.md"
DEFAULT_EXPORT_DIR = "tmp/phase8e-audit-export"
GUARDED_EXPORT_ROOT = (REPO_ROOT / DEFAULT_EXPORT_DIR).resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PHASE8E_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "export_pack"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"

STORE_LABEL = "audit_records_jsonl"

# (label, argparse dest, evidence-copy destination filename)
EVIDENCE_SPECS = (
    (STORE_LABEL, "store_path", "audit-records.jsonl"),
    ("verification_json", "verification_json", "audit-store-verification.json"),
    ("verification_md", "verification_md", "audit-store-verification.md"),
    ("query_json", "query_json", "audit-query-result.json"),
    ("query_md", "query_md", "audit-query-result.md"),
)

GROUP_FIELDS = (
    ("by_product_id", "product_id"),
    ("by_report_week", "report_week"),
    ("by_selected_gate", "selected_gate"),
    ("by_operator", "operator"),
    ("by_primitive_outcome", "primitive_outcome"),
    ("by_manual_review_status", "manual_review_status"),
)


class ExportPathError(Exception):
    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT.resolve()).as_posix()


def _validate_optional_path(raw: str) -> Path | None:
    """Return the resolved path, or None if it is safely absent."""
    if not raw:
        raise ExportPathError("evidence path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise ExportPathError("path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise ExportPathError("symlinked evidence paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise ExportPathError("evidence path must resolve inside the repository", "outside_repo") from None

    rel_parts = rel.parts
    if rel_parts and rel_parts[0] in REJECTED_ROOTS:
        raise ExportPathError(f"evidence path must not resolve under {rel_parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise ExportPathError(f"evidence path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_export_dir(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if resolved != GUARDED_EXPORT_ROOT and GUARDED_EXPORT_ROOT not in resolved.parents:
        raise ExportPathError(f"export dir must resolve under {DEFAULT_EXPORT_DIR}", "export_dir_rejected")
    return resolved


def _read_jsonl(store_file: Path) -> tuple[int, int, list[dict[str, Any]], list[dict[str, Any]]]:
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
                {"line_number": line_number, "issue_type": "invalid_json", "message": "line is not valid JSON", "source": STORE_LABEL}
            )
            continue
        if not isinstance(obj, dict):
            invalid_line_count += 1
            warnings.append(
                {"line_number": line_number, "issue_type": "not_object", "message": "line is not a JSON object", "source": STORE_LABEL}
            )
            continue
        records.append(obj)

    return total_lines, invalid_line_count, warnings, records


def _build_group_summary(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = record.get(field)
        key = "null" if value is None else str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _read_optional_report_status(path: Path | None, status_field: str, source_label: str, warnings: list[dict[str, Any]]) -> str | None:
    if path is None:
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        warnings.append(
            {"line_number": None, "issue_type": "invalid_report_json", "message": f"{source_label} is not valid JSON", "source": source_label}
        )
        return None
    if not isinstance(obj, dict):
        warnings.append(
            {"line_number": None, "issue_type": "invalid_report_json", "message": f"{source_label} is not a JSON object", "source": source_label}
        )
        return None
    return obj.get(status_field)


def _safety_statement() -> str:
    return (
        "Phase 8E export is read-only against all source evidence. It never "
        "appends to or otherwise mutates audit-records.jsonl or any Phase 8C/"
        "8D report, executes no primitive, calls no Phase 7D wrapper, calls "
        "no Phase 8B ingest writer, calls no Phase 8C verifier, calls no "
        "Phase 8D query CLI, performs no vault read/write, and makes no "
        "network, backend, API, or database call."
    )


def _limitations() -> list[str]:
    return [
        "local tmp export only",
        "no archive signing",
        "no encryption",
        "no SQLite index",
        "no S3/DynamoDB",
        "no backend/API",
        "no authenticated identity",
        "no production deployment",
        "no retention enforcement",
        "no automated distribution",
        "no automatic remediation",
    ]


def _render_md(manifest: dict[str, Any]) -> str:
    lines = [
        "# Phase 8E Audit Export Pack",
        "",
        f"phase8e_status: {manifest['phase8e_status']}",
        f"durable_audit_store_status: {manifest['durable_audit_store_status']}",
        f"phase7d_runtime_readiness: {manifest['phase7d_runtime_readiness']}",
        "",
        f"- export status: {manifest['export_status']}",
        f"- export dir: {manifest['export_dir']}",
        f"- record count: {manifest['record_count']}",
        f"- warning count: {manifest['warning_count']}",
        f"- verification status: {manifest['verification_status']}",
        f"- query status: {manifest['query_status']}",
        "",
        "## Source evidence",
        "",
        "| label | path | exists | sha256 | size_bytes | copied_to |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in manifest["source_evidence"]:
        lines.append(
            f"| {entry['label']} | {entry['path']} | {entry['exists']} | {entry['sha256']} | "
            f"{entry['size_bytes']} | {entry['copied_to']} |"
        )
    lines.append("")

    lines.append("## Missing evidence")
    lines.append("")
    if manifest["missing_evidence"]:
        lines += [f"- {label}" for label in manifest["missing_evidence"]]
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Source hashes")
    lines.append("")
    for label, digest in sorted(manifest["source_hashes"].items()):
        lines.append(f"- {label}: {digest}")
    lines.append("")

    lines.append("## Reporting summaries")
    lines.append("")
    for name, _ in GROUP_FIELDS:
        lines.append(f"### {name}")
        lines.append("")
        group = manifest["summaries"].get(name, {})
        if group:
            for key, count in sorted(group.items()):
                lines.append(f"- {key}: {count}")
        else:
            lines.append("- none")
        lines.append("")

    lines.append("## Copied files")
    lines.append("")
    if manifest["include_copies"] and manifest["copied_files"]:
        for entry in manifest["copied_files"]:
            lines.append(f"- {entry['label']}: {entry['dest_path']}")
    elif manifest["include_copies"]:
        lines.append("- none")
    else:
        lines.append("- not requested (`--include-copies` was not set)")
    lines.append("")

    lines += [
        "## Safety statement",
        "",
        manifest["safety_statement"],
        "",
        "## Known limitations",
        "",
    ]
    lines += [f"- {item}" for item in manifest["limitations"]]
    lines.append("")
    return "\n".join(lines)


def _write_output(export_dir: Path, manifest: dict[str, Any]) -> None:
    manifest_path = export_dir / "audit-export-manifest.json"
    summary_path = export_dir / "audit-export-summary.md"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(_render_md(manifest), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    export_dir = _validate_export_dir(args.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    resolved: dict[str, Path | None] = {}
    for label, attr, _dest_name in EVIDENCE_SPECS:
        resolved[label] = _validate_optional_path(getattr(args, attr))

    warnings: list[dict[str, Any]] = []
    source_evidence: list[dict[str, Any]] = []
    source_hashes: dict[str, str | None] = {}
    missing_evidence: list[str] = []

    for label, attr, _dest_name in EVIDENCE_SPECS:
        raw = getattr(args, attr)
        path = resolved[label]
        if path is None:
            source_evidence.append(
                {"label": label, "path": raw, "exists": False, "allowed": True, "sha256": None, "size_bytes": None, "copied_to": None}
            )
            source_hashes[label] = None
            missing_evidence.append(label)
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        source_evidence.append(
            {"label": label, "path": _rel(path), "exists": True, "allowed": True, "sha256": digest, "size_bytes": len(data), "copied_to": None}
        )
        source_hashes[label] = digest

    store_path_resolved = resolved[STORE_LABEL]
    total_lines = invalid_line_count = 0
    records: list[dict[str, Any]] = []
    if store_path_resolved is not None:
        total_lines, invalid_line_count, jsonl_warnings, records = _read_jsonl(store_path_resolved)
        warnings.extend(jsonl_warnings)

    record_count = len(records)
    summaries = {name: _build_group_summary(records, field) for name, field in GROUP_FIELDS}

    verification_status = _read_optional_report_status(
        resolved["verification_json"], "verification_status", "verification_json", warnings
    )
    query_status = _read_optional_report_status(resolved["query_json"], "query_status", "query_json", warnings)

    copied_files: list[dict[str, Any]] = []
    if args.include_copies:
        evidence_dir = export_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        for entry, (label, _attr, dest_name) in zip(source_evidence, EVIDENCE_SPECS):
            path = resolved[label]
            if path is None:
                continue
            dest = evidence_dir / dest_name
            dest.write_bytes(path.read_bytes())
            dest_rel = _rel(dest)
            entry["copied_to"] = dest_rel
            copied_files.append({"label": label, "dest_path": dest_rel, "sha256": entry["sha256"]})

    store_missing = store_path_resolved is None
    has_warnings = bool(warnings)
    has_missing_optional = any(label != STORE_LABEL for label in missing_evidence)

    if store_missing or record_count == 0:
        export_status = "empty"
    elif not has_warnings and not has_missing_optional:
        export_status = "success"
    else:
        export_status = "warning"

    manifest = {
        "phase8e_status": PHASE8E_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "export_status": export_status,
        "export_dir": _rel(export_dir),
        "generated_at": _now_utc(),
        "include_copies": args.include_copies,
        "source_evidence": source_evidence,
        "missing_evidence": missing_evidence,
        "source_hashes": source_hashes,
        "record_count": record_count,
        "invalid_line_count": invalid_line_count,
        "warning_count": len(warnings),
        "verification_status": verification_status,
        "query_status": query_status,
        "summaries": summaries,
        "copied_files": copied_files,
        "warnings": warnings,
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }
    _write_output(export_dir, manifest)
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8E read-only audit export pack over Phase 8B/8C/8D local evidence."
    )
    parser.add_argument("--store-path", default=DEFAULT_STORE_PATH, dest="store_path")
    parser.add_argument("--verification-json", default=DEFAULT_VERIFICATION_JSON, dest="verification_json")
    parser.add_argument("--verification-md", default=DEFAULT_VERIFICATION_MD, dest="verification_md")
    parser.add_argument("--query-json", default=DEFAULT_QUERY_JSON, dest="query_json")
    parser.add_argument("--query-md", default=DEFAULT_QUERY_MD, dest="query_md")
    parser.add_argument("--export-dir", default=DEFAULT_EXPORT_DIR, dest="export_dir")
    parser.add_argument("--include-copies", action="store_true", dest="include_copies")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        manifest = run(args)
    except ExportPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"export_status: {manifest['export_status']}")
    print(f"record_count: {manifest['record_count']}")
    print(f"warning_count: {manifest['warning_count']}")
    print(f"phase8e_status: {manifest['phase8e_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
