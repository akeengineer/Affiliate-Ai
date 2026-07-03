from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/061-phase8j-detached-signature-verifier-design.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8I_DOC = REPO_ROOT / "docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md"
PHASE8H_DOC = REPO_ROOT / "docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md"
PHASE8G_DOC = REPO_ROOT / "docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md"

NEW_PHASE8J_FILES = (TASK_FILE, DESIGN_DOC)

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

def test_phase8j_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8J file: {path}"


def test_no_phase8j_runtime_script_exists() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase8j*")), "Phase 8J must not add runtime scripts"
    assert not any(scripts_dir.glob("run_phase8j*.sh")), "Phase 8J must not add a shell runner"


def test_phase8j_task_status_token() -> None:
    assert "phase8j_status: success" in _text(TASK_FILE)


def test_phase8j_design_doc_status_tokens() -> None:
    text = _text(DESIGN_DOC)
    for token in (
        "phase8j_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: detached_signature_verifier_design",
        "signing_implementation_status: design_only",
        "signature_runtime_status: not_implemented",
        "signature_verifier_runtime_status: not_implemented",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8j_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "docs/tests design-only",
        "no signature verifier implementation",
        "no signing implementation",
        "no detached signature runtime implementation",
        "no key generation",
        "no private key handling",
        "no encryption implementation",
        "no kms implementation",
        "no secrets manager implementation",
        "no backend",
        "no shell runner",
        "no runtime wrapper behavior change",
        "no primitive execution",
        "no vault reads/writes",
        "no next-gate automation",
        "chain execution",
        "no mutation intent",
    ):
        assert token in low, f"missing scope token: {token}"


# ── C. Required design sections ──────────────────────────────────────────────

def test_phase8j_design_doc_has_required_sections() -> None:
    low = _text(DESIGN_DOC).lower()
    for heading in (
        "purpose",
        "scope",
        "current trust boundary",
        "design objectives",
        "signature verifier input contract",
        "signature envelope validation model",
        "signed payload descriptor validation model",
        "signed payload hash validation model",
        "bundle hash and manifest hash cross-check model",
        "key metadata validation model",
        "signer identity assurance interpretation",
        "revocation and rotation interpretation model",
        "signature status transition model",
        "verification status model",
        "failure taxonomy mapping",
        "reviewer action mapping",
        "verification report schema",
        "approval boundary",
        "non-repudiation limitation",
        "privacy and secret handling",
        "non-goals",
        "phase 8i design boundary",
        "phase 8h verifier boundary",
        "phase 8e export boundary",
        "phase 7d approval boundary",
        "future implementation path",
        "major-phase checkpoint policy",
        "known limitations",
    ):
        assert f"### {heading}" in low, f"missing design section: {heading}"


def test_phase8j_task_has_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    for heading in (
        "purpose",
        "scope",
        "files",
        "status model",
        "detached signature verifier design objective",
        "current trust boundary",
        "signature verifier input contract",
        "signature envelope validation model",
        "signed payload descriptor validation model",
        "signed payload hash validation model",
        "bundle hash and manifest hash cross-check model",
        "key metadata validation model",
        "signer identity assurance interpretation",
        "revocation and rotation interpretation model",
        "signature status transition model",
        "verification status model",
        "failure taxonomy mapping",
        "reviewer action mapping",
        "verification report schema",
        "approval boundary",
        "non-repudiation limitation",
        "privacy and secret handling",
        "non-goals",
        "phase 8i design boundary",
        "phase 8h verifier boundary",
        "phase 8e export boundary",
        "phase 7d approval boundary",
        "future implementation path",
        "test strategy",
        "acceptance criteria",
        "focused verification commands",
        "major-phase checkpoint policy",
        "known limitations",
        "final status target",
    ):
        assert f"## {heading}" in low, f"missing task section: {heading}"


# ── D. Verifier input contract assertions ────────────────────────────────────

def test_phase8j_input_contract_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "detached signature envelope",
        "signed payload descriptor",
        "phase 8e export manifest",
        "phase 8g/8h export integrity verification report",
        "key metadata record",
        "revocation metadata",
        "rotation metadata",
        "signing policy metadata",
        "evidence",
        "no private keys",
        "inputs must not include private keys",
        "no secrets",
        "inputs must not include secrets",
        "no approval flags",
        "inputs must not include approval flags",
        "must not mutate",
        "must not trigger approval",
    ):
        assert token in low, f"missing input contract token: {token}"


