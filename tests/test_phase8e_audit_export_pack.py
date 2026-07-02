from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/056-phase8e-audit-export-pack.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"
EXPORT_SCRIPT = REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8D_DOC = REPO_ROOT / "docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md"
PHASE8C_DOC = REPO_ROOT / "docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md"

NEW_PHASE8E_FILES = (TASK_FILE, DESIGN_DOC, EXPORT_SCRIPT, RUNNER_SCRIPT)

TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase8e-test-input"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/ingest_phase8b_audit_record.py": "d4af3b87e058a5ff93bf4b9ce57471dca4782a432098206df5dbb4275b7ff8a0",
    REPO_ROOT / "scripts/dev/run_phase8b_audit_ingest.sh": "9eeeb71d72fd6183caddf97a9dfa7406f985fcac06af5f16f67c2d7f9d2ca343",
    REPO_ROOT / "scripts/dev/verify_phase8c_audit_store.py": "87edb8355f3f5868782a16060950d53bb80e09ac3f27d99e16377261fc763787",
    REPO_ROOT / "scripts/dev/run_phase8c_audit_report.sh": "72755c4576de3485a4827a4ce908c4dc64e53cb36cf907e335ff622c52ade7f1",
    REPO_ROOT / "scripts/dev/query_phase8d_audit_store.py": "3ffab49a1cd16a744a8fe04e788601e567b2191a94a3fbcda55d8da864e5bf82",
    REPO_ROOT / "scripts/dev/run_phase8d_audit_query.sh": "2ad91d7551d5c027203772ab6109aebaf08eb21766fbe64fde07208205179649",
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
    REPO_ROOT / "scripts/dev/run_phase7b_audit_verifier.sh": "2eed4c68f12dff5306fc244c1a42a843d87b3af6150105fa9681593cd678bfa5",
    REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py": "6c959019f458bd4e79ddf23a9e58055f5fbc16e99660496c4451c13783329c3e",
    REPO_ROOT / "scripts/dev/promote_product_candidates.py": "496055979f5492389237662d756c4a51a6428da60c804e4ccba72efff0f1ff6e",
    REPO_ROOT / "scripts/dev/create_decision.py": "ac27e4300d617f60e45799980fead1f7e3a09f5f1f083ef5d42c1d327ded4613",
    REPO_ROOT / "scripts/dev/finalize_decision.py": "1c829e797b49ca8a3cff875a1609a06f093ca104873fa20597784a8adac3d177",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_export(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), *cli_args],
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


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@pytest.fixture()
def work_dir():
    unique = uuid.uuid4().hex[:12]
    base_dir = TEST_INPUT_ROOT / unique
    base_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "store": base_dir / "audit-records.jsonl",
        "verification_json": base_dir / "audit-store-verification.json",
        "verification_md": base_dir / "audit-store-verification.md",
        "query_json": base_dir / "audit-query-result.json",
        "query_md": base_dir / "audit-query-result.md",
    }
    export_dir_abs = REPO_ROOT / f"tmp/phase8e-audit-export/pytest-{unique}"
    export_dir_rel = export_dir_abs.relative_to(REPO_ROOT).as_posix()
    try:
        yield base_dir, paths, export_dir_abs, export_dir_rel
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(export_dir_abs, ignore_errors=True)


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _cli_for(paths: dict, export_dir_rel: str, *extra: str) -> list[str]:
    args = [
        "--store-path", _rel(paths["store"]),
        "--verification-json", _rel(paths["verification_json"]),
        "--verification-md", _rel(paths["verification_md"]),
        "--query-json", _rel(paths["query_json"]),
        "--query-md", _rel(paths["query_md"]),
        "--export-dir", export_dir_rel,
    ]
    args.extend(extra)
    return args


@pytest.fixture()
def full_chain(work_dir):
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    rec = _build_valid_record()
    _write_jsonl(paths["store"], [rec])
    _write_json(paths["verification_json"], {"phase8c_status": "success", "verification_status": "valid", "record_count": 1})
    paths["verification_md"].write_text("# Phase 8C Verification\n\nverification_status: valid\n", encoding="utf-8")
    _write_json(paths["query_json"], {"phase8d_status": "success", "query_status": "success", "matched_records": 1})
    paths["query_md"].write_text("# Phase 8D Query Result\n\nquery_status: success\n", encoding="utf-8")
    return base_dir, paths, export_dir_abs, export_dir_rel, rec


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8e_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, EXPORT_SCRIPT, RUNNER_SCRIPT, THIS_TEST):
        assert path.is_file(), f"missing Phase 8E file: {path}"


