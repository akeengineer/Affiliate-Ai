#!/usr/bin/env python3
"""Phase 8G local hash-only export integrity verifier over Phase 8E manifests.

Reads a Phase 8E export manifest, recomputes sha256 hashes for the source
evidence entries and copied evidence files it references, recomputes a
canonical bundle descriptor and bundle hash, best-effort recomputes a
manifest hash if the manifest already carries one, and writes a read-only
verification report under tmp/phase8g-export-integrity/. This is a
hash-only prototype: it implements no signing, generates no keys, handles
no private key material, and implements no encryption. It never mutates the
export pack or source evidence, never executes an approval primitive, never
calls the Phase 7D wrapper or the Phase 8B/8C/8D/8E scripts, never reads or
writes the vault, and never makes a network, backend, API, or database
call. A verified/hash-valid export is not approval. Python standard library
only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MANIFEST_PATH = "tmp/phase8e-audit-export/audit-export-manifest.json"
DEFAULT_REPORT_DIR = "tmp/phase8g-export-integrity"
GUARDED_REPORT_ROOT = (REPO_ROOT / DEFAULT_REPORT_DIR).resolve()
DEFAULT_EVIDENCE_DIR = (REPO_ROOT / "tmp/phase8e-audit-export/evidence").resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PHASE8G_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "export_integrity_verifier"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"
SIGNING_IMPLEMENTATION_STATUS = "not_implemented"


class IntegrityPathError(Exception):
    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT.resolve()).as_posix()


def _validate_manifest_path(raw: str) -> Path | None:
    """Return the resolved manifest path, or None if it is safely absent."""
    if not raw:
        raise IntegrityPathError("manifest path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise IntegrityPathError("path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise IntegrityPathError("symlinked manifest paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise IntegrityPathError("manifest path must resolve inside the repository", "outside_repo") from None

    rel_parts = rel.parts
    if rel_parts and rel_parts[0] in REJECTED_ROOTS:
        raise IntegrityPathError(f"manifest path must not resolve under {rel_parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise IntegrityPathError(f"manifest path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_report_dir(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    if resolved != GUARDED_REPORT_ROOT and GUARDED_REPORT_ROOT not in resolved.parents:
        raise IntegrityPathError(f"report dir must resolve under {DEFAULT_REPORT_DIR}", "report_dir_rejected")
    return resolved


def _classify_evidence_path(raw: str) -> tuple[str, Path | None]:
    """Classify an evidence path as ('safe_exists' | 'safe_missing' | 'unsafe', resolved_path_or_None)."""
    if not raw or ".." in Path(raw).parts:
        return "unsafe", None

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        return "unsafe", None

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        return "unsafe", None

    if rel.parts and rel.parts[0] in REJECTED_ROOTS:
        return "unsafe", None

    if not resolved.exists():
        return "safe_missing", resolved
    if not resolved.is_file():
        return "unsafe", None
    return "safe_exists", resolved


def _verify_source_evidence(manifest: dict[str, Any], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    source_evidence = manifest.get("source_evidence")
    if not isinstance(source_evidence, list):
        return results

    for entry in source_evidence:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label")
        raw_path = entry.get("path")
        expected_sha256 = entry.get("sha256")
        expected_size = entry.get("size_bytes")
        manifest_exists = entry.get("exists")
        manifest_allowed = entry.get("allowed", True)

        result: dict[str, Any] = {
            "label": label,
            "path": raw_path,
            "exists": False,
            "allowed": bool(manifest_allowed),
            "expected_sha256": expected_sha256,
            "actual_sha256": None,
            "expected_size_bytes": expected_size,
            "actual_size_bytes": None,
            "hash_status": "not_applicable",
            "size_status": "not_applicable",
        }

        if not manifest_exists or not manifest_allowed or not raw_path:
            results.append(result)
            continue

        status, resolved = _classify_evidence_path(raw_path)
        if status == "unsafe":
            result["allowed"] = False
            result["hash_status"] = "unavailable"
            result["size_status"] = "unavailable"
            issues.append(
                {"issue_type": "disallowed_evidence_path", "message": f"evidence path is unsafe: {raw_path}", "path": raw_path, "label": label}
            )
            results.append(result)
            continue

        if status == "safe_missing":
            result["hash_status"] = "missing_file"
            result["size_status"] = "missing_file"
            issues.append(
                {"issue_type": "missing_evidence_file", "message": f"evidence file is missing: {raw_path}", "path": raw_path, "label": label}
            )
            results.append(result)
            continue

        data = resolved.read_bytes()
        actual_sha256 = _sha256_hex(data)
        actual_size = len(data)
        result["exists"] = True
        result["actual_sha256"] = actual_sha256
        result["actual_size_bytes"] = actual_size

        if expected_sha256 is not None:
            if actual_sha256 == expected_sha256:
                result["hash_status"] = "match"
            else:
                result["hash_status"] = "mismatch"
                issues.append(
                    {"issue_type": "hash_mismatch", "message": f"evidence hash mismatch: {label}", "path": raw_path, "label": label}
                )
        else:
            result["hash_status"] = "not_checked"

        if expected_size is not None:
            if actual_size == expected_size:
                result["size_status"] = "match"
            else:
                result["size_status"] = "mismatch"
                issues.append(
                    {"issue_type": "size_mismatch", "message": f"evidence size mismatch: {label}", "path": raw_path, "label": label}
                )
        else:
            result["size_status"] = "not_checked"

        results.append(result)

    return results


def _allowed_evidence_dirs(manifest: dict[str, Any]) -> list[Path]:
    dirs = [DEFAULT_EVIDENCE_DIR]
    export_dir_raw = manifest.get("export_dir")
    if isinstance(export_dir_raw, str) and export_dir_raw:
        candidate = Path(export_dir_raw)
        if not candidate.is_absolute():
            candidate = REPO_ROOT / candidate
        dirs.append((candidate / "evidence").resolve())
    return dirs


def _verify_copied_evidence(manifest: dict[str, Any], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    copied_files = manifest.get("copied_files")
    if not isinstance(copied_files, list):
        return results

    source_by_label: dict[str, Any] = {}
    source_evidence = manifest.get("source_evidence")
    if isinstance(source_evidence, list):
        for entry in source_evidence:
            if isinstance(entry, dict) and entry.get("label"):
                source_by_label[entry["label"]] = entry

    allowed_dirs = _allowed_evidence_dirs(manifest)

    for entry in copied_files:
        if not isinstance(entry, dict):
            continue
        label = entry.get("label")
        dest_path_raw = entry.get("dest_path")
        expected_from_source = source_by_label.get(label, {}).get("sha256") if label else None
        compare_sha256 = expected_from_source if expected_from_source is not None else entry.get("sha256")

        result: dict[str, Any] = {
            "label": label,
            "path": dest_path_raw,
            "exists": False,
            "allowed": False,
            "expected_sha256": compare_sha256,
            "actual_sha256": None,
            "expected_size_bytes": None,
            "actual_size_bytes": None,
            "hash_status": "not_applicable",
            "size_status": "not_checked",
        }

        if not dest_path_raw:
            results.append(result)
            continue

        status, resolved = _classify_evidence_path(dest_path_raw)
        if status == "unsafe":
            result["hash_status"] = "unavailable"
            issues.append(
                {
                    "issue_type": "disallowed_copied_evidence_path",
                    "message": f"copied evidence path is unsafe: {dest_path_raw}",
                    "path": dest_path_raw,
                    "label": label,
                }
            )
            results.append(result)
            continue

        if not any(resolved == d or d in resolved.parents for d in allowed_dirs):
            result["exists"] = status == "safe_exists"
            result["hash_status"] = "unavailable"
            issues.append(
                {
                    "issue_type": "disallowed_copied_evidence_path",
                    "message": f"copied evidence path outside allowed evidence directory: {dest_path_raw}",
                    "path": dest_path_raw,
                    "label": label,
                }
            )
            results.append(result)
            continue

        if status == "safe_missing":
            result["allowed"] = True
            result["hash_status"] = "missing_file"
            issues.append(
                {
                    "issue_type": "missing_copied_evidence_file",
                    "message": f"copied evidence file is missing: {dest_path_raw}",
                    "path": dest_path_raw,
                    "label": label,
                }
            )
            results.append(result)
            continue

        data = resolved.read_bytes()
        actual_sha256 = _sha256_hex(data)
        result["exists"] = True
        result["allowed"] = True
        result["actual_sha256"] = actual_sha256
        result["actual_size_bytes"] = len(data)

        if compare_sha256 is not None:
            if actual_sha256 == compare_sha256:
                result["hash_status"] = "match"
            else:
                result["hash_status"] = "mismatch"
                issues.append(
                    {
                        "issue_type": "copied_evidence_hash_mismatch",
                        "message": f"copied evidence hash mismatch: {label}",
                        "path": dest_path_raw,
                        "label": label,
                    }
                )
        else:
            result["hash_status"] = "not_checked"

        results.append(result)

    return results


def _build_bundle_descriptor(manifest: dict[str, Any]) -> dict[str, Any]:
    reduced_evidence = []
    source_evidence = manifest.get("source_evidence")
    if isinstance(source_evidence, list):
        for entry in source_evidence:
            if not isinstance(entry, dict):
                continue
            reduced_evidence.append(
                {
                    "label": entry.get("label"),
                    "path": entry.get("path"),
                    "sha256": entry.get("sha256"),
                    "size_bytes": entry.get("size_bytes"),
                }
            )
    reduced_evidence.sort(key=lambda e: e.get("label") or "")

    reduced_copied = []
    copied_files = manifest.get("copied_files")
    if isinstance(copied_files, list):
        for entry in copied_files:
            if not isinstance(entry, dict):
                continue
            reduced_copied.append({"path": entry.get("dest_path"), "sha256": entry.get("sha256")})
    reduced_copied.sort(key=lambda e: e.get("path") or "")

    return {
        "source_evidence": reduced_evidence,
        "copied_files": reduced_copied,
        "record_count": manifest.get("record_count"),
        "verification_status": manifest.get("verification_status"),
        "query_status": manifest.get("query_status"),
        "phase8e_status": manifest.get("phase8e_status"),
        "durable_audit_store_status": manifest.get("durable_audit_store_status"),
    }


def _safety_statement() -> str:
    return (
        "Phase 8G verification is a local hash-only prototype, read-only "
        "against the export pack and all source evidence. It implements no "
        "signing, generates no keys, handles no private key material, and "
        "implements no encryption. It executes no primitive, calls no "
        "Phase 7D wrapper, calls no Phase 8B/8C/8D/8E script, performs no "
        "vault read/write, and makes no network, backend, API, or database "
        "call. A verified or hash-valid export is not approval."
    )


def _limitations() -> list[str]:
    return [
        "local tmp verifier only",
        "hash-only",
        "no signature verification",
        "no signing",
        "no key management",
        "no encryption",
        "no backend/API",
        "no authenticated identity",
        "no production deployment",
        "no automatic remediation",
    ]


def _empty_report(manifest_path_ref: str, report_dir: Path) -> dict[str, Any]:
    return {
        "phase8g_status": PHASE8G_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "verification_status": "empty",
        "hash_only_verification": True,
        "manifest_path": manifest_path_ref,
        "report_dir": _rel(report_dir),
        "evidence_count": 0,
        "copied_evidence_count": 0,
        "issue_count": 0,
        "manifest_hash_status": "not_present",
        "bundle_hash_status": "computed_only",
        "computed_manifest_hash": None,
        "manifest_manifest_hash": None,
        "computed_bundle_hash": None,
        "manifest_bundle_hash": None,
        "evidence_results": [],
        "copied_evidence_results": [],
        "issues": [],
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _invalid_report(manifest_path_ref: str, report_dir: Path, category: str, message: str) -> dict[str, Any]:
    return {
        "phase8g_status": PHASE8G_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "verification_status": "invalid",
        "hash_only_verification": True,
        "manifest_path": manifest_path_ref,
        "report_dir": _rel(report_dir),
        "evidence_count": 0,
        "copied_evidence_count": 0,
        "issue_count": 1,
        "manifest_hash_status": "not_present",
        "bundle_hash_status": "computed_only",
        "computed_manifest_hash": None,
        "manifest_manifest_hash": None,
        "computed_bundle_hash": None,
        "manifest_bundle_hash": None,
        "evidence_results": [],
        "copied_evidence_results": [],
        "issues": [{"issue_type": category, "message": message, "path": manifest_path_ref, "label": None}],
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _build_report(
    *,
    manifest_path_ref: str,
    report_dir: Path,
    evidence_results: list[dict[str, Any]],
    copied_evidence_results: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    manifest_hash_status: str,
    bundle_hash_status: str,
    computed_manifest_hash: str,
    manifest_manifest_hash: str | None,
    computed_bundle_hash: str,
    manifest_bundle_hash: str | None,
) -> dict[str, Any]:
    issue_count = len(issues)
    verification_status = "valid" if issue_count == 0 else "warning"
    return {
        "phase8g_status": PHASE8G_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "verification_status": verification_status,
        "hash_only_verification": True,
        "manifest_path": manifest_path_ref,
        "report_dir": _rel(report_dir),
        "evidence_count": len(evidence_results),
        "copied_evidence_count": len(copied_evidence_results),
        "issue_count": issue_count,
        "manifest_hash_status": manifest_hash_status,
        "bundle_hash_status": bundle_hash_status,
        "computed_manifest_hash": computed_manifest_hash,
        "manifest_manifest_hash": manifest_manifest_hash,
        "computed_bundle_hash": computed_bundle_hash,
        "manifest_bundle_hash": manifest_bundle_hash,
        "evidence_results": evidence_results,
        "copied_evidence_results": copied_evidence_results,
        "issues": issues,
        "safety_statement": _safety_statement(),
        "limitations": _limitations(),
    }


def _render_evidence_table(title: str, rows: list[dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.append("- none")
        lines.append("")
        return lines
    lines.append("| label | path | exists | hash_status | size_status |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(f"| {row['label']} | {row['path']} | {row['exists']} | {row['hash_status']} | {row['size_status']} |")
    lines.append("")
    return lines


def _render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 8G Export Integrity Verification",
        "",
        f"phase8g_status: {report['phase8g_status']}",
        f"durable_audit_store_status: {report['durable_audit_store_status']}",
        f"phase7d_runtime_readiness: {report['phase7d_runtime_readiness']}",
        f"signing_implementation_status: {report['signing_implementation_status']}",
        "",
        "This is a local hash-only verification. No signature is checked or "
        "produced in this phase.",
        "",
        f"- verification status: {report['verification_status']}",
        f"- manifest path: {report['manifest_path']}",
        f"- evidence count: {report['evidence_count']}",
        f"- copied evidence count: {report['copied_evidence_count']}",
        f"- issue count: {report['issue_count']}",
        f"- manifest hash status: {report['manifest_hash_status']}",
        f"- bundle hash status: {report['bundle_hash_status']}",
        "",
    ]
    lines += _render_evidence_table("Evidence results", report["evidence_results"])
    lines += _render_evidence_table("Copied evidence results", report["copied_evidence_results"])

    lines.append("## Issues")
    lines.append("")
    if report["issues"]:
        lines.append("| type | label | path | message |")
        lines.append("| --- | --- | --- | --- |")
        for issue in report["issues"]:
            lines.append(f"| {issue.get('issue_type')} | {issue.get('label')} | {issue.get('path')} | {issue.get('message')} |")
    else:
        lines.append("No issues")
    lines.append("")

    lines += [
        "## Safety statement",
        "",
        report["safety_statement"],
        "",
        "Verified export is not approval. A hash-valid export result does not "
        "authorize, trigger, or imply approval of any Phase 7D gate.",
        "",
        "## Known limitations",
        "",
    ]
    lines += [f"- {item}" for item in report["limitations"]]
    lines.append("")
    return "\n".join(lines)


def _write_report(report_dir: Path, report: dict[str, Any]) -> None:
    json_path = report_dir / "export-integrity-verification.json"
    md_path = report_dir / "export-integrity-verification.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_md(report), encoding="utf-8")


def run(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    """Return (report, ok) where ok is False only on a critical path/manifest failure."""
    report_dir = _validate_report_dir(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        manifest_file = _validate_manifest_path(args.manifest_path)
    except IntegrityPathError as exc:
        report = _invalid_report(args.manifest_path, report_dir, exc.category, str(exc))
        _write_report(report_dir, report)
        return report, False

    if manifest_file is None:
        report = _empty_report(args.manifest_path, report_dir)
        _write_report(report_dir, report)
        return report, True

    manifest_path_ref = _rel(manifest_file)
    raw_text = manifest_file.read_text(encoding="utf-8")
    try:
        manifest = json.loads(raw_text)
    except json.JSONDecodeError:
        report = _invalid_report(manifest_path_ref, report_dir, "invalid_json", "manifest is not valid JSON")
        _write_report(report_dir, report)
        return report, False
    if not isinstance(manifest, dict):
        report = _invalid_report(manifest_path_ref, report_dir, "invalid_json", "manifest is not a JSON object")
        _write_report(report_dir, report)
        return report, False

    issues: list[dict[str, Any]] = []
    evidence_results = _verify_source_evidence(manifest, issues)
    copied_evidence_results = _verify_copied_evidence(manifest, issues)

    manifest_manifest_hash = manifest.get("manifest_hash")
    stripped_manifest = {k: v for k, v in manifest.items() if k != "manifest_hash"}
    computed_manifest_hash = _sha256_hex(_canonical_json(stripped_manifest).encode("utf-8"))
    if manifest_manifest_hash:
        manifest_hash_status = "match" if computed_manifest_hash == manifest_manifest_hash else "mismatch"
        if manifest_hash_status == "mismatch":
            issues.append(
                {"issue_type": "manifest_hash_mismatch", "message": "manifest_hash does not match recomputed value", "path": None, "label": None}
            )
    else:
        manifest_hash_status = "not_present"

    bundle_descriptor = _build_bundle_descriptor(manifest)
    computed_bundle_hash = _sha256_hex(_canonical_json(bundle_descriptor).encode("utf-8"))
    manifest_bundle_hash = manifest.get("bundle_hash")
    if manifest_bundle_hash:
        bundle_hash_status = "match" if computed_bundle_hash == manifest_bundle_hash else "mismatch"
        if bundle_hash_status == "mismatch":
            issues.append(
                {"issue_type": "bundle_hash_mismatch", "message": "bundle_hash does not match recomputed value", "path": None, "label": None}
            )
    else:
        bundle_hash_status = "computed_only"

    report = _build_report(
        manifest_path_ref=manifest_path_ref,
        report_dir=report_dir,
        evidence_results=evidence_results,
        copied_evidence_results=copied_evidence_results,
        issues=issues,
        manifest_hash_status=manifest_hash_status,
        bundle_hash_status=bundle_hash_status,
        computed_manifest_hash=computed_manifest_hash,
        manifest_manifest_hash=manifest_manifest_hash,
        computed_bundle_hash=computed_bundle_hash,
        manifest_bundle_hash=manifest_bundle_hash,
    )
    _write_report(report_dir, report)
    return report, True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8G local hash-only export integrity verifier over Phase 8E manifests."
    )
    parser.add_argument("--manifest-path", default=DEFAULT_MANIFEST_PATH, dest="manifest_path")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR, dest="report_dir")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report, ok = run(args)
    except IntegrityPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"verification_status: {report['verification_status']}")
    print(f"evidence_count: {report['evidence_count']}")
    print(f"issue_count: {report['issue_count']}")
    print(f"manifest_hash_status: {report['manifest_hash_status']}")
    print(f"bundle_hash_status: {report['bundle_hash_status']}")
    print(f"phase8g_status: {report['phase8g_status']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
