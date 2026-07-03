from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/062-phase8k-key-management-design.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8J_DOC = REPO_ROOT / "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md"
PHASE8I_DOC = REPO_ROOT / "docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md"
PHASE8F_DOC = REPO_ROOT / "docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md"

NEW_PHASE8K_FILES = (TASK_FILE, DESIGN_DOC)

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py": "1711d387f813b2d8e046704ed7063f1ad7c050413c0b999b7358e0ad6939dc1c",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh": "486258b28e74f9034681e5cc7d3827efddbc19ed6e5f0a6266097d6679560c9d",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py": "c656cb49c645f056be4069e78aa5fdf63cc77d3a6676d2ae5bd96fde2a0d8b31",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh": "9441dc0e5a3fa692fb532c1f1475f89f871b4ed4289bb0d567cf26e6a1305cca",
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py": "3ffab49a1cd16a744a8fe04e788601e567b2191a94a3fbcda55d8da864e5bf82",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh": "2ad91d7551d5c027203772ab6109aebaf08eb21766fbe64fde07208205179649",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8k_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8K file: {path}"


def test_no_phase8k_runtime_script_exists() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase8k*")), "Phase 8K must not add runtime scripts"
    assert not any(scripts_dir.glob("run_phase8k*.sh")), "Phase 8K must not add a shell runner"


def test_phase8k_task_status_token() -> None:
    assert "phase8k_status: success" in _text(TASK_FILE)


def test_phase8k_design_doc_status_tokens() -> None:
    text = _text(DESIGN_DOC)
    for token in (
        "phase8k_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: key_management_design",
        "signing_implementation_status: design_only",
        "signature_runtime_status: not_implemented",
        "signature_verifier_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8k_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "docs/tests design-only",
        "no key management implementation",
        "no key generation",
        "no private key handling",
        "no public key runtime handling beyond design references",
        "no key file creation",
        "no certificate file creation",
        "no signing implementation",
        "no signature verifier implementation",
        "no encryption implementation",
        "no kms/secrets manager implementation",
        "no backend/api/database",
        "no runtime script",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing scope token: {token}"


# ── C. Required design sections ──────────────────────────────────────────────

REQUIRED_DESIGN_SECTIONS = (
    "current key trust boundary",
    "key governance roles",
    "key metadata model",
    "key custody model",
    "key lifecycle model",
    "key creation policy",
    "key activation policy",
    "key rotation policy",
    "key revocation policy",
    "key retirement policy",
    "key compromise policy",
    "key storage options considered",
    "key access control model",
    "key audit trail model",
    "signer-to-key binding model",
    "key policy version model",
    "compatibility with phase 8i signature envelope",
    "compatibility with phase 8j verifier design",
    "failure taxonomy mapping",
    "reviewer action mapping",
    "approval boundary",
    "privacy and secret handling",
    "non-goals",
    "phase 8j verifier design boundary",
    "phase 8i signature design boundary",
    "phase 8h verifier boundary",
    "phase 7d approval boundary",
    "future implementation path",
    "major-phase checkpoint policy",
    "known limitations",
)


def test_phase8k_design_doc_has_required_sections() -> None:
    low = _text(DESIGN_DOC).lower()
    for heading in REQUIRED_DESIGN_SECTIONS:
        assert f"### {heading}" in low, f"missing design section: {heading}"


def test_phase8k_task_has_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    for heading in (
        "purpose",
        "scope",
        "files",
        "status model",
        "key management design objective",
        *REQUIRED_DESIGN_SECTIONS,
        "test strategy",
        "acceptance criteria",
        "focused verification commands",
        "known limitations",
        "final status target",
    ):
        assert f"## {heading}" in low, f"missing task section: {heading}"


# ── D. Key governance roles ──────────────────────────────────────────────────

def test_phase8k_key_governance_roles() -> None:
    text = _text(DESIGN_DOC)
    for role in (
        "key_owner",
        "key_custodian",
        "signer",
        "reviewer",
        "security_owner",
        "system_owner",
        "emergency_revocation_authority",
    ):
        assert role in text, f"missing key governance role: {role}"

    low = text.lower()
    for token in (
        "roles are governance design only",
        "role assignment is not approval",
        "the `signer` role is not approval",
        "the `reviewer` role remains review guidance only",
    ):
        assert token in low, f"missing key governance role rule: {token}"


# ── E. Key metadata ───────────────────────────────────────────────────────────

def test_phase8k_key_metadata_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "key_id",
        "key_version",
        "key_fingerprint",
        "key_algorithm_family",
        "key_purpose",
        "key_scope",
        "key_owner",
        "key_custodian",
        "key_created_at_utc",
        "key_activated_at_utc",
        "key_expires_at_utc",
        "key_rotated_at_utc",
        "key_revoked_at_utc",
        "key_status",
        "key_status_reason",
        "signing_policy_version",
        "rotation_epoch",
        "revocation_reference",
        "approval_boundary_statement",
    ):
        assert field in text, f"missing key metadata field: {field}"


