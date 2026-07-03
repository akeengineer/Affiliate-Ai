from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/060-phase8i-detached-signature-design-finalization.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8H_DOC = REPO_ROOT / "docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md"
PHASE8G_DOC = REPO_ROOT / "docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md"
PHASE8F_DOC = REPO_ROOT / "docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md"

NEW_PHASE8I_FILES = (TASK_FILE, DESIGN_DOC)

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

def test_phase8i_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8I file: {path}"


def test_no_phase8i_runtime_script_exists() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase8i*")), "Phase 8I must not add runtime scripts"
    assert not any(scripts_dir.glob("run_phase8i*.sh")), "Phase 8I must not add a shell runner"


def test_phase8i_status_tokens() -> None:
    assert "phase8i_status: success" in _text(TASK_FILE)
    text = _text(DESIGN_DOC)
    assert "phase8i_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text
    assert "durable_audit_store_status: detached_signature_design_finalized" in text
    assert "signing_implementation_status: design_only" in text
    assert "signature_runtime_status: not_implemented" in text


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8i_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "docs/tests design-only",
        "no signing implementation",
        "no signature verifier implementation",
        "no detached signature runtime implementation",
        "no key generation",
        "no private key handling",
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

def test_phase8i_design_doc_has_required_sections() -> None:
    low = _text(DESIGN_DOC).lower()
    for heading in (
        "current trust boundary",
        "design objectives",
        "signed payload descriptor model",
        "detached signature envelope schema",
        "signing target model",
        "bundle hash signing model",
        "signer metadata model",
        "key identifier model",
        "signature algorithm policy",
        "signing policy version model",
        "key lifecycle model",
        "rotation policy",
        "revocation policy",
        "verification ceremony",
        "signature failure taxonomy",
        "signing event audit trail model",
        "non-repudiation limitation",
        "privacy and secret handling",
        "non-goals",
        "phase 8h verifier boundary",
        "phase 8e export boundary",
        "phase 7d approval boundary",
        "future implementation path",
        "known limitations",
    ):
        assert f"### {heading}" in low, f"missing design section: {heading}"


def test_phase8i_task_has_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    for heading in (
        "purpose",
        "scope",
        "files",
        "status model",
        "detached signature design objective",
        "current trust boundary",
        "signed payload descriptor model",
        "detached signature envelope schema",
        "signing target model",
        "bundle hash signing model",
        "signer metadata model",
        "key identifier model",
        "signature algorithm policy",
        "signing policy version model",
        "key lifecycle model",
        "rotation policy",
        "revocation policy",
        "verification ceremony",
        "signature failure taxonomy",
        "signing event audit trail model",
        "non-repudiation limitation",
        "privacy and secret handling",
        "non-goals",
        "phase 8h verifier boundary",
        "phase 8e export boundary",
        "phase 7d approval boundary",
        "future implementation path",
        "test strategy",
        "acceptance criteria",
        "verification commands",
        "known limitations",
        "final status target",
    ):
        assert f"## {heading}" in low, f"missing task section: {heading}"


# ── D. Signed payload descriptor assertions ─────────────────────────────────

def test_phase8i_signed_payload_descriptor_fields() -> None:
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
        "deterministic field ordering",
        "the payload descriptor is not approval",
        "the payload descriptor must not include private key material",
        "the payload descriptor must not include secrets",
        "the payload descriptor must not include approval flags",
    ):
        assert token in low, f"missing payload descriptor rule: {token}"


# ── E. Detached signature envelope assertions ────────────────────────────────

