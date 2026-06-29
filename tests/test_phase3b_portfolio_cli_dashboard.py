from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_SCRIPT = REPO_ROOT / "scripts/dev/portfolio_dashboard.py"
BASH_WRAPPER = REPO_ROOT / "scripts/dev/run_phase3b_portfolio_dashboard.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/016-phase3b-portfolio-cli-dashboard.md"

SCORES_DIR = REPO_ROOT / "tmp/phase2e-import-score-report/scores"
PHASE3A_DIR = REPO_ROOT / "tmp/phase3a-dashboard"
PORTFOLIO_DIR = REPO_ROOT / "tmp/phase3b-portfolio-dashboard"
VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

WEEK = "2099-W02"
PORTFOLIO_PATH = PORTFOLIO_DIR / f"portfolio-{WEEK}.md"

COUNT_FIELDS = (
    "report_week",
    "total_products",
    "launch_count",
    "small_batch_test_count",
    "watchlist_count",
    "reject_count",
    "top_n",
    "skipped_count",
    "phase3a_artifact_count",
    "promoted_count",
    "decision_draft_count",
    "decision_complete_count",
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

# Test product ids (kept distinct so vault/phase3a fixtures can be cleaned up).
TEST_IDS = (
    "pytest-phase3b-a",
    "pytest-phase3b-b",
    "pytest-phase3b-c",
    "pytest-phase3b-d",
    "pytest-phase3b-e",
)


def _write_score(
    product_id: str,
    *,
    score: float,
    decision: str,
    name: str | None = None,
    confidence: int = 100,
    extra: dict | None = None,
) -> None:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "product_id": product_id,
        "product_name": name or f"Name {product_id}",
        "marketplace": "TikTok Shop",
        "currency": "USD",
        "product_opportunity_score": score,
        "score_decision": decision,
        "confidence_score": confidence,
    }
    if extra:
        payload.update(extra)
    (SCORES_DIR / f"{product_id}.json").write_text(json.dumps(payload), encoding="utf-8")


def _write_raw_score(filename: str, text: str) -> None:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    (SCORES_DIR / filename).write_text(text, encoding="utf-8")


def _write_phase3a(product_id: str) -> None:
    PHASE3A_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE3A_DIR / f"dashboard-{product_id}-{WEEK}.md").write_text(
        "---\ntype: phase3a_dashboard_summary\n"
        f"report_week: {WEEK}\nproduct_id: {product_id}\nstatus: complete\n---\n",
        encoding="utf-8",
    )


def _write_vault_product(product_id: str) -> None:
    VAULT_PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
    (VAULT_PRODUCTS_DIR / f"{product_id}.md").write_text(
        "---\ntype: product_candidate\n"
        f"product_id: {product_id}\nstatus: active\n---\n",
        encoding="utf-8",
    )


def _write_vault_decision(product_id: str, status: str) -> None:
    VAULT_DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    (VAULT_DECISIONS_DIR / f"dec-{product_id}-{WEEK}.md").write_text(
        "---\ntype: decision\n"
        f"decision_id: dec-{product_id}-{WEEK}\nproduct_id: {product_id}\n"
        f"status: {status}\n---\n",
        encoding="utf-8",
    )


def _cleanup_satellite() -> None:
    PORTFOLIO_PATH.unlink(missing_ok=True)
    for product_id in TEST_IDS:
        (PHASE3A_DIR / f"dashboard-{product_id}-{WEEK}.md").unlink(missing_ok=True)
        (VAULT_PRODUCTS_DIR / f"{product_id}.md").unlink(missing_ok=True)
        (VAULT_DECISIONS_DIR / f"dec-{product_id}-{WEEK}.md").unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _isolate_scores(tmp_path_factory):
    """Stash any real score files so the portfolio glob only sees test files."""
    stash = tmp_path_factory.mktemp("scores_stash")
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    for path in list(SCORES_DIR.iterdir()):
        if path.is_file():
            shutil.move(str(path), str(stash / path.name))
    _cleanup_satellite()
    try:
        yield
    finally:
        for path in list(SCORES_DIR.iterdir()):
            if path.is_file():
                path.unlink()
        for path in stash.iterdir():
            shutil.move(str(path), str(SCORES_DIR / path.name))
        _cleanup_satellite()


def _run_py(*extra_args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PORTFOLIO_SCRIPT), *extra_args],
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


