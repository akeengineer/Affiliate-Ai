#!/usr/bin/env python3
"""Phase 8L local detached signature prototype for Phase 8E export packs.

Local-only, prototype-only. Reads a Phase 8E export manifest (and optionally a
Phase 8G/8H integrity verification report), builds a canonical signed payload
descriptor, computes ``signed_payload_sha256``, and — only when the in-memory
prototype key ``AFFILIATE_PHASE8L_PROTOTYPE_KEY`` is set — produces a local
HMAC-SHA256 prototype detached signature. All outputs are written only under
``tmp/phase8l-detached-signature/``.

This tool never signs with real key material, never generates or persists keys,
never calls the Phase 7D wrapper or an approval primitive, never calls the
Phase 8B/8C/8D/8E/8G scripts, never reads or writes the vault, and never
performs any network/database/backend behavior. Python standard library only.

A prototype signature is evidence only. It is NOT approval. Approval remains the
Phase 7D selected-gate manual boundary.
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

DEFAULT_MANIFEST_PATH = "tmp/phase8e-audit-export/audit-export-manifest.json"
DEFAULT_INTEGRITY_REPORT_PATH = "tmp/phase8g-export-integrity/export-integrity-verification.json"
DEFAULT_OUTPUT_DIR = "tmp/phase8l-detached-signature"
GUARDED_OUTPUT_ROOT = (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()

REJECTED_ROOTS = ("vault", "docs", "scripts", "tests", "codex")

PROTOTYPE_KEY_ENV = "AFFILIATE_PHASE8L_PROTOTYPE_KEY"

PHASE8L_STATUS = "success"
DURABLE_AUDIT_STORE_STATUS = "local_detached_signature_prototype"
PHASE7D_RUNTIME_READINESS = "implemented_manual_gate"
SIGNING_IMPLEMENTATION_STATUS = "prototype_local_only"
SIGNATURE_RUNTIME_STATUS = "local_prototype"
SIGNATURE_VERIFIER_RUNTIME_STATUS = "not_implemented"
KEY_MANAGEMENT_RUNTIME_STATUS = "not_implemented"
MAJOR_PHASE_BRANCH_WORKFLOW = "enabled"

PROTOTYPE_SIGNATURE_ALGORITHM = "hmac-sha256-prototype"
PAYLOAD_SCHEMA_VERSION = "phase8l.signed_payload_descriptor.v1"
ENVELOPE_SCHEMA_VERSION = "phase8l.detached_signature_envelope.v1"

DEFAULT_SIGNER_ID = "operator_declared"
DEFAULT_SIGNER_ROLE = "operator"
DEFAULT_SIGNER_IDENTITY_ASSURANCE = "operator_declared"
DEFAULT_KEY_ID = "phase8l-prototype-key"
DEFAULT_KEY_VERSION = "prototype-v1"
DEFAULT_SIGNING_POLICY_VERSION = "phase8l.prototype.signing_policy.v1"

ALLOWED_IDENTITY_ASSURANCE = (
    "unauthenticated",
    "operator_declared",
    "local_registry_verified",
    "enterprise_identity_verified",
    "hardware_backed",
)

APPROVAL_BOUNDARY_STATEMENT = (
    "This detached signature and its metadata are evidence only; they are not "
    "approval. A prototype signature does not approve anything, does not set "
    "approval flags, does not call the Phase 7D wrapper or any primitive, and "
    "does not trigger the next gate. Approval remains the Phase 7D "
    "selected-gate manual boundary."
)

SAFETY_STATEMENT = (
    "Signature is not approval. Signed export is not approval. Local prototype "
    "signature is not approval. Signature generation does not execute a "
    "primitive, does not call the wrapper, does not trigger the next gate, does "
    "not set approval flags, and does not write the vault. Outputs are written "
    "only under tmp/phase8l-detached-signature/."
)

LIMITATIONS = [
    "local prototype only",
    "hmac-sha256 prototype signature only, not production signing",
    "no signature verifier runtime",
    "no key management runtime",
    "no governed key custody",
    "no encryption",
    "no authenticated operator identity",
    "no non-repudiation",
    "no backend/API/database",
    "no production deployment",
]


class Phase8LPathError(Exception):
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
    """Return the resolved input path, or None if it is safely absent.

    Rejects empty paths, path traversal, symlinks, paths that resolve outside
    the repository, paths under a rejected source root (vault/docs/scripts/
    tests/codex), and existing non-file paths.
    """
    if not raw:
        raise Phase8LPathError(f"{label} path is empty", "empty_path")
    if ".." in Path(raw).parts:
        raise Phase8LPathError(f"{label} path traversal is not allowed", "path_traversal")

    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_symlink():
        raise Phase8LPathError(f"symlinked {label} paths are not allowed", "symlink_rejected")

    repo_root_resolved = REPO_ROOT.resolve()
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(repo_root_resolved)
    except ValueError:
        raise Phase8LPathError(f"{label} path must resolve inside the repository", "outside_repo") from None

    if rel.parts and rel.parts[0] in REJECTED_ROOTS:
        raise Phase8LPathError(f"{label} path must not resolve under {rel.parts[0]}/", "rejected_source_root")

    if not resolved.exists():
        return None
    if not resolved.is_file():
        raise Phase8LPathError(f"{label} path is not a file: {raw}", "not_a_file")
    return resolved


def _validate_output_dir(raw: str) -> Path:
    if not raw:
        raise Phase8LPathError("output-dir is empty", "output_dir_rejected")
    if ".." in Path(raw).parts:
        raise Phase8LPathError("output-dir path traversal is not allowed", "output_dir_rejected")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    if candidate.is_symlink():
        raise Phase8LPathError("symlinked output-dir is not allowed", "output_dir_rejected")
    resolved = candidate.resolve()
    if resolved != GUARDED_OUTPUT_ROOT and GUARDED_OUTPUT_ROOT not in resolved.parents:
        raise Phase8LPathError(
            f"output-dir must resolve under {DEFAULT_OUTPUT_DIR}", "output_dir_rejected"
        )
    return resolved


def _validate_identity_assurance(value: str) -> str:
    if value not in ALLOWED_IDENTITY_ASSURANCE:
        raise Phase8LPathError(
            f"signer-identity-assurance must be one of {ALLOWED_IDENTITY_ASSURANCE}",
            "invalid_identity_assurance",
        )
    return value


def _read_integrity_report(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _build_descriptor(
    manifest_file: Path,
    integrity: dict[str, Any],
    signer_id: str,
    signer_role: str,
    signer_identity_assurance: str,
    key_id: str,
    key_version: str,
    signing_policy_version: str,
) -> dict[str, Any]:
    manifest_bytes = manifest_file.read_bytes()
    return {
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
        "export_manifest_path": _rel(manifest_file),
        "export_manifest_sha256": _sha256_hex(manifest_bytes),
        "bundle_hash": integrity.get("computed_bundle_hash"),
        "computed_manifest_hash": integrity.get("computed_manifest_hash"),
        "report_schema_version": integrity.get("report_schema_version"),
        "issue_taxonomy_version": integrity.get("issue_taxonomy_version"),
        "compatibility_matrix_version": integrity.get("compatibility_matrix_version"),
        "verifier_hardening_status": integrity.get("verifier_hardening_status"),
        "verification_status": integrity.get("verification_status"),
        "compatibility_result": integrity.get("compatibility_result"),
        "incident_classification": integrity.get("incident_classification"),
        "reviewer_action": integrity.get("reviewer_action"),
        "reviewer_action_required": integrity.get("reviewer_action_required"),
        "generated_from_phase": "phase8l",
        "generated_by_tool": "build_phase8l_detached_signature.py",
        "created_at_utc": _now_utc(),
        "signing_policy_version": signing_policy_version,
        "signer_id": signer_id,
        "signer_role": signer_role,
        "signer_identity_assurance": signer_identity_assurance,
        "key_id": key_id,
        "key_version": key_version,
        "approval_boundary_statement": APPROVAL_BOUNDARY_STATEMENT,
    }


def _compute_prototype_signature(signed_payload_sha256: str) -> str | None:
    """Return the HMAC-SHA256 prototype signature hex digest, or None if the
    in-memory prototype key env var is unset.

    The raw key is used only in memory here and is never returned, written, or
    logged. The returned value is a MAC over ``signed_payload_sha256``.
    """
    raw_key = os.environ.get(PROTOTYPE_KEY_ENV)
    if not raw_key:
        return None
    return hmac.new(
        raw_key.encode("utf-8"),
        signed_payload_sha256.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _build_envelope(
    descriptor: dict[str, Any],
    signed_payload_sha256: str,
    descriptor_path: Path,
    signature_artifact_path: Path,
    envelope_path: Path,
    signature_value: str | None,
    signature_status: str,
    signing_status: str,
) -> dict[str, Any]:
    detached_signature_path = (
        _rel(signature_artifact_path) if signature_value is not None else _rel(envelope_path)
    )
    envelope: dict[str, Any] = {
        "signature_schema_version": ENVELOPE_SCHEMA_VERSION,
        "signed_payload_sha256": signed_payload_sha256,
        "signed_payload_descriptor_path": _rel(descriptor_path),
        "detached_signature_path": detached_signature_path,
        "signature_algorithm": PROTOTYPE_SIGNATURE_ALGORITHM,
        "signature_encoding": "hex",
        "key_id": descriptor["key_id"],
        "key_version": descriptor["key_version"],
        "signer_id": descriptor["signer_id"],
        "signer_role": descriptor["signer_role"],
        "signer_identity_assurance": descriptor["signer_identity_assurance"],
        "signing_policy_version": descriptor["signing_policy_version"],
        "signing_timestamp_utc": _now_utc(),
        "signature_status": signature_status,
        "signing_status": signing_status,
        "verification_status": "not_verified",
        "revocation_status": "not_checked",
        "rotation_epoch": "prototype",
        "approval_boundary_statement": APPROVAL_BOUNDARY_STATEMENT,
        "signature_runtime_status": SIGNATURE_RUNTIME_STATUS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "detached_signature_value": signature_value,
    }
    return envelope


def _build_summary(
    signing_status: str,
    signature_status: str,
    signed_payload_sha256: str | None,
    output_dir: Path,
    manifest_path_ref: str,
    integrity_report_path_ref: str | None,
    descriptor_path: Path | None,
    envelope_path: Path | None,
    signer_id: str,
    signer_role: str,
    signer_identity_assurance: str,
    key_id: str,
    key_version: str,
    signing_policy_version: str,
) -> dict[str, Any]:
    return {
        "phase8l_status": PHASE8L_STATUS,
        "durable_audit_store_status": DURABLE_AUDIT_STORE_STATUS,
        "phase7d_runtime_readiness": PHASE7D_RUNTIME_READINESS,
        "signing_implementation_status": SIGNING_IMPLEMENTATION_STATUS,
        "signature_runtime_status": SIGNATURE_RUNTIME_STATUS,
        "signature_verifier_runtime_status": SIGNATURE_VERIFIER_RUNTIME_STATUS,
        "key_management_runtime_status": KEY_MANAGEMENT_RUNTIME_STATUS,
        "major_phase_branch_workflow": MAJOR_PHASE_BRANCH_WORKFLOW,
        "signing_status": signing_status,
        "signature_status": signature_status,
        "prototype_signature_algorithm": PROTOTYPE_SIGNATURE_ALGORITHM,
        "signed_payload_sha256": signed_payload_sha256,
        "output_dir": _rel(output_dir),
        "manifest_path": manifest_path_ref,
        "integrity_report_path": integrity_report_path_ref,
        "signed_payload_descriptor_path": _rel(descriptor_path) if descriptor_path else None,
        "detached_signature_envelope_path": _rel(envelope_path) if envelope_path else None,
        "signer_id": signer_id,
        "signer_role": signer_role,
        "signer_identity_assurance": signer_identity_assurance,
        "key_id": key_id,
        "key_version": key_version,
        "signing_policy_version": signing_policy_version,
        "safety_statement": SAFETY_STATEMENT,
        "approval_boundary_statement": APPROVAL_BOUNDARY_STATEMENT,
        "limitations": LIMITATIONS,
    }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Phase 8L — Local Detached Signature Prototype Summary",
        "",
        "```text",
        f"phase8l_status: {summary['phase8l_status']}",
        f"signing_status: {summary['signing_status']}",
        f"signature_status: {summary['signature_status']}",
        f"prototype_signature_algorithm: {summary['prototype_signature_algorithm']}",
        f"signed_payload_sha256: {summary['signed_payload_sha256']}",
        "```",
        "",
        "## Signer metadata",
        "",
        f"- signer_id: {summary['signer_id']}",
        f"- signer_role: {summary['signer_role']}",
        f"- signer_identity_assurance: {summary['signer_identity_assurance']}",
        "",
        "## Key metadata",
        "",
        f"- key_id: {summary['key_id']}",
        f"- key_version: {summary['key_version']}",
        f"- signing_policy_version: {summary['signing_policy_version']}",
        "",
        "## Output paths",
        "",
        f"- output_dir: {summary['output_dir']}",
        f"- manifest_path: {summary['manifest_path']}",
        f"- integrity_report_path: {summary['integrity_report_path']}",
        f"- signed_payload_descriptor_path: {summary['signed_payload_descriptor_path']}",
        f"- detached_signature_envelope_path: {summary['detached_signature_envelope_path']}",
        "",
        "## Safety boundary",
        "",
        "- signature is not approval",
        "- signed export is not approval",
        "- local prototype signature is not approval",
        "- signature generation does not call the wrapper or primitives",
        "- signature generation does not trigger the next gate",
        "- signature generation does not set approval flags",
        "- signature generation does not write the vault",
        "- reviewer action remains review guidance only",
        "",
        f"{summary['safety_statement']}",
        "",
        f"{summary['approval_boundary_statement']}",
        "",
        "## Known limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in summary["limitations"])
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(output_dir: Path, summary: dict[str, Any]) -> None:
    _write_json(output_dir / "detached-signature-summary.json", summary)
    (output_dir / "detached-signature-summary.md").write_text(
        _render_summary_md(summary), encoding="utf-8"
    )


def run(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    """Return (summary, ok). ok is False on a path/manifest failure."""
    output_dir = _validate_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    signer_id = args.signer_id
    signer_role = args.signer_role
    signer_identity_assurance = _validate_identity_assurance(args.signer_identity_assurance)
    key_id = args.key_id
    key_version = args.key_version
    signing_policy_version = args.signing_policy_version

    descriptor_path = output_dir / "signed-payload-descriptor.json"
    envelope_path = output_dir / "detached-signature-envelope.json"
    signature_artifact_path = output_dir / "detached-signature.sig"

    # ── Validate the manifest path (missing is allowed; unsafe is rejected) ──
    try:
        manifest_file = _validate_input_path(args.manifest_path, "manifest")
    except Phase8LPathError as exc:
        summary = _build_summary(
            signing_status="invalid_manifest_path",
            signature_status="not_present",
            signed_payload_sha256=None,
            output_dir=output_dir,
            manifest_path_ref=args.manifest_path,
            integrity_report_path_ref=args.integrity_report_path,
            descriptor_path=None,
            envelope_path=None,
            signer_id=signer_id,
            signer_role=signer_role,
            signer_identity_assurance=signer_identity_assurance,
            key_id=key_id,
            key_version=key_version,
            signing_policy_version=signing_policy_version,
        )
        summary["path_error_category"] = exc.category
        _write_summary(output_dir, summary)
        return summary, False

    # ── Missing manifest: not-ready output, exit 0 ───────────────────────────
    if manifest_file is None:
        summary = _build_summary(
            signing_status="skipped_missing_manifest",
            signature_status="not_present",
            signed_payload_sha256=None,
            output_dir=output_dir,
            manifest_path_ref=args.manifest_path,
            integrity_report_path_ref=args.integrity_report_path,
            descriptor_path=None,
            envelope_path=None,
            signer_id=signer_id,
            signer_role=signer_role,
            signer_identity_assurance=signer_identity_assurance,
            key_id=key_id,
            key_version=key_version,
            signing_policy_version=signing_policy_version,
        )
        _write_summary(output_dir, summary)
        return summary, True

    # ── Manifest present: must be a JSON object ──────────────────────────────
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        summary = _build_summary(
            signing_status="invalid_manifest",
            signature_status="not_present",
            signed_payload_sha256=None,
            output_dir=output_dir,
            manifest_path_ref=_rel(manifest_file),
            integrity_report_path_ref=args.integrity_report_path,
            descriptor_path=None,
            envelope_path=None,
            signer_id=signer_id,
            signer_role=signer_role,
            signer_identity_assurance=signer_identity_assurance,
            key_id=key_id,
            key_version=key_version,
            signing_policy_version=signing_policy_version,
        )
        _write_summary(output_dir, summary)
        return summary, False
    if not isinstance(manifest, dict):
        summary = _build_summary(
            signing_status="invalid_manifest",
            signature_status="not_present",
            signed_payload_sha256=None,
            output_dir=output_dir,
            manifest_path_ref=_rel(manifest_file),
            integrity_report_path_ref=args.integrity_report_path,
            descriptor_path=None,
            envelope_path=None,
            signer_id=signer_id,
            signer_role=signer_role,
            signer_identity_assurance=signer_identity_assurance,
            key_id=key_id,
            key_version=key_version,
            signing_policy_version=signing_policy_version,
        )
        _write_summary(output_dir, summary)
        return summary, False

    # ── Optional integrity report (unsafe path is rejected when provided) ────
    integrity_report_file = _validate_input_path(args.integrity_report_path, "integrity-report")
    integrity = _read_integrity_report(integrity_report_file)
    integrity_report_ref = _rel(integrity_report_file) if integrity_report_file else args.integrity_report_path

    # ── Build canonical descriptor and hash it ───────────────────────────────
    descriptor = _build_descriptor(
        manifest_file=manifest_file,
        integrity=integrity,
        signer_id=signer_id,
        signer_role=signer_role,
        signer_identity_assurance=signer_identity_assurance,
        key_id=key_id,
        key_version=key_version,
        signing_policy_version=signing_policy_version,
    )
    signed_payload_sha256 = _sha256_hex(_canonical_json(descriptor).encode("utf-8"))

    # ── Prototype signature (only when the in-memory key env var is set) ─────
    signature_value = _compute_prototype_signature(signed_payload_sha256)
    if signature_value is None:
        signing_status = "skipped_missing_prototype_key"
        signature_status = "not_ready"
    else:
        signing_status = "signed_local_prototype"
        signature_status = "present"

    envelope = _build_envelope(
        descriptor=descriptor,
        signed_payload_sha256=signed_payload_sha256,
        descriptor_path=descriptor_path,
        signature_artifact_path=signature_artifact_path,
        envelope_path=envelope_path,
        signature_value=signature_value,
        signature_status=signature_status,
        signing_status=signing_status,
    )

    _write_json(descriptor_path, descriptor)
    _write_json(envelope_path, envelope)
    if signature_value is not None:
        signature_artifact_path.write_text(signature_value + "\n", encoding="utf-8")

    summary = _build_summary(
        signing_status=signing_status,
        signature_status=signature_status,
        signed_payload_sha256=signed_payload_sha256,
        output_dir=output_dir,
        manifest_path_ref=_rel(manifest_file),
        integrity_report_path_ref=integrity_report_ref,
        descriptor_path=descriptor_path,
        envelope_path=envelope_path,
        signer_id=signer_id,
        signer_role=signer_role,
        signer_identity_assurance=signer_identity_assurance,
        key_id=key_id,
        key_version=key_version,
        signing_policy_version=signing_policy_version,
    )
    _write_summary(output_dir, summary)
    return summary, True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 8L local-only detached signature prototype over a Phase 8E export manifest."
    )
    parser.add_argument("--manifest-path", default=DEFAULT_MANIFEST_PATH, dest="manifest_path")
    parser.add_argument(
        "--integrity-report-path", default=DEFAULT_INTEGRITY_REPORT_PATH, dest="integrity_report_path"
    )
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, dest="output_dir")
    parser.add_argument("--signer-id", default=DEFAULT_SIGNER_ID, dest="signer_id")
    parser.add_argument("--signer-role", default=DEFAULT_SIGNER_ROLE, dest="signer_role")
    parser.add_argument(
        "--signer-identity-assurance",
        default=DEFAULT_SIGNER_IDENTITY_ASSURANCE,
        dest="signer_identity_assurance",
    )
    parser.add_argument("--key-id", default=DEFAULT_KEY_ID, dest="key_id")
    parser.add_argument("--key-version", default=DEFAULT_KEY_VERSION, dest="key_version")
    parser.add_argument(
        "--signing-policy-version",
        default=DEFAULT_SIGNING_POLICY_VERSION,
        dest="signing_policy_version",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary, ok = run(args)
    except Phase8LPathError as exc:
        print(f"error: {exc} [{exc.category}]", file=sys.stderr)
        return 1

    print(f"phase8l_status: {summary['phase8l_status']}")
    print(f"signing_status: {summary['signing_status']}")
    print(f"signature_status: {summary['signature_status']}")
    print(f"signed_payload_sha256: {summary['signed_payload_sha256']}")
    print(f"output_dir: {summary['output_dir']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
