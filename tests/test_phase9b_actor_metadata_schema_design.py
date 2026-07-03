from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/068-phase9b-actor-metadata-schema-design.md"
DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
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


def test_phase9b_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9B file: {path}"


def test_phase9b_no_runtime_script_or_runner() -> None:
    py_matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase9b*.py"))
    sh_matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase9b*.sh"))
    assert py_matches == [], f"unexpected Phase 9B runtime script: {py_matches}"
    assert sh_matches == [], f"unexpected Phase 9B shell runner: {sh_matches}"


def test_phase9b_task_status_token() -> None:
    assert "phase9b_status: success" in _text(TASK_FILE)


def test_phase9b_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase9b_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: phase8_final_acceptance_pack",
        "identity_boundary_status: design_only",
        "actor_metadata_schema_status: design_only",
        "actor_metadata_runtime_status: not_implemented",
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


def test_phase9b_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "docs/tests design-only",
        "no runtime scripts",
        "no shell runner",
        "no schema validator implementation",
        "no actor registry",
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


def test_phase9b_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Purpose",
        "### Scope",
        "### Current trust boundary after Phase 9A",
        "### Actor metadata schema overview",
        "### Actor metadata top-level object",
        "### actor_id schema",
        "### actor_type enum",
        "### actor_display_label model",
        "### actor_role_labels model",
        "### actor_identity_assurance enum",
        "### actor_identity_source enum",
        "### actor_session_reference model",
        "### actor_attestation model",
        "### actor_action_scope model",
        "### identity_evidence_reference model",
        "### approval_boundary_statement field",
        "### Operator metadata profile",
        "### Reviewer metadata profile",
        "### Signer metadata profile",
        "### Key governance actor profile",
        "### System/test actor profile",
        "### Schema versioning model",
        "### Schema compatibility model",
        "### Privacy and PII constraints",
        "### Secret handling constraints",
        "### Future validation boundary",
        "### Future registry boundary",
        "### Future audit/report mapping",
        "### Compatibility with Phase 9A",
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
# D. Top-level schema assertions
# ---------------------------------------------------------------------------


def test_phase9b_top_level_schema_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "actor_metadata",
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
        "no runtime validator exists",
        "no json schema file is produced in phase 9b",
        "schema validity is not approval",
    ):
        assert token in low, f"missing top-level schema token: {token}"


# ---------------------------------------------------------------------------
# E. actor_id assertions
# ---------------------------------------------------------------------------


def test_phase9b_actor_id_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "actor_<stable-pseudonymous-id>",
        "lowercase letters",
        "digits",
        "underscore",
        "hyphen",
        "no whitespace",
        "no raw email by default",
        "no secrets",
        "no api keys",
        "no access tokens",
        "no private key fragments",
        "no unnecessary pii",
        "actor_id is stable attribution only",
        "actor_id is not approval",
        "actor_id must not be used as authentication proof",
        "actor_id must not trigger wrapper or primitives",
    ):
        assert token in low, f"missing actor_id token: {token}"


# ---------------------------------------------------------------------------
# F. actor_type and role assertions
# ---------------------------------------------------------------------------


def test_phase9b_actor_type_and_role_assertions() -> None:
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
        "automation_placeholder",
        "operator",
        "automation",
        "test",
        "role label is not runtime permission",
        "role label is not approval",
    ):
        assert token in low, f"missing actor_type/role token: {token}"


# ---------------------------------------------------------------------------
# G. identity assurance / source assertions
# ---------------------------------------------------------------------------


def test_phase9b_identity_assurance_and_source_assertions() -> None:
    low = _flat(DOC)
    for token in (
        # assurance
        "unauthenticated",
        "operator_declared",
        "local_machine_observed",
        "local_config_verified",
        "repository_config_verified",
        "external_identity_verified",
        "enterprise_identity_verified",
        "hardware_backed",
        "current expected values are unauthenticated or operator_declared",
        # source
        "none",
        "terminal_user_label",
        "git_user_config",
        "environment_operator_label",
        "local_config_operator_label",
        "repository_operator_registry",
        "signed_identity_assertion",
        "external_idp_claim",
        "enterprise_directory_claim",
        "hardware_key_attestation",
        "phase 9b implements none of these sources at runtime",
    ):
        assert token in low, f"missing identity assurance/source token: {token}"


# ---------------------------------------------------------------------------
# H. session / attestation / action-scope assertions
# ---------------------------------------------------------------------------


