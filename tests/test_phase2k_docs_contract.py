from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_FILE = REPO_ROOT / "codex/tasks/014-phase2k-operating-manual.md"
MANUAL = REPO_ROOT / "docs/PHASE2_OPERATING_MANUAL.md"
FLOW = REPO_ROOT / "docs/PHASE2_GOVERNANCE_FLOW.md"
DRY_RUN_SCRIPT = REPO_ROOT / "scripts/dev/run_phase2_full_dry_run.sh"
SAMPLE_CSV = REPO_ROOT / "vault/samples/import/product-candidates.csv"

PRODUCT_ID = "prod-laptop-stand"
REPORT_WEEK = "2026-W26"
VAULT_PRODUCT = REPO_ROOT / "vault" / "products" / f"{PRODUCT_ID}.md"
VAULT_DECISION = REPO_ROOT / "vault" / "decisions" / f"dec-{PRODUCT_ID}-{REPORT_WEEK}.md"

OUTPUT_DIRS = [
    REPO_ROOT / "tmp/phase2e-import-score-report",
    REPO_ROOT / "tmp/phase2f-hermes",
    REPO_ROOT / "tmp/phase2j-hermes-governance",
]


def _clean_vault() -> None:
    VAULT_PRODUCT.unlink(missing_ok=True)
    VAULT_DECISION.unlink(missing_ok=True)


def _run_dry_run(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(DRY_RUN_SCRIPT), str(SAMPLE_CSV), REPORT_WEEK, PRODUCT_ID],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


# ── 1-3. files exist ──────────────────────────────────────────────────────────

def test_operating_manual_exists() -> None:
    assert MANUAL.is_file()


def test_governance_flow_exists() -> None:
    assert FLOW.is_file()


def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


# ── 4. manual mentions all Phase 2 stages ─────────────────────────────────────

def test_manual_mentions_all_stages() -> None:
    text = MANUAL.read_text(encoding="utf-8")
    for stage in ["2D", "2E", "2F", "2G", "2H", "2I", "2J"]:
        assert f"Phase {stage}" in text, f"manual missing Phase {stage}"


# ── 5. manual documents guardrails ────────────────────────────────────────────

def test_manual_documents_guardrails() -> None:
    text = MANUAL.read_text(encoding="utf-8")
    for guardrail in [
        "no database",
        "no UI",
        "no external APIs",
        "no autopublish",
        "no campaign launch",
    ]:
        assert guardrail in text, f"manual missing guardrail: {guardrail}"


# ── 6. manual documents approved vault writes ─────────────────────────────────

def test_manual_documents_approved_vault_writes() -> None:
    text = MANUAL.read_text(encoding="utf-8")
    assert "vault/products" in text
    assert "vault/decisions" in text
    assert "all vault writes require explicit approval" in text


# ── 7. governance flow contains a Mermaid diagram ─────────────────────────────

def test_flow_contains_mermaid() -> None:
    text = FLOW.read_text(encoding="utf-8")
    assert "```mermaid" in text


# ── 8. governance flow explains Phase 2J dry-run only ─────────────────────────

def test_flow_explains_phase2j_dry_run_only() -> None:
    text = FLOW.read_text(encoding="utf-8")
    assert "Why Phase 2J is dry-run only" in text


# ── 9. governance flow mentions not_executed statuses ─────────────────────────

def test_flow_mentions_not_executed_statuses() -> None:
    text = FLOW.read_text(encoding="utf-8")
    assert "decision_status: not_executed" in text
    assert "finalization_status: not_executed" in text


# ── 10. full dry-run wrapper (only if it exists) ──────────────────────────────

def test_dry_run_script_syntax_and_executable() -> None:
    if not DRY_RUN_SCRIPT.exists():
        return
    assert os.access(DRY_RUN_SCRIPT, os.X_OK)
    result = subprocess.run(
        ["bash", "-n", str(DRY_RUN_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_dry_run_default_passes_without_vault_writes() -> None:
    if not DRY_RUN_SCRIPT.exists():
        return
    for d in OUTPUT_DIRS:
        shutil.rmtree(d, ignore_errors=True)
    _clean_vault()
    try:
        result = _run_dry_run(env=os.environ.copy())
        assert result.returncode == 0, result.stderr
        assert "phase2e_status: success" in result.stdout
        assert "phase2f_status: success" in result.stdout
        assert "phase2j_status: success" in result.stdout
        assert "final_status: success" in result.stdout
        assert not VAULT_PRODUCT.exists(), "must not write vault/products/<id>.md"
        assert not VAULT_DECISION.exists(), "must not write vault/decisions/dec-<id>-<week>.md"
    finally:
        _clean_vault()


def test_dry_run_fails_when_autopublish_true() -> None:
    if not DRY_RUN_SCRIPT.exists():
        return
    _clean_vault()
    result = _run_dry_run(env={**os.environ, "ENABLE_AUTOPUBLISH": "true"})
    assert result.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in result.stderr
