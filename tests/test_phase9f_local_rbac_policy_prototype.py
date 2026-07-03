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

RUNTIME = REPO_ROOT / "scripts/dev/evaluate_phase9f_local_rbac_policy.py"
RUNNER = REPO_ROOT / "scripts/dev/run_phase9f_local_rbac_policy.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/072-phase9f-local-rbac-policy-prototype.md"
DOC = REPO_ROOT / "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md"
THIS_TEST = Path(__file__)

ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
PHASE9E_DOC = REPO_ROOT / "docs/PHASE9E_RBAC_DESIGN.md"
PHASE9D_DOC = REPO_ROOT / "docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md"
PHASE9C_DOC = REPO_ROOT / "docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md"
PHASE9B_DOC = REPO_ROOT / "docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md"
PHASE9A_DOC = REPO_ROOT / "docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md"
PHASE8O_DOC = REPO_ROOT / "docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md"

INPUT_DIR = REPO_ROOT / "tmp/phase9f-test-input"
OUT_BASE = "tmp/phase9f-local-rbac-policy"

PROTECTED_HASHES = {
    REPO_ROOT / "scripts/dev/build_phase9d_actor_attribution_report.py": "46b20935f235fc48a60737ed167a3f612b95afacdd978c326f110b61bf9af473",
    REPO_ROOT / "scripts/dev/run_phase9d_actor_attribution_report.sh": "900513d415be02280437752e4aefb9af6fbff3ab55c684f2943c20e43dc2fc43",
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

VALID_POLICY = {
    "policy_version": "phase9f.local_rbac_policy.v1",
    "policy_status": "local_advisory_prototype",
    "policy_mode": "advisory_only",
    "approval_boundary_statement": "RBAC policy is not approval; approval remains Phase 7D selected-gate manual boundary",
    "permissions": [
        {
            "permission_id": "perm_operator_read",
            "effect": "allow",
            "roles": ["operator"],
            "resources": ["scoring_report"],
            "actions": ["read"],
            "required_identity_assurance": "unauthenticated",
            "obligations": ["require_audit_record"],
            "approval_boundary_statement": "RBAC eligibility is not approval",
        },
        {
            "permission_id": "perm_reviewer_gate_allow",
            "effect": "allow",
            "roles": ["reviewer"],
            "resources": ["phase7d_selected_gate"],
            "actions": ["approve_selected_gate"],
            "required_identity_assurance": "operator_declared",
            "obligations": ["require_phase7d_selected_gate"],
            "approval_boundary_statement": "RBAC eligibility is not approval",
        },
    ],
}
VALID_SUBJECT = {
    "subject_id": "subject_op_1",
    "subject_actor_id": "actor_operator_one",
    "subject_actor_type": "human_operator",
    "subject_identity_assurance": "operator_declared",
    "subject_identity_source": "environment_operator_label",
    "subject_role_labels": ["operator"],
}
VALID_REQUEST = {
    "request_id": "req1",
    "subject": VALID_SUBJECT,
    "resource": {"resource_type": "scoring_report", "resource_id": "res1"},
    "action": "read",
    "approval_boundary_statement": "RBAC advisory decision is not approval",
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
    return f"tmp/phase9f-test-input/{name}"


def _run(policy_rel, request_rel, registry_rel=None, attribution_rel=None, output_dir=None):
    out = output_dir or f"{OUT_BASE}/run"
    cmd = [sys.executable, str(RUNTIME), "--policy", policy_rel, "--request", request_rel, "--output-dir", out]
    if registry_rel is not None:
        cmd += ["--registry", registry_rel]
    if attribution_rel is not None:
        cmd += ["--attribution", attribution_rel]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    report_path = REPO_ROOT / out / "local-rbac-decision-report.json"
    report = json.loads(_text(report_path)) if report_path.is_file() else None
    return proc, report, REPO_ROOT / out


def _valid_policy_path(name="policy.json", policy=None) -> str:
    return _write_input(name, policy or VALID_POLICY)


def _valid_request_path(name="request.json", request=None) -> str:
    return _write_input(name, request or VALID_REQUEST)


# ---------------------------------------------------------------------------
# A. File existence and status
# ---------------------------------------------------------------------------


def test_phase9f_required_files_exist() -> None:
    for path in (RUNTIME, RUNNER, TASK_FILE, DOC, THIS_TEST):
        assert path.is_file(), f"missing Phase 9F file: {path}"


def test_phase9f_status_tokens() -> None:
    assert "phase9f_status: success" in _text(TASK_FILE)
    text = _text(DOC)
    for token in (
        "phase9f_status: success",
        "rbac_policy_status: local_advisory_prototype",
        "rbac_runtime_status: local_advisory_prototype",
        "rbac_enforcement_status: not_implemented",
        "actor_attribution_status: local_report_prototype",
        "actor_metadata_runtime_status: local_registry_prototype",
        "local_operator_registry_status: prototype_local_only",
        "identity_runtime_status: not_implemented",
        "authentication_runtime_status: not_implemented",
        "key_management_runtime_status: not_implemented",
        "phase9_branch_workflow: enabled",
    ):
        assert token in text, f"missing status token: {token}"


def test_phase9f_runner_is_executable_755() -> None:
    mode = stat.S_IMODE(RUNNER.stat().st_mode)
    assert mode == 0o755, f"runner mode is {oct(mode)}, expected 0o755"


# ---------------------------------------------------------------------------
# B. Scope safety
# ---------------------------------------------------------------------------


def test_phase9f_scope_safety_tokens() -> None:
    low = _flat(DOC)
    for token in (
        "local-only advisory rbac policy prototype",
        "no rbac enforcement",
        "no authentication runtime",
        "no login",
        "no session runtime",
        "no user store",
        "no backend/api/database",
        "no key management runtime",
        "no wrapper behavior change",
        "no primitive execution",
        "no vault read/write",
        "no phase 8 runtime behavior change",
        "no phase 9c/9d runtime behavior change",
    ):
        assert token in low, f"missing scope safety token: {token}"


# ---------------------------------------------------------------------------
# C. Runtime static safety
# ---------------------------------------------------------------------------


def test_phase9f_runtime_static_safety() -> None:
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
    assert "opa " not in low
    assert "rego" not in low
    assert "run_phase7d" not in low
    assert "execute_single_gate_approval" not in low
    assert "run_phase8" not in low
    assert "run_phase9c" not in low
    assert "run_phase9d" not in low
    assert "manage_phase9c" not in low
    assert "build_phase9d" not in low


def test_phase9f_runner_static_safety() -> None:
    src = _text(RUNNER)
    assert "--execute" not in src
    assert "APPROVE_PROMOTE=true" not in src
    assert "APPROVE_DECISION=true" not in src
    assert "APPROVE_FINALIZE=true" not in src
    assert "approve_all=true" not in src
    assert "run_phase7d" not in src
    assert "execute_single_gate_approval" not in src
    assert "run_phase8" not in src
    assert "run_phase9c" not in src
    assert "run_phase9d" not in src
    assert stat.S_IMODE(RUNNER.stat().st_mode) == 0o755


def test_phase9f_py_compile_and_bash_n() -> None:
    proc = subprocess.run([sys.executable, "-m", "py_compile", str(RUNTIME)],
                          cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    proc = subprocess.run(["bash", "-n", str(RUNNER)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


# ---------------------------------------------------------------------------
# D. Valid allow behavior
# ---------------------------------------------------------------------------


def test_phase9f_valid_allow() -> None:
    policy = _valid_policy_path("valid_policy.json")
    request = _valid_request_path("valid_request.json")
    proc, report, out_dir = _run(policy, request, output_dir=f"{OUT_BASE}/valid")
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "local-rbac-decision-report.json").is_file()
    assert (out_dir / "local-rbac-decision-report.md").is_file()
    assert report["advisory_decision"] == "allow"
    assert report["decision_reason"] == "policy_allow"
    assert "perm_operator_read" in report["matched_permission_ids"]
    assert report["reviewer_action"] == "no_action_required"
    assert "obligations" in report
    md = _text(out_dir / "local-rbac-decision-report.md").lower()
    assert "local rbac policy prototype is not enforcement" in md
    assert "rbac allow decision is not approval" in md
    assert "approval remains phase 7d selected-gate manual boundary" in md
    for f in out_dir.iterdir():
        assert f.parent == out_dir


# ---------------------------------------------------------------------------
# E. Explicit deny precedence
# ---------------------------------------------------------------------------


def test_phase9f_explicit_deny_precedence() -> None:
    policy = copy.deepcopy(VALID_POLICY)
    policy["permissions"].append({
        "permission_id": "perm_operator_deny",
        "effect": "deny",
        "roles": ["operator"],
        "resources": ["scoring_report"],
        "actions": ["read"],
        "required_identity_assurance": "unauthenticated",
        "obligations": [],
        "approval_boundary_statement": "RBAC eligibility is not approval",
    })
    policy_path = _valid_policy_path("deny_policy.json", policy)
    request = _valid_request_path("deny_request.json")
    proc, report, _ = _run(policy_path, request, output_dir=f"{OUT_BASE}/deny")
    assert proc.returncode == 0, proc.stderr
    assert report["advisory_decision"] == "deny"
    assert report["decision_reason"] == "explicit_deny"
    assert "perm_operator_deny" in report["denied_permission_ids"]


# ---------------------------------------------------------------------------
# F. No matching permission behavior
# ---------------------------------------------------------------------------


def test_phase9f_no_matching_permission() -> None:
    policy = _valid_policy_path("nomatch_policy.json")
    request_data = {
        **copy.deepcopy(VALID_REQUEST),
        "resource": {"resource_type": "audit_export_pack", "resource_id": "r2"},
        "action": "export",
    }
    request = _valid_request_path("nomatch_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/nomatch")
    assert proc.returncode == 0, proc.stderr
    assert report["advisory_decision"] == "deny"
    assert report["decision_reason"] == "no_matching_permission"
    assert report["reviewer_action"] in ("manual_review_required", "reject_action_until_resolved")


# ---------------------------------------------------------------------------
# G. Insufficient identity assurance
# ---------------------------------------------------------------------------


def test_phase9f_insufficient_identity_assurance() -> None:
    policy = _valid_policy_path("weak_policy.json")
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_id": "s3", "subject_identity_assurance": "unauthenticated", "subject_role_labels": ["reviewer"]}
    request_data = {
        **copy.deepcopy(VALID_REQUEST),
        "subject": subject,
        "resource": {"resource_type": "phase7d_selected_gate", "resource_id": "gate1"},
        "action": "approve_selected_gate",
    }
    request = _valid_request_path("weak_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/weak")
    assert proc.returncode == 0, proc.stderr
    assert report["advisory_decision"] == "conditional_allow"
    assert report["decision_reason"] == "insufficient_identity_assurance"
    assert report["reviewer_action"] == "manual_review_required"


# ---------------------------------------------------------------------------
# H. execute_primitive hard block
# ---------------------------------------------------------------------------


def test_phase9f_execute_primitive_blocked() -> None:
    policy = _valid_policy_path("prim_policy.json")
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_identity_assurance": "hardware_backed"}
    request_data = {**copy.deepcopy(VALID_REQUEST), "subject": subject, "action": "execute_primitive"}
    request = _valid_request_path("prim_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/prim")
    assert proc.returncode == 0, proc.stderr
    assert report["advisory_decision"] == "deny"
    assert report["decision_reason"] == "primitive_execution_blocked"
    assert report["reviewer_action"] == "reject_action_until_resolved"
    assert "require_no_primitive_execution" in report["obligations"]


# ---------------------------------------------------------------------------
# I. approve_selected_gate advisory-only behavior
# ---------------------------------------------------------------------------


def test_phase9f_approve_selected_gate_advisory_allow() -> None:
    policy = _valid_policy_path("gate_policy.json")
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_id": "s5", "subject_identity_assurance": "operator_declared", "subject_role_labels": ["reviewer"]}
    request_data = {
        **copy.deepcopy(VALID_REQUEST),
        "subject": subject,
        "resource": {"resource_type": "phase7d_selected_gate", "resource_id": "gate1"},
        "action": "approve_selected_gate",
    }
    request = _valid_request_path("gate_request.json", request_data)
    proc, report, out_dir = _run(policy, request, output_dir=f"{OUT_BASE}/gate")
    assert proc.returncode == 0, proc.stderr
    assert report["advisory_decision"] == "allow"
    assert "require_phase7d_selected_gate" in report["obligations"]
    md = _text(out_dir / "local-rbac-decision-report.md").lower()
    assert "rbac allow decision is not approval" in md
    assert "run_phase7d" not in md


# ---------------------------------------------------------------------------
# J. Optional registry context
# ---------------------------------------------------------------------------


def test_phase9f_optional_registry_context() -> None:
    registry_path = REPO_ROOT / "tmp/phase9c-local-operator-registry/operator-registry.json"
    if not registry_path.is_file():
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts/dev/manage_phase9c_local_operator_registry.py"),
             "--input", "tmp/phase9c-test-input/valid.json", "--mode", "build"],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
        )
    before = registry_path.read_bytes() if registry_path.is_file() else None
    policy = _valid_policy_path("ctx_policy.json")
    request = _valid_request_path("ctx_request.json")
    proc, report, out_dir = _run(policy, request, registry_rel="tmp/phase9c-local-operator-registry/operator-registry.json",
                                 output_dir=f"{OUT_BASE}/ctx")
    assert proc.returncode == 0, proc.stderr
    assert "registry_context" in report
    md = _text(out_dir / "local-rbac-decision-report.md").lower()
    assert "registry presence is not authentication" in md
    if before is not None:
        assert registry_path.read_bytes() == before


# ---------------------------------------------------------------------------
# K. Optional attribution context
# ---------------------------------------------------------------------------


def test_phase9f_optional_attribution_context() -> None:
    attribution = _write_input("attribution.json", {"attributed_records": [{"evidence_id": "ev1"}]})
    before = (REPO_ROOT / attribution).read_bytes()
    policy = _valid_policy_path("attr_policy.json")
    request = _valid_request_path("attr_request.json")
    proc, report, out_dir = _run(policy, request, attribution_rel=attribution, output_dir=f"{OUT_BASE}/attr")
    assert proc.returncode == 0, proc.stderr
    assert "attribution_context" in report
    md = _text(out_dir / "local-rbac-decision-report.md").lower()
    assert "actor attribution is not approval" in md
    assert (REPO_ROOT / attribution).read_bytes() == before


# ---------------------------------------------------------------------------
# L. Invalid policy / request behavior
# ---------------------------------------------------------------------------


def test_phase9f_missing_policy_nonzero() -> None:
    request = _valid_request_path("mp_request.json")
    proc, _, _ = _run("tmp/phase9f-test-input/no-policy.json", request, output_dir=f"{OUT_BASE}/mp")
    assert proc.returncode != 0


def test_phase9f_invalid_policy_json_nonzero() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "badpolicy.json").write_text("not json{", encoding="utf-8")
    request = _valid_request_path("ip_request.json")
    proc, report, _ = _run("tmp/phase9f-test-input/badpolicy.json", request, output_dir=f"{OUT_BASE}/ip")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_policy_json" for i in report["issues"])


def test_phase9f_policy_scalar_nonzero() -> None:
    policy = _write_input("scalar_policy.json", 7)
    request = _valid_request_path("sp_request.json")
    proc, _, _ = _run(policy, request, output_dir=f"{OUT_BASE}/sp")
    assert proc.returncode != 0


def test_phase9f_missing_request_nonzero() -> None:
    policy = _valid_policy_path("mr_policy.json")
    proc, _, _ = _run(policy, "tmp/phase9f-test-input/no-request.json", output_dir=f"{OUT_BASE}/mr")
    assert proc.returncode != 0


def test_phase9f_invalid_request_json_nonzero() -> None:
    policy = _valid_policy_path("ir_policy.json")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "badrequest.json").write_text("not json{", encoding="utf-8")
    proc, report, _ = _run(policy, "tmp/phase9f-test-input/badrequest.json", output_dir=f"{OUT_BASE}/ir")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "invalid_request_json" for i in report["issues"])


