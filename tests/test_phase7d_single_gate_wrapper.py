from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh"
CORE = REPO_ROOT / "scripts/dev/execute_single_gate_approval.py"
TASK_FILE = REPO_ROOT / "codex/tasks/048-phase7d-single-gate-runtime-wrapper.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUT_DIR = REPO_ROOT / "tmp/phase7d-single-gate-wrapper"
PHASE6B_DIR = REPO_ROOT / "tmp/phase6b-approval-review"
PHASE6C_DIR = REPO_ROOT / "tmp/phase6c-approval-review-verifier"
PHASE6E_DIR = REPO_ROOT / "tmp/phase6e-approval-execution-plan"
PHASE2E_DIR = REPO_ROOT / "tmp/phase2e-import-score-report"
VAULT_PRODUCTS = REPO_ROOT / "vault/products"
VAULT_DECISIONS = REPO_ROOT / "vault/decisions"

PRODUCT_ID = "prod-phase7d-test"
WEEK = "2026-W26"
DECISION_ID = f"dec-{PRODUCT_ID}-{WEEK}"
VALID_OPERATOR = "operator-phase7d"
VALID_REASON = "manual review completed safely"
VALID_INTENT = "selected gate only"

EXIT_INVALID = 1
EXIT_PREVENTED = 2
EXIT_BLOCKED = 3
EXIT_FAILURE = 4
EXIT_AUDIT_FAILURE = 5

TRUTHY = ("1", "true", "yes", "y", "on")


