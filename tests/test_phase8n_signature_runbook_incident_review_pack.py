from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/065-phase8n-signature-runbook-incident-review-pack.md"
DOC = REPO_ROOT / "docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8M_DOC = REPO_ROOT / "docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md"
PHASE8L_DOC = REPO_ROOT / "docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md"
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
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh",
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh",
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
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py": "3ffab49a1cd16a744a8fe04e788601e567b2191a94a3fbcda55d8da864e5bf82",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh": "2ad91d7551d5c027203772ab6109aebaf08eb21766fbe64fde07208205179649",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

NEW_PHASE8N_FILES = (TASK_FILE, DOC, THIS_TEST)
EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase8n_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8N file: {path}"


def test_phase8n_no_runtime_script_exists() -> None:
    matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase8n*"))
    assert matches == [], f"unexpected Phase 8N runtime files: {matches}"


def test_phase8n_task_status_token() -> None:
    assert "phase8n_status: success" in _text(TASK_FILE)


def test_phase8n_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase8n_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: signature_runbook_incident_review_pack",
        "signing_implementation_status: prototype_local_only",
        "signature_runtime_status: local_prototype",
        "signature_verifier_runtime_status: local_prototype",
        "key_management_runtime_status: not_implemented",
        "runbook_runtime_status: docs_only",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


def test_phase8n_doc_scope_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "docs/tests/runbook-pack only",
        "signature incident runbook",
        "incident review pack checklist",
        "operator safe-demo procedure",
        "reviewer decision checklist",
        "escalation matrix",
        "evidence preservation checklist",
        "incident-to-action matrix",
        "phase 8o handoff criteria",
        "no new runtime scripts",
        "no signing implementation",
        "no verifier implementation",
        "no key management implementation",
        "no key generation",
        "no kms/secrets manager",
        "no backend/api/database",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no new mutation path",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing scope token: {token}"


def test_phase8n_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Current trust boundary",
        "### Operator safe-demo procedure",
        "### Reviewer incident review procedure",
        "### Evidence preservation checklist",
        "### Incident classification matrix",
        "### Signature verification outcome matrix",
        "### Missing input procedure",
        "### Missing prototype key procedure",
        "### Signature not-ready procedure",
        "### Invalid descriptor/envelope procedure",
        "### Signed payload hash mismatch procedure",
        "### Signature HMAC mismatch procedure",
        "### Unsupported algorithm/encoding procedure",
        "### Missing signature value procedure",
        "### Key metadata review procedure",
        "### Revocation/rotation review procedure",
        "### Escalation matrix",
        "### Reviewer action checklist",
        "### Approval boundary checklist",
        "### Security/privacy checklist",
        "### Operator mistake recovery",
        "### Phase 8O handoff criteria",
        "### Non-goals",
        "### Phase 8M verifier prototype boundary",
        "### Phase 8L signing prototype boundary",
        "### Phase 8K key management boundary",
        "### Phase 8J verifier design boundary",
        "### Phase 8H verifier boundary",
        "### Phase 8E export boundary",
        "### Phase 7D approval boundary",
        "### Major-phase checkpoint policy",
        "### Known limitations",
    ):
        assert token in text, f"missing section: {token}"


def test_phase8n_operator_safe_demo_procedure() -> None:
    text = _text(DOC)
    for token in (
        "1. Confirm branch and clean working tree.",
        "2. Confirm Phase 8E export pack exists.",
        "3. Confirm Phase 8G/8H integrity report exists.",
        "4. Run Phase 8L signing prototype",
        "5. Confirm Phase 8L outputs under `tmp/phase8l-detached-signature/`.",
        "6. Run Phase 8M verifier prototype",
        "7. Confirm Phase 8M outputs under `tmp/phase8m-detached-signature-verifier/`.",
        "8. Review `signature_verification_status`.",
        "9. Review `verification_status`.",
        "10. Review `signature_status`.",
        "11. Review `incident_classification`.",
        "12. Review `reviewer_action`.",
        "13. Preserve evidence.",
        "14. Do not treat any result as approval.",
        "15. Do not run wrapper or primitives from this runbook.",
    ):
        assert token in text, f"missing safe-demo step: {token}"
    low = text.lower()
    assert "raw key examples" not in low
    assert "real secrets" not in low