def test_phase9f_request_scalar_nonzero() -> None:
    policy = _valid_policy_path("sr_policy.json")
    request = _write_input("scalar_request.json", 9)
    proc, _, _ = _run(policy, request, output_dir=f"{OUT_BASE}/sr")
    assert proc.returncode != 0


def test_phase9f_missing_required_policy_field_nonzero() -> None:
    policy_data = copy.deepcopy(VALID_POLICY)
    del policy_data["permissions"]
    policy = _valid_policy_path("mrf_policy.json", policy_data)
    request = _valid_request_path("mrf_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/mrf")
    assert proc.returncode != 0


def test_phase9f_missing_required_request_field_nonzero() -> None:
    policy = _valid_policy_path("mrrf_policy.json")
    request_data = copy.deepcopy(VALID_REQUEST)
    del request_data["action"]
    request = _valid_request_path("mrrf_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/mrrf")
    assert proc.returncode != 0


# ---------------------------------------------------------------------------
# M. Policy validation behavior
# ---------------------------------------------------------------------------


def test_phase9f_wrong_policy_version_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "policy_version": "wrong.v0"}
    policy = _valid_policy_path("wv_policy.json", policy_data)
    request = _valid_request_path("wv_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/wv")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "policy_version_incompatible" for i in report["issues"])


