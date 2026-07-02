from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/053-phase8b-local-append-only-audit-store.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md"
INGEST_SCRIPT = REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh"
THIS_TEST = Path(__file__)

PHASE8A_DOC = REPO_ROOT / "docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RUNBOOK = REPO_ROOT / "docs/PHASE7H_OPERATOR_RUNBOOK.md"

NEW_PHASE8B_FILES = (TASK_FILE, DESIGN_DOC, INGEST_SCRIPT, RUNNER_SCRIPT)

TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase8b-test-input"

PROTECTED_HASHES = {
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

# Import the ingest module directly (no side effects at import time; the CLI
# entrypoint is guarded by `if __name__ == "__main__"`) so tests share the
# implementation's own field list instead of a hand-duplicated copy.
_spec = importlib.util.spec_from_file_location("phase8b_ingest_module", INGEST_SCRIPT)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
REQUIRED_RECORD_FIELDS = _module.REQUIRED_RECORD_FIELDS


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sample_audit(**overrides) -> dict:
    base = {
        "product_id": "prod-laptop-stand",
        "report_week": "2026-W26",
        "selected_gate": "promote",
        "primitive_name": "promote_product_candidates.py",
        "operator": "operator-a",
        "approval_reason": "acceptance test",
        "timestamp": "2026-07-01T00:00:00Z",
        "source_packet_path": "tmp/phase6b-approval-review/packet.json",
        "verifier_path": "tmp/phase6c-approval-review-verifier/out.json",
        "execution_plan_path": "tmp/phase6e-approval-execution-plan/plan.json",
        "precondition_summary": "all checks passed",
        "result_summary": "promote completed",
        "outcome": "success",
        "mutation_attempted": True,
        "gate_specific_approval_intent": "promote-intent",
        "approved_flag_name": "APPROVE_PROMOTE",
        "wrapper_version": "phase7d-1",
        "audit_schema_version": "1",
    }
    base.update(overrides)
    return base


def _write_json(path: Path, obj: dict) -> bytes:
    data = json.dumps(obj, indent=2).encode("utf-8")
    path.write_bytes(data)
    return data


def _run_ingest(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INGEST_SCRIPT), *cli_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def work_dir():
    unique = uuid.uuid4().hex[:12]
    input_dir = TEST_INPUT_ROOT / unique
    store_rel = f"tmp/phase8b-audit-store/pytest-{unique}"
    store_abs = REPO_ROOT / store_rel
    input_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield input_dir, store_rel, store_abs
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(store_abs, ignore_errors=True)


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8b_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, INGEST_SCRIPT, RUNNER_SCRIPT, THIS_TEST):
        assert path.is_file(), f"missing Phase 8B file: {path}"


def test_phase8b_status_tokens() -> None:
    assert "phase8b_status: success" in _text(TASK_FILE)
    assert "phase8b_status: success" in _text(DESIGN_DOC)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(DESIGN_DOC)
    assert "durable_audit_store_status: local_append_only_prototype" in _text(DESIGN_DOC)


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8b_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "ingest-only",
        "append-only jsonl",
        "hash-chain",
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

def test_ingest_script_no_forbidden_imports() -> None:
    text = _text(INGEST_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"ingest script must not: {forbidden}"
    assert "fastapi" not in text.lower()


def test_ingest_script_no_primitive_or_vault_write_markers() -> None:
    text = _text(INGEST_SCRIPT)
    for primitive in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert primitive not in text, f"ingest script must not reference primitive: {primitive}"
    for marker in ("vault/products", "vault/decisions", "VAULT_PRODUCTS", "VAULT_DECISIONS"):
        assert marker not in text, f"ingest script must not reference vault write target: {marker}"


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
    ):
        assert forbidden not in text, f"shell runner must not contain: {forbidden}"


def test_shell_runner_executable_mode() -> None:
    mode = RUNNER_SCRIPT.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_ingest_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(INGEST_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Ingest behavior ───────────────────────────────────────────────────────

def test_ingest_first_record_success(work_dir) -> None:
    input_dir, store_rel, store_abs = work_dir
    audit_path = input_dir / "sample.json"
    raw_bytes = _write_json(audit_path, _sample_audit())
    rel_audit_path = audit_path.relative_to(REPO_ROOT).as_posix()

    result = _run_ingest("--audit-artifact", rel_audit_path, "--store-dir", store_rel)
    assert result.returncode == 0, result.stderr

    jsonl_path = store_abs / "audit-records.jsonl"
    assert jsonl_path.is_file()
    lines = [line for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])

    for field in REQUIRED_RECORD_FIELDS:
        assert field in record, f"missing normalized record field: {field}"

    assert record["artifact_hash"] == _sha256_bytes(raw_bytes)
    assert record["previous_record_hash"] is None
    assert re.fullmatch(r"[0-9a-f]{64}", record["record_hash"])
    assert record["audit_record_id"] == "audit-" + record["record_hash"][:16]

    summary_json_path = store_abs / "audit-ingest-summary.json"
    summary_md_path = store_abs / "audit-ingest-summary.md"
    assert summary_json_path.is_file()
    assert summary_md_path.is_file()

    summary = json.loads(summary_json_path.read_text(encoding="utf-8"))
    assert summary["phase8b_status"] == "success"
    assert summary["durable_audit_store_status"] == "local_append_only_prototype"
    md_text = summary_md_path.read_text(encoding="utf-8")
    assert "phase8b_status: success" in md_text
    assert "durable_audit_store_status: local_append_only_prototype" in md_text

    assert audit_path.read_bytes() == raw_bytes, "source audit artifact must not be mutated"


