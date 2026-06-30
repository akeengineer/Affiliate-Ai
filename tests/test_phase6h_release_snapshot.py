from __future__ import annotations

import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/041-phase6h-release-snapshot-update.md"
SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE6.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
DEMO = REPO_ROOT / "docs/DEMO.md"
ACCEPTANCE = REPO_ROOT / "docs/ACCEPTANCE.md"

NEW_FILES = (SNAPSHOT, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-2. existence + final status ─────────────────────────────────────────────

def test_task_and_snapshot_exist() -> None:
    assert TASK_FILE.is_file()
    assert SNAPSHOT.is_file()


def test_task_final_status() -> None:
    assert "phase6h_status: success" in _text(TASK_FILE)


# ── 3. phase matrix ───────────────────────────────────────────────────────────

def test_snapshot_phase_matrix() -> None:
    text = _text(SNAPSHOT)
    for phase in ("Phase 6A", "Phase 6B", "Phase 6C", "Phase 6D", "Phase 6E", "Phase 6F", "Phase 6G"):
        assert phase in text, f"snapshot missing phase: {phase}"


# ── 4. safe read-only chain ───────────────────────────────────────────────────

def test_snapshot_documents_safe_chain() -> None:
    text = _text(SNAPSHOT)
    assert "5D -> 6B -> 6C -> 6E" in text
    for cmd in (
        "run_phase5d_ui_shell_demo.sh",
        "run_phase6b_approval_review_packet.sh",
        "run_phase6c_approval_review_verifier.sh",
        "run_phase6e_approval_execution_plan.sh",
    ):
        assert cmd in text, f"snapshot missing command: {cmd}"


# ── 5-13. guardrail statements ────────────────────────────────────────────────

def test_snapshot_guardrail_statements() -> None:
    low = _text(SNAPSHOT).lower()
    assert "no runtime approval wrapper exists" in low
    assert "no runtime audit verifier exists" in low
    assert "no vault read/write" in low or "no vault writes" in low
    assert "no approval mutation" in low
    assert "phase 2g/2h/2i" in low and "remain unchanged" in low
    assert "boundary-only" in low  # 6F and 6G
    assert "separate future phase" in low
    assert "backend/api/database/marketplace" in low and "out of scope" in low


def test_snapshot_no_2ghi_execution_statement() -> None:
    low = _text(SNAPSHOT).lower()
    assert "no vault read/write was introduced" in low or "no approval mutation was introduced" in low


# ── 14-17. doc updates ────────────────────────────────────────────────────────

def test_project_state_references_snapshot() -> None:
    assert "docs/RELEASE_SNAPSHOT_PHASE6.md" in _text(PROJECT_STATE)


def test_roadmap_marks_6h_complete() -> None:
    text = _text(ROADMAP)
    assert "Phase 6H" in text
    assert "complete" in text.lower() or "done" in text.lower()


def test_demo_has_phase6_section() -> None:
    assert "Phase 6 read-only approval chain" in _text(DEMO)


def test_acceptance_has_phase6_section() -> None:
    assert "Phase 6 read-only approval chain acceptance" in _text(ACCEPTANCE)


# ── 18-19. token regression ───────────────────────────────────────────────────

def test_roadmap_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped token: {token}"


def test_project_state_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI", "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped token: {token}"


# ── 20. Phase 3E/5E snapshot references untouched ─────────────────────────────

def test_phase3e_5e_snapshots_intact() -> None:
    assert (REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE3.md").is_file()
    assert (REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE5.md").is_file()


# ── 21. no runtime script ─────────────────────────────────────────────────────

def test_no_phase6h_runtime_script() -> None:
    assert glob.glob(str(REPO_ROOT / "scripts/dev/*phase6h*")) == []


# ── 22. no-execution guard (new files only) ───────────────────────────────────

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


# ── 23. static safety (new files only) ────────────────────────────────────────

def test_new_files_static_safety() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai",
                      "AWS_SECRET_ACCESS_KEY", "BEGIN PRIVATE KEY", "OPENAI_API_KEY"):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
