from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMAND_CENTER = REPO_ROOT / "scripts/dev/command_center.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/017-phase3c-operator-command-center.md"

SAMPLE_CSV = "vault/samples/import/product-candidates.csv"
WEEK = "2026-W26"
PRODUCT_ID = "prod-laptop-stand"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"
PHASE3A_ARTIFACT = REPO_ROOT / f"tmp/phase3a-dashboard/dashboard-{PRODUCT_ID}-{WEEK}.md"
PHASE3B_ARTIFACT = REPO_ROOT / f"tmp/phase3b-portfolio-dashboard/portfolio-{WEEK}.md"

COMMAND_NAMES = ("help", "status", "doctor", "dry-run", "product", "portfolio")

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

REQUIRED_STATUS_KEYS = (
    "repo_root",
    "branch",
    "enable_autopublish",
    "enable_openai_api_direct",
    "approve_promote",
    "approve_decision",
    "approve_finalize",
    "phase2e_score_files",
    "phase2f_hermes_summaries",
    "phase2j_governance_summaries",
    "phase3a_dashboards",
    "phase3b_portfolios",
    "status_command",
)

REQUIRED_DOCTOR_CHECKS = (
    "check: run_phase2_full_dry_run.sh -> PASS",
    "check: run_phase3a_dashboard_summary.sh -> PASS",
    "check: run_phase3b_portfolio_dashboard.sh -> PASS",
    "check: dashboard_summary.py -> PASS",
    "check: portfolio_dashboard.py -> PASS",
    "check: ENABLE_AUTOPUBLISH safe -> PASS",
    "check: ENABLE_OPENAI_API_DIRECT safe -> PASS",
    "check: APPROVE_PROMOTE safe -> PASS",
    "check: APPROVE_DECISION safe -> PASS",
    "check: APPROVE_FINALIZE safe -> PASS",
)


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(COMMAND_CENTER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = [p.name for p in VAULT_PRODUCTS_DIR.iterdir()] if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = [p.name for p in VAULT_DECISIONS_DIR.iterdir()] if VAULT_DECISIONS_DIR.is_dir() else []
    return sorted(products), sorted(decisions)


# ── 1. existence + executable ─────────────────────────────────────────────────

def test_artifacts_exist_and_executable() -> None:
    assert TASK_FILE.is_file()
    assert COMMAND_CENTER.is_file()
    assert os.access(COMMAND_CENTER, os.X_OK)


# ── 2. help / no args / -h / --help ───────────────────────────────────────────

@pytest.mark.parametrize("args", [(), ("help",), ("-h",), ("--help",)])
def test_help_variants(args: tuple[str, ...]) -> None:
    result = _run(*args)
    assert result.returncode == 0, result.stderr
    for name in COMMAND_NAMES:
        assert name in result.stdout, f"help missing command {name}"


# ── 3. unknown command ────────────────────────────────────────────────────────

def test_unknown_command() -> None:
    result = _run("bogus-command")
    assert result.returncode != 0
    assert "Usage:" in result.stderr


# ── 4-5. status ───────────────────────────────────────────────────────────────

def test_status_keys_present() -> None:
    result = _run("status")
    assert result.returncode == 0, result.stderr
    for key in REQUIRED_STATUS_KEYS:
        assert any(line.startswith(f"{key}:") for line in result.stdout.splitlines()), f"missing {key}"
    assert "status_command: success" in result.stdout


def test_status_has_no_vault_paths() -> None:
    result = _run("status")
    assert result.returncode == 0, result.stderr
    for path in PRIVATE_VAULT_PATHS:
        assert path not in result.stdout, f"status leaked vault path: {path}"


# ── 6-7. doctor clean ─────────────────────────────────────────────────────────

def test_doctor_clean() -> None:
    env = {k: v for k, v in os.environ.items() if k not in (
        "ENABLE_AUTOPUBLISH",
        "ENABLE_OPENAI_API_DIRECT",
        "APPROVE_PROMOTE",
        "APPROVE_DECISION",
        "APPROVE_FINALIZE",
    )}
    result = _run("doctor", env=env)
    assert result.returncode == 0, result.stderr
    assert "doctor_status: success" in result.stdout
    for check in REQUIRED_DOCTOR_CHECKS:
        assert check in result.stdout, f"missing doctor check: {check}"


# ── 8-10. doctor unsafe flags ─────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT", "APPROVE_PROMOTE"])
def test_doctor_fails_on_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run("doctor", env=env)
    assert result.returncode != 0
    assert f"check: {flag} safe -> FAIL" in result.stdout
    assert "doctor_status: failed" in result.stdout


# ── 11. dry-run routing ───────────────────────────────────────────────────────

def test_dry_run_routes() -> None:
    result = _run("dry-run", SAMPLE_CSV, WEEK, PRODUCT_ID)
    assert result.returncode == 0, result.stderr
    assert "final_status: success" in result.stdout


# ── 12. product routing with missing id ───────────────────────────────────────

def test_product_missing_id_fails_downstream() -> None:
    result = _run("product", "no-such-product-xyz", WEEK)
    assert result.returncode != 0
    assert "score JSON not found" in result.stderr


# ── 13-14. product happy path (populate via dry-run first) ─────────────────────

def test_product_after_populate() -> None:
    populate = _run("dry-run", SAMPLE_CSV, WEEK, PRODUCT_ID)
    assert populate.returncode == 0, populate.stderr
    result = _run("product", PRODUCT_ID, WEEK)
    assert result.returncode == 0, result.stderr
    assert "phase3a_status: success" in result.stdout


def test_product_write_creates_artifact() -> None:
    populate = _run("dry-run", SAMPLE_CSV, WEEK, PRODUCT_ID)
    assert populate.returncode == 0, populate.stderr
    result = _run("product", PRODUCT_ID, WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert "phase3a_status: success" in result.stdout
    assert PHASE3A_ARTIFACT.is_file()


# ── 15-16. portfolio routing ──────────────────────────────────────────────────

def test_portfolio_routes() -> None:
    result = _run("portfolio", WEEK)
    assert result.returncode == 0, result.stderr
    assert "phase3b_status: success" in result.stdout


def test_portfolio_top_and_write() -> None:
    result = _run("portfolio", WEEK, "--top", "3", "--write")
    assert result.returncode == 0, result.stderr
    assert "top_n: 3" in result.stdout
    assert PHASE3B_ARTIFACT.is_file()


# ── 17-18. validation ─────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "args",
    [
        ("dry-run", SAMPLE_CSV, "2026-W2", PRODUCT_ID),
        ("product", PRODUCT_ID, "2026-W2"),
        ("portfolio", "2026-W2"),
    ],
)
def test_invalid_week(args: tuple[str, ...]) -> None:
    result = _run(*args)
    assert result.returncode != 0
    assert "week must match" in result.stderr


@pytest.mark.parametrize(
    "args",
    [
        ("dry-run", SAMPLE_CSV, WEEK, "Bad_ID"),
        ("product", "Bad_ID", WEEK),
    ],
)
def test_invalid_product_id(args: tuple[str, ...]) -> None:
    result = _run(*args)
    assert result.returncode != 0
    assert "product_id must match" in result.stderr


# ── 19. dry-run missing csv ───────────────────────────────────────────────────

def test_dry_run_missing_csv() -> None:
    result = _run("dry-run", "vault/samples/import/does-not-exist.csv", WEEK, PRODUCT_ID)
    assert result.returncode != 0
    assert "csv_path does not exist" in result.stderr


# ── 20-21. action guardrails ──────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT"])
def test_action_commands_fail_on_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    for args in (
        ("dry-run", SAMPLE_CSV, WEEK, PRODUCT_ID),
        ("product", PRODUCT_ID, WEEK),
        ("portfolio", WEEK),
    ):
        result = _run(*args, env=env)
        assert result.returncode != 0, f"{args} should fail with {flag}=true"
        assert flag in result.stderr


# ── 22-23. static safety checks ───────────────────────────────────────────────

def test_no_approved_workflow_references() -> None:
    text = COMMAND_CENTER.read_text(encoding="utf-8")
    for forbidden in ("run_phase2g", "run_phase2h", "run_phase2i"):
        assert forbidden not in text, f"references approved wrapper: {forbidden}"


def test_no_vault_write_script_references() -> None:
    text = COMMAND_CENTER.read_text(encoding="utf-8")
    for forbidden in (
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ):
        assert forbidden not in text, f"references vault-write script: {forbidden}"


# ── 24. no vault write after any command ──────────────────────────────────────

def test_no_vault_write() -> None:
    before = _vault_snapshot()
    _run("status")
    _run("doctor")
    _run("dry-run", SAMPLE_CSV, WEEK, PRODUCT_ID)
    _run("product", PRODUCT_ID, WEEK, "--write")
    _run("portfolio", WEEK, "--write")
    after = _vault_snapshot()
    assert before == after, f"vault changed: before={before} after={after}"
    assert after == ([], []), f"unexpected vault files: {after}"
