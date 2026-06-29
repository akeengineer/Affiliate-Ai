from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FINALIZE_SCRIPT = REPO_ROOT / "scripts/dev/finalize_decision.py"
BASH_WRAPPER = REPO_ROOT / "scripts/dev/run_phase2i_decision_finalization.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/012-phase2i-decision-finalization-gate.md"
AUDIT_DIR = REPO_ROOT / "tmp" / "phase2i-decision-finalization"
VAULT_DECISIONS = REPO_ROOT / "vault" / "decisions"

TEST_PRODUCT_ID = "pytest-phase2i-test"
DECISION_ID = f"dec-{TEST_PRODUCT_ID}-2026-W26"

DRAFT_FRONTMATTER: dict[str, Any] = {
    "type": "decision",
    "decision_id": DECISION_ID,
    "product_id": TEST_PRODUCT_ID,
    "final_decision": "small_batch_test",
    "score_decision": "small_batch_test",
    "product_opportunity_score": 77.65,
    "confidence_score": 100,
    "missing_signal_count": 0,
    "vote_count": 0,
    "compliance_status": "approved",
    "override_reason": None,
    "decision_summary": "score_decision=small_batch_test confirmed",
    "required_actions": [],
    "status": "draft",
    "created_at": "2026-06-29T02:00:00Z",
    "updated_at": "2026-06-29T03:00:00Z",
}

BODY = (
    "\n# Decision — pytest-phase2i-test\n\n## Summary\n\n"
    "Product: pytest-phase2i-test\nFinal decision: small_batch_test\n\n"
    "## Notes\n\n(empty)\n"
)

REASON = "Compliance approved; manual review completed"


def _write_decision_note(frontmatter: dict[str, Any] = DRAFT_FRONTMATTER) -> Path:
    VAULT_DECISIONS.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    note = f"---\n{fm_text}\n---\n{BODY}"
    path = VAULT_DECISIONS / f"{DECISION_ID}.md"
    path.write_text(note, encoding="utf-8")
    return path


def _cleanup() -> None:
    (VAULT_DECISIONS / f"{DECISION_ID}.md").unlink(missing_ok=True)
    (AUDIT_DIR / f"audit-{DECISION_ID}.md").unlink(missing_ok=True)


def _run(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(FINALIZE_SCRIPT), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_wrapper(decision_id: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(BASH_WRAPPER), decision_id],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _base_args() -> list[str]:
    return ["--decision-id", DECISION_ID, "--finalization-reason", REASON]


# ── 1. artifacts exist ────────────────────────────────────────────────────────

def test_phase2i_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert FINALIZE_SCRIPT.is_file()
    assert BASH_WRAPPER.is_file()
    assert os.access(BASH_WRAPPER, os.X_OK)


# ── 2. dry-run completes ──────────────────────────────────────────────────────

def test_dry_run_completes_with_draft_decision() -> None:
    _cleanup()
    _write_decision_note()
    try:
        result = _run(*_base_args())
        assert result.returncode == 0, result.stderr
        assert "phase2i_status: dry_run_complete" in result.stdout
        assert f"decision_id: {DECISION_ID}" in result.stdout
        assert "compliance_status: approved" in result.stdout
    finally:
        _cleanup()


# ── 3. dry-run audit frontmatter ──────────────────────────────────────────────

def test_dry_run_writes_audit() -> None:
    _cleanup()
    _write_decision_note()
    try:
        _run(*_base_args())
        audit = AUDIT_DIR / f"audit-{DECISION_ID}.md"
        assert audit.is_file()
        text = audit.read_text(encoding="utf-8")
        assert "type: phase2i_audit" in text
        assert "mode: dry_run" in text
        assert "phase2i_status: dry_run_complete" in text
    finally:
        _cleanup()


# ── 4. dry-run does not mutate vault ──────────────────────────────────────────

def test_dry_run_does_not_mutate_vault() -> None:
    _cleanup()
    path = _write_decision_note()
    original = path.read_text(encoding="utf-8")
    try:
        _run(*_base_args())
        assert path.read_text(encoding="utf-8") == original
        assert "status: draft" in path.read_text(encoding="utf-8")
        assert "status: complete" not in path.read_text(encoding="utf-8")
    finally:
        _cleanup()


# ── 5. approved updates status to complete ────────────────────────────────────

def test_approve_updates_status_complete() -> None:
    _cleanup()
    path = _write_decision_note()
    try:
        result = _run(*_base_args(), "--approve")
        assert result.returncode == 0, result.stderr
        assert "phase2i_status: success" in result.stdout
        text = path.read_text(encoding="utf-8")
        assert "status: complete" in text
        assert "status: draft" not in text
    finally:
        _cleanup()


# ── 6. approved writes finalized_at and finalization_reason ───────────────────

def test_approve_writes_finalized_fields() -> None:
    _cleanup()
    path = _write_decision_note()
    try:
        _run(*_base_args(), "--approve")
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])
        assert fm["finalized_at"] and fm["finalized_at"] != "(dry-run)"
        assert fm["finalization_reason"] == REASON
        assert fm["status"] == "complete"
    finally:
        _cleanup()