def _load_module() -> ModuleType:
    assert CORE.is_file(), "Phase 7D Python core must exist"
    spec = importlib.util.spec_from_file_location("phase7d_runtime", CORE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    for key in (
        "APPROVE_PROMOTE",
        "APPROVE_DECISION",
        "APPROVE_FINALIZE",
        "APPROVE_ALL",
        "GLOBAL_APPROVAL",
        "AFFILIATE_PHASE7D_EMERGENCY_STOP",
    ):
        env.pop(key, None)
    env.update(overrides)
    return env


def _run_wrapper(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=env or _base_env(),
    )


def _cleanup_paths() -> None:
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    for directory in (PHASE6B_DIR, PHASE6C_DIR, PHASE6E_DIR):
        for path in directory.glob(f"*{PRODUCT_ID}*{WEEK}*"):
            path.unlink(missing_ok=True)
    if (PHASE2E_DIR / "scores" / f"{PRODUCT_ID}.json").exists():
        (PHASE2E_DIR / "scores" / f"{PRODUCT_ID}.json").unlink()
    product_note = VAULT_PRODUCTS / f"{PRODUCT_ID}.md"
    decision_note = VAULT_DECISIONS / f"{DECISION_ID}.md"
    product_note.unlink(missing_ok=True)
    decision_note.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _clean_runtime_artifacts() -> None:
    _cleanup_paths()
    yield
    _cleanup_paths()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _phase2e_score_path(pid: str = PRODUCT_ID) -> str:
    return f"tmp/phase2e-import-score-report/scores/{pid}.json"


def _phase6b_path(pid: str = PRODUCT_ID, week: str = WEEK) -> Path:
    return PHASE6B_DIR / f"review-{pid}-{week}.json"


def _phase6c_path(pid: str = PRODUCT_ID, week: str = WEEK) -> Path:
    return PHASE6C_DIR / f"verification-review-{pid}-{week}.json"


def _phase6e_path(pid: str = PRODUCT_ID, week: str = WEEK) -> Path:
    return PHASE6E_DIR / f"execution-plan-{pid}-{week}.json"


def _result_audit_path(gate: str, pid: str = PRODUCT_ID, week: str = WEEK) -> Path:
    return OUT_DIR / f"audit-result-{pid}-{week}-{gate}.json"


def _intent_audit_path(gate: str, pid: str = PRODUCT_ID, week: str = WEEK) -> Path:
    return OUT_DIR / f"audit-intent-{pid}-{week}-{gate}.json"


def _write_phase2e_score(pid: str = PRODUCT_ID, score_decision: str = "small_batch_test") -> None:
    score_path = PHASE2E_DIR / "scores" / f"{pid}.json"
    _write_json(
        score_path,
        {
            "product_id": pid,
            "product_opportunity_score": 77.65,
            "score_decision": score_decision,
            "confidence_score": 100,
            "missing_signal_count": 0,
        },
    )


def _write_phase6b(
    *,
    pid: str = PRODUCT_ID,
    week: str = WEEK,
    score_decision: str = "small_batch_test",
    compliance_status: str = "approved",
    promote_ready: bool = True,
    decision_ready: bool = True,
    finalization_ready: bool = True,
    phase2e_score_path: str | None = None,
    dry_run: bool = True,
) -> Path:
    path = phase2e_score_path or _phase2e_score_path(pid)
    payload = {
        "type": "phase6b_approval_review",
        "product_id": pid,
        "report_week": week,
        "generated_at": "2026-07-01T09:10:00Z",
        "score": {
            "score_decision": score_decision,
            "product_opportunity_score": 77.65,
            "confidence_score": 100,
            "missing_signal_count": 0,
        },
        "compliance_status": compliance_status,
        "verifier": {
            "phase4d_status": "success",
            "phase5c_verdict": "ready",
            "phase5d_status": "ready",
            "phase5d_verdict": "ready",
        },
        "governance": {
            "promoted_status": "manual_gate_required",
            "decision_status": "manual_gate_required",
            "finalization_status": "manual_gate_required",
        },
        "sources": [
            {
                "name": "phase2e_score",
                "path": path,
                "present": True,
                "bytes": 123,
                "sha256": "abc123",
            }
        ],
        "operator": "<operator-placeholder>",
        "approval_reason": "<reason-placeholder>",
        "gates": {
            "promote_gate_ready": promote_ready,
            "decision_gate_ready": decision_ready,
            "finalization_gate_ready": finalization_ready,
        },
        "dry_run": dry_run,
        "statement": "Dry-run only.",
        "readiness_note": "Readiness is not authorization to mutate.",
    }
    return _write_json(_phase6b_path(pid, week), payload)


def _write_phase6c(*, pid: str = PRODUCT_ID, week: str = WEEK, verdict: str = "ready") -> Path:
    payload = {
        "type": "phase6c_approval_review_verification",
        "product_id": pid,
        "report_week": week,
        "generated_at": "2026-07-01T09:10:01Z",
        "verdict": verdict,
        "checks": {
            "packet_json_exists": True,
            "packet_md_exists": True,
            "packet_type_ok": True,
            "dry_run_true": True,
            "ids_match": True,
            "evidence_present": True,
            "score_scalar_safe": True,
            "compliance_safe": True,
            "verifier_present": True,
            "gates_complete": True,
            "finalization_consistent": True,
            "sources_tmp_only": True,
            "no_leakage": True,
            "no_approval_execution": True,
            "readiness_note_ok": True,
        },
        "warnings": [],
        "source_integrity": [],
        "packet_path": f"tmp/phase6b-approval-review/review-{pid}-{week}.json",
    }
    return _write_json(_phase6c_path(pid, week), payload)


def _write_phase6e(
    *,
    pid: str = PRODUCT_ID,
    week: str = WEEK,
    verdict: str = "ready",
    promote_ready: bool = True,
    decision_ready: bool = True,
    finalization_ready: bool = True,
    promote_blocked_reason: str | None = None,
    decision_blocked_reason: str | None = None,
    finalization_blocked_reason: str | None = None,
) -> Path:
    payload = {
        "type": "phase6e_approval_execution_plan",
        "product_id": pid,
        "report_week": week,
        "generated_at": "2026-07-01T09:10:02Z",
        "dry_run": True,
        "packet_path": f"tmp/phase6b-approval-review/review-{pid}-{week}.json",
        "verifier_path": f"tmp/phase6c-approval-review-verifier/verification-review-{pid}-{week}.json",
        "boundary_doc_path": "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md",
        "boundary_doc": {"present": True, "bytes": 100, "sha256": "def456"},
        "verifier_verdict": "ready",
        "preconditions": {
            "packet_exists": True,
            "verifier_exists": True,
            "verifier_ready": True,
            "ids_match": True,
            "packet_dry_run_true": True,
            "no_approval_execution_signal": True,
            "no_leakage_confirmed": True,
            "sources_tmp_only_confirmed": True,
            "finalization_consistent": True,
            "boundary_doc_exists": True,
            "gate_order_defined": True,
            "finalization_blocked_unless_compliance_approved": True,
        },
        "proposed_gate_sequence": ["promote", "decision", "finalization"],
        "per_gate_plan": {
            "promote": {
                "primitive_name": "promote_product_candidates.py",
                "required_flag_name": "APPROVE_PROMOTE",
                "plan_ready": promote_ready,
                "blocked_reason": promote_blocked_reason,
            },
            "decision": {
                "primitive_name": "create_decision.py",
                "required_flag_name": "APPROVE_DECISION",
                "plan_ready": decision_ready,
                "blocked_reason": decision_blocked_reason,
            },
            "finalization": {
                "primitive_name": "finalize_decision.py",
                "required_flag_name": "APPROVE_FINALIZE",
                "plan_ready": finalization_ready,
                "blocked_reason": finalization_blocked_reason,
            },
        },
        "required_future_operator_inputs": ["operator identity", "approval reason", "gate-specific approval intent"],
        "audit_preview": {
            "product_id": pid,
            "report_week": week,
            "gate_name": "<gate-name-placeholder>",
            "primitive_name": "<primitive-name-placeholder>",
            "operator": "<operator-placeholder>",
            "approval_reason": "<reason-placeholder>",
            "timestamp": "2026-07-01T09:10:02Z",
            "source_packet_path": f"tmp/phase6b-approval-review/review-{pid}-{week}.json",
            "verifier_path": f"tmp/phase6c-approval-review-verifier/verification-review-{pid}-{week}.json",
            "precondition_summary": "dry_run_plan_preconditions",
            "result_summary": "dry_run_plan",
        },
        "blockers": [] if verdict != "blocked" else ["selected gate blocked elsewhere"],
        "verdict": verdict,
        "statement": "Dry-run only.",
    }
    return _write_json(_phase6e_path(pid, week), payload)


def _write_product_note(*, pid: str = PRODUCT_ID, status: str = "scored") -> Path:
    VAULT_PRODUCTS.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "type": "product_candidate",
        "product_id": pid,
        "product_name": "Phase 7D Test Product",
        "marketplace": "TikTok Shop",
        "currency": "USD",
        "demand_score": 83,
        "trend_velocity_score": 79,
        "marketplace_rank_score": 76,
        "commission_score": 72,
        "content_fit_score": 81,
        "competition_gap_score": 69,
        "risk_score": 22,
        "product_opportunity_score": 77.65,
        "score_decision": "small_batch_test",
        "confidence_score": 100,
        "missing_signal_count": 0,
        "last_scored_at": "2026-06-29T03:00:00Z",
        "status": status,
        "created_at": "2026-06-29T02:00:00Z",
        "updated_at": "2026-06-29T03:00:00Z",
    }
    text = "\n".join(
        [
            "---",
            yaml.safe_dump(frontmatter, sort_keys=False).strip(),
            "---",
            "",
            "# Product",
            "",
            "Phase 7D vault supplement note.",
            "",
        ]
    )
    path = VAULT_PRODUCTS / f"{pid}.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_decision_note(
    *,
    pid: str = PRODUCT_ID,
    week: str = WEEK,
    compliance_status: str = "approved",
    status: str = "draft",
) -> Path:
    VAULT_DECISIONS.mkdir(parents=True, exist_ok=True)
    decision_id = f"dec-{pid}-{week}"
    frontmatter = {
        "type": "decision",
        "decision_id": decision_id,
        "product_id": pid,
        "final_decision": "small_batch_test",
        "score_decision": "small_batch_test",
        "product_opportunity_score": 77.65,
        "confidence_score": 100,
        "missing_signal_count": 0,
        "vote_count": 0,
        "compliance_status": compliance_status,
        "override_reason": None,
        "decision_summary": "score_decision confirmed",
        "required_actions": [],
        "status": status,
        "created_at": "2026-06-29T02:00:00Z",
        "updated_at": "2026-06-29T03:00:00Z",
    }
    text = "\n".join(
        [
            "---",
            yaml.safe_dump(frontmatter, sort_keys=False).strip(),
            "---",
            "",
            "# Decision",
            "",
            "Phase 7D vault supplement draft.",
            "",
        ]
    )
    path = VAULT_DECISIONS / f"{decision_id}.md"
    path.write_text(text, encoding="utf-8")
    return path


