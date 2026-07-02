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

TASK_FILE = REPO_ROOT / "codex/tasks/059-phase8h-export-integrity-verifier-hardening.md"
DESIGN_DOC = REPO_ROOT / "docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md"
VERIFIER_SCRIPT = REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py"
RUNNER_SCRIPT = REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE8G_DOC = REPO_ROOT / "docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md"
PHASE8F_DOC = REPO_ROOT / "docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md"
PHASE8E_DOC = REPO_ROOT / "docs/PHASE8E_AUDIT_EXPORT_PACK.md"

NEW_PHASE8H_FILES = (TASK_FILE, DESIGN_DOC, VERIFIER_SCRIPT)

TEST_INPUT_ROOT = REPO_ROOT / "tmp/phase8h-test-input"

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


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _run_verifier(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFIER_SCRIPT), *cli_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def work_dir():
    unique = uuid.uuid4().hex[:12]
    base_dir = TEST_INPUT_ROOT / unique
    base_dir.mkdir(parents=True, exist_ok=True)
    report_dir_abs = REPO_ROOT / f"tmp/phase8g-export-integrity/pytest8h-{unique}"
    report_dir_rel = report_dir_abs.relative_to(REPO_ROOT).as_posix()
    try:
        yield base_dir, report_dir_abs, report_dir_rel
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(report_dir_abs, ignore_errors=True)


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _build_export_fixture(base_dir: Path, **manifest_overrides):
    """Build a minimal Phase 8E-style export dir with a manifest and evidence copies."""
    export_dir = base_dir / "export"
    evidence_dir = export_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    records_bytes = json.dumps({"product_id": "prod-aaa", "record_hash": "abc123"}, sort_keys=True).encode("utf-8") + b"\n"
    verification_bytes = json.dumps({"verification_status": "valid"}, sort_keys=True).encode("utf-8") + b"\n"
    verification_md_bytes = b"# verification\nverification_status: valid\n"
    query_bytes = json.dumps({"query_status": "success"}, sort_keys=True).encode("utf-8") + b"\n"
    query_md_bytes = b"# query\nquery_status: success\n"

    files = {
        "audit_records_jsonl": ("audit-records.jsonl", records_bytes),
        "verification_json": ("audit-store-verification.json", verification_bytes),
        "verification_md": ("audit-store-verification.md", verification_md_bytes),
        "query_json": ("audit-query-result.json", query_bytes),
        "query_md": ("audit-query-result.md", query_md_bytes),
    }

    source_evidence = []
    copied_files = []
    for label, (filename, data) in files.items():
        dest = evidence_dir / filename
        dest.write_bytes(data)
        digest = _sha256_bytes(data)
        source_evidence.append(
            {
                "label": label,
                "path": _rel(dest),
                "exists": True,
                "allowed": True,
                "sha256": digest,
                "size_bytes": len(data),
                "copied_to": _rel(dest),
            }
        )
        copied_files.append({"label": label, "dest_path": _rel(dest), "sha256": digest})

    manifest = {
        "phase8e_status": "success",
        "durable_audit_store_status": "export_pack",
        "phase7d_runtime_readiness": "implemented_manual_gate",
        "export_status": "success",
        "export_dir": _rel(export_dir),
        "generated_at": "2026-07-01T00:00:00Z",
        "include_copies": True,
        "source_evidence": source_evidence,
        "missing_evidence": [],
        "source_hashes": {label: entry["sha256"] for label, entry in zip(files, source_evidence)},
        "record_count": 1,
        "invalid_line_count": 0,
        "warning_count": 0,
        "verification_status": "valid",
        "query_status": "success",
        "summaries": {"by_product_id": {"prod-aaa": 1}},
        "copied_files": copied_files,
        "warnings": [],
        "safety_statement": "test fixture",
        "limitations": [],
    }
    manifest.update(manifest_overrides)
    manifest_path = export_dir / "audit-export-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, manifest, evidence_dir


# ── A. File existence and status ────────────────────────────────────────────

def test_phase8h_required_files_exist() -> None:
    for path in (TASK_FILE, DESIGN_DOC, VERIFIER_SCRIPT, RUNNER_SCRIPT, THIS_TEST):
        assert path.is_file(), f"missing Phase 8H file: {path}"


def test_no_phase8h_shell_runner_exists() -> None:
    scripts_dir = REPO_ROOT / "scripts/dev"
    assert not any(scripts_dir.glob("run_phase8h*.sh")), "Phase 8H must not add a shell runner"
    assert not any(scripts_dir.glob("*phase8h*.sh")), "Phase 8H must not add any shell runner"