def test_phase9f_wrong_policy_status_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "policy_status": "production"}
    policy = _valid_policy_path("ws_policy.json", policy_data)
    request = _valid_request_path("ws_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/ws")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "policy_mode_invalid" for i in report["issues"])


def test_phase9f_wrong_policy_mode_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "policy_mode": "enforce"}
    policy = _valid_policy_path("wm_policy.json", policy_data)
    request = _valid_request_path("wm_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/wm")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "policy_mode_invalid" for i in report["issues"])


def test_phase9f_enforcement_enabled_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "enforcement_enabled": True}
    policy = _valid_policy_path("enf_policy.json", policy_data)
    request = _valid_request_path("enf_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/enf")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "enforcement_enabled_present" for i in report["issues"])


def test_phase9f_permissions_not_list_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "permissions": "nope"}
    policy = _valid_policy_path("pnl_policy.json", policy_data)
    request = _valid_request_path("pnl_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/pnl")
    assert proc.returncode != 0


def test_phase9f_permission_missing_field_rejected() -> None:
    policy_data = copy.deepcopy(VALID_POLICY)
    del policy_data["permissions"][0]["resources"]
    policy = _valid_policy_path("pmf_policy.json", policy_data)
    request = _valid_request_path("pmf_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/pmf")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "permission_missing" for i in report["issues"])