def _field(stdout: str, key: str) -> str:
    for line in stdout.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"field {key} not found in stdout")


def _top_product_order(stdout: str) -> list[str]:
    lines = stdout.splitlines()
    order: list[str] = []
    in_top = False
    for line in lines:
        if line.startswith("rank | product_id"):
            in_top = True
            continue
        if in_top:
            if not line.strip() or line.startswith("portfolio_path:") or line.startswith("phase3b_status:"):
                break
            order.append(line.split("|")[1].strip())
    return order


def _assert_no_forbidden(text: str) -> None:
    for pattern in PRIVATE_VAULT_PATHS:
        assert pattern not in text, f"leaked private vault path: {pattern}"
    for pattern in AFFILIATE_URL_PATTERNS:
        assert pattern not in text, f"leaked affiliate url pattern: {pattern}"
    for pattern in CONTENT_MARKERS:
        assert pattern not in text, f"leaked content marker: {pattern}"
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
    assert not re.search(r"AKIA[A-Z0-9]{16}", text)
    assert not re.search(r"Bearer [A-Za-z0-9]{20,}", text)


# ── 1. artifacts exist + wrapper executable ───────────────────────────────────

def test_artifacts_exist_and_wrapper_executable() -> None:
    assert TASK_FILE.is_file()
    assert PORTFOLIO_SCRIPT.is_file()
    assert BASH_WRAPPER.is_file()
    assert os.access(BASH_WRAPPER, os.X_OK)


# ── 2. happy path counts ──────────────────────────────────────────────────────

def test_happy_path_counts() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_score("pytest-phase3b-b", score=80, decision="small_batch_test")
    _write_score("pytest-phase3b-c", score=70, decision="watchlist")
    _write_score("pytest-phase3b-d", score=60, decision="reject")
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    for field in COUNT_FIELDS:
        assert any(line.startswith(f"{field}:") for line in result.stdout.splitlines())
    assert _field(result.stdout, "total_products") == "4"
    assert _field(result.stdout, "launch_count") == "1"
    assert _field(result.stdout, "small_batch_test_count") == "1"
    assert _field(result.stdout, "watchlist_count") == "1"
    assert _field(result.stdout, "reject_count") == "1"
    assert _field(result.stdout, "skipped_count") == "0"
    assert "phase3b_status: success" in result.stdout


# ── 3. grouping by decision ───────────────────────────────────────────────────

def test_grouping_by_decision() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_score("pytest-phase3b-b", score=88, decision="launch")
    _write_score("pytest-phase3b-c", score=70, decision="watchlist")
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "launch_count") == "2"
    assert _field(result.stdout, "watchlist_count") == "1"
    assert _field(result.stdout, "small_batch_test_count") == "0"
    artifact = PORTFOLIO_PATH.read_text(encoding="utf-8")
    launch_section = artifact.split("### Launch", 1)[1].split("###", 1)[0]
    assert "pytest-phase3b-a" in launch_section
    assert "pytest-phase3b-b" in launch_section


# ── 4. ranking desc + product_id tie-break ────────────────────────────────────

def test_ranking_and_tiebreak() -> None:
    _write_score("pytest-phase3b-e", score=90, decision="launch")
    _write_score("pytest-phase3b-a", score=90, decision="launch")  # tie with e
    _write_score("pytest-phase3b-b", score=80, decision="small_batch_test")
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    order = _top_product_order(result.stdout)
    assert order == ["pytest-phase3b-a", "pytest-phase3b-e", "pytest-phase3b-b"]


# ── 5. --top limits displayed products ────────────────────────────────────────

def test_top_limits_display() -> None:
    for idx, pid in enumerate(("pytest-phase3b-a", "pytest-phase3b-b", "pytest-phase3b-c", "pytest-phase3b-d")):
        _write_score(pid, score=90 - idx, decision="launch")
    result = _run_py("--week", WEEK, "--top", "2")
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "top_n") == "2"
    assert _field(result.stdout, "total_products") == "4"
    assert len(_top_product_order(result.stdout)) == 2


# ── 6. default top_n is 10 ────────────────────────────────────────────────────

def test_default_top_n() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "top_n") == "10"


# ── 7. --write creates artifact ───────────────────────────────────────────────

def test_write_creates_artifact() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert PORTFOLIO_PATH.is_file()
    assert "portfolio_path:" in result.stdout


