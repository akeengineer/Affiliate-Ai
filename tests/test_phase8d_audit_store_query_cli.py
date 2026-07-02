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

TASK_FILE = REPO_ROOT / "codex/tasks/055-phase8d-audit-store-query-cli.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md"
QUERY_SCRIPT = REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8C_DOC = REPO_ROOT / "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md"
PHASE8B_DOC = REPO_ROOT / "docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md"

NEW_PHASE8D_FILES = (TASK_FILE, DESIGN_DOC, QUERY_SCRIPT, RUNNER_SCRIPT)

TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase8d-test-input"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
    REPO_ROOT / "scripts/dev/promote_product_candidates.py": "496055979f5492389237662d756c4a51a6428da60c804e4ccba72efff0f1ff6e",
    REPO_ROOT / "scripts/dev/create_decision.py": "ac27e4300d617f60e45799980fead1f7e3a09f5f1f083ef5d42c1d327ded4613",
    REPO_ROOT / "scripts/dev/finalize_decision.py": "1c829e797b49ca8a3cff875a1609a06f093ca104873fa20597784a8adac3d177",
}

# Import the query module directly (no side effects at import time; the CLI
# entrypoint is guarded by `if __name__ == "__main__"`) so tests share the
# implementation's own hash function instead of a hand-duplicated copy.
_spec = importlib.util.spec_from_file_location("phase8d_query_module", QUERY_SCRIPT)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
_hash_status = _module._hash_status


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_query(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(QUERY_SCRIPT), *cli_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _build_valid_record(**overrides) -> dict:
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
        "previous_record_hash": None,
        "retention_class": "standard",
        "phase8b_ingested_at": "2026-07-02T00:00:00Z",
        "phase8b_store_version": "phase8b-1",
        "phase8b_operator_note": None,
    }
    base.update(overrides)
    record_hash = hashlib.sha256(
        _canonical_json({k: v for k, v in base.items() if k not in ("record_hash", "audit_record_id")}).encode(
            "utf-8"
        )
    ).hexdigest()
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
    report_dir_abs = REPO_ROOT / f"tmp/phase8d-audit-query/pytest-{unique}"
    report_dir_rel = report_dir_abs.relative_to(REPO_ROOT).as_posix()
    try:
        yield store_path_abs, store_path_rel, report_dir_abs, report_dir_rel
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(report_dir_abs, ignore_errors=True)


@pytest.fixture()
def fixture_store(work_dir):
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record(
        product_id="prod-aaa",
        report_week="2026-W26",
        selected_gate="promote",
        operator="operator-a",
        primitive_outcome="success",
        manual_review_status=None,
        incident_id=None,
        created_at="2026-07-01T00:00:00Z",
        phase8b_ingested_at="2026-07-02T00:00:00Z",
    )
    rec2 = _build_valid_record(
        product_id="prod-bbb",
        report_week="2026-W26",
        selected_gate="decision",
        operator="operator-b",
        primitive_outcome="failure",
        manual_review_status="pending",
        incident_id="incident-1",
        created_at="2026-07-01T02:00:00Z",
        phase8b_ingested_at="2026-07-02T02:00:00Z",
    )
    rec3 = _build_valid_record(
        product_id="prod-ccc",
        report_week="2026-W27",
        selected_gate="finalization",
        operator="operator-a",
        primitive_outcome="success",
        manual_review_status=None,
        incident_id=None,
        created_at="2026-07-01T01:00:00Z",
        phase8b_ingested_at="2026-07-02T01:00:00Z",
    )
    _write_jsonl(store_abs, [rec1, rec2, rec3])
    return store_abs, store_rel, report_dir_abs, report_dir_rel, (rec1, rec2, rec3)


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8d_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, QUERY_SCRIPT, RUNNER_SCRIPT, THIS_TEST):
        assert path.is_file(), f"missing Phase 8D file: {path}"


def test_phase8d_status_tokens() -> None:
    assert "phase8d_status: success" in _text(TASK_FILE)
    assert "phase8d_status: success" in _text(DESIGN_DOC)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(DESIGN_DOC)
    assert "durable_audit_store_status: jsonl_query_cli" in _text(DESIGN_DOC)


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8d_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "read-only jsonl query cli",
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

def test_query_script_no_forbidden_imports() -> None:
    text = _text(QUERY_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"query script must not: {forbidden}"
    assert "fastapi" not in text.lower()


def test_query_script_no_primitive_or_vault_write_markers() -> None:
    text = _text(QUERY_SCRIPT)
    for primitive in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert primitive not in text, f"query script must not reference primitive: {primitive}"
    for marker in ("vault/products", "vault/decisions", "VAULT_PRODUCTS", "VAULT_DECISIONS"):
        assert marker not in text, f"query script must not reference vault write target: {marker}"


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
        "verify_phase8c_audit_store",
        "run_phase8c_audit_report",
    ):
        assert forbidden not in text, f"shell runner must not contain: {forbidden}"