def test_phase8k_key_status_values() -> None:
    text = _text(DESIGN_DOC)
    for value in (
        "proposed",
        "active",
        "rotating",
        "retired",
        "revoked",
        "expired",
        "compromised",
        "unknown",
    ):
        assert value in text, f"missing key_status value: {value}"


def test_phase8k_key_metadata_rules() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "key metadata must not include private key material",
        "key metadata must not include secrets",
        "key metadata must not include approval flags",
        "key metadata is not proof of signer identity without identity assurance",
        "key metadata is not approval",
    ):
        assert token in low, f"missing key metadata rule: {token}"


# ── F. Key custody / storage ─────────────────────────────────────────────────

def test_phase8k_key_custody_models() -> None:
    text = _text(DESIGN_DOC)
    for model in (
        "local_offline_key",
        "os_keychain",
        "hardware_security_key",
        "cloud_kms",
        "enterprise_secrets_manager",
    ):
        assert model in text, f"missing key custody model: {model}"

    low = text.lower()
    for token in (
        "strengths",
        "weaknesses",
        "operational fit",
        "risk profile",
        "recommended phase",
        "implementation status",
        "phase 8k implements none of these custody options",
        "no provider-specific commands are included",
        "no key-generation commands are included",
        "no private key storage examples are included",
    ):
        assert token in low, f"missing key custody/storage token: {token}"


# ── G. Lifecycle / rotation / revocation / retirement / compromise ──────────

def test_phase8k_lifecycle_state_values() -> None:
    text = _text(DESIGN_DOC)
    for value in (
        "proposed",
        "active",
        "rotating",
        "retired",
        "revoked",
        "expired",
        "compromised",
        "unknown",
    ):
        assert value in text, f"missing lifecycle state value: {value}"


def test_phase8k_lifecycle_transitions() -> None:
    text = _text(DESIGN_DOC)
    for transition in (
        "`proposed` -> `active`",
        "`active` -> `rotating`",
        "`rotating` -> `active`",
        "`active` -> `compromised`",
        "`compromised` -> `revoked`",
        "`unknown` -> `manual_review_required`",
    ):
        assert transition in text, f"missing lifecycle transition: {transition}"


def test_phase8k_lifecycle_safety_statements() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "a lifecycle state change must not trigger approval",
        "a lifecycle state change must not trigger the wrapper",
        "a lifecycle state change must not trigger the next gate",
    ):
        assert token in low, f"missing lifecycle safety statement: {token}"


def test_phase8k_rotation_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "rotation_trigger",
        "rotation_cadence",
        "rotation_owner",
        "overlap_window",
        "previous_key_validation_policy",
        "stale_signature_policy",
        "historical_signature_policy",
        "rotation_audit_event",
    ):
        assert field in text, f"missing rotation field: {field}"


def test_phase8k_revocation_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "revocation_trigger",
        "revocation_authority",
        "revocation_effective_at_utc",
        "revocation_reason",
        "affected_signature_review",
        "historical_evidence_treatment",
        "emergency_revocation_path",
        "revocation_audit_event",
    ):
        assert field in text, f"missing revocation field: {field}"


def test_phase8k_retirement_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "retirement_trigger",
        "retirement_owner",
        "retirement_effective_at_utc",
        "historical_validation_policy",
    ):
        assert field in text, f"missing retirement field: {field}"


