from __future__ import annotations

import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/039-phase6f-single-gate-manual-approval-wrapper-boundary.md"
BOUNDARY = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md"
EXEC_BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"

NEW_FILES = (BOUNDARY, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-4. existence / scope / no runtime script ────────────────────────────────

def test_task_and_boundary_exist() -> None:
    assert TASK_FILE.is_file()
    assert BOUNDARY.is_file()


def test_task_final_status() -> None:
    assert "phase6f_status: success" in _text(TASK_FILE)


def test_boundary_scope_is_docs_only() -> None:
    low = _text(BOUNDARY).lower()
    assert "boundary-only" in low or "docs/tests/task-only" in low


def test_no_phase6f_runtime_script() -> None:
    assert glob.glob(str(REPO_ROOT / "scripts/dev/*phase6f*")) == []


# ── 5-8. preconditions ────────────────────────────────────────────────────────

def test_boundary_references_6b_6c_6e() -> None:
    text = _text(BOUNDARY)
    assert "Phase 6B" in text and "Phase 6C" in text and "Phase 6E" in text


def test_boundary_requires_6c_ready() -> None:
    assert "Phase 6C verdict is `ready`" in _text(BOUNDARY)


def test_boundary_requires_6e_not_failed() -> None:
    low = _text(BOUNDARY).lower()
    assert "not `failed`" in low or "not failed" in low


def test_boundary_requires_execution_plan() -> None:
    assert "execution plan exists" in _text(BOUNDARY).lower()


# ── 9-15. single-gate policy ──────────────────────────────────────────────────

def test_boundary_single_gate_only() -> None:
    low = _text(BOUNDARY).lower()
    assert "exactly one selected gate per" in low or "single gate per" in low


def test_boundary_gate_names() -> None:
    text = _text(BOUNDARY)
    for gate in ("`promote`", "`decision`", "`finalization`"):
        assert gate in text, f"missing gate name: {gate}"


def test_boundary_rejects_global_and_multigate() -> None:
    low = _text(BOUNDARY).lower()
    assert "no chain execution" in low
    assert "no approve-all" in low
    assert "no automatic next-gate execution" in low
    assert "multi-gate execution" in low
    assert "global approve" in low


def test_boundary_no_ui_direct() -> None:
    assert "no direct execution from the ui shell" in _text(BOUNDARY).lower()


def test_boundary_no_skip_order() -> None:
    assert "no skipping the required order" in _text(BOUNDARY).lower()


def test_boundary_decision_requires_promote() -> None:
    assert "decision requires promote completion evidence" in _text(BOUNDARY).lower()


def test_boundary_finalization_requires_decision_and_compliance() -> None:
    low = _text(BOUNDARY).lower()
    assert "finalization requires decision completion evidence" in low
    assert "compliance_status" in low and "approved" in low


# ── 16-19. primitives + flags ─────────────────────────────────────────────────

def test_boundary_references_primitives() -> None:
    text = _text(BOUNDARY)
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive reference: {prim}"


def test_boundary_flag_names() -> None:
    text = _text(BOUNDARY)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"


def test_boundary_only_matching_flag() -> None:
    assert "require only the flag matching the selected gate" in _text(BOUNDARY).lower()


def test_boundary_rejects_unrelated_and_multiple_flags() -> None:
    low = _text(BOUNDARY).lower()
    assert "reject unrelated approval flags" in low
    assert "reject multiple approval flags" in low


# ── 20-21. audit model ────────────────────────────────────────────────────────

def test_boundary_audit_fields() -> None:
    text = _text(BOUNDARY)
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
    ):
        assert field in text, f"missing audit field: {field}"


def test_boundary_audit_mutation_attempted() -> None:
    assert "whether mutation was attempted" in _text(BOUNDARY).lower()


# ── 22. failure / safety ──────────────────────────────────────────────────────

def test_boundary_failure_safety_model() -> None:
    low = _text(BOUNDARY).lower()
    assert "failed precondition means no primitive execution" in low
    assert "no automatic rollback" in low
    assert "no silent retry" in low
    assert "partial completion must remain visible" in low
    assert "rerun policy must be explicit" in low


# ── 23. forbidden automation ──────────────────────────────────────────────────

def test_boundary_forbidden_automation() -> None:
    low = _text(BOUNDARY).lower()
    for token in (
        "autopublish",
        "campaign launch",
        "affiliate link generation",
        "marketplace connector",
        "external api submit",
        "hidden promotion",
        "ui-direct approval",
        "global approve",
        "multi-gate execution",
        "finalization without compliance approved",
        "vault write without explicit gate-specific approval",
    ):
        assert token in low, f"missing forbidden token: {token}"


# ── 24. no-execution guard (new files only) ───────────────────────────────────

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


# ── 25. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ── 26. additive pointer ──────────────────────────────────────────────────────

def test_exec_boundary_points_to_single_gate() -> None:
    assert "SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md" in _text(EXEC_BOUNDARY)


# ── 27. ROADMAP / PROJECT_STATE token regression ──────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_project_state_points_to_single_gate() -> None:
    assert "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md" in _text(PROJECT_STATE)
