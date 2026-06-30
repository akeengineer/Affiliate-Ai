from __future__ import annotations

import glob
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/037-phase6d-manual-approval-execution-boundary.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md"
WORKFLOW_BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md"
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
    assert "phase6d_status: success" in _text(TASK_FILE)


def test_boundary_scope_is_docs_only() -> None:
    low = _text(BOUNDARY).lower()
    assert "boundary-only" in low or "docs/tests/task-only" in low


def test_no_phase6d_runtime_script() -> None:
    assert glob.glob(str(REPO_ROOT / "scripts/dev/*phase6d*")) == []


# ── 5-7. preconditions (6B/6C, ready) ─────────────────────────────────────────

def test_boundary_references_6b_6c_preconditions() -> None:
    text = _text(BOUNDARY)
    assert "Phase 6B" in text
    assert "Phase 6C" in text


def test_boundary_requires_ready_verdict() -> None:
    text = _text(BOUNDARY)
    assert "`ready`" in text or "verdict is `ready`" in text


def test_boundary_rejects_warning_failed_for_mutation() -> None:
    low = _text(BOUNDARY).lower()
    assert "warning" in low and "failed" in low and "not sufficient for mutation" in low


# ── 8-10. gates / flags / primitives ──────────────────────────────────────────

def test_boundary_has_gate_names() -> None:
    low = _text(BOUNDARY).lower()
    for gate in ("promote gate", "decision gate", "finalization gate"):
        assert gate in low, f"missing gate: {gate}"


def test_boundary_has_flag_names() -> None:
    text = _text(BOUNDARY)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"


def test_boundary_references_primitives() -> None:
    text = _text(BOUNDARY)
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive reference: {prim}"


# ── 11-14. ordering / compliance / UI / per-gate ──────────────────────────────

def test_boundary_has_mandatory_order() -> None:
    assert "promote -> decision -> finalization" in _text(BOUNDARY)


def test_boundary_finalization_requires_compliance() -> None:
    low = _text(BOUNDARY).lower()
    assert "no finalization unless" in low and "approved" in low


def test_boundary_no_ui_direct() -> None:
    assert "no direct execution from the ui shell" in _text(BOUNDARY).lower()


def test_boundary_per_gate_no_global() -> None:
    low = _text(BOUNDARY).lower()
    assert "per-gate" in low
    assert "no broad/global approval" in low or "no approve-all" in low


# ── 15. audit fields ──────────────────────────────────────────────────────────

def test_boundary_has_audit_fields() -> None:
    text = _text(BOUNDARY)
    for field in (
        "product_id",
        "report_week",
        "gate_name",
        "primitive_name",
        "operator",
        "approval_reason",
        "timestamp",
        "source_packet_path",
        "verifier_path",
        "precondition_summary",
        "result_summary",
    ):
        assert field in text, f"missing audit field: {field}"


# ── 16. failure / rollback ────────────────────────────────────────────────────

def test_boundary_failure_rollback_model() -> None:
    low = _text(BOUNDARY).lower()
    assert "no automatic rollback" in low
    assert "failed gate stops the sequence" in low
    assert "partial completion must be visible in audit" in low
    assert "rerun policy must be explicit" in low
    assert "non-idempotent" in low


# ── 17. forbidden automation ──────────────────────────────────────────────────

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
        "finalization without compliance approved",
        "vault write without explicit gate-specific approval",
    ):
        assert token in low, f"missing forbidden token: {token}"


# ── 18. no-execution guard (new files only) ───────────────────────────────────

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


# ── 19. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ── 20. additive pointer ──────────────────────────────────────────────────────

def test_workflow_boundary_points_to_execution_boundary() -> None:
    assert "MANUAL_APPROVAL_EXECUTION_BOUNDARY.md" in _text(WORKFLOW_BOUNDARY)


# ── 21. ROADMAP / PROJECT_STATE token regression ──────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_project_state_points_to_execution_boundary() -> None:
    assert "docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md" in _text(PROJECT_STATE)
