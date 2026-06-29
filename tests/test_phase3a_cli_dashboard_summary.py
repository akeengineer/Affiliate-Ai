from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_SCRIPT = REPO_ROOT / "scripts/dev/dashboard_summary.py"
BASH_WRAPPER = REPO_ROOT / "scripts/dev/run_phase3a_dashboard_summary.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/015-phase3a-cli-dashboard-summary.md"

PHASE2E_ROOT = REPO_ROOT / "tmp/phase2e-import-score-report"
SCORES_DIR = PHASE2E_ROOT / "scores"
HERMES_DIR = REPO_ROOT / "tmp/phase2f-hermes"
GOVERNANCE_DIR = REPO_ROOT / "tmp/phase2j-hermes-governance"
DASHBOARD_DIR = REPO_ROOT / "tmp/phase3a-dashboard"
VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

PRODUCT_ID = "pytest-phase3a-test"
WEEK = "2099-W01"

ANCHOR_PATH = SCORES_DIR / f"{PRODUCT_ID}.json"
WEEKLY_PATH = PHASE2E_ROOT / f"weekly-report-{WEEK}.md"
HERMES_PATH = HERMES_DIR / f"operational-summary-{WEEK}.md"
GOVERNANCE_PATH = GOVERNANCE_DIR / f"governance-summary-{WEEK}.md"
DASHBOARD_PATH = DASHBOARD_DIR / f"dashboard-{PRODUCT_ID}-{WEEK}.md"
VAULT_PRODUCT_PATH = VAULT_PRODUCTS_DIR / f"{PRODUCT_ID}.md"
VAULT_DECISION_PATH = VAULT_DECISIONS_DIR / f"dec-{PRODUCT_ID}-{WEEK}.md"

REQUIRED_FIELDS = (
    "product_id",
    "product_name",
    "product_opportunity_score",
    "score_decision",
    "confidence_score",
    "report_status",
    "hermes_summary_status",
    "governance_summary_status",
    "promote_status",
    "decision_status",
    "finalization_status",
    "next_allowed_action",
)

PRIVATE_VAULT_PATHS = (
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
)
AFFILIATE_URL_PATTERNS = (
    "aff=",
    "affiliate=",
    "tag=",
    "partner=",
    "sp_atk=",
    "bit.ly",
    "amzn.to",
    "shopee.link",
)
CONTENT_MARKERS = (
    "content_draft",
    "campaign_copy",
    "tiktok_script",
    "hook_text",
    "blog_post",
    "autopublish",
)


def _write_anchor() -> None:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "product_id": PRODUCT_ID,
        "product_name": "Pytest Phase3A Widget",
        "marketplace": "TikTok Shop",
        "currency": "USD",
        "product_opportunity_score": 77.65,
        "score_decision": "small_batch_test",
        "confidence_score": 100,
        "missing_signal_count": 0,
        "missing_signals": [],
    }
    ANCHOR_PATH.write_text(json.dumps(payload), encoding="utf-8")


def _write_weekly() -> None:
    PHASE2E_ROOT.mkdir(parents=True, exist_ok=True)
    WEEKLY_PATH.write_text(
        "---\n"
        "type: weekly_report\n"
        f"report_id: weekly-report-{WEEK}\n"
        f"report_week: {WEEK}\n"
        "candidate_count: 1\n"
        "status: generated\n"
        "---\n\n# Weekly Report\n",
        encoding="utf-8",
    )


def _write_hermes() -> None:
    HERMES_DIR.mkdir(parents=True, exist_ok=True)
    HERMES_PATH.write_text(
        "---\n"
        "type: hermes_operational_summary\n"
        f"report_week: {WEEK}\n"
        "status: complete\n"
        "---\n\n# Hermes Operational Summary\n",
        encoding="utf-8",
    )


def _write_governance(
    *,
    promoted_status: str = "dry_run_not_promoted",
    decision_status: str = "not_executed",
    finalization_status: str = "not_executed",
    next_allowed_action: str = "Promote candidate via Phase 2G approval gate",
) -> None:
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)
    GOVERNANCE_PATH.write_text(
        "---\n"
        "type: hermes_governance_summary\n"
        f"report_week: {WEEK}\n"
        f"product_id: {PRODUCT_ID}\n"
        "score_decision: small_batch_test\n"
        f"promoted_status: {promoted_status}\n"
        f"decision_status: {decision_status}\n"
        f"finalization_status: {finalization_status}\n"
        f'next_allowed_action: "{next_allowed_action}"\n'
        "status: complete\n"
        "---\n\n# Hermes Governance Summary\n",
        encoding="utf-8",
    )


def _write_vault_decision(status: str) -> None:
    VAULT_DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DECISION_PATH.write_text(
        "---\n"
        "type: decision\n"
        f"decision_id: dec-{PRODUCT_ID}-{WEEK}\n"
        f"product_id: {PRODUCT_ID}\n"
        "final_decision: small_batch_test\n"
        "compliance_status: approved\n"
        f"status: {status}\n"
        "created_at: '2099-01-01T00:00:00Z'\n"
        "updated_at: '2099-01-01T00:00:00Z'\n"
        "---\n\n# Decision\n",
        encoding="utf-8",
    )


def _cleanup_all() -> None:
    for path in (
        ANCHOR_PATH,
        WEEKLY_PATH,
        HERMES_PATH,
        GOVERNANCE_PATH,
        DASHBOARD_PATH,
        VAULT_PRODUCT_PATH,
        VAULT_DECISION_PATH,
    ):
        path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _clean():
    _cleanup_all()
    yield
    _cleanup_all()