def test_shell_runner_executable_mode() -> None:
    mode = RUNNER_SCRIPT.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_shell_runner_git_index_mode_is_100755() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-s", "scripts/dev/run_phase8d_audit_query.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.stdout.startswith("100755 "), f"unexpected git index mode: {result.stdout!r}"


def test_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_query_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(QUERY_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Missing store behavior ─────────────────────────────────────────────────

def test_missing_store_produces_empty_result(work_dir) -> None:
    _, store_rel, report_dir_abs, report_dir_rel = work_dir
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr

    json_path = report_dir_abs / "audit-query-result.json"
    md_path = report_dir_abs / "audit-query-result.md"
    assert json_path.is_file()
    assert md_path.is_file()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["query_status"] == "empty"
    assert report["total_records_read"] == 0
    assert report["matched_records"] == 0


# ── E. Query behavior ──────────────────────────────────────────────────────────

def _query(fixture_store, *extra_args):
    store_abs, store_rel, report_dir_abs, report_dir_rel, _ = fixture_store
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, *extra_args)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    return report


def test_query_by_product_id(fixture_store) -> None:
    report = _query(fixture_store, "--product-id", "prod-aaa")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["product_id"] == "prod-aaa"


def test_query_by_report_week(fixture_store) -> None:
    report = _query(fixture_store, "--report-week", "2026-W27")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["report_week"] == "2026-W27"


def test_query_by_selected_gate(fixture_store) -> None:
    report = _query(fixture_store, "--selected-gate", "decision")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["selected_gate"] == "decision"


def test_query_by_operator(fixture_store) -> None:
    report = _query(fixture_store, "--operator", "operator-a")
    assert report["matched_records"] == 2


def test_query_by_primitive_outcome(fixture_store) -> None:
    report = _query(fixture_store, "--primitive-outcome", "failure")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["primitive_outcome"] == "failure"


def test_query_by_manual_review_status(fixture_store) -> None:
    report = _query(fixture_store, "--manual-review-status", "pending")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["manual_review_status"] == "pending"


def test_query_by_incident_id(fixture_store) -> None:
    report = _query(fixture_store, "--incident-id", "incident-1")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["incident_id"] == "incident-1"


def test_query_by_hash_status_valid(fixture_store) -> None:
    report = _query(fixture_store, "--hash-status", "valid")
    assert report["matched_records"] == 3


def test_filters_combine_as_and(fixture_store) -> None:
    report = _query(fixture_store, "--operator", "operator-a", "--selected-gate", "finalization")
    assert report["matched_records"] == 1
    assert report["records"][0]["record"]["product_id"] == "prod-ccc"


def test_no_match_returns_no_matches_status(fixture_store) -> None:
    report = _query(fixture_store, "--product-id", "prod-does-not-exist")
    assert report["query_status"] == "no_matches"
    assert report["matched_records"] == 0


def test_returned_records_do_not_exceed_limit(fixture_store) -> None:
    report = _query(fixture_store, "--limit", "2")
    assert report["matched_records"] == 3
    assert report["returned_records"] == 2
    assert len(report["records"]) == 2


def test_source_jsonl_unchanged_after_query(fixture_store) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel, _ = fixture_store
    original_bytes = store_abs.read_bytes()
    _query(fixture_store)
    assert store_abs.read_bytes() == original_bytes


# ── F. Sorting and limit behavior ─────────────────────────────────────────────

def test_default_sort_by_phase8b_ingested_at_ascending(fixture_store) -> None:
    report = _query(fixture_store)
    ids = [entry["record"]["product_id"] for entry in report["records"]]
    assert ids == ["prod-aaa", "prod-ccc", "prod-bbb"]


def test_sort_by_created_at(fixture_store) -> None:
    report = _query(fixture_store, "--sort-by", "created_at")
    ids = [entry["record"]["product_id"] for entry in report["records"]]
    assert ids == ["prod-aaa", "prod-ccc", "prod-bbb"]


def test_descending_option(fixture_store) -> None:
    report = _query(fixture_store, "--descending")
    ids = [entry["record"]["product_id"] for entry in report["records"]]
    assert ids == ["prod-bbb", "prod-ccc", "prod-aaa"]


def test_invalid_limit_rejected(fixture_store) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel, _ = fixture_store
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, "--limit", "0")
    assert result.returncode != 0
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, "--limit", "1001")
    assert result.returncode != 0
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, "--limit", "not-a-number")
    assert result.returncode != 0


def test_invalid_sort_field_rejected(fixture_store) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel, _ = fixture_store
    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, "--sort-by", "bogus_field")
    assert result.returncode != 0


# ── G. Invalid line handling ──────────────────────────────────────────────────

def test_invalid_json_line_produces_warning(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record()
    store_abs.parent.mkdir(parents=True, exist_ok=True)
    with store_abs.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec1, sort_keys=True) + "\n")
        fh.write("{not valid json\n")

    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    assert report["query_status"] == "warning"
    assert any(w["issue_type"] == "invalid_json" for w in report["warnings"])
    assert report["matched_records"] == 1


