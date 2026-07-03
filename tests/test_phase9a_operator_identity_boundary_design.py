from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/067-phase9a-operator-identity-boundary-design.md"
DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
PHASE8N_DOC = REPO_ROOT / "docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md"
PHASE8K_DOC = REPO_ROOT / "docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md"
PHASE8J_DOC = REPO_ROOT / "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md"

PROTECTED_RUNTIME_FILES = (
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh",
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh",
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py",
)

PROTECTED_HASHES = {
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


def test_phase9a_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9A file: {path}"


def test_phase9a_no_runtime_script_or_runner() -> None:
    py_matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase9a*.py"))
    sh_matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase9a*.sh"))
    assert py_matches == [], f"unexpected Phase 9A runtime script: {py_matches}"
    assert sh_matches == [], f"unexpected Phase 9A shell runner: {sh_matches}"


def test_phase9a_task_status_token() -> None:
    assert "phase9a_status: success" in _text(TASK_FILE)


def test_phase9a_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase9a_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: phase8_final_acceptance_pack",
        "identity_boundary_status: design_only",
        "identity_runtime_status: not_implemented",
        "rbac_runtime_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "operator_identity_assurance_status: unauthenticated_or_operator_declared",
        "signing_implementation_status: prototype_local_only",
        "signature_runtime_status: local_prototype",
        "signature_verifier_runtime_status: local_prototype",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9a_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "docs/tests design-only",
        "no runtime scripts",
        "no shell runner",
        "no authentication runtime",
        "no rbac runtime",
        "no login",
        "no oauth/oidc/saml",
        "no backend/api/database",
        "no key management runtime",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
    ):
        assert token in low, f"missing scope safety token: {token}"


# ---------------------------------------------------------------------------
# C. Required sections
# ---------------------------------------------------------------------------


def test_phase9a_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Purpose",
        "### Scope",
        "### Current trust boundary after Phase 8",
        "### Actor identity model",
        "### Operator ID model",
        "### Reviewer ID model",
        "### Signer ID model",
        "### Actor ID model",
        "### Service/system actor model",
        "### Identity assurance levels",
        "### Identity evidence model",
        "### Identity-to-action attribution model",
        "### Approval actor attribution boundary",
        "### Signature actor attribution boundary",
        "### Reviewer action attribution boundary",
        "### Key governance role attribution boundary",
        "### Future RBAC boundary",
        "### Future authentication provider boundary",
        "### Future session boundary",
        "### Future audit event actor fields",
        "### Privacy and PII minimization",
        "### Non-repudiation limitations",
        "### Migration path",
        "### Compatibility with Phase 7D",
        "### Compatibility with Phase 8L/8M/8N/8O",
        "### Failure taxonomy",
        "### Reviewer action mapping",
        "### Approval boundary",
        "### Non-goals",
        "### Known limitations",
    ):
        assert token in text, f"missing section: {token}"


# ---------------------------------------------------------------------------
# D. Actor model assertions
# ---------------------------------------------------------------------------


def test_phase9a_actor_model_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "human_operator",
        "reviewer",
        "signer",
        "key_owner",
        "key_custodian",
        "security_owner",
        "system_owner",
        "emergency_revocation_authority",
        "system_process",
        "test_fixture",
        "purpose",
        "allowed interpretation",
        "forbidden interpretation",
        "identity assurance expectation",
        "audit attribution use",
        "approval boundary",
    ):
        assert token in low, f"missing actor model token: {token}"


# ---------------------------------------------------------------------------
# E. Identity models assertions
# ---------------------------------------------------------------------------


def test_phase9a_identity_models_assertions() -> None:
    low = _flat(DOC)
    for token in (
        # operator_id fields
        "operator_id",
        "operator_display_label",
        "operator_role_label",
        "operator_identity_assurance",
        "operator_identity_source",
        "operator_session_reference",
        "operator_attestation",
        "operator_action_scope",
        "operator_timestamp_utc",
        # reviewer_id fields
        "reviewer_id",
        "reviewer_display_label",
        "reviewer_role_label",
        "reviewer_review_scope",
        "reviewer_action",
        "reviewer_timestamp_utc",
        # signer_id fields
        "signer_id",
        "signer_display_label",
        "signer_role",
        "signer_to_key_binding_reference",
        "signing_policy_version",
        # normalized actor_id fields
        "actor_id",
        "actor_type",
        "actor_display_label",
        "actor_role_labels",
        "actor_action_scope",
        "actor_session_reference",
        "actor_attestation",
        "actor_timestamp_utc",
        "approval_boundary_statement",
        # service/system rules
        "automation actor placeholder",
        "automation actor is not enabled in phase 9a",
        # not-approval rules
        "operator_id is not approval",
        "reviewer_id is not approval",
        "signer_id is not approval",
        "actor_id is attribution only",
        "system actor must not be used to bypass manual approval",
    ):
        assert token in low, f"missing identity model token: {token}"


