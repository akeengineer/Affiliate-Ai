#!/usr/bin/env python3
"""Phase 9C Local Operator Registry Prototype.

Local-only, metadata-only, evidence-only. Reads a local JSON file of conceptual
Phase 9B actor_metadata records, validates a local subset of that schema,
optionally builds a deterministic local registry file, and emits local registry
reports under tmp/phase9c-local-operator-registry/.

This prototype is NOT authentication, NOT RBAC, NOT login, NOT a session store,
and NOT a user database. A registry record is attribution metadata only. Valid
actor metadata is not approval, registry presence is not approval, and approval
remains the Phase 7D selected-gate manual boundary.

Standard library only. No network, no database, no subprocess, no shell
execution, no key generation, no vault access, no wrapper/primitive calls, and
no mutation outside the tmp output directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = "tmp/phase9c-local-operator-registry"
ALLOWED_OUTPUT_PREFIX = ("tmp", "phase9c-local-operator-registry")
FORBIDDEN_INPUT_ROOTS = {"vault", "docs", "scripts", "codex", ".git"}

STATUS_BLOCK = {
    "phase9c_status": "success",
    "phase7d_runtime_readiness": "implemented_manual_gate",
    "durable_audit_store_status": "phase8_final_acceptance_pack",
    "identity_boundary_status": "design_only",
    "actor_metadata_schema_status": "design_only",
    "actor_metadata_runtime_status": "local_registry_prototype",
    "local_operator_registry_status": "prototype_local_only",
    "identity_runtime_status": "not_implemented",
    "rbac_runtime_status": "not_implemented",
    "authentication_runtime_status": "not_implemented",
    "operator_identity_assurance_status": "unauthenticated_or_operator_declared",
    "signing_implementation_status": "prototype_local_only",
    "signature_runtime_status": "local_prototype",
    "signature_verifier_runtime_status": "local_prototype",
    "key_management_runtime_status": "not_implemented",
    "phase9_branch_workflow": "enabled",
}

APPROVAL_BOUNDARY_STATEMENT = (
    "local operator registry is not authentication; registry presence is not "
    "approval; valid actor metadata is not approval; approval remains Phase 7D "
    "selected-gate manual boundary"
)
SAFETY_STATEMENT = (
    "metadata-only, evidence-only local prototype; no authentication, no RBAC, "
    "no login, no session, no user store, no backend/API/database, no vault "
    "write, no primitive execution"
)
LIMITATIONS = [
    "local prototype only",
    "no authentication",
    "no RBAC",
    "no login",
    "no session runtime",
    "no user store",
    "no backend/API/database",
    "no key custody",
    "no strong non-repudiation",
    "no production deployment",
]

REQUIRED_FIELDS = [
    "actor_schema_version",
    "actor_id",
    "actor_type",
    "actor_display_label",
    "actor_role_labels",
    "actor_identity_assurance",
    "actor_identity_source",
    "actor_session_reference",
    "actor_attestation",
    "actor_action_scope",
    "identity_evidence_references",
    "actor_timestamp_utc",
    "privacy_classification",
    "approval_boundary_statement",
]
MISSING_ISSUE_TYPE = {
    "actor_schema_version": "actor_schema_version_missing",
    "actor_id": "actor_id_missing",
    "actor_type": "actor_type_missing",
    "actor_identity_assurance": "actor_identity_assurance_missing",
    "approval_boundary_statement": "approval_boundary_statement_missing",
}

ALLOWED_SCHEMA_VERSION = "phase9b.actor_metadata.v1"
ALLOWED_ACTOR_TYPES = {
    "human_operator", "reviewer", "signer", "key_owner", "key_custodian",
    "security_owner", "system_owner", "emergency_revocation_authority",
    "system_process", "test_fixture", "automation_placeholder",
}
ALLOWED_ROLE_LABELS = {
    "operator", "reviewer", "signer", "key_owner", "key_custodian",
    "security_owner", "system_owner", "emergency_revocation_authority",
    "automation", "test",
}
ALLOWED_IDENTITY_ASSURANCE = {
    "unauthenticated", "operator_declared", "local_machine_observed",
    "local_config_verified", "repository_config_verified",
    "external_identity_verified", "enterprise_identity_verified",
    "hardware_backed",
}
ALLOWED_IDENTITY_SOURCE = {
    "none", "terminal_user_label", "git_user_config",
    "environment_operator_label", "local_config_operator_label",
    "repository_operator_registry", "signed_identity_assertion",
    "external_idp_claim", "enterprise_directory_claim",
    "hardware_key_attestation",
}
ALLOWED_ACTION_SCOPES = {
    "export_pack_generation", "export_integrity_verification",
    "local_signature_creation", "local_signature_verification",
    "incident_review", "final_acceptance_review",
    "selected_gate_manual_approval", "primitive_execution",
    "key_governance_review", "test_fixture_generation",
}

APPROVAL_BOUNDARY_PHRASES = (
    "actor metadata is not approval",
    "actor attribution is not approval",
    "approval remains phase 7d selected-gate manual boundary",
)
APPROVAL_FLAG_KEYS = (
    "approved", "is_approved", "approval_granted", "auto_approve",
    "approve_all", "next_gate", "execute",
)
PRIMITIVE_INTENT_KEYS = (
    "execute_primitive", "primitive_execution_intent", "run_primitive",
)

ACTOR_ID_RE = re.compile(r"^actor_[a-z0-9_-]{3,64}$")
URL_SCHEME_RE = re.compile(r"[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.IGNORECASE)
SECRET_MARKERS = (
    "begin private key",
    "begin rsa private key",
    "begin openssh private key",
    "api_key=",
    "secret=",
    "token=",
    "password=",
    "aws_secret_access_key",
    "ssh-rsa",
    "access_token",
    "id_token",
    "refresh_token",
    "affiliate_phase8l_prototype_key",
)

# issue_type -> (severity, incident_classification, reviewer_action)
REJECT = "reject_actor_metadata_until_resolved"
REVIEW = "manual_review_required"
NOOP = "no_action_required"
ISSUE_SPEC = {
    "input_missing": ("critical", "actor_metadata_not_available", REJECT),
    "invalid_json": ("critical", "actor_metadata_schema_failure", REJECT),
    "invalid_input_shape": ("critical", "actor_metadata_schema_failure", REJECT),
    "unsafe_path": ("critical", "actor_metadata_not_available", REJECT),
    "actor_schema_version_missing": ("warning", "actor_metadata_schema_failure", REJECT),
    "actor_id_missing": ("warning", "actor_metadata_schema_failure", REJECT),
    "actor_id_invalid_format": ("warning", "actor_metadata_schema_failure", REJECT),
    "actor_type_missing": ("warning", "actor_metadata_schema_failure", REJECT),
    "actor_type_unknown": ("warning", "actor_metadata_schema_failure", REJECT),
    "actor_identity_assurance_missing": ("warning", "identity_assurance_review_required", REJECT),
    "actor_identity_assurance_insufficient": ("warning", "identity_assurance_review_required", REJECT),
    "actor_identity_source_unknown": ("warning", "identity_policy_review_required", REJECT),
    "actor_role_label_unknown": ("warning", "identity_policy_review_required", REJECT),
    "actor_scope_invalid": ("warning", "actor_scope_review_required", REJECT),
    "actor_session_reference_invalid": ("warning", "actor_metadata_schema_failure", REJECT),
    "identity_evidence_reference_invalid": ("warning", "actor_metadata_schema_failure", REJECT),
    "identity_metadata_contains_secret": ("critical", "privacy_review_required", REJECT),
    "identity_metadata_contains_unnecessary_pii": ("warning", "privacy_review_required", REJECT),
    "approval_boundary_statement_missing": ("warning", "identity_policy_review_required", REJECT),
    "approval_flag_present": ("critical", "actor_metadata_schema_failure", REJECT),
    "primitive_execution_intent_present": ("critical", "actor_metadata_schema_failure", REJECT),
    "duplicate_actor_id": ("warning", "actor_metadata_schema_failure", REVIEW),
    "field_missing": ("warning", "actor_metadata_schema_failure", REJECT),
}
INCIDENT_PRIORITY = [
    "privacy_review_required",
    "actor_metadata_schema_failure",
    "identity_assurance_review_required",
    "identity_policy_review_required",
    "actor_scope_review_required",
    "actor_metadata_not_available",
    "none",
]


class RegistryError(Exception):
    """Input-level failure carrying an issue_type."""

    def __init__(self, issue_type: str, message: str) -> None:
        super().__init__(message)
        self.issue_type = issue_type
        self.message = message


def make_issue(issue_type: str, actor_id: str, message: str) -> dict:
    severity, incident, reviewer = ISSUE_SPEC.get(
        issue_type, ("warning", "actor_metadata_schema_failure", REJECT)
    )
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident,
        "reviewer_action": reviewer,
        "actor_id": actor_id,
        "message": message,
    }


def _iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _scan_secret(record: dict, actor_id: str) -> list:
    issues = []
    for text in _iter_strings(record):
        low = text.lower()
        if any(marker in low for marker in SECRET_MARKERS):
            issues.append(make_issue(
                "identity_metadata_contains_secret", actor_id,
                "actor metadata contains a secret-like marker",
            ))
            break
    for text in _iter_strings(record):
        if URL_SCHEME_RE.search(text):
            issues.append(make_issue(
                "identity_metadata_contains_secret", actor_id,
                "actor metadata contains an external URL scheme",
            ))
            break
    return issues


def _validate_record(record) -> tuple:
    """Return (actor_id, issues) for one record."""
    if not isinstance(record, dict):
        return "", [make_issue(
            "invalid_input_shape", "",
            "actor metadata record must be a JSON object",
        )]

    actor_id_raw = record.get("actor_id", "")
    actor_id = actor_id_raw if isinstance(actor_id_raw, str) else ""
    issues = []

    # Required field presence.
    for field in REQUIRED_FIELDS:
        if field not in record:
            issue_type = MISSING_ISSUE_TYPE.get(field, "field_missing")
            issues.append(make_issue(issue_type, actor_id, f"missing required field: {field}"))

    # actor_schema_version.
    if "actor_schema_version" in record and record.get("actor_schema_version") != ALLOWED_SCHEMA_VERSION:
        issues.append(make_issue(
            "actor_schema_version_missing", actor_id,
            f"actor_schema_version must be {ALLOWED_SCHEMA_VERSION}",
        ))

    # actor_id format.
    if "actor_id" in record:
        if not isinstance(actor_id_raw, str) or not actor_id:
            issues.append(make_issue("actor_id_missing", actor_id, "actor_id must be a non-empty string"))
        elif "approve" in actor_id.lower() or "approval" in actor_id.lower():
            issues.append(make_issue("actor_id_invalid_format", actor_id, "actor_id must not be approval-like"))
        elif not ACTOR_ID_RE.match(actor_id):
            issues.append(make_issue(
                "actor_id_invalid_format", actor_id,
                "actor_id must match ^actor_[a-z0-9_-]{3,64}$ with no whitespace, @, or URL scheme",
            ))

    # actor_type.
    if "actor_type" in record and record.get("actor_type") not in ALLOWED_ACTOR_TYPES:
        issues.append(make_issue("actor_type_unknown", actor_id, "actor_type is not an allowed value"))

    # actor_role_labels.
    if "actor_role_labels" in record:
        roles = record.get("actor_role_labels")
        if not isinstance(roles, list) or any(r not in ALLOWED_ROLE_LABELS for r in roles):
            issues.append(make_issue("actor_role_label_unknown", actor_id, "actor_role_labels contains an unknown label"))

    # actor_identity_assurance.
    if "actor_identity_assurance" in record and record.get("actor_identity_assurance") not in ALLOWED_IDENTITY_ASSURANCE:
        issues.append(make_issue("actor_identity_assurance_insufficient", actor_id, "actor_identity_assurance is not an allowed value"))

    # actor_identity_source.
    if "actor_identity_source" in record and record.get("actor_identity_source") not in ALLOWED_IDENTITY_SOURCE:
        issues.append(make_issue("actor_identity_source_unknown", actor_id, "actor_identity_source is not an allowed value"))

    # actor_action_scope.
    if "actor_action_scope" in record:
        scope = record.get("actor_action_scope")
        category = scope.get("action_category") if isinstance(scope, dict) else None
        if category not in ALLOWED_ACTION_SCOPES:
            issues.append(make_issue("actor_scope_invalid", actor_id, "actor_action_scope.action_category is invalid"))

    # actor_session_reference (optional value, may be null or object).
    if "actor_session_reference" in record:
        sref = record.get("actor_session_reference")
        if sref is not None and not isinstance(sref, dict):
            issues.append(make_issue("actor_session_reference_invalid", actor_id, "actor_session_reference must be null or an object"))

    # identity_evidence_references (list of objects).
    if "identity_evidence_references" in record:
        refs = record.get("identity_evidence_references")
        if not isinstance(refs, list) or any(not isinstance(r, dict) for r in refs):
            issues.append(make_issue("identity_evidence_reference_invalid", actor_id, "identity_evidence_references must be a list of objects"))

    # approval_boundary_statement phrase.
    if "approval_boundary_statement" in record:
        stmt = record.get("approval_boundary_statement")
        stmt_low = stmt.lower() if isinstance(stmt, str) else ""
        if not any(phrase in stmt_low for phrase in APPROVAL_BOUNDARY_PHRASES):
            issues.append(make_issue("approval_boundary_statement_missing", actor_id, "approval_boundary_statement must include an approval boundary phrase"))

    # Approval flags.
    for key in APPROVAL_FLAG_KEYS:
        if record.get(key):
            issues.append(make_issue("approval_flag_present", actor_id, f"approval flag '{key}' must not be truthy"))
    for key in PRIMITIVE_INTENT_KEYS:
        if record.get(key):
            issues.append(make_issue("primitive_execution_intent_present", actor_id, f"primitive execution intent '{key}' is not allowed"))

    # Raw email as unnecessary PII (outside actor_id, which already forbids '@').
    for field, value in record.items():
        if field == "actor_id":
            continue
        for text in _iter_strings(value):
            if EMAIL_RE.search(text):
                issues.append(make_issue("identity_metadata_contains_unnecessary_pii", actor_id, "actor metadata contains a raw email address"))
                break
        else:
            continue
        break

    # Secret / URL scan.
    issues.extend(_scan_secret(record, actor_id))

    return actor_id, issues


def _resolve_input(input_arg: str) -> Path:
    raw = Path(input_arg)
    if raw.is_symlink():
        raise RegistryError("unsafe_path", "input path must not be a symlink")
    resolved = raw.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise RegistryError("unsafe_path", "input path must resolve under the repository root")
    if rel.parts and rel.parts[0] in FORBIDDEN_INPUT_ROOTS:
        raise RegistryError("unsafe_path", f"input path must not be under {rel.parts[0]}/")
    if not resolved.is_file():
        raise RegistryError("input_missing", "input path does not exist")
    return resolved


def _resolve_output_dir(output_arg: str) -> Path:
    resolved = Path(output_arg).resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise RegistryError("unsafe_path", "output-dir must resolve under the repository root")
    if rel.parts[:2] != ALLOWED_OUTPUT_PREFIX:
        raise RegistryError("unsafe_path", "output-dir must be tmp/phase9c-local-operator-registry or below it")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _read_records(input_path: Path) -> list:
    try:
        text = input_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise RegistryError("input_missing", f"cannot read input: {exc}")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RegistryError("invalid_json", f"input is not valid JSON: {exc}")
    if isinstance(raw, dict):
        if isinstance(raw.get("actor_metadata"), list):
            return list(raw["actor_metadata"])
        return [raw]
    if isinstance(raw, list):
        return list(raw)
    raise RegistryError("invalid_input_shape", "input must be a JSON object or array")


def _severity_counts(issues: list) -> dict:
    counts = {"info": 0, "warning": 0, "critical": 0}
    for issue in issues:
        sev = issue.get("severity", "warning")
        counts[sev] = counts.get(sev, 0) + 1
    return counts


def _overall_incident(issues: list) -> str:
    present = {issue["incident_classification"] for issue in issues}
    for incident in INCIDENT_PRIORITY:
        if incident in present:
            return incident
    return "none"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _report_markdown(payload: dict) -> str:
    lines = [
        "# Phase 9C Local Operator Registry Report",
        "",
        f"- phase9c_status: {payload['phase9c_status']}",
        f"- registry_status: {payload['registry_status']}",
        f"- validation_status: {payload['validation_status']}",
        f"- registry_record_count: {payload['registry_record_count']}",
        f"- valid_record_count: {payload['valid_record_count']}",
        f"- invalid_record_count: {payload['invalid_record_count']}",
        f"- duplicate_actor_count: {payload['duplicate_actor_count']}",
        f"- failure_count: {payload['failure_count']}",
        f"- reviewer_action: {payload['reviewer_action']}",
        f"- incident_classification: {payload['incident_classification']}",
        "",
        "## Issue summary",
        "",
    ]
    if payload["issues"]:
        for issue in payload["issues"]:
            lines.append(
                f"- [{issue['severity']}] {issue['issue_type']} "
                f"(actor_id={issue['actor_id'] or 'n/a'}): {issue['message']}"
            )
    else:
        lines.append("- no issues")
    lines += [
        "",
        "## Output paths",
        "",
    ]
    for name, value in payload["output_paths"].items():
        lines.append(f"- {name}: {value}")
    lines += [
        "",
        "## Limitations",
        "",
    ]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Approval boundary",
        "",
        "- local operator registry is not authentication",
        "- registry presence is not approval",
        "- valid actor metadata is not approval",
        "- approval remains Phase 7D selected-gate manual boundary",
        "",
    ]
    return "\n".join(lines)


def _base_payload() -> dict:
    payload = dict(STATUS_BLOCK)
    payload["approval_boundary_statement"] = APPROVAL_BOUNDARY_STATEMENT
    payload["safety_statement"] = SAFETY_STATEMENT
    payload["limitations"] = list(LIMITATIONS)
    return payload


def _emit_error_report(output_dir: Path, issue: dict) -> None:
    payload = _base_payload()
    payload.update({
        "registry_status": "not_built",
        "validation_status": "invalid",
        "registry_record_count": 0,
        "valid_record_count": 0,
        "invalid_record_count": 0,
        "duplicate_actor_count": 0,
        "failure_count": 1,
        "severity_counts": _severity_counts([issue]),
        "reviewer_action": issue["reviewer_action"],
        "reviewer_action_required": True,
        "incident_classification": issue["incident_classification"],
        "issues": [issue],
        "output_paths": {},
    })
    report_json = output_dir / "operator-registry-report.json"
    report_md = output_dir / "operator-registry-report.md"
    payload["output_paths"] = {
        "operator_registry_report_json": str(report_json.relative_to(REPO_ROOT)),
        "operator_registry_report_md": str(report_md.relative_to(REPO_ROOT)),
    }
    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")


def run_validate_or_build(input_arg: str, output_dir: Path, mode: str) -> int:
    input_path = _resolve_input(input_arg)
    records = _read_records(input_path)

    all_issues = []
    valid_records = []
    invalid_count = 0
    for record in records:
        actor_id, issues = _validate_record(record)
        record_invalid = any(i["issue_type"] != "duplicate_actor_id" for i in issues)
        all_issues.extend(issues)
        if record_invalid:
            invalid_count += 1
        else:
            valid_records.append((actor_id, record))

    # Deduplicate valid records by actor_id (keep first deterministically).
    seen = set()
    deduped = []
    duplicate_count = 0
    for actor_id, record in valid_records:
        if actor_id in seen:
            duplicate_count += 1
            all_issues.append(make_issue("duplicate_actor_id", actor_id, "duplicate actor_id kept first record only"))
        else:
            seen.add(actor_id)
            deduped.append(record)

    valid_count = len(valid_records)
    registry_records = deduped

    if invalid_count > 0:
        validation_status = "invalid"
        registry_status = "not_built"
        reviewer_action = REJECT
        exit_code = 1
    elif duplicate_count > 0:
        validation_status = "warning"
        registry_status = "built_with_warnings" if mode == "build" else "not_built"
        reviewer_action = REVIEW
        exit_code = 0
    else:
        validation_status = "valid"
        registry_status = "built" if mode == "build" else "not_built"
        reviewer_action = NOOP
        exit_code = 0

    payload = _base_payload()
    payload.update({
        "registry_status": registry_status,
        "validation_status": validation_status,
        "registry_record_count": len(registry_records),
        "valid_record_count": valid_count,
        "invalid_record_count": invalid_count,
        "duplicate_actor_count": duplicate_count,
        "failure_count": len(all_issues),
        "severity_counts": _severity_counts(all_issues),
        "reviewer_action": reviewer_action,
        "reviewer_action_required": reviewer_action != NOOP,
        "incident_classification": _overall_incident(all_issues),
        "issues": all_issues,
    })

    registry_json = output_dir / "operator-registry.json"
    report_json = output_dir / "operator-registry-report.json"
    report_md = output_dir / "operator-registry-report.md"
    output_paths = {
        "operator_registry_report_json": str(report_json.relative_to(REPO_ROOT)),
        "operator_registry_report_md": str(report_md.relative_to(REPO_ROOT)),
    }

    wrote_registry = mode == "build" and registry_status in ("built", "built_with_warnings")
    if wrote_registry:
        registry_payload = _base_payload()
        registry_payload.update({
            "registry_status": registry_status,
            "registry_record_count": len(registry_records),
            "actor_registry": registry_records,
        })
        _write_json(registry_json, registry_payload)
        output_paths["operator_registry_json"] = str(registry_json.relative_to(REPO_ROOT))

    payload["output_paths"] = output_paths
    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")
    return exit_code


def run_list_or_report(output_dir: Path, mode: str) -> int:
    registry_json = output_dir / "operator-registry.json"
    if not registry_json.is_file():
        issue = make_issue("input_missing", "", "operator-registry.json not found; run build first")
        _emit_error_report(output_dir, issue)
        return 1

    registry_payload = json.loads(registry_json.read_text(encoding="utf-8"))
    records = registry_payload.get("actor_registry", [])

    payload = _base_payload()
    payload.update({
        "registry_status": "loaded",
        "validation_status": "not_run",
        "registry_record_count": len(records),
        "valid_record_count": len(records),
        "invalid_record_count": 0,
        "duplicate_actor_count": 0,
        "failure_count": 0,
        "severity_counts": _severity_counts([]),
        "reviewer_action": NOOP,
        "reviewer_action_required": False,
        "incident_classification": "none",
        "issues": [],
    })

    if mode == "list":
        listing = [
            {
                "actor_id": r.get("actor_id", ""),
                "actor_type": r.get("actor_type", ""),
                "actor_role_labels": r.get("actor_role_labels", []),
                "actor_identity_assurance": r.get("actor_identity_assurance", ""),
            }
            for r in records
        ]
        list_json = output_dir / "operator-registry-list.json"
        list_md = output_dir / "operator-registry-list.md"
        payload["actor_listing"] = listing
        payload["output_paths"] = {
            "operator_registry_list_json": str(list_json.relative_to(REPO_ROOT)),
            "operator_registry_list_md": str(list_md.relative_to(REPO_ROOT)),
        }
        _write_json(list_json, payload)
        md_lines = [
            "# Phase 9C Local Operator Registry List",
            "",
            f"- registry_record_count: {len(records)}",
            "",
            "## Registered actors",
            "",
        ]
        if listing:
            for entry in listing:
                md_lines.append(f"- {entry['actor_id']} ({entry['actor_type']})")
        else:
            md_lines.append("- no actors")
        md_lines += [
            "",
            "- local operator registry is not authentication",
            "- registry presence is not approval",
            "- valid actor metadata is not approval",
            "- approval remains Phase 7D selected-gate manual boundary",
            "",
        ]
        list_md.write_text("\n".join(md_lines), encoding="utf-8")
    else:  # report
        report_json = output_dir / "operator-registry-report.json"
        report_md = output_dir / "operator-registry-report.md"
        payload["output_paths"] = {
            "operator_registry_report_json": str(report_json.relative_to(REPO_ROOT)),
            "operator_registry_report_md": str(report_md.relative_to(REPO_ROOT)),
        }
        _write_json(report_json, payload)
        report_md.write_text(_report_markdown(payload), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Phase 9C Local Operator Registry Prototype")
    parser.add_argument("--input", default=None, help="path to a local actor_metadata JSON file")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", choices=("validate", "build", "list", "report"), default="build")
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
    except RegistryError as exc:
        print(f"phase9c error: {exc.issue_type}: {exc.message}", file=sys.stderr)
        return 2

    if args.mode in ("validate", "build"):
        if not args.input:
            issue = make_issue("input_missing", "", "--input is required for validate/build")
            _emit_error_report(output_dir, issue)
            print("phase9c error: input_missing: --input is required", file=sys.stderr)
            return 1
        try:
            return run_validate_or_build(args.input, output_dir, args.mode)
        except RegistryError as exc:
            issue = make_issue(exc.issue_type, "", exc.message)
            _emit_error_report(output_dir, issue)
            print(f"phase9c error: {exc.issue_type}: {exc.message}", file=sys.stderr)
            return 1

    return run_list_or_report(output_dir, args.mode)


if __name__ == "__main__":
    sys.exit(main())