def test_non_object_line_produces_warning(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    rec1 = _build_valid_record()
    store_abs.parent.mkdir(parents=True, exist_ok=True)
    with store_abs.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec1, sort_keys=True) + "\n")
        fh.write("[1, 2, 3]\n")

    result = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    assert report["query_status"] == "warning"
    assert any(w["issue_type"] == "not_object" for w in report["warnings"])
    assert report["matched_records"] == 1


# ── H. Hash status behavior ────────────────────────────────────────────────────

def test_hash_status_valid_for_correct_record() -> None:
    rec = _build_valid_record()
    assert _hash_status(rec) == "valid"


def test_hash_status_invalid_for_corrupted_record() -> None:
    rec = _build_valid_record()
    rec["result_summary"] = "tampered without updating record_hash"
    assert _hash_status(rec) == "invalid"


def test_hash_status_unknown_for_incomplete_record() -> None:
    rec = _build_valid_record()
    del rec["record_hash"]
    assert _hash_status(rec) == "unknown"


def test_query_hash_status_end_to_end(work_dir) -> None:
    store_abs, store_rel, report_dir_abs, report_dir_rel = work_dir
    good = _build_valid_record(product_id="prod-good")
    corrupted = _build_valid_record(product_id="prod-corrupted")
    corrupted["result_summary"] = "tampered without updating record_hash"
    incomplete = _build_valid_record(product_id="prod-incomplete")
    del incomplete["record_hash"]
    _write_jsonl(store_abs, [good, corrupted, incomplete])

    valid_report = _run_query("--store-path", store_rel, "--report-dir", report_dir_rel, "--hash-status", "valid")
    assert valid_report.returncode == 0
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    assert [r["record"]["product_id"] for r in report["records"]] == ["prod-good"]

    invalid_report = _run_query(
        "--store-path", store_rel, "--report-dir", report_dir_rel, "--hash-status", "invalid"
    )
    assert invalid_report.returncode == 0
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    assert [r["record"]["product_id"] for r in report["records"]] == ["prod-corrupted"]

    unknown_report = _run_query(
        "--store-path", store_rel, "--report-dir", report_dir_rel, "--hash-status", "unknown"
    )
    assert unknown_report.returncode == 0
    report = json.loads((report_dir_abs / "audit-query-result.json").read_text(encoding="utf-8"))
    assert [r["record"]["product_id"] for r in report["records"]] == ["prod-incomplete"]


# ── I. Path safety ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("root", ["vault", "docs", "scripts", "tests", "codex"])
def test_reject_store_path_under_rejected_roots(root, work_dir) -> None:
    _, _, report_dir_abs, report_dir_rel = work_dir
    marker = REPO_ROOT / root / f"_phase8d_pytest_{uuid.uuid4().hex[:8]}.jsonl"
    marker.write_text("", encoding="utf-8")
    try:
        result = _run_query("--store-path", marker.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
        assert result.returncode != 0
    finally:
        marker.unlink(missing_ok=True)


def test_reject_symlinked_store_path(work_dir) -> None:
    store_abs, _, report_dir_abs, report_dir_rel = work_dir
    real = store_abs.parent / "real.jsonl"
    _write_jsonl(real, [_build_valid_record()])
    link = store_abs.parent / "link.jsonl"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported in this environment")
    result = _run_query("--store-path", link.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
    assert result.returncode != 0


def test_reject_report_dir_outside_guarded_root(work_dir) -> None:
    store_abs, store_rel, _, _ = work_dir
    _write_jsonl(store_abs, [_build_valid_record()])
    outside_report_dir = REPO_ROOT / "tmp/phase8d-not-allowed"
    try:
        result = _run_query("--store-path", store_rel, "--report-dir", "tmp/phase8d-not-allowed")
        assert result.returncode != 0
        assert not outside_report_dir.exists()
    finally:
        shutil.rmtree(outside_report_dir, ignore_errors=True)


# ── J. Documentation regression ───────────────────────────────────────────────

def test_roadmap_references_phase8d() -> None:
    text = _text(ROADMAP)
    assert "Phase 8D" in text
    assert "Audit Store Query CLI over JSONL" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_references_phase8d() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8c_doc_references_phase8d() -> None:
    assert "Phase 8D" in _text(PHASE8C_DOC)


def test_phase8b_doc_references_phase8d() -> None:
    assert "Phase 8D" in _text(PHASE8B_DOC)


# ── K. Protected runtime files unchanged ──────────────────────────────────────

def test_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256_file(path) == expected_hash, f"protected runtime changed: {path}"


# ── L. Static safety for new Phase 8D files only ─────────────────────────────

def test_new_phase8d_files_static_safety() -> None:
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
    for path in NEW_PHASE8D_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
