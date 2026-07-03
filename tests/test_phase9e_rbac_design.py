from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/071-phase9e-rbac-design.md"
DOC = REPO_ROOT / "docs/PHASE9E_RBAC_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE9B_DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py": "ef26e4f11f5ecb73e31f01261b56adb35df223f514edc0986e32f9d00d441aca",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh": "de6cd990e794d5893d31f682a9c7073a350af30c701665c43729d0d889095ff0",
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py": "6a7fddfbb3077c18816b81c57738bd79471db5a3f578d35292fde8e8f318de09",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh": "ecd3d6846702948f5a9b77addcd6254ea3a7295dcb01765ebcad91ced1a196cb",
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py": "1711d387f813b2d8e046704ed7063f1ad7c050413c0b999b7358e0ad6939dc1c",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh": "486258b28e74f9034681e5cc7d3827efddbc19ed6e5f0a6266097d6679560c9d",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py": "c656cb49c645f056be4069e78aa5fdf63cc77d3a6676d2ae5bd96fde2a0d8b31",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh": "9441dc0e5a3fa692fb532c1f1475f89f871b4ed4289bb0d567cf26e6a1305cca",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase9e_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9E file: {path}"


def test_phase9e_no_runtime_script_or_runner() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase9e*.py", "*phase9e*.sh"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9E runtime file: {matches}"


def test_phase9e_task_status_token() -> None:
    assert "phase9e_status: success" in _text(TASK_FILE)


def test_phase9e_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase9e_status: success",
        "rbac_design_status: design_only",
        "rbac_runtime_status: not_implemented",
        "actor_attribution_status: local_report_prototype",
        "actor_metadata_runtime_status: local_registry_prototype",
        "local_operator_registry_status: prototype_local_only",
        "identity_runtime_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9e_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "docs/tests design-only",
        "no runtime scripts",
        "no shell runner",
        "no policy engine implementation",
        "no rbac enforcement",
        "no permission gate",
        "no authentication runtime",
        "no login",
        "no session runtime",
        "no user store",
        "no backend/api/database",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
    ):
        assert token in low, f"missing scope safety token: {token}"


# ---------------------------------------------------------------------------
# C. Required sections
# ---------------------------------------------------------------------------


def test_phase9e_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Purpose",
        "### Scope",
        "### Current trust boundary after Phase 9D",
        "### RBAC concept model",
        "### Subject model",
        "### Role model",
        "### Permission model",
        "### Resource model",
        "### Action model",
        "### Decision model",
        "### Obligation model",
        "### Denial model",
        "### Audit event model",
        "### Policy versioning model",
        "### Policy evaluation lifecycle design",
        "### Role-to-actor metadata mapping",
        "### Governance role mapping",
        "### Product workflow resource model",
        "### Signature/export resource model",
        "### Registry/attribution resource model",
        "### Approval boundary preservation",
        "### Non-authentication boundary",
        "### Non-approval boundary",
        "### Future local policy prototype boundary",
        "### Compatibility with Phase 9D",
        "### Compatibility with Phase 9C",
        "### Compatibility with Phase 9B",
        "### Compatibility with Phase 9A",
        "### Compatibility with Phase 8O/8L/8M",
        "### Compatibility with Phase 7D",
        "### Failure taxonomy",
        "### Reviewer action mapping",
        "### Non-goals",
        "### Known limitations",
    ):
        assert token in text, f"missing section: {token}"


# ---------------------------------------------------------------------------
# D. RBAC concept assertions
# ---------------------------------------------------------------------------


def test_phase9e_concept_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "subject", "role", "permission", "resource", "action", "condition",
        "decision", "obligation", "denial", "audit_event",
        "rbac concept model is design-only",
        "no runtime evaluator exists",
        "no policy file is produced in phase 9e",
        "rbac eligibility is not approval",
    ):
        assert token in low, f"missing concept token: {token}"


# ---------------------------------------------------------------------------
# E. Subject model assertions
# ---------------------------------------------------------------------------