# ── 7. approved preserves final_decision and body byte-for-byte ───────────────

def test_approve_preserves_final_decision_and_body() -> None:
    _cleanup()
    path = _write_decision_note()
    try:
        _run(*_base_args(), "--approve")
        text = path.read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("---")[1])
        assert fm["final_decision"] == "small_batch_test"
        assert text.endswith(BODY), "markdown body must be preserved byte-for-byte"
    finally:
        _cleanup()


# ── 8. status complete source fails (no re-finalize) ──────────────────────────

def test_status_complete_source_fails() -> None:
    _cleanup()
    fm = {**DRAFT_FRONTMATTER, "status": "complete"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args(), "--approve")
        assert result.returncode != 0
        assert "draft" in result.stderr
    finally:
        _cleanup()


# ── 9. type not decision fails ────────────────────────────────────────────────

def test_type_not_decision_fails() -> None:
    _cleanup()
    fm = {**DRAFT_FRONTMATTER, "type": "product_candidate"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "type must be decision" in result.stderr
    finally:
        _cleanup()


# ── 10-12. compliance_status gate ─────────────────────────────────────────────

def test_compliance_pending_fails() -> None:
    _cleanup()
    fm = {**DRAFT_FRONTMATTER, "compliance_status": "pending"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "compliance_status" in result.stderr
    finally:
        _cleanup()


def test_compliance_needs_review_fails() -> None:
    _cleanup()
    fm = {**DRAFT_FRONTMATTER, "compliance_status": "needs_review"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "compliance_status" in result.stderr
    finally:
        _cleanup()


def test_compliance_blocked_fails() -> None:
    _cleanup()
    fm = {**DRAFT_FRONTMATTER, "compliance_status": "blocked"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "compliance_status" in result.stderr
    finally:
        _cleanup()


# ── 13. missing required field fails and names it ─────────────────────────────

def test_missing_required_field_fails() -> None:
    _cleanup()
    fm = {k: v for k, v in DRAFT_FRONTMATTER.items() if k != "score_decision"}
    _write_decision_note(frontmatter=fm)
    try:
        result = _run(*_base_args())
        assert result.returncode != 0
        assert "score_decision" in result.stderr
    finally:
        _cleanup()


# ── 14. empty finalization_reason fails ───────────────────────────────────────

def test_empty_finalization_reason_fails() -> None:
    _cleanup()
    _write_decision_note()
    try:
        result = _run("--decision-id", DECISION_ID, "--finalization-reason", "   ")
        assert result.returncode != 0
        assert "finalization_reason" in result.stderr
    finally:
        _cleanup()


# ── 15. affiliate pattern in reason fails ─────────────────────────────────────

def test_affiliate_pattern_reason_fails() -> None:
    _cleanup()
    _write_decision_note()
    try:
        result = _run(
            "--decision-id", DECISION_ID,
            "--finalization-reason", "approved, see amzn.to/xyz",
        )
        assert result.returncode != 0
        assert "affiliate" in result.stderr
    finally:
        _cleanup()


# ── 16. secret pattern in reason fails ────────────────────────────────────────

def test_secret_pattern_reason_fails() -> None:
    _cleanup()
    _write_decision_note()
    try:
        result = _run(
            "--decision-id", DECISION_ID,
            "--finalization-reason", "key is sk-ABCDEFGHIJKLMNOPQRSTUVWX",
        )
        assert result.returncode != 0
        assert "secret" in result.stderr
    finally:
        _cleanup()


# ── 17. nonexistent decision-id fails ─────────────────────────────────────────

def test_nonexistent_decision_id_fails() -> None:
    missing_id = "dec-pytest-phase2i-missing-2026-W26"
    (VAULT_DECISIONS / f"{missing_id}.md").unlink(missing_ok=True)
    result = _run("--decision-id", missing_id, "--finalization-reason", REASON)
    assert result.returncode != 0
    assert "not found" in result.stderr


# ── 18. invalid decision-id format fails ──────────────────────────────────────

def test_invalid_decision_id_fails() -> None:
    result = _run("--decision-id", "not-a-valid-id", "--finalization-reason", REASON)
    assert result.returncode != 0
    assert "decision-id must match" in result.stderr


# ── 19. bash wrapper fails when ENABLE_AUTOPUBLISH=true ────────────────────────

def test_bash_wrapper_fails_when_autopublish_true() -> None:
    result = _run_wrapper(
        DECISION_ID,
        env={**os.environ, "FINALIZATION_REASON": REASON, "ENABLE_AUTOPUBLISH": "true"},
    )
    assert result.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in result.stderr


# ── 20. bash wrapper defaults to dry-run ──────────────────────────────────────

def test_bash_wrapper_defaults_to_dry_run() -> None:
    _cleanup()
    path = _write_decision_note()
    try:
        result = _run_wrapper(
            DECISION_ID,
            env={**os.environ, "FINALIZATION_REASON": REASON},
        )
        assert result.returncode == 0, result.stderr
        assert "phase2i_status: dry_run_complete" in result.stdout
        assert "status: draft" in path.read_text(encoding="utf-8")
    finally:
        _cleanup()