def test_phase8h_status_tokens() -> None:
    assert "phase8h_status: success" in _text(TASK_FILE)
    text = _text(DESIGN_DOC)
    assert "phase8h_status: success" in text
    assert "phase8g_status: success" in text
    assert "phase7d_runtime_readiness: implemented_manual_gate" in text
    assert "durable_audit_store_status: export_integrity_verifier_hardened" in text
    assert "signing_implementation_status: not_implemented" in text
    assert "verifier_hardening_status: enabled" in text


# ── B. Scope safety ──────────────────────────────────────────────────────────

def test_phase8h_design_doc_scope_tokens() -> None:
    low = _text(DESIGN_DOC).lower()
    for token in (
        "verifier hardening only",
        "local hash-only verifier remains",
        "no signing implementation",
        "no signature verification implementation",
        "no key generation",
        "no private key handling",
        "no encryption",
        "no kms/secrets manager",
        "no backend/api/database",
        "no sqlite/s3/dynamodb",
        "no network behavior",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
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


def test_verifier_script_no_signing_key_or_encryption_commands() -> None:
    text = _text(VERIFIER_SCRIPT)
    for forbidden in ("ssh-keygen", "openssl", "gpg ", "cryptography.hazmat", "Fernet", "rsa.generate"):
        assert forbidden not in text, f"verifier script must not: {forbidden}"


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
        "verify_phase8c_audit_store",
        "run_phase8c_audit_report",
        "query_phase8d_audit_store",
        "run_phase8d_audit_query",
        "build_phase8e_audit_export_pack",
        "run_phase8e_audit_export",
    ):
        assert forbidden not in text, f"shell runner must not contain: {forbidden}"


def test_shell_runner_executable_mode() -> None:
    mode = RUNNER_SCRIPT.stat().st_mode & 0o777
    assert mode == 0o755, f"expected 0755, got {oct(mode)}"


def test_shell_runner_git_index_mode_is_100755() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-s", "scripts/dev/run_phase8g_export_integrity.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.stdout.startswith("100755 "), f"unexpected git index mode: {result.stdout!r}"


