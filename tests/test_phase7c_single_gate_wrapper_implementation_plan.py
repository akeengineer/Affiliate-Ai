from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/044-phase7c-single-gate-wrapper-implementation-plan.md"
PLAN = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md"
BOUNDARY = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RELEASE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"

NEW_FILES = (PLAN, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-3. existence / status / scope ───────────────────────────────────────────

def test_task_and_plan_exist() -> None:
    assert TASK_FILE.is_file()
    assert PLAN.is_file()


def test_task_final_status() -> None:
    assert "phase7c_status: success" in _text(TASK_FILE)


def test_plan_scope_is_docs_only() -> None:
    low = _text(PLAN).lower()
    assert "docs/tests/task-only" in low or "implementation plan only" in low


# ── 4-6. no runtime wrapper / 7C-only / 7D future ─────────────────────────────

def test_no_phase7d_wrapper_scripts() -> None:
    assert not (REPO_ROOT / "scripts/dev/run_phase7d_single_gate_wrapper.sh").exists()
    assert not (REPO_ROOT / "scripts/dev/run_manual_approval_wrapper.sh").exists()
    assert not (REPO_ROOT / "scripts/dev/execute_single_gate_approval.py").exists()


def test_plan_states_no_runtime_wrapper() -> None:
    assert "no runtime wrapper exists in phase 7c" in _text(PLAN).lower()


def test_plan_names_phase7d_future_high_risk() -> None:
    low = _text(PLAN).lower()
    assert "phase 7d" in low
    assert "high-risk" in low


# ── 7-9. objective / command shape / one gate ─────────────────────────────────

def test_plan_defines_objective() -> None:
    low = _text(PLAN).lower()
    assert "implementation objective" in low
    assert "execute at most one primitive" in low
    assert "write one audit artifact" in low


def test_plan_command_shape_proposed_only() -> None:
    text = _text(PLAN)
    assert "run_phase7d_single_gate_wrapper.sh" in text
    assert "proposed future name only" in text.lower()


def test_plan_exactly_one_gate() -> None:
    assert "accept exactly one" in _text(PLAN).lower()


# ── 10. allowed gates ─────────────────────────────────────────────────────────

def test_plan_allowed_gates() -> None:
    text = _text(PLAN)
    for gate in ("promote", "decision", "finalization"):
        assert gate in text, f"missing gate: {gate}"


# ── 11-20. precondition contract ──────────────────────────────────────────────

def test_plan_precondition_contract() -> None:
    assert "precondition contract" in _text(PLAN).lower()


def test_plan_requires_6b_dry_run() -> None:
    low = _text(PLAN).lower()
    assert "phase 6b packet exists" in low
    assert "phase 6b packet has `dry_run` true" in low


def test_plan_requires_6c_ready() -> None:
    assert "phase 6c verdict is `ready`" in _text(PLAN).lower()


def test_plan_requires_6e_plan_not_failed() -> None:
    low = _text(PLAN).lower()
    assert "phase 6e execution plan exists" in low
    assert "phase 6e plan has `dry_run` true" in low
    assert "phase 6e overall verdict is not `failed`" in low


def test_plan_requires_gate_in_per_gate_plan() -> None:
    assert "per_gate_plan" in _text(PLAN)


def test_plan_requires_plan_ready_not_blocked() -> None:
    low = _text(PLAN).lower()
    assert "plan_ready` is true" in low
    assert "blocked_reason` is empty or null" in low


def test_plan_documents_blocked_overall_nuance() -> None:
    low = _text(PLAN).lower()
    assert "overall verdict may be `blocked`" in low
    assert "readiness by the selected gate" in low


def test_plan_requires_id_week_match() -> None:
    low = _text(PLAN).lower()
    assert "`product_id` matches across operator input, phase 6b, phase 6c, and phase 6e" in low
    assert "`report_week` matches across operator input, phase 6b, phase 6c, and phase 6e" in low


def test_plan_requires_decision_promote_evidence() -> None:
    assert "decision requires promote completion evidence" in _text(PLAN).lower()


def test_plan_requires_finalization_compliance() -> None:
    low = _text(PLAN).lower()
    assert "finalization requires decision completion evidence" in low
    assert "finalization requires `compliance_status` to be `approved`" in low


# ── 21-22. gate-to-primitive mapping + allowlist ──────────────────────────────

def test_plan_gate_primitive_mapping() -> None:
    text = _text(PLAN)
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive: {prim}"


def test_plan_allowlist_no_dynamic_invocation() -> None:
    low = _text(PLAN).lower()
    assert "explicit allowlist mapping" in low
    assert "dynamic untrusted string" in low


# ── 23. approval flag policy ──────────────────────────────────────────────────

def test_plan_approval_flag_policy() -> None:
    text = _text(PLAN)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"
    low = text.lower()
    for token in (
        "exactly one matching",
        "unrelated approval flag",
        "multiple approval flags",
        "global approval",
        "approve-all",
    ):
        assert token in low, f"missing approval flag policy token: {token}"


# ── 24-25. audit artifact contract + 7B validatable ───────────────────────────

def test_plan_audit_artifact_fields() -> None:
    text = _text(PLAN)
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


def test_plan_audit_validatable_by_7b() -> None:
    assert "validatable by the phase 7b audit verifier" in _text(PLAN).lower()


# ── 26. failure / safety behavior ─────────────────────────────────────────────

def test_plan_failure_safety_behavior() -> None:
    low = _text(PLAN).lower()
    for token in (
        "fail closed before primitive execution",
        "execute no primitive on a failed precondition",
        "execute at most one primitive",
        "stop after a primitive failure",
        "never auto-run the next gate",
        "never retry silently",
        "never rollback automatically",
        "never infer approval",
    ):
        assert token in low, f"missing failure/safety token: {token}"


# ── 27. Phase 7B verifier integration ─────────────────────────────────────────

def test_plan_phase7b_integration() -> None:
    low = _text(PLAN).lower()
    assert "phase 7b verifier integration" in low
    assert "remains read-only" in low
    assert "does not trigger the next gate" in low


# ── 28. future Phase 7D test plan ─────────────────────────────────────────────

def test_plan_future_phase7d_tests() -> None:
    low = _text(PLAN).lower()
    assert "future phase 7d test plan" in low
    assert "executes the promote primitive only" in low
    assert "primitive failure -> failure audit and no next gate" in low


# ── 29-32. additive pointers ──────────────────────────────────────────────────

def test_roadmap_references_7c_and_7d() -> None:
    text = _text(ROADMAP)
    assert "Phase 7C" in text
    assert "Phase 7D" in text
    assert "SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md" in text


def test_project_state_points_to_plan() -> None:
    assert "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md" in _text(PROJECT_STATE)


def test_boundary_points_to_plan() -> None:
    assert "SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md" in _text(BOUNDARY)


def test_release_snapshot_points_to_7c() -> None:
    text = _text(RELEASE_SNAPSHOT)
    assert "Phase 7C" in text
    assert "SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md" in text


# ── 33-34. token regression ───────────────────────────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


# ── 35. no-execution guard (new files only) ───────────────────────────────────

def test_new_files_no_execution_forms() -> None:
    banned = [
        "APPROVE_PROMOTE=true",
        "APPROVE_DECISION=true",
        "APPROVE_FINALIZE=true",
        "bash scripts/dev/run_phase2g",
        "bash scripts/dev/run_phase2h",
        "bash scripts/dev/run_phase2i",
        "python scripts/dev/promote_product_candidates.py",
        "python scripts/dev/create_decision.py",
        "python scripts/dev/finalize_decision.py",
    ]
    for path in NEW_FILES:
        text = _text(path)
        for form in banned:
            assert form not in text, f"{path.name} contains execution form: {form}"


# ── 36. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
