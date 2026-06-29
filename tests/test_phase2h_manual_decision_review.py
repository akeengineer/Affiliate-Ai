from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_SCRIPT = REPO_ROOT / "scripts/dev/create_decision.py"
BASH_WRAPPER = REPO_ROOT / "scripts/dev/run_phase2h_decision_review.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/011-phase2h-manual-decision-review.md"
REVIEW_DIR = REPO_ROOT / "tmp" / "phase2h-decision-review"
VAULT_DECISIONS = REPO_ROOT / "vault" / "decisions"
VAULT_PRODUCTS = REPO_ROOT / "vault" / "products"

TEST_PRODUCT_ID = "pytest-phase2h-test"
REPORT_WEEK = "2026-W26"
DECISION_ID = f"dec-{TEST_PRODUCT_ID}-{REPORT_WEEK}"

SCORED_FRONTMATTER: dict[str, Any] = {
    "type": "product_candidate",
    "product_id": TEST_PRODUCT_ID,
    "product_name": "Pytest Phase 2H Test Product",
    "marketplace": "TikTok Shop",
    "currency": "USD",
    "demand_score": 83,
    "trend_velocity_score": 79,
    "marketplace_rank_score": 76,
    "commission_score": 72,
    "content_fit_score": 81,
    "competition_gap_score": 69,
    "risk_score": 22,
    "product_opportunity_score": 77.65,
    "score_decision": "small_batch_test",
    "confidence_score": 100,
    "missing_signal_count": 0,
    "last_scored_at": "2026-06-29T03:00:00Z",
    "status": "scored",
    "created_at": "2026-06-29T02:00:00Z",
    "updated_at": "2026-06-29T03:00:00Z",
}


def _write_product_note(frontmatter: dict[str, Any] = SCORED_FRONTMATTER) -> Path:
    VAULT_PRODUCTS.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    note = f"---\n{fm_text}\n---\n\n# {frontmatter['product_name']}\n\n## Summary\n- Test note.\n"
    path = VAULT_PRODUCTS / f"{frontmatter['product_id']}.md"
    path.write_text(note, encoding="utf-8")
    return path