def test_phase9e_subject_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "subject_id", "subject_actor_id", "subject_actor_type",
        "subject_identity_assurance", "subject_identity_source",
        "subject_role_labels", "subject_session_reference",
        "subject_registry_reference", "subject_attribution_reference",
        "approval_boundary_statement",
        "subject is not authentication by itself",
        "subject is not approval",
        "subject must map to phase 9b actor metadata",
    ):
        assert token in low, f"missing subject token: {token}"


# ---------------------------------------------------------------------------
# F. Role model assertions
# ---------------------------------------------------------------------------


def test_phase9e_role_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "affiliate_operator", "affiliate_reviewer", "affiliate_signer",
        "affiliate_key_owner", "affiliate_key_custodian", "affiliate_security_owner",
        "affiliate_system_owner", "affiliate_emergency_revocation_authority",
        "affiliate_auditor", "affiliate_test_operator",
        "affiliate_automation_placeholder",
        "role is not runtime permission in phase 9e",
    ):
        assert token in low, f"missing role token: {token}"


# ---------------------------------------------------------------------------
# G. Permission / resource / action assertions
# ---------------------------------------------------------------------------


def test_phase9e_permission_resource_action_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "permission_id", "resource_type", "allowed_actions", "denied_actions",
        "required_identity_assurance", "required_actor_role_labels", "obligations",
        "permission is design-only",
        "permission does not approve product action",
        "permission does not execute primitive",
        # resources
        "product_candidate", "scoring_report", "weekly_report", "promotion_gate",
        "manual_decision", "finalization_decision", "phase7d_selected_gate",
        "audit_store_record", "audit_store_report", "audit_export_pack",
        "export_integrity_report", "detached_signature_envelope",
        "signature_verifier_report", "signature_incident_runbook",
        "final_acceptance_pack", "actor_registry", "actor_attribution_report",
        "rbac_policy", "test_fixture",
        # actions
        "read", "list", "build_report", "validate", "export",
        "sign_local_prototype", "verify_local_prototype", "review", "annotate",
        "register_actor", "attribute_actor", "approve_selected_gate",
        "execute_primitive", "manage_key_governance_metadata",
        "manage_policy_design", "test_generate_fixture",
        "approve_selected_gate remains phase 7d only",
        "execute_primitive remains protected",
    ):
        assert token in low, f"missing permission/resource/action token: {token}"


# ---------------------------------------------------------------------------
# H. Decision / obligation / denial assertions
# ---------------------------------------------------------------------------


def test_phase9e_decision_obligation_denial_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "allow", "deny", "conditional_allow", "manual_review_required",
        "not_applicable",
        "allow is not product approval",
        "allow must not trigger wrapper",
        "allow must not execute primitive",
        "conditional_allow must not bypass manual approval",
        "require_actor_attribution", "require_manual_review",
        "require_phase7d_selected_gate", "require_signature_verification_review",
        "require_final_acceptance_review", "require_privacy_review",
        "require_key_governance_review", "require_incident_review",
        "require_audit_record", "require_no_primitive_execution",
        "subject_missing", "role_missing", "permission_missing",
        "insufficient_identity_assurance", "resource_not_allowed",
        "action_not_allowed", "approval_boundary_required",
        "actor_attribution_required", "privacy_review_required",
        "key_governance_review_required", "primitive_execution_blocked",
        "next_gate_blocked",
    ):
        assert token in low, f"missing decision/obligation/denial token: {token}"


# ---------------------------------------------------------------------------
# I. Audit / policy lifecycle assertions
# ---------------------------------------------------------------------------


def test_phase9e_audit_policy_lifecycle_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "rbac_event_id", "policy_version", "subject_id", "subject_actor_id",
        "resource_type", "resource_id", "action", "decision", "obligations",
        "denial_reasons", "reviewer_action", "actor_attribution_reference",
        "approval_boundary_statement", "event_timestamp_utc",
        "rbac audit event is not approval",
        "initial future policy version: phase9f.local_rbac_policy.v1",
        "design version: phase9e.rbac_design.v1",
        "actor_schema_version phase9b.actor_metadata.v1",
        "load local policy", "load subject actor metadata",
        "load requested resource/action", "evaluate role mapping",
        "evaluate identity assurance requirement",
        "evaluate resource/action permission", "produce decision",
        "attach obligations", "write local advisory report",
        "preserve approval boundary",
        "phase 9e implements none of this runtime",
    ):
        assert token in low, f"missing audit/policy token: {token}"


