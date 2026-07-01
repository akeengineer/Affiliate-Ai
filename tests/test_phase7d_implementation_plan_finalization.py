from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/046-phase7d-implementation-plan-finalization.md"
BLUEPRINT = REPO_ROOT / "docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
READINESS_REVIEW = REPO_ROOT / "docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md"
IMPLEMENTATION_PLAN = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md"
RELEASE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"

NEW_FILES = (TASK_FILE, BLUEPRINT)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_task_and_blueprint_exist() -> None:
    assert TASK_FILE.is_file()
    assert BLUEPRINT.is_file()


def test_task_final_status() -> None:
    assert "phase7d_plan_finalization_status: success" in _text(TASK_FILE)


def test_blueprint_status_model() -> None:
    text = _text(BLUEPRINT)
    assert "phase7d_plan_finalization_status: success" in text
    assert "phase7d_runtime_readiness: blocked" in text


def test_blueprint_scope_is_plan_only() -> None:
    low = _text(BLUEPRINT).lower()
    assert "docs/tests/task-only" in low or "implementation blueprint only" in low


def test_runtime_wrapper_scripts_now_exist_but_blueprint_remains_historical() -> None:
    assert (REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh").is_file()
    assert not (REPO_ROOT / "scripts/dev/run_manual_approval_wrapper.sh").exists()
    assert (REPO_ROOT / "scripts/dev/execute_single_gate_approval.py").is_file()


def test_future_runtime_files_are_proposed_only() -> None:
    text = _text(BLUEPRINT)
    for path in (
        "scripts/dev/run_phase7d_single_gate_wrapper.sh",
        "scripts/dev/execute_single_gate_approval.py",
        "tests/test_phase7d_single_gate_wrapper.py",
    ):
        assert path in text, f"missing proposed future file: {path}"
    assert "proposed only" in text.lower()
    assert "phase 7d-p does not create these files" in text.lower()


def test_future_cli_contract_is_proposed_only() -> None:
    text = _text(BLUEPRINT)
    assert (
        "bash scripts/dev/run_phase7d_single_gate_wrapper.sh "
        "<gate> <product_id> <report_week> --operator <operator> "
        "--reason <reason> --intent <intent>"
    ) in text
    assert "proposed-only" in text.lower()
    assert "phase 7d-p must not add this command" in text.lower()


def test_blueprint_is_single_gate_only() -> None:
    low = _text(BLUEPRINT).lower()
    assert "exactly one gate" in low
    assert "no approve-all" in low
    assert "no chain execution" in low


def test_future_shell_wrapper_behavior() -> None:
    low = _text(BLUEPRINT).lower()
    for token in (
        "strict shell mode",
        "resolve the repository root dynamically",
        "reject multiple gate values",
        "reject missing operator, reason, or intent",
        "choose a python interpreter",
        "not execute primitives directly in shell",
        "cross-cwd execution",
    ):
        assert token in low, f"missing shell behavior: {token}"


def test_future_python_core_design() -> None:
    low = _text(BLUEPRINT).lower()
    for token in (
        "parse gate, product_id, report_week, operator, reason, and intent",
        "validate the product_id pattern",
        "validate the report_week pattern",
        "load the phase 6b packet",
        "load the phase 6c verifier output",
        "load the phase 6e execution plan",
        "validate evidence path safety",
        "validate phase 6b `dry_run` is true",
        "validate phase 6c verdict is `ready`",
        "validate phase 6e `dry_run` is true",
        "reject phase 6e overall `failed`",
        "validate selected gate `plan_ready` is true",
        "validate selected gate `blocked_reason` is empty or null",
        "never run the next gate",
    ):
        assert token in low, f"missing Python core design token: {token}"


def test_ordered_validation_pipeline() -> None:
    text = _text(BLUEPRINT)
    stages = (
        "1. CLI argument validation",
        "2. Input path and evidence discovery",
        "3. Evidence safety validation",
        "4. Product/report consistency validation",
        "5. Phase 6B packet validation",
        "6. Phase 6C verifier validation",
        "7. Phase 6E execution plan validation",
        "8. Selected-gate readiness validation",
        "9. Approval flag validation",
        "10. Emergency stop / dry-run / operator confirmation validation",
        "11. Intent audit write",
        "12. Single primitive invocation",
        "13. Result audit write",
        "14. Phase 7B handoff note",
    )
    offsets = [text.index(stage) for stage in stages]
    assert offsets == sorted(offsets)
    low = text.lower()
    assert "no primitive execution occurs before all validations pass" in low
    assert "no vault write occurs before all validations pass" in low


def test_primitive_invocation_strategy() -> None:
    text = _text(BLUEPRINT)
    for primitive in (
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ):
        assert primitive in text, f"missing primitive reference: {primitive}"
    low = text.lower()
    for token in (
        "explicit dictionary/allowlist only",
        "no dynamic import from the gate string",
        "no shell eval",
        "no arbitrary subprocess target",
        "no untrusted string command construction",
        "at most one primitive",
        "primitive failure stops execution",
    ):
        assert token in low, f"missing invocation safety token: {token}"


def test_approval_flag_strategy() -> None:
    text = _text(BLUEPRINT)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag name: {flag}"
    low = text.lower()
    for token in (
        "exactly one matching approval flag",
        "reject an unrelated truthy flag",
        "reject multiple truthy flags",
        "reject global approval",
        "reject approve-all",
        "reject approval flag persistence",
    ):
        assert token in low, f"missing approval flag strategy: {token}"


def test_audit_strategy_and_required_fields() -> None:
    text = _text(BLUEPRINT)
    for outcome in ("`success`", "`failure`", "`blocked`", "`prevented`"):
        assert outcome in text, f"missing audit outcome: {outcome}"
    for field in (
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
    ):
        assert field in text, f"missing audit field: {field}"
    low = text.lower()
    assert "intent/pre-execution audit" in low
    assert "result/post-execution audit" in low
    assert "partial completion visible and manual review required" in low


def test_phase7b_handoff() -> None:
    low = _text(BLUEPRINT).lower()
    assert "wrapper prints the audit artifact path" in low
    assert "wrapper does not auto-run phase 7b by default" in low
    assert "phase 7b `valid` is not approval" in low
    assert "does not trigger the next gate" in low
    assert "phase 7b remains read-only" in low


def test_future_test_and_mocking_strategies() -> None:
    low = _text(BLUEPRINT).lower()
    for group in ("group a", "group b", "group c", "group d", "group e", "group f"):
        assert group in low, f"missing future test group: {group}"
    for token in (
        "tests must not call real mutation primitives",
        "primitive invocation should be isolated and observable",
        "exactly one primitive was selected",
        "unselected primitives were not called",
        "snapshot the vault before/after",
        "must run isolated, not concurrently",
    ):
        assert token in low, f"missing test strategy token: {token}"


def test_emergency_stop_and_dry_run_strategy() -> None:
    low = _text(BLUEPRINT).lower()
    assert "default mode must be dry-run/prevented" in low
    assert "emergency stop should override approval" in low
    assert "dry-run report should show what would execute without executing" in low
    assert "runtime readiness remains blocked until this strategy is explicitly accepted" in low


def test_future_merge_checklist() -> None:
    low = _text(BLUEPRINT).lower()
    assert "future merge checklist" in low
    for token in (
        "explicit allowlist only",
        "exactly one gate accepted",
        "audit write-order tested",
        "phase 7b compatibility tested",
        "no primitive on failed precondition",
        "no vault write on failed precondition",
        "full suite passes",
    ):
        assert token in low, f"missing merge checklist token: {token}"


def test_documentation_pointers() -> None:
    assert "Phase 7D-P" in _text(ROADMAP)
    assert "Phase 7D" in _text(ROADMAP)
    assert "docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md" in _text(PROJECT_STATE)
    assert "PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md" in _text(READINESS_REVIEW)
    assert "PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md" in _text(IMPLEMENTATION_PLAN)
    assert "Phase 7D-P" in _text(RELEASE_SNAPSHOT)


def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in (
        "Current architecture",
        "no database",
        "no FastAPI",
        "no UI",
        "no external APIs",
        "no autopublish",
    ):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_new_files_no_execution_forms() -> None:
    banned = (
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
    )
    for path in NEW_FILES:
        text = _text(path)
        for form in banned:
            assert form not in text, f"{path.name} contains execution form: {form}"


def test_new_files_static_safety() -> None:
    banned = (
        "http://",
        "https://",
        "/home/ubuntu/Affiliate-Ai",
        "AWS_SECRET_ACCESS_KEY",
        "BEGIN PRIVATE KEY",
        "OPENAI_API_KEY",
    )
    for path in NEW_FILES:
        text = _text(path)
        for token in banned:
            assert token not in text, f"{path.name} contains forbidden token: {token}"
