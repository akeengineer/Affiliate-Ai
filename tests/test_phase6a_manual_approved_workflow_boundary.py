from __future__ import annotations

import glob
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/034-phase6a-manual-approved-workflow-boundary.md"
BOUNDARY = REPO_ROOT / "docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"

NEW_FILES = (BOUNDARY, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-3. existence / scope ────────────────────────────────────────────────────

def test_boundary_and_task_exist() -> None:
    assert BOUNDARY.is_file()
    assert TASK_FILE.is_file()


def test_task_final_status() -> None:
    assert "phase6a_status: success" in _text(TASK_FILE)


def test_boundary_scope_is_docs_only() -> None:
    low = _text(BOUNDARY).lower()
    assert "boundary contract only" in low or "docs/tests/task-only" in low


# ── 4-5. gates + flag names ───────────────────────────────────────────────────

def test_boundary_has_gate_names() -> None:
    low = _text(BOUNDARY).lower()
    for gate in ("promote gate", "decision gate", "finalization gate"):
        assert gate in low, f"missing gate: {gate}"


def test_boundary_has_flag_names() -> None:
    text = _text(BOUNDARY)
    for flag in ("APPROVE_PROMOTE", "APPROVE_DECISION", "APPROVE_FINALIZE"):
        assert flag in text, f"missing flag: {flag}"


# ── 6. primitive references ───────────────────────────────────────────────────

def test_boundary_references_primitives() -> None:
    text = _text(BOUNDARY)
    for prim in ("promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
        assert prim in text, f"missing primitive reference: {prim}"


# ── 7. mandatory ordering ─────────────────────────────────────────────────────

def test_boundary_has_gate_order() -> None:
    text = _text(BOUNDARY)
    assert "promote -> decision -> finalization" in text


# ── 8. evidence fields ────────────────────────────────────────────────────────

def test_boundary_has_evidence_fields() -> None:
    text = _text(BOUNDARY)
    low = text.lower()
    for field in (
        "product_id",
        "report_week",
        "score_decision",
        "product_opportunity_score",
        "confidence_score",
        "compliance_status",
        "timestamp",
        "approval reason",
    ):
        assert field in text, f"missing evidence field: {field}"
    assert "verifier status" in low or "verifier verdict" in low
    assert "operator identity placeholder" in low


# ── 9. source artifact references ─────────────────────────────────────────────

def test_boundary_references_source_phases() -> None:
    text = _text(BOUNDARY)
    for phase in ("Phase 2E", "Phase 2F", "Phase 2J", "Phase 3A", "Phase 3B", "Phase 4E", "Phase 5D"):
        assert phase in text, f"missing source artifact phase: {phase}"


# ── 10. forbidden automation ──────────────────────────────────────────────────

def test_boundary_documents_forbidden_automation() -> None:
    low = _text(BOUNDARY).lower()
    for token in (
        "autopublish",
        "campaign launch",
        "external api submit",
        "affiliate link generation",
        "direct approval from ui shell",
        "vault write without explicit approval",
        "finalization without",
    ):
        assert token in low, f"missing forbidden-automation token: {token}"


# ── 11. no runtime script added ───────────────────────────────────────────────

def test_no_phase6a_runtime_script() -> None:
    matches = glob.glob(str(REPO_ROOT / "scripts/dev/*phase6a*"))
    assert matches == [], f"unexpected Phase 6A script(s): {matches}"
    assert not (REPO_ROOT / "scripts/dev/run_phase6a_manual_approval.sh").exists()


# ── 12. no execution examples ─────────────────────────────────────────────────

def test_new_files_have_no_execution_examples() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for banned in (
            "APPROVE_PROMOTE=true",
            "APPROVE_DECISION=true",
            "APPROVE_FINALIZE=true",
            "bash scripts/dev/run_phase2g",
            "bash scripts/dev/run_phase2h",
            "bash scripts/dev/run_phase2i",
        ):
            assert banned not in text, f"{path.name} contains execution example: {banned}"


# ── 13. ROADMAP / PROJECT_STATE token regression ──────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 4A", "Phase 4B", "Phase 4C", "Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


def test_project_state_points_to_boundary() -> None:
    assert "docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md" in _text(PROJECT_STATE)


# ── 14. static safety (new Phase 6A files only) ───────────────────────────────

def test_new_files_static_safety() -> None:
    secret_markers = ("AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY")
    secret_res = (re.compile(r"sk-[A-Za-z0-9]{20,}"), re.compile(r"AKIA[A-Z0-9]{16}"))
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai", "tag=", "affiliate="):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        for marker in secret_markers:
            assert marker not in text, f"{path.name} contains secret marker: {marker}"
        for rx in secret_res:
            assert not rx.search(text), f"{path.name} contains a secret-like pattern"
