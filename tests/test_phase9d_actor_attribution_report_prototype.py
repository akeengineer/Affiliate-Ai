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

RUNTIME = REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/070-phase9d-actor-attribution-in-audit-reports.md"
DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE9B_DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

INPUT_DIR = REPO_ROOT / "tmp/phase9d-test-input"
OUT_BASE = "tmp/phase9d-actor-attribution"

PROTECTED_RUNTIME_FILES = (
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh",
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
    REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py": "19d8f8eea523c1b7014463fb351764842429dcb30076e4469a959bd7c326fb6e",
    REPO_ROOT / "scripts/dev/run_phase9c_local_operator_registry.sh": "6526dbeb53cbeeecf1485e73747ebee7f26e62c12f04295616c77b0f869bb21a",
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

ACTOR_ONE = {
    "actor_schema_version": "phase9b.actor_metadata.v1",
    "actor_id": "actor_operator_one",
    "actor_type": "human_operator",
    "actor_display_label": "Operator One",
    "actor_role_labels": ["operator"],
    "actor_identity_assurance": "operator_declared",
    "actor_identity_source": "environment_operator_label",
    "actor_action_scope": {"action_category": "final_acceptance_review"},
    "privacy_classification": "pseudonymous",
    "approval_boundary_statement": "actor metadata is not approval",
}
ACTOR_TWO = {
    **copy.deepcopy(ACTOR_ONE),
    "actor_id": "actor_reviewer_two",
    "actor_type": "reviewer",
    "actor_display_label": "Reviewer Two",
    "actor_role_labels": ["reviewer"],
    "actor_identity_assurance": "unauthenticated",
    "actor_identity_source": "none",
    "approval_boundary_statement": "approval remains Phase 7D selected-gate manual boundary",
}
EVIDENCE_ONE = {
    "evidence_id": "ev1",
    "evidence_type": "export_manifest",
    "evidence_path": "tmp/phase8e-audit-export/manifest.json",
    "evidence_phase": "phase8e",
    "evidence_purpose": "export pack",
}
EVIDENCE_TWO = {
    "evidence_id": "ev2",
    "evidence_type": "verification_report",
    "evidence_path": "tmp/phase8m-detached-signature-verifier/report.json",
    "evidence_phase": "phase8m",
    "evidence_purpose": "verifier report",
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
    return f"tmp/phase9d-test-input/{name}"


def _run(registry_rel, evidence_rel, actor_id=None, output_dir=None):
    out = output_dir or f"{OUT_BASE}/run"
    cmd = [sys.executable, str(RUNTIME), "--registry", registry_rel,
           "--evidence", evidence_rel, "--output-dir", out]
    if actor_id is not None:
        cmd += ["--actor-id", actor_id]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    report_path = REPO_ROOT / out / "actor-attribution-report.json"
    report = json.loads(_text(report_path)) if report_path.is_file() else None
    return proc, report, REPO_ROOT / out


def _valid_registry(name="reg.json", actors=None) -> str:
    return _write_input(name, {"actor_registry": actors or [ACTOR_ONE, ACTOR_TWO]})


def _valid_evidence(name="ev.json", refs=None) -> str:
    return _write_input(name, {"evidence_references": refs or [EVIDENCE_ONE, EVIDENCE_TWO]})


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase9d_required_files_exist() -> None:
    for path in (RUNTIME, RUNNER, TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9D file: {path}"


def test_phase9d_status_tokens() -> None:
    assert "phase9d_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    for token in (
        "phase9d_status: success",
        "actor_attribution_status: local_report_prototype",
        "actor_metadata_runtime_status: local_registry_prototype",
        "local_operator_registry_status: prototype_local_only",
        "identity_runtime_status: not_implemented",
        "rbac_runtime_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


def test_phase9d_runner_is_executable_755() -> None:
    mode = stat.S_IMODE(RUNNER.stat().st_mode)
    assert mode == 0o755, f"runner mode is {oct(mode)}, expected 0o755"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9d_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "local-only actor attribution report prototype",
        "consumes local phase 9c operator registry",
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


def test_phase9d_runtime_static_safety() -> None:
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
    assert "run_phase7d" not in low
    assert "execute_single_gate_approval" not in low
    assert "run_phase8" not in low


def test_phase9d_runner_static_safety() -> None:
    src = _text(RUNNER)
    assert "--execute" not in src
    assert "APPROVE_PROMOTE=true" not in src
    assert "APPROVE_DECISION=true" not in src
    assert "APPROVE_FINALIZE=true" not in src
    assert "approve_all=true" not in src
    assert "run_phase7d" not in src
    assert "execute_single_gate_approval" not in src
    assert "run_phase8" not in src
    assert stat.S_IMODE(RUNNER.stat().st_mode) == 0o755


def test_phase9d_py_compile_and_bash_n() -> None:
    proc = subprocess.run([sys.executable, "-m", "py_compile", str(RUNTIME)],
                          cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    proc = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


# ---------------------------------------------------------------------------
# D. Valid attribution behavior
# ---------------------------------------------------------------------------


def test_phase9d_valid_attribution() -> None:
    reg = _valid_registry("valid_reg.json")
    ev = _valid_evidence("valid_ev.json")
    proc, report, out_dir = _run(reg, ev, actor_id="actor_operator_one",
                                 output_dir=f"{OUT_BASE}/valid")
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "actor-attribution-report.json").is_file()
    assert (out_dir / "actor-attribution-report.md").is_file()
    assert report["attribution_report_status"] == "built"
    assert report["actor_attribution_status"] == "local_report_prototype"
    assert report["selected_actor_id"] == "actor_operator_one"
    assert report["evidence_reference_count"] == 2
    assert report["attributed_record_count"] == 2
    assert report["reviewer_action"] == "no_action_required"
    for rec in report["attributed_records"]:
        assert "actor_metadata" in rec
        assert rec["actor_id"] == "actor_operator_one"
        assert rec["evidence_id"] in ("ev1", "ev2")
    md = _text(out_dir / "actor-attribution-report.md").lower()
    assert "actor attribution is not authentication" in md
    assert "actor attribution is not approval" in md
    assert "attributed report is evidence only" in md
    for f in out_dir.iterdir():
        assert f.parent == out_dir


# ---------------------------------------------------------------------------
# E. Deterministic actor selection
# ---------------------------------------------------------------------------


def test_phase9d_default_actor_is_first_sorted() -> None:
    reg = _valid_registry("det_reg.json", actors=[ACTOR_TWO, ACTOR_ONE])
    ev = _valid_evidence("det_ev.json")
    proc, report, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/det")
    assert proc.returncode == 0, proc.stderr
    assert report["selected_actor_id"] == "actor_operator_one"


# ---------------------------------------------------------------------------
# F. Duplicate actor behavior
# ---------------------------------------------------------------------------


def test_phase9d_duplicate_actor() -> None:
    reg = _valid_registry("dup_reg.json", actors=[ACTOR_ONE, copy.deepcopy(ACTOR_ONE)])
    ev = _valid_evidence("dup_ev.json")
    proc, report, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/dup")
    assert proc.returncode == 0, proc.stderr
    assert report["attribution_report_status"] == "built_with_warnings"
    assert report["duplicate_actor_count"] == 1
    assert report["reviewer_action"] == "manual_review_required"
    assert any(i["issue_type"] == "duplicate_actor_id" for i in report["issues"])


# ---------------------------------------------------------------------------
# G. Missing / invalid registry
# ---------------------------------------------------------------------------


def test_phase9d_missing_registry_nonzero() -> None:
    ev = _valid_evidence("mr_ev.json")
    proc, _, _ = _run("tmp/phase9d-test-input/no-registry.json", ev, output_dir=f"{OUT_BASE}/mr")
    assert proc.returncode != 0


def test_phase9d_invalid_registry_json_nonzero() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "badreg.json").write_text("not json{", encoding="utf-8")
    ev = _valid_evidence("ir_ev.json")
    proc, report, _ = _run("tmp/phase9d-test-input/badreg.json", ev, output_dir=f"{OUT_BASE}/ir")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_registry_json" for i in report["issues"])


def test_phase9d_registry_scalar_nonzero() -> None:
    reg = _write_input("scalar_reg.json", 7)
    ev = _valid_evidence("sr_ev.json")
    proc, _, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/sr")
    assert proc.returncode != 0


def test_phase9d_registry_no_actors_nonzero() -> None:
    reg = _write_input("empty_reg.json", {"actor_registry": []})
    ev = _valid_evidence("er_ev.json")
    proc, report, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/er")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "registry_actor_missing" for i in report["issues"])


# ---------------------------------------------------------------------------
# H. Missing / invalid evidence
# ---------------------------------------------------------------------------


def test_phase9d_missing_evidence_nonzero() -> None:
    reg = _valid_registry("me_reg.json")
    proc, _, _ = _run(reg, "tmp/phase9d-test-input/no-evidence.json", output_dir=f"{OUT_BASE}/me")
    assert proc.returncode != 0


def test_phase9d_invalid_evidence_json_nonzero() -> None:
    reg = _valid_registry("ie_reg.json")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "badev.json").write_text("not json{", encoding="utf-8")
    proc, report, _ = _run(reg, "tmp/phase9d-test-input/badev.json", output_dir=f"{OUT_BASE}/ie")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_evidence_json" for i in report["issues"])


def test_phase9d_evidence_scalar_nonzero() -> None:
    reg = _valid_registry("es_reg.json")
    ev = _write_input("scalar_ev.json", 9)
    proc, _, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/es")
    assert proc.returncode != 0


def test_phase9d_evidence_no_refs_nonzero() -> None:
    reg = _valid_registry("nr_reg.json")
    ev = _write_input("empty_ev.json", {"evidence_references": []})
    proc, _, _ = _run(reg, ev, output_dir=f"{OUT_BASE}/nr")
    assert proc.returncode != 0


def test_phase9d_evidence_missing_field_nonzero() -> None:
    reg = _valid_registry("mf_reg.json")
    ev = _write_input("mf_ev.json", {"evidence_references": [{"evidence_id": "e1", "evidence_type": "t"}]})
    proc, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/mf")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "evidence_reference_missing_field" for i in report["issues"])


# ---------------------------------------------------------------------------
# I. Actor not found
# ---------------------------------------------------------------------------


def test_phase9d_actor_not_found() -> None:
    reg = _valid_registry("nf_reg.json")
    ev = _valid_evidence("nf_ev.json")
    proc, report, _ = _run(reg, ev, actor_id="actor_ghost", output_dir=f"{OUT_BASE}/nf")
    assert proc.returncode != 0
    assert (report["actor_attribution_status"] == "failed_actor_not_found"
            or report["attribution_report_status"] == "not_built")
    assert report["reviewer_action"] in ("manual_review_required", "reject_actor_metadata_until_resolved")
    assert any(i["issue_type"] == "actor_not_found" for i in report["issues"])


# ---------------------------------------------------------------------------
# J. Privacy / secret validation
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
def test_phase9d_secret_rejection(value) -> None:
    actor = copy.deepcopy(ACTOR_ONE)
    actor["actor_display_label"] = value
    reg = _valid_registry(f"sec_reg_{abs(hash(value))}.json", actors=[actor])
    ev = _valid_evidence(f"sec_ev_{abs(hash(value))}.json")
    proc, report, _ = _run(reg, ev, actor_id="actor_operator_one",
                           output_dir=f"{OUT_BASE}/sec-{abs(hash(value))}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "actor_metadata_contains_secret" for i in report["issues"])


def test_phase9d_raw_email_in_actor_id_rejected() -> None:
    actor = copy.deepcopy(ACTOR_ONE)
    actor["actor_id"] = "actor_person@example.com"
    reg = _valid_registry("email_reg.json", actors=[actor])
    ev = _valid_evidence("email_ev.json")
    proc, report, _ = _run(reg, ev, actor_id="actor_person@example.com", output_dir=f"{OUT_BASE}/email")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "actor_metadata_contains_unnecessary_pii" for i in report["issues"])


# ---------------------------------------------------------------------------
# K. Approval boundary validation
# ---------------------------------------------------------------------------


def test_phase9d_approval_statement_missing_phrase_rejected() -> None:
    actor = copy.deepcopy(ACTOR_ONE)
    actor["approval_boundary_statement"] = "hello world"
    reg = _valid_registry("abs_reg.json", actors=[actor])
    ev = _valid_evidence("abs_ev.json")
    proc, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/abs")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_boundary_statement_missing" for i in report["issues"])


