from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/033-phase5e-release-snapshot-update.md"
SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE5.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
DEMO = REPO_ROOT / "docs/DEMO.md"
ACCEPTANCE = REPO_ROOT / "docs/ACCEPTANCE.md"

# Only the brand-new Phase 5E files are scanned for static safety, so existing
# token-contract content elsewhere is never treated as a violation.
NEW_FILES = (SNAPSHOT, TASK_FILE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 1-3. existence + final status ─────────────────────────────────────────────

def test_snapshot_exists() -> None:
    assert SNAPSHOT.is_file()


def test_task_exists() -> None:
    assert TASK_FILE.is_file()


def test_task_final_status() -> None:
    assert "phase5e_status: success" in _text(TASK_FILE)


# ── 4. phase tokens ───────────────────────────────────────────────────────────

def test_snapshot_phase_tokens() -> None:
    text = _text(SNAPSHOT)
    for token in ("Phase 4A", "Phase 4B", "Phase 4C", "Phase 4D", "Phase 4E",
                  "Phase 5A", "Phase 5B", "Phase 5C", "Phase 5D"):
        assert token in text, f"snapshot missing phase token: {token}"


# ── 5-6. commands + outputs ───────────────────────────────────────────────────

def test_commands_mentioned() -> None:
    combined = _text(SNAPSHOT) + _text(PROJECT_STATE)
    for cmd in ("run_phase4e_demo_bundle.sh", "run_phase5b_ui_shell.sh",
                "run_phase5c_ui_shell_verifier.sh", "run_phase5d_ui_shell_demo.sh"):
        assert cmd in combined, f"missing command: {cmd}"


def test_outputs_mentioned() -> None:
    combined = _text(SNAPSHOT) + _text(PROJECT_STATE)
    for out in ("tmp/phase4e-demo-bundle/", "tmp/phase5b-ui-shell/",
                "tmp/phase5c-ui-shell-verifier/", "tmp/phase5d-ui-shell-demo/"):
        assert out in combined, f"missing output: {out}"


# ── 7. verdict/status tokens ──────────────────────────────────────────────────

def test_verdict_tokens() -> None:
    text = _text(SNAPSHOT)
    for token in ("ready", "warning", "failed", "phase5d_status", "ui_shell_demo_status"):
        assert token in text, f"snapshot missing verdict token: {token}"


# ── 8. PROJECT_STATE Phase 5 capability tokens ────────────────────────────────

def test_project_state_capability_tokens() -> None:
    text = _text(PROJECT_STATE)
    for token in ("static read-only UI shell", "UI shell verifier", "UI shell demo bundle"):
        assert token in text, f"PROJECT_STATE missing capability token: {token}"


# ── 9. ROADMAP marks Phase 5A-5D complete ─────────────────────────────────────

def test_roadmap_marks_phase5_complete() -> None:
    text = _text(ROADMAP)
    assert "Phase 5D" in text
    assert "complete" in text.lower() or "done" in text.lower()
    for token in ("Phase 5A", "Phase 5B", "Phase 5C", "Phase 5D"):
        assert token in text, f"ROADMAP missing token: {token}"


# ── 10. Phase 3E regression guard (PROJECT_STATE) ─────────────────────────────

def test_project_state_phase3e_tokens_preserved() -> None:
    text = _text(PROJECT_STATE)
    for token in ("Current architecture", "no database", "no FastAPI", "no UI",
                  "no external APIs", "no autopublish"):
        assert token in text, f"PROJECT_STATE dropped Phase 3E token: {token}"


# ── 11. ROADMAP Phase 3E token contract preserved ─────────────────────────────

def test_roadmap_phase3e_tokens_preserved() -> None:
    text = _text(ROADMAP)
    for token in ("Phase 4A", "Phase 4B", "Phase 4C", "Phase 5", "read-only", "manual-approved"):
        assert token in text, f"ROADMAP dropped Phase 3E token: {token}"


# ── 12-13. DEMO + ACCEPTANCE references ───────────────────────────────────────

def test_demo_references() -> None:
    text = _text(DEMO)
    assert "run_phase5d_ui_shell_demo.sh" in text
    assert "tmp/phase5b-ui-shell/index.html" in text


def test_acceptance_references() -> None:
    text = _text(ACCEPTANCE)
    assert "run_phase5d_ui_shell_demo.sh" in text
    for token in ("ready", "warning", "failed"):
        assert token in text, f"ACCEPTANCE missing token: {token}"


# ── 14. static safety on the new Phase 5E files ───────────────────────────────

def test_new_files_static_safety() -> None:
    secret_res = (re.compile(r"sk-[A-Za-z0-9]{20,}"), re.compile(r"AKIA[A-Z0-9]{16}"),
                  re.compile(r"Bearer [A-Za-z0-9]{20,}"))
    for path in NEW_FILES:
        text = _text(path)
        for token in ("http://", "https://", "/home/ubuntu/Affiliate-Ai", "tag=", "affiliate="):
            assert token not in text, f"{path.name} contains forbidden token: {token}"
        for rx in secret_res:
            assert not rx.search(text), f"{path.name} contains a secret-like marker"


# ── 15. new files do not instruct approved-workflow execution ─────────────────

def test_new_files_no_approved_workflow() -> None:
    for path in NEW_FILES:
        text = _text(path)
        for ref in ("run_phase2g", "run_phase2h", "run_phase2i",
                    "promote_product_candidates.py", "create_decision.py", "finalize_decision.py"):
            assert ref not in text, f"{path.name} references approved workflow: {ref}"
