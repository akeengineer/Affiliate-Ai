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
BUILD_SCRIPT = REPO_ROOT / "scripts/dev/build_snapshot_catalog.py"
WRAPPER = REPO_ROOT / "scripts/dev/run_phase4c_snapshot_catalog.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/022-phase4c-static-snapshot-catalog.md"
GITIGNORE = REPO_ROOT / ".gitignore"

TMP_DIR = REPO_ROOT / "tmp"
CATALOG_DIR = TMP_DIR / "phase4c-snapshot-catalog"

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

EXPECTED_FILES = {"index.html", "catalog.json", "README.md", "GUARDRAILS.md"}

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
    "no vault reads",
    "no vault writes",
    "no approval mutation",
    "no Phase 2G/2H/2I triggering",
    "no marketplace connector",
    "no raw artifact export",
    "read-only only",
)


def _manifest(week: str, *, vault_included: bool = False, dashboards: int = 1, scores: int = 1) -> dict:
    return {
        "type": "phase4b_ui_snapshot",
        "report_week": week,
        "generated_at": "2099-01-01T00:00:00Z",
        "files": [
            {"name": "index.html", "sha256": "a" * 64, "bytes": 100},
            {"name": "README.md", "sha256": "b" * 64, "bytes": 50},
        ],
        "source_summary": {
            "portfolio_artifact": "present",
            "product_dashboards": dashboards,
            "score_files": scores,
            "vault_included": vault_included,
        },
    }


def _make_snapshot(dir_name: str, manifest: dict | None = None, *, raw: str | None = None) -> Path:
    snap_dir = TMP_DIR / dir_name
    snap_dir.mkdir(parents=True, exist_ok=True)
    text = raw if raw is not None else json.dumps(manifest)
    (snap_dir / "manifest.json").write_text(text, encoding="utf-8")
    return snap_dir


def _clean_catalog() -> None:
    if CATALOG_DIR.is_dir():
        for path in CATALOG_DIR.iterdir():
            if path.is_file():
                path.unlink()


def _existing_snapshot_dirs() -> list[Path]:
    return [p for p in TMP_DIR.glob("phase4b-ui-snapshot*") if p.is_dir()]


@pytest.fixture(autouse=True)
def _isolate(tmp_path_factory):
    """Stash any real Phase 4B snapshot dirs so the catalog only sees fixtures."""
    stash = tmp_path_factory.mktemp("snap_stash")
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    for path in _existing_snapshot_dirs():
        shutil.move(str(path), str(stash / path.name))
    _clean_catalog()
    try:
        yield
    finally:
        for path in _existing_snapshot_dirs():
            shutil.rmtree(path)
        for path in stash.iterdir():
            shutil.move(str(path), str(TMP_DIR / path.name))
        _clean_catalog()