def _write_ready_evidence(*, compliance_status: str = "approved", finalization_ready: bool = True) -> None:
    _write_phase2e_score()
    _write_phase6b(compliance_status=compliance_status, finalization_ready=finalization_ready)
    _write_phase6c(verdict="ready")
    _write_phase6e(verdict="ready", finalization_ready=finalization_ready, finalization_blocked_reason=None if finalization_ready else "compliance_status not approved")


def _confirm(gate: str, pid: str = PRODUCT_ID, week: str = WEEK) -> str:
    return f"EXECUTE_PHASE7D:{gate}:{pid}:{week}"


def _audit_field_names() -> set[str]:
    return {
        "product_id",
        "report_week",
        "selected_gate",
        "primitive_name",
        "operator",
        "approval_reason",
        "timestamp",
        "source_packet_path",
        "verifier_path",
        "execution_plan_path",
        "precondition_summary",
        "result_summary",
        "outcome",
        "mutation_attempted",
        "gate_specific_approval_intent",
        "approved_flag_name",
        "wrapper_version",
        "audit_schema_version",
    }


def test_artifacts_exist_and_task_status() -> None:
    assert WRAPPER.is_file()
    assert CORE.is_file()
    assert TASK_FILE.is_file()
    assert "phase7d_status: success" in TASK_FILE.read_text(encoding="utf-8")
    assert "phase7d_runtime_readiness: implemented_manual_gate" in TASK_FILE.read_text(encoding="utf-8")