def test_phase8k_compromise_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "compromise_detection_source",
        "compromise_severity",
        "affected_signature_scope",
        "incident_review_owner",
    ):
        assert field in text, f"missing compromise field: {field}"


def test_phase8k_rotation_revocation_compromise_safety_statements() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "rotation must not delete historical evidence",
        "rotation must not trigger the wrapper or execution",
        "revocation must not delete evidence",
        "revocation must not trigger rollback",
        "revocation must not trigger primitive execution",
        "compromise must not delete evidence",
        "compromise must not trigger automatic rollback or execution",
    ):
        assert token in low, f"missing rotation/revocation/compromise safety statement: {token}"


# ── H. Access control / audit / signer binding ───────────────────────────────

def test_phase8k_access_control_permissions() -> None:
    text = _text(DESIGN_DOC)
    for permission in (
        "key_read_metadata_permission",
        "key_sign_permission",
        "key_rotate_permission",
        "key_revoke_permission",
        "key_retire_permission",
        "key_review_permission",
        "emergency_revoke_permission",
    ):
        assert permission in text, f"missing access control permission: {permission}"

    low = text.lower()
    assert "`key_sign_permission` does not approve product decisions".lower() in low


def test_phase8k_key_audit_trail_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "key_event_id",
        "key_id",
        "key_version",
        "key_event_type",
        "key_status_before",
        "key_status_after",
        "actor_id",
        "actor_role",
        "reason",
        "policy_version",
        "event_timestamp_utc",
        "evidence_reference",
        "approval_boundary_statement",
    ):
        assert field in text, f"missing key audit trail field: {field}"

    for value in (
        "key_creation_requested",
        "key_activated",
        "key_rotated",
        "key_retired",
        "key_revoked",
        "key_expired",
        "key_compromise_reported",
        "key_metadata_reviewed",
    ):
        assert value in text, f"missing key_event_type value: {value}"

    low = text.lower()
    assert "the key audit trail is evidence only" in low


def test_phase8k_signer_to_key_binding_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "signer_id",
        "signer_role",
        "signer_identity_assurance",
        "key_id",
        "key_version",
        "binding_status",
        "binding_created_at_utc",
        "binding_expires_at_utc",
        "binding_policy_version",
    ):
        assert field in text, f"missing signer-to-key binding field: {field}"

    for value in ("proposed", "active", "suspended", "revoked", "expired", "unknown"):
        assert value in text, f"missing binding_status value: {value}"

    low = text.lower()
    for token in (
        "`key_sign_permission` does not approve product decisions",
        "the key audit trail is evidence only",
    ):
        assert token in low, f"missing access control/audit rule: {token}"


# ── I. Compatibility ──────────────────────────────────────────────────────────

def test_phase8k_phase8i_envelope_compatibility_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "key_id",
        "signer_id",
        "signer_role",
        "signer_identity_assurance",
        "signing_policy_version",
        "revocation_status",
        "rotation_epoch",
        "approval_boundary_statement",
    ):
        assert field in text, f"missing Phase 8I envelope compatibility field: {field}"


def test_phase8k_phase8j_verifier_compatibility_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "key_status",
        "key_status_reason",
        "key_fingerprint",
        "key_version",
        "revocation_reference",
        "rotation_epoch",
        "key_policy_version",
    ):
        assert field in text, f"missing Phase 8J verifier compatibility field: {field}"

    low = text.lower()
    for token in (
        "signer-to-key binding",
        "verifier interpretation is evidence only",
        "verifier interpretation is not approval",
    ):
        assert token in low, f"missing compatibility rule: {token}"


# ── J. Failure taxonomy ───────────────────────────────────────────────────────

FAILURE_TYPES = (
    "key_metadata_missing",
    "key_status_unknown",
    "key_not_active",
    "key_revoked",
    "key_expired",
    "key_retired",
    "key_compromised",
    "key_policy_mismatch",
    "key_owner_missing",
    "key_custodian_missing",
    "key_fingerprint_missing",
    "signer_binding_missing",
    "signer_binding_revoked",
    "rotation_epoch_stale",
    "revocation_reference_missing",
    "identity_assurance_insufficient",
)