# ---------------------------------------------------------------------------
# F. Identity assurance assertions
# ---------------------------------------------------------------------------


def test_phase9a_identity_assurance_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "unauthenticated",
        "operator_declared",
        "local_machine_observed",
        "local_config_verified",
        "repository_config_verified",
        "external_identity_verified",
        "enterprise_identity_verified",
        "hardware_backed",
        "meaning",
        "evidence source",
        "allowed use",
        "forbidden use",
        "non-repudiation strength",
        "recommended phase",
        "current expected level is unauthenticated or operator_declared",
    ):
        assert token in low, f"missing identity assurance token: {token}"


# ---------------------------------------------------------------------------
# G. Identity evidence assertions
# ---------------------------------------------------------------------------


def test_phase9a_identity_evidence_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "terminal_user_label",
        "git_user_config",
        "environment_operator_label",
        "local_config_operator_label",
        "repository_operator_registry",
        "signed_identity_assertion",
        "external_idp_claim",
        "enterprise_directory_claim",
        "hardware_key_attestation",
        "trust strength",
        "privacy risk",
        "mutation risk",
        "audit use",
        "phase availability",
        "phase 9a implements none of them at runtime",
    ):
        assert token in low, f"missing identity evidence token: {token}"


# ---------------------------------------------------------------------------
# H. Attribution boundary assertions
# ---------------------------------------------------------------------------


def test_phase9a_attribution_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "export pack generation",
        "export integrity verification",
        "local signing prototype",
        "local verifier prototype",
        "runbook review",
        "final acceptance review",
        "selected-gate manual approval",
        "primitive execution",
        "identity attribution records who performed or reviewed an action, not whether the action is approved",
        "approval actor fields are future-only",
        "phase 9a does not implement approval event changes",
        "signature actor attribution must not trigger wrapper or next gate",
        "reviewer action remains guidance only",
    ):
        assert token in low, f"missing attribution boundary token: {token}"


# ---------------------------------------------------------------------------
# I. RBAC / auth / session boundary assertions
# ---------------------------------------------------------------------------


def test_phase9a_rbac_auth_session_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "permission",
        "role",
        "policy",
        "subject",
        "resource",
        "action",
        "decision",
        "obligation",
        "audit event",
        "phase 9a does not implement rbac",
        "rbac decision is not product approval",
        "local config identity",
        "os identity",
        "git identity",
        "oidc provider",
        "saml provider",
        "enterprise directory",
        "hardware-backed identity",
        "phase 9a implements none of these providers",
        "no oauth/oidc/saml runtime",
        "no user store",
        "no session store",
        "session_id",
        "session is not approval",
    ):
        assert token in low, f"missing rbac/auth/session token: {token}"


# ---------------------------------------------------------------------------
# J. Privacy and non-repudiation assertions
# ---------------------------------------------------------------------------


def test_phase9a_privacy_and_non_repudiation_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "do not store unnecessary personal data",
        "prefer pseudonymous operator_id",
        "avoid email unless required by future enterprise identity",
        "never store secrets as identity metadata",
        "sanitize logs",
        "separate display labels from stable identifiers",
        "unauthenticated identity provides no strong non-repudiation",
        "operator_declared identity provides weak attribution only",
        "git config identity is not proof of human identity",
        "enterprise non-repudiation requires authenticated identity, governed key custody, policy, audit trail, and revocation/rotation controls",
        "phase 9a implements none of the runtime controls",
    ):
        assert token in low, f"missing privacy/non-repudiation token: {token}"


# ---------------------------------------------------------------------------
# K. Migration path assertions
# ---------------------------------------------------------------------------


