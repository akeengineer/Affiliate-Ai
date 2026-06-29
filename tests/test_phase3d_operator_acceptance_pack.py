from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase3d_acceptance.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/018-phase3d-operator-acceptance-pack.md"
ACCEPTANCE_DOC = REPO_ROOT / "docs/ACCEPTANCE.md"
DEMO_DOC = REPO_ROOT / "docs/DEMO.md"

SAMPLE_CSV = "vault/samples/import/product-candidates.csv"
WEEK = "2026-W26"
PRODUCT_ID = "prod-laptop-stand"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

EXPECTED_ARTIFACTS = (
    REPO_ROOT / f"tmp/phase2e-import-score-report/scores/{PRODUCT_ID}.json",
    REPO_ROOT / f"tmp/phase2e-import-score-report/weekly-report-{WEEK}.md",
    REPO_ROOT / f"tmp/phase2f-hermes/operational-summary-{WEEK}.md",
    REPO_ROOT / f"tmp/phase2j-hermes-governance/governance-summary-{WEEK}.md",
    REPO_ROOT / f"tmp/phase3a-dashboard/dashboard-{PRODUCT_ID}-{WEEK}.md",
    REPO_ROOT / f"tmp/phase3b-portfolio-dashboard/portfolio-{WEEK}.md",
)

PASS_STEP_LINES = (
    "step: doctor -> PASS",
    "step: dry-run -> PASS",
    "step: product --write -> PASS",
    "step: portfolio --top 5 --write -> PASS",
)

PRIVATE_VAULT_PATHS = (
    "vault/products",
    "vault/decisions",
    "vault/trends",
    "vault/marketplace-signals",
    "vault/commissions",
    "vault/meetings",
    "vault/contents",
    "vault/compliance",
    "vault/reports",
    "vault/.obsidian",
)

HARD_GUARDRAILS = (
    "no database",
    "no FastAPI",
    "no UI",
    "no external APIs",
    "no affiliate content generation",
    "no autopublish",
    "no campaign launch",
    "no vault writes",
)


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


# ── 1-4. existence ────────────────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_wrapper_exists_and_executable() -> None:
    assert WRAPPER.is_file()
    assert os.access(WRAPPER, os.X_OK)


def test_acceptance_doc_exists() -> None:
    assert ACCEPTANCE_DOC.is_file()


def test_demo_doc_exists() -> None:
    assert DEMO_DOC.is_file()


# ── 5-6. happy path ───────────────────────────────────────────────────────────

def test_happy_path_success() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr
    assert "acceptance_status: success" in result.stdout


def test_happy_path_pass_steps() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr
    for line in PASS_STEP_LINES:
        assert line in result.stdout, f"missing step line: {line}"


# ── 7. artifacts present ──────────────────────────────────────────────────────

def test_happy_path_creates_artifacts() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr
    for artifact in EXPECTED_ARTIFACTS:
        assert artifact.is_file(), f"missing artifact: {artifact}"


# ── 8-9. no vault write ───────────────────────────────────────────────────────

def test_no_vault_write_snapshot() -> None:
    before = _vault_snapshot()
    result = _run()
    assert result.returncode == 0, result.stderr
    after = _vault_snapshot()
    assert before == after, f"vault changed: before={before} after={after}"


def test_output_reports_zero_vault_writes() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr
    assert "vault_products_writes: 0" in result.stdout
    assert "vault_decisions_writes: 0" in result.stdout


# ── 10-12. guardrail flags fail at doctor gate ────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT", "APPROVE_PROMOTE"])
def test_unsafe_flag_fails(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run(env=env)
    assert result.returncode != 0
    assert "acceptance_status: failed" in result.stdout


# ── 13-16. argument validation ────────────────────────────────────────────────

@pytest.mark.parametrize("args", [(SAMPLE_CSV,), (SAMPLE_CSV, WEEK)])
def test_wrong_arg_count(args: tuple[str, ...]) -> None:
    result = _run(*args)
    assert result.returncode != 0
    assert "Usage:" in result.stderr


def test_invalid_week() -> None:
    result = _run(SAMPLE_CSV, "2026-W2", PRODUCT_ID)
    assert result.returncode != 0
    assert "week must match" in result.stderr


def test_invalid_product_id() -> None:
    result = _run(SAMPLE_CSV, WEEK, "Bad_ID")
    assert result.returncode != 0
    assert "product_id must match" in result.stderr


def test_missing_csv() -> None:
    result = _run("vault/samples/import/does-not-exist.csv", WEEK, PRODUCT_ID)
    assert result.returncode != 0
    assert "csv_path does not exist" in result.stderr


# ── 17-22. static safety checks ───────────────────────────────────────────────

def test_static_calls_command_center() -> None:
    assert "command_center.sh" in WRAPPER.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "forbidden",
    [
        "run_phase2_full_dry_run.sh",
        "run_phase3a_dashboard_summary.sh",
        "run_phase3b_portfolio_dashboard.sh",
        "run_phase2g",
        "run_phase2h",
        "run_phase2i",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ],
)
def test_static_no_direct_or_approved_routes(forbidden: str) -> None:
    assert forbidden not in WRAPPER.read_text(encoding="utf-8"), f"references {forbidden}"


# ── 23. no private vault slash paths in output ────────────────────────────────

def test_output_has_no_vault_slash_paths() -> None:
    result = _run()
    assert result.returncode == 0, result.stderr
    combined = result.stdout + result.stderr
    for path in PRIVATE_VAULT_PATHS:
        assert path not in combined, f"output leaked vault path: {path}"


# ── 24-25. docs content ───────────────────────────────────────────────────────

def test_docs_mention_guardrails() -> None:
    acceptance = ACCEPTANCE_DOC.read_text(encoding="utf-8")
    for guardrail in HARD_GUARDRAILS:
        assert guardrail in acceptance, f"ACCEPTANCE.md missing guardrail: {guardrail}"
    assert "Phase 2G/2H/2I" in acceptance


def test_docs_mention_vault_diff_model() -> None:
    acceptance = ACCEPTANCE_DOC.read_text(encoding="utf-8").lower()
    assert "before" in acceptance and "after" in acceptance
    assert "diff" in acceptance