def test_phase9f_unknown_effect_rejected() -> None:
    policy_data = copy.deepcopy(VALID_POLICY)
    policy_data["permissions"][0]["effect"] = "maybe"
    policy = _valid_policy_path("ue_policy.json", policy_data)
    request = _valid_request_path("ue_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/ue")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "permission_unknown" for i in report["issues"])


# ---------------------------------------------------------------------------
# N. Request validation behavior
# ---------------------------------------------------------------------------


def test_phase9f_subject_missing_rejected() -> None:
    request_data = copy.deepcopy(VALID_REQUEST)
    del request_data["subject"]
    policy = _valid_policy_path("sm_policy.json")
    request = _valid_request_path("sm_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/sm")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "subject_missing" for i in report["issues"])


def test_phase9f_resource_missing_rejected() -> None:
    request_data = copy.deepcopy(VALID_REQUEST)
    del request_data["resource"]
    policy = _valid_policy_path("rm_policy.json")
    request = _valid_request_path("rm_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/rm")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "resource_unknown" for i in report["issues"])


def test_phase9f_action_missing_rejected() -> None:
    request_data = copy.deepcopy(VALID_REQUEST)
    del request_data["action"]
    policy = _valid_policy_path("am_policy.json")
    request = _valid_request_path("am_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/am")
    assert proc.returncode != 0