def test_phase9b_session_attestation_action_scope_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "session_id",
        "session_started_at_utc",
        "session_expires_at_utc",
        "session_identity_assurance",
        "session_provider",
        "phase 9b does not implement session runtime",
        "session reference is not approval",
        "attestation is not approval",
        "export_pack_generation",
        "export_integrity_verification",
        "local_signature_creation",
        "local_signature_verification",
        "incident_review",
        "final_acceptance_review",
        "selected_gate_manual_approval",
        "primitive_execution",
        "key_governance_review",
        "test_fixture_generation",
        "action_scope is attribution only",
        "action_scope is not permission",
        "action_scope is not approval",
    ):
        assert token in low, f"missing session/attestation/action-scope token: {token}"


# ---------------------------------------------------------------------------
# I. identity evidence assertions
# ---------------------------------------------------------------------------


def test_phase9b_identity_evidence_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "evidence_type",
        "evidence_reference",
        "evidence_trust_level",
        "evidence_privacy_classification",
        "evidence_timestamp_utc",
        "evidence references must not contain raw secrets",
        "evidence reference is not approval",
    ):
        assert token in low, f"missing identity evidence token: {token}"


# ---------------------------------------------------------------------------
# J. profile assertions
# ---------------------------------------------------------------------------


def test_phase9b_profile_assertions() -> None:
    text = _text(DOC)
    for section in (
        "### Operator metadata profile",
        "### Reviewer metadata profile",
        "### Signer metadata profile",
        "### Key governance actor profile",
        "### System/test actor profile",
    ):
        assert section in text, f"missing profile section: {section}"
    low = _flat(DOC)
    for token in (
        "phase 8l signer_id maps to future signer actor metadata",
        "reviewer action remains guidance only",
        "signer metadata is not non-repudiation",
        "verified signature remains not approval",
        "automation_placeholder is not enabled",
        "system/test actor must not bypass manual approval",
    ):
        assert token in low, f"missing profile token: {token}"


# ---------------------------------------------------------------------------
# K. versioning / compatibility assertions
# ---------------------------------------------------------------------------


def test_phase9b_versioning_and_compatibility_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "actor_schema_version initial value: phase9b.actor_metadata.v1",
        "breaking vs additive fields",
        "approval_boundary_statement preservation",
        "phase 9a actor boundary compatibility",
        "phase 7d approval event compatibility",
        "phase 8l signer metadata compatibility",
        "phase 8m verifier report compatibility",
        "phase 8n runbook reviewer action compatibility",
        "phase 8o final acceptance compatibility",
        "future phase 9c registry compatibility",
        "future phase 9d audit/report attribution compatibility",
    ):
        assert token in low, f"missing versioning/compatibility token: {token}"


# ---------------------------------------------------------------------------
# L. privacy / secret assertions
# ---------------------------------------------------------------------------


def test_phase9b_privacy_and_secret_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "prefer pseudonymous actor_id",
        "avoid email unless future enterprise identity requires it",
        "separate display label from stable actor_id",
        "no secrets in actor metadata",
        "no access tokens",
        "no private key material",
        "no api keys",
        "avoid raw terminal dumps",
        "minimize personal data",
        "support future redaction",
        "actor metadata must never contain raw affiliate_phase8l_prototype_key",
        "actor metadata must never contain private keys",
        "actor metadata must never contain certificates",
        "actor metadata must never contain oauth/oidc/saml tokens",
        "actor metadata must never contain database passwords",
        "actor metadata must never contain affiliate credentials",
    ):
        assert token in low, f"missing privacy/secret token: {token}"


# ---------------------------------------------------------------------------
# M. future boundary assertions
# ---------------------------------------------------------------------------


def test_phase9b_future_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 9b does not implement validation runtime",
        "future validator must be local-first",
        "future validator must not approve",
        "future validator must not trigger wrapper/primitives",
        "belongs to phase 9c or later",
        "registry record is not authentication",
        "registry presence is not approval",
        "future actor metadata is attribution only",
        "audit attribution is not approval",
    ):
        assert token in low, f"missing future boundary token: {token}"


# ---------------------------------------------------------------------------
# N. failure taxonomy assertions
# ---------------------------------------------------------------------------