@pytest.mark.parametrize("flag", [
    "approved", "is_approved", "approval_granted", "auto_approve", "approve_all",
    "next_gate", "execute",
])
def test_phase9d_approval_flag_rejected(flag) -> None:
    reg = _valid_registry(f"flag_reg_{flag}.json")
    ref = {**copy.deepcopy(EVIDENCE_ONE), flag: True}
    ev = _write_input(f"flag_ev_{flag}.json", {"evidence_references": [ref]})
    proc, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/flag-{flag}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_flag_present" for i in report["issues"])


def test_phase9d_primitive_execution_intent_rejected() -> None:
    reg = _valid_registry("prim_reg.json")
    ref = {**copy.deepcopy(EVIDENCE_ONE), "execute_primitive": True}
    ev = _write_input("prim_ev.json", {"evidence_references": [ref]})
    proc, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/prim")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "primitive_execution_intent_present" for i in report["issues"])


# ---------------------------------------------------------------------------
# L. Report schema behavior
# ---------------------------------------------------------------------------


def test_phase9d_report_schema() -> None:
    reg = _valid_registry("schema_reg.json")
    ev = _valid_evidence("schema_ev.json")
    _, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/schema")
    for field in (
        "phase9d_status", "phase7d_runtime_readiness", "durable_audit_store_status",
        "identity_boundary_status", "actor_metadata_schema_status",
        "actor_metadata_runtime_status", "local_operator_registry_status",
        "actor_attribution_status", "identity_runtime_status", "rbac_runtime_status",
        "authentication_runtime_status", "operator_identity_assurance_status",
        "signing_implementation_status", "signature_runtime_status",
        "signature_verifier_runtime_status", "key_management_runtime_status",
        "phase9_branch_workflow", "attribution_report_status", "selected_actor_id",
        "evidence_reference_count", "attributed_record_count", "unattributed_record_count",
        "duplicate_actor_count", "failure_count", "severity_counts", "reviewer_action",
        "reviewer_action_required", "incident_classification", "approval_boundary_statement",
        "safety_statement", "limitations", "issues", "attributed_records",
    ):
        assert field in report, f"report missing field: {field}"
    assert set(report["severity_counts"]) == {"info", "warning", "critical"}

    # issue schema on an invalid run
    reg = _valid_registry("schema_bad_reg.json")
    ev = _write_input("schema_bad_ev.json", {"evidence_references": [{"evidence_id": "e1"}]})
    _, report, _ = _run(reg, ev, actor_id="actor_operator_one", output_dir=f"{OUT_BASE}/schema-bad")
    for issue in report["issues"]:
        for key in ("issue_type", "severity", "incident_classification", "reviewer_action",
                    "actor_id", "evidence_id", "message"):
            assert key in issue, f"issue missing key: {key}"


