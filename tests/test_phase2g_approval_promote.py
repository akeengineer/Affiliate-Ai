from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMOTE_SCRIPT = REPO_ROOT / "scripts/dev/promote_product_candidates.py"
BASH_WRAPPER = REPO_ROOT / "scripts/dev/run_phase2g_approval_promote.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/010-phase2g-approval-promote-gate.md"
AUDIT_DIR = REPO_ROOT / "tmp" / "phase2g-approval-promote"
VAULT_PRODUCTS = REPO_ROOT / "vault" / "products"

# Test fixtures live under tmp/ so they pass the safe source check
TEST_SOURCE = REPO_ROOT / "tmp" / "pytest-phase2g-source"
TEST_PRODUCT_ID = "pytest-phase2g-test"

SAMPLE_FRONTMATTER: dict[str, Any] = {
    "type": "product_candidate",
    "product_id": TEST_PRODUCT_ID,
    "product_name": "Pytest Test Product",
    "marketplace": "TikTok Shop",
    "currency": "USD",
    "demand_score": 83,
    "trend_velocity_score": 79,
    "marketplace_rank_score": 76,
    "commission_score": 72,
    "content_fit_score": 81,
    "competition_gap_score": 69,
    "risk_score": 22,
    "status": "draft",
    "created_at": "2026-06-29T02:00:00Z",
    "updated_at": "2026-06-29T02:00:00Z",
}

SAMPLE_SCORE: dict[str, Any] = {
    "product_id": TEST_PRODUCT_ID,
    "product_name": "Pytest Test Product",
    "marketplace": "TikTok Shop",
    "currency": "USD",
    "product_opportunity_score": 77.65,
    "score_decision": "small_batch_test",
    "confidence_score": 100,
    "missing_signal_count": 0,
    "missing_signals": [],
    "component_scores": {},
    "note_refs": {},
}


def _make_source(
    *,
    frontmatter: dict[str, Any] = SAMPLE_FRONTMATTER,
    score: dict[str, Any] = SAMPLE_SCORE,
) -> Path:
    product_id = str(frontmatter["product_id"])
    shutil.rmtree(TEST_SOURCE, ignore_errors=True)
    products_dir = TEST_SOURCE / "products"
    scores_dir = TEST_SOURCE / "scores"
    products_dir.mkdir(parents=True)
    scores_dir.mkdir(parents=True)

    fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    note = f"---\n{fm_text}\n---\n\n# {frontmatter['product_name']}\n\n## Summary\n- Test note.\n"
    (products_dir / f"{product_id}.md").write_text(note, encoding="utf-8")
    (scores_dir / f"{product_id}.json").write_text(json.dumps(score), encoding="utf-8")
    return TEST_SOURCE


def _run(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PROMOTE_SCRIPT), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_wrapper(source_dir: str, report_week: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(BASH_WRAPPER), source_dir, report_week],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_phase2g_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMOTE_SCRIPT.is_file()
    assert BASH_WRAPPER.is_file()
    assert os.access(BASH_WRAPPER, os.X_OK)


def test_dry_run_completes_with_sample_source() -> None:
    shutil.rmtree(AUDIT_DIR, ignore_errors=True)
    _make_source()

    completed = _run(
        "--source-dir", str(TEST_SOURCE),
        "--report-week", "2026-W26",
    )

    assert completed.returncode == 0, completed.stderr
    assert "phase2g_status: dry_run_complete" in completed.stdout
    assert "validated_count: 1" in completed.stdout
    assert "promoted_count: 0" in completed.stdout


def test_dry_run_creates_audit_with_correct_frontmatter() -> None:
    shutil.rmtree(AUDIT_DIR, ignore_errors=True)
    _make_source()
    _run("--source-dir", str(TEST_SOURCE), "--report-week", "2026-W26")

    audit_path = AUDIT_DIR / "audit-2026-W26.md"
    assert audit_path.is_file()
    text = audit_path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "type: phase2g_audit" in text
    assert "mode: dry_run" in text
    assert "promoted_count: 0" in text
    assert "validated_count: 1" in text


def test_dry_run_does_not_write_vault_products() -> None:
    _make_source()
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.unlink(missing_ok=True)

    _run("--source-dir", str(TEST_SOURCE), "--report-week", "2026-W26")

    assert not dest.exists(), "dry-run must not write to vault/products/"


