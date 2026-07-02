from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/054-phase8c-audit-store-verifier-reporting.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md"
VERIFIER_SCRIPT = REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8B_DOC = REPO_ROOT / "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md"
PHASE8A_DOC = REPO_ROOT / "docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md"

NEW_PHASE8C_FILES = (TASK_FILE, DESIGN_DOC, VERIFIER_SCRIPT, RUNNER_SCRIPT)

TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase8c-test-input"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
    REPO_ROOT / "scripts/dev/run_phase7g_safe_demo_pack.sh": "be5f5410d4f4e66b61bda8ba0d4c9861b51f2afb8cb8c099b5c1c60ac6630abb",
    REPO_ROOT / "scripts/dev/build_phase7g_operator_acceptance_summary.py": "9dc7b38a355d8c9d9a5e57c43524308567c0ccf8130449b1a895c5281fc042cf",
    REPO_ROOT / "scripts/dev/promote_product_candidates.py": "496055979f5492389237662d756c4a51a6428da60c804e4ccba72efff0f1ff6e",
    REPO_ROOT / "scripts/dev/create_decision.py": "ac27e4300d617f60e45799980fead1f7e3a09f5f1f083ef5d42c1d327ded4613",
    REPO_ROOT / "scripts/dev/finalize_decision.py": "1c829e797b49ca8a3cff875a1609a06f093ca104873fa20597784a8adac3d177",
}

# Import the verifier module directly (no side effects at import time; the
# CLI entrypoint is guarded by `if __name__ == "__main__"`) so tests share
# the implementation's own field list and hash function instead of a
# hand-duplicated copy.
_spec = importlib.util.spec_from_file_location("phase8c_verifier_module", VERIFIER_SCRIPT)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
REQUIRED_REPORT_FIELDS = _module.REQUIRED_REPORT_FIELDS
_recompute_record_hash = _module._recompute_record_hash


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_verifier(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFIER_SCRIPT), *cli_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _build_valid_record(previous_record_hash: str | None, **overrides) -> dict:
    base = {
        "audit_schema_version": "1",
        "source_phase": "phase7d_single_gate_wrapper",
        "product_id": "prod-aaa",
        "report_week": "2026-W26",
        "selected_gate": "promote",
        "wrapper_version": "phase7d-1",
        "operator": "operator-a",
        "approval_reason": "acceptance test",
        "approval_intent": "promote-intent",
        "execution_mode": None,
        "emergency_stop_state": None,
        "mutation_attempted": True,
        "primitive_name": "promote_product_candidates.py",
        "primitive_outcome": "success",
        "phase6b_packet_ref": None,
        "phase6c_verifier_ref": None,
        "phase6e_plan_ref": None,
        "phase7b_verifier_ref": None,
        "intent_audit_ref": None,
        "result_audit_ref": None,
        "source_audit_artifact_ref": "tmp/phase8b-test-input/sample.json",
        "precondition_summary": "all checks passed",
        "result_summary": "promote completed",
        "manual_review_status": None,
        "incident_id": None,
        "created_at": "2026-07-01T00:00:00Z",
        "completed_at": None,
        "artifact_hash": hashlib.sha256(uuid.uuid4().bytes).hexdigest(),
        "previous_record_hash": previous_record_hash,
        "retention_class": "standard",
        "phase8b_ingested_at": "2026-07-02T00:00:00Z",
        "phase8b_store_version": "phase8b-1",
        "phase8b_operator_note": None,
    }
    base.update(overrides)
    record_hash = _recompute_record_hash(base)
    base["audit_record_id"] = "audit-" + record_hash[:16]
    base["record_hash"] = record_hash
    return base


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")


@pytest.fixture()
def work_dir():
    unique = uuid.uuid4().hex[:12]
    base_dir = TEST_INPUT_ROOT / unique
    base_dir.mkdir(parents=True, exist_ok=True)
    store_path_abs = base_dir / "audit-records.jsonl"
    store_path_rel = store_path_abs.relative_to(REPO_ROOT).as_posix()
    report_dir_abs = REPO_ROOT / f"tmp/phase8c-audit-report/pytest-{unique}"
    report_dir_rel = report_dir_abs.relative_to(REPO_ROOT).as_posix()
    try:
        yield store_path_abs, store_path_rel, report_dir_abs, report_dir_rel
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(report_dir_abs, ignore_errors=True)


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8c_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, VERIFIER_SCRIPT, RUNNER_SCRIPT, THIS_TEST):
        assert path.is_file(), f"missing Phase 8C file: {path}"