def test_phase9f_unknown_resource_rejected() -> None:
    request_data = {**copy.deepcopy(VALID_REQUEST), "resource": {"resource_type": "spaceship", "resource_id": "r1"}}
    policy = _valid_policy_path("ur_policy.json")
    request = _valid_request_path("ur_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/ur")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "resource_unknown" for i in report["issues"])


def test_phase9f_unknown_action_rejected() -> None:
    request_data = {**copy.deepcopy(VALID_REQUEST), "action": "fly_to_moon"}
    policy = _valid_policy_path("ua_policy.json")
    request = _valid_request_path("ua_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/ua")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "action_unknown" for i in report["issues"])


def test_phase9f_unknown_identity_assurance_rejected() -> None:
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_identity_assurance": "telepathic"}
    request_data = {**copy.deepcopy(VALID_REQUEST), "subject": subject}
    policy = _valid_policy_path("uia_policy.json")
    request = _valid_request_path("uia_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/uia")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "subject_unknown" for i in report["issues"])


# ---------------------------------------------------------------------------
# O. Privacy / secret validation
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
def test_phase9f_secret_rejection(value) -> None:
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_display_label": value}
    request_data = {**copy.deepcopy(VALID_REQUEST), "subject": subject}
    policy = _valid_policy_path(f"sec_policy_{abs(hash(value))}.json")
    request = _valid_request_path(f"sec_request_{abs(hash(value))}.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/sec-{abs(hash(value))}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "privacy_review_required" for i in report["issues"])


def test_phase9f_raw_email_in_subject_actor_id_rejected() -> None:
    subject = {**copy.deepcopy(VALID_SUBJECT), "subject_actor_id": "actor_person@example.com"}
    request_data = {**copy.deepcopy(VALID_REQUEST), "subject": subject}
    policy = _valid_policy_path("email_policy.json")
    request = _valid_request_path("email_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/email")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "privacy_review_required" for i in report["issues"])