def test_approve_promotes_and_enriches_note() -> None:
    _make_source()
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.unlink(missing_ok=True)

    try:
        completed = _run(
            "--source-dir", str(TEST_SOURCE),
            "--report-week", "2026-W26",
            "--approve",
        )
        assert completed.returncode == 0, completed.stderr
        assert "phase2g_status: success" in completed.stdout
        assert "promoted_count: 1" in completed.stdout
        assert dest.is_file()
    finally:
        dest.unlink(missing_ok=True)


def test_approve_promoted_note_has_scored_status_and_score_fields() -> None:
    _make_source()
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.unlink(missing_ok=True)

    try:
        _run(
            "--source-dir", str(TEST_SOURCE),
            "--report-week", "2026-W26",
            "--approve",
        )
        text = dest.read_text(encoding="utf-8")
        assert "type: product_candidate" in text
        assert "status: scored" in text
        assert "product_opportunity_score:" in text
        assert "score_decision: small_batch_test" in text
        assert "confidence_score:" in text
        assert "missing_signal_count:" in text
        assert "last_scored_at:" in text
        # created_at must be preserved, updated_at must differ
        assert "created_at: '2026-06-29T02:00:00Z'" in text
        match = re.search(r"updated_at: (.+)", text)
        assert match and match.group(1).strip() != "'2026-06-29T02:00:00Z'"
    finally:
        dest.unlink(missing_ok=True)


def test_approve_fails_when_destination_exists() -> None:
    _make_source()
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.write_text("existing content", encoding="utf-8")

    try:
        completed = _run(
            "--source-dir", str(TEST_SOURCE),
            "--report-week", "2026-W26",
            "--approve",
        )
        assert completed.returncode != 0
        assert "already exists" in completed.stderr
        assert dest.read_text(encoding="utf-8") == "existing content"
    finally:
        dest.unlink(missing_ok=True)


def test_rejects_note_with_affiliate_url() -> None:
    fm = {**SAMPLE_FRONTMATTER, "product_url": "https://example.com/prod?aff=mycode123"}
    _make_source(frontmatter=fm)

    completed = _run(
        "--source-dir", str(TEST_SOURCE),
        "--report-week", "2026-W26",
    )

    assert completed.returncode != 0
    assert "affiliate tracking" in completed.stderr


def test_rejects_note_with_wrong_type() -> None:
    fm = {**SAMPLE_FRONTMATTER, "type": "weekly_report"}
    score = {**SAMPLE_SCORE}
    _make_source(frontmatter=fm, score=score)

    completed = _run(
        "--source-dir", str(TEST_SOURCE),
        "--report-week", "2026-W26",
    )

    assert completed.returncode != 0
    assert "product_candidate" in completed.stderr


def test_rejects_note_with_score_decision_reject() -> None:
    fm = {
        **SAMPLE_FRONTMATTER,
        "demand_score": 10,
        "trend_velocity_score": 10,
        "marketplace_rank_score": 10,
        "commission_score": 10,
        "content_fit_score": 10,
        "competition_gap_score": 10,
        "risk_score": 95,
    }
    score = {
        **SAMPLE_SCORE,
        "score_decision": "reject",
        "product_opportunity_score": 15.25,
    }
    _make_source(frontmatter=fm, score=score)
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.unlink(missing_ok=True)

    completed = _run(
        "--source-dir", str(TEST_SOURCE),
        "--report-week", "2026-W26",
        "--approve",
    )

    assert completed.returncode != 0
    assert "reject" in completed.stderr
    assert not dest.exists()


def test_bash_wrapper_dry_run_by_default() -> None:
    _make_source()
    dest = VAULT_PRODUCTS / f"{TEST_PRODUCT_ID}.md"
    dest.unlink(missing_ok=True)

    completed = _run_wrapper(str(TEST_SOURCE), "2026-W26", env=os.environ.copy())

    assert completed.returncode == 0, completed.stderr
    assert "phase2g_status: dry_run_complete" in completed.stdout
    assert not dest.exists()


def test_bash_wrapper_fails_when_autopublish_true() -> None:
    _make_source()

    completed = _run_wrapper(
        str(TEST_SOURCE),
        "2026-W26",
        env={**os.environ, "ENABLE_AUTOPUBLISH": "true"},
    )

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in completed.stderr