def test_phase8c_status_tokens() -> None:
    assert "phase8c_status: success" in _text(TASK_FILE)
    assert "phase8c_status: success" in _text(DESIGN_DOC)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(DESIGN_DOC)
    assert "durable_audit_store_status: jsonl_verifier_reporting" in _text(DESIGN_DOC)


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8c_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "read-only jsonl verifier/reporting",
        "no append",
        "no source store mutation",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no backend/api/database",
        "no sqlite/s3/dynamodb",
        "no network behavior",
        "no new mutation path",
        "no next-gate automation",
        "no chain execution",
    ):
        assert token in low, f"missing scope token: {token}"


# ── C. Runtime static safety ─────────────────────────────────────────────────

def test_verifier_script_no_forbidden_imports() -> None:
    text = _text(VERIFIER_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"verifier script must not: {forbidden}"
    assert "fastapi" not in text.lower()


def test_verifier_script_no_primitive_or_vault_write_markers() -> None:
    text = _text(VERIFIER_SCRIPT)
    for primitive in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert primitive not in text, f"verifier script must not reference primitive: {primitive}"
    for marker in ("vault/products", "vault/decisions", "VAULT_PRODUCTS", "VAULT_DECISIONS"):
        assert marker not in text, f"verifier script must not reference vault write target: {marker}"


def test_shell_runner_static_safety() -> None:
    text = _text(RUNNER_SCRIPT)
    for forbidden in (
        "--execute",
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "run_phase7d_single_gate_wrapper",
        "execute_single_gate_approval",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
        "run_phase7b_audit_verifier",
        "verify_manual_approval_audit",
        "ingest_phase8b_audit_record",
        "run_phase8b_audit_ingest",
    ):
        assert forbidden not in text, f"shell runner must not contain: {forbidden}"


def test_shell_runner_executable_mode() -> None:
    mode = RUNNER_SCRIPT.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_verifier_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(VERIFIER_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Empty store behavior ──────────────────────────────────────────────────

def test_missing_store_produces_empty_report(work_dir) -> None:
    _, store_rel, report_dir_abs, report_dir_rel = work_dir
    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    json_path = report_dir_abs / "audit-store-verification.json"
    md_path = report_dir_abs / "audit-store-verification.md"
    assert json_path.is_file()
    assert md_path.is_file()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["verification_status"] == "empty"
    assert report["record_count"] == 0
    assert report["issue_count"] == 0
    assert report["hash_chain_valid"] is True


# ── E. Valid store behavior ───────────────────────────────────────────────────

def test_valid_store_behavior(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None, product_id="prod-aaa", operator="operator-a", selected_gate="promote", primitive_outcome="success")
    rec2 = _build_valid_record(
        rec1["record_hash"], product_id="prod-bbb", operator="operator-b", selected_gate="decision", primitive_outcome="failure"
    )
    _write_jsonl(store_abs, [rec1, rec2])
    original_bytes = store_abs.read_bytes()

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "valid"
    assert report["record_count"] == 2
    assert report["hash_chain_valid"] is True
    assert report["issue_count"] == 0
    for name in (
        "by_product_id",
        "by_report_week",
        "by_selected_gate",
        "by_operator",
        "by_primitive_outcome",
        "by_manual_review_status",
    ):
        assert name in report["summaries"], f"missing summary group: {name}"
    assert report["summaries"]["by_product_id"] == {"prod-aaa": 1, "prod-bbb": 1}

    md_text = (report_dir_abs / "audit-store-verification.md").read_text(encoding="utf-8")
    assert "phase8c_status: success" in md_text

    assert store_abs.read_bytes() == original_bytes, "source JSONL store must not be mutated"


# ── F. Hash mismatch behavior ─────────────────────────────────────────────────

def test_hash_mismatch_detected(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None)
    corrupted = dict(rec1)
    corrupted["result_summary"] = "tampered content without updating record_hash"
    _write_jsonl(store_abs, [corrupted])

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert report["hash_chain_valid"] is False
    assert report["issue_count"] > 0
    assert any(issue["issue_type"] == "hash_mismatch" for issue in report["issues"])


# ── G. Chain mismatch behavior ────────────────────────────────────────────────

def test_chain_mismatch_detected(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None)
    rec2 = _build_valid_record("0" * 64)
    _write_jsonl(store_abs, [rec1, rec2])

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert report["hash_chain_valid"] is False
    assert any(issue["issue_type"] == "previous_record_hash_mismatch" for issue in report["issues"])


# ── H. Duplicate behavior ─────────────────────────────────────────────────────

def test_duplicate_detection(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None)
    rec2 = dict(rec1)  # exact duplicate: same audit_record_id/artifact_hash/record_hash
    _write_jsonl(store_abs, [rec1, rec2])

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert report["duplicate_audit_record_id_count"] > 0
    assert report["duplicate_artifact_hash_count"] > 0
    assert report["duplicate_record_hash_count"] > 0


# ── I. Invalid JSON / non-object / missing fields ────────────────────────────

def test_invalid_json_line_produces_warning_issue(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None)
    store_abs.parent.mkdir(parents=True, exist_ok=True)
    with store_abs.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec1, sort_keys=True) + "\n")
        fh.write("{not valid json\n")

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert any(issue["issue_type"] == "invalid_json" for issue in report["issues"])
    assert report["invalid_line_count"] >= 1
    assert report["record_count"] == 1


