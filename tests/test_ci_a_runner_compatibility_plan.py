from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/026-ci-a-python-tests-runner-compatibility-plan.md"
PLAN = REPO_ROOT / "docs/CI_RUNNER_COMPATIBILITY_PLAN.md"

DOCS = [TASK_FILE, PLAN]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join(_text(p) for p in DOCS)


def _combined_lower() -> str:
    return _combined().lower()


# ── files exist ───────────────────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_plan_doc_exists() -> None:
    assert PLAN.is_file()


# ── three root causes documented ──────────────────────────────────────────────

def test_docs_name_the_failing_scripts() -> None:
    combined = _combined()
    assert "scripts/tmux/start-affiliate-warroom.sh" in combined
    assert "scripts/dev/check_hermes_runtime.sh" in combined


def test_docs_name_hardcoded_repo_root() -> None:
    assert "/home/ubuntu/Affiliate-Ai" in _combined()


def test_docs_name_operator_only_coupling() -> None:
    combined = _combined_lower()
    assert "sudo hermes" in combined
    assert "project_dir" in combined


def test_docs_name_nested_smoke_test() -> None:
    combined = _combined()
    assert "tests/test_phase1_smoke.py" in combined


def test_docs_state_failure_counts() -> None:
    combined = _combined()
    assert "6 failed" in combined
    assert "362 passed" in combined


# ── portability principle documented ──────────────────────────────────────────

def test_docs_state_derive_repo_root_principle() -> None:
    combined = _combined()
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in combined


# ── subphases documented ──────────────────────────────────────────────────────

def test_docs_include_subphases() -> None:
    combined = _combined()
    for token in ["Phase CI-A", "Phase CI-B", "Phase CI-C"]:
        assert token in combined, f"missing subphase: {token}"


# ── plan-only scope: no fix applied in this phase ─────────────────────────────

def test_docs_state_plan_only() -> None:
    combined = _combined_lower()
    assert "docs/tests only" in combined or "plan only" in combined
    assert "no script change" in combined


def test_warroom_script_still_hardcoded_in_this_phase() -> None:
    # Phase CI-A is plan-only; the portability fix is deferred to CI-B.
    # This guard fails if someone applies the fix in the plan PR by mistake.
    warroom = REPO_ROOT / "scripts/tmux/start-affiliate-warroom.sh"
    assert 'PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/Affiliate-Ai}"' in _text(warroom)


# ── final status target ───────────────────────────────────────────────────────

def test_task_file_includes_final_status() -> None:
    assert "phase_ci_a_status: success" in _text(TASK_FILE)