# ── E. Signature envelope validation assertions ──────────────────────────────

def test_phase8j_signature_envelope_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "signature_schema_version",
        "signed_payload_sha256",
        "signed_payload_descriptor_path",
        "detached_signature_path",
        "signature_algorithm",
        "signature_encoding",
        "key_id",
        "signer_id",
        "signer_role",
        "signer_identity_assurance",
        "signing_policy_version",
        "signing_timestamp_utc",
        "signature_status",
        "verification_status",
        "revocation_status",
        "rotation_epoch",
        "approval_boundary_statement",
    ):
        assert field in text, f"missing signature envelope field: {field}"

    low = text.lower()
    for token in (
        "schema version supported",
        "algorithm allowed by policy",
        "encoding allowed by policy",
        "`key_id` present",
        "signer metadata present",
        "path separation",
        "no private key material",
        "no mutation intent",
    ):
        assert token in low, f"missing envelope validation rule: {token}"


# ── F. Signed payload descriptor validation assertions ───────────────────────

def test_phase8j_payload_descriptor_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "payload_schema_version",
        "export_manifest_path",
        "export_manifest_sha256",
        "bundle_hash",
        "computed_manifest_hash",
        "report_schema_version",
        "issue_taxonomy_version",
        "compatibility_matrix_version",
        "verifier_hardening_status",
        "verification_status",
        "compatibility_result",
        "incident_classification",
        "reviewer_action",
        "reviewer_action_required",
        "generated_from_phase",
        "generated_by_tool",
        "created_at_utc",
    ):
        assert field in text, f"missing payload descriptor field: {field}"

    low = text.lower()
    for token in (
        "canonical json",
        "deterministic ordering",
        "references the phase 8h report schema",
        "descriptor is not approval",
    ):
        assert token in low, f"missing payload descriptor rule: {token}"


# ── G. Hash/cross-check assertions ───────────────────────────────────────────

def test_phase8j_hash_and_cross_check_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "signed_payload_sha256",
        "computed",
        "export_manifest_sha256",
        "computed_manifest_hash",
        "bundle_hash",
        "mismatch",
        "not approval",
        "must not trigger the wrapper",
        "must not trigger the next gate",
    ):
        assert token in low, f"missing hash/cross-check token: {token}"


# ── H. Key/signature status assertions ───────────────────────────────────────

def test_phase8j_key_status_values() -> None:
    text = _text(DESIGN_DOC)
    for status in ("active", "retired", "revoked", "expired", "unknown"):
        assert status in text, f"missing key_status value: {status}"


def test_phase8j_signer_identity_assurance_values() -> None:
    text = _text(DESIGN_DOC)
    for value in (
        "unauthenticated",
        "operator_declared",
        "local_registry_verified",
        "enterprise_identity_verified",
        "hardware_backed",
    ):
        assert value in text, f"missing signer_identity_assurance value: {value}"


def test_phase8j_revocation_and_rotation_values() -> None:
    text = _text(DESIGN_DOC)
    for value in ("not_checked", "not_revoked", "revoked", "unknown"):
        assert value in text, f"missing revocation_status value: {value}"
    for value in ("current_epoch", "previous_epoch_allowed", "stale_epoch", "unknown_epoch"):
        assert value in text, f"missing rotation value: {value}"


def test_phase8j_signature_status_transition_values() -> None:
    text = _text(DESIGN_DOC)
    for value in (
        "not_present",
        "present",
        "malformed",
        "unsupported_algorithm",
        "key_not_found",
        "verification_failed",
        "verification_passed",
        "revoked_key",
        "expired_key",
        "policy_mismatch",
    ):
        assert value in text, f"missing signature status value: {value}"


def test_phase8j_verification_status_values() -> None:
    text = _text(DESIGN_DOC)
    for value in ("empty", "valid", "warning", "invalid"):
        assert value in text, f"missing verification_status value: {value}"


# ── I. Failure taxonomy assertions ───────────────────────────────────────────

FAILURE_TYPES = (
    "signature_missing",
    "signature_malformed",
    "unsupported_algorithm",
    "signed_payload_hash_mismatch",
    "bundle_hash_mismatch",
    "manifest_hash_mismatch",
    "key_not_found",
    "key_revoked",
    "key_expired",
    "key_status_unknown",
    "signing_policy_mismatch",
    "signer_identity_unverified",
    "signature_verification_failed",
    "signature_replay_suspected",
    "signature_metadata_incomplete",
)


