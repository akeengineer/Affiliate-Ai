#!/usr/bin/env python3
"""Phase 9F Local RBAC Policy Prototype.

Local-only, advisory-only, metadata-only, evidence-only. Reads a local RBAC
policy JSON and a local subject/resource/action request JSON, optionally
consults an existing Phase 9C operator registry and/or Phase 9D actor
attribution report as advisory context, evaluates advisory RBAC eligibility
deterministically, and writes an advisory decision report under
tmp/phase9f-local-rbac-policy/.

This prototype is NOT enforcement, NOT authentication, NOT RBAC runtime
permission gating, NOT login, NOT a session store, and NOT a user database. An
advisory allow decision is not approval, an advisory deny decision is not an
incident by itself, and the advisory report is evidence only. Approval remains
the Phase 7D selected-gate manual boundary.

Standard library only. No network, no database, no subprocess, no shell
execution, no key generation, no vault access, no wrapper/primitive calls, no
Phase 8/9C/9D runtime calls, and no mutation outside the tmp output directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = "tmp/phase9f-local-rbac-policy"
ALLOWED_OUTPUT_PREFIX = ("tmp", "phase9f-local-rbac-policy")
FORBIDDEN_INPUT_ROOTS = {"vault", "docs", "scripts", "codex", ".git"}

REGISTRY_CONTAINERS = ("actor_metadata", "actor_registry", "records", "registry_records", "operators")

STATUS_BLOCK = {
    "phase9f_status": "success",
    "phase7d_runtime_readiness": "implemented_manual_gate",
    "durable_audit_store_status": "phase8_final_acceptance_pack",
    "identity_boundary_status": "design_only",
    "actor_metadata_schema_status": "design_only",
    "actor_metadata_runtime_status": "local_registry_prototype",
    "local_operator_registry_status": "prototype_local_only",
    "actor_attribution_status": "local_report_prototype",
    "rbac_design_status": "design_only",
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
    "phase9_branch_workflow": "enabled",
}

APPROVAL_BOUNDARY_STATEMENT = (
    "local RBAC policy prototype is not enforcement; RBAC allow decision is not "
    "approval; RBAC eligibility is not approval; RBAC advisory report is "
    "evidence only; approval remains Phase 7D selected-gate manual boundary"
)
SAFETY_STATEMENT = (
    "advisory-only, metadata-only, local-only, evidence-only prototype; no "
    "enforcement, no authentication, no RBAC runtime permission gating, no "
    "login, no session, no user store, no backend/API/database, no vault "
    "write, no primitive execution"
)
LIMITATIONS = [
    "local advisory prototype only",
    "no RBAC enforcement",
    "no production policy engine",
    "no authentication",
    "no login",
    "no session runtime",
    "no user store",
    "no enterprise identity",
    "no governed key custody",
    "no strong non-repudiation",
    "no backend/API/database",
    "no production deployment",
]

REQUIRED_POLICY_FIELDS = (
    "policy_version", "policy_status", "policy_mode", "permissions",
    "approval_boundary_statement",
)
REQUIRED_PERMISSION_FIELDS = (
    "permission_id", "effect", "roles", "resources", "actions",
    "required_identity_assurance", "obligations", "approval_boundary_statement",
)
REQUIRED_REQUEST_FIELDS = ("request_id", "subject", "resource", "action", "approval_boundary_statement")
REQUIRED_SUBJECT_FIELDS = (
    "subject_id", "subject_actor_id", "subject_actor_type",
    "subject_identity_assurance", "subject_identity_source", "subject_role_labels",
)
REQUIRED_RESOURCE_FIELDS = ("resource_type", "resource_id")

ALLOWED_POLICY_VERSION = "phase9f.local_rbac_policy.v1"
ALLOWED_POLICY_STATUS = "local_advisory_prototype"
ALLOWED_POLICY_MODE = "advisory_only"
ALLOWED_EFFECTS = {"allow", "deny"}

ALLOWED_RESOURCE_TYPES = {
    "product_candidate", "scoring_report", "weekly_report", "promotion_gate",
    "manual_decision", "finalization_decision", "phase7d_selected_gate",
    "audit_store_record", "audit_store_report", "audit_export_pack",
    "export_integrity_report", "detached_signature_envelope",
    "signature_verifier_report", "signature_incident_runbook",
    "final_acceptance_pack", "actor_registry", "actor_attribution_report",
    "rbac_policy", "test_fixture",
}
ALLOWED_ACTIONS = {
    "read", "list", "build_report", "validate", "export",
    "sign_local_prototype", "verify_local_prototype", "review", "annotate",
    "register_actor", "attribute_actor", "approve_selected_gate",
    "execute_primitive", "manage_key_governance_metadata",
    "manage_policy_design", "test_generate_fixture",
}
IDENTITY_ASSURANCE_ORDER = [
    "unauthenticated", "operator_declared", "local_machine_observed",
    "local_config_verified", "repository_config_verified",
    "external_identity_verified", "enterprise_identity_verified",
    "hardware_backed",
]
ALLOWED_IDENTITY_ASSURANCE = set(IDENTITY_ASSURANCE_ORDER)

APPROVAL_BOUNDARY_PHRASES = (
    "rbac policy is not approval",
    "rbac eligibility is not approval",
    "rbac advisory decision is not approval",
    "approval remains phase 7d selected-gate manual boundary",
)
APPROVAL_FLAG_KEYS = (
    "approved", "is_approved", "approval_granted", "auto_approve",
    "approve_all", "next_gate", "execute",
)
PRIMITIVE_INTENT_KEYS = (
    "execute_primitive_intent", "primitive_execution_intent", "run_primitive",
)

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

REJECT_POLICY = "reject_rbac_policy_until_resolved"
REJECT_ACTION = "reject_action_until_resolved"
REVIEW = "manual_review_required"
NOOP = "no_action_required"

ISSUE_SPEC = {
    "policy_missing": ("critical", "rbac_decision_not_available", REJECT_POLICY),
    "request_missing": ("critical", "rbac_decision_not_available", REJECT_ACTION),
    "invalid_policy_json": ("critical", "rbac_policy_review_required", REJECT_POLICY),
    "invalid_request_json": ("critical", "rbac_decision_not_available", REJECT_ACTION),
    "invalid_policy_shape": ("critical", "rbac_policy_review_required", REJECT_POLICY),
    "invalid_request_shape": ("critical", "rbac_decision_not_available", REJECT_ACTION),
    "policy_version_missing": ("warning", "rbac_policy_review_required", REJECT_POLICY),
    "policy_version_incompatible": ("warning", "rbac_policy_review_required", REJECT_POLICY),
    "policy_mode_invalid": ("critical", "rbac_policy_review_required", REJECT_POLICY),
    "enforcement_enabled_present": ("critical", "approval_boundary_review_required", REJECT_POLICY),
    "permission_missing": ("warning", "rbac_policy_review_required", REJECT_POLICY),
    "permission_unknown": ("warning", "rbac_policy_review_required", REJECT_POLICY),
    "subject_missing": ("critical", "rbac_decision_not_available", REJECT_ACTION),
    "subject_unknown": ("warning", "actor_scope_review_required", REVIEW),
    "subject_identity_assurance_insufficient": ("warning", "identity_assurance_review_required", REVIEW),
    "role_missing": ("warning", "rbac_policy_review_required", REJECT_POLICY),
    "role_unknown": ("warning", "actor_scope_review_required", REVIEW),
    "resource_unknown": ("warning", "actor_scope_review_required", REJECT_ACTION),
    "action_unknown": ("warning", "actor_scope_review_required", REJECT_ACTION),
    "obligation_unmet": ("warning", "approval_boundary_review_required", REVIEW),
    "approval_boundary_required": ("critical", "approval_boundary_review_required", REJECT_ACTION),
    "privacy_review_required": ("critical", "privacy_review_required", REJECT_ACTION),
    "primitive_execution_blocked": ("critical", "primitive_execution_blocked", REJECT_ACTION),
    "next_gate_blocked": ("critical", "next_gate_blocked", REJECT_ACTION),
    "approval_flag_present": ("critical", "approval_boundary_review_required", REJECT_ACTION),
    "unsafe_path": ("critical", "rbac_decision_not_available", REJECT_ACTION),
}
INCIDENT_PRIORITY = [
    "privacy_review_required",
    "approval_boundary_review_required",
    "primitive_execution_blocked",
    "next_gate_blocked",
    "rbac_policy_review_required",
    "identity_assurance_review_required",
    "actor_scope_review_required",
    "rbac_decision_not_available",
    "none",
]
REVIEWER_PRIORITY = [REJECT_ACTION, REJECT_POLICY, REVIEW, NOOP]


class RbacError(Exception):
    def __init__(self, issue_type: str, message: str) -> None:
        super().__init__(message)
        self.issue_type = issue_type
        self.message = message


def make_issue(issue_type, message, subject_id="", resource_id="", action="", permission_id="") -> dict:
    severity, incident, reviewer = ISSUE_SPEC.get(
        issue_type, ("warning", "rbac_policy_review_required", REJECT_POLICY)
    )
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident,
        "reviewer_action": reviewer,
        "subject_id": subject_id,
        "resource_id": resource_id,
        "action": action,
        "permission_id": permission_id,
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


def _has_secret(mapping) -> bool:
    for text in _iter_strings(mapping):
        low = text.lower()
        if any(marker in low for marker in SECRET_MARKERS):
            return True
        if URL_SCHEME_RE.search(text):
            return True
    return False


def _has_email(mapping) -> bool:
    for text in _iter_strings(mapping):
        if EMAIL_RE.search(text):
            return True
    return False


def _approval_flag_issues(mapping, **ids) -> list:
    issues = []
    if not isinstance(mapping, dict):
        return issues
    for key in APPROVAL_FLAG_KEYS:
        if mapping.get(key):
            issues.append(make_issue("approval_flag_present", f"approval flag '{key}' must not be truthy", **ids))
    for key in PRIMITIVE_INTENT_KEYS:
        if mapping.get(key):
            issues.append(make_issue("primitive_execution_blocked", f"primitive execution intent '{key}' is not allowed", **ids))
    return issues


def _resolve_input(path_arg: str, missing_type: str) -> Path:
    raw = Path(path_arg)
    if raw.is_symlink():
        raise RbacError("unsafe_path", f"input path must not be a symlink: {path_arg}")
    resolved = raw.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise RbacError("unsafe_path", f"input path must resolve under the repository root: {path_arg}")
    if rel.parts and rel.parts[0] in FORBIDDEN_INPUT_ROOTS:
        raise RbacError("unsafe_path", f"input path must not be under {rel.parts[0]}/")
    if not resolved.is_file():
        raise RbacError(missing_type, f"input path does not exist: {path_arg}")
    return resolved


def _resolve_output_dir(output_arg: str) -> Path:
    resolved = Path(output_arg).resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise RbacError("unsafe_path", "output-dir must resolve under the repository root")
    if rel.parts[:2] != ALLOWED_OUTPUT_PREFIX:
        raise RbacError("unsafe_path", "output-dir must be tmp/phase9f-local-rbac-policy or below it")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _load_json(path: Path, json_error: str):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise RbacError("policy_missing", f"cannot read input: {exc}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RbacError(json_error, f"input is not valid JSON: {exc}")


def _extract_registry_records(raw) -> list:
    if not isinstance(raw, dict):
        return []
    for container in REGISTRY_CONTAINERS:
        value = raw.get(container)
        if isinstance(value, list):
            return [r for r in value if isinstance(r, dict)]
    return []


def _severity_counts(issues: list) -> dict:
    counts = {"info": 0, "warning": 0, "critical": 0}
    for issue in issues:
        counts[issue.get("severity", "warning")] = counts.get(issue.get("severity", "warning"), 0) + 1
    return counts


def _overall_incident(issues: list) -> str:
    present = {i["incident_classification"] for i in issues}
    for incident in INCIDENT_PRIORITY:
        if incident in present:
            return incident
    return "none"


def _overall_reviewer(issues: list) -> str:
    present = {i["reviewer_action"] for i in issues}
    for action in REVIEWER_PRIORITY:
        if action in present:
            return action
    return NOOP


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _base_payload() -> dict:
    payload = dict(STATUS_BLOCK)
    payload["approval_boundary_statement"] = APPROVAL_BOUNDARY_STATEMENT
    payload["safety_statement"] = SAFETY_STATEMENT
    payload["limitations"] = list(LIMITATIONS)
    return payload


def _report_markdown(payload: dict) -> str:
    lines = [
        "# Phase 9F Local RBAC Policy Decision Report",
        "",
        f"- phase9f_status: {payload['phase9f_status']}",
        f"- advisory_decision: {payload['advisory_decision']}",
        f"- decision_reason: {payload['decision_reason']}",
        f"- matched_permission_ids: {payload['matched_permission_ids']}",
        f"- denied_permission_ids: {payload['denied_permission_ids']}",
        f"- obligations: {payload['obligations']}",
        f"- denial_reasons: {payload['denial_reasons']}",
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
                f"(subject_id={issue['subject_id'] or 'n/a'}, "
                f"resource_id={issue['resource_id'] or 'n/a'}, "
                f"action={issue['action'] or 'n/a'}, "
                f"permission_id={issue['permission_id'] or 'n/a'}): {issue['message']}"
            )
    else:
        lines.append("- no issues")
    lines += ["", "## Output paths", ""]
    for name, value in payload["output_paths"].items():
        lines.append(f"- {name}: {value}")
    lines += ["", "## Limitations", ""]
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Approval boundary",
        "",
        "- local RBAC policy prototype is not enforcement",
        "- RBAC allow decision is not approval",
        "- RBAC eligibility is not approval",
        "- RBAC advisory report is evidence only",
        "- registry presence is not authentication",
        "- actor attribution is not approval",
        "- approval remains Phase 7D selected-gate manual boundary",
        "",
    ]
    return "\n".join(lines)


def _emit_error_report(output_dir: Path, issue: dict) -> None:
    payload = _base_payload()
    report_json = output_dir / "local-rbac-decision-report.json"
    report_md = output_dir / "local-rbac-decision-report.md"
    payload.update({
        "advisory_decision": "deny",
        "decision_reason": issue["issue_type"],
        "matched_permission_ids": [],
        "denied_permission_ids": [],
        "obligations": [],
        "denial_reasons": [issue["issue_type"]],
        "failure_count": 1,
        "severity_counts": _severity_counts([issue]),
        "reviewer_action": issue["reviewer_action"],
        "reviewer_action_required": True,
        "incident_classification": issue["incident_classification"],
        "issues": [issue],
        "request": {},
        "subject": {},
        "resource": {},
        "action": "",
        "output_paths": {
            "local_rbac_decision_report_json": str(report_json.relative_to(REPO_ROOT)),
            "local_rbac_decision_report_md": str(report_md.relative_to(REPO_ROOT)),
        },
    })
    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")


def _validate_policy(policy: dict) -> list:
    issues = []
    for field in REQUIRED_POLICY_FIELDS:
        if field not in policy:
            issue_type = {
                "policy_version": "policy_version_missing",
            }.get(field, "policy_missing")
            issues.append(make_issue(issue_type, f"policy missing required field: {field}"))

    if policy.get("policy_version") != ALLOWED_POLICY_VERSION:
        issues.append(make_issue("policy_version_incompatible", f"policy_version must be {ALLOWED_POLICY_VERSION}"))
    if policy.get("policy_status") != ALLOWED_POLICY_STATUS:
        issues.append(make_issue("policy_mode_invalid", f"policy_status must be {ALLOWED_POLICY_STATUS}"))
    if policy.get("policy_mode") != ALLOWED_POLICY_MODE:
        issues.append(make_issue("policy_mode_invalid", f"policy_mode must be {ALLOWED_POLICY_MODE}"))
    if policy.get("enforcement_enabled"):
        issues.append(make_issue("enforcement_enabled_present", "policy must not set enforcement_enabled: true"))

    stmt = policy.get("approval_boundary_statement")
    stmt_low = stmt.lower() if isinstance(stmt, str) else ""
    if not any(phrase in stmt_low for phrase in APPROVAL_BOUNDARY_PHRASES):
        issues.append(make_issue("approval_boundary_required", "policy approval_boundary_statement missing required phrase"))

    permissions = policy.get("permissions")
    if not isinstance(permissions, list):
        issues.append(make_issue("invalid_policy_shape", "policy permissions must be a list"))
        permissions = []

    for perm in permissions:
        if not isinstance(perm, dict):
            issues.append(make_issue("permission_missing", "permission entry must be an object"))
            continue
        pid = perm.get("permission_id", "")
        for field in REQUIRED_PERMISSION_FIELDS:
            if field not in perm:
                issues.append(make_issue("permission_missing", f"permission missing required field: {field}", permission_id=pid))
        if perm.get("effect") not in ALLOWED_EFFECTS and "effect" in perm:
            issues.append(make_issue("permission_unknown", "permission effect must be allow or deny", permission_id=pid))
        issues.extend(_approval_flag_issues(perm, permission_id=pid))
        if _has_secret(perm):
            issues.append(make_issue("privacy_review_required", "permission contains a secret-like marker or URL", permission_id=pid))

    issues.extend(_approval_flag_issues(policy))
    if _has_secret(policy):
        issues.append(make_issue("privacy_review_required", "policy contains a secret-like marker or URL"))

    return issues


def _validate_request(request: dict) -> list:
    issues = []
    for field in REQUIRED_REQUEST_FIELDS:
        if field not in request:
            issue_type = {"subject": "subject_missing", "resource": "resource_unknown", "action": "action_unknown"}.get(field, "invalid_request_shape")
            issues.append(make_issue(issue_type, f"request missing required field: {field}"))

    subject = request.get("subject")
    if not isinstance(subject, dict):
        issues.append(make_issue("subject_missing", "request.subject must be an object"))
        subject = {}
    else:
        for field in REQUIRED_SUBJECT_FIELDS:
            if field not in subject:
                issue_type = "role_missing" if field == "subject_role_labels" else "subject_missing"
                issues.append(make_issue(issue_type, f"subject missing required field: {field}", subject_id=subject.get("subject_id", "")))
        assurance = subject.get("subject_identity_assurance")
        if assurance is not None and assurance not in ALLOWED_IDENTITY_ASSURANCE:
            issues.append(make_issue("subject_unknown", "subject_identity_assurance is not an allowed value", subject_id=subject.get("subject_id", "")))

    resource = request.get("resource")
    if not isinstance(resource, dict):
        issues.append(make_issue("resource_unknown", "request.resource must be an object"))
        resource = {}
    else:
        for field in REQUIRED_RESOURCE_FIELDS:
            if field not in resource:
                issues.append(make_issue("resource_unknown", f"resource missing required field: {field}", resource_id=resource.get("resource_id", "")))
        rtype = resource.get("resource_type")
        if rtype is not None and rtype not in ALLOWED_RESOURCE_TYPES:
            issues.append(make_issue("resource_unknown", "resource_type is not an allowed value", resource_id=resource.get("resource_id", "")))

    action = request.get("action")
    if isinstance(action, str) and action not in ALLOWED_ACTIONS:
        issues.append(make_issue("action_unknown", "action is not an allowed value", action=action))

    stmt = request.get("approval_boundary_statement")
    stmt_low = stmt.lower() if isinstance(stmt, str) else ""
    if not any(phrase in stmt_low for phrase in APPROVAL_BOUNDARY_PHRASES):
        issues.append(make_issue("approval_boundary_required", "request approval_boundary_statement missing required phrase"))

    issues.extend(_approval_flag_issues(request, subject_id=subject.get("subject_id", "") if isinstance(subject, dict) else ""))
    if _has_secret(request):
        issues.append(make_issue("privacy_review_required", "request contains a secret-like marker or URL"))
    if isinstance(subject, dict) and (_has_email(subject.get("subject_actor_id", "")) or _has_email(subject.get("subject_id", ""))):
        issues.append(make_issue("privacy_review_required", "subject_actor_id or subject_id contains a raw email address", subject_id=subject.get("subject_id", "")))

    return issues


def _assurance_rank(value: str) -> int:
    try:
        return IDENTITY_ASSURANCE_ORDER.index(value)
    except ValueError:
        return -1


def _permission_matches(perm: dict, subject: dict, resource: dict, action: str) -> bool:
    roles = perm.get("roles") or []
    subject_roles = subject.get("subject_role_labels") or []
    if not any(role in subject_roles for role in roles):
        return False
    resources = perm.get("resources") or []
    if "*" not in resources and resource.get("resource_type") not in resources:
        return False
    actions = perm.get("actions") or []
    if "*" not in actions and action not in actions:
        return False
    return True


def _identity_sufficient(perm: dict, subject: dict) -> bool:
    required = perm.get("required_identity_assurance")
    if not required:
        return True
    return _assurance_rank(subject.get("subject_identity_assurance", "")) >= _assurance_rank(required)


def evaluate(policy: dict, request: dict) -> dict:
    subject = request.get("subject", {})
    resource = request.get("resource", {})
    action = request.get("action", "")
    permissions = sorted(
        (p for p in policy.get("permissions", []) if isinstance(p, dict)),
        key=lambda p: p.get("permission_id", ""),
    )

    matched_allow = []
    matched_deny = []
    matched_conditional = []
    obligations: list = []

    if action == "execute_primitive":
        return {
            "advisory_decision": "deny",
            "decision_reason": "primitive_execution_blocked",
            "matched_permission_ids": [],
            "denied_permission_ids": [],
            "obligations": ["require_no_primitive_execution"],
            "denial_reasons": ["primitive_execution_blocked"],
            "reviewer_action": "reject_action_until_resolved",
        }

    for perm in permissions:
        if not _permission_matches(perm, subject, resource, action):
            continue
        pid = perm.get("permission_id", "")
        if perm.get("effect") == "deny":
            matched_deny.append(pid)
            continue
        if _identity_sufficient(perm, subject):
            matched_allow.append(pid)
            obligations.extend(perm.get("obligations") or [])
        else:
            matched_conditional.append(pid)
            obligations.extend(perm.get("obligations") or [])

    if matched_deny:
        return {
            "advisory_decision": "deny",
            "decision_reason": "explicit_deny",
            "matched_permission_ids": [],
            "denied_permission_ids": sorted(matched_deny),
            "obligations": sorted(set(obligations)),
            "denial_reasons": ["explicit_deny"],
            "reviewer_action": "manual_review_required",
        }

    if matched_allow:
        result = {
            "advisory_decision": "allow",
            "decision_reason": "policy_allow",
            "matched_permission_ids": sorted(matched_allow),
            "denied_permission_ids": [],
            "obligations": sorted(set(obligations)),
            "denial_reasons": [],
            "reviewer_action": "no_action_required",
        }
        if action == "approve_selected_gate":
            result["obligations"] = sorted(set(result["obligations"]) | {"require_phase7d_selected_gate"})
        return result

    if matched_conditional:
        return {
            "advisory_decision": "conditional_allow",
            "decision_reason": "insufficient_identity_assurance",
            "matched_permission_ids": sorted(matched_conditional),
            "denied_permission_ids": [],
            "obligations": sorted(set(obligations) | {"require_manual_review"}),
            "denial_reasons": ["insufficient_identity_assurance"],
            "reviewer_action": "manual_review_required",
        }

    return {
        "advisory_decision": "deny",
        "decision_reason": "no_matching_permission",
        "matched_permission_ids": [],
        "denied_permission_ids": [],
        "obligations": [],
        "denial_reasons": ["no_matching_permission"],
        "reviewer_action": "manual_review_required",
    }


def build_report(policy_arg, request_arg, registry_arg, attribution_arg, output_dir: Path) -> int:
    policy_path = _resolve_input(policy_arg, "policy_missing")
    request_path = _resolve_input(request_arg, "request_missing")

    policy_raw = _load_json(policy_path, "invalid_policy_json")
    if not isinstance(policy_raw, dict):
        raise RbacError("invalid_policy_shape", "policy must be a JSON object")

    request_raw = _load_json(request_path, "invalid_request_json")
    if not isinstance(request_raw, dict):
        raise RbacError("invalid_request_shape", "request must be a JSON object")

    issues = []
    issues.extend(_validate_policy(policy_raw))
    issues.extend(_validate_request(request_raw))

    registry_context = None
    if registry_arg:
        registry_path = _resolve_input(registry_arg, "policy_missing")
        registry_raw = _load_json(registry_path, "invalid_policy_json")
        records = _extract_registry_records(registry_raw)
        registry_context = {
            "registry_record_count": len(records),
            "registry_presence_statement": "registry presence is not authentication and is not approval",
        }

    attribution_context = None
    if attribution_arg:
        attribution_path = _resolve_input(attribution_arg, "policy_missing")
        attribution_raw = _load_json(attribution_path, "invalid_policy_json")
        if isinstance(attribution_raw, dict):
            attribution_context = {
                "attribution_record_count": len(attribution_raw.get("attributed_records", []) or []),
                "attribution_statement": "actor attribution is not authentication and is not approval",
            }

    invalidating = [i for i in issues if i["issue_type"] != "duplicate"]

    subject = request_raw.get("subject", {}) if isinstance(request_raw.get("subject"), dict) else {}
    resource = request_raw.get("resource", {}) if isinstance(request_raw.get("resource"), dict) else {}
    action = request_raw.get("action", "") if isinstance(request_raw.get("action"), str) else ""

    report_json = output_dir / "local-rbac-decision-report.json"
    report_md = output_dir / "local-rbac-decision-report.md"

    if invalidating:
        payload = _base_payload()
        reviewer_action = _overall_reviewer(issues)
        payload.update({
            "advisory_decision": "deny",
            "decision_reason": "invalid_input",
            "matched_permission_ids": [],
            "denied_permission_ids": [],
            "obligations": [],
            "denial_reasons": [i["issue_type"] for i in invalidating],
            "failure_count": len(issues),
            "severity_counts": _severity_counts(issues),
            "reviewer_action": reviewer_action,
            "reviewer_action_required": True,
            "incident_classification": _overall_incident(issues),
            "issues": issues,
            "request": request_raw,
            "subject": subject,
            "resource": resource,
            "action": action,
            "output_paths": {
                "local_rbac_decision_report_json": str(report_json.relative_to(REPO_ROOT)),
                "local_rbac_decision_report_md": str(report_md.relative_to(REPO_ROOT)),
            },
        })
        if registry_context:
            payload["registry_context"] = registry_context
        if attribution_context:
            payload["attribution_context"] = attribution_context
        _write_json(report_json, payload)
        report_md.write_text(_report_markdown(payload), encoding="utf-8")
        return 1

    decision = evaluate(policy_raw, request_raw)

    payload = _base_payload()
    payload.update(decision)
    payload.update({
        "failure_count": len(issues),
        "severity_counts": _severity_counts(issues),
        "reviewer_action_required": decision["reviewer_action"] != NOOP,
        "incident_classification": _overall_incident(issues) if issues else "none",
        "issues": issues,
        "request": request_raw,
        "subject": subject,
        "resource": resource,
        "action": action,
        "output_paths": {
            "local_rbac_decision_report_json": str(report_json.relative_to(REPO_ROOT)),
            "local_rbac_decision_report_md": str(report_md.relative_to(REPO_ROOT)),
        },
    })
    if registry_context:
        payload["registry_context"] = registry_context
    if attribution_context:
        payload["attribution_context"] = attribution_context

    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Phase 9F Local RBAC Policy Prototype")
    parser.add_argument("--policy", default=None)
    parser.add_argument("--request", default=None)
    parser.add_argument("--registry", default=None)
    parser.add_argument("--attribution", default=None)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
    except RbacError as exc:
        print(f"phase9f error: {exc.issue_type}: {exc.message}", file=sys.stderr)
        return 2

    if not args.policy:
        issue = make_issue("policy_missing", "--policy is required")
        _emit_error_report(output_dir, issue)
        print("phase9f error: policy_missing: --policy is required", file=sys.stderr)
        return 1
    if not args.request:
        issue = make_issue("request_missing", "--request is required")
        _emit_error_report(output_dir, issue)
        print("phase9f error: request_missing: --request is required", file=sys.stderr)
        return 1

    try:
        return build_report(args.policy, args.request, args.registry, args.attribution, output_dir)
    except RbacError as exc:
        issue = make_issue(exc.issue_type, exc.message)
        _emit_error_report(output_dir, issue)
        print(f"phase9f error: {exc.issue_type}: {exc.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
