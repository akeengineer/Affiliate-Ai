from __future__ import annotations

import copy
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

RUNTIME = REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/069-phase9c-local-operator-registry-prototype.md"
DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9B_DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

INPUT_DIR = REPO_ROOT / "tmp/phase9c-test-input"
OUT_BASE = "tmp/phase9c-local-operator-registry"

PROTECTED_RUNTIME_FILES = (
    REPO_ROOT / "scripts/dev/verify_phase8m_detached_signature.py",
    REPO_ROOT / "scripts/dev/run_phase8m_detached_signature_verifier.sh",
    REPO_ROOT / "scripts/dev/build_phase8l_detached_signature.py",
    REPO_ROOT / "scripts/dev/run_phase8l_detached_signature.sh",
    REPO_ROOT / "scripts/dev/verify_phase8g_export_integrity.py",
    REPO_ROOT / "scripts/dev/run_phase8g_export_integrity.sh",
    REPO_ROOT / "scripts/dev/build_phase8e_audit_export_pack.py",
    REPO_ROOT / "scripts/dev/run_phase8e_audit_export.sh",
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
    REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh": "372aef7a133950a24a1de859a1ba0c01486fd2c84bf46ded783105acc4e47b7d",
    REPO_ROOT / "scripts/dev/execute_single_gate_approval.py": "1b1d00817b1ae89c2840f18c9fe3b73f091abec9c900bf0bff83ad6820e9cebb",
}

EXCLUDED_PARTS = {".git", ".venv", "tmp", "vault", "node_modules", "vendor"}

VALID_RECORD = {
    "actor_schema_version": "phase9b.actor_metadata.v1",
    "actor_id": "actor_operator_one",
    "actor_type": "human_operator",
    "actor_display_label": "Operator One",
    "actor_role_labels": ["operator"],
    "actor_identity_assurance": "operator_declared",
    "actor_identity_source": "environment_operator_label",
    "actor_session_reference": None,
    "actor_attestation": {"attestation_type": "operator_statement"},
    "actor_action_scope": {"action_category": "final_acceptance_review"},
    "identity_evidence_references": [],
    "actor_timestamp_utc": "2026-07-03T00:00:00Z",
    "privacy_classification": "pseudonymous",
    "approval_boundary_statement": "actor metadata is not approval",
}
SECOND_RECORD = {
    **copy.deepcopy(VALID_RECORD),
    "actor_id": "actor_reviewer_two",
    "actor_type": "reviewer",
    "actor_display_label": "Reviewer Two",
    "actor_role_labels": ["reviewer"],
    "actor_identity_assurance": "unauthenticated",
    "actor_identity_source": "none",
    "actor_action_scope": {"action_category": "incident_review"},
    "approval_boundary_statement": "approval remains Phase 7D selected-gate manual boundary",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(_text(path).lower().replace("`", "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_input(name: str, payload) -> str:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = INPUT_DIR / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return f"tmp/phase9c-test-input/{name}"


def _run(mode: str, input_rel=None, output_dir=None, raw_input=None):
    out = output_dir or f"{OUT_BASE}/{mode}-run"
    cmd = [sys.executable, str(RUNTIME), "--mode", mode, "--output-dir", out]
    if input_rel is not None:
        cmd += ["--input", input_rel]
    if raw_input is not None:
        cmd += ["--input", raw_input]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    report_path = REPO_ROOT / out / "operator-registry-report.json"
    report = json.loads(_text(report_path)) if report_path.is_file() else None
    return proc, report, REPO_ROOT / out


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase9c_required_files_exist() -> None:
    for path in (RUNTIME, RUNNER, TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9C file: {path}"


def test_phase9c_status_tokens() -> None:
    assert "phase9c_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    for token in (
        "phase9c_status: success",
        "actor_metadata_runtime_status: local_registry_prototype",
        "local_operator_registry_status: prototype_local_only",
        "identity_runtime_status: not_implemented",
        "rbac_runtime_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


def test_phase9c_runner_is_executable_755() -> None:
    mode = stat.S_IMODE(RUNNER.stat().st_mode)
    assert mode == 0o755, f"runner mode is {oct(mode)}, expected 0o755"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9c_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "local-only operator registry prototype",
        "no authentication runtime",
        "no rbac runtime",
        "no login",
        "no session runtime",
        "no user store",
        "no backend/api/database",
        "no key management runtime",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no phase 8 runtime behavior change",
    ):
        assert token in low, f"missing scope safety token: {token}"


# ---------------------------------------------------------------------------
# C. Runtime static safety
# ---------------------------------------------------------------------------


def test_phase9c_runtime_static_safety() -> None:
    src = _text(RUNTIME)
    low = src.lower()
    assert "import subprocess" not in src
    assert "subprocess." not in src
    assert "sqlite3" not in low
    assert "boto3" not in low
    assert "import requests" not in low
    assert "httpx" not in low
    assert "urllib" not in low
    assert "fastapi" not in low
    assert "oauth" not in low
    assert "oidc" not in low
    assert "saml" not in low
    assert ".connect(" not in src
    assert "CREATE TABLE" not in src
    assert "ssh-keygen" not in low
    assert "openssl genrsa" not in low
    assert "http://" not in low
    assert "https://" not in low
    # no wrapper / primitive / Phase 8 runtime call
    assert "run_phase7d" not in low
    assert "execute_single_gate_approval" not in low
    assert "run_phase8" not in low


def test_phase9c_runner_static_safety() -> None:
    src = _text(RUNNER)
    assert "--execute" not in src
    assert "APPROVE_PROMOTE=true" not in src
    assert "APPROVE_DECISION=true" not in src
    assert "APPROVE_FINALIZE=true" not in src
    assert "approve_all=true" not in src
    assert "run_phase7d" not in src
    assert "execute_single_gate_approval" not in src
    assert "run_phase8" not in src
    mode = stat.S_IMODE(RUNNER.stat().st_mode)
    assert mode == 0o755


def test_phase9c_py_compile_and_bash_n() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(RUNTIME)],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    proc = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


# ---------------------------------------------------------------------------
# D. Valid build behavior
# ---------------------------------------------------------------------------


def test_phase9c_valid_build() -> None:
    inp = _write_input("valid_build.json", {"actor_metadata": [VALID_RECORD, SECOND_RECORD]})
    proc, report, out_dir = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/valid-build")
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "operator-registry.json").is_file()
    assert (out_dir / "operator-registry-report.json").is_file()
    assert (out_dir / "operator-registry-report.md").is_file()
    assert report["validation_status"] == "valid"
    assert report["registry_status"] == "built"
    assert report["registry_record_count"] == 2
    assert report["reviewer_action"] == "no_action_required"
    md = _text(out_dir / "operator-registry-report.md").lower()
    assert "local operator registry is not authentication" in md
    assert "registry presence is not approval" in md
    assert "valid actor metadata is not approval" in md
    # outputs only under the output dir
    for f in out_dir.iterdir():
        assert f.parent == out_dir


# ---------------------------------------------------------------------------
# E. Validate mode behavior
# ---------------------------------------------------------------------------


def test_phase9c_validate_mode() -> None:
    inp = _write_input("validate_mode.json", [VALID_RECORD])
    proc, report, out_dir = _run("validate", input_rel=inp, output_dir=f"{OUT_BASE}/validate-mode")
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "operator-registry-report.json").is_file()
    assert not (out_dir / "operator-registry.json").is_file()
    assert report["validation_status"] == "valid"


