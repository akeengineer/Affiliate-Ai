from __future__ import annotations

import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/040-phase6g-manual-approval-audit-verifier-boundary.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md"
WRAPPER_BOUNDARY = REPO_ROOT / "docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md"
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
    assert "phase6g_status: success" in _text(TASK_FILE)


def test_boundary_scope_is_docs_only() -> None:
    low = _text(BOUNDARY).lower()
    assert "boundary-only" in low or "docs/tests/task-only" in low


def test_no_phase6g_runtime_script() -> None:
    assert glob.glob(str(REPO_ROOT / "scripts/dev/*phase6g*")) == []


# ── 5-6. purpose + required audit fields ──────────────────────────────────────

def test_boundary_defines_purpose() -> None:
    low = _text(BOUNDARY).lower()
    assert "audit verifier" in low
    assert "report evidence only" in low and "read-only" in low


def test_boundary_required_audit_fields() -> None:
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
        "mutation_attempted",
        "gate_specific_approval_intent",
        "approved_flag_name",
        "wrapper_version",
        "audit_schema_version",
    ):
        assert field in text, f"missing audit field: {field}"


# ── 7-10. gate values, primitives, flags, matching ───────────────────────────

def test_boundary_gate_values() -> None:
    text = _text(BOUNDARY)
    for gate in ("`promote`", "`decision`", "`finalization`"):
        assert gate in text, f"missing gate value: {gate}"


def test_boundary_references_primitives() -> None:
    text = _text(BOUNDARY)
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive: {prim}"


def test_boundary_references_flags() -> None:
    text = _text(BOUNDARY)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"


def test_boundary_primitive_flag_matching() -> None:
    low = _text(BOUNDARY).lower()
    assert "primitive_name` must match the selected gate" in low or "must match the selected gate" in low
    assert "approved_flag_name` must match the selected gate" in low or "must match the selected gate" in low


# ── 11-12. outcome values + mutation consistency ──────────────────────────────

def test_boundary_outcome_values() -> None:
    text = _text(BOUNDARY)
    for outcome in ("`success`", "`failure`", "`blocked`", "`prevented`"):
        assert outcome in text, f"missing outcome value: {outcome}"


def test_boundary_mutation_consistency() -> None:
    low = _text(BOUNDARY).lower()
    assert "`blocked` or `prevented` means `mutation_attempted` must be false" in low
    assert "must be" in low and "explicit" in low


# ── 13-15. artifact references + path safety ──────────────────────────────────

def test_boundary_references_chain_artifacts() -> None:
    low = _text(BOUNDARY).lower()
    assert "phase 6b packet path" in low
    assert "phase 6c verifier path" in low
    assert "phase 6e execution plan path" in low


def test_boundary_tmp_relative_paths() -> None:
    low = _text(BOUNDARY).lower()
    assert "relative `tmp/` paths" in low


def test_boundary_rejects_unsafe_paths() -> None:
    low = _text(BOUNDARY).lower()
    assert "must not be absolute" in low
    assert "must not include traversal" in low
    assert "must not include vault paths" in low
    assert "must not contain external urls" in low
    assert "must not contain secrets" in low
    assert "must not contain operator-local paths" in low


# ── 16. single-gate consistency ───────────────────────────────────────────────

def test_boundary_single_gate_consistency() -> None:
    low = _text(BOUNDARY).lower()
    for token in (
        "multi-gate list",
        "approve-all",
        "global approval",
        "automatic next-gate",
        "chain execution",
        "hidden promotion",
        "ui-direct approval",
    ):
        assert token in low, f"missing single-gate consistency token: {token}"


# ── 17-18. verdict policy + exit ──────────────────────────────────────────────

def test_boundary_verdict_policy() -> None:
    low = _text(BOUNDARY).lower()
    assert "valid:" in low and "warning:" in low and "invalid:" in low


def test_boundary_verdict_exit_policy() -> None:
    low = _text(BOUNDARY).lower()
    assert "`valid` exits 0" in low
    assert "`warning` exits 0" in low
    assert "`invalid` exits" in low and "non-zero" in low


# ── 19. failure / safety model ────────────────────────────────────────────────

def test_boundary_failure_safety_model() -> None:
    low = _text(BOUNDARY).lower()
    assert "never executes primitives" in low
    assert "never mutates the vault" in low
    assert "reports evidence only" in low
    assert "fail closed" in low
    assert "partial completion explicit" in low or "make partial completion explicit" in low


# ── 20. forbidden automation ──────────────────────────────────────────────────

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


# ── 21. no-execution guard (new files only) ───────────────────────────────────

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


# ── 22. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"


# ── 23. additive pointer ──────────────────────────────────────────────────────

def test_wrapper_boundary_points_to_audit_verifier() -> None:
    assert "MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md" in _text(WRAPPER_BOUNDARY)


# ── 24. ROADMAP / PROJECT_STATE token regression ──────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_project_state_points_to_audit_verifier() -> None:
    assert "docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md" in _text(PROJECT_STATE)