# ── 8. artifact frontmatter type ──────────────────────────────────────────────

def test_artifact_type() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _run_py("--week", WEEK, "--write")
    assert "type: phase3b_portfolio_dashboard" in PORTFOLIO_PATH.read_text(encoding="utf-8")


# ── 9. empty scores dir exits 0 with zero counts ──────────────────────────────

def test_empty_scores_dir() -> None:
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "total_products") == "0"
    assert _field(result.stdout, "launch_count") == "0"
    assert _field(result.stdout, "skipped_count") == "0"
    assert "phase3b_status: success" in result.stdout


# ── 10. malformed JSON skipped ────────────────────────────────────────────────

def test_malformed_json_skipped() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_raw_score("pytest-phase3b-broken.json", "{ not valid json")
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "total_products") == "1"
    assert _field(result.stdout, "skipped_count") == "1"


# ── 11. invalid week ──────────────────────────────────────────────────────────

def test_invalid_week() -> None:
    result = _run_py("--week", "2099-W2")
    assert result.returncode != 0
    assert "week must match" in result.stderr


# ── 12. invalid --top ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_invalid_top(value: str) -> None:
    result = _run_py("--week", WEEK, "--top", value)
    assert result.returncode != 0


# ── 13. phase3a artifact count ────────────────────────────────────────────────

def test_phase3a_artifact_count() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_score("pytest-phase3b-b", score=80, decision="launch")
    _write_phase3a("pytest-phase3b-a")
    result = _run_py("--week", WEEK)
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "phase3a_artifact_count") == "1"


# ── 14. vault counts without leaking paths ────────────────────────────────────

def test_vault_counts() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_score("pytest-phase3b-b", score=80, decision="small_batch_test")
    _write_score("pytest-phase3b-c", score=70, decision="watchlist")
    _write_vault_product("pytest-phase3b-a")
    _write_vault_decision("pytest-phase3b-b", "draft")
    _write_vault_decision("pytest-phase3b-c", "complete")
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert _field(result.stdout, "promoted_count") == "1"
    assert _field(result.stdout, "decision_draft_count") == "1"
    assert _field(result.stdout, "decision_complete_count") == "1"
    _assert_no_forbidden(result.stdout)
    _assert_no_forbidden(PORTFOLIO_PATH.read_text(encoding="utf-8"))


# ── 15. no input_path or note_refs emitted ────────────────────────────────────

def test_no_input_path_or_note_refs() -> None:
    _write_score(
        "pytest-phase3b-a",
        score=90,
        decision="launch",
        extra={
            "input_path": "/home/ubuntu/Affiliate-Ai/vault/products/secret.md",
            "note_refs": {"trend_signal_note": "vault/products/leak.md"},
        },
    )
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    artifact = PORTFOLIO_PATH.read_text(encoding="utf-8")
    for text in (result.stdout, artifact):
        assert "input_path" not in text
        assert "note_refs" not in text
        assert "secret.md" not in text
        assert "leak.md" not in text


# ── 16-17. scrubbing ──────────────────────────────────────────────────────────

def test_output_is_clean() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    _write_score("pytest-phase3b-b", score=80, decision="reject")
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    _assert_no_forbidden(result.stdout)
    _assert_no_forbidden(PORTFOLIO_PATH.read_text(encoding="utf-8"))


# ── 18. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    result = _run_py("--week", WEEK, "--write")
    assert result.returncode == 0, result.stderr
    assert not (VAULT_PRODUCTS_DIR / "pytest-phase3b-a.md").exists()
    assert not (VAULT_DECISIONS_DIR / f"dec-pytest-phase3b-a-{WEEK}.md").exists()


# ── 19-20. wrapper guardrails ─────────────────────────────────────────────────

def test_wrapper_fails_on_autopublish() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    env = {**os.environ, "ENABLE_AUTOPUBLISH": "true"}
    result = _run_sh(WEEK, env=env)
    assert result.returncode != 0
    assert "ENABLE_AUTOPUBLISH" in result.stderr


def test_wrapper_fails_on_openai_direct() -> None:
    _write_score("pytest-phase3b-a", score=90, decision="launch")
    env = {**os.environ, "ENABLE_OPENAI_API_DIRECT": "true"}
    result = _run_sh(WEEK, env=env)
    assert result.returncode != 0
    assert "ENABLE_OPENAI_API_DIRECT" in result.stderr