# ---------------------------------------------------------------------------
# P. Approval boundary validation
# ---------------------------------------------------------------------------


def test_phase9f_policy_approval_statement_missing_rejected() -> None:
    policy_data = copy.deepcopy(VALID_POLICY)
    del policy_data["approval_boundary_statement"]
    policy = _valid_policy_path("pabs_policy.json", policy_data)
    request = _valid_request_path("pabs_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/pabs")
    assert proc.returncode != 0


def test_phase9f_request_approval_statement_missing_rejected() -> None:
    request_data = copy.deepcopy(VALID_REQUEST)
    del request_data["approval_boundary_statement"]
    policy = _valid_policy_path("rabs_policy.json")
    request = _valid_request_path("rabs_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/rabs")
    assert proc.returncode != 0


def test_phase9f_approval_statement_wrong_phrase_rejected() -> None:
    policy_data = {**copy.deepcopy(VALID_POLICY), "approval_boundary_statement": "hello world"}
    policy = _valid_policy_path("wp_policy.json", policy_data)
    request = _valid_request_path("wp_request.json")
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/wp")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_boundary_required" for i in report["issues"])


@pytest.mark.parametrize("flag", [
    "approved", "is_approved", "approval_granted", "auto_approve", "approve_all",
    "next_gate", "execute",
])
def test_phase9f_approval_flag_rejected(flag) -> None:
    request_data = {**copy.deepcopy(VALID_REQUEST), flag: True}
    policy = _valid_policy_path(f"flag_policy_{flag}.json")
    request = _valid_request_path(f"flag_request_{flag}.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/flag-{flag}")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "approval_flag_present" for i in report["issues"])


