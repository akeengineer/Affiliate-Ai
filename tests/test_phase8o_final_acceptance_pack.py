from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/066-phase8o-final-acceptance-pack.md"
DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8N_DOC = REPO_ROOT / "docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md"
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

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase8o_required_files_exist() -> None:
    for path in (TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 8O file: {path}"


def test_phase8o_no_builder_or_runner_added() -> None:
    matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase8o*"))
    assert matches == [], f"unexpected Phase 8O runtime files: {matches}"


def test_phase8o_task_status_token() -> None:
    assert "phase8o_status: success" in _text(TASK_FILE)


def test_phase8o_doc_status_tokens() -> None:
    text = _text(DOC)
    for token in (
        "phase8o_status: success",
        "phase7d_runtime_readiness: implemented_manual_gate",
        "durable_audit_store_status: phase8_final_acceptance_pack",
        "signing_implementation_status: prototype_local_only",
        "signature_runtime_status: local_prototype",
        "signature_verifier_runtime_status: local_prototype",
        "key_management_runtime_status: not_implemented",
        "runbook_runtime_status: docs_only",
        "phase8_major_branch_status: ready_for_pr_after_full_suite",
        "major_phase_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


def test_phase8o_doc_scope_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "local-only final acceptance pack",
        "final acceptance report",
        "final scenario matrix",
        "major phase 8 pr readiness checklist",
        "full-suite readiness criteria",
        "missing input scenario",
        "signature not-ready scenario",
        "valid local prototype signature scenario",
        "signature mismatch scenario",
        "signed payload hash mismatch scenario",
        "no new signing model",
        "no new verifier model",
        "no production signing",
        "no production verifier",
        "no key management runtime",
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


def test_phase8o_required_sections() -> None:
    text = _text(DOC)
    for token in (
        "### Current trust boundary",
        "### Final acceptance pack contents",
        "### Acceptance scenario matrix",
        "### Missing input scenario",
        "### Signature not-ready scenario",
        "### Valid local prototype signature scenario",
        "### Signature mismatch scenario",
        "### Signed payload hash mismatch scenario",
        "### Evidence preservation requirements",
        "### Final report schema",
        "### Major Phase 8 PR readiness checklist",
        "### Full-suite requirement",
        "### Merge readiness criteria",
        "### Non-goals",
        "### Phase 8N runbook boundary",
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


def test_phase8o_scenario_matrix_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "missing_input",
        "signature_not_ready",
        "valid_local_prototype_signature",
        "signature_mismatch",
        "signed_payload_hash_mismatch",
        "scenario objective",
        "required prior artifacts",
        "operator action",
        "expected phase 8l status",
        "expected phase 8m status",
        "expected verification_status",
        "expected signature_status",
        "expected incident_classification",
        "expected reviewer_action",
        "expected exit behavior",
        "evidence to preserve",
        "approval boundary reminder",
    ):
        assert token in low, f"missing scenario matrix token: {token}"


def test_phase8o_scenario_specific_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "skipped_missing_signature_inputs",
        "verification_status: empty",
        "signature_status: not_present",
        "exit 0",
        "do not fabricate descriptor/envelope",
        "skipped_missing_prototype_key",
        "skipped_signature_not_ready",
        "verification_status: warning",
        "signature_status: not_ready",
        "signed_local_prototype",
        "verified_local_prototype",
        "verification_status: valid",
        "signature_status: verification_passed",
        "signed_payload_hash_status: match",
        "reviewer_action: no_action_required",
        "failed_signature_mismatch",
        "verification_status: invalid",
        "signature_status: verification_failed",
        "incident_classification: signature_integrity_failure",
        "reviewer_action: reject_signature_until_resolved",
        "nonzero exit",
        "failed_signed_payload_hash_mismatch",
        "signed_payload_hash_status: mismatch",
        "preserve evidence",
        "do not approve",
    ):
        assert token in low, f"missing scenario token: {token}"


def test_phase8o_evidence_preservation_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase 8e export manifest",
        "phase 8g/8h integrity report",
        "phase 8l signed payload descriptor",
        "phase 8l detached signature envelope",
        "phase 8l summary json/md",
        "phase 8m verification json/md",
        "phase 8n runbook reference",
        "scenario name",
        "command metadata without secrets",
        "prototype key presence indicator only, never raw key",
        "expected status",
        "actual status",
        "result",
        "reviewer action",
        "incident classification",
        "limitations",
        "preserve evidence without mutating source artifacts",
        "do not write raw prototype key",
        "do not write vault",
        "do not delete failed evidence",
    ):
        assert token in low, f"missing evidence token: {token}"