# ---------------------------------------------------------------------------
# M. Path safety
# ---------------------------------------------------------------------------


def test_phase9d_registry_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "reg.json"
    outside.write_text(json.dumps({"actor_registry": [ACTOR_ONE]}), encoding="utf-8")
    ev = _valid_evidence("out_ev.json")
    proc, _, _ = _run(str(outside), ev, output_dir=f"{OUT_BASE}/out-reg")
    assert proc.returncode != 0


def test_phase9d_evidence_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "ev.json"
    outside.write_text(json.dumps({"evidence_references": [EVIDENCE_ONE]}), encoding="utf-8")
    reg = _valid_registry("out_reg.json")
    proc, _, _ = _run(reg, str(outside), output_dir=f"{OUT_BASE}/out-ev")
    assert proc.returncode != 0


@pytest.mark.parametrize("bad", ["docs/ROADMAP.md", "codex/tasks/070-phase9d-actor-attribution-in-audit-reports.md"])
def test_phase9d_forbidden_registry_root_rejected(bad) -> None:
    ev = _valid_evidence("forb_ev.json")
    proc, _, _ = _run(bad, ev, output_dir=f"{OUT_BASE}/forb")
    assert proc.returncode != 0


def test_phase9d_symlink_registry_rejected() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = INPUT_DIR / "sym_target_reg.json"
    target.write_text(json.dumps({"actor_registry": [ACTOR_ONE]}), encoding="utf-8")
    link = INPUT_DIR / "sym_reg.json"
    if link.exists() or link.is_symlink():
        link.unlink()
    os.symlink(target, link)
    ev = _valid_evidence("sym_ev.json")
    proc, _, _ = _run("tmp/phase9d-test-input/sym_reg.json", ev, output_dir=f"{OUT_BASE}/sym")
    assert proc.returncode != 0