# ---------------------------------------------------------------------------
# F. List / report behavior
# ---------------------------------------------------------------------------


def test_phase9c_list_and_report() -> None:
    out = f"{OUT_BASE}/list-report"
    inp = _write_input("list_report.json", {"actor_metadata": [VALID_RECORD, SECOND_RECORD]})
    proc, _, out_dir = _run("build", input_rel=inp, output_dir=out)
    assert proc.returncode == 0, proc.stderr

    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--mode", "list", "--output-dir", out],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "operator-registry-list.json").is_file()
    assert (out_dir / "operator-registry-list.md").is_file()
    listing = json.loads(_text(out_dir / "operator-registry-list.json"))
    ids = {e["actor_id"] for e in listing["actor_listing"]}
    assert {"actor_operator_one", "actor_reviewer_two"} <= ids

    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--mode", "report", "--output-dir", out],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "operator-registry-report.json").is_file()


# ---------------------------------------------------------------------------
# G. Invalid JSON / input behavior
# ---------------------------------------------------------------------------


def test_phase9c_missing_input_nonzero() -> None:
    proc, _, _ = _run("build", input_rel="tmp/phase9c-test-input/does-not-exist.json",
                       output_dir=f"{OUT_BASE}/missing")
    assert proc.returncode != 0


def test_phase9c_invalid_json_nonzero() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    p = INPUT_DIR / "broken.json"
    p.write_text("not json{", encoding="utf-8")
    proc, report, _ = _run("build", input_rel="tmp/phase9c-test-input/broken.json",
                            output_dir=f"{OUT_BASE}/invalid-json")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_json" for i in report["issues"])


def test_phase9c_scalar_shape_nonzero() -> None:
    inp = _write_input("scalar.json", 42)
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/scalar")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_input_shape" for i in report["issues"])


# ---------------------------------------------------------------------------
# H. Required field validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", list(VALID_RECORD.keys()))
def test_phase9c_missing_required_field(field: str) -> None:
    record = copy.deepcopy(VALID_RECORD)
    del record[field]
    inp = _write_input(f"missing_{field}.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/missing-{field}")
    assert proc.returncode != 0
    assert report["validation_status"] == "invalid"
    assert report["registry_status"] == "not_built"
    assert report["reviewer_action"] == "reject_actor_metadata_until_resolved"


