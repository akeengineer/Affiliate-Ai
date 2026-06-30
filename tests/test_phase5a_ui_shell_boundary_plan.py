from __future__ import annotations

import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_FILE = REPO_ROOT / "codex/tasks/025-phase5a-ui-shell-boundary-plan.md"
BOUNDARY = REPO_ROOT / "docs/UI_SHELL_BOUNDARY.md"
PLAN = REPO_ROOT / "docs/PHASE5_READONLY_UI_SHELL_PLAN.md"
GITIGNORE = REPO_ROOT / ".gitignore"

NEW_DOC_FILES = [TASK_FILE, BOUNDARY, PLAN]

PHASE4E_DEMO_COMMAND = "bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join(_text(p) for p in NEW_DOC_FILES)


def _combined_lower() -> str:
    return _combined().lower()


# ── 1-3. files exist ──────────────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_boundary_doc_exists() -> None:
    assert BOUNDARY.is_file()


def test_plan_doc_exists() -> None:
    assert PLAN.is_file()


# ── 4. final status target ────────────────────────────────────────────────────

def test_task_file_includes_final_status() -> None:
    assert "phase5a_status: success" in _text(TASK_FILE)


# ── 5. Phase 4E demo command ──────────────────────────────────────────────────

def test_docs_mention_phase4e_demo_command() -> None:
    assert PHASE4E_DEMO_COMMAND in _combined()


# ── 6. preferred future data sources ──────────────────────────────────────────

def test_docs_mention_preferred_data_sources() -> None:
    combined = _combined()
    for token in [
        "phase4b-ui-snapshot",
        "phase4c-snapshot-catalog",
        "phase4d-demo-verifier",
        "phase4e-demo-bundle",
    ]:
        assert token in combined, f"missing preferred data source: {token}"


# ── 7. legacy/reference-only data sources ─────────────────────────────────────

def test_docs_mention_legacy_data_sources() -> None:
    combined = _combined()
    for token in [
        "phase3b-portfolio-dashboard",
        "phase3a-dashboard",
        "phase2e-import-score-report",
    ]:
        assert token in combined, f"missing legacy data source: {token}"


# ── 8. forbid vault reads and writes ──────────────────────────────────────────

def test_docs_forbid_vault_reads_and_writes() -> None:
    combined = _combined_lower()
    assert "vault read" in combined
    assert "vault write" in combined


# ── 9. forbid backend stack ───────────────────────────────────────────────────

def test_docs_forbid_backend_stack() -> None:
    combined = _combined_lower()
    for token in ["database", "fastapi", "backend", "server", "api routes"]:
        assert token in combined, f"docs must reference forbidden: {token}"


# ── 10. forbid approval mutation functions ────────────────────────────────────

def test_docs_forbid_approval_functions() -> None:
    combined = _combined_lower()
    for token in ["approvals", "promote", "create decision", "finalize decision"]:
        assert token in combined, f"docs must forbid: {token}"


# ── 11. forbid external connectors ────────────────────────────────────────────

def test_docs_forbid_external_connectors() -> None:
    combined = _combined_lower()
    for token in ["external apis", "external urls", "marketplace connector"]:
        assert token in combined, f"docs must forbid: {token}"


# ── 12. forbid affiliate publishing ───────────────────────────────────────────

def test_docs_forbid_affiliate_publishing() -> None:
    combined = _combined_lower()
    for token in ["affiliate content", "autopublish", "campaign launch"]:
        assert token in combined, f"docs must forbid: {token}"


# ── 13. forbid raw artifact export/body ───────────────────────────────────────

def test_docs_forbid_raw_artifact_usage() -> None:
    combined = _combined_lower()
    assert "raw artifact export" in combined
    assert "raw artifact body" in combined


# ── 14. docs/tests only ───────────────────────────────────────────────────────

def test_docs_state_docs_tests_only() -> None:
    assert "docs/tests only" in _combined_lower()


# ── 15. no UI shell implementation yet ────────────────────────────────────────

def test_docs_state_no_ui_shell_yet() -> None:
    assert "no ui shell" in _combined_lower()


# ── 16. future subphases ──────────────────────────────────────────────────────

def test_docs_include_future_subphases() -> None:
    combined = _combined()
    for token in ["Phase 5B", "Phase 5C", "Phase 5D", "Phase 5E"]:
        assert token in combined, f"missing subphase: {token}"


# ── 17. known limitations ─────────────────────────────────────────────────────

def test_docs_include_known_limitations() -> None:
    assert "known limitations" in _text(BOUNDARY).lower()
    assert "exit criteria" in _text(PLAN).lower()


# ── 18. no forbidden implementation files added ───────────────────────────────

def test_no_forbidden_implementation_files() -> None:
    forbidden = [
        "package.json",
        "package-lock.json",
        "next.config.js",
        "vite.config.js",
        "app",
        "src",
        "pages",
        "components",
        "frontend",
        "backend",
        "api",
    ]
    for name in forbidden:
        assert not (REPO_ROOT / name).exists(), f"forbidden path present: {name}"


# ── 19. no new runtime script for Phase 5A ────────────────────────────────────

def test_no_phase5a_runtime_script() -> None:
    matches = glob.glob(str(REPO_ROOT / "scripts/dev/*phase5a*"))
    assert matches == [], f"unexpected Phase 5A script(s): {matches}"
    assert not (REPO_ROOT / "scripts/dev/run_phase5a_ui_shell.sh").exists()


# ── 20. .gitignore not modified for Phase 5A ──────────────────────────────────

def test_gitignore_not_modified_for_phase5a() -> None:
    assert "phase5a" not in _text(GITIGNORE).lower()


# ── 21. no external URLs in new docs ──────────────────────────────────────────

def test_docs_have_no_external_urls() -> None:
    for path in NEW_DOC_FILES:
        text = _text(path)
        assert "http://" not in text, f"{path.name} contains http://"
        assert "https://" not in text, f"{path.name} contains https://"


# ── 22. no secrets or affiliate URL markers ───────────────────────────────────

def test_docs_have_no_secret_or_affiliate_markers() -> None:
    markers = [
        "api_key",
        "apikey",
        "AKIA",
        "BEGIN RSA",
        "password=",
        "?tag=",
        "aff_id",
        "affid=",
        "?ref=",
    ]
    combined = _combined()
    for marker in markers:
        assert marker not in combined, f"docs contain forbidden marker: {marker}"


# ── 23. no instruction to run approved workflows ──────────────────────────────

def test_docs_do_not_run_approved_workflows() -> None:
    combined = _combined()
    for script in [
        "run_phase2g_approval_promote.sh",
        "run_phase2h_decision_review.sh",
        "run_phase2i_decision_finalization.sh",
    ]:
        assert script not in combined, f"docs must not run: {script}"


# ── 24. no mutation scripts as runnable actions ───────────────────────────────

def test_docs_do_not_reference_mutation_scripts() -> None:
    combined = _combined()
    for script in [
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ]:
        assert script not in combined, f"docs must not reference: {script}"


# ── 25. no framework install instruction ──────────────────────────────────────

def test_docs_have_no_framework_install_instruction() -> None:
    combined = _combined_lower()
    for instruction in [
        "npm install",
        "npx ",
        "create-next-app",
        "create-react-app",
        "npm create vite",
        "yarn add",
        "pnpm add",
    ]:
        assert instruction not in combined, f"docs contain install instruction: {instruction}"