def test_phase8i_signature_envelope_fields() -> None:
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

    for status in (
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
        assert status in text, f"missing signature_status value: {status}"

    flat = _flat(DESIGN_DOC)
    for token in (
        "the signature envelope must be stored separately from the export manifest",
        "the signature envelope must not mutate source evidence",
        "the signature envelope must not trigger approval",
        "the signature envelope must not trigger the wrapper",
        "the signature envelope must not trigger the next gate",
    ):
        assert token in flat, f"missing envelope rule: {token}"


# ── F. Key lifecycle / rotation / revocation assertions ──────────────────────

def test_phase8i_key_lifecycle_states() -> None:
    text = _text(DESIGN_DOC)
    for state in ("proposed", "active", "rotating", "retired", "revoked", "expired"):
        assert state in text, f"missing key lifecycle state: {state}"
    for status in ("active", "retired", "revoked", "expired", "unknown"):
        assert status in text, f"missing key_status value: {status}"


def test_phase8i_rotation_and_revocation_coverage() -> None:
    flat = _flat(DESIGN_DOC)
    for token in (
        "rotation trigger",
        "rotation cadence",
        "rotation owner",
        "overlap window",
        "stale signature handling",
        "revocation trigger",
        "revocation authority",
        "revocation effective time",
        "affected signature review",
        "emergency revocation path",
    ):
        assert token in flat, f"missing rotation/revocation token: {token}"


def test_phase8i_private_key_and_revocation_safety_statements() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "private keys must never be committed",
        "private keys must never be placed in tmp export packs",
        "private keys must never be written to docs",
        "revocation must not delete evidence",
        "revocation must not trigger rollback",
    ):
        assert token in low, f"missing private-key/revocation safety token: {token}"


# ── G. Signature failure taxonomy assertions ─────────────────────────────────

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


def test_phase8i_failure_taxonomy_types() -> None:
    text = _text(DESIGN_DOC)
    for failure_type in FAILURE_TYPES:
        assert failure_type in text, f"missing failure type: {failure_type}"


def test_phase8i_failure_taxonomy_severity_and_actions() -> None:
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


# ── H. Approval boundary assertions ─────────────────────────────────────────

def test_phase8i_approval_boundary_assertions() -> None:
    flat = _flat(DESIGN_DOC)
    for token in (
        "a signature is not approval",
        "a verified signature is not approval",
        "a signed export is not approval",
        "signer metadata is not approval",
        "reviewer action is not approval",
        "signing must not bypass the selected-gate manual approval boundary",
        "signing must not set approval flags",
        "signing must not trigger the wrapper",
        "signing must not trigger the next gate",
        "approval remains the phase 7d selected-gate manual boundary",
    ):
        assert token in flat, f"missing approval boundary token: {token}"


# ── I. Documentation regression ──────────────────────────────────────────────

def test_phase8i_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8I" in text
    assert "Detached Signature Design Finalization" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8i_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8i_phase8h_doc_references() -> None:
    assert "Phase 8I" in _text(PHASE8H_DOC)


def test_phase8i_phase8g_doc_references() -> None:
    assert "Phase 8I" in _text(PHASE8G_DOC)


def test_phase8i_phase8f_doc_references() -> None:
    assert "Phase 8I" in _text(PHASE8F_DOC)


# ── J. Protected runtime files unchanged / no implementation files ─────────

def test_phase8i_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


def test_phase8i_no_signing_key_or_cert_files_added() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    # Phase 8L adds a sanctioned local-only detached signature prototype runtime
    # whose filenames legitimately contain "signature"; whitelist exactly those.
    sanctioned_signature_scripts = {
        "build_phase8l_detached_signature.py",
        "run_phase8l_detached_signature.sh",
        "verify_phase8m_detached_signature.py",
        "run_phase8m_detached_signature_verifier.sh",
    }
    sign_hits = [p for p in scripts_dir.glob("*sign*") if p.name not in sanctioned_signature_scripts]
    assert not sign_hits, f"Phase 8I must not add signing scripts: {sign_hits}"
    for pattern in ("*.pem", "*.key", "*.crt", "*.pub", "*.p12", "*.pfx"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8I must not add key/cert files matching {pattern}"

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8i_no_database_backend_api_or_package_json_added() -> None:
    forbidden_suffixes = (".sql", ".sqlite", ".db")
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            raise AssertionError(f"unexpected database file found: {path}")
    assert not (REPO_ROOT / "package.json").exists()


# ── K. Static safety for only the two new Phase 8I files ────────────────────

def test_new_phase8i_files_static_safety() -> None:
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
    for path in NEW_PHASE8I_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