# ---------------------------------------------------------------------------
# I. Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field,bad,issue", [
    ("actor_type", "wizard", "actor_type_unknown"),
    ("actor_role_labels", ["overlord"], "actor_role_label_unknown"),
    ("actor_identity_assurance", "telepathic", "actor_identity_assurance_insufficient"),
    ("actor_identity_source", "crystal_ball", "actor_identity_source_unknown"),
])
def test_phase9c_enum_rejection(field, bad, issue) -> None:
    record = copy.deepcopy(VALID_RECORD)
    record[field] = bad
    inp = _write_input(f"enum_{field}.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/enum-{field}")
    assert proc.returncode != 0
    assert report["validation_status"] == "invalid"
    assert any(i["issue_type"] == issue for i in report["issues"])


def test_phase9c_unknown_action_scope_rejected() -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["actor_action_scope"] = {"action_category": "launch_missiles"}
    inp = _write_input("scope_bad.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/scope-bad")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "actor_scope_invalid" for i in report["issues"])


# ---------------------------------------------------------------------------
# J. actor_id validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_id", [
    "actor id with space",
    "actor_person@example.com",
    "actor_HasUpperCase",
    "actor_secret=abc",
    "actor_approved_one",
    "AB",
])
def test_phase9c_actor_id_rejection(bad_id) -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["actor_id"] = bad_id
    inp = _write_input(f"id_{abs(hash(bad_id))}.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/id-{abs(hash(bad_id))}")
    assert proc.returncode != 0
    assert report["validation_status"] == "invalid"


def test_phase9c_actor_id_url_scheme_rejected() -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["actor_id"] = "actor_ftp://host"
    inp = _write_input("id_url.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/id-url")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "actor_id_invalid_format" for i in report["issues"])


# ---------------------------------------------------------------------------
# K. Privacy / secret validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [
    "AFFILIATE_PHASE8L_PROTOTYPE_KEY=deadbeef",
    "BEGIN PRIVATE KEY",
    "API_KEY=abc123",
    "SECRET=abc123",
    "TOKEN=abc123",
    "PASSWORD=hunter2",
    "AWS_SECRET_ACCESS_KEY",
    "access_token=xyz",
    "id_token=xyz",
    "refresh_token=xyz",
    "db_password=hunter2",
])
def test_phase9c_secret_rejection(value) -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["actor_display_label"] = value
    inp = _write_input(f"secret_{abs(hash(value))}.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/secret-{abs(hash(value))}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "identity_metadata_contains_secret" for i in report["issues"])


def test_phase9c_raw_email_flagged_as_pii() -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["actor_display_label"] = "contact person@example.com"
    inp = _write_input("pii_email.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/pii-email")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "identity_metadata_contains_unnecessary_pii" for i in report["issues"])


# ---------------------------------------------------------------------------
# L. Approval boundary validation
# ---------------------------------------------------------------------------


def test_phase9c_approval_statement_missing_phrase_rejected() -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["approval_boundary_statement"] = "hello world"
    inp = _write_input("abs_bad.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/abs-bad")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_boundary_statement_missing" for i in report["issues"])


@pytest.mark.parametrize("flag", [
    "approved", "is_approved", "approval_granted", "auto_approve", "approve_all",
    "next_gate", "execute",
])
def test_phase9c_approval_flag_rejected(flag) -> None:
    record = copy.deepcopy(VALID_RECORD)
    record[flag] = True
    inp = _write_input(f"flag_{flag}.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/flag-{flag}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_flag_present" for i in report["issues"])


def test_phase9c_primitive_execution_intent_rejected() -> None:
    record = copy.deepcopy(VALID_RECORD)
    record["execute_primitive"] = True
    inp = _write_input("prim.json", [record])
    proc, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/prim")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "primitive_execution_intent_present" for i in report["issues"])


# ---------------------------------------------------------------------------
# M. Duplicate actor handling
# ---------------------------------------------------------------------------


def test_phase9c_duplicate_actor_handling() -> None:
    dup = copy.deepcopy(VALID_RECORD)
    inp = _write_input("dupes.json", {"actor_metadata": [VALID_RECORD, dup]})
    proc, report, out_dir = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/dupes")
    assert proc.returncode == 0, proc.stderr
    assert report["validation_status"] == "warning"
    assert report["registry_status"] == "built_with_warnings"
    assert report["duplicate_actor_count"] == 1
    assert report["reviewer_action"] == "manual_review_required"
    registry = json.loads(_text(out_dir / "operator-registry.json"))
    assert registry["registry_record_count"] == 1
    assert any(i["issue_type"] == "duplicate_actor_id" for i in report["issues"])