def test_phase8e_status_tokens() -> None:
    assert "phase8e_status: success" in _text(TASK_FILE)
    assert "phase8e_status: success" in _text(DESIGN_DOC)
    assert "phase7d_runtime_readiness: implemented_manual_gate" in _text(DESIGN_DOC)
    assert "durable_audit_store_status: export_pack" in _text(DESIGN_DOC)


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8e_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "read-only export pack",
        "no append",
        "no source evidence mutation",
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

def test_export_script_no_forbidden_imports() -> None:
    text = _text(EXPORT_SCRIPT)
    for forbidden in (
        "import subprocess",
        "import sqlite3",
        "import boto3",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in text, f"export script must not: {forbidden}"
    assert "fastapi" not in text.lower()


def test_export_script_no_primitive_or_vault_write_markers() -> None:
    text = _text(EXPORT_SCRIPT)
    for primitive in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert primitive not in text, f"export script must not reference primitive: {primitive}"
    for marker in ("vault/products", "vault/decisions", "VAULT_PRODUCTS", "VAULT_DECISIONS"):
        assert marker not in text, f"export script must not reference vault write target: {marker}"


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
        "query_phase8d_audit_store",
        "run_phase8d_audit_query",
    ):
        assert forbidden not in text, f"shell runner must not contain: {forbidden}"


def test_shell_runner_executable_mode() -> None:
    mode = RUNNER_SCRIPT.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_shell_runner_git_index_mode_is_100755() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-s", "scripts/dev/run_phase8e_audit_export.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.stdout.startswith("100755 "), f"unexpected git index mode: {result.stdout!r}"