def _run_py(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DASHBOARD_SCRIPT), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_sh(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(BASH_WRAPPER), *extra_args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _assert_no_forbidden(text: str) -> None:
    import re

    for pattern in PRIVATE_VAULT_PATHS:
        assert pattern not in text, f"leaked private vault path: {pattern}"
    for pattern in AFFILIATE_URL_PATTERNS:
        assert pattern not in text, f"leaked affiliate url pattern: {pattern}"
    for pattern in CONTENT_MARKERS:
        assert pattern not in text, f"leaked content marker: {pattern}"
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
    assert not re.search(r"AKIA[A-Z0-9]{16}", text)
    assert not re.search(r"Bearer [A-Za-z0-9]{20,}", text)


# ── 1. artifacts exist and wrapper is executable ──────────────────────────────

def test_artifacts_exist_and_wrapper_executable() -> None:
    assert TASK_FILE.is_file()
    assert DASHBOARD_SCRIPT.is_file()
    assert BASH_WRAPPER.is_file()
    assert os.access(BASH_WRAPPER, os.X_OK)


# ── 2. happy path stdout has all 12 fields ────────────────────────────────────

def test_happy_path_stdout_has_all_fields() -> None:
    _write_anchor()
    _write_weekly()
    _write_hermes()
    _write_governance()
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    for field in REQUIRED_FIELDS:
        assert any(line.startswith(f"{field}:") for line in lines), f"missing field {field}"
    assert "phase3a_status: success" in result.stdout
    assert "report_status: generated" in result.stdout
    assert "hermes_summary_status: complete" in result.stdout
    assert "governance_summary_status: complete" in result.stdout


# ── 3. --write creates the dashboard artifact ─────────────────────────────────

def test_write_creates_artifact() -> None:
    _write_anchor()
    _write_governance()
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert DASHBOARD_PATH.is_file()
    assert "dashboard_path:" in result.stdout
    assert "phase3a_status: success" in result.stdout


# ── 4. artifact frontmatter type ──────────────────────────────────────────────

def test_artifact_has_expected_type() -> None:
    _write_anchor()
    _run_py("--product-id", PRODUCT_ID, "--week", WEEK, "--write")
    text = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert "type: phase3a_dashboard_summary" in text


# ── 5. degraded mode (missing 2F and 2J) ──────────────────────────────────────

def test_degraded_mode_missing_summaries() -> None:
    _write_anchor()  # only the anchor; no weekly/hermes/governance
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK)
    assert result.returncode == 0, result.stderr
    assert "report_status: missing" in result.stdout
    assert "hermes_summary_status: missing" in result.stdout
    assert "governance_summary_status: missing" in result.stdout
    assert "promote_status: unknown" in result.stdout
    assert "decision_status: unknown" in result.stdout
    assert "finalization_status: unknown" in result.stdout


# ── 6. missing score JSON exits non-zero ──────────────────────────────────────

def test_missing_score_json_exits_nonzero() -> None:
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK)
    assert result.returncode != 0
    assert "score JSON not found" in result.stderr


# ── 7. invalid product_id exits non-zero ──────────────────────────────────────

def test_invalid_product_id_exits_nonzero() -> None:
    result = _run_py("--product-id", "Invalid_ID", "--week", WEEK)
    assert result.returncode != 0
    assert "product-id must match" in result.stderr


# ── 8. invalid week exits non-zero ────────────────────────────────────────────

def test_invalid_week_exits_nonzero() -> None:
    result = _run_py("--product-id", PRODUCT_ID, "--week", "2099-W1")
    assert result.returncode != 0
    assert "week must match" in result.stderr


# ── 9-11. output and artifact are scrubbed ────────────────────────────────────

def test_output_and_artifact_are_clean() -> None:
    _write_anchor()
    _write_weekly()
    _write_hermes()
    _write_governance()
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    _assert_no_forbidden(result.stdout)
    _assert_no_forbidden(DASHBOARD_PATH.read_text(encoding="utf-8"))


# ── 12. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    _write_anchor()
    _write_governance()
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert not VAULT_PRODUCT_PATH.exists()
    assert not VAULT_DECISION_PATH.exists()


# ── 13. optional vault decision drives status without leaking path ─────────────

def test_vault_decision_complete_drives_status() -> None:
    _write_anchor()
    _write_governance()  # governance says not_executed; vault should win
    _write_vault_decision("complete")
    result = _run_py("--product-id", PRODUCT_ID, "--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert "decision_status: complete" in result.stdout
    assert "finalization_status: finalized" in result.stdout
    _assert_no_forbidden(result.stdout)
    _assert_no_forbidden(DASHBOARD_PATH.read_text(encoding="utf-8"))


# ── 14-15. wrapper guardrails ─────────────────────────────────────────────────

def test_wrapper_fails_on_autopublish() -> None:
    _write_anchor()
    env = {**os.environ, "ENABLE_AUTOPUBLISH": "true"}
    result = _run_sh(PRODUCT_ID, WEEK, env=env)
    assert result.returncode != 0
    assert "ENABLE_AUTOPUBLISH" in result.stderr


def test_wrapper_fails_on_openai_direct() -> None:
    _write_anchor()
    env = {**os.environ, "ENABLE_OPENAI_API_DIRECT": "true"}
    result = _run_sh(PRODUCT_ID, WEEK, env=env)
    assert result.returncode != 0
    assert "ENABLE_OPENAI_API_DIRECT" in result.stderr