def test_phase9f_primitive_execution_intent_rejected() -> None:
    request_data = {**copy.deepcopy(VALID_REQUEST), "primitive_execution_intent": True}
    policy = _valid_policy_path("pei_policy.json")
    request = _valid_request_path("pei_request.json", request_data)
    proc, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/pei")
    assert proc.returncode != 0
    assert any(i["issue_type"] == "primitive_execution_blocked" for i in report["issues"])


# ---------------------------------------------------------------------------
# Q. Report schema behavior
# ---------------------------------------------------------------------------


def test_phase9f_report_schema() -> None:
    policy = _valid_policy_path("schema_policy.json")
    request = _valid_request_path("schema_request.json")
    _, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/schema")
    for field in (
        "phase9f_status", "phase7d_runtime_readiness", "durable_audit_store_status",
        "identity_boundary_status", "actor_metadata_schema_status",
        "actor_metadata_runtime_status", "local_operator_registry_status",
        "actor_attribution_status", "rbac_design_status", "rbac_policy_status",
        "rbac_runtime_status", "rbac_enforcement_status", "identity_runtime_status",
        "authentication_runtime_status", "operator_identity_assurance_status",
        "signing_implementation_status", "signature_runtime_status",
        "signature_verifier_runtime_status", "key_management_runtime_status",
        "phase9_branch_workflow", "advisory_decision", "decision_reason",
        "matched_permission_ids", "denied_permission_ids", "obligations",
        "denial_reasons", "reviewer_action", "reviewer_action_required",
        "incident_classification", "severity_counts", "approval_boundary_statement",
        "safety_statement", "limitations", "issues", "request", "subject",
        "resource", "action",
    ):
        assert field in report, f"report missing field: {field}"
    assert set(report["severity_counts"]) == {"info", "warning", "critical"}

    bad_request = {**copy.deepcopy(VALID_REQUEST), "action": "bogus_action"}
    policy = _valid_policy_path("schema_bad_policy.json")
    request = _valid_request_path("schema_bad_request.json", bad_request)
    _, report, _ = _run(policy, request, output_dir=f"{OUT_BASE}/schema-bad")
    for issue in report["issues"]:
        for key in ("issue_type", "severity", "incident_classification", "reviewer_action",
                    "subject_id", "resource_id", "action", "permission_id", "message"):
            assert key in issue, f"issue missing key: {key}"


# ---------------------------------------------------------------------------
# R. Path safety
# ---------------------------------------------------------------------------


def test_phase9f_policy_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "policy.json"
    outside.write_text(json.dumps(VALID_POLICY), encoding="utf-8")
    request = _valid_request_path("out_request.json")
    proc, _, _ = _run(str(outside), request, output_dir=f"{OUT_BASE}/out-policy")
    assert proc.returncode != 0


def test_phase9f_request_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "request.json"
    outside.write_text(json.dumps(VALID_REQUEST), encoding="utf-8")
    policy = _valid_policy_path("out2_policy.json")
    proc, _, _ = _run(policy, str(outside), output_dir=f"{OUT_BASE}/out-request")
    assert proc.returncode != 0


def test_phase9f_registry_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "reg.json"
    outside.write_text(json.dumps({"actor_registry": []}), encoding="utf-8")
    policy = _valid_policy_path("out3_policy.json")
    request = _valid_request_path("out3_request.json")
    proc, _, _ = _run(policy, request, registry_rel=str(outside), output_dir=f"{OUT_BASE}/out-registry")
    assert proc.returncode != 0


def test_phase9f_attribution_outside_repo_rejected(tmp_path) -> None:
    outside = tmp_path / "attr.json"
    outside.write_text(json.dumps({"attributed_records": []}), encoding="utf-8")
    policy = _valid_policy_path("out4_policy.json")
    request = _valid_request_path("out4_request.json")
    proc, _, _ = _run(policy, request, attribution_rel=str(outside), output_dir=f"{OUT_BASE}/out-attr")
    assert proc.returncode != 0