def test_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_export_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(EXPORT_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Missing evidence behavior ──────────────────────────────────────────────

def test_missing_store_produces_empty_export(work_dir) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr

    manifest_path = export_dir_abs / "audit-export-manifest.json"
    summary_path = export_dir_abs / "audit-export-summary.md"
    assert manifest_path.is_file()
    assert summary_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["export_status"] == "empty"
    assert "audit_records_jsonl" in manifest["missing_evidence"]
    assert manifest["record_count"] == 0


# ── E. Export behavior without copies ────────────────────────────────────────

def test_export_without_copies(full_chain) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel, rec = full_chain
    original_bytes = {name: p.read_bytes() for name, p in paths.items()}

    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr

    manifest = json.loads((export_dir_abs / "audit-export-manifest.json").read_text(encoding="utf-8"))
    assert manifest["export_status"] == "success"
    assert manifest["record_count"] == 1
    labels = {entry["label"]: entry for entry in manifest["source_evidence"]}
    assert set(labels) == {"audit_records_jsonl", "verification_json", "verification_md", "query_json", "query_md"}
    for entry in labels.values():
        assert entry["exists"] is True
        assert entry["sha256"] is not None
    assert manifest["source_hashes"]["audit_records_jsonl"] == labels["audit_records_jsonl"]["sha256"]
    assert manifest["verification_status"] == "valid"
    assert manifest["query_status"] == "success"
    for name in (
        "by_product_id",
        "by_report_week",
        "by_selected_gate",
        "by_operator",
        "by_primitive_outcome",
        "by_manual_review_status",
    ):
        assert name in manifest["summaries"], f"missing summary group: {name}"
    assert manifest["summaries"]["by_product_id"] == {"prod-aaa": 1}
    assert manifest["copied_files"] == []

    assert (export_dir_abs / "audit-export-summary.md").is_file()

    for name, p in paths.items():
        assert p.read_bytes() == original_bytes[name], f"source evidence mutated: {name}"


# ── F. Export behavior with copies ───────────────────────────────────────────

def test_export_with_copies(full_chain) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel, rec = full_chain
    result = _run_export(*_cli_for(paths, export_dir_rel, "--include-copies"))
    assert result.returncode == 0, result.stderr

    manifest = json.loads((export_dir_abs / "audit-export-manifest.json").read_text(encoding="utf-8"))
    assert manifest["include_copies"] is True
    assert len(manifest["copied_files"]) == 5

    evidence_dir = export_dir_abs / "evidence"
    expected = {
        "audit-records.jsonl": paths["store"],
        "audit-store-verification.json": paths["verification_json"],
        "audit-store-verification.md": paths["verification_md"],
        "audit-query-result.json": paths["query_json"],
        "audit-query-result.md": paths["query_md"],
    }
    for dest_name, source_path in expected.items():
        dest = evidence_dir / dest_name
        assert dest.is_file(), f"missing evidence copy: {dest_name}"
        assert dest.read_bytes() == source_path.read_bytes(), f"copy not byte-identical: {dest_name}"


def test_no_copy_without_include_copies_flag(full_chain) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel, rec = full_chain
    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr
    assert not (export_dir_abs / "evidence").exists()


# ── G. Warning behavior ───────────────────────────────────────────────────────

def test_invalid_jsonl_line_produces_warning_export(full_chain) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel, rec = full_chain
    with paths["store"].open("a", encoding="utf-8") as fh:
        fh.write("{not valid json\n")

    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr
    manifest = json.loads((export_dir_abs / "audit-export-manifest.json").read_text(encoding="utf-8"))
    assert manifest["export_status"] == "warning"
    assert manifest["record_count"] == 1
    assert any(w["issue_type"] == "invalid_json" for w in manifest["warnings"])


def test_invalid_optional_report_json_produces_warning_export(full_chain) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel, rec = full_chain
    paths["verification_json"].write_text("{not valid json", encoding="utf-8")

    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr
    manifest = json.loads((export_dir_abs / "audit-export-manifest.json").read_text(encoding="utf-8"))
    assert manifest["export_status"] == "warning"
    assert manifest["verification_status"] is None
    assert any(w["issue_type"] == "invalid_report_json" for w in manifest["warnings"])


def test_missing_optional_reports_produce_warning_export(work_dir) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    _write_jsonl(paths["store"], [_build_valid_record()])

    result = _run_export(*_cli_for(paths, export_dir_rel))
    assert result.returncode == 0, result.stderr
    manifest = json.loads((export_dir_abs / "audit-export-manifest.json").read_text(encoding="utf-8"))
    assert manifest["export_status"] == "warning"
    assert manifest["record_count"] == 1
    for label in ("verification_json", "verification_md", "query_json", "query_md"):
        assert label in manifest["missing_evidence"]
    assert manifest["summaries"]["by_product_id"] == {"prod-aaa": 1}


# ── H. Path safety ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("root", ["vault", "docs", "scripts", "tests", "codex"])
def test_reject_store_path_under_rejected_roots(root, work_dir) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    marker = REPO_ROOT / root / f"_phase8e_pytest_{uuid.uuid4().hex[:8]}.jsonl"
    marker.write_text("", encoding="utf-8")
    try:
        result = _run_export("--store-path", marker.relative_to(REPO_ROOT).as_posix(), "--export-dir", export_dir_rel)
        assert result.returncode != 0
    finally:
        marker.unlink(missing_ok=True)


def test_reject_symlinked_store_path(work_dir) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    real = base_dir / "real.jsonl"
    _write_jsonl(real, [_build_valid_record()])
    link = base_dir / "link.jsonl"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported in this environment")
    result = _run_export(
        "--store-path", link.relative_to(REPO_ROOT).as_posix(), "--export-dir", export_dir_rel
    )
    assert result.returncode != 0


def test_reject_export_dir_outside_guarded_root(work_dir) -> None:
    base_dir, paths, export_dir_abs, export_dir_rel = work_dir
    _write_jsonl(paths["store"], [_build_valid_record()])
    outside_export_dir = REPO_ROOT / "tmp/phase8e-not-allowed"
    try:
        result = _run_export("--store-path", _rel(paths["store"]), "--export-dir", "tmp/phase8e-not-allowed")
        assert result.returncode != 0
        assert not outside_export_dir.exists()
    finally:
        shutil.rmtree(outside_export_dir, ignore_errors=True)


# ── I. Documentation regression ───────────────────────────────────────────────

def test_roadmap_references_phase8e() -> None:
    text = _text(ROADMAP)
    assert "Phase 8E" in text
    assert "Audit Export Pack" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_references_phase8e() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8E_AUDIT_EXPORT_PACK.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8d_doc_references_phase8e() -> None:
    assert "Phase 8E" in _text(PHASE8D_DOC)


def test_phase8c_doc_references_phase8e() -> None:
    assert "Phase 8E" in _text(PHASE8C_DOC)


# ── J. Protected runtime files unchanged ──────────────────────────────────────

def test_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256_file(path) == expected_hash, f"protected runtime changed: {path}"


# ── K. Static safety for new Phase 8E files only ─────────────────────────────

def test_new_phase8e_files_static_safety() -> None:
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
    for path in NEW_PHASE8E_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