def test_phase8o_final_report_schema_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "phase8o_status",
        "durable_audit_store_status",
        "phase7d_runtime_readiness",
        "signing_implementation_status",
        "signature_runtime_status",
        "signature_verifier_runtime_status",
        "key_management_runtime_status",
        "runbook_runtime_status",
        "phase8_major_branch_status",
        "major_phase_branch_workflow",
        "scenario_count",
        "passed_scenarios",
        "failed_scenarios",
        "scenario_results",
        "protected_runtime_status",
        "full_suite_required",
        "full_suite_status",
        "pr_readiness_status",
        "approval_boundary_statement",
        "safety_statement",
        "limitations",
    ):
        assert token in low, f"missing final report schema token: {token}"


def test_phase8o_pr_and_merge_readiness_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "8j checkpoint exists",
        "8k checkpoint exists",
        "8l checkpoint exists",
        "8m checkpoint exists",
        "8n checkpoint exists",
        "8o checkpoint exists",
        "focused 8o tests pass",
        "8m/8l/8k/8j regressions pass",
        "8h/8g regressions pass",
        "8e export regression passes",
        "7d wrapper regression passes",
        "full suite passes",
        "shell runner permissions correct",
        "hardcoded path grep clean",
        "git diff --check clean",
        "no key/cert files",
        "no backend/api/database files",
        "no package.json",
        "no primitive execution",
        "no vault write",
        "no approval inference",
        "pr body states local prototype only",
        "pr body states signature/verified signature/final acceptance is not approval",
        "worktree clean",
        "one major phase 8 pr opened from feature/phase8-signature-governance-completion",
    ):
        assert token in low, f"missing readiness token: {token}"


def test_phase8o_full_suite_requirement_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "full suite must be run after phase 8o focused verification passes",
        "env -u affiliate_require_operator_runtime python -m pytest -q",
        "major phase 8 pr must not be opened until full suite passes",
    ):
        assert token in low, f"missing full-suite token: {token}"


def test_phase8o_approval_boundary_assertions() -> None:
    low = _flat(DOC)
    for token in (
        "signature is not approval",
        "signed export is not approval",
        "verified signature is not approval",
        "verification passed is not approval",
        "signature verifier result is not approval",
        "final acceptance pack is not approval",
        "final acceptance passed is not approval",
        "reviewer action is guidance only",
        "acceptance report is evidence only",
        "acceptance pack must not trigger wrapper",
        "acceptance pack must not trigger next gate",
        "acceptance pack must not set approval flags",
        "approval remains phase 7d selected-gate manual boundary",
    ):
        assert token in low, f"missing approval token: {token}"


def test_phase8o_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 8O" in roadmap
    assert "Phase 8 Final Acceptance Pack" in roadmap
    assert "feature/phase8-signature-governance-completion" in roadmap
    assert "open one major Phase 8 PR after full suite passes" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md" in project_state
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

    for doc in (PHASE8N_DOC, PHASE8M_DOC, PHASE8L_DOC, PHASE8K_DOC, PHASE8J_DOC):
        assert "Phase 8O" in _text(doc), f"missing Phase 8O reference in {doc.name}"


def test_phase8o_protected_runtime_files_exist_and_are_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


def test_phase8o_no_unsafe_implementation_files_added() -> None:
    matches = sorted(p.name for p in (REPO_ROOT / "scripts/dev").glob("*phase8o*"))
    assert matches == [], f"unexpected Phase 8O scripts: {matches}"
    assert not (REPO_ROOT / "package.json").exists()


def test_phase8o_static_safety_scan_new_files_only() -> None:
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


def test_phase8o_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