def test_phase8n_reviewer_procedure() -> None:
    text = _text(DOC)
    for token in (
        "1. Read Phase 8M verification JSON.",
        "2. Read Phase 8M Markdown summary.",
        "3. Confirm report status tokens.",
        "4. Confirm descriptor/envelope paths.",
        "5. Confirm `output_dir` boundary.",
        "6. Confirm `issues` array.",
        "7. Confirm `failure_count` and `severity_counts`.",
        "8. Confirm `incident_classification`.",
        "9. Confirm `reviewer_action`.",
        "10. Apply incident classification matrix.",
        "11. Apply evidence preservation checklist.",
        "12. Escalate if required.",
        "13. Record review notes outside vault unless future approved store exists.",
        "14. Never approve solely from signature verification.",
        "15. Never trigger Phase 7D wrapper from incident review.",
    ):
        assert token in text, f"missing reviewer step: {token}"


def test_phase8n_evidence_preservation_checklist() -> None:
    low = _flat(DOC)
    for token in (
        "phase 8e export manifest",
        "phase 8g/8h integrity report",
        "phase 8l signed payload descriptor",
        "phase 8l detached signature envelope",
        "phase 8l summary json/md",
        "phase 8m verification json/md",
        "command invocation metadata without secrets",
        "environment key presence indicator only, never raw key",
        "timestamp",
        "operator/reviewer notes",
        "incident classification",
        "reviewer action",
        "affected product/week/gate if available",
        "preserve evidence without mutating source artifacts",
        "do not copy raw prototype key",
        "do not write vault in phase 8n",
        "do not delete failed evidence",
    ):
        assert token in low, f"missing evidence checklist token: {token}"


def test_phase8n_incident_classification_matrix() -> None:
    low = _flat(DOC)
    for token in (
        "none",
        "signature_not_available",
        "signature_integrity_failure",
        "key_lifecycle_review_required",
        "policy_review_required",
        "signer_identity_review_required",
        "replay_review_required",
        "meaning",
        "common trigger",
        "severity",
        "reviewer_action",
        "escalation target",
        "evidence to preserve",
        "approval boundary reminder",
    ):
        assert token in low, f"missing incident matrix token: {token}"


def test_phase8n_signature_verification_outcome_matrix() -> None:
    low = _flat(DOC)
    for token in (
        "skipped_missing_signature_inputs",
        "skipped_signature_not_ready",
        "skipped_signature_not_present",
        "skipped_missing_prototype_key",
        "verified_local_prototype",
        "failed_invalid_input",
        "failed_schema_validation",
        "failed_signed_payload_hash_mismatch",
        "failed_unsupported_algorithm",
        "failed_unsupported_encoding",
        "failed_missing_signature_value",
        "failed_signature_mismatch",
        "verification_status",
        "signature_status",
        "severity",
        "incident_classification",
        "reviewer_action",
        "operator response",
        "reviewer response",
        "escalation requirement",
    ):
        assert token in low, f"missing outcome matrix token: {token}"


def test_phase8n_procedure_specific_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "do not fabricate descriptor/envelope",
        "never write raw key",
        "not_ready as failure of evidence integrity",
        "reject signature until resolved",
        "escalate to security_owner and system_owner",
        "escalate to security_owner",
        "do not introduce external signing tools",
        "preserve envelope",
        "key metadata is not identity proof",
        "do not delete historical evidence",
    ):
        assert token in low, f"missing procedure token: {token}"
    assert "not_ready is not approval" in low


def test_phase8n_escalation_and_reviewer_action_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "operator",
        "reviewer",
        "system_owner",
        "security_owner",
        "key_owner",
        "key_custodian",
        "emergency_revocation_authority",
        "missing signature input",
        "missing prototype key",
        "invalid descriptor/envelope",
        "signed payload hash mismatch",
        "hmac mismatch",
        "unsupported algorithm/encoding",
        "key lifecycle issue",
        "suspected replay",
        "roles are governance labels only until phase 9 identity/rbac",
        "no_action_required",
        "manual_review_required",
        "reject_signature_until_resolved",
        "reviewer action is guidance only",
        "reviewer action is not approval",
        "reviewer action must not execute primitive/wrapper/next gate",
    ):
        assert token in low, f"missing escalation/reviewer token: {token}"