def test_json_array_line_produces_warning_issue(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    store_abs.parent.mkdir(parents=True, exist_ok=True)
    store_abs.write_text("[1, 2, 3]\n", encoding="utf-8")

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert any(issue["issue_type"] == "not_object" for issue in report["issues"])
    assert report["record_count"] == 0


def test_missing_required_fields_produce_warning_issue(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(None)
    for field in ("operator", "manual_review_status"):
        rec1.pop(field, None)
    _write_jsonl(store_abs, [rec1])

    result = _run_verifier("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    report = json.loads((report_dir_abs / "audit-store-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert any(issue["issue_type"] == "missing_required_field" for issue in report["issues"])
    # Verifier continues: the record is still counted and reported.
    assert report["record_count"] == 1


def test_required_report_fields_constant_matches_documented_fields() -> None:
    text = _text(DESIGN_DOC) + _text(TASK_FILE)
    for field in REQUIRED_REPORT_FIELDS:
        assert field in text, f"documented field list missing: {field}"


# ── J. Path safety ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("root", ["vault", "docs", "scripts", "tests", "codex"])
def test_reject_store_path_under_rejected_roots(root, work_dir) -> None:
    _, _, report_dir_abs, report_dir_rel = work_dir
    marker = REPO_ROOT / root / f"_phase8c_pytest_{uuid.uuid4().hex[:8]}.jsonl"
    marker.write_text("", encoding="utf-8")
    try:
        result = _run_verifier(
            "--store-path", marker.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel
        )
        assert result.returncode != 0
    finally:
        marker.unlink(missing_ok=True)


def test_reject_symlinked_store_path(work_dir) -> None:
    store_abs, _, report_dir_abs, report_dir_rel = work_dir
    real = store_abs.parent / "real.jsonl"
    _write_jsonl(real, [_build_valid_record(None)])
    link = store_abs.parent / "link.jsonl"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported in this environment")
    result = _run_verifier(
        "--store-path", link.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel
    )
    assert result.returncode != 0


def test_reject_report_dir_outside_guarded_root(work_dir) -> None:
    store_abs, store_rel, _, _ = work_dir
    _write_jsonl(store_abs, [_build_valid_record(None)])
    outside_report_dir = REPO_ROOT / "tmp/phase8c-not-allowed"
    try:
        result = _run_verifier("--store-path", store_rel, "--report-dir", "tmp/phase8c-not-allowed")
        assert result.returncode != 0
        assert not outside_report_dir.exists()
    finally:
        shutil.rmtree(outside_report_dir, ignore_errors=True)


# ── K. Documentation regression ───────────────────────────────────────────────

def test_roadmap_references_phase8c() -> None:
    text = _text(ROADMAP)
    assert "Phase 8C" in text
    assert "Audit Store Verifier / Reporting over JSONL" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_references_phase8c() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8b_doc_references_phase8c() -> None:
    assert "Phase 8C" in _text(PHASE8B_DOC)


def test_phase8a_doc_references_phase8c() -> None:
    assert "Phase 8C" in _text(PHASE8A_DOC)


# ── L. Protected runtime files unchanged ──────────────────────────────────────

def test_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256_file(path) == expected_hash, f"protected runtime changed: {path}"


# ── M. Static safety for new Phase 8C files only ─────────────────────────────

def test_new_phase8c_files_static_safety() -> None:
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
    )
    for path in NEW_PHASE8C_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