# ---------------------------------------------------------------------------
# N. Report schema behavior
# ---------------------------------------------------------------------------


def test_phase9c_report_schema() -> None:
    inp = _write_input("schema_ok.json", [VALID_RECORD])
    _, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/schema-ok")
    for field in (
        "phase9c_status", "phase7d_runtime_readiness", "durable_audit_store_status",
        "identity_boundary_status", "actor_metadata_schema_status",
        "actor_metadata_runtime_status", "local_operator_registry_status",
        "identity_runtime_status", "rbac_runtime_status", "authentication_runtime_status",
        "operator_identity_assurance_status", "signing_implementation_status",
        "signature_runtime_status", "signature_verifier_runtime_status",
        "key_management_runtime_status", "phase9_branch_workflow",
        "registry_status", "validation_status", "registry_record_count",
        "valid_record_count", "invalid_record_count", "duplicate_actor_count",
        "failure_count", "severity_counts", "reviewer_action", "reviewer_action_required",
        "incident_classification", "approval_boundary_statement", "safety_statement",
        "limitations", "issues",
    ):
        assert field in report, f"report missing field: {field}"
    assert set(report["severity_counts"]) == {"info", "warning", "critical"}

    # issue schema on an invalid run
    bad = copy.deepcopy(VALID_RECORD)
    bad["actor_type"] = "wizard"
    inp = _write_input("schema_bad.json", [bad])
    _, report, _ = _run("build", input_rel=inp, output_dir=f"{OUT_BASE}/schema-bad")
    for issue in report["issues"]:
        for key in ("issue_type", "severity", "incident_classification", "reviewer_action", "actor_id", "message"):
            assert key in issue, f"issue missing key: {key}"


# ---------------------------------------------------------------------------
# O. Path safety
# ---------------------------------------------------------------------------


def test_phase9c_input_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps([VALID_RECORD]), encoding="utf-8")
    proc, _, _ = _run("build", input_rel=str(outside), output_dir=f"{OUT_BASE}/outside")
    assert proc.returncode != 0


@pytest.mark.parametrize("path", [
    "docs/ROADMAP.md",
    "scripts/dev/run_phase9c_local_operator_registry.sh",
    "codex/tasks/069-phase9c-local-operator-registry-prototype.md",
])
def test_phase9c_forbidden_input_root_rejected(path) -> None:
    proc, _, _ = _run("build", input_rel=path, output_dir=f"{OUT_BASE}/forbidden")
    assert proc.returncode != 0


def test_phase9c_symlink_input_rejected() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = INPUT_DIR / "symlink_target.json"
    target.write_text(json.dumps([VALID_RECORD]), encoding="utf-8")
    link = INPUT_DIR / "symlink_input.json"
    if link.exists() or link.is_symlink():
        link.unlink()
    os.symlink(target, link)
    proc, _, _ = _run("build", input_rel="tmp/phase9c-test-input/symlink_input.json",
                       output_dir=f"{OUT_BASE}/symlink")
    assert proc.returncode != 0


def test_phase9c_output_dir_escape_rejected() -> None:
    inp = _write_input("out_escape.json", [VALID_RECORD])
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--mode", "build", "--input", inp,
         "--output-dir", "tmp/some-other-dir"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


def test_phase9c_output_dir_traversal_rejected() -> None:
    inp = _write_input("out_trav.json", [VALID_RECORD])
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--mode", "build", "--input", inp,
         "--output-dir", "tmp/phase9c-local-operator-registry/../.."],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


# ---------------------------------------------------------------------------
# P. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9c_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 9C" in roadmap
    assert "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md" in project_state
    for token in (
        "Current architecture", "no database", "no FastAPI", "no UI",
        "no external APIs", "no autopublish",
    ):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9B_DOC, PHASE9A_DOC, PHASE8O_DOC):
        assert "Phase 9C" in _text(doc), f"missing Phase 9C reference in {doc.name}"


# ---------------------------------------------------------------------------
# Q. Protected runtime files unchanged
# ---------------------------------------------------------------------------


def test_phase9c_protected_runtime_files_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


# ---------------------------------------------------------------------------
# R. Static safety for new Phase 9C files only
# ---------------------------------------------------------------------------


def test_phase9c_static_safety_new_files_only() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "ssh-keygen",
        "openssl genrsa",
        "openssl req",
        "openssl enc",
        "gpg --gen-key",
        "boto3.client",
        "sqlite3.connect",
        "CREATE TABLE",
        "uvicorn ",
        "curl ",
        "wget ",
        "python scripts/dev/execute_single_gate_approval.py",
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh",
    )
    for path in (RUNTIME, RUNNER, TASK_FILE, DOC):
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ---------------------------------------------------------------------------
# S. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9c_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
    assert not (REPO_ROOT / "package.json").exists()
