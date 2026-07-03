#!/usr/bin/env python3
"""Build a local-only derived evidence bundle for Phase 10C.

This prototype reads a single local manifest, validates safe evidence/context
references, hashes present files, treats safe missing files as warnings, rejects
unsafe paths/secrets/approval flags/execution intent, and writes deterministic
JSON/Markdown only under tmp/phase10c-local-evidence-bundle/.

Local evidence bundle is not approval. Evidence bundle validity is not
approval. Actor context is not authentication. RBAC advisory context is not
enforcement. RBAC allow decision is not approval. Signature verification
remains not approval. Approval remains Phase 7D selected-gate manual boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = "tmp/phase10c-local-evidence-bundle"
ALLOWED_OUTPUT_PREFIX = ("tmp", "phase10c-local-evidence-bundle")
FORBIDDEN_ROOTS = {"vault", "docs", "scripts", "codex", ".git"}
ALLOWED_REFERENCE_PREFIXES = {("tmp",), ("tests", "fixtures")}

STATUS_BLOCK = {
    "phase10c_status": "success",
    "phase10b_status": "success",
    "phase10a_status": "success",
    "phase7d_runtime_readiness": "implemented_manual_gate",
    "durable_audit_store_status": "phase8_final_acceptance_pack",
    "audit_actor_attribution_integration_status": "design_only",
    "governed_runtime_integration_status": "local_evidence_bundle_prototype",
    "integration_runtime_status": "local_evidence_bundle_prototype",
    "local_evidence_bundle_status": "prototype_local_only",
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
    "derived evidence bundle only",
    "no authentication runtime",
    "no RBAC enforcement",
    "no backend/API/database",
    "no key management runtime",
    "no primitive execution",
    "no audit store mutation",
]

MANIFEST_REQUIRED_FIELDS = (
    "bundle_schema_version",
    "bundle_id",
    "bundle_purpose",
    "evidence_references",
    "approval_boundary_statement",
)
REFERENCE_REQUIRED_FIELDS = (
    "evidence_id",
    "evidence_type",
    "evidence_phase",
    "evidence_path",
    "evidence_purpose",
    "evidence_boundary_statement",
)

ALLOWED_EVIDENCE_TYPES = {
    "audit_export_pack",
    "export_integrity_report",
    "detached_signature_envelope",
    "signature_verifier_report",
    "final_acceptance_pack",
    "local_operator_registry",
    "actor_attribution_report",
    "local_rbac_advisory_report",
    "selected_gate_boundary_reference",
    "audit_store_report",
    "audit_query_result",
    "test_fixture",
}
ALLOWED_EVIDENCE_PHASES = {
    "phase7d",
    "phase8b",
    "phase8c",
    "phase8d",
    "phase8e",
    "phase8g",
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
    "test_fixture",
}

OPTIONAL_REFERENCE_RULES = {
    "actor_context_reference": {
        "allowed_phrases": (
            "actor context is not authentication",
            "actor context is not approval",
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
            "signature verification remains not approval",
            "evidence bundle validity is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "signature_review_required",
    },
    "approval_boundary_reference": {
        "allowed_phrases": (
            "evidence reference is not approval",
            "evidence bundle validity is not approval",
            "approval remains phase 7d selected-gate manual boundary",
        ),
        "warning_incident": "approval_boundary_review_required",
    },
}

APPROVAL_BOUNDARY_PHRASES = (
    "local evidence bundle is not approval",
    "evidence bundle validity is not approval",
    "approval remains phase 7d selected-gate manual boundary",
)
EVIDENCE_BOUNDARY_PHRASES = (
    "evidence reference is not approval",
    "evidence hash is not approval",
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
    "evidence_review_required",
    "evidence_bundle_review_required",
    "none",
]
REVIEWER_PRIORITY = [
    "reject_runtime_scope_until_resolved",
    "reject_evidence_bundle_until_resolved",
    "manual_review_required",
    "no_action_required",
]


class BundleError(Exception):
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
    evidence_id: str = "",
    reference_type: str = "",
) -> dict:
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident,
        "reviewer_action": reviewer_action,
        "evidence_id": evidence_id,
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
        raise BundleError(
            make_issue(
                "unsafe_output_dir",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "output-dir must resolve under the repository root",
            )
        ) from exc
    if rel.parts[:2] != ALLOWED_OUTPUT_PREFIX:
        raise BundleError(
            make_issue(
                "unsafe_output_dir",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "output-dir must be tmp/phase10c-local-evidence-bundle or below it",
            )
        )
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _resolve_repo_relative(path_arg: str, *, allow_missing: bool) -> tuple[Path, str]:
    raw = Path(path_arg)
    candidate = raw if raw.is_absolute() else REPO_ROOT / raw
    if candidate.is_symlink():
        raise BundleError(
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
        raise BundleError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must resolve under the repository root: {path_arg}",
            )
        ) from exc
    if rel.parts and rel.parts[0] in FORBIDDEN_ROOTS:
        raise BundleError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must not resolve under {rel.parts[0]}/: {path_arg}",
            )
        )
    if rel.parts[:1] not in ALLOWED_REFERENCE_PREFIXES and rel.parts[:2] not in ALLOWED_REFERENCE_PREFIXES:
        raise BundleError(
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
        raise BundleError(
            make_issue(
                "missing_path",
                "warning",
                "evidence_review_required",
                "manual_review_required",
                f"path does not exist: {path_arg}",
            )
        )
    if not resolved.is_file():
        raise BundleError(
            make_issue(
                "unsafe_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"path must be a file: {path_arg}",
            )
        )
    return resolved, str(rel)


def _resolve_manifest_path(path_arg: str) -> Path:
    resolved = (REPO_ROOT / Path(path_arg)).resolve() if not Path(path_arg).is_absolute() else Path(path_arg).resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise BundleError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "manifest path must resolve under the repository root",
            )
        ) from exc
    if rel.parts and rel.parts[0] in FORBIDDEN_ROOTS:
        raise BundleError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                f"manifest path must not resolve under {rel.parts[0]}/",
            )
        )
    if resolved.is_symlink():
        raise BundleError(
            make_issue(
                "unsafe_manifest_path",
                "critical",
                "runtime_scope_violation",
                "reject_runtime_scope_until_resolved",
                "manifest path must not be a symlink",
            )
        )
    if not resolved.is_file():
        raise BundleError(
            make_issue(
                "manifest_missing",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                "manifest path does not exist",
            )
        )
    return resolved


def _load_manifest(manifest_path: Path) -> dict:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleError(
            make_issue(
                "invalid_manifest_json",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                f"manifest is not valid JSON: {exc}",
            )
        ) from exc
    if not isinstance(data, dict):
        raise BundleError(
            make_issue(
                "invalid_manifest_shape",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
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
                    "evidence_bundle_review_required",
                    "reject_evidence_bundle_until_resolved",
                    f"manifest is missing required field: {field}",
                )
            )
    if manifest.get("bundle_schema_version") != "phase10c.local_evidence_bundle.v1":
        issues.append(
            make_issue(
                "invalid_bundle_schema_version",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                "bundle_schema_version must be phase10c.local_evidence_bundle.v1",
            )
        )
    if not isinstance(manifest.get("evidence_references"), list):
        issues.append(
            make_issue(
                "invalid_evidence_references",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                "evidence_references must be a list",
            )
        )
    elif not manifest["evidence_references"]:
        issues.append(
            make_issue(
                "empty_evidence_references",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                "evidence_references must not be empty",
            )
        )


def _validate_secret_and_approval_guards(manifest: dict, issues: list[dict]) -> None:
    if _contains_secret_like_data(manifest):
        issues.append(
            make_issue(
                "secret_like_metadata",
                "critical",
                "privacy_review_required",
                "reject_evidence_bundle_until_resolved",
                "manifest contains secret-like, URL-like, or raw email data",
            )
        )
    truthy_approval = _collect_truthy_flags(manifest, APPROVAL_FLAG_KEYS)
    for key in truthy_approval:
        issues.append(
            make_issue(
                "approval_flag_present",
                "critical",
                "approval_boundary_review_required",
                "reject_evidence_bundle_until_resolved",
                f"approval flag must not be truthy: {key}",
            )
        )
    truthy_execute = _collect_truthy_flags(manifest, EXECUTION_FLAG_KEYS)
    for key in truthy_execute:
        incident = "approval_boundary_review_required" if key != "enforcement_enabled" else "runtime_scope_violation"
        issues.append(
            make_issue(
                "execution_intent_present",
                "critical",
                incident,
                "reject_runtime_scope_until_resolved" if key == "enforcement_enabled" else "reject_evidence_bundle_until_resolved",
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
                "reject_evidence_bundle_until_resolved",
                "approval_boundary_statement must declare not-approval semantics",
            )
        )


def _build_reference_record(reference: dict, issues: list[dict]) -> dict:
    evidence_id = str(reference.get("evidence_id", ""))
    for field in REFERENCE_REQUIRED_FIELDS:
        if field not in reference:
            issues.append(
                make_issue(
                    "evidence_reference_missing_field",
                    "critical",
                    "evidence_bundle_review_required",
                    "reject_evidence_bundle_until_resolved",
                    f"evidence reference is missing required field: {field}",
                    evidence_id=evidence_id,
                )
            )
    if reference.get("evidence_type") not in ALLOWED_EVIDENCE_TYPES:
        issues.append(
            make_issue(
                "invalid_evidence_type",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                f"unsupported evidence_type: {reference.get('evidence_type')}",
                evidence_id=evidence_id,
            )
        )
    if reference.get("evidence_phase") not in ALLOWED_EVIDENCE_PHASES:
        issues.append(
            make_issue(
                "invalid_evidence_phase",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                f"unsupported evidence_phase: {reference.get('evidence_phase')}",
                evidence_id=evidence_id,
            )
        )
    if _contains_secret_like_data(reference):
        issues.append(
            make_issue(
                "secret_like_evidence_metadata",
                "critical",
                "privacy_review_required",
                "reject_evidence_bundle_until_resolved",
                "evidence reference contains secret-like, URL-like, or raw email data",
                evidence_id=evidence_id,
            )
        )
    boundary = _normalize_text(str(reference.get("evidence_boundary_statement", "")))
    if not any(token in boundary for token in EVIDENCE_BOUNDARY_PHRASES):
        issues.append(
            make_issue(
                "evidence_boundary_statement_missing",
                "critical",
                "approval_boundary_review_required",
                "reject_evidence_bundle_until_resolved",
                "evidence_boundary_statement must declare not-approval semantics",
                evidence_id=evidence_id,
            )
        )

    record = dict(reference)
    path_arg = str(reference.get("evidence_path", ""))
    try:
        resolved, relative_path = _resolve_repo_relative(path_arg, allow_missing=True)
    except BundleError as exc:
        issue = dict(exc.issue)
        issue["evidence_id"] = evidence_id
        issues.append(issue)
        record["evidence_status"] = "invalid"
        record["relative_path"] = ""
        return record

    record["relative_path"] = relative_path
    if not resolved.exists():
        record["evidence_status"] = "missing"
        issues.append(
            make_issue(
                "evidence_missing",
                "warning",
                "evidence_review_required",
                "manual_review_required",
                f"safe evidence path is missing: {path_arg}",
                evidence_id=evidence_id,
            )
        )
        return record

    record["evidence_status"] = "present"
    record["size_bytes"] = resolved.stat().st_size
    record["sha256"] = _sha256_file(resolved)
    return record


def _build_optional_reference(field_name: str, payload: object, issues: list[dict]) -> dict | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        issues.append(
            make_issue(
                "invalid_optional_reference_shape",
                "critical",
                "evidence_bundle_review_required",
                "reject_evidence_bundle_until_resolved",
                f"{field_name} must be an object",
                reference_type=field_name,
            )
        )
        return {"reference_status": "invalid"}

    if _contains_secret_like_data(payload):
        issues.append(
            make_issue(
                "secret_like_optional_reference",
                "critical",
                "privacy_review_required",
                "reject_evidence_bundle_until_resolved",
                f"{field_name} contains secret-like, URL-like, or raw email data",
                reference_type=field_name,
            )
        )

    allowed_phrases = OPTIONAL_REFERENCE_RULES[field_name]["allowed_phrases"]
    boundary = _normalize_text(str(payload.get("reference_boundary_statement", "")))
    if not any(token in boundary for token in allowed_phrases):
        issues.append(
            make_issue(
                "optional_reference_boundary_missing",
                "critical",
                "approval_boundary_review_required",
                "reject_evidence_bundle_until_resolved",
                f"{field_name} must declare its non-approval boundary",
                reference_type=field_name,
            )
        )

    path_arg = str(payload.get("reference_path", ""))
    record = dict(payload)
    try:
        resolved, relative_path = _resolve_repo_relative(path_arg, allow_missing=True)
    except BundleError as exc:
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
    return record


def _select_incident(issues: list[dict]) -> str:
    if not issues:
        return "none"
    incidents = {issue["incident_classification"] for issue in issues}
    for incident in INCIDENT_PRIORITY:
        if incident in incidents:
            return incident
    return "evidence_bundle_review_required"


def _select_reviewer_action(issues: list[dict]) -> str:
    if not issues:
        return "no_action_required"
    actions = {issue["reviewer_action"] for issue in issues}
    for action in REVIEWER_PRIORITY:
        if action in actions:
            return action
    return "manual_review_required"


def _severity_counts(issues: list[dict]) -> dict:
    counts = {"info": 0, "warning": 0, "critical": 0}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return counts


def _determine_bundle_status(issues: list[dict]) -> str:
    if any(issue["severity"] == "critical" for issue in issues):
        return "not_built"
    if any(issue["severity"] == "warning" for issue in issues):
        return "built_with_warnings"
    return "built"


def _markdown_report(bundle: dict, output_dir: Path) -> str:
    lines = [
        "# Phase 10C Local Evidence Bundle",
        "",
        f"- phase10c_status: `{bundle['phase10c_status']}`",
        f"- bundle_status: `{bundle['bundle_status']}`",
        f"- bundle_id: `{bundle['bundle_id']}`",
        f"- evidence_reference_count: `{bundle['evidence_reference_count']}`",
        f"- present_evidence_count: `{bundle['present_evidence_count']}`",
        f"- missing_evidence_count: `{bundle['missing_evidence_count']}`",
        f"- invalid_evidence_count: `{bundle['invalid_evidence_count']}`",
        f"- bundle_hash: `{bundle['bundle_hash']}`",
        f"- reviewer_action: `{bundle['reviewer_action']}`",
        "",
        "## Issue Summary",
        "",
        f"- info: `{bundle['severity_counts']['info']}`",
        f"- warning: `{bundle['severity_counts']['warning']}`",
        f"- critical: `{bundle['severity_counts']['critical']}`",
        "",
        "## Output Paths",
        "",
        f"- JSON: `{output_dir / 'local-evidence-bundle.json'}`",
        f"- Markdown: `{output_dir / 'local-evidence-bundle.md'}`",
        "",
        "## Limitations",
        "",
    ]
    for item in bundle["limitations"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary Statements",
            "",
            "- local evidence bundle is not approval",
            "- evidence bundle validity is not approval",
            "- actor context is not authentication",
            "- RBAC advisory context is not enforcement",
            "- RBAC allow decision is not approval",
            "- approval remains Phase 7D selected-gate manual boundary",
        ]
    )
    if bundle["issues"]:
        lines.extend(["", "## Issues", ""])
        for issue in bundle["issues"]:
            lines.append(
                f"- [{issue['severity']}] {issue['issue_type']}: {issue['message']}"
            )
    return "\n".join(lines) + "\n"


def _build_bundle(manifest: dict) -> dict:
    issues: list[dict] = []
    evidence_records: list[dict] = []
    optional_contexts: dict[str, dict | None] = {}

    _validate_manifest_basics(manifest, issues)
    _validate_secret_and_approval_guards(manifest, issues)

    evidence_references = manifest.get("evidence_references")
    if isinstance(evidence_references, list):
        for reference in evidence_references:
            if not isinstance(reference, dict):
                issues.append(
                    make_issue(
                        "invalid_evidence_reference_shape",
                        "critical",
                        "evidence_bundle_review_required",
                        "reject_evidence_bundle_until_resolved",
                        "each evidence reference must be an object",
                    )
                )
                evidence_records.append({"evidence_status": "invalid"})
                continue
            evidence_records.append(_build_reference_record(reference, issues))

    for field_name in OPTIONAL_REFERENCE_RULES:
        optional_contexts[field_name] = _build_optional_reference(field_name, manifest.get(field_name), issues)

    severity_counts = _severity_counts(issues)
    bundle_status = _determine_bundle_status(issues)
    incident = _select_incident(issues)
    reviewer_action = _select_reviewer_action(issues)

    bundle = {
        **STATUS_BLOCK,
        "bundle_schema_version": str(manifest.get("bundle_schema_version", "")),
        "bundle_id": str(manifest.get("bundle_id", "")),
        "bundle_purpose": str(manifest.get("bundle_purpose", "")),
        "bundle_status": bundle_status,
        "evidence_reference_count": len(evidence_records),
        "present_evidence_count": sum(1 for item in evidence_records if item.get("evidence_status") == "present"),
        "missing_evidence_count": sum(1 for item in evidence_records if item.get("evidence_status") == "missing"),
        "invalid_evidence_count": sum(1 for item in evidence_records if item.get("evidence_status") == "invalid")
        + sum(1 for issue in issues if issue["severity"] == "critical" and issue["issue_type"].startswith("invalid_")),
        "optional_context_count": sum(1 for item in optional_contexts.values() if item is not None),
        "bundle_hash": "",
        "reviewer_action": reviewer_action,
        "reviewer_action_required": reviewer_action != "no_action_required",
        "incident_classification": incident,
        "severity_counts": severity_counts,
        "approval_boundary_statement": str(manifest.get("approval_boundary_statement", "")),
        "safety_statement": (
            "local-only derived evidence bundle prototype; deterministic JSON/Markdown only; "
            "safe missing evidence becomes warnings; unsafe paths, secrets, approval flags, "
            "execution intent, and enforcement intent are rejected"
        ),
        "limitations": list(manifest.get("limitations", LIMITATIONS if manifest.get("limitations") is None else []))
        if isinstance(manifest.get("limitations"), list) or manifest.get("limitations") is None
        else LIMITATIONS,
        "issues": issues,
        "evidence_references": evidence_records,
        "actor_context_reference": optional_contexts["actor_context_reference"],
        "rbac_advisory_context_reference": optional_contexts["rbac_advisory_context_reference"],
        "signature_context_reference": optional_contexts["signature_context_reference"],
        "approval_boundary_reference": optional_contexts["approval_boundary_reference"],
    }
    bundle["bundle_hash"] = _sha256_bytes(_canonical_json({**bundle, "bundle_hash": ""}).replace('"bundle_hash":""', '"bundle_hash":null').encode("utf-8"))
    clone = json.loads(json.dumps(bundle))
    clone.pop("bundle_hash", None)
    bundle["bundle_hash"] = _sha256_bytes(_canonical_json(clone).encode("utf-8"))
    return bundle


def _write_outputs(bundle: dict, output_dir: Path) -> None:
    json_path = output_dir / "local-evidence-bundle.json"
    markdown_path = output_dir / "local-evidence-bundle.md"
    json_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown_report(bundle, output_dir), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
    except BundleError as exc:
        print(exc.issue["message"], file=sys.stderr)
        return 1

    try:
        manifest_path = _resolve_manifest_path(args.manifest)
        manifest = _load_manifest(manifest_path)
        bundle = _build_bundle(manifest)
    except BundleError as exc:
        fallback_manifest = {
            "bundle_schema_version": "",
            "bundle_id": "",
            "bundle_purpose": "",
            "approval_boundary_statement": "",
            "evidence_references": [],
        }
        bundle = _build_bundle(fallback_manifest)
        bundle["bundle_status"] = "not_built"
        bundle["issues"] = [exc.issue]
        bundle["severity_counts"] = _severity_counts(bundle["issues"])
        bundle["incident_classification"] = _select_incident(bundle["issues"])
        bundle["reviewer_action"] = _select_reviewer_action(bundle["issues"])
        bundle["reviewer_action_required"] = True
        bundle["bundle_hash"] = _sha256_bytes(
            _canonical_json({k: v for k, v in bundle.items() if k != "bundle_hash"}).encode("utf-8")
        )
        _write_outputs(bundle, output_dir)
        print(exc.issue["message"], file=sys.stderr)
        return 1

    _write_outputs(bundle, output_dir)
    if bundle["bundle_status"] == "not_built":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
