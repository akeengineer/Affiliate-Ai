from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts/dev/build_ui_mock.py"
WRAPPER = REPO_ROOT / "scripts/dev/run_phase4a_ui_mock.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/020-phase4a-local-readonly-ui-mock.md"
UI_MOCK_DOC = REPO_ROOT / "docs/UI_MOCK.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PORTFOLIO_DIR = REPO_ROOT / "tmp/phase3b-portfolio-dashboard"
DASHBOARD_DIR = REPO_ROOT / "tmp/phase3a-dashboard"
SCORES_DIR = REPO_ROOT / "tmp/phase2e-import-score-report/scores"
OUT = REPO_ROOT / "tmp/phase4a-ui/index.html"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

WEEK = "2099-W04"
TEST_IDS = ("pytest-phase4a-a", "pytest-phase4a-b")

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
AFFILIATE_URL_PATTERNS = ("aff=", "affiliate=", "tag=", "partner=", "sp_atk=", "bit.ly", "amzn.to", "shopee.link")
CONTENT_MARKERS = ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post", "autopublish")


def _write_portfolio(**counts: int) -> None:
    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["---", "type: phase3b_portfolio_dashboard", f"report_week: {WEEK}"]
    for key in (
        "total_products",
        "launch_count",
        "small_batch_test_count",
        "watchlist_count",
        "reject_count",
        "top_n",
        "promoted_count",
        "decision_draft_count",
        "decision_complete_count",
    ):
        lines.append(f"{key}: {counts.get(key, 0)}")
    lines += ["status: complete", "---", "", "# portfolio", ""]
    (PORTFOLIO_DIR / f"portfolio-{WEEK}.md").write_text("\n".join(lines), encoding="utf-8")


def _write_dashboard(product_id: str, *, name: str, score: float, decision: str, confidence: int) -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    text = (
        "---\n"
        "type: phase3a_dashboard_summary\n"
        f"report_week: {WEEK}\n"
        f"product_id: {product_id}\n"
        f"product_name: {name}\n"
        f"product_opportunity_score: {score}\n"
        f"score_decision: {decision}\n"
        f"confidence_score: {confidence}\n"
        "report_status: generated\n"
        "hermes_summary_status: complete\n"
        "governance_summary_status: complete\n"
        "promote_status: dry_run_not_promoted\n"
        "decision_status: not_executed\n"
        "finalization_status: not_executed\n"
        'next_allowed_action: "Promote candidate through Phase 2G approval gate"\n'
        'generated_at: "2099-01-01T00:00:00Z"\n'
        "status: complete\n"
        "---\n\n# dashboard\n"
    )
    (DASHBOARD_DIR / f"dashboard-{product_id}-{WEEK}.md").write_text(text, encoding="utf-8")


def _cleanup() -> None:
    OUT.unlink(missing_ok=True)
    (PORTFOLIO_DIR / f"portfolio-{WEEK}.md").unlink(missing_ok=True)
    for product_id in TEST_IDS:
        (DASHBOARD_DIR / f"dashboard-{product_id}-{WEEK}.md").unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _isolate(tmp_path_factory):
    """Stash real score JSON so the fallback glob only sees test fixtures."""
    stash = tmp_path_factory.mktemp("scores_stash")
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    for path in list(SCORES_DIR.glob("*.json")):
        shutil.move(str(path), str(stash / path.name))
    _cleanup()
    try:
        yield
    finally:
        for path in list(SCORES_DIR.glob("*.json")):
            path.unlink()
        for path in stash.glob("*.json"):
            shutil.move(str(path), str(SCORES_DIR / path.name))
        _cleanup()


def _run_build(week: str = WEEK) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--week", week],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _run_wrapper(week: str = WEEK, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER), week],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


# ── 1-6. existence + syntax ───────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_build_script_exists() -> None:
    assert BUILD_SCRIPT.is_file()


def test_wrapper_exists_and_executable() -> None:
    assert WRAPPER.is_file()
    assert os.access(WRAPPER, os.X_OK)


def test_ui_mock_doc_exists() -> None:
    assert UI_MOCK_DOC.is_file()


def test_gitignore_includes_phase4a() -> None:
    assert "tmp/phase4a-ui/" in GITIGNORE.read_text(encoding="utf-8")


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 7-8. build + structure ────────────────────────────────────────────────────

