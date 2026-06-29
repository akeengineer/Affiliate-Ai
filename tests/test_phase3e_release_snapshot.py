from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = REPO_ROOT / "codex/tasks/019-phase3e-release-snapshot.md"
PROJECT_STATE = REPO_ROOT / "docs/PROJECT_STATE.md"
RELEASE_SNAPSHOT = REPO_ROOT / "docs/RELEASE_SNAPSHOT_PHASE3.md"
ROADMAP = REPO_ROOT / "docs/ROADMAP.md"
SHOW_SCRIPT = REPO_ROOT / "scripts/dev/show_release_snapshot.sh"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

GUARDRAILS = (
    "no database",
    "no FastAPI",
    "no UI",
    "no external APIs",
    "no affiliate content generation",
    "no autopublish",
    "no campaign launch",
    "no vault writes by default",
)

PHASE_TOKENS = (
    "Phase 1",
    "Phase 2A",
    "Phase 2B",
    "Phase 2C",
    "Phase 2D",
    "Phase 2E",
    "Phase 2F",
    "Phase 2G",
    "Phase 2H",
    "Phase 2I",
    "Phase 2J",
    "Phase 2K",
    "Phase 3A",
    "Phase 3B",
    "Phase 3C",
    "Phase 3D",
)

COMMAND_TOKENS = (
    "help",
    "status",
    "doctor",
    "dry-run",
    "product",
    "portfolio",
    "run_phase3d_acceptance.sh",
)

ARTIFACT_MAP_SECTIONS = (
    "tmp outputs",
    "vault memory outputs",
    "docs",
    "scripts",
)

ROADMAP_TOKENS = (
    "Phase 4A",
    "Phase 4B",
    "Phase 4C",
    "Phase 5",
    "read-only",
    "manual-approved",
)


def _run_show(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SHOW_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


# ── 1-5. existence ────────────────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_project_state_exists() -> None:
    assert PROJECT_STATE.is_file()


def test_release_snapshot_exists() -> None:
    assert RELEASE_SNAPSHOT.is_file()


def test_roadmap_exists() -> None:
    assert ROADMAP.is_file()


def test_show_script_exists_and_executable() -> None:
    assert SHOW_SCRIPT.is_file()
    assert os.access(SHOW_SCRIPT, os.X_OK)


# ── 6. bash -n ────────────────────────────────────────────────────────────────

def test_show_script_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(SHOW_SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 7. guardrails ─────────────────────────────────────────────────────────────

def test_project_state_mentions_guardrails() -> None:
    text = PROJECT_STATE.read_text(encoding="utf-8")
    for guardrail in GUARDRAILS:
        assert guardrail in text, f"PROJECT_STATE.md missing guardrail: {guardrail}"


# ── 8. phase matrix ───────────────────────────────────────────────────────────

def test_release_snapshot_mentions_phases() -> None:
    text = RELEASE_SNAPSHOT.read_text(encoding="utf-8")
    for token in PHASE_TOKENS:
        assert token in text, f"RELEASE_SNAPSHOT_PHASE3.md missing phase token: {token}"


# ── 9. operator command tokens ────────────────────────────────────────────────

def test_project_state_mentions_commands() -> None:
    text = PROJECT_STATE.read_text(encoding="utf-8")
    for token in COMMAND_TOKENS:
        assert token in text, f"PROJECT_STATE.md missing command token: {token}"


# ── 10. acceptance output tokens ──────────────────────────────────────────────

def test_release_snapshot_mentions_acceptance_tokens() -> None:
    text = RELEASE_SNAPSHOT.read_text(encoding="utf-8")
    for token in ("acceptance_status: success", "vault_products_writes: 0", "vault_decisions_writes: 0"):
        assert token in text, f"RELEASE_SNAPSHOT_PHASE3.md missing token: {token}"


# ── 11. roadmap tokens ────────────────────────────────────────────────────────

def test_roadmap_mentions_tokens() -> None:
    text = ROADMAP.read_text(encoding="utf-8")
    for token in ROADMAP_TOKENS:
        assert token in text, f"ROADMAP.md missing token: {token}"


# ── 12. artifact map sections ─────────────────────────────────────────────────

def test_project_state_has_artifact_map_sections() -> None:
    text = PROJECT_STATE.read_text(encoding="utf-8")
    for section in ARTIFACT_MAP_SECTIONS:
        assert section in text, f"PROJECT_STATE.md missing artifact-map section: {section}"


# ── 13-14. show script runtime ────────────────────────────────────────────────

def test_show_script_runs() -> None:
    result = _run_show()
    assert result.returncode == 0, result.stderr


def test_show_script_output_content() -> None:
    result = _run_show()
    assert result.returncode == 0, result.stderr
    assert "Current architecture" in result.stdout
    assert "status_command: success" in result.stdout


# ── 15. no vault write ────────────────────────────────────────────────────────

def test_show_script_no_vault_write() -> None:
    before = _vault_snapshot()
    result = _run_show()
    assert result.returncode == 0, result.stderr
    after = _vault_snapshot()
    assert before == after, f"vault changed: before={before} after={after}"


# ── 16. no hardcoded pytest count asserted ────────────────────────────────────
# (Intentionally omitted: the docs and tests do not assert a brittle total
# pytest count. RELEASE_SNAPSHOT_PHASE3.md documents `python -m pytest -q`.)
