from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts/dev/build_ui_snapshot.py"
WRAPPER = REPO_ROOT / "scripts/dev/run_phase4b_ui_snapshot.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/021-phase4b-ui-snapshot-pack.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE4A_HTML = REPO_ROOT / "tmp/phase4a-ui/index.html"
PORTFOLIO_DIR = REPO_ROOT / "tmp/phase3b-portfolio-dashboard"
DASHBOARD_DIR = REPO_ROOT / "tmp/phase3a-dashboard"
SCORES_DIR = REPO_ROOT / "tmp/phase2e-import-score-report/scores"
SNAP_DIR = REPO_ROOT / "tmp/phase4b-ui-snapshot"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

WEEK = "2099-W05"
EXPECTED_FILES = {"index.html", "manifest.json", "README.md", "INVENTORY.md", "GUARDRAILS.md"}
TEST_ID = "pytest-phase4b-a"

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
CONTENT_MARKERS = ("content_draft", "campaign_copy", "tiktok_script", "hook_text", "blog_post")

GUARDRAIL_TOKENS = (
    "no database",
    "no FastAPI",
    "no backend service",
    "no external APIs",
    "no external URLs",
    "no affiliate content generation",
    "no autopublish",
    "no campaign launch",
    "no vault writes",
    "no approval mutation",
    "no Phase 2G/2H/2I triggering",
    "no marketplace connector",
    "read-only only",
)


def _write_portfolio() -> None:
    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    (PORTFOLIO_DIR / f"portfolio-{WEEK}.md").write_text(
        "---\ntype: phase3b_portfolio_dashboard\n"
        f"report_week: {WEEK}\n"
        "total_products: 1\nlaunch_count: 1\nsmall_batch_test_count: 0\n"
        "watchlist_count: 0\nreject_count: 0\ntop_n: 10\n"
        "promoted_count: 0\ndecision_draft_count: 0\ndecision_complete_count: 0\n"
        "status: complete\n---\n\n# portfolio\n",
        encoding="utf-8",
    )


def _write_dashboard() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    (DASHBOARD_DIR / f"dashboard-{TEST_ID}-{WEEK}.md").write_text(
        "---\ntype: phase3a_dashboard_summary\n"
        f"report_week: {WEEK}\nproduct_id: {TEST_ID}\nproduct_name: Widget A\n"
        "product_opportunity_score: 88\nscore_decision: launch\nconfidence_score: 95\n"
        "report_status: generated\nhermes_summary_status: complete\n"
        "governance_summary_status: complete\npromote_status: dry_run_not_promoted\n"
        "decision_status: not_executed\nfinalization_status: not_executed\n"
        'next_allowed_action: "Promote candidate through Phase 2G approval gate"\n'
        "status: complete\n---\n\n# dashboard\n",
        encoding="utf-8",
    )


def _write_score() -> None:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    (SCORES_DIR / f"{TEST_ID}.json").write_text(
        json.dumps(
            {
                "product_id": TEST_ID,
                "product_name": "Widget A",
                "product_opportunity_score": 88,
                "score_decision": "launch",
                "confidence_score": 95,
            }
        ),
        encoding="utf-8",
    )


def _clean_snapshot() -> None:
    if SNAP_DIR.is_dir():
        for path in SNAP_DIR.iterdir():
            if path.is_file():
                path.unlink()


def _clean_fixtures() -> None:
    (PORTFOLIO_DIR / f"portfolio-{WEEK}.md").unlink(missing_ok=True)
    (DASHBOARD_DIR / f"dashboard-{TEST_ID}-{WEEK}.md").unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def _isolate(tmp_path_factory):
    stash = tmp_path_factory.mktemp("scores_stash")
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    for path in list(SCORES_DIR.glob("*.json")):
        shutil.move(str(path), str(stash / path.name))
    _clean_snapshot()
    _clean_fixtures()
    try:
        yield
    finally:
        for path in list(SCORES_DIR.glob("*.json")):
            path.unlink()
        for path in stash.glob("*.json"):
            shutil.move(str(path), str(SCORES_DIR / path.name))
        _clean_snapshot()
        _clean_fixtures()


def _populate() -> None:
    _write_portfolio()
    _write_dashboard()
    _write_score()


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