def test_phase8n_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "verified signature is not approval",
        "verification passed is not approval",
        "signature verifier result is not approval",
        "signed export is not approval",
        "local prototype signature is not approval",
        "key metadata is not approval",
        "reviewer action is not approval",
        "runbook action is not approval",
        "incident review is not approval",
        "signature workflow must not bypass selected-gate manual approval",
        "signature workflow must not set approval flags",
        "signature workflow must not trigger wrapper",
        "signature workflow must not trigger next gate",
        "approval remains phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval token: {token}"


def test_phase8n_security_privacy_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "never write raw affiliate_phase8l_prototype_key",
        "never paste raw secrets into reports",
        "never commit key/cert files",
        "never copy private key material",
        "never include affiliate secrets",
        "never include api keys",
        "sanitize terminal logs",
        "preserve evidence without mutation",
        "avoid unnecessary personal data",
        "keep outputs in tmp paths only for current local workflow",
    ):
        assert token in low, f"missing security token: {token}"


def test_phase8n_operator_mistake_recovery_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "wrong key used",
        "missing key",
        "wrong descriptor path",
        "wrong envelope path",
        "stale phase 8l output",
        "overwritten tmp output",
        "invalid json",
        "path rejected by safety guard",
        "accidental command with wrong env",
        "immediate action",
        "evidence preservation",
        "rerun condition",
        "escalation if needed",
        "approval boundary reminder",
    ):
        assert token in low, f"missing recovery token: {token}"


def test_phase8n_phase8o_handoff_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 8l signing prototype focused tests pass",
        "phase 8m verifier prototype focused tests pass",
        "phase 8n runbook tests pass",
        "phase 8g/8h regressions pass",
        "phase 8e export regression passes before phase 8o final acceptance",
        "phase 7d wrapper regression passes before phase 8o final acceptance",
        "no runtime behavior changes in phase 8n",
        "no key/cert files",
        "no backend/api/database",
        "no primitive execution",
        "no vault write",
        "missing input",
        "not_ready",
        "valid",
        "mismatch",
        "hash mismatch scenarios safely",
        "full suite is deferred until phase 8o final acceptance",
    ):
        assert token in low, f"missing handoff token: {token}"


def test_phase8n_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 8N" in roadmap
    assert "checkpoint-only within `feature/phase8-signature-governance-completion`" in roadmap
    assert "Phase 8O Phase 8 Final Acceptance Pack" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md" in project_state
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for text in (_flat(ROADMAP), _flat(PROJECT_STATE)):
        assert "major_phase_branch_workflow" in text or "major phase branch workflow" in text

    for doc in (PHASE8M_DOC, PHASE8L_DOC, PHASE8K_DOC, PHASE8J_DOC):
        assert "Phase 8N" in _text(doc), f"missing Phase 8N reference in {doc.name}"


def test_phase8n_protected_runtime_files_exist_and_are_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


def test_phase8n_no_implementation_files_added() -> None:
    matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase8n*"))
    assert matches == [], f"unexpected Phase 8N scripts: {matches}"
    assert not (REPO_ROOT / "package.json").exists()


def test_phase8n_static_safety_scan_new_files_only() -> None:
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
        "gpg --gen-key",
        "curl ",
        "wget ",
        "uvicorn ",
        "sqlite3.connect",
        "boto3.client",
        "CREATE TABLE",
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "python scripts/dev/execute_single_gate_approval.py",
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh",
        "aws kms",
        "cryptography.hazmat",
        "sqlite3 ",
        "boto3 ",
    )
    for path in (TASK_FILE, DOC):
        text = _text(path)
        for token in banned_literals:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        assert "AFFILIATE_PHASE8L_PROTOTYPE_KEY" in text
        assert not re.search(r"approve_[a-z_]+\s*[:=]\s*true", text, flags=re.IGNORECASE)


def test_phase8n_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
