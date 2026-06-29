from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/dev/run_phase2j_governance_orchestration.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/013-phase2j-hermes-governance-orchestration.md"
PROMPT_FILE = REPO_ROOT / "prompts/workflows/hermes-phase2j-governance-orchestration.md"
SAMPLE_CSV = REPO_ROOT / "vault/samples/import/product-candidates.csv"
OUTPUT_DIR = REPO_ROOT / "tmp/phase2j-hermes-governance"

PRODUCT_ID = "prod-laptop-stand"
REPORT_WEEK = "2026-W26"
SUMMARY_PATH = OUTPUT_DIR / f"governance-summary-{REPORT_WEEK}.md"

VAULT_PRODUCT = REPO_ROOT / "vault" / "products" / f"{PRODUCT_ID}.md"
VAULT_DECISION = REPO_ROOT / "vault" / "decisions" / f"dec-{PRODUCT_ID}-{REPORT_WEEK}.md"

PRIVATE_VAULT_PATHS = [
    "vault/products",
    "vault/trends",
    "vault/marketplace-signals",
    "vault/commissions",
    "vault/meetings",
    "vault/decisions",
    "vault/contents",
    "vault/compliance",
    "vault/reports",
    "vault/.obsidian",
]


def _clean_vault() -> None:
    """Defensive: remove leftover vault artifacts so 2G dry-run starts clean."""
    VAULT_PRODUCT.unlink(missing_ok=True)
    VAULT_DECISION.unlink(missing_ok=True)


def run_phase2j(
    *,
    product_id: str = PRODUCT_ID,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), str(SAMPLE_CSV), REPORT_WEEK, product_id],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


# ── 1. artifacts exist ────────────────────────────────────────────────────────

def test_phase2j_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMPT_FILE.is_file()
    assert SCRIPT_PATH.is_file()
    assert os.access(SCRIPT_PATH, os.X_OK)


# ── 2. default run passes ─────────────────────────────────────────────────────

def test_run_phase2j_passes() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    completed = run_phase2j(env=os.environ.copy())
    assert completed.returncode == 0, completed.stderr
    assert "phase2j_status: success" in completed.stdout
    assert "summary_path:" in completed.stdout
    assert SUMMARY_PATH.is_file()


# ── 3. summary frontmatter ────────────────────────────────────────────────────

def test_summary_has_correct_frontmatter() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    run_phase2j(env=os.environ.copy())
    text = SUMMARY_PATH.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "type: hermes_governance_summary" in text
    assert f"report_week: {REPORT_WEEK}" in text
    assert "mode: dry_run" in text


# ── 4. summary has required governance fields ─────────────────────────────────

def test_summary_has_required_fields() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    run_phase2j(env=os.environ.copy())
    text = SUMMARY_PATH.read_text(encoding="utf-8")
    assert f"product_id: {PRODUCT_ID}" in text
    assert "score_decision: small_batch_test" in text
    assert "promoted_status: dry_run_not_promoted" in text
    assert "decision_status: not_executed" in text
    assert "finalization_status: not_executed" in text
    assert "compliance_gate_status: not_evaluated" in text
    assert "next_allowed_action:" in text
    assert "## Blocked risks" in text


# ── 5. default run does NOT write vault ───────────────────────────────────────

def test_default_run_does_not_write_vault() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    try:
        run_phase2j(env=os.environ.copy())
        assert not VAULT_PRODUCT.exists(), "must not write vault/products/"
        assert not VAULT_DECISION.exists(), "must not write vault/decisions/"
    finally:
        _clean_vault()


# ── 6. summary has no private vault paths ─────────────────────────────────────

def test_summary_has_no_private_vault_paths() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    run_phase2j(env=os.environ.copy())
    text = SUMMARY_PATH.read_text(encoding="utf-8")
    for private_path in PRIVATE_VAULT_PATHS:
        assert private_path not in text, f"Summary references private vault path: {private_path}"


# ── 7. summary has no affiliate content markers ───────────────────────────────

def test_summary_has_no_affiliate_content_markers() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    run_phase2j(env=os.environ.copy())
    text = SUMMARY_PATH.read_text(encoding="utf-8")
    for marker in ["content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post"]:
        assert marker not in text, f"Summary contains affiliate content marker: {marker}"
    assert "http://" not in text
    assert "https://" not in text


# ── 8. fails when ENABLE_AUTOPUBLISH=true ─────────────────────────────────────

def test_fails_when_autopublish_true() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    completed = run_phase2j(env={**os.environ, "ENABLE_AUTOPUBLISH": "true"})
    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in completed.stderr
    assert not OUTPUT_DIR.exists()


# ── 9. fails when ENABLE_OPENAI_API_DIRECT=true ───────────────────────────────

def test_fails_when_openai_direct_enabled() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    _clean_vault()
    completed = run_phase2j(env={**os.environ, "ENABLE_OPENAI_API_DIRECT": "true"})
    assert completed.returncode != 0
    assert "ENABLE_OPENAI_API_DIRECT=true is not allowed" in completed.stderr
    assert not OUTPUT_DIR.exists()


# ── 10. invalid product-id fails ──────────────────────────────────────────────

def test_invalid_product_id_fails() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    completed = run_phase2j(product_id="../evil", env=os.environ.copy())
    assert completed.returncode != 0
    assert "product-id must match" in completed.stderr
    assert not OUTPUT_DIR.exists()