def _snapshot_files() -> set[str]:
    return {p.name for p in SNAP_DIR.iterdir() if p.is_file()} if SNAP_DIR.is_dir() else set()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _vault_snapshot() -> tuple[list[str], list[str]]:
    products = sorted(p.name for p in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    decisions = sorted(p.name for p in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return products, decisions


# ── 1-5. existence + syntax ───────────────────────────────────────────────────

def test_task_file_exists() -> None:
    assert TASK_FILE.is_file()


def test_build_script_exists() -> None:
    assert BUILD_SCRIPT.is_file()


def test_wrapper_exists_and_executable() -> None:
    assert WRAPPER.is_file()
    assert os.access(WRAPPER, os.X_OK)


def test_gitignore_includes_phase4b() -> None:
    assert "tmp/phase4b-ui-snapshot/" in GITIGNORE.read_text(encoding="utf-8")


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 6-7. build + exact files ──────────────────────────────────────────────────

def test_build_creates_snapshot() -> None:
    _populate()
    result = _run_build()
    assert result.returncode == 0, result.stderr
    assert SNAP_DIR.is_dir()
    assert "phase4b_status: success" in result.stdout


def test_snapshot_contains_exact_files() -> None:
    _populate()
    _run_build()
    assert _snapshot_files() == EXPECTED_FILES


# ── 8. index.html matches Phase 4A ────────────────────────────────────────────

def test_index_matches_phase4a() -> None:
    _populate()
    _run_build()
    assert _sha256_file(SNAP_DIR / "index.html") == _sha256_file(PHASE4A_HTML)


# ── 9-13. manifest ────────────────────────────────────────────────────────────

def test_manifest_valid_json() -> None:
    _populate()
    _run_build()
    json.loads((SNAP_DIR / "manifest.json").read_text(encoding="utf-8"))


def test_manifest_type_and_week() -> None:
    _populate()
    _run_build()
    manifest = json.loads((SNAP_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["type"] == "phase4b_ui_snapshot"
    assert manifest["report_week"] == WEEK


def test_manifest_files_match_actual() -> None:
    _populate()
    _run_build()
    manifest = json.loads((SNAP_DIR / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = SNAP_DIR / entry["name"]
        assert path.is_file()
        assert entry["sha256"] == _sha256_file(path)
        assert entry["bytes"] == path.stat().st_size


def test_manifest_source_summary_vault_false() -> None:
    _populate()
    _run_build()
    manifest = json.loads((SNAP_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_summary"]["vault_included"] is False


# ── 14-16. docs content ───────────────────────────────────────────────────────

def test_readme_content() -> None:
    _populate()
    _run_build()
    text = (SNAP_DIR / "README.md").read_text(encoding="utf-8")
    for token in ("open", "read-only", "no backend", "no server", "no external URLs", "no vault files"):
        assert token in text, f"README missing: {token}"


def test_inventory_content() -> None:
    _populate()
    _run_build()
    text = (SNAP_DIR / "INVENTORY.md").read_text(encoding="utf-8")
    assert "no vault files included" in text
    assert "vault_included: false" in text
    assert "product_dashboards" in text
    assert "score_files" in text


def test_guardrails_content() -> None:
    _populate()
    _run_build()
    text = (SNAP_DIR / "GUARDRAILS.md").read_text(encoding="utf-8")
    for token in GUARDRAIL_TOKENS:
        assert token in text, f"GUARDRAILS missing: {token}"


# ── 17-19. scrubbing across all files ─────────────────────────────────────────

def test_no_forbidden_content_in_any_file() -> None:
    _populate()
    _run_build()
    for path in SNAP_DIR.iterdir():
        text = path.read_text(encoding="utf-8")
        for vp in PRIVATE_VAULT_PATHS:
            assert vp not in text, f"{path.name} leaked vault path {vp}"
        for url in ("http://", "https://"):
            assert url not in text, f"{path.name} contains external URL {url}"
        for ap in AFFILIATE_URL_PATTERNS:
            assert ap not in text, f"{path.name} contains affiliate pattern {ap}"
        for marker in CONTENT_MARKERS:
            assert marker not in text, f"{path.name} contains content marker {marker}"
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
        assert not re.search(r"AKIA[A-Z0-9]{16}", text)
        assert not re.search(r"Bearer [A-Za-z0-9]{20,}", text)


# ── 20. no raw artifacts copied ───────────────────────────────────────────────

def test_no_raw_artifacts_in_snapshot() -> None:
    _populate()
    _run_build()
    names = _snapshot_files()
    assert names == EXPECTED_FILES
    for name in names:
        assert not name.startswith("dashboard-")
        assert not name.startswith("portfolio-")
        assert not (name.endswith(".json") and name != "manifest.json")


# ── 21. index.html self-contained ─────────────────────────────────────────────

def test_index_self_contained() -> None:
    _populate()
    _run_build()
    html = (SNAP_DIR / "index.html").read_text(encoding="utf-8")
    for forbidden in ("<script", "fetch(", "XMLHttpRequest", "import(", "<link "):
        assert forbidden not in html, f"index.html not self-contained: {forbidden}"


# ── 22. degraded mode ─────────────────────────────────────────────────────────

def test_degraded_mode() -> None:
    result = _run_build()
    assert result.returncode == 0, result.stderr
    assert _snapshot_files() == EXPECTED_FILES
    manifest = json.loads((SNAP_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_summary"]["portfolio_artifact"] == "absent"
    assert manifest["source_summary"]["product_dashboards"] == 0


# ── 23-25. validation / guardrails ────────────────────────────────────────────

def test_invalid_week() -> None:
    result = _run_build("2099-W5")
    assert result.returncode != 0
    assert "week must match" in result.stderr


@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT"])
def test_wrapper_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run_wrapper(env=env)
    assert result.returncode != 0
    assert flag in result.stderr


# ── 26. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    _populate()
    before = _vault_snapshot()
    result = _run_build()
    assert result.returncode == 0, result.stderr
    after = _vault_snapshot()
    assert before == after


# ── 27. idempotent ────────────────────────────────────────────────────────────

def test_idempotent() -> None:
    _populate()
    first = _run_build()
    assert first.returncode == 0, first.stderr
    second = _run_build()
    assert second.returncode == 0, second.stderr
    assert _snapshot_files() == EXPECTED_FILES


# ── 28-30. static safety ──────────────────────────────────────────────────────

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
    assert forbidden not in build_text
    assert forbidden not in wrapper_text


def test_static_no_artifact_copy_helpers() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    # The builder must not bulk-copy artifact directories into the snapshot.
    assert "copytree" not in text
    assert "shutil.copy" not in text
