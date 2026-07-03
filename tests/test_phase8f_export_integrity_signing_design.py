from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/057-phase8f-export-integrity-signing-design.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8E_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"
PHASE8D_DOC = REPO_ROOT / "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md"

NEW_PHASE8F_FILES = (TASK_FILE, DESIGN_DOC)

PROTECTED_HASHES = {
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

def test_phase8f_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8F file: {path}"


def test_phase8f_status_tokens() -> None:
    assert "phase8f_status: success" in _text(TASK_FILE)
    text = _text(DESIGN_DOC)
    assert "phase8f_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text
    assert "durable_audit_store_status: export_integrity_signing_design" in text
    assert "signing_implementation_status: design_only" in text


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8f_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "docs/tests design-only",
        "no signing implementation",
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


# ── C. Trust limitation and objectives ───────────────────────────────────────

def test_phase8f_design_doc_trust_limitation_coverage() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "phase 8e creates local export packs",
        "phase 8e does not sign exports",
        "phase 8e does not authenticate operator identity",
        "evidence packaging, not a trusted approval artifact",
    ):
        assert token in low, f"missing trust-limitation token: {token}"


def test_phase8f_design_doc_design_objectives_coverage() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "manifest hash",
        "evidence file hashes",
        "bundle hash",
        "detached signature",
        "public verification metadata",
        "signer identity field",
        "key identifier",
        "signing policy version",
        "reviewer verification result",
        "tamper-evidence failure state",
        "no approval trigger",
        "no next-gate trigger",
    ):
        assert token in low, f"missing design-objective token: {token}"


# ── D. Required design sections ──────────────────────────────────────────────

def test_phase8f_design_doc_has_required_sections() -> None:
    low = _text(DESIGN_DOC).lower()
    for heading in (
        "manifest hash model",
        "evidence file hash model",
        "bundle hash model",
        "detached signature model",
        "signing key ownership policy",
        "key storage options considered",
        "verification ceremony",
        "reviewer trust model",
        "signature failure behavior",
        "tamper-evidence model",
        "privacy and secret handling",
        "non-goals",
        "phase 8e export boundary",
        "phase 7d approval boundary",
        "future implementation path",
        "known limitations",
    ):
        assert f"### {heading}" in low, f"missing design section: {heading}"


def test_phase8f_task_has_required_sections() -> None:
    low = _text(TASK_FILE).lower()
    for heading in (
        "purpose",
        "scope",
        "files",
        "status model",
        "export integrity objective",
        "current export trust limitation",
        "manifest hash model",
        "evidence file hash model",
        "bundle hash model",
        "detached signature model",
        "signing key ownership policy",
        "key storage options considered",
        "verification ceremony",
        "reviewer trust model",
        "signature failure behavior",
        "tamper-evidence model",
        "privacy and secret handling",
        "non-goals",
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


# ── E. Key storage options ───────────────────────────────────────────────────

def test_phase8f_design_doc_key_storage_options() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "local offline key file",
        "os keychain",
        "hardware security key",
        "cloud kms",
        "enterprise secrets manager",
        "strengths",
        "weaknesses",
        "operational fit",
        "recommended phase",
        "phase 8f implements none of these options",
    ):
        assert token in low, f"missing key-storage-option token: {token}"


# ── F. Signature is not approval assertions ─────────────────────────────────

def test_phase8f_design_doc_signature_not_approval_assertions() -> None:
    flat = _flat(DESIGN_DOC)
    for token in (
        "a signature is not approval",
        "a verified export is not approval",
        "reviewer verification is not primitive execution",
        "signing must not bypass the selected-gate manual approval boundary",
        "signing must not set approval flags",
        "signing must not trigger the phase 7d wrapper",
        "signing must not trigger the next gate",
        "approval remains the phase 7d selected-gate manual boundary",
    ):
        assert token in flat, f"missing signature-not-approval token: {token}"


# ── G. Failure behavior assertions ──────────────────────────────────────────

def test_phase8f_design_doc_failure_behavior_assertions() -> None:
    flat = _flat(DESIGN_DOC)
    for token in (
        "a missing signature in the current phase is expected",
        "a future signature mismatch means a tamper-evidence failure",
        "a key id mismatch requires manual review",
        "an expired or revoked key requires manual review",
        "an unknown signer requires manual review",
        "a hash mismatch (manifest, evidence, or bundle) requires manual review",
        "a verification failure must not auto-delete evidence",
        "a verification failure must not retry execution",
        "a verification failure must not trigger rollback",
        "a verification failure must not trigger the next gate",
    ):
        assert token in flat, f"missing failure-behavior token: {token}"


# ── H. Documentation regression ──────────────────────────────────────────────

def test_phase8f_roadmap_references() -> None:
    text = _text(ROADMAP)
    assert "Phase 8F" in text
    assert "Export Integrity / Signing Design" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_phase8f_project_state_references() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8f_phase8e_doc_references() -> None:
    assert "Phase 8F" in _text(PHASE8E_DOC)


def test_phase8f_phase8d_doc_references() -> None:
    assert "Phase 8F" in _text(PHASE8D_DOC)


# ── I. Protected runtime files unchanged / no implementation files ─────────

def test_phase8f_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256(path) == expected_hash, f"protected runtime changed: {path}"


def test_phase8f_no_runtime_signing_or_key_files_added() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("*phase8f*")), "Phase 8F must not add runtime scripts"

    sanctioned_signing_runtime = {
        "build_phase8l_detached_signature.py",
        "run_phase8l_detached_signature.sh",
        "run_phase8m_detached_signature_verifier.sh",
        "verify_phase8m_detached_signature.py",
    }
    observed_signing_runtime = {path.name for path in scripts_dir.glob("*sign*")}
    assert observed_signing_runtime == sanctioned_signing_runtime, (
        "Phase 8F design-only guard must allow only the sanctioned "
        "Phase 8L/8M local prototype signing/verifier runtime files"
    )

    for pattern in ("*.pem", "*.key", "*.crt", "*.pub", "*.p12", "*.pfx"):
        assert not any(scripts_dir.glob(pattern)), f"Phase 8F must not add signing/key/cert files matching {pattern}"

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"


def test_phase8f_no_database_backend_api_files_added() -> None:
    forbidden_suffixes = (".sql", ".sqlite", ".db")
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "node_modules", ".venv", "tmp", "vault"} for part in path.parts):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            raise AssertionError(f"unexpected database file found: {path}")
    assert not (REPO_ROOT / "package.json").exists()


# ── J. Static safety for only the two new Phase 8F files ────────────────────

def test_new_phase8f_files_static_safety() -> None:
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
    for path in NEW_PHASE8F_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