def test_phase9d_output_dir_escape_rejected() -> None:
    reg = _valid_registry("oe_reg.json")
    ev = _valid_evidence("oe_ev.json")
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--registry", reg, "--evidence", ev,
         "--output-dir", "tmp/other-9d-dir"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


def test_phase9d_output_dir_traversal_rejected() -> None:
    reg = _valid_registry("ot_reg.json")
    ev = _valid_evidence("ot_ev.json")
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--registry", reg, "--evidence", ev,
         "--output-dir", "tmp/phase9d-actor-attribution/../.."],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


# ---------------------------------------------------------------------------
# N. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9d_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 9D" in roadmap
    assert "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md" in project_state
    for token in ("Current architecture", "no database", "no FastAPI", "no UI",
                  "no external APIs", "no autopublish"):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9C_DOC, PHASE9B_DOC, PHASE9A_DOC, PHASE8O_DOC):
        assert "Phase 9D" in _text(doc), f"missing Phase 9D reference in {doc.name}"


# ---------------------------------------------------------------------------
# O. Protected runtime files unchanged
# ---------------------------------------------------------------------------


def test_phase9d_protected_runtime_files_unchanged() -> None:
    for path in PROTECTED_RUNTIME_FILES:
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == PROTECTED_HASHES[path], f"protected runtime changed: {path}"


# ---------------------------------------------------------------------------
# P. Static safety for new Phase 9D files only
# ---------------------------------------------------------------------------


def test_phase9d_static_safety_new_files_only() -> None:
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
# Q. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9d_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        assert path.suffix.lower() not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert path.suffix.lower() not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
    assert not (REPO_ROOT / "package.json").exists()