def test_phase9a_migration_path_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "design-only identity boundary",
        "actor metadata schema design",
        "local operator registry prototype",
        "actor attribution in audit/report outputs",
        "rbac design",
        "local rbac policy prototype",
        "external identity provider integration",
        "all later phases must preserve the phase 7d approval boundary",
    ):
        assert token in low, f"missing migration token: {token}"


# ---------------------------------------------------------------------------
# L. Compatibility assertions
# ---------------------------------------------------------------------------


def test_phase9a_compatibility_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 7d remains the selected-gate manual approval runtime",
        "phase 9a does not modify phase 7d",
        "phase 8l signer_id remains local prototype metadata",
        "phase 8m reviewer/signer metadata remains evidence only",
        "phase 8n reviewer action remains guidance only",
        "phase 8o final acceptance remains evidence only",
        "phase 9a does not modify phase 8 runtime",
    ):
        assert token in low, f"missing compatibility token: {token}"


# ---------------------------------------------------------------------------
# M. Failure taxonomy assertions
# ---------------------------------------------------------------------------


def test_phase9a_failure_taxonomy_assertions() -> None:
    low = _flat(DOC)
    for token in (
        # failure types
        "actor_missing",
        "actor_ambiguous",
        "identity_assurance_missing",
        "identity_assurance_insufficient",
        "actor_role_unknown",
        "actor_scope_mismatch",
        "session_missing",
        "session_expired",
        "provider_unavailable",
        "identity_claim_unverified",
        "identity_metadata_contains_secret",
        "identity_metadata_contains_unnecessary_pii",
        # incident classifications
        "none",
        "identity_not_available",
        "identity_assurance_review_required",
        "identity_policy_review_required",
        "privacy_review_required",
        "actor_scope_review_required",
        # reviewer actions
        "no_action_required",
        "manual_review_required",
        "reject_identity_until_resolved",
        # severities
        "info",
        "warning",
        "critical",
    ):
        assert token in low, f"missing failure taxonomy token: {token}"


# ---------------------------------------------------------------------------
# N. Approval boundary assertions
# ---------------------------------------------------------------------------


def test_phase9a_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "operator identity is not approval",
        "authenticated identity is not approval",
        "reviewer identity is not approval",
        "signer identity is not approval",
        "actor attribution is not approval",
        "rbac eligibility is not approval",
        "identity assurance is not approval",
        "key ownership is not approval",
        "signature verification remains not approval",
        "final acceptance remains not approval",
        "approval remains phase 7d selected-gate manual boundary",
        "identity metadata must not trigger wrapper",
        "identity metadata must not execute primitives",
        "identity metadata must not trigger next gate",
        "identity metadata must not set approval flags",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ---------------------------------------------------------------------------
# O. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9a_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)

    assert "Phase 9A" in roadmap
    assert "Phase 9B" in roadmap
    assert "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md" in project_state
    assert "identity_boundary_status" in project_state
    assert "design_only" in project_state
    assert "not_implemented" in project_state
    assert "unauthenticated_or_operator_declared" in project_state
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE8O_DOC, PHASE8N_DOC, PHASE8K_DOC, PHASE8J_DOC):
        assert "Phase 9A" in _text(doc), f"missing Phase 9A reference in {doc.name}"


# ---------------------------------------------------------------------------
# P. Protected runtime files unchanged / no implementation files
# ---------------------------------------------------------------------------


def test_phase9a_protected_runtime_files_exist_and_are_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


def test_phase9a_no_implementation_files_added() -> None:
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*phase9a*", "*identity*", "*rbac*", "*auth*", "*login*", "*oauth*", "*oidc*", "*saml*"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9A implementation files ({pattern}): {matches}"
    assert not (REPO_ROOT / "package.json").exists()


# ---------------------------------------------------------------------------
# Q. Static safety for new Phase 9A docs/task only
# ---------------------------------------------------------------------------


def test_phase9a_static_safety_scan_new_files_only() -> None:
    banned_literals = (
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
        "gpg --sign",
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
    )
    for path in (TASK_FILE, DOC):
        text = _text(path)
        for token in banned_literals:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        assert not re.search(r"approve_[a-z_]+\s*[:=]\s*true", text, flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# R. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9a_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
    # Phase 9A adds no package.json at the project root.
    assert not (REPO_ROOT / "package.json").exists()