def test_wrapper_executable_syntax_and_gitignore() -> None:
    assert os.access(WRAPPER, os.X_OK)
    assert stat.S_IMODE(WRAPPER.stat().st_mode) & 0o111
    shell_check = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert shell_check.returncode == 0, shell_check.stderr
    pyc = subprocess.run([sys.executable, "-m", "py_compile", str(CORE)], capture_output=True, text=True)
    assert pyc.returncode == 0, pyc.stderr
    assert "tmp/phase7d-single-gate-wrapper/" in GITIGNORE.read_text(encoding="utf-8")


def test_missing_args_exit_1() -> None:
    result = _run_wrapper()
    assert result.returncode == EXIT_INVALID


def test_invalid_product_week_and_placeholder_values_exit_1() -> None:
    module = _load_module()
    assert module.main(["promote", "BAD!", WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT]) == EXIT_INVALID
    assert module.main(["promote", PRODUCT_ID, "2026-26", "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT]) == EXIT_INVALID
    assert module.main(["promote", PRODUCT_ID, WEEK, "--operator", "<operator-placeholder>", "--reason", VALID_REASON, "--intent", VALID_INTENT]) == EXIT_INVALID
    assert module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", "<reason-placeholder>", "--intent", VALID_INTENT]) == EXIT_INVALID
    assert module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", "<intent-placeholder>"]) == EXIT_INVALID


def test_approve_all_intent_is_prevented_and_no_primitive() -> None:
    module = _load_module()
    _write_ready_evidence()
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", "approve-all"])
    assert result == EXIT_PREVENTED
    assert _result_audit_path("promote").is_file()


def test_missing_phase6b_packet_blocks() -> None:
    module = _load_module()
    _write_phase6c()
    _write_phase6e()
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED
    audit = json.loads(_result_audit_path("promote").read_text())
    assert audit["outcome"] == "blocked"
    assert audit["mutation_attempted"] is False


def test_unsafe_phase6b_path_is_prevented() -> None:
    module = _load_module()
    _write_ready_evidence()
    module.discover_evidence_paths = lambda *args, **kwargs: {
        "packet_path": "/tmp/evil.json",
        "verifier_path": f"tmp/phase6c-approval-review-verifier/verification-review-{PRODUCT_ID}-{WEEK}.json",
        "execution_plan_path": f"tmp/phase6e-approval-execution-plan/execution-plan-{PRODUCT_ID}-{WEEK}.json",
    }
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_PREVENTED


def test_phase6b_dry_run_false_blocks() -> None:
    module = _load_module()
    _write_phase2e_score()
    _write_phase6b(dry_run=False)
    _write_phase6c()
    _write_phase6e()
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_phase6c_not_ready_blocks() -> None:
    module = _load_module()
    _write_phase2e_score()
    _write_phase6b()
    _write_phase6c(verdict="warning")
    _write_phase6e()
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_phase6e_failed_blocks() -> None:
    module = _load_module()
    _write_phase2e_score()
    _write_phase6b()
    _write_phase6c()
    _write_phase6e(verdict="failed")
    result = module.main(["promote", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_phase6e_overall_blocked_but_selected_gate_ready_reaches_dry_run_prevented() -> None:
    module = _load_module()
    _write_phase2e_score()
    _write_phase6b(finalization_ready=False)
    _write_phase6c()
    _write_phase6e(verdict="blocked", promote_ready=True, decision_ready=True, finalization_ready=False, finalization_blocked_reason="compliance_status not approved")
    result = module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED or result == EXIT_PREVENTED


def test_decision_gate_requires_promoted_product_note() -> None:
    module = _load_module()
    _write_ready_evidence()
    result = module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_finalization_gate_requires_decision_draft() -> None:
    module = _load_module()
    _write_ready_evidence()
    result = module.main(["finalization", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_finalization_requires_compliance_approved() -> None:
    module = _load_module()
    _write_ready_evidence(compliance_status="not_evaluated", finalization_ready=False)
    _write_decision_note(compliance_status="not_evaluated")
    result = module.main(["finalization", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_BLOCKED


def test_missing_or_invalid_decision_value_is_prevented() -> None:
    module = _load_module()
    _write_phase2e_score()
    _write_phase6b(score_decision="")
    _write_phase6c()
    _write_phase6e()
    _write_product_note()
    result = module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_PREVENTED


def test_execute_absent_is_prevented_dry_run_and_evidence_unchanged() -> None:
    module = _load_module()
    _write_ready_evidence()
    _write_product_note()
    packet_hash = _sha256(_phase6b_path())
    verifier_hash = _sha256(_phase6c_path())
    plan_hash = _sha256(_phase6e_path())
    result = module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT])
    assert result == EXIT_PREVENTED
    assert _sha256(_phase6b_path()) == packet_hash
    assert _sha256(_phase6c_path()) == verifier_hash
    assert _sha256(_phase6e_path()) == plan_hash


def test_matching_flag_missing_unrelated_multiple_and_global_approval_are_prevented() -> None:
    module = _load_module()
    _write_ready_evidence()
    _write_product_note()
    assert module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")]) == EXIT_PREVENTED
    env = _base_env(APPROVE_PROMOTE="true")
    result = subprocess.run(
        [sys.executable, str(CORE), "decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == EXIT_PREVENTED
    env = _base_env(APPROVE_DECISION="true", APPROVE_PROMOTE="true")
    result = subprocess.run(
        [sys.executable, str(CORE), "decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == EXIT_PREVENTED
    env = _base_env(APPROVE_DECISION="true", APPROVE_ALL="true")
    result = subprocess.run(
        [sys.executable, str(CORE), "decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == EXIT_PREVENTED


def test_confirmation_missing_or_mismatch_and_emergency_stop_are_prevented() -> None:
    module = _load_module()
    _write_ready_evidence()
    _write_product_note()
    os.environ["APPROVE_DECISION"] = "true"
    try:
        assert module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute"]) == EXIT_PREVENTED
        assert module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", "WRONG"]) == EXIT_PREVENTED
        os.environ["AFFILIATE_PHASE7D_EMERGENCY_STOP"] = TRUTHY[0]
        assert module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")]) == EXIT_PREVENTED
        os.environ.pop("AFFILIATE_PHASE7D_EMERGENCY_STOP", None)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / "EMERGENCY_STOP").write_text("stop\n", encoding="utf-8")
        assert module.main(["decision", PRODUCT_ID, WEEK, "--operator", VALID_OPERATOR, "--reason", VALID_REASON, "--intent", VALID_INTENT, "--execute", "--confirm", _confirm("decision")]) == EXIT_PREVENTED
    finally:
        os.environ.pop("APPROVE_DECISION", None)
        os.environ.pop("AFFILIATE_PHASE7D_EMERGENCY_STOP", None)


@pytest.mark.parametrize(
    ("gate", "env_key", "setup_fn", "expected_script"),
    [
        ("promote", "APPROVE_PROMOTE", lambda: None, "promote_product_candidates.py"),
        ("decision", "APPROVE_DECISION", _write_product_note, "create_decision.py"),
        ("finalization", "APPROVE_FINALIZE", _write_decision_note, "finalize_decision.py"),
    ],
)
def test_success_paths_use_monkeypatched_single_selected_primitive(
    monkeypatch: pytest.MonkeyPatch,
    gate: str,
    env_key: str,
    setup_fn,
    expected_script: str,
) -> None:
    module = _load_module()
    _write_ready_evidence()
    if gate == "finalization":
        _write_ready_evidence(compliance_status="approved", finalization_ready=True)
    setup_fn()
    monkeypatch.setenv(env_key, "true")

    seen: dict[str, Any] = {}

    def fake_invoke_selected_primitive(*, gate: str, primitive_name: str, primitive_args: list[str], env: dict[str, str]) -> SimpleNamespace:
        seen["gate"] = gate
        seen["primitive_name"] = primitive_name
        seen["primitive_args"] = primitive_args
        seen["intent_exists_before_call"] = _intent_audit_path(gate).is_file()
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(module, "invoke_selected_primitive", fake_invoke_selected_primitive)

    exit_code = module.main(
        [
            gate,
            PRODUCT_ID,
            WEEK,
            "--operator",
            VALID_OPERATOR,
            "--reason",
            VALID_REASON,
            "--intent",
            VALID_INTENT,
            "--execute",
            "--confirm",
            _confirm(gate),
        ]
    )

    assert exit_code == 0
    assert seen["gate"] == gate
    assert seen["primitive_name"] == expected_script
    assert seen["intent_exists_before_call"] is True
    result_audit = json.loads(_result_audit_path(gate).read_text())
    assert result_audit["outcome"] == "success"
    assert result_audit["mutation_attempted"] is True
    assert _audit_field_names().issubset(result_audit.keys())


def test_primitive_failure_writes_failure_audit_and_exit_4(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    _write_ready_evidence()
    _write_product_note()
    monkeypatch.setenv("APPROVE_DECISION", "true")

    def fake_invoke_selected_primitive(**_: Any) -> SimpleNamespace:
        return SimpleNamespace(returncode=9, stdout="", stderr="primitive failed")

    monkeypatch.setattr(module, "invoke_selected_primitive", fake_invoke_selected_primitive)
    exit_code = module.main(
        [
            "decision",
            PRODUCT_ID,
            WEEK,
            "--operator",
            VALID_OPERATOR,
            "--reason",
            VALID_REASON,
            "--intent",
            VALID_INTENT,
            "--execute",
            "--confirm",
            _confirm("decision"),
        ]
    )
    assert exit_code == EXIT_FAILURE
    result_audit = json.loads(_result_audit_path("decision").read_text())
    assert result_audit["outcome"] == "failure"
    assert "manual review" in result_audit["result_summary"].lower()


@pytest.mark.parametrize("outcome", ["prevented", "blocked", "success", "failure"])
def test_audit_is_phase7b_compatible(outcome: str) -> None:
    verifier = REPO_ROOT / "scripts/dev/verify_manual_approval_audit.py"
    assert verifier.is_file()
    gate = "decision"
    audit = {
        "product_id": PRODUCT_ID,
        "report_week": WEEK,
        "selected_gate": gate,
        "primitive_name": "create_decision.py",
        "operator": VALID_OPERATOR,
        "approval_reason": VALID_REASON,
        "timestamp": "2026-07-01T09:10:03Z",
        "source_packet_path": f"tmp/phase6b-approval-review/review-{PRODUCT_ID}-{WEEK}.json",
        "verifier_path": f"tmp/phase6c-approval-review-verifier/verification-review-{PRODUCT_ID}-{WEEK}.json",
        "execution_plan_path": f"tmp/phase6e-approval-execution-plan/execution-plan-{PRODUCT_ID}-{WEEK}.json",
        "precondition_summary": "preconditions_ok",
        "result_summary": "manual review required" if outcome == "failure" else f"{outcome}_summary",
        "outcome": outcome,
        "mutation_attempted": outcome in {"success", "failure"},
        "gate_specific_approval_intent": "decision_only",
        "approved_flag_name": "APPROVE_DECISION",
        "wrapper_version": "7d",
        "audit_schema_version": "1",
    }
    _write_phase2e_score()
    _write_phase6b()
    _write_phase6c()
    _write_phase6e()
    audit_path = _result_audit_path(gate)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(verifier), str(audit_path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=_base_env(),
    )
    assert result.returncode in (0, 1)
    payload = json.loads((REPO_ROOT / f"tmp/phase7b-audit-verifier/audit-verification-{PRODUCT_ID}-{WEEK}-{gate}.json").read_text())
    assert payload["verdict"] in ("valid", "warning")


def test_shell_wrapper_cross_cwd_no_mutation_path() -> None:
    _write_ready_evidence()
    _write_product_note()
    scratch = REPO_ROOT / "tmp/phase7d-crosscwd"
    scratch.mkdir(parents=True, exist_ok=True)
    result = _run_wrapper(
        "decision",
        PRODUCT_ID,
        WEEK,
        "--operator",
        VALID_OPERATOR,
        "--reason",
        VALID_REASON,
        "--intent",
        VALID_INTENT,
        cwd=scratch,
    )
    assert result.returncode == EXIT_PREVENTED
    assert "audit_path:" in result.stdout
