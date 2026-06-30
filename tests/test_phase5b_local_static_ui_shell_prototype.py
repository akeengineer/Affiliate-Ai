from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase5b_ui_shell.sh"
BUILD = REPO_ROOT / "scripts/dev/build_ui_shell.py"
TASK_FILE = REPO_ROOT / "codex/tasks/030-phase5b-local-static-ui-shell-prototype.md"
DOC = REPO_ROOT / "docs/UI_SHELL.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE4E_WRAPPER = REPO_ROOT / "scripts/dev/run_phase4e_demo_bundle.sh"
OUT = REPO_ROOT / "tmp/phase5b-ui-shell/index.html"
WEEK = "2026-W26"

SOURCES = [
    REPO_ROOT / "tmp/phase4e-demo-bundle/demo-bundle-summary.json",
    REPO_ROOT / "tmp/phase4b-ui-snapshot/manifest.json",
    REPO_ROOT / "tmp/phase4c-snapshot-catalog/catalog.json",
    REPO_ROOT / "tmp/phase4d-demo-verifier/verification-summary.json",
]

VAULT_PRODUCTS_DIR = REPO_ROOT / "vault/products"
VAULT_DECISIONS_DIR = REPO_ROOT / "vault/decisions"

GUARDRAIL_FLAGS = [
    "ENABLE_AUTOPUBLISH",
    "ENABLE_OPENAI_API_DIRECT",
    "APPROVE_PROMOTE",
    "APPROVE_DECISION",
    "APPROVE_FINALIZE",
]


def _base_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("AFFILIATE_REQUIRE_OPERATOR_RUNTIME", None)
    env.update(overrides)
    return env


