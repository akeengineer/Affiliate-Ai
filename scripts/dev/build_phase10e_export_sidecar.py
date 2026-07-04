#!/usr/bin/env python3
"""Build a local-only derived export sidecar for Phase 10E.

This prototype reads one local manifest, validates safe export/context
references, hashes present files, extracts safe summary fields from optional
JSON context files, treats safe missing files as warnings, rejects unsafe
paths, secrets, approval flags, and execution intent, and writes deterministic
JSON/Markdown only under tmp/phase10e-export-sidecar/.

Export sidecar is not approval. Export sidecar validity is not approval.
Verified export is not approval. Signed export is not approval. Actor context
is not authentication. RBAC advisory context is not enforcement. Verified
signature remains not approval. Approval remains Phase 7D selected-gate manual
boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = "tmp/phase10e-export-sidecar"
ALLOWED_OUTPUT_PREFIX = ("tmp", "phase10e-export-sidecar")
FORBIDDEN_ROOTS = {"vault", "docs", "scripts", "codex", ".git"}
ALLOWED_REFERENCE_PREFIXES = {("tmp",), ("tests", "fixtures")}

STATUS_BLOCK = {
    "phase10e_status": "success",
    "phase10d_status": "success",
    "phase10c_status": "success",
    "phase10b_status": "success",
    "phase10a_status": "success",
    "phase7d_runtime_readiness": "implemented_manual_gate",
    "durable_audit_store_status": "phase8_final_acceptance_pack",
    "audit_actor_attribution_integration_status": "derived_report_prototype",
    "governed_runtime_integration_status": "local_evidence_bundle_actor_report_and_export_sidecar_prototypes",
    "integration_runtime_status": "local_export_sidecar_prototype",
    "local_evidence_bundle_status": "prototype_local_only",
    "actor_attributed_audit_report_status": "prototype_local_only",
    "export_sidecar_status": "prototype_local_only",
    "identity_boundary_status": "design_only",
    "actor_metadata_schema_status": "design_only",
    "actor_metadata_runtime_status": "local_registry_prototype",
    "local_operator_registry_status": "prototype_local_only",
    "actor_attribution_status": "local_report_prototype",
    "rbac_policy_status": "local_advisory_prototype",
    "rbac_runtime_status": "local_advisory_prototype",
    "rbac_enforcement_status": "not_implemented",
    "identity_runtime_status": "not_implemented",
    "authentication_runtime_status": "not_implemented",
    "operator_identity_assurance_status": "unauthenticated_or_operator_declared",
    "signing_implementation_status": "prototype_local_only",
    "signature_runtime_status": "local_prototype",
    "signature_verifier_runtime_status": "local_prototype",
    "key_management_runtime_status": "not_implemented",
    "backend_api_database_status": "not_implemented",
    "phase10_branch_workflow": "enabled",
}

LIMITATIONS = [
    "local prototype only",
    "derived export sidecar only",
    "no authentication runtime",
    "no RBAC enforcement",
    "no backend/API/database",
    "no key management runtime",
    "no export mutation",
    "no primitive execution",
]

MANIFEST_REQUIRED_FIELDS = (
    "sidecar_schema_version",
    "sidecar_id",
    "sidecar_purpose",
    "export_references",
    "approval_boundary_statement",
)
REFERENCE_REQUIRED_FIELDS = (
    "export_id",
    "export_type",
    "export_phase",
    "export_path",
    "export_purpose",
    "export_boundary_statement",
)

ALLOWED_EXPORT_TYPES = {
    "audit_export_manifest",
    "audit_export_summary",
    "audit_export_evidence_file",
    "export_integrity_report",
    "detached_signature_envelope",
    "signature_verifier_report",
    "final_acceptance_pack",
    "local_evidence_bundle",
    "actor_attributed_audit_report",
    "actor_attribution_report",
    "local_rbac_advisory_report",
    "selected_gate_boundary_reference",
    "test_fixture",
}
ALLOWED_EXPORT_PHASES = {
    "phase7d",
    "phase8e",
    "phase8g",
    "phase8h",
    "phase8l",
    "phase8m",
    "phase8o",
    "phase9c",
    "phase9d",
    "phase9f",
    "phase9g",
    "phase10a",
    "phase10b",
    "phase10c",
    "phase10d",
    "phase10e",
    "test_fixture",
}

OPTIONAL_REFERENCE_RULES = {
    "evidence_bundle_reference": {
        "allowed_phrases": (
            "evidence bundle validity is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "evidence_bundle_review_required",
    },
    "actor_attributed_audit_report_reference": {
        "allowed_phrases": (
            "actor-attributed audit report is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "actor_attributed_audit_report_review_required",
    },
    "actor_attribution_context_reference": {
        "allowed_phrases": (
            "actor context is not authentication",
            "audit actor attribution is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "actor_context_review_required",
    },
    "rbac_advisory_context_reference": {
        "allowed_phrases": (
            "rbac advisory context is not enforcement",
            "rbac allow decision is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "rbac_advisory_review_required",
    },
    "signature_context_reference": {
        "allowed_phrases": (
            "verified signature remains not approval",
            "signature verifier result is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "signature_review_required",
    },
    "export_integrity_context_reference": {
        "allowed_phrases": (
            "verified export is not approval",
            "export manifest hash is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "export_integrity_review_required",
    },
    "final_acceptance_context_reference": {
        "allowed_phrases": (
            "final acceptance remains not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "final_acceptance_review_required",
    },
    "approval_boundary_reference": {
        "allowed_phrases": (
            "approval remains phase 7d selected-gate manual boundary",
            "export sidecar is not approval",
        ),
        "warning_incident": "approval_boundary_review_required",
    },
}

EVIDENCE_BUNDLE_FIELDS = (
    "bundle_id",
    "bundle_status",
    "bundle_hash",
    "evidence_reference_count",
    "present_evidence_count",
    "missing_evidence_count",
    "approval_boundary_statement",
)
ACTOR_REPORT_FIELDS = (
    "report_id",
    "report_status",
    "report_hash",
    "audit_evidence_reference_count",
    "present_evidence_count",
    "missing_evidence_count",
    "actor_context_summary",
    "rbac_advisory_context_summary",
    "approval_boundary_statement",
)
ACTOR_CONTEXT_FIELDS = (
    "actor_id",
    "actor_type",
    "actor_identity_assurance",
    "actor_identity_source",
    "actor_role_labels",
    "actor_attribution_status",
    "approval_boundary_statement",
)
RBAC_CONTEXT_FIELDS = (
    "advisory_decision",
    "decision_reason",
    "obligations",
    "denial_reasons",
    "rbac_policy_status",
    "rbac_enforcement_status",
    "approval_boundary_statement",
)
SIGNATURE_CONTEXT_FIELDS = (
    "export_integrity_status",
    "signature_verification_status",
    "signed_payload_hash_status",
    "verification_result",
    "compatibility_result",
    "approval_boundary_statement",
)
FINAL_ACCEPTANCE_FIELDS = (
    "phase8o_status",
    "final_acceptance_status",
    "reviewer_action",
    "approval_boundary_statement",
)

APPROVAL_BOUNDARY_PHRASES = (
    "export sidecar is not approval",
    "export sidecar validity is not approval",
    "approval remains phase 7d selected-gate manual boundary",
)
EXPORT_BOUNDARY_PHRASES = (
    "export sidecar inclusion is not approval",
    "export manifest hash is not approval",
    "export sidecar hash is not approval",
    "approval remains phase 7d selected-gate manual boundary",
)
APPROVAL_FLAG_KEYS = (
    "approved",
    "is_approved",
    "approval_granted",
    "auto_approve",
    "approve_all",
)
EXECUTION_FLAG_KEYS = ("next_gate", "execute", "enforcement_enabled")
PRIMITIVE_INTENT_KEYS = (
    "execute_primitive",
    "primitive_execution_intent",
    "run_primitive",
    "execution_intent",
)
SECRET_MARKERS = (
    "affiliate_phase8l_prototype_key",
    "begin private key",
    "begin rsa private key",
    "begin openssh private key",
    "api_key=",
    "secret=",
    "token=",
    "password=",
    "aws_secret_access_key",
    "ssh-rsa",
    "oauth access_token",
    "access_token",
    "id_token",
    "refresh_token",
)
URL_SCHEME_RE = re.compile(r"[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.IGNORECASE)
INCIDENT_PRIORITY = [
    "privacy_review_required",
    "approval_boundary_review_required",
    "primitive_execution_blocked",
    "runtime_scope_violation",
    "actor_context_review_required",
    "rbac_advisory_review_required",
    "signature_review_required",
    "export_integrity_review_required",
    "final_acceptance_review_required",
    "export_review_required",
    "evidence_bundle_review_required",
    "actor_attributed_audit_report_review_required",
    "none",
]
REVIEWER_PRIORITY = [
    "reject_runtime_scope_until_resolved",
    "reject_export_sidecar_until_resolved",
    "manual_review_required",
    "no_action_required",
]


class SidecarError(Exception):
    def __init__(self, issue: dict) -> None:
        super().__init__(issue["message"])
        self.issue = issue


def make_issue(
    issue_type: str,
    severity: str,
    incident: str,
    reviewer_action: str,
    message: str,
    *,
    export_id: str = "",
    reference_type: str = "",
) -> dict:
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident,
        "reviewer_action": reviewer_action,
        "export_id": export_id,
        "reference_type": reference_type,
        "message": message,
    }


def _iter_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _contains_secret_like_data(value: object) -> bool:
    for text in _iter_strings(value):
        low = text.lower()
        if any(marker in low for marker in SECRET_MARKERS):
            return True
        if URL_SCHEME_RE.search(text):
            return True
        if EMAIL_RE.search(text):
            return True
    return False


def _collect_truthy_flags(mapping: object, keys: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    if isinstance(mapping, dict):
        for key, value in mapping.items():
            if key in keys and bool(value):
                hits.append(key)
            hits.extend(_collect_truthy_flags(value, keys))
    elif isinstance(mapping, list):
        for item in mapping:
            hits.extend(_collect_truthy_flags(item, keys))
    return hits


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _resolve_output_dir(output_arg: str) -> Path:
    resolved = Path(output_arg).resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise SidecarError(
            make_issue(
                "unsafe_output_dir",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "output-dir must resolve under the repository root",
            )
        ) from exc
    if rel.parts[:2] != ALLOWED_OUTPUT_PREFIX:
        raise SidecarError(
            make_issue(
                "unsafe_output_dir",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "output-dir must be tmp/phase10e-export-sidecar or below it",
            )
        )
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _resolve_manifest_path(path_arg: str) -> Path:
    candidate = Path(path_arg) if Path(path_arg).is_absolute() else REPO_ROOT / path_arg
    if candidate.is_symlink():
        raise SidecarError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "manifest path must not be a symlink",
            )
        )
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise SidecarError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "manifest path must resolve under the repository root",
            )
        ) from exc
    if rel.parts and rel.parts[0] in FORBIDDEN_ROOTS:
        raise SidecarError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"manifest path must not resolve under {rel.parts[0]}/",
            )
        )
    if not resolved.is_file():
        raise SidecarError(
            make_issue(
                "manifest_missing",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                "manifest path does not exist",
            )
        )
    return resolved


def _resolve_repo_relative(
    path_arg: str,
    *,
    allow_missing: bool,
    incident: str,
    reviewer_action: str,
) -> tuple[Path, str]:
    candidate = Path(path_arg) if Path(path_arg).is_absolute() else REPO_ROOT / path_arg
    if candidate.is_symlink():
        raise SidecarError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must not be a symlink: {path_arg}",
            )
        )
    resolved = candidate.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise SidecarError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must resolve under the repository root: {path_arg}",
            )
        ) from exc
    if rel.parts and rel.parts[0] in FORBIDDEN_ROOTS:
        raise SidecarError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must not resolve under {rel.parts[0]}/: {path_arg}",
            )
        )
    if rel.parts[:1] not in ALLOWED_REFERENCE_PREFIXES and rel.parts[:2] not in ALLOWED_REFERENCE_PREFIXES:
        raise SidecarError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must resolve under tmp/ or tests/fixtures/: {path_arg}",
            )
        )
    if not resolved.exists():
        if allow_missing:
            return resolved, str(rel)
        raise SidecarError(make_issue("missing_path", "warning", incident, reviewer_action, f"path does not exist: {path_arg}"))
    if not resolved.is_file():
        raise SidecarError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must be a file: {path_arg}",
            )
        )
    return resolved, str(rel)


def _load_manifest(manifest_path: Path) -> dict:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SidecarError(
            make_issue(
                "invalid_manifest_json",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                f"manifest is not valid JSON: {exc}",
            )
        ) from exc
    if not isinstance(data, dict):
        raise SidecarError(
            make_issue(
                "invalid_manifest_shape",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                "manifest must be a JSON object",
            )
        )
    return data


def _validate_manifest_basics(manifest: dict, issues: list[dict]) -> None:
    for field in MANIFEST_REQUIRED_FIELDS:
        if field not in manifest:
            issues.append(
                make_issue(
                    "manifest_missing_field",
                    "critical",
                    "export_review_required",
                    "reject_export_sidecar_until_resolved",
                    f"manifest is missing required field: {field}",
                )
            )
    if manifest.get("sidecar_schema_version") != "phase10e.export_sidecar.v1":
        issues.append(
            make_issue(
                "invalid_sidecar_schema_version",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                "sidecar_schema_version must be phase10e.export_sidecar.v1",
            )
        )
    if not isinstance(manifest.get("export_references"), list):
        issues.append(
            make_issue(
                "invalid_export_references",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                "export_references must be a list",
            )
        )
    elif not manifest["export_references"]:
        issues.append(
            make_issue(
                "empty_export_references",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                "export_references must not be empty",
            )
        )


def _validate_secret_and_approval_guards(manifest: dict, issues: list[dict]) -> None:
    if _contains_secret_like_data(manifest):
        issues.append(
            make_issue(
                "secret_like_metadata",
                "critical",
                "privacy_review_required",
                "reject_export_sidecar_until_resolved",
                "manifest contains secret-like, URL-like, or raw email data",
            )
        )
    for key in _collect_truthy_flags(manifest, APPROVAL_FLAG_KEYS):
        issues.append(
            make_issue(
                "approval_flag_present",
                "critical",
                "approval_boundary_review_required",
                "reject_export_sidecar_until_resolved",
                f"approval flag must not be truthy: {key}",
            )
        )
    for key in _collect_truthy_flags(manifest, EXECUTION_FLAG_KEYS):
        incident = "approval_boundary_review_required" if key != "enforcement_enabled" else "runtime_scope_violation"
        reviewer = "reject_export_sidecar_until_resolved" if key != "enforcement_enabled" else "reject_runtime_scope_until_resolved"
        issues.append(
            make_issue(
                "execution_intent_present",
                "critical",
                incident,
                reviewer,
                f"execution or enforcement intent must not be truthy: {key}",
            )
        )
    for key in _collect_truthy_flags(manifest, PRIMITIVE_INTENT_KEYS):
        issues.append(
            make_issue(
                "primitive_execution_intent_present",
                "critical",
                "primitive_execution_blocked",
                "reject_runtime_scope_until_resolved",
                f"primitive execution intent is not allowed: {key}",
            )
        )
    statement = _normalize_text(str(manifest.get("approval_boundary_statement", "")))
    if not any(token in statement for token in APPROVAL_BOUNDARY_PHRASES):
        issues.append(
            make_issue(
                "approval_boundary_statement_missing",
                "critical",
                "approval_boundary_review_required",
                "reject_export_sidecar_until_resolved",
                "approval_boundary_statement must declare not-approval semantics",
            )
        )


def _build_export_record(reference: dict, issues: list[dict]) -> dict:
    export_id = str(reference.get("export_id", ""))
    for field in REFERENCE_REQUIRED_FIELDS:
        if field not in reference:
            issues.append(
                make_issue(
                    "export_reference_missing_field",
                    "critical",
                    "export_review_required",
                    "reject_export_sidecar_until_resolved",
                    f"export reference is missing required field: {field}",
                    export_id=export_id,
                )
            )
    if reference.get("export_type") not in ALLOWED_EXPORT_TYPES:
        issues.append(
            make_issue(
                "invalid_export_type",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                f"unsupported export_type: {reference.get('export_type')}",
                export_id=export_id,
            )
        )
    if reference.get("export_phase") not in ALLOWED_EXPORT_PHASES:
        issues.append(
            make_issue(
                "invalid_export_phase",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                f"unsupported export_phase: {reference.get('export_phase')}",
                export_id=export_id,
            )
        )
    if _contains_secret_like_data(reference):
        issues.append(
            make_issue(
                "secret_like_export_metadata",
                "critical",
                "privacy_review_required",
                "reject_export_sidecar_until_resolved",
                "export reference contains secret-like, URL-like, or raw email data",
                export_id=export_id,
            )
        )
    boundary = _normalize_text(str(reference.get("export_boundary_statement", "")))
    if not any(token in boundary for token in EXPORT_BOUNDARY_PHRASES):
        issues.append(
            make_issue(
                "export_boundary_statement_missing",
                "critical",
                "approval_boundary_review_required",
                "reject_export_sidecar_until_resolved",
                "export_boundary_statement must declare not-approval semantics",
                export_id=export_id,
            )
        )

    record = dict(reference)
    path_arg = str(reference.get("export_path", ""))
    try:
        resolved, relative_path = _resolve_repo_relative(
            path_arg,
            allow_missing=True,
            incident="export_review_required",
            reviewer_action="manual_review_required",
        )
    except SidecarError as exc:
        issue = dict(exc.issue)
        issue["export_id"] = export_id
        issues.append(issue)
        record["export_status"] = "invalid"
        record["relative_path"] = ""
        return record

    record["relative_path"] = relative_path
    if not resolved.exists():
        record["export_status"] = "missing"
        issues.append(
            make_issue(
                "export_file_missing",
                "warning",
                "export_review_required",
                "manual_review_required",
                f"safe export path is missing: {path_arg}",
                export_id=export_id,
            )
        )
        return record

    record["export_status"] = "present"
    record["size_bytes"] = resolved.stat().st_size
    record["sha256"] = _sha256_file(resolved)
    return record


def _extract_summary(field_name: str, parsed: dict, issues: list[dict], *, reference_type: str) -> dict:
    if field_name == "evidence_bundle_reference":
        wanted = EVIDENCE_BUNDLE_FIELDS
        missing_issue = "evidence_bundle_summary_missing"
        incident = "evidence_bundle_review_required"
    elif field_name == "actor_attributed_audit_report_reference":
        wanted = ACTOR_REPORT_FIELDS
        missing_issue = "actor_report_summary_missing"
        incident = "actor_attributed_audit_report_review_required"
    elif field_name == "actor_attribution_context_reference":
        wanted = ACTOR_CONTEXT_FIELDS
        missing_issue = "actor_context_summary_missing"
        incident = "actor_context_review_required"
    elif field_name == "rbac_advisory_context_reference":
        wanted = RBAC_CONTEXT_FIELDS
        missing_issue = "rbac_context_summary_missing"
        incident = "rbac_advisory_review_required"
    elif field_name in {"signature_context_reference", "export_integrity_context_reference"}:
        return {key: parsed[key] for key in SIGNATURE_CONTEXT_FIELDS if key in parsed}
    else:
        return {key: parsed[key] for key in FINAL_ACCEPTANCE_FIELDS if key in parsed}

    summary: dict = {}
    missing: list[str] = []
    for key in wanted:
        if key in parsed:
            summary[key] = parsed[key]
        else:
            missing.append(key)
    if missing:
        issues.append(
            make_issue(
                missing_issue,
                "warning",
                incident,
                "manual_review_required",
                f"summary fields missing from {field_name}: {', '.join(missing)}",
                reference_type=reference_type,
            )
        )
    return summary


def _build_optional_reference(field_name: str, payload: object, issues: list[dict]) -> dict:
    if payload is None:
        return {"reference_status": "absent", "reference_type": field_name}
    if not isinstance(payload, dict):
        issues.append(
            make_issue(
                "invalid_optional_reference_shape",
                "critical",
                "export_review_required",
                "reject_export_sidecar_until_resolved",
                f"{field_name} must be an object",
                reference_type=field_name,
            )
        )
        return {"reference_status": "invalid", "reference_type": field_name}

    allowed_phrases = OPTIONAL_REFERENCE_RULES[field_name]["allowed_phrases"]
    boundary = _normalize_text(str(payload.get("reference_boundary_statement", "")))
    if not any(token in boundary for token in allowed_phrases):
        issues.append(
            make_issue(
                "optional_reference_boundary_missing",
                "critical",
                "approval_boundary_review_required",
                "reject_export_sidecar_until_resolved",
                f"{field_name} must declare its non-approval boundary",
                reference_type=field_name,
            )
        )

    if _contains_secret_like_data(payload):
        issues.append(
            make_issue(
                "secret_like_optional_reference",
                "critical",
                "privacy_review_required",
                "reject_export_sidecar_until_resolved",
                f"{field_name} contains secret-like, URL-like, or raw email data",
                reference_type=field_name,
            )
        )

    path_arg = str(payload.get("reference_path", ""))
    record = dict(payload)
    try:
        resolved, relative_path = _resolve_repo_relative(
            path_arg,
            allow_missing=True,
            incident=OPTIONAL_REFERENCE_RULES[field_name]["warning_incident"],
            reviewer_action="manual_review_required",
        )
    except SidecarError as exc:
        issue = dict(exc.issue)
        issue["reference_type"] = field_name
        issues.append(issue)
        record["reference_status"] = "invalid"
        return record

    record["relative_path"] = relative_path
    if not resolved.exists():
        record["reference_status"] = "missing"
        issues.append(
            make_issue(
                "optional_reference_missing",
                "warning",
                OPTIONAL_REFERENCE_RULES[field_name]["warning_incident"],
                "manual_review_required",
                f"safe optional reference is missing: {path_arg}",
                reference_type=field_name,
            )
        )
        return record

    record["reference_status"] = "present"
    record["size_bytes"] = resolved.stat().st_size
    record["sha256"] = _sha256_file(resolved)

    if field_name == "approval_boundary_reference":
        return record

    try:
        parsed = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        issues.append(
            make_issue(
                "optional_context_json_invalid",
                "warning",
                OPTIONAL_REFERENCE_RULES[field_name]["warning_incident"],
                "manual_review_required",
                f"{field_name} is present but not valid JSON",
                reference_type=field_name,
            )
        )
        return record

    if not isinstance(parsed, dict):
        issues.append(
            make_issue(
                "optional_context_json_invalid",
                "warning",
                OPTIONAL_REFERENCE_RULES[field_name]["warning_incident"],
                "manual_review_required",
                f"{field_name} must parse to a JSON object",
                reference_type=field_name,
            )
        )
        return record

    if _contains_secret_like_data(parsed):
        issues.append(
            make_issue(
                "secret_like_optional_context",
                "critical",
                "privacy_review_required",
                "reject_export_sidecar_until_resolved",
                f"{field_name} JSON contains secret-like, URL-like, or raw email data",
                reference_type=field_name,
            )
        )
        return record

    summary = _extract_summary(field_name, parsed, issues, reference_type=field_name)
    summary["reference_status"] = "present"
    summary["reference_type"] = field_name
    summary["relative_path"] = relative_path
    summary["size_bytes"] = record["size_bytes"]
    summary["sha256"] = record["sha256"]
    return summary


def _severity_counts(issues: list[dict]) -> dict:
    counts = {"info": 0, "warning": 0, "critical": 0}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return counts


def _select_incident(issues: list[dict]) -> str:
    if not issues:
        return "none"
    incidents = {issue["incident_classification"] for issue in issues}
    for incident in INCIDENT_PRIORITY:
        if incident in incidents:
            return incident
    return "export_review_required"


def _select_reviewer_action(issues: list[dict]) -> str:
    if not issues:
        return "no_action_required"
    actions = {issue["reviewer_action"] for issue in issues}
    for action in REVIEWER_PRIORITY:
        if action in actions:
            return action
    return "manual_review_required"


def _determine_sidecar_status(issues: list[dict]) -> str:
    if any(issue["severity"] == "critical" for issue in issues):
        return "not_built"
    if any(issue["severity"] == "warning" for issue in issues):
        return "built_with_warnings"
    return "built"


def _build_report(manifest: dict) -> dict:
    issues: list[dict] = []
    export_records: list[dict] = []

    _validate_manifest_basics(manifest, issues)
    _validate_secret_and_approval_guards(manifest, issues)

    references = manifest.get("export_references")
    if isinstance(references, list):
        for reference in references:
            if not isinstance(reference, dict):
                issues.append(
                    make_issue(
                        "invalid_export_reference_shape",
                        "critical",
                        "export_review_required",
                        "reject_export_sidecar_until_resolved",
                        "each export reference must be an object",
                    )
                )
                export_records.append({"export_status": "invalid"})
                continue
            export_records.append(_build_export_record(reference, issues))

    evidence_bundle_summary = _build_optional_reference("evidence_bundle_reference", manifest.get("evidence_bundle_reference"), issues)
    actor_attributed_audit_report_summary = _build_optional_reference(
        "actor_attributed_audit_report_reference",
        manifest.get("actor_attributed_audit_report_reference"),
        issues,
    )
    actor_attribution_context_summary = _build_optional_reference(
        "actor_attribution_context_reference",
        manifest.get("actor_attribution_context_reference"),
        issues,
    )
    rbac_advisory_context_summary = _build_optional_reference(
        "rbac_advisory_context_reference",
        manifest.get("rbac_advisory_context_reference"),
        issues,
    )
    signature_context_summary = _build_optional_reference(
        "signature_context_reference",
        manifest.get("signature_context_reference"),
        issues,
    )
    export_integrity_context_summary = _build_optional_reference(
        "export_integrity_context_reference",
        manifest.get("export_integrity_context_reference"),
        issues,
    )
    final_acceptance_context_summary = _build_optional_reference(
        "final_acceptance_context_reference",
        manifest.get("final_acceptance_context_reference"),
        issues,
    )
    approval_boundary_reference = _build_optional_reference(
        "approval_boundary_reference",
        manifest.get("approval_boundary_reference"),
        issues,
    )

    report = {
        **STATUS_BLOCK,
        "sidecar_schema_version": str(manifest.get("sidecar_schema_version", "")),
        "sidecar_id": str(manifest.get("sidecar_id", "")),
        "sidecar_purpose": str(manifest.get("sidecar_purpose", "")),
        "sidecar_status": _determine_sidecar_status(issues),
        "export_reference_count": len(export_records),
        "present_export_count": sum(1 for item in export_records if item.get("export_status") == "present"),
        "missing_export_count": sum(1 for item in export_records if item.get("export_status") == "missing"),
        "invalid_export_count": sum(1 for item in export_records if item.get("export_status") == "invalid"),
        "optional_context_count": sum(
            1
            for item in (
                evidence_bundle_summary,
                actor_attributed_audit_report_summary,
                actor_attribution_context_summary,
                rbac_advisory_context_summary,
                signature_context_summary,
                export_integrity_context_summary,
                final_acceptance_context_summary,
                approval_boundary_reference,
            )
            if item.get("reference_status") != "absent"
        ),
        "sidecar_hash": "",
        "reviewer_action": _select_reviewer_action(issues),
        "reviewer_action_required": _select_reviewer_action(issues) != "no_action_required",
        "incident_classification": _select_incident(issues),
        "severity_counts": _severity_counts(issues),
        "approval_boundary_statement": str(manifest.get("approval_boundary_statement", "")),
        "safety_statement": (
            "local-only derived export sidecar prototype; deterministic JSON/Markdown only; "
            "safe missing references become warnings; unsafe paths, secrets, approval flags, "
            "and execution intent are rejected"
        ),
        "limitations": manifest.get("limitations", LIMITATIONS)
        if isinstance(manifest.get("limitations"), list) or manifest.get("limitations") is None
        else LIMITATIONS,
        "issues": issues,
        "export_references": export_records,
        "evidence_bundle_summary": evidence_bundle_summary,
        "actor_attributed_audit_report_summary": actor_attributed_audit_report_summary,
        "actor_attribution_context_summary": actor_attribution_context_summary,
        "rbac_advisory_context_summary": rbac_advisory_context_summary,
        "signature_context_summary": signature_context_summary,
        "export_integrity_context_summary": export_integrity_context_summary,
        "final_acceptance_context_summary": final_acceptance_context_summary,
        "approval_boundary_reference": approval_boundary_reference,
    }
    if report["limitations"] is None:
        report["limitations"] = LIMITATIONS
    clone = json.loads(json.dumps(report))
    clone.pop("sidecar_hash", None)
    report["sidecar_hash"] = _sha256_bytes(_canonical_json(clone).encode("utf-8"))
    return report


def _markdown_report(report: dict, output_dir: Path) -> str:
    lines = [
        "# Phase 10E Export Sidecar",
        "",
        f"- phase10e_status: `{report['phase10e_status']}`",
        f"- sidecar_status: `{report['sidecar_status']}`",
        f"- sidecar_id: `{report['sidecar_id']}`",
        f"- export_reference_count: `{report['export_reference_count']}`",
        f"- present_export_count: `{report['present_export_count']}`",
        f"- missing_export_count: `{report['missing_export_count']}`",
        f"- invalid_export_count: `{report['invalid_export_count']}`",
        f"- sidecar_hash: `{report['sidecar_hash']}`",
        f"- reviewer_action: `{report['reviewer_action']}`",
        "",
        "## Issue Summary",
        "",
        f"- info: `{report['severity_counts']['info']}`",
        f"- warning: `{report['severity_counts']['warning']}`",
        f"- critical: `{report['severity_counts']['critical']}`",
        "",
        "## Export Source Summary",
        "",
        f"- {json.dumps(report['export_references'], sort_keys=True)}",
        "",
        "## Actor/RBAC Context Summary",
        "",
        f"- {json.dumps(report['actor_attribution_context_summary'], sort_keys=True)}",
        f"- {json.dumps(report['rbac_advisory_context_summary'], sort_keys=True)}",
        "",
        "## Evidence and Approval Context Summary",
        "",
        f"- {json.dumps(report['evidence_bundle_summary'], sort_keys=True)}",
        f"- {json.dumps(report['actor_attributed_audit_report_summary'], sort_keys=True)}",
        f"- {json.dumps(report['signature_context_summary'], sort_keys=True)}",
        f"- {json.dumps(report['export_integrity_context_summary'], sort_keys=True)}",
        f"- {json.dumps(report['final_acceptance_context_summary'], sort_keys=True)}",
        "",
        "## Output Paths",
        "",
        f"- JSON: `{output_dir / 'export-sidecar.json'}`",
        f"- Markdown: `{output_dir / 'export-sidecar.md'}`",
        "",
        "## Limitations",
        "",
    ]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary Statements",
            "",
            "- export sidecar is not approval",
            "- export sidecar validity is not approval",
            "- export sidecar inclusion is not approval",
            "- export sidecar hash is not approval",
            "- export manifest hash is not approval",
            "- verified export is not approval",
            "- signed export is not approval",
            "- verified signature remains not approval",
            "- signature verifier result is not approval",
            "- final acceptance remains not approval",
            "- actor-attributed audit report is not approval",
            "- actor context is not authentication",
            "- RBAC advisory context is not enforcement",
            "- RBAC allow decision is not approval",
            "- evidence bundle validity is not approval",
            "- approval remains Phase 7D selected-gate manual boundary",
        ]
    )
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- [{issue['severity']}] {issue['issue_type']}: {issue['message']}")
    return "\n".join(lines) + "\n"


def _write_outputs(report: dict, output_dir: Path) -> None:
    json_path = output_dir / "export-sidecar.json"
    markdown_path = output_dir / "export-sidecar.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown_report(report, output_dir), encoding="utf-8")


def _fallback_report(issue: dict) -> dict:
    report = {
        **STATUS_BLOCK,
        "sidecar_schema_version": "",
        "sidecar_id": "",
        "sidecar_purpose": "",
        "sidecar_status": "not_built",
        "export_reference_count": 0,
        "present_export_count": 0,
        "missing_export_count": 0,
        "invalid_export_count": 1 if issue["severity"] == "critical" else 0,
        "optional_context_count": 0,
        "sidecar_hash": "",
        "reviewer_action": issue["reviewer_action"],
        "reviewer_action_required": True,
        "incident_classification": issue["incident_classification"],
        "severity_counts": _severity_counts([issue]),
        "approval_boundary_statement": "",
        "safety_statement": (
            "local-only derived export sidecar prototype; deterministic JSON/Markdown only; "
            "unsafe paths, secrets, approval flags, and execution intent are rejected"
        ),
        "limitations": LIMITATIONS,
        "issues": [issue],
        "export_references": [],
        "evidence_bundle_summary": {"reference_status": "absent", "reference_type": "evidence_bundle_reference"},
        "actor_attributed_audit_report_summary": {
            "reference_status": "absent",
            "reference_type": "actor_attributed_audit_report_reference",
        },
        "actor_attribution_context_summary": {
            "reference_status": "absent",
            "reference_type": "actor_attribution_context_reference",
        },
        "rbac_advisory_context_summary": {
            "reference_status": "absent",
            "reference_type": "rbac_advisory_context_reference",
        },
        "signature_context_summary": {"reference_status": "absent", "reference_type": "signature_context_reference"},
        "export_integrity_context_summary": {
            "reference_status": "absent",
            "reference_type": "export_integrity_context_reference",
        },
        "final_acceptance_context_summary": {
            "reference_status": "absent",
            "reference_type": "final_acceptance_context_reference",
        },
        "approval_boundary_reference": {"reference_status": "absent", "reference_type": "approval_boundary_reference"},
    }
    clone = json.loads(json.dumps(report))
    clone.pop("sidecar_hash", None)
    report["sidecar_hash"] = _sha256_bytes(_canonical_json(clone).encode("utf-8"))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
    except SidecarError as exc:
        print(exc.issue["message"], file=sys.stderr)
        return 1

    try:
        manifest_path = _resolve_manifest_path(args.manifest)
        manifest = _load_manifest(manifest_path)
        report = _build_report(manifest)
    except SidecarError as exc:
        report = _fallback_report(exc.issue)
        _write_outputs(report, output_dir)
        print(exc.issue["message"], file=sys.stderr)
        return 1

    _write_outputs(report, output_dir)
    if report["sidecar_status"] == "not_built":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