# ---------------------------------------------------------------------------
# J. Role mapping assertions
# ---------------------------------------------------------------------------


def test_phase9e_role_mapping_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "affiliate_operator -> human_operator/operator",
        "affiliate_reviewer -> reviewer/reviewer",
        "affiliate_signer -> signer/signer",
        "affiliate_key_owner -> key_owner/key_owner",
        "affiliate_key_custodian -> key_custodian/key_custodian",
        "affiliate_security_owner -> security_owner/security_owner",
        "affiliate_system_owner -> system_owner/system_owner",
        "affiliate_emergency_revocation_authority -> emergency_revocation_authority/emergency_revocation_authority",
        "affiliate_auditor -> reviewer or human_operator/auditor",
        "affiliate_test_operator -> test_fixture/test",
        "affiliate_automation_placeholder -> automation_placeholder/automation",
        "mappings are governance metadata only",
    ):
        assert token in low, f"missing role mapping token: {token}"


# ---------------------------------------------------------------------------
# K. Workflow / resource compatibility assertions
# ---------------------------------------------------------------------------


def test_phase9e_workflow_resource_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "score_product", "generate_weekly_report", "import_csv",
        "promote_candidate", "create_manual_decision", "finalize_decision",
        "selected_gate_wrapper",
        "selected_gate_wrapper remains phase 7d selected manual approval boundary",
        "build audit export pack", "verify export integrity",
        "local detached signature creation", "local detached signature verification",
        "signature incident review", "final acceptance review",
        "signature verification remains not approval",
        "final acceptance remains not approval",
        "local operator registry build/list/report",
        "actor attribution report build", "actor metadata validation",
        "actor attribution review",
        "registry presence is not authentication",
        "actor attribution is not approval",
    ):
        assert token in low, f"missing workflow/resource token: {token}"


# ---------------------------------------------------------------------------
# L. Approval boundary assertions
# ---------------------------------------------------------------------------


def test_phase9e_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "rbac design is not rbac enforcement",
        "rbac runtime is not implemented",
        "rbac policy is not approval",
        "rbac eligibility is not approval",
        "rbac decision is not product approval",
        "allow decision is not approval",
        "role label is not runtime permission",
        "governance role label is not approval",
        "actor metadata is not approval",
        "actor attribution is not approval",
        "registry presence is not authentication",
        "registry presence is not approval",
        "authentication is not approval",
        "signature verification remains not approval",
        "final acceptance remains not approval",
        "approval remains phase 7d selected-gate manual boundary",
        "rbac design must not trigger wrapper",
        "rbac design must not execute primitives",
        "rbac design must not trigger next gate",
        "rbac design must not set approval flags",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ---------------------------------------------------------------------------
# M. Future Phase 9F boundary assertions
# ---------------------------------------------------------------------------


def test_phase9e_future_9f_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "future phase 9f may add local rbac policy prototype",
        "phase 9f must remain local-only unless explicitly changed later",
        "phase 9f must not implement authentication",
        "phase 9f must not call wrapper/primitives",
        "phase 9f must produce advisory decisions only",
        "phase 9f must preserve phase 7d approval boundary",
    ):
        assert token in low, f"missing future 9f token: {token}"


# ---------------------------------------------------------------------------
# N. Compatibility assertions
# ---------------------------------------------------------------------------


def test_phase9e_compatibility_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 9e uses phase 9d attribution report as future subject/evidence context",
        "phase 9e does not modify phase 9d runtime",
        "actor attribution remains not authentication or approval",
        "phase 9e uses phase 9c registry as future subject source",
        "phase 9e does not modify phase 9c runtime",
        "registry presence remains not authentication or approval",
        "phase 9e maps roles and subjects to phase 9b actor metadata schema",
        "schema validity remains not approval",
        "phase 9e preserves phase 9a identity boundary",
        "operator identity remains unauthenticated or operator-declared",
        "phase 9e does not modify phase 8 runtime",
        "rbac design does not modify phase 7d",
        "rbac design must not approve anything",
    ):
        assert token in low, f"missing compatibility token: {token}"