def _run_build() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _run_wrapper(env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(WRAPPER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def _catalog_files() -> set[str]:
    return {p.name for p in CATALOG_DIR.iterdir() if p.is_file()} if CATALOG_DIR.is_dir() else set()


def _catalog_json() -> dict:
    return json.loads((CATALOG_DIR / "catalog.json").read_text(encoding="utf-8"))


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


def test_gitignore_includes_phase4c() -> None:
    assert "tmp/phase4c-snapshot-catalog/" in GITIGNORE.read_text(encoding="utf-8")


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


# ── 6-10. build + catalog.json ────────────────────────────────────────────────

def test_build_creates_catalog() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    result = _run_build()
    assert result.returncode == 0, result.stderr
    assert CATALOG_DIR.is_dir()
    assert "phase4c_status: success" in result.stdout


def test_catalog_contains_exact_files() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    assert _catalog_files() == EXPECTED_FILES


def test_catalog_json_valid_and_typed() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    catalog = _catalog_json()
    assert catalog["type"] == "phase4c_snapshot_catalog"
    assert "snapshots" in catalog
    assert "snapshot_count" in catalog


# ── 11. single snapshot fidelity ──────────────────────────────────────────────

def test_single_snapshot_fields() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06", dashboards=2, scores=3))
    _run_build()
    catalog = _catalog_json()
    assert catalog["snapshot_count"] == 1
    snap = catalog["snapshots"][0]
    assert snap["source_dir"] == "tmp/phase4b-ui-snapshot"
    assert snap["report_week"] == "2099-W06"
    assert snap["index_sha256"] == "a" * 64
    assert snap["file_count"] == 2
    assert snap["total_bytes"] == 150
    assert snap["source_summary"]["product_dashboards"] == 2
    assert snap["source_summary"]["score_files"] == 3
    assert snap["source_summary"]["vault_included"] is False


# ── 12. multi-snapshot ────────────────────────────────────────────────────────

def test_multi_snapshot() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _make_snapshot("phase4b-ui-snapshot-extra", _manifest("2099-W07"))
    _run_build()
    catalog = _catalog_json()
    assert catalog["snapshot_count"] == 2
    weeks = [s["report_week"] for s in catalog["snapshots"]]
    assert weeks == ["2099-W06", "2099-W07"]


# ── 13. malformed manifest skipped ────────────────────────────────────────────

def test_malformed_manifest_skipped() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _make_snapshot("phase4b-ui-snapshot-bad", raw="{ not valid json")
    _run_build()
    catalog = _catalog_json()
    assert catalog["snapshot_count"] == 1
    assert catalog["skipped_count"] == 1


# ── 14. empty catalog ─────────────────────────────────────────────────────────

def test_empty_catalog() -> None:
    result = _run_build()
    assert result.returncode == 0, result.stderr
    catalog = _catalog_json()
    assert catalog["snapshot_count"] == 0
    assert "no snapshots found" in (CATALOG_DIR / "index.html").read_text(encoding="utf-8")


# ── 15-17. index.html ─────────────────────────────────────────────────────────

def test_index_structure() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    html = (CATALOG_DIR / "index.html").read_text(encoding="utf-8")
    assert "Snapshot Catalog" in html
    assert "READ-ONLY CATALOG" in html
    assert "2099-W06" in html


def test_index_self_contained() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    html = (CATALOG_DIR / "index.html").read_text(encoding="utf-8")
    for forbidden in ("http://", "https://", "<script", "fetch(", "XMLHttpRequest", "import(", "<link "):
        assert forbidden not in html, f"not self-contained: {forbidden}"


def test_index_href_relative_only() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    html = (CATALOG_DIR / "index.html").read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"]*)"', html)
    assert hrefs, "expected at least one snapshot link"
    for href in hrefs:
        assert not href.startswith("http"), f"non-relative href: {href}"
        assert href.startswith("../") or href.startswith("./") or not href.startswith("/")


# ── 18. no raw artifacts in catalog ───────────────────────────────────────────

def test_no_raw_artifacts() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    names = _catalog_files()
    assert names == EXPECTED_FILES
    assert "manifest.json" not in names
    for name in names:
        assert not name.startswith("dashboard-")
        assert not name.startswith("portfolio-")
        assert not (name.endswith(".json") and name != "catalog.json")


# ── 19-20. docs ───────────────────────────────────────────────────────────────

def test_readme_content() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    text = (CATALOG_DIR / "README.md").read_text(encoding="utf-8")
    for token in ("read-only", "no backend", "no server", "no external URLs", "no vault files", "no raw artifacts"):
        assert token in text, f"README missing: {token}"


def test_guardrails_content() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    text = (CATALOG_DIR / "GUARDRAILS.md").read_text(encoding="utf-8")
    for token in GUARDRAIL_TOKENS:
        assert token in text, f"GUARDRAILS missing: {token}"


# ── 21-22. scrubbing ──────────────────────────────────────────────────────────

def test_no_forbidden_content() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    _run_build()
    for path in CATALOG_DIR.iterdir():
        text = path.read_text(encoding="utf-8")
        for vp in PRIVATE_VAULT_PATHS:
            assert vp not in text, f"{path.name} leaked vault path {vp}"
        for url in ("http://", "https://"):
            assert url not in text, f"{path.name} external URL {url}"
        for ap in AFFILIATE_URL_PATTERNS:
            assert ap not in text, f"{path.name} affiliate pattern {ap}"
        for marker in CONTENT_MARKERS:
            assert marker not in text, f"{path.name} content marker {marker}"
        assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
        assert not re.search(r"AKIA[A-Z0-9]{16}", text)
        assert not re.search(r"Bearer [A-Za-z0-9]{20,}", text)


# ── 23. unsafe manifest skipped ───────────────────────────────────────────────

def test_unsafe_vault_included_skipped() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06", vault_included=True))
    _run_build()
    catalog = _catalog_json()
    assert catalog["snapshot_count"] == 0
    assert catalog["skipped_count"] == 1


# ── 24-25. wrapper guardrails ─────────────────────────────────────────────────

@pytest.mark.parametrize("flag", ["ENABLE_AUTOPUBLISH", "ENABLE_OPENAI_API_DIRECT"])
def test_wrapper_unsafe_flag(flag: str) -> None:
    env = {**os.environ, flag: "true"}
    result = _run_wrapper(env=env)
    assert result.returncode != 0
    assert flag in result.stderr


# ── 26. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    before = _vault_snapshot()
    _run_build()
    after = _vault_snapshot()
    assert before == after


# ── 27. idempotent ────────────────────────────────────────────────────────────

def test_idempotent() -> None:
    _make_snapshot("phase4b-ui-snapshot", _manifest("2099-W06"))
    assert _run_build().returncode == 0
    assert _run_build().returncode == 0
    assert _catalog_files() == EXPECTED_FILES


# ── 28-31. static safety ──────────────────────────────────────────────────────

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


def test_static_no_vault_paths() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert 'REPO_ROOT / "vault"' not in text
    assert "vault/products" not in text
    assert "vault/decisions" not in text


def test_static_no_raw_artifact_reads() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("phase3a-dashboard", "phase3b-portfolio", "phase2e-import"):
        assert forbidden not in text, f"core references raw artifact source: {forbidden}"