def test_shell_runner_bash_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(RUNNER_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_verifier_script_py_compile_ok() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(VERIFIER_SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


# ── D. Hardened schema fields ──────────────────────────────────────────────

REQUIRED_HARDENED_FIELDS = (
    "phase8h_status",
    "report_schema_version",
    "issue_taxonomy_version",
    "compatibility_matrix_version",
    "verifier_hardening_status",
    "deterministic_output_contract",
    "compatibility_result",
    "severity_counts",
    "incident_classification",
    "reviewer_action",
    "reviewer_action_required",
    "approval_boundary_statement",
)

REQUIRED_LEGACY_FIELDS = (
    "phase8g_status",
    "durable_audit_store_status",
    "phase7d_runtime_readiness",
    "signing_implementation_status",
    "verification_status",
    "hash_only_verification",
    "manifest_path",
    "report_dir",
    "evidence_count",
    "copied_evidence_count",
    "issue_count",
    "manifest_hash_status",
    "bundle_hash_status",
    "computed_manifest_hash",
    "manifest_manifest_hash",
    "computed_bundle_hash",
    "manifest_bundle_hash",
    "evidence_results",
    "copied_evidence_results",
    "issues",
    "safety_statement",
    "limitations",
)


def test_hardened_fields_present_missing_manifest(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    missing_path = base_dir / "does-not-exist.json"
    result = _run_verifier("--manifest-path", missing_path.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    for field in REQUIRED_HARDENED_FIELDS + REQUIRED_LEGACY_FIELDS:
        assert field in report, f"missing field: {field}"


def test_hardened_fields_present_valid_export(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, _, _ = _build_export_fixture(base_dir)
    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    for field in REQUIRED_HARDENED_FIELDS + REQUIRED_LEGACY_FIELDS:
        assert field in report, f"missing field: {field}"


# ── E. Missing manifest hardening ────────────────────────────────────────────

def test_missing_manifest_hardening(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    missing_path = base_dir / "does-not-exist.json"
    result = _run_verifier("--manifest-path", missing_path.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "empty"
    assert report["incident_classification"] == "missing_manifest"
    assert report["reviewer_action"] == "no_action_required"
    assert report["reviewer_action_required"] is False
    md_text = (report_dir_abs / "export-integrity-verification.md").read_text(encoding="utf-8")
    assert "verified export is not approval" in md_text.lower()


# ── F. Valid export hardening ─────────────────────────────────────────────

def test_valid_export_hardening(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, _, _ = _build_export_fixture(base_dir)
    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "valid"
    assert report["compatibility_result"] == "compatible"
    assert report["incident_classification"] == "none"
    assert report["reviewer_action"] == "no_action_required"
    assert report["reviewer_action_required"] is False
    assert report["severity_counts"]["warning"] == 0
    assert report["severity_counts"]["critical"] == 0
    assert report["deterministic_output_contract"]["stable_report_schema"] is True
    assert report["report_schema_version"] == "phase8g.integrity_report.v2"


# ── G. Issue taxonomy and severity mapping ──────────────────────────────────

def _assert_warning_issue(report, expected_issue_type) -> None:
    assert report["verification_status"] == "warning"
    assert report["reviewer_action"] == "manual_review_required"
    assert report["reviewer_action_required"] is True
    assert report["incident_classification"] == "tamper_evidence_warning"
    matches = [i for i in report["issues"] if i["issue_type"] == expected_issue_type]
    assert matches, f"expected issue_type {expected_issue_type} not found in {report['issues']}"
    for issue in matches:
        assert issue["severity"] == "warning"
        assert issue["incident_classification"] == "tamper_evidence_warning"
        assert issue["reviewer_action"] == "manual_review_required"


def test_evidence_hash_mismatch_taxonomy(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, evidence_dir = _build_export_fixture(base_dir)
    (evidence_dir / "audit-records.jsonl").write_bytes(b'{"tampered": true}\n')

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert any(i["issue_type"] in ("hash_mismatch", "copied_evidence_hash_mismatch") for i in report["issues"])
    for issue in report["issues"]:
        if issue["issue_type"] in ("hash_mismatch", "copied_evidence_hash_mismatch"):
            assert issue["severity"] == "warning"
            assert issue["incident_classification"] == "tamper_evidence_warning"
            assert issue["reviewer_action"] == "manual_review_required"
    assert report["reviewer_action_required"] is True


def test_evidence_size_mismatch_taxonomy(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(base_dir)
    for entry in manifest["source_evidence"]:
        if entry["label"] == "audit_records_jsonl":
            entry["size_bytes"] = entry["size_bytes"] + 1
            entry["sha256"] = None
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    _assert_warning_issue(report, "size_mismatch")


def test_missing_evidence_taxonomy(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, evidence_dir = _build_export_fixture(base_dir)
    (evidence_dir / "audit-query-result.md").unlink()

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "warning"
    assert any(
        i["issue_type"] in ("missing_evidence_file", "missing_copied_evidence_file") for i in report["issues"]
    )
    assert report["incident_classification"] == "tamper_evidence_warning"
    assert report["reviewer_action"] == "manual_review_required"
    assert report["reviewer_action_required"] is True


def test_manifest_hash_mismatch_taxonomy(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(base_dir)
    manifest["manifest_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    _assert_warning_issue(report, "manifest_hash_mismatch")


def test_bundle_hash_mismatch_taxonomy(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(base_dir)
    manifest["bundle_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    _assert_warning_issue(report, "bundle_hash_mismatch")


# ── H. Critical path/manifest behavior ───────────────────────────────────────

def test_invalid_json_manifest_critical(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    bad = base_dir / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    result = _run_verifier("--manifest-path", _rel(bad), "--report-dir", report_dir_rel)
    assert result.returncode != 0
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "invalid"
    assert report["severity_counts"]["critical"] == 1
    assert report["reviewer_action"] == "reject_export_until_resolved"
    assert report["incident_classification"] == "malformed_manifest"


def test_json_array_manifest_critical(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    arr = base_dir / "array.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    result = _run_verifier("--manifest-path", _rel(arr), "--report-dir", report_dir_rel)
    assert result.returncode != 0
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["verification_status"] == "invalid"
    assert report["incident_classification"] == "malformed_manifest"
    assert report["reviewer_action"] == "reject_export_until_resolved"


@pytest.mark.parametrize("root", ["vault", "docs", "scripts", "tests", "codex"])
def test_reject_manifest_path_under_rejected_roots_critical(root, work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    marker = REPO_ROOT / root / f"_phase8h_pytest_{uuid.uuid4().hex[:8]}.json"
    marker.write_text("{}", encoding="utf-8")
    try:
        result = _run_verifier("--manifest-path", marker.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
        assert result.returncode != 0
        report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
        assert report["verification_status"] == "invalid"
        assert report["severity_counts"]["critical"] == 1
        assert report["reviewer_action"] == "reject_export_until_resolved"
        assert report["incident_classification"] == "path_safety_violation"
    finally:
        marker.unlink(missing_ok=True)


def test_reject_symlinked_manifest_critical(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    real = base_dir / "real.json"
    real.write_text("{}", encoding="utf-8")
    link = base_dir / "link.json"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks not supported in this environment")
    result = _run_verifier("--manifest-path", link.relative_to(REPO_ROOT).as_posix(), "--report-dir", report_dir_rel)
    assert result.returncode != 0
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["incident_classification"] == "path_safety_violation"
    assert report["reviewer_action"] == "reject_export_until_resolved"


def test_reject_report_dir_outside_guarded_root(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, _, _ = _build_export_fixture(base_dir)
    outside_report_dir = REPO_ROOT / "tmp/phase8g-not-allowed"
    try:
        result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", "tmp/phase8g-not-allowed")
        assert result.returncode != 0
        assert not outside_report_dir.exists()
    finally:
        shutil.rmtree(outside_report_dir, ignore_errors=True)


# ── I. Compatibility matrix behavior ─────────────────────────────────────────

def test_compatibility_compatible(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, _, _ = _build_export_fixture(base_dir)
    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["compatibility_result"] == "compatible"
    assert not any(i["issue_type"] == "compatibility_warning" for i in report["issues"])


def test_compatibility_missing_field_review_required(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(base_dir)
    del manifest["phase8e_status"]
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["compatibility_result"] == "review_required"
    compat_issues = [i for i in report["issues"] if i["issue_type"] == "compatibility_warning"]
    assert compat_issues
    assert compat_issues[0]["severity"] == "warning"
    assert report["verification_status"] == "warning"


def test_compatibility_unknown_value_review_required(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(base_dir, durable_audit_store_status=None)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["compatibility_result"] == "review_required"
    assert any(i["issue_type"] == "compatibility_warning" for i in report["issues"])


def test_compatibility_conflicting_value_incompatible(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, _ = _build_export_fixture(
        base_dir, phase7d_runtime_readiness="approve_all_mode"
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert result.returncode == 0, result.stderr
    report = json.loads((report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8"))
    assert report["compatibility_result"] == "incompatible"
    compat_issues = [i for i in report["issues"] if i["issue_type"] == "compatibility_warning"]
    assert compat_issues
    assert compat_issues[0]["severity"] == "warning"
    # Incompatible is a review issue, not a critical path-safety failure.
    assert report["verification_status"] == "warning"
    assert report["severity_counts"]["critical"] == 0


# ── J. Deterministic output behavior ──────────────────────────────────────

def test_deterministic_output_across_repeated_runs(work_dir) -> None:
    base_dir, report_dir_abs, report_dir_rel = work_dir
    manifest_path, manifest, evidence_dir = _build_export_fixture(base_dir)
    (evidence_dir / "audit-records.jsonl").write_bytes(b'{"tampered": true}\n')

    first = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert first.returncode == 0, first.stderr
    first_json = (report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8")
    first_report = json.loads(first_json)

    second = _run_verifier("--manifest-path", _rel(manifest_path), "--report-dir", report_dir_rel)
    assert second.returncode == 0, second.stderr
    second_json = (report_dir_abs / "export-integrity-verification.json").read_text(encoding="utf-8")
    second_report = json.loads(second_json)

    assert first_json == second_json, "report JSON must be byte-identical across repeated runs"

    issue_types_first = [i["issue_type"] for i in first_report["issues"]]
    issue_types_second = [i["issue_type"] for i in second_report["issues"]]
    assert issue_types_first == issue_types_second

    severities_first = [i["severity"] for i in first_report["issues"]]
    severity_rank = {"critical": 0, "warning": 1, "info": 2}
    assert [severity_rank[s] for s in severities_first] == sorted(severity_rank[s] for s in severities_first)

    evidence_keys_first = [(e["label"] or "", e["path"] or "") for e in first_report["evidence_results"]]
    assert evidence_keys_first == sorted(evidence_keys_first)
    copied_keys_first = [(e["label"] or "", e["path"] or "") for e in first_report["copied_evidence_results"]]
    assert copied_keys_first == sorted(copied_keys_first)


# ── K. Documentation regression ───────────────────────────────────────────────

def test_roadmap_references_phase8h() -> None:
    text = _text(ROADMAP)
    assert "Phase 8H" in text
    assert "Export Integrity Verifier Hardening" in text
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_references_phase8h() -> None:
    text = _text(PROJECT_STATE)
    assert "docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md" in text
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_phase8g_doc_references_phase8h() -> None:
    assert "Phase 8H" in _text(PHASE8G_DOC)


def test_phase8f_doc_references_phase8h() -> None:
    assert "Phase 8H" in _text(PHASE8F_DOC)


def test_phase8e_doc_references_phase8h() -> None:
    assert "Phase 8H" in _text(PHASE8E_DOC)


# ── L. Protected runtime files unchanged ──────────────────────────────────────

def test_protected_runtime_files_unchanged() -> None:
    for path, expected_hash in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected file: {path}"
        assert _sha256_file(path) == expected_hash, f"protected runtime changed: {path}"


# ── M. Static safety for new Phase 8H files and modified verifier ───────────

def test_new_phase8h_files_static_safety() -> None:
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
    for path in NEW_PHASE8H_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