# ---------------------------------------------------------------------------
# O. Failure taxonomy assertions
# ---------------------------------------------------------------------------


def test_phase9e_failure_taxonomy_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "subject_missing", "subject_unknown",
        "subject_identity_assurance_insufficient", "role_missing", "role_unknown",
        "permission_missing", "permission_unknown", "resource_unknown",
        "action_unknown", "policy_version_missing", "policy_version_incompatible",
        "obligation_unmet", "approval_boundary_required", "actor_attribution_required",
        "privacy_review_required", "primitive_execution_blocked", "next_gate_blocked",
        "approval_flag_present",
        "rbac_policy_review_required", "identity_assurance_review_required",
        "actor_scope_review_required", "approval_boundary_review_required",
        "no_action_required", "manual_review_required",
        "reject_rbac_policy_until_resolved", "reject_action_until_resolved",
        "info", "warning", "critical",
    ):
        assert token in low, f"missing failure taxonomy token: {token}"


# ---------------------------------------------------------------------------
# P. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9e_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 9E" in roadmap
    assert "docs/PHASE9E_RBAC_DESIGN.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9E_RBAC_DESIGN.md" in project_state
    for token in ("Current architecture", "no database", "no FastAPI", "no UI",
                  "no external APIs", "no autopublish"):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9D_DOC, PHASE9C_DOC, PHASE9B_DOC, PHASE9A_DOC, PHASE8O_DOC):
        assert "Phase 9E" in _text(doc), f"missing Phase 9E reference in {doc.name}"


# ---------------------------------------------------------------------------
# Q. Protected runtime files unchanged / no implementation files
# ---------------------------------------------------------------------------


def test_phase9e_protected_runtime_files_unchanged() -> None:
    for path, digest in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == digest, f"protected runtime changed: {path}"


def test_phase9e_no_implementation_files_added() -> None:
    dev = REPO_ROOT / "scripts/dev"
    # Phase 9E itself is design-only. "*rbac*"/"*policy*" are intentionally not
    # forbidden here: Phase 9F is the explicitly authorized local advisory RBAC
    # policy prototype phase and legitimately owns rbac/policy-named scripts.
    for pattern in ("*phase9e*", "*auth*", "*login*"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9E implementation files ({pattern}): {matches}"
    assert not (REPO_ROOT / "package.json").exists()


# ---------------------------------------------------------------------------
# R. Static safety for new Phase 9E docs/task only
# ---------------------------------------------------------------------------


def test_phase9e_static_safety_scan_new_files_only() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "BEGIN RSA PRIVATE KEY",
        "BEGIN PRIVATE KEY",
        "BEGIN OPENSSH PRIVATE KEY",
        "AWS_SECRET_ACCESS_KEY",
        "OPENAI_API_KEY",
        "ssh-keygen",
        "openssl genrsa",
        "openssl req",
        "openssl enc",
        "gpg --gen-key",
        "curl ",
        "wget ",
        "uvicorn ",
        "fastapi",
        "sqlite3.connect",
        "sqlite3 ",
        "boto3.client",
        "boto3 ",
        "CREATE TABLE",
        "aws kms",
        "cryptography.hazmat",
        "python scripts/dev/execute_single_gate_approval.py",
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh",
        "opa eval",
    )
    for path in (TASK_FILE, DOC):
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        assert not re.search(r"approve_[a-z_]+\s*[:=]\s*true", text, flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# S. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9e_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        suffix = path.suffix.lower()
        assert suffix not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert suffix not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
        assert suffix != ".rego", f"unexpected policy (.rego) file: {path}"
    assert not (REPO_ROOT / "package.json").exists()
    # No RBAC-runtime policy files added under scripts/dev.
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*policy*.json", "*policy*.yaml", "*policy*.yml", "*rbac*.json"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected RBAC policy runtime file ({pattern}): {matches}"