def test_phase8k_failure_taxonomy_types() -> None:
    text = _text(DESIGN_DOC)
    for failure_type in FAILURE_TYPES:
        assert failure_type in text, f"missing failure type: {failure_type}"


def test_phase8k_failure_taxonomy_severity_incident_and_actions() -> None:
    text = _text(DESIGN_DOC)
    for severity in ("info", "warning", "critical"):
        assert severity in text, f"missing severity value: {severity}"
    for classification in (
        "none",
        "key_metadata_review_required",
        "key_lifecycle_review_required",
        "key_compromise_review_required",
        "signer_binding_review_required",
        "policy_review_required",
    ):
        assert classification in text, f"missing incident classification value: {classification}"
    for action in (
        "no_action_required",
        "manual_review_required",
        "reject_signature_until_resolved",
    ):
        assert action in text, f"missing reviewer action value: {action}"


# ── K. Approval boundary ──────────────────────────────────────────────────────

def test_phase8k_approval_boundary_assertions() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "key metadata is not approval",
        "active key is not approval",
        "key owner is not approval",
        "key custodian is not approval",
        "signer-to-key binding is not approval",
        "key policy eligibility is not approval",
        "signature created using an eligible key is not approval",
        "must not bypass the selected-gate manual approval",
        "must not set approval flags",
        "must not trigger the wrapper",
        "must not trigger the next gate",
        "phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ── L. Documentation regression ──────────────────────────────────────────────

def test_phase8k_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8K" in text
    assert "PHASE8K_KEY_MANAGEMENT_DESIGN.md" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8k_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8k_major_phase_branch_workflow_reference() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "major_phase_branch_workflow" in roadmap or "major phase branch workflow" in roadmap.lower()
    assert "major_phase_branch_workflow" in project_state or "major phase branch workflow" in project_state.lower()


def test_phase8k_phase8j_doc_references() -> None:
    assert "Phase 8K" in _text(PHASE8J_DOC)


def test_phase8k_phase8i_doc_references() -> None:
    assert "Phase 8K" in _text(PHASE8I_DOC)


def test_phase8k_phase8f_doc_references() -> None:
    assert "Phase 8K" in _text(PHASE8F_DOC)


# ── M. Protected files / no implementation ───────────────────────────────────

def test_phase8k_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


def test_phase8k_no_signing_key_or_cert_files_added() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    for pattern in ("*sign*", "*.pem", "*.key", "*.crt", "*.pub", "*.p12", "*.pfx"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8K must not add signing/key/cert files matching {pattern}"

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8k_no_key_management_or_keygen_scripts_added() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    for pattern in ("*key_management*", "*keygen*", "*generate_key*"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8K must not add key-management/keygen scripts matching {pattern}"


def test_phase8k_no_database_backend_api_or_package_json_added() -> None:
    forbidden_suffixes = (".sql", ".sqlite", ".db")
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            raise AssertionError(f"unexpected database file found: {path}")
    assert not (REPO_ROOT / "package.json").exists()


# ── N. Static safety for only the two new Phase 8K files ────────────────────

def test_new_phase8k_files_static_safety() -> None:
    banned = (
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "APPROVE_PROMOTE=1",
        "APPROVE_DECISION=1",
        "APPROVE_FINALIZE=1",
        "export APPROVE_PROMOTE=",
        "export APPROVE_DECISION=",
        "export APPROVE_FINALIZE=",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "AWS_SECRET_ACCESS_KEY",
        "BEGIN PRIVATE KEY",
        "BEGIN RSA PRIVATE KEY",
        "BEGIN OPENSSH PRIVATE KEY",
        "OPENAI_API_KEY",
        "curl ",
        "wget ",
        "uvicorn ",
        "fastapi(",
        "sqlite3.connect",
        "boto3.client",
        "boto3.resource",
        "CREATE TABLE",
        "requests.",
        "socket.",
        "ssh-keygen",
        "openssl genrsa",
        "openssl req",
        "gpg --gen-key",
        "aws kms",
        "cryptography.hazmat",
    )
    for path in NEW_PHASE8K_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