def test_phase8j_failure_taxonomy_types() -> None:
    text = _text(DESIGN_DOC)
    for failure_type in FAILURE_TYPES:
        assert failure_type in text, f"missing failure type: {failure_type}"


def test_phase8j_failure_taxonomy_severity_and_actions() -> None:
    text = _text(DESIGN_DOC)
    for severity in ("info", "warning", "critical"):
        assert severity in text
    for action in ("no_action_required", "manual_review_required", "reject_signature_until_resolved"):
        assert action in text, f"missing reviewer action value: {action}"
    for classification in (
        "none",
        "signature_not_available",
        "signature_integrity_failure",
        "key_lifecycle_review_required",
        "policy_review_required",
        "signer_identity_review_required",
        "replay_review_required",
    ):
        assert classification in text, f"missing incident classification value: {classification}"


# ── J. Verification report schema assertions ─────────────────────────────────

def test_phase8j_verification_report_schema_fields() -> None:
    text = _text(DESIGN_DOC)
    for field in (
        "phase8j_status",
        "signature_verifier_runtime_status",
        "signing_implementation_status",
        "signature_verification_status",
        "signature_status",
        "verification_status",
        "signature_schema_version",
        "signed_payload_sha256",
        "computed_signed_payload_sha256",
        "bundle_hash_status",
        "manifest_hash_status",
        "key_status",
        "revocation_status",
        "rotation_status",
        "signer_identity_assurance",
        "failure_count",
        "severity_counts",
        "incident_classification",
        "reviewer_action",
        "reviewer_action_required",
        "approval_boundary_statement",
        "issues",
        "safety_statement",
        "limitations",
    ):
        assert field in text, f"missing verification report field: {field}"

    low = text.lower()
    for token in (
        "deterministic",
        "must not contain private keys",
        "must not contain secrets",
        "must not contain approval flags",
    ):
        assert token in low, f"missing verification report rule: {token}"


# ── K. Approval boundary assertions ──────────────────────────────────────────

def test_phase8j_approval_boundary_assertions() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "a signature verifier result is not approval",
        "a verified signature is not approval",
        "a signed export is not approval",
        "signer metadata is not approval",
        "reviewer action is not approval",
        "must not bypass the selected-gate manual",
        "must not set or imply approval flags",
        "must not trigger wrapper execution",
        "must not trigger next gate",
        "phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval boundary token: {token}"


# ── L. Documentation regression ──────────────────────────────────────────────

def test_phase8j_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8J" in text
    assert "PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8j_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8j_major_phase_branch_workflow_reference() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "major_phase_branch_workflow" in roadmap or "major phase branch workflow" in roadmap.lower()
    assert "major_phase_branch_workflow" in project_state or "major phase branch workflow" in project_state.lower()


def test_phase8j_phase8i_doc_references() -> None:
    assert "Phase 8J" in _text(PHASE8I_DOC)


def test_phase8j_phase8h_doc_references() -> None:
    assert "Phase 8J" in _text(PHASE8H_DOC)


def test_phase8j_phase8g_doc_references() -> None:
    assert "Phase 8J" in _text(PHASE8G_DOC)


# ── M. Protected runtime files unchanged / no implementation files ─────────

def test_phase8j_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


def test_phase8j_no_signing_key_or_cert_files_added() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    # Phase 8L adds a sanctioned local-only detached signature prototype runtime
    # whose filenames legitimately contain "signature"; whitelist exactly those.
    sanctioned_signature_scripts = {
        "build_phase8l_detached_signature.py",
        "run_phase8l_detached_signature.sh",
    }
    sign_hits = [p for p in scripts_dir.glob("*sign*") if p.name not in sanctioned_signature_scripts]
    assert not sign_hits, f"Phase 8J must not add signing scripts: {sign_hits}"
    for pattern in ("*.pem", "*.key", "*.crt", "*.pub", "*.p12", "*.pfx"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8J must not add key/cert files matching {pattern}"

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8j_no_database_backend_api_or_package_json_added() -> None:
    forbidden_suffixes = (".sql", ".sqlite", ".db")
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            raise AssertionError(f"unexpected database file found: {path}")
    assert not (REPO_ROOT / "package.json").exists()


# ── N. Static safety for only the two new Phase 8J files ────────────────────

def test_new_phase8j_files_static_safety() -> None:
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
    for path in NEW_PHASE8J_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