# ── E. Hash-chain behavior ───────────────────────────────────────────────────

def test_hash_chain_across_two_records(work_dir) -> None:
    input_dir, store_rel, store_abs = work_dir
    audit1 = input_dir / "a1.json"
    audit2 = input_dir / "a2.json"
    _write_json(audit1, _sample_audit(product_id="prod-aaa"))
    _write_json(audit2, _sample_audit(product_id="prod-bbb"))

    r1 = _run_ingest("--audit-artifact", audit1.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert r1.returncode == 0, r1.stderr
    r2 = _run_ingest("--audit-artifact", audit2.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert r2.returncode == 0, r2.stderr

    lines = [
        line for line in (store_abs / "audit-records.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(lines) == 2
    rec1 = json.loads(lines[0])
    rec2 = json.loads(lines[1])

    assert rec1["previous_record_hash"] is None
    assert rec2["previous_record_hash"] == rec1["record_hash"]

    for rec in (rec1, rec2):
        stripped = {k: v for k, v in rec.items() if k not in ("record_hash", "audit_record_id")}
        recomputed = hashlib.sha256(_canonical_json(stripped).encode("utf-8")).hexdigest()
        assert recomputed == rec["record_hash"]


# ── F. Duplicate behavior ────────────────────────────────────────────────────

def test_duplicate_ingest_is_noop(work_dir) -> None:
    input_dir, store_rel, store_abs = work_dir
    audit_path = input_dir / "dup.json"
    _write_json(audit_path, _sample_audit())
    rel_path = audit_path.relative_to(REPO_ROOT).as_posix()

    r1 = _run_ingest("--audit-artifact", rel_path, "--store-dir", store_rel)
    assert r1.returncode == 0, r1.stderr
    r2 = _run_ingest("--audit-artifact", rel_path, "--store-dir", store_rel)
    assert r2.returncode == 0, r2.stderr

    lines = [
        line for line in (store_abs / "audit-records.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(lines) == 1

    summary = json.loads((store_abs / "audit-ingest-summary.json").read_text(encoding="utf-8"))
    assert summary["ingest_status"] == "duplicate_skipped"
    assert summary["duplicate"] is True
    assert summary["appended"] is False


# ── G. Path safety ────────────────────────────────────────────────────────────

def test_reject_missing_file(work_dir) -> None:
    input_dir, store_rel, _ = work_dir
    missing = input_dir / "missing.json"
    result = _run_ingest("--audit-artifact", missing.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert result.returncode != 0


def test_reject_directory(work_dir) -> None:
    input_dir, store_rel, _ = work_dir
    result = _run_ingest("--audit-artifact", input_dir.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert result.returncode != 0


def test_reject_invalid_json(work_dir) -> None:
    input_dir, store_rel, _ = work_dir
    bad = input_dir / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    result = _run_ingest("--audit-artifact", bad.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert result.returncode != 0


def test_reject_json_array(work_dir) -> None:
    input_dir, store_rel, _ = work_dir
    arr = input_dir / "array.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    result = _run_ingest("--audit-artifact", arr.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert result.returncode != 0


@pytest.mark.parametrize("root", ["vault", "docs", "scripts", "tests", "codex"])
def test_reject_source_under_rejected_roots(root, work_dir) -> None:
    _, store_rel, _ = work_dir
    marker = REPO_ROOT / root / f"_phase8b_pytest_{uuid.uuid4().hex[:8]}.json"
    marker.write_text(json.dumps({"a": 1}), encoding="utf-8")
    try:
        result = _run_ingest("--audit-artifact", marker.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
        assert result.returncode != 0
    finally:
        marker.unlink(missing_ok=True)


def test_reject_symlink(work_dir) -> None:
    input_dir, store_rel, _ = work_dir
    real = input_dir / "real.json"
    _write_json(real, _sample_audit())
    link = input_dir / "link.json"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported in this environment")
    result = _run_ingest("--audit-artifact", link.relative_to(REPO_ROOT).as_posix(), "--store-dir", store_rel)
    assert result.returncode != 0


def test_reject_store_dir_outside_guarded_root(work_dir) -> None:
    input_dir, _, _ = work_dir
    audit_path = input_dir / "sample.json"
    _write_json(audit_path, _sample_audit())
    outside_store = REPO_ROOT / "tmp/phase8b-not-allowed"
    try:
        result = _run_ingest(
            "--audit-artifact",
            audit_path.relative_to(REPO_ROOT).as_posix(),
            "--store-dir",
            "tmp/phase8b-not-allowed",
        )
        assert result.returncode != 0
        assert not outside_store.exists()
    finally:
        shutil.rmtree(outside_store, ignore_errors=True)


# ── H. Documentation regression ───────────────────────────────────────────────

def test_roadmap_references_phase8b() -> None:
    text = _text(ROADMAP)
    assert "Phase 8B" in text
    assert "Local Append-only Audit Store Prototype" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_references_phase8b() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8a_doc_references_phase8b() -> None:
    text = _text(PHASE8A_DOC)
    assert "Phase 8B" in text


def test_runbook_references_phase8b() -> None:
    text = _text(RUNBOOK)
    assert "Phase 8B" in text


# ── I. Protected runtime files unchanged ─────────────────────────────────────

def test_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256_file(path) == expected_hash, f"protected runtime changed: {path}"


# ── J. Static safety for new Phase 8B files only ─────────────────────────────

def test_new_phase8b_files_static_safety() -> None:
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
    for path in NEW_PHASE8B_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