def test_phase9b_failure_taxonomy_assertions() -> None:
    low = _flat(DOC)
    for token in (
        # failure types
        "actor_schema_version_missing",
        "actor_id_missing",
        "actor_id_invalid_format",
        "actor_type_missing",
        "actor_type_unknown",
        "actor_identity_assurance_missing",
        "actor_identity_assurance_insufficient",
        "actor_identity_source_unknown",
        "actor_role_label_unknown",
        "actor_scope_invalid",
        "actor_session_reference_invalid",
        "identity_evidence_reference_invalid",
        "identity_metadata_contains_secret",
        "identity_metadata_contains_unnecessary_pii",
        "approval_boundary_statement_missing",
        # incident classifications
        "actor_metadata_not_available",
        "actor_metadata_schema_failure",
        "identity_assurance_review_required",
        "identity_policy_review_required",
        "privacy_review_required",
        "actor_scope_review_required",
        # reviewer actions
        "no_action_required",
        "manual_review_required",
        "reject_actor_metadata_until_resolved",
        # severities
        "info",
        "warning",
        "critical",
    ):
        assert token in low, f"missing failure taxonomy token: {token}"


# ---------------------------------------------------------------------------
# O. Approval boundary assertions
# ---------------------------------------------------------------------------


def test_phase9b_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "actor metadata is not approval",
        "actor attribution is not approval",
        "actor_id is not approval",
        "operator metadata is not approval",
        "reviewer metadata is not approval",
        "signer metadata is not approval",
        "identity assurance is not approval",
        "identity source is not approval",
        "session reference is not approval",
        "schema validity is not approval",
        "rbac eligibility is not approval",
        "signature verification remains not approval",
        "final acceptance remains not approval",
        "approval remains phase 7d selected-gate manual boundary",
        "actor metadata must not trigger wrapper",
        "actor metadata must not execute primitives",
        "actor metadata must not trigger next gate",
        "actor metadata must not set approval flags",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ---------------------------------------------------------------------------
# P. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9b_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)

    assert "Phase 9B" in roadmap
    assert "Phase 9C" in roadmap
    assert "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md" in project_state
    assert "actor_metadata_schema_status" in project_state
    assert "actor_metadata_runtime_status" in project_state
    assert "design_only" in project_state
    assert "not_implemented" in project_state
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9A_DOC, PHASE8O_DOC, PHASE8N_DOC, PHASE8K_DOC, PHASE8J_DOC):
        assert "Phase 9B" in _text(doc), f"missing Phase 9B reference in {doc.name}"


# ---------------------------------------------------------------------------
# Q. Protected runtime files unchanged / no implementation files
# ---------------------------------------------------------------------------


def test_phase9b_protected_runtime_files_exist_and_are_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


def test_phase9b_no_implementation_files_added() -> None:
    dev = REPO_ROOT / "scripts/dev"
    # Phase 9B itself is design-only. Patterns are Phase-9B-specific and
    # security-runtime-specific; later phases (e.g. the Phase 9C local operator
    # registry, the Phase 9F local advisory RBAC policy prototype) may
    # legitimately add registry/actor/schema/rbac-named scripts, so those
    # generic names are intentionally not forbidden here.
    for pattern in (
        "*phase9b*",
        "*auth*",
        "*login*",
        "*oauth*",
        "*oidc*",
        "*saml*",
    ):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected Phase 9B implementation files ({pattern}): {matches}"
    assert not (REPO_ROOT / "package.json").exists()


# ---------------------------------------------------------------------------
# R. Static safety for new Phase 9B docs/task only
# ---------------------------------------------------------------------------


def test_phase9b_static_safety_scan_new_files_only() -> None:
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
        "sqlite3.connect",
        "sqlite3 ",
        "boto3.client",
        "boto3 ",
        "CREATE TABLE",
        "aws kms",
        "cryptography.hazmat",
        "python scripts/dev/execute_single_gate_approval.py",
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh",
    )
    for path in (TASK_FILE, DOC):
        text = _text(path)
        for token in banned_literals:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        # AFFILIATE_PHASE8L_PROTOTYPE_KEY is allowed only in secret-handling docs.
        assert "AFFILIATE_PHASE8L_PROTOTYPE_KEY" in text
        assert not re.search(r"approve_[a-z_]+\s*[:=]\s*true", text, flags=re.IGNORECASE)


# ---------------------------------------------------------------------------
# S. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9b_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
    # Phase 9B adds no package.json at the project root.
    assert not (REPO_ROOT / "package.json").exists()