def _cleanup() -> None:
    (VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md").unlink(missing_ok=True)
    (VAULT_DECISIONS / f"{DECISION_ID}.md").unlink(missing_ok=True)
    tmp_artifact = REVIEW_DIR / f"{DECISION_ID}.md"
    tmp_artifact.unlink(missing_ok=True)


def _run(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DECISION_SCRIPT), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_wrapper(
    product_id: str,
    decision: str,
    report_week: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(BASH_WRAPPER), product_id, decision, report_week],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _base_args() -> list[str]:
    return [
        "--product-id", TEST_PRODUCT_ID,
        "--decision", "small_batch_test",
        "--report-week", REPORT_WEEK,
    ]


# ── 1. artifacts exist ────────────────────────────────────────────────────────

def test_phase2h_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert DECISION_SCRIPT.is_file()
    assert BASH_WRAPPER.is_file()
    assert os.access(BASH_WRAPPER, os.X_OK)


# ── 2. dry-run completes ──────────────────────────────────────────────────────

def test_dry_run_completes_with_scored_product() -> None:
    _cleanup()
    _write_product_note()
    try:
        result = _run(*_base_args())
        assert result.returncode == 0, result.stderr
        assert "phase2h_status: dry_run_complete" in result.stdout
        assert f"final_decision: small_batch_test" in result.stdout
        assert f"product_id: {TEST_PRODUCT_ID}" in result.stdout
    finally:
        _cleanup()


# ── 3. dry-run creates artifact in tmp ───────────────────────────────────────

def test_dry_run_creates_decision_in_tmp() -> None:
    _cleanup()
    _write_product_note()
    try:
        _run(*_base_args())
        artifact = REVIEW_DIR / f"{DECISION_ID}.md"
        assert artifact.is_file(), "dry-run must create decision artifact in tmp/"
        text = artifact.read_text(encoding="utf-8")
        assert "type: decision" in text
        assert f"decision_id: {DECISION_ID}" in text
        assert "final_decision: small_batch_test" in text
    finally:
        _cleanup()


# ── 4. dry-run audit has correct frontmatter ─────────────────────────────────

def test_dry_run_creates_audit_with_correct_frontmatter() -> None:
    _cleanup()
    _write_product_note()
    try:
        _run(*_base_args())
        audit_path = REVIEW_DIR / f"audit-{REPORT_WEEK}.md"
        assert audit_path.is_file()
        text = audit_path.read_text(encoding="utf-8")
        assert "type: phase2h_audit" in text
        assert "mode: dry_run" in text
        assert f"product_id: {TEST_PRODUCT_ID}" in text
    finally:
        _cleanup()


# ── 5. dry-run does NOT write vault/decisions ─────────────────────────────────

def test_dry_run_does_not_write_vault_decisions() -> None:
    _cleanup()
    _write_product_note()
    vault_dest = VAULT_DECISIONS / f"{DECISION_ID}.md"
    try:
        _run(*_base_args())
        assert not vault_dest.exists(), "dry-run must not write to vault/decisions/"
    finally:
        _cleanup()


# ── 6. approved mode writes vault/decisions ───────────────────────────────────

def test_approve_writes_vault_decisions() -> None:
    _cleanup()
    _write_product_note()
    vault_dest = VAULT_DECISIONS / f"{DECISION_ID}.md"
    try:
        result = _run(*_base_args(), "--approve")
        assert result.returncode == 0, result.stderr
        assert "phase2h_status: success" in result.stdout
        assert vault_dest.is_file()
    finally:
        _cleanup()


# ── 7. approved artifact has required fields ──────────────────────────────────

def test_approve_artifact_has_required_fields() -> None:
    _cleanup()
    _write_product_note()
    vault_dest = VAULT_DECISIONS / f"{DECISION_ID}.md"
    try:
        _run(*_base_args(), "--approve")
        text = vault_dest.read_text(encoding="utf-8")
        assert "type: decision" in text
        assert "final_decision: small_batch_test" in text
        assert "score_decision: small_batch_test" in text
        assert "product_opportunity_score:" in text
        assert "confidence_score:" in text
        assert "missing_signal_count:" in text
        assert "compliance_status: pending" in text
        assert "status: draft" in text
    finally:
        _cleanup()


# ── 8. compatible conservative decision passes without override ───────────────

def test_compatible_decision_passes_without_override() -> None:
    """watchlist is more conservative than small_batch_test — allowed without override."""
    _cleanup()
    _write_product_note()
    try:
        result = _run(
            "--product-id", TEST_PRODUCT_ID,
            "--decision", "watchlist",
            "--report-week", REPORT_WEEK,
        )
        assert result.returncode == 0, result.stderr
        assert "phase2h_status: dry_run_complete" in result.stdout
    finally:
        _cleanup()


# ── 9. upgrade without override fails ────────────────────────────────────────

def test_upgrade_without_override_fails() -> None:
    """launch upgrades score_decision=small_batch_test — must fail without override."""
    _cleanup()
    _write_product_note()
    try:
        result = _run(
            "--product-id", TEST_PRODUCT_ID,
            "--decision", "launch",
            "--report-week", REPORT_WEEK,
        )
        assert result.returncode != 0
        assert "override-reason" in result.stderr
    finally:
        _cleanup()


# ── 10. upgrade with override passes ─────────────────────────────────────────

def test_upgrade_with_override_passes() -> None:
    _cleanup()
    _write_product_note()
    try:
        result = _run(
            "--product-id", TEST_PRODUCT_ID,
            "--decision", "launch",
            "--report-week", REPORT_WEEK,
            "--override-reason", "Demand spike confirmed by new trend signal",
        )
        assert result.returncode == 0, result.stderr
        assert "phase2h_status: dry_run_complete" in result.stdout
        artifact = REVIEW_DIR / f"dec-{TEST_PRODUCT_ID}-launch-{REPORT_WEEK}.md"
        # decision ID uses product_id + report_week only
        artifact = REVIEW_DIR / f"{DECISION_ID}.md"
        text = artifact.read_text(encoding="utf-8")
        assert "final_decision: launch" in text
        assert "override_reason:" in text
    finally:
        _cleanup()


# ── 11. reject score upgraded to watchlist without override fails ─────────────

def test_reject_score_upgraded_requires_override() -> None:
    """score_decision=reject → deciding watchlist is an upgrade, must need override."""
    _cleanup()
    fm = {**SCORED_FRONTMATTER, "score_decision": "reject", "product_opportunity_score": 50.0}
    _write_product_note(frontmatter=fm)
    try:
        result = _run(
            "--product-id", TEST_PRODUCT_ID,
            "--decision", "watchlist",
            "--report-week", REPORT_WEEK,
        )
        assert result.returncode != 0
        assert "override-reason" in result.stderr
    finally:
        _cleanup()


# ── 12. status draft source fails ────────────────────────────────────────────

def test_rejects_when_status_not_scored() -> None:
    _cleanup()
    fm = {**SCORED_FRONTMATTER, "status": "draft"}
    _write_product_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "scored" in result.stderr
    finally:
        _cleanup()


# ── 13. missing enriched fields fails ────────────────────────────────────────

def test_rejects_when_enriched_fields_missing() -> None:
    _cleanup()
    fm = {k: v for k, v in SCORED_FRONTMATTER.items() if k != "product_opportunity_score"}
    _write_product_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "product_opportunity_score" in result.stderr
    finally:
        _cleanup()


# ── 14. duplicate decision fails, no overwrite ────────────────────────────────

def test_duplicate_decision_fails_without_overwrite() -> None:
    _cleanup()
    _write_product_note()
    existing = REVIEW_DIR / f"{DECISION_ID}.md"
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    existing.write_text("existing content", encoding="utf-8")
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "already exists" in result.stderr
        assert existing.read_text(encoding="utf-8") == "existing content"
    finally:
        _cleanup()
        existing.unlink(missing_ok=True)


# ── 15. bash wrapper fails when ENABLE_AUTOPUBLISH=true ──────────────────────

def test_bash_wrapper_fails_when_autopublish_true() -> None:
    result = _run_wrapper(
        TEST_PRODUCT_ID,
        "small_batch_test",
        REPORT_WEEK,
        env={**os.environ, "ENABLE_AUTOPUBLISH": "true"},
    )
    assert result.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in result.stderr