def _run(*args: str, env: dict[str, str] | None = None, cwd: Path | None = None):
    return subprocess.run(
        ["bash", str(WRAPPER), *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=env or _base_env(),
    )


def _build_phase4() -> None:
    res = subprocess.run(
        ["bash", str(PHASE4E_WRAPPER), WEEK],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=_base_env(),
    )
    assert res.returncode == 0, res.stderr


def _vault_lists() -> tuple[list[str], list[str]]:
    p = sorted(x.name for x in VAULT_PRODUCTS_DIR.iterdir()) if VAULT_PRODUCTS_DIR.is_dir() else []
    d = sorted(x.name for x in VAULT_DECISIONS_DIR.iterdir()) if VAULT_DECISIONS_DIR.is_dir() else []
    return p, d


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert DOC.is_file()
    assert BUILD.is_file()
    assert WRAPPER.is_file()


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_build_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(BUILD)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase5b() -> None:
    assert "tmp/phase5b-ui-shell/" in GITIGNORE.read_text(encoding="utf-8")


# ── 6-8. argument + guardrail validation ──────────────────────────────────────

def test_invalid_week_fails() -> None:
    assert _run("2026W26").returncode != 0


def test_wrong_arg_count_fails() -> None:
    assert _run().returncode != 0
    assert _run(WEEK, "extra").returncode != 0


@pytest.mark.parametrize("flag", GUARDRAIL_FLAGS)
def test_guardrail_flags_fail(flag: str) -> None:
    assert _run(WEEK, env=_base_env(**{flag: "true"})).returncode != 0


# ── 9-10. end-to-end + HTML content ───────────────────────────────────────────

def test_end_to_end() -> None:
    _build_phase4()
    res = _run(WEEK)
    assert res.returncode == 0, res.stderr
    assert "ui_shell_path:" in res.stdout
    assert "phase5b_status: success" in res.stdout
    assert OUT.is_file()


def test_html_content() -> None:
    _build_phase4()
    assert _run(WEEK).returncode == 0
    html = OUT.read_text(encoding="utf-8")
    assert "READ-ONLY SHELL" in html
    for section in (
        "Demo readiness",
        "Snapshot status",
        "Catalog status",
        "Verification status",
        "Local links",
        "Guardrails",
    ):
        assert section in html, f"missing section: {section}"
    assert "../phase4b-ui-snapshot/index.html" in html
    assert "../phase4c-snapshot-catalog/index.html" in html


# ── 11-12. self-contained / zero-JS / cleanliness ─────────────────────────────

def test_self_contained_zero_js() -> None:
    _build_phase4()
    assert _run(WEEK).returncode == 0
    html = OUT.read_text(encoding="utf-8")
    for token in ("http://", "https://", "<script", "fetch(", "XMLHttpRequest", "import(", "<iframe", "<form", "<link"):
        assert token not in html, f"forbidden token present: {token}"
    assert not re.search(r"<[^>]*\son[a-z]+\s*=", html, re.IGNORECASE), "inline event handler present"


def test_cleanliness() -> None:
    _build_phase4()
    assert _run(WEEK).returncode == 0
    html = OUT.read_text(encoding="utf-8")
    for token in ("/home/ubuntu/Affiliate-Ai", "vault/products", "vault/decisions", "tag=", "affiliate=", "autopublish"):
        assert token not in html, f"unclean token present: {token}"


# ── 13. missing Phase 4 outputs → notice + exit 0 ─────────────────────────────

def test_missing_outputs_degrade_gracefully() -> None:
    backups: list[tuple[Path, Path]] = []
    for src in SOURCES:
        if src.is_file():
            bak = src.with_suffix(src.suffix + ".bak")
            src.rename(bak)
            backups.append((src, bak))
    try:
        res = _run(WEEK)
        assert res.returncode == 0, res.stderr
        html = OUT.read_text(encoding="utf-8")
        assert "output not found" in html
    finally:
        for src, bak in backups:
            bak.rename(src)


# ── 14. no vault write ────────────────────────────────────────────────────────

def test_no_vault_write() -> None:
    before = _vault_lists()
    _build_phase4()
    assert _run(WEEK).returncode == 0
    after = _vault_lists()
    assert before == after, "Phase 5B must not write the vault"


# ── 15. reads only the four Phase 4 sources (no vault read) ───────────────────

def test_reads_only_phase4_sources() -> None:
    src = BUILD.read_text(encoding="utf-8")
    assert "vault/products" not in src
    assert "vault/decisions" not in src
    assert "phase2e-import-score-report" not in src
    assert "phase3a-dashboard" not in src
    assert "phase3b-portfolio-dashboard" not in src
    for needed in (
        "tmp/phase4e-demo-bundle/demo-bundle-summary.json",
        "tmp/phase4b-ui-snapshot/manifest.json",
        "tmp/phase4c-snapshot-catalog/catalog.json",
        "tmp/phase4d-demo-verifier/verification-summary.json",
    ):
        assert needed in src, f"expected source not referenced: {needed}"


# ── 16. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    _build_phase4()
    res = subprocess.run(
        ["bash", str(WRAPPER), WEEK],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=_base_env(),
    )
    assert res.returncode == 0, res.stderr
    assert "phase5b_status: success" in res.stdout


# ── 17. CI-C alignment ────────────────────────────────────────────────────────

def test_ci_c_alignment() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert "/home/ubuntu/Affiliate-Ai" not in text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in text
    for pattern in (r"\bcurl\b", r"\bwget\b", r"\bnc\b", r"\bnetcat\b", r"https?://"):
        assert not re.search(pattern, text), f"network token in wrapper: {pattern}"


# ── 18. static boundary: no approved-workflow references ──────────────────────

def test_no_approved_workflow_references() -> None:
    for path in (WRAPPER, BUILD):
        text = path.read_text(encoding="utf-8")
        for ref in (
            "run_phase2g",
            "run_phase2h",
            "run_phase2i",
            "promote_product_candidates.py",
            "create_decision.py",
            "finalize_decision.py",
        ):
            assert ref not in text, f"{path.name} references approved workflow: {ref}"
