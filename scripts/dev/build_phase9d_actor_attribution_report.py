#!/usr/bin/env python3
"""Phase 9D Actor Attribution in Audit/Reports.

Local-only, metadata-only, evidence-only. Reads an existing Phase 9C local
operator registry and a local evidence/report reference file, attaches selected
actor metadata to each evidence reference, and writes an actor-attributed report
under tmp/phase9d-actor-attribution/.

This prototype is NOT authentication, NOT RBAC, NOT login, NOT a session store,
and NOT a user database. Actor attribution is attribution metadata only. Actor
attribution is not approval, registry presence is not approval, an attributed
report is evidence only, and approval remains the Phase 7D selected-gate manual
boundary.

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
DEFAULT_REGISTRY = "tmp/phase9c-local-operator-registry/operator-registry.json"
DEFAULT_OUTPUT_DIR = "tmp/phase9d-actor-attribution"
ALLOWED_OUTPUT_PREFIX = ("tmp", "phase9d-actor-attribution")
FORBIDDEN_INPUT_ROOTS = {"vault", "docs", "scripts", "codex", ".git"}

# Registry containers accepted for compatibility (Phase 9C writes actor_registry).
REGISTRY_CONTAINERS = ("actor_metadata", "actor_registry", "records", "registry_records", "operators")
EVIDENCE_CONTAINERS = ("evidence_references", "reports", "audit_records", "artifacts")

STATUS_BLOCK = {
    "phase9d_status": "success",
    "phase7d_runtime_readiness": "implemented_manual_gate",
    "durable_audit_store_status": "phase8_final_acceptance_pack",
    "identity_boundary_status": "design_only",
    "actor_metadata_schema_status": "design_only",
    "actor_metadata_runtime_status": "local_registry_prototype",
    "local_operator_registry_status": "prototype_local_only",
    "actor_attribution_status": "local_report_prototype",
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
    "actor attribution is not authentication; actor attribution is not approval; "
    "attributed report is evidence only; approval remains Phase 7D selected-gate "
    "manual boundary"
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

ACTOR_REQUIRED_FIELDS = (
    "actor_id", "actor_type", "actor_display_label", "actor_role_labels",
    "actor_identity_assurance", "actor_identity_source", "actor_action_scope",
    "privacy_classification", "approval_boundary_statement",
)
EVIDENCE_REQUIRED_FIELDS = (
    "evidence_id", "evidence_type", "evidence_path", "evidence_phase",
    "evidence_purpose",
)

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

REJECT_ACTOR = "reject_actor_metadata_until_resolved"
REJECT_ATTR = "reject_attribution_until_resolved"
REVIEW = "manual_review_required"
NOOP = "no_action_required"

# issue_type -> (severity, incident_classification, reviewer_action)
ISSUE_SPEC = {
    "registry_missing": ("critical", "actor_attribution_not_available", REJECT_ATTR),
    "evidence_missing": ("critical", "actor_attribution_not_available", REJECT_ATTR),
    "invalid_registry_json": ("critical", "actor_metadata_schema_failure", REJECT_ATTR),
    "invalid_evidence_json": ("critical", "evidence_reference_failure", REJECT_ATTR),
    "invalid_registry_shape": ("critical", "actor_metadata_schema_failure", REJECT_ATTR),
    "invalid_evidence_shape": ("critical", "evidence_reference_failure", REJECT_ATTR),
    "registry_actor_missing": ("critical", "actor_attribution_not_available", REJECT_ATTR),
    "actor_not_found": ("critical", "actor_attribution_not_available", REVIEW),
    "duplicate_actor_id": ("warning", "actor_metadata_schema_failure", REVIEW),
    "evidence_reference_missing_field": ("critical", "evidence_reference_failure", REJECT_ATTR),
    "actor_metadata_contains_secret": ("critical", "privacy_review_required", REJECT_ACTOR),
    "evidence_metadata_contains_secret": ("critical", "privacy_review_required", REJECT_ATTR),
    "actor_metadata_contains_unnecessary_pii": ("warning", "privacy_review_required", REJECT_ACTOR),
    "approval_boundary_statement_missing": ("warning", "identity_policy_review_required", REJECT_ACTOR),
    "approval_flag_present": ("critical", "actor_metadata_schema_failure", REJECT_ATTR),
    "primitive_execution_intent_present": ("critical", "actor_metadata_schema_failure", REJECT_ATTR),
    "unsafe_path": ("critical", "actor_attribution_not_available", REJECT_ATTR),
}
INCIDENT_PRIORITY = [
    "privacy_review_required",
    "actor_metadata_schema_failure",
    "evidence_reference_failure",
    "identity_assurance_review_required",
    "identity_policy_review_required",
    "actor_scope_review_required",
    "actor_attribution_not_available",
    "none",
]
REVIEWER_PRIORITY = [REJECT_ATTR, REJECT_ACTOR, REVIEW, NOOP]


class AttributionError(Exception):
    def __init__(self, issue_type: str, message: str) -> None:
        super().__init__(message)
        self.issue_type = issue_type
        self.message = message


def make_issue(issue_type: str, message: str, actor_id: str = "", evidence_id: str = "") -> dict:
    severity, incident, reviewer = ISSUE_SPEC.get(
        issue_type, ("warning", "actor_metadata_schema_failure", REJECT_ATTR)
    )
    return {
        "issue_type": issue_type,
        "severity": severity,
        "incident_classification": incident,
        "reviewer_action": reviewer,
        "actor_id": actor_id,
        "evidence_id": evidence_id,
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


def _approval_flag_issues(mapping, actor_id: str = "", evidence_id: str = "") -> list:
    issues = []
    if not isinstance(mapping, dict):
        return issues
    for key in APPROVAL_FLAG_KEYS:
        if mapping.get(key):
            issues.append(make_issue("approval_flag_present", f"approval flag '{key}' must not be truthy", actor_id, evidence_id))
    for key in PRIMITIVE_INTENT_KEYS:
        if mapping.get(key):
            issues.append(make_issue("primitive_execution_intent_present", f"primitive execution intent '{key}' is not allowed", actor_id, evidence_id))
    return issues


def _resolve_input(path_arg: str, missing_type: str) -> Path:
    raw = Path(path_arg)
    if raw.is_symlink():
        raise AttributionError("unsafe_path", f"input path must not be a symlink: {path_arg}")
    resolved = raw.resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise AttributionError("unsafe_path", f"input path must resolve under the repository root: {path_arg}")
    if rel.parts and rel.parts[0] in FORBIDDEN_INPUT_ROOTS:
        raise AttributionError("unsafe_path", f"input path must not be under {rel.parts[0]}/")
    if not resolved.is_file():
        raise AttributionError(missing_type, f"input path does not exist: {path_arg}")
    return resolved


def _resolve_output_dir(output_arg: str) -> Path:
    resolved = Path(output_arg).resolve()
    try:
        rel = resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise AttributionError("unsafe_path", "output-dir must resolve under the repository root")
    if rel.parts[:2] != ALLOWED_OUTPUT_PREFIX:
        raise AttributionError("unsafe_path", "output-dir must be tmp/phase9d-actor-attribution or below it")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _load_json(path: Path, json_error: str):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise AttributionError("registry_missing", f"cannot read input: {exc}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AttributionError(json_error, f"input is not valid JSON: {exc}")


def _extract_records(raw, containers, shape_error, allow_top_array=False) -> list:
    if isinstance(raw, dict):
        for container in containers:
            value = raw.get(container)
            if isinstance(value, list):
                return list(value)
        return []
    if allow_top_array and isinstance(raw, list):
        return list(raw)
    raise AttributionError(shape_error, "input has an unexpected shape")


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
        "# Phase 9D Actor Attribution Report",
        "",
        f"- phase9d_status: {payload['phase9d_status']}",
        f"- attribution_report_status: {payload['attribution_report_status']}",
        f"- actor_attribution_status: {payload['actor_attribution_status']}",
        f"- selected_actor_id: {payload['selected_actor_id']}",
        f"- evidence_reference_count: {payload['evidence_reference_count']}",
        f"- attributed_record_count: {payload['attributed_record_count']}",
        f"- unattributed_record_count: {payload['unattributed_record_count']}",
        f"- duplicate_actor_count: {payload['duplicate_actor_count']}",
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
                f"(actor_id={issue['actor_id'] or 'n/a'}, "
                f"evidence_id={issue['evidence_id'] or 'n/a'}): {issue['message']}"
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
        "- actor attribution is not authentication",
        "- actor attribution is not approval",
        "- registry presence is not approval",
        "- attributed report is evidence only",
        "- approval remains Phase 7D selected-gate manual boundary",
        "",
    ]
    return "\n".join(lines)


def _emit_error_report(output_dir: Path, issue: dict, actor_attribution_status: str = "local_report_prototype") -> None:
    payload = _base_payload()
    payload["actor_attribution_status"] = actor_attribution_status
    report_json = output_dir / "actor-attribution-report.json"
    report_md = output_dir / "actor-attribution-report.md"
    payload.update({
        "attribution_report_status": "not_built",
        "selected_actor_id": "",
        "evidence_reference_count": 0,
        "attributed_record_count": 0,
        "unattributed_record_count": 0,
        "duplicate_actor_count": 0,
        "failure_count": 1,
        "severity_counts": _severity_counts([issue]),
        "reviewer_action": issue["reviewer_action"],
        "reviewer_action_required": True,
        "incident_classification": issue["incident_classification"],
        "issues": [issue],
        "attributed_records": [],
        "output_paths": {
            "actor_attribution_report_json": str(report_json.relative_to(REPO_ROOT)),
            "actor_attribution_report_md": str(report_md.relative_to(REPO_ROOT)),
        },
    })
    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")


def build_report(registry_arg: str, evidence_arg: str, actor_id_arg, output_dir: Path) -> int:
    registry_path = _resolve_input(registry_arg, "registry_missing")
    evidence_path = _resolve_input(evidence_arg, "evidence_missing")

    registry_raw = _load_json(registry_path, "invalid_registry_json")
    if not isinstance(registry_raw, dict):
        raise AttributionError("invalid_registry_shape", "registry must be a JSON object")
    actor_records = _extract_records(registry_raw, REGISTRY_CONTAINERS, "invalid_registry_shape")
    actor_records = [r for r in actor_records if isinstance(r, dict)]
    if not actor_records:
        raise AttributionError("registry_actor_missing", "registry has no actor records")

    evidence_raw = _load_json(evidence_path, "invalid_evidence_json")
    evidence_refs = _extract_records(evidence_raw, EVIDENCE_CONTAINERS, "invalid_evidence_shape", allow_top_array=True)
    evidence_refs = [r for r in evidence_refs if isinstance(r, dict)]
    if not evidence_refs:
        raise AttributionError("invalid_evidence_shape", "no evidence references found")

    issues = []

    # Duplicate actor detection (registry-wide).
    seen = set()
    duplicate_count = 0
    for rec in actor_records:
        aid = rec.get("actor_id", "")
        if aid in seen:
            duplicate_count += 1
            issues.append(make_issue("duplicate_actor_id", "duplicate actor_id in registry", actor_id=aid))
        else:
            seen.add(aid)

    # Actor selection.
    if actor_id_arg:
        candidates = [r for r in actor_records if r.get("actor_id") == actor_id_arg]
        if not candidates:
            issue = make_issue("actor_not_found", f"actor_id not found in registry: {actor_id_arg}", actor_id=actor_id_arg)
            _emit_error_report(output_dir, issue, actor_attribution_status="failed_actor_not_found")
            print(f"phase9d error: actor_not_found: {actor_id_arg}", file=sys.stderr)
            return 1
        selected = candidates[0]
    else:
        selected = sorted(actor_records, key=lambda r: r.get("actor_id", ""))[0]
    selected_actor_id = selected.get("actor_id", "")

    # Approval boundary statement on the selected actor.
    stmt = selected.get("approval_boundary_statement")
    stmt_low = stmt.lower() if isinstance(stmt, str) else ""
    if not any(phrase in stmt_low for phrase in APPROVAL_BOUNDARY_PHRASES):
        issues.append(make_issue("approval_boundary_statement_missing", "selected actor approval_boundary_statement missing required phrase", actor_id=selected_actor_id))

    # Privacy / secret scan on selected actor.
    if _has_secret(selected):
        issues.append(make_issue("actor_metadata_contains_secret", "selected actor metadata contains a secret-like marker or URL", actor_id=selected_actor_id))
    if _has_email(selected):
        issues.append(make_issue("actor_metadata_contains_unnecessary_pii", "selected actor metadata contains a raw email address", actor_id=selected_actor_id))

    # Approval-flag / primitive scan on selected actor.
    issues.extend(_approval_flag_issues(selected, actor_id=selected_actor_id))

    # Evidence references: required fields, secrets, approval flags.
    for ref in evidence_refs:
        eid = ref.get("evidence_id", "")
        for field in EVIDENCE_REQUIRED_FIELDS:
            if field not in ref:
                issues.append(make_issue("evidence_reference_missing_field", f"evidence reference missing field: {field}", evidence_id=eid))
        if _has_secret(ref):
            issues.append(make_issue("evidence_metadata_contains_secret", "evidence reference contains a secret-like marker or URL", evidence_id=eid))
        issues.extend(_approval_flag_issues(ref, evidence_id=eid))

    invalidating = [i for i in issues if i["issue_type"] != "duplicate_actor_id"]

    if invalidating:
        attribution_report_status = "not_built"
        attributed_records = []
        exit_code = 1
    elif duplicate_count > 0:
        attribution_report_status = "built_with_warnings"
        attributed_records = _attribute(selected, selected_actor_id, evidence_refs)
        exit_code = 0
    else:
        attribution_report_status = "built"
        attributed_records = _attribute(selected, selected_actor_id, evidence_refs)
        exit_code = 0

    reviewer_action = _overall_reviewer(issues)
    payload = _base_payload()
    report_json = output_dir / "actor-attribution-report.json"
    report_md = output_dir / "actor-attribution-report.md"
    payload.update({
        "attribution_report_status": attribution_report_status,
        "selected_actor_id": selected_actor_id,
        "evidence_reference_count": len(evidence_refs),
        "attributed_record_count": len(attributed_records),
        "unattributed_record_count": len(evidence_refs) - len(attributed_records),
        "duplicate_actor_count": duplicate_count,
        "failure_count": len(issues),
        "severity_counts": _severity_counts(issues),
        "reviewer_action": reviewer_action,
        "reviewer_action_required": reviewer_action != NOOP,
        "incident_classification": _overall_incident(issues),
        "issues": issues,
        "attributed_records": attributed_records,
        "output_paths": {
            "actor_attribution_report_json": str(report_json.relative_to(REPO_ROOT)),
            "actor_attribution_report_md": str(report_md.relative_to(REPO_ROOT)),
        },
    })
    _write_json(report_json, payload)
    report_md.write_text(_report_markdown(payload), encoding="utf-8")
    return exit_code


def _attribute(selected: dict, selected_actor_id: str, evidence_refs: list) -> list:
    records = []
    for ref in evidence_refs:
        records.append({
            "evidence_id": ref.get("evidence_id", ""),
            "evidence_type": ref.get("evidence_type", ""),
            "evidence_path": ref.get("evidence_path", ""),
            "evidence_phase": ref.get("evidence_phase", ""),
            "evidence_purpose": ref.get("evidence_purpose", ""),
            "actor_metadata": selected,
            "actor_id": selected_actor_id,
            "actor_type": selected.get("actor_type", ""),
            "actor_identity_assurance": selected.get("actor_identity_assurance", ""),
            "actor_identity_source": selected.get("actor_identity_source", ""),
            "actor_role_labels": selected.get("actor_role_labels", []),
            "attribution_status": "attributed",
            "approval_boundary_statement": selected.get("approval_boundary_statement", APPROVAL_BOUNDARY_STATEMENT),
        })
    return records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Phase 9D Actor Attribution in Audit/Reports")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--evidence", default=None)
    parser.add_argument("--actor-id", default=None)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    try:
        output_dir = _resolve_output_dir(args.output_dir)
    except AttributionError as exc:
        print(f"phase9d error: {exc.issue_type}: {exc.message}", file=sys.stderr)
        return 2

    if not args.evidence:
        issue = make_issue("evidence_missing", "--evidence is required")
        _emit_error_report(output_dir, issue)
        print("phase9d error: evidence_missing: --evidence is required", file=sys.stderr)
        return 1

    try:
        return build_report(args.registry, args.evidence, args.actor_id, output_dir)
    except AttributionError as exc:
        issue = make_issue(exc.issue_type, exc.message)
        _emit_error_report(output_dir, issue)
        print(f"phase9d error: {exc.issue_type}: {exc.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