@pytest.mark.parametrize("bad", ["docs/ROADMAP.md", "codex/tasks/072-phase9f-local-rbac-policy-prototype.md"])
def test_phase9f_forbidden_policy_root_rejected(bad) -> None:
    request = _valid_request_path("forb_request.json")
    proc, _, _ = _run(bad, request, output_dir=f"{OUT_BASE}/forb")
    assert proc.returncode != 0


def test_phase9f_symlink_policy_rejected() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = INPUT_DIR / "sym_target_policy.json"
    target.write_text(json.dumps(VALID_POLICY), encoding="utf-8")
    link = INPUT_DIR / "sym_policy.json"
    if link.exists() or link.is_symlink():
        link.unlink()
    os.symlink(target, link)
    request = _valid_request_path("sym_request.json")
    proc, _, _ = _run("tmp/phase9f-test-input/sym_policy.json", request, output_dir=f"{OUT_BASE}/sym")
    assert proc.returncode != 0


def test_phase9f_output_dir_escape_rejected() -> None:
    policy = _valid_policy_path("oe_policy.json")
    request = _valid_request_path("oe_request.json")
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--policy", policy, "--request", request,
         "--output-dir", "tmp/other-9f-dir"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


def test_phase9f_output_dir_traversal_rejected() -> None:
    policy = _valid_policy_path("ot_policy.json")
    request = _valid_request_path("ot_request.json")
    proc = subprocess.run(
        [sys.executable, str(RUNTIME), "--policy", policy, "--request", request,
         "--output-dir", "tmp/phase9f-local-rbac-policy/../.."],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode != 0


# ---------------------------------------------------------------------------
# S. Documentation regression
# ---------------------------------------------------------------------------


def test_phase9f_documentation_regressions() -> None:
    roadmap = _text(ROADMAP)
    project_state = _text(PROJECT_STATE)
    assert "Phase 9F" in roadmap
    assert "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md" in roadmap
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in roadmap, f"ROADMAP dropped token: {token}"

    assert "docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md" in project_state
    for token in ("Current architecture", "no database", "no FastAPI", "no UI",
                  "no external APIs", "no autopublish"):
        assert token in project_state, f"PROJECT_STATE dropped token: {token}"

    for doc in (PHASE9E_DOC, PHASE9D_DOC, PHASE9C_DOC, PHASE9B_DOC, PHASE9A_DOC, PHASE8O_DOC):
        assert "Phase 9F" in _text(doc), f"missing Phase 9F reference in {doc.name}"


# ---------------------------------------------------------------------------
# T. Protected runtime files unchanged
# ---------------------------------------------------------------------------


def test_phase9f_protected_runtime_files_unchanged() -> None:
    for path, digest in PROTECTED_HASHES.items():
        assert path.is_file(), f"missing protected runtime file: {path}"
        assert _sha256(path) == digest, f"protected runtime changed: {path}"


# ---------------------------------------------------------------------------
# U. Static safety for new Phase 9F files only
# ---------------------------------------------------------------------------


def test_phase9f_static_safety_new_files_only() -> None:
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
        "opa eval",
        ".rego",
    )
    for path in (RUNTIME, RUNNER, TASK_FILE, DOC):
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ---------------------------------------------------------------------------
# V. Repo-wide artifact safety
# ---------------------------------------------------------------------------


def test_phase9f_repo_wide_artifact_safety() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        suffix = path.suffix.lower()
        assert suffix not in (".pem", ".key", ".crt", ".p12", ".pfx"), f"unexpected key/cert file: {path}"
        assert suffix not in (".sql", ".sqlite", ".db"), f"unexpected database file: {path}"
        assert suffix != ".rego", f"unexpected policy (.rego) file: {path}"
    assert not (REPO_ROOT / "package.json").exists()
    dev = REPO_ROOT / "scripts/dev"
    for pattern in ("*.rego", "*opa*"):
        matches = sorted(p.name for p in dev.glob(pattern))
        assert matches == [], f"unexpected OPA/Rego runtime file ({pattern}): {matches}"
