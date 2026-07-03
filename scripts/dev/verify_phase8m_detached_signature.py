#!/usr/bin/env python3
"""Phase 8M local detached signature verifier prototype for Phase 8L outputs.

Local-only, prototype-only. Reads a Phase 8L signed payload descriptor and
detached signature envelope (and optionally the Phase 8L summary), recomputes
``signed_payload_sha256`` from the canonical descriptor JSON, compares it to the
envelope value, validates basic descriptor/envelope schema, and — only when the
in-memory prototype key ``AFFILIATE_PHASE8L_PROTOTYPE_KEY`` is set — verifies the
HMAC-SHA256 prototype signature. All outputs are written only under
``tmp/phase8m-detached-signature-verifier/``.

This tool never signs anything, never generates or persists keys, never calls
the Phase 7D wrapper or an approval primitive, never calls the Phase 8B/8C/8D/
8E/8G/8L scripts, never reads or writes the vault, and never performs any
network/database/backend behavior. Python standard library only.

A verified prototype signature is evidence only. It is NOT approval. Approval
remains the Phase 7D selected-gate manual boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DESCRIPTOR_PATH = "tmp/phase8l-detached-signature/signed-payload-descriptor.json"
DEFAULT_ENVELOPE_PATH = "tmp/phase8l-detached-signature/detached-signature-envelope.json"
DEFAULT_SUMMARY_PATH = "tmp/phase8l-detached-signature/detached-signature-summary.json"
DEFAULT_OUTPUT_DIR = "tmp/phase8m-detached-signature-verifier"
GUARDED_OUTPUT_ROOT = (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PROTOTYPE_KEY_ENV = "AFFILIATE_PHASE8L_PROTOTYPE_KEY"

EXPECTED_SIGNATURE_ALGORITHM = "hmac-sha256-prototype"
EXPECTED_SIGNATURE_ENCODING = "hex"

PHASE8M_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "detached_signature_verifier_prototype"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"
SIGNING_IMPLEMENTATION_STATUS = "prototype_local_only"
SIGNATURE_RUNTIME_STATUS = "local_prototype"
SIGNATURE_VERIFIER_RUNTIME_STATUS = "local_prototype"
KEY_MANAGEMENT_RUNTIME_STATUS = "not_implemented"
MAJOR_PHASE_BRANCH_WORKFLOW = "enabled"

DESCRIPTOR_REQUIRED_FIELDS = (
    "payload_schema_version",
    "export_manifest_path",
    "export_manifest_sha256",
    "bundle_hash",
    "computed_manifest_hash",
    "report_schema_version",
    "issue_taxonomy_version",
    "compatibility_matrix_version",
    "verifier_hardening_status",
    "verification_status",
    "compatibility_result",
    "incident_classification",
    "reviewer_action",
    "reviewer_action_required",
    "generated_from_phase",
    "generated_by_tool",
    "created_at_utc",
    "signing_policy_version",
    "signer_id",
    "signer_role",
    "signer_identity_assurance",
    "key_id",
    "key_version",
    "approval_boundary_statement",
)

ENVELOPE_REQUIRED_FIELDS = (
    "signature_schema_version",
    "signed_payload_sha256",
    "signed_payload_descriptor_path",
    "detached_signature_path",
    "signature_algorithm",
    "signature_encoding",
    "key_id",
    "key_version",
    "signer_id",
    "signer_role",
    "signer_identity_assurance",
    "signing_policy_version",
    "signing_timestamp_utc",
    "signature_status",
    "signing_status",
    "verification_status",
    "revocation_status",
    "rotation_epoch",
    "approval_boundary_statement",
    "signature_runtime_status",
    "signing_implementation_status",
)

APPROVAL_BOUNDARY_STATEMENT = (
    "This verification result and its metadata are evidence only; they are not "
    "approval. A verified signature does not approve anything, does not set "
    "approval flags, does not call the Phase 7D wrapper or any primitive, and "
    "does not trigger the next gate. Approval remains the Phase 7D "
    "selected-gate manual boundary."
)

SAFETY_STATEMENT = (
    "Verified signature is not approval. Verification passed is not approval. "
    "Signature verifier result is not approval. Signature verification does not "
    "execute a primitive, does not call the wrapper, does not trigger the next "
    "gate, does not set approval flags, and does not write the vault. Outputs "
    "are written only under tmp/phase8m-detached-signature-verifier/."
)

LIMITATIONS = [
    "local prototype only",
    "hmac-sha256 prototype verification only, not a production signature verifier",
    "no production signing",
    "no key management runtime",
    "no governed key custody",
    "no encryption",
    "no authenticated operator identity",
    "no non-repudiation",
    "no backend/API/database",
    "no production deployment",
]


class Phase8MPathError(Exception):
    """Raised when a caller-provided path is unsafe or unusable."""

    def __init__(self, message: str, category: str) -> None:
        super().__init__(message)
        self.category = category


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_input_path(raw: str, label: str) -> Path | None:
    """Return the resolved input path, or None if it is safely absent."""
    if not raw:
        raise Phase8MPathError(f"{label} path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise Phase8MPathError(f"{label} path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise Phase8MPathError(f"symlinked {label} paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise Phase8MPathError(f"{label} path must resolve inside the repository", "outside_repo") from None

    if rel.parts and rel.parts[0] in REJECTED_ROOTS:
        raise Phase8MPathError(f"{label} path must not resolve under {rel.parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise Phase8MPathError(f"{label} path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_output_dir(raw: str) -> Path:
    if not raw:
        raise Phase8MPathError("output-dir is empty", "output_dir_rejected")
    if ".." in Path(raw).parts:
        raise Phase8MPathError("output-dir path traversal is not allowed", "output_dir_rejected")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    if candidate.is_symlink():
        raise Phase8MPathError("symlinked output-dir is not allowed", "output_dir_rejected")
    resolved = candidate.resolve()
    if resolved != GUARDED_OUTPUT_ROOT and GUARDED_OUTPUT_ROOT not in resolved.parents:
        raise Phase8MPathError(
            f"output-dir must resolve under {DEFAULT_OUTPUT_DIR}", "output_dir_rejected"
        )
    return resolved


def _new_issue(issue_type: str, severity: str, incident_classification: str, reviewer_action: str, message: str) -> dict[str, Any]:
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident_classification,
        "reviewer_action": reviewer_action,
        "message": message,
    }


def _severity_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"info": 0, "warning": 0, "critical": 0}
    for issue in issues:
        sev = issue.get("severity")
        if sev in counts:
            counts[sev] += 1
    return counts


def _load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Return (obj, error_category). error_category is set only on failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "invalid_json"
    if not isinstance(data, dict):
        return None, "not_object"
    return data, None


def _build_report(
    *,
    signature_verification_status: str,
    signature_status: str,
    verification_status: str,
    incident_classification: str,
    reviewer_action: str,
    signed_payload_hash_status: str,
    computed_signed_payload_sha256: str | None,
    descriptor: dict[str, Any] | None,
    envelope: dict[str, Any] | None,
    descriptor_path_ref: str,
    envelope_path_ref: str,
    summary_path_ref: str | None,
    output_dir: Path,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    envelope = envelope or {}
    failure_count = sum(1 for issue in issues if issue.get("severity") == "critical")
    return {
        "phase8m_status": PHASE8M_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "signature_runtime_status": SIGNATURE_RUNTIME_STATUS,
        "signature_verifier_runtime_status": SIGNATURE_VERIFIER_RUNTIME_STATUS,
        "key_management_runtime_status": KEY_MANAGEMENT_RUNTIME_STATUS,
        "major_phase_branch_workflow": MAJOR_PHASE_BRANCH_WORKFLOW,
        "signature_verification_status": signature_verification_status,
        "signature_status": signature_status,
        "verification_status": verification_status,
        "signature_schema_version": envelope.get("signature_schema_version"),
        "signed_payload_sha256": envelope.get("signed_payload_sha256"),
        "computed_signed_payload_sha256": computed_signed_payload_sha256,
        "signed_payload_hash_status": signed_payload_hash_status,
        "signature_algorithm": envelope.get("signature_algorithm"),
        "signature_encoding": envelope.get("signature_encoding"),
        "key_id": envelope.get("key_id"),
        "key_version": envelope.get("key_version"),
        "key_status": "unknown",
        "revocation_status": envelope.get("revocation_status", "not_checked"),
        "rotation_status": envelope.get("rotation_epoch", "unknown"),
        "signer_id": envelope.get("signer_id"),
        "signer_role": envelope.get("signer_role"),
        "signer_identity_assurance": envelope.get("signer_identity_assurance"),
        "failure_count": failure_count,
        "severity_counts": _severity_counts(issues),
        "incident_classification": incident_classification,
        "reviewer_action": reviewer_action,
        "reviewer_action_required": reviewer_action != "no_action_required",
        "descriptor_path": descriptor_path_ref,
        "envelope_path": envelope_path_ref,
        "summary_path": summary_path_ref,
        "output_dir": _rel(output_dir),
        "issues": issues,
        "safety_statement": SAFETY_STATEMENT,
        "approval_boundary_statement": APPROVAL_BOUNDARY_STATEMENT,
        "limitations": LIMITATIONS,
    }


def _render_report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 8M — Detached Signature Verifier Prototype Report",
        "",
        "```text",
        f"phase8m_status: {report['phase8m_status']}",
        f"signature_verification_status: {report['signature_verification_status']}",
        f"verification_status: {report['verification_status']}",
        f"signature_status: {report['signature_status']}",
        f"signed_payload_hash_status: {report['signed_payload_hash_status']}",
        "```",
        "",
        "## Signer metadata",
        "",
        f"- signer_id: {report['signer_id']}",
        f"- signer_role: {report['signer_role']}",
        f"- signer_identity_assurance: {report['signer_identity_assurance']}",
        "",
        "## Key metadata",
        "",
        f"- key_id: {report['key_id']}",
        f"- key_version: {report['key_version']}",
        f"- key_status: {report['key_status']}",
        f"- revocation_status: {report['revocation_status']}",
        f"- rotation_status: {report['rotation_status']}",
        "",
        "## Issue summary",
        "",
        f"- failure_count: {report['failure_count']}",
        f"- severity_counts: {report['severity_counts']}",
        f"- incident_classification: {report['incident_classification']}",
        f"- reviewer_action: {report['reviewer_action']}",
    ]
    if report["issues"]:
        lines.append("")
        for issue in report["issues"]:
            lines.append(
                f"- [{issue['severity']}] {issue['issue_type']}: {issue['message']} "
                f"(reviewer_action: {issue['reviewer_action']})"
            )
    lines.extend(
        [
            "",
            "## Output paths",
            "",
            f"- descriptor_path: {report['descriptor_path']}",
            f"- envelope_path: {report['envelope_path']}",
            f"- summary_path: {report['summary_path']}",
            f"- output_dir: {report['output_dir']}",
            "",
            "## Safety boundary",
            "",
            "- verified signature is not approval",
            "- verification passed is not approval",
            "- signature verifier result is not approval",
            "- valid verification_status is not approval",
            "- signature verification does not call the wrapper or primitives",
            "- signature verification does not trigger the next gate",
            "- signature verification does not set approval flags",
            "- signature verification does not write the vault",
            "- reviewer action remains review guidance only",
            "",
            f"{report['safety_statement']}",
            "",
            f"{report['approval_boundary_statement']}",
            "",
            "## Known limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def _write_report(output_dir: Path, report: dict[str, Any]) -> None:
    (output_dir / "detached-signature-verification.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "detached-signature-verification.md").write_text(
        _render_report_md(report), encoding="utf-8"
    )


def run(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    """Return (report, ok). ok is False on any failure/invalid outcome."""
    output_dir = _validate_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Validate descriptor + envelope paths (missing is allowed) ────────────
    descriptor_file = _validate_input_path(args.descriptor_path, "descriptor")
    envelope_file = _validate_input_path(args.envelope_path, "envelope")

    # ── Missing descriptor or envelope: not-ready, exit 0 ────────────────────
    if descriptor_file is None or envelope_file is None:
        report = _build_report(
            signature_verification_status="skipped_missing_signature_inputs",
            signature_status="not_present",
            verification_status="empty",
            incident_classification="signature_not_available",
            reviewer_action="no_action_required",
            signed_payload_hash_status="not_checked",
            computed_signed_payload_sha256=None,
            descriptor=None,
            envelope=None,
            descriptor_path_ref=args.descriptor_path,
            envelope_path_ref=args.envelope_path,
            summary_path_ref=args.summary_path,
            output_dir=output_dir,
            issues=[
                _new_issue(
                    "missing_signature_inputs",
                    "info",
                    "signature_not_available",
                    "no_action_required",
                    "descriptor and/or envelope not present; nothing to verify yet",
                )
            ],
        )
        _write_report(output_dir, report)
        return report, True

    descriptor_ref = _rel(descriptor_file)
    envelope_ref = _rel(envelope_file)

    # ── Load descriptor + envelope as JSON objects ───────────────────────────
    descriptor, derr = _load_json_object(descriptor_file)
    envelope, eerr = _load_json_object(envelope_file)
    if derr or eerr:
        issues = []
        if derr:
            issues.append(_new_issue("invalid_descriptor", "critical", "signature_integrity_failure", "reject_signature_until_resolved", f"descriptor is {derr}"))
        if eerr:
            issues.append(_new_issue("invalid_envelope", "critical", "signature_integrity_failure", "reject_signature_until_resolved", f"envelope is {eerr}"))
        report = _build_report(
            signature_verification_status="failed_invalid_input",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="signature_integrity_failure",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="not_checked",
            computed_signed_payload_sha256=None,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=args.summary_path,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False

    issues: list[dict[str, Any]] = []

    # ── Optional summary (warning issue if missing/invalid; never fatal) ─────
    summary_ref: str | None = None
    try:
        summary_file = _validate_input_path(args.summary_path, "summary")
    except Phase8MPathError as exc:
        summary_file = None
        issues.append(_new_issue("summary_path_unsafe", "warning", "policy_review_required", "manual_review_required", f"summary path rejected: {exc}"))
    if summary_file is None:
        summary_ref = args.summary_path
        issues.append(_new_issue("summary_missing", "warning", "none", "manual_review_required", "Phase 8L summary not present (optional)"))
    else:
        summary_ref = _rel(summary_file)
        _summary_obj, serr = _load_json_object(summary_file)
        if serr:
            issues.append(_new_issue("summary_invalid", "warning", "none", "manual_review_required", f"summary is {serr} (optional)"))

    # ── Schema validation ────────────────────────────────────────────────────
    missing_descriptor = [f for f in DESCRIPTOR_REQUIRED_FIELDS if f not in descriptor]
    missing_envelope = [f for f in ENVELOPE_REQUIRED_FIELDS if f not in envelope]
    for field in missing_descriptor:
        issues.append(_new_issue("missing_descriptor_field", "critical", "policy_review_required", "reject_signature_until_resolved", f"descriptor missing required field: {field}"))
    for field in missing_envelope:
        issues.append(_new_issue("missing_envelope_field", "critical", "policy_review_required", "reject_signature_until_resolved", f"envelope missing required field: {field}"))
    if missing_descriptor or missing_envelope:
        report = _build_report(
            signature_verification_status="failed_schema_validation",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="policy_review_required",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="not_checked",
            computed_signed_payload_sha256=None,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False

    # ── Signed payload hash verification ─────────────────────────────────────
    computed_hash = _sha256_hex(_canonical_json(descriptor).encode("utf-8"))
    envelope_hash = envelope.get("signed_payload_sha256")
    if computed_hash != envelope_hash:
        issues.append(_new_issue("signed_payload_hash_mismatch", "critical", "signature_integrity_failure", "reject_signature_until_resolved", "recomputed signed_payload_sha256 does not match envelope value"))
        report = _build_report(
            signature_verification_status="failed_signed_payload_hash_mismatch",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="signature_integrity_failure",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="mismatch",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False

    # ── Prototype HMAC verification ──────────────────────────────────────────
    algorithm = envelope.get("signature_algorithm")
    encoding = envelope.get("signature_encoding")
    if algorithm != EXPECTED_SIGNATURE_ALGORITHM:
        issues.append(_new_issue("unsupported_algorithm", "critical", "policy_review_required", "reject_signature_until_resolved", f"unsupported signature_algorithm: {algorithm}"))
        report = _build_report(
            signature_verification_status="failed_unsupported_algorithm",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="policy_review_required",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False
    if encoding != EXPECTED_SIGNATURE_ENCODING:
        issues.append(_new_issue("unsupported_encoding", "critical", "policy_review_required", "reject_signature_until_resolved", f"unsupported signature_encoding: {encoding}"))
        report = _build_report(
            signature_verification_status="failed_unsupported_encoding",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="policy_review_required",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False

    envelope_signature_status = envelope.get("signature_status")
    envelope_signing_status = envelope.get("signing_status")
    detached_signature_value = envelope.get("detached_signature_value")

    # Signature not ready (Phase 8L skipped signing because its key was absent).
    if envelope_signature_status == "not_ready" or envelope_signing_status == "skipped_missing_prototype_key":
        issues.append(_new_issue("signature_not_ready", "warning", "signature_not_available", "manual_review_required", "envelope signature is not ready (Phase 8L skipped signing)"))
        report = _build_report(
            signature_verification_status="skipped_signature_not_ready",
            signature_status="not_ready",
            verification_status="warning",
            incident_classification="signature_not_available",
            reviewer_action="manual_review_required",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, True

    # Signature not present at all.
    if envelope_signature_status == "not_present":
        issues.append(_new_issue("signature_not_present", "info", "signature_not_available", "manual_review_required", "envelope reports no signature present"))
        report = _build_report(
            signature_verification_status="skipped_signature_not_present",
            signature_status="not_present",
            verification_status="empty",
            incident_classification="signature_not_available",
            reviewer_action="manual_review_required",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, True

    # Prototype key not provided: cannot verify cryptographically.
    raw_key = os.environ.get(PROTOTYPE_KEY_ENV)
    if not raw_key:
        issues.append(_new_issue("prototype_key_missing", "warning", "signature_not_available", "manual_review_required", "prototype key env var not provided; HMAC not verified"))
        report = _build_report(
            signature_verification_status="skipped_missing_prototype_key",
            signature_status="present",
            verification_status="warning",
            incident_classification="signature_not_available",
            reviewer_action="manual_review_required",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, True

    # Prototype key present but no signature value to verify.
    if not detached_signature_value:
        issues.append(_new_issue("missing_signature_value", "critical", "signature_integrity_failure", "reject_signature_until_resolved", "envelope signature_status present but detached_signature_value is missing"))
        report = _build_report(
            signature_verification_status="failed_missing_signature_value",
            signature_status="verification_failed",
            verification_status="invalid",
            incident_classification="signature_integrity_failure",
            reviewer_action="reject_signature_until_resolved",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, False

    expected_signature = hmac.new(
        raw_key.encode("utf-8"),
        str(envelope_hash).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if hmac.compare_digest(expected_signature, str(detached_signature_value)):
        report = _build_report(
            signature_verification_status="verified_local_prototype",
            signature_status="verification_passed",
            verification_status="valid",
            incident_classification="none",
            reviewer_action="no_action_required",
            signed_payload_hash_status="match",
            computed_signed_payload_sha256=computed_hash,
            descriptor=descriptor,
            envelope=envelope,
            descriptor_path_ref=descriptor_ref,
            envelope_path_ref=envelope_ref,
            summary_path_ref=summary_ref,
            output_dir=output_dir,
            issues=issues,
        )
        _write_report(output_dir, report)
        return report, True

    issues.append(_new_issue("signature_mismatch", "critical", "signature_integrity_failure", "reject_signature_until_resolved", "prototype HMAC signature does not match"))
    report = _build_report(
        signature_verification_status="failed_signature_mismatch",
        signature_status="verification_failed",
        verification_status="invalid",
        incident_classification="signature_integrity_failure",
        reviewer_action="reject_signature_until_resolved",
        signed_payload_hash_status="match",
        computed_signed_payload_sha256=computed_hash,
        descriptor=descriptor,
        envelope=envelope,
        descriptor_path_ref=descriptor_ref,
        envelope_path_ref=envelope_ref,
        summary_path_ref=summary_ref,
        output_dir=output_dir,
        issues=issues,
    )
    _write_report(output_dir, report)
    return report, False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8M local-only detached signature verifier prototype over Phase 8L outputs."
    )
    parser.add_argument("--descriptor-path", default=DEFAULT_DESCRIPTOR_PATH, dest="descriptor_path")
    parser.add_argument("--envelope-path", default=DEFAULT_ENVELOPE_PATH, dest="envelope_path")
    parser.add_argument("--summary-path", default=DEFAULT_SUMMARY_PATH, dest="summary_path")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, dest="output_dir")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report, ok = run(args)
    except Phase8MPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"phase8m_status: {report['phase8m_status']}")
    print(f"signature_verification_status: {report['signature_verification_status']}")
    print(f"verification_status: {report['verification_status']}")
    print(f"signature_status: {report['signature_status']}")
    print(f"signed_payload_hash_status: {report['signed_payload_hash_status']}")
    print(f"reviewer_action: {report['reviewer_action']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