def test_build_creates_html() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    result = _run_build()
    assert result.returncode == 0, result.stderr
    assert OUT.is_file()
    assert "phase4a_status: success" in result.stdout


def test_html_structure() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    _run_build()
    html = OUT.read_text(encoding="utf-8")
    for marker in ("<!doctype html", "<head", "<title", "<body", "Portfolio overview", "Top products", "Per-product", "READ-ONLY MOCK"):
        assert marker in html, f"missing structural marker: {marker}"


# ── 9. self-contained ─────────────────────────────────────────────────────────

def test_html_self_contained() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    _run_build()
    html = OUT.read_text(encoding="utf-8")
    for forbidden in ("http://", "https://", "<script", "fetch(", "XMLHttpRequest", "import(", "<link "):
        assert forbidden not in html, f"HTML is not self-contained: {forbidden}"


# ── 10. fixture values present ────────────────────────────────────────────────

def test_html_contains_fixture_values() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    _run_build()
    html = OUT.read_text(encoding="utf-8")
    for token in ("pytest-phase4a-a", "Widget A", "88", "launch", "95"):
        assert token in html, f"missing fixture value: {token}"


# ── 11. injection escaped ─────────────────────────────────────────────────────

def test_html_escapes_injection() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="<script>alert(1)</script>", score=88, decision="launch", confidence=95)
    result = _run_build()
    assert result.returncode == 0, result.stderr
    html = OUT.read_text(encoding="utf-8")
    assert "&lt;script&gt;" in html
    assert "<script>alert(1)" not in html


# ── 12. degraded mode ─────────────────────────────────────────────────────────

def test_degraded_mode() -> None:
    result = _run_build()
    assert result.returncode == 0, result.stderr
    html = OUT.read_text(encoding="utf-8")
    assert f"no artifacts for {WEEK}" in html


# ── 13. invalid week ──────────────────────────────────────────────────────────

def test_invalid_week() -> None:
    result = _run_build("2099-W4")
    assert result.returncode != 0
    assert "week must match" in result.stderr


# ── 14-15. wrapper guardrails ─────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT"])
def test_wrapper_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run_wrapper(env=env)
    assert result.returncode != 0
    assert flag in result.stderr


# ── 16. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    before = _vault_snapshot()
    result = _run_build()
    assert result.returncode == 0, result.stderr
    after = _vault_snapshot()
    assert before == after, f"vault changed: before={before} after={after}"


# ── 17-18. scrubbing ──────────────────────────────────────────────────────────

def test_html_has_no_forbidden_content() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    _run_build()
    html = OUT.read_text(encoding="utf-8")
    for path in PRIVATE_VAULT_PATHS:
        assert path not in html, f"leaked vault path: {path}"
    for pattern in AFFILIATE_URL_PATTERNS:
        assert pattern not in html, f"leaked affiliate pattern: {pattern}"
    for marker in CONTENT_MARKERS:
        assert marker not in html, f"leaked content marker: {marker}"
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", html)
    assert not re.search(r"AKIA[A-Z0-9]{16}", html)
    assert not re.search(r"Bearer [A-Za-z0-9]{20,}", html)


# ── 19. idempotent ────────────────────────────────────────────────────────────

def test_idempotent_build() -> None:
    _write_portfolio(total_products=1, launch_count=1, top_n=10)
    _write_dashboard("pytest-phase4a-a", name="Widget A", score=88, decision="launch", confidence=95)
    first = _run_build()
    assert first.returncode == 0, first.stderr
    second = _run_build()
    assert second.returncode == 0, second.stderr
    assert OUT.is_file()


# ── 20-21. static safety ──────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "forbidden",
    [
        "run_phase2g",
        "run_phase2h",
        "run_phase2i",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ],
)
def test_static_no_approved_references(forbidden: str) -> None:
    build_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    assert forbidden not in build_text, f"build script references {forbidden}"
    assert forbidden not in wrapper_text, f"wrapper references {forbidden}"


# ── 22. docs content ──────────────────────────────────────────────────────────

def test_docs_mention_constraints() -> None:
    text = UI_MOCK_DOC.read_text(encoding="utf-8")
    for token in ("no server", "no API", "no database", "no external resources", "no vault writes"):
        assert token in text, f"UI_MOCK.md missing: {token}"
