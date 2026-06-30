from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "scripts/dev/run_phase5c_ui_shell_verifier.sh"
VERIFY = REPO_ROOT / "scripts/dev/verify_ui_shell.py"
TASK_FILE = REPO_ROOT / "codex/tasks/031-phase5c-ui-shell-verifier.md"
DOC = REPO_ROOT / "docs/UI_SHELL.md"
GITIGNORE = REPO_ROOT / ".gitignore"

PHASE4E_WRAPPER = REPO_ROOT / "scripts/dev/run_phase4e_demo_bundle.sh"
PHASE5B_WRAPPER = REPO_ROOT / "scripts/dev/run_phase5b_ui_shell.sh"

SHELL = REPO_ROOT / "tmp/phase5b-ui-shell/index.html"
OUT_DIR = REPO_ROOT / "tmp/phase5c-ui-shell-verifier"
REPORT = OUT_DIR / "verification-report.md"
SUMMARY = OUT_DIR / "verification-summary.json"
PHASE4D_SOURCE = REPO_ROOT / "tmp/phase4d-demo-verifier/verification-summary.json"

WEEK = "2026-W26"

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


def _build_chain() -> None:
    for wrapper, extra in ((PHASE4E_WRAPPER, [WEEK]), (PHASE5B_WRAPPER, [WEEK])):
        res = subprocess.run(
            ["bash", str(wrapper), *extra],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env=_base_env(),
        )
        assert res.returncode == 0, res.stderr


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert DOC.is_file()
    assert VERIFY.is_file()
    assert WRAPPER.is_file()


def test_wrapper_executable() -> None:
    assert os.access(WRAPPER, os.X_OK)


def test_wrapper_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(WRAPPER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_verifier_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(VERIFY)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase5c() -> None:
    assert "tmp/phase5c-ui-shell-verifier/" in GITIGNORE.read_text(encoding="utf-8")


# ── 6-7. argument + guardrail validation ──────────────────────────────────────

def test_wrong_arg_count_fails() -> None:
    assert _run("unexpected").returncode != 0


@pytest.mark.parametrize("flag", GUARDRAIL_FLAGS)
def test_guardrail_flags_fail(flag: str) -> None:
    assert _run(env=_base_env(**{flag: "true"})).returncode != 0


# ── 8-9. end-to-end ready + report/summary content ───────────────────────────

def test_end_to_end_ready() -> None:
    _build_chain()
    res = _run()
    assert res.returncode == 0, res.stderr
    assert "verdict: ready" in res.stdout
    assert "phase5c_status: success" in res.stdout
    assert REPORT.is_file()
    assert SUMMARY.is_file()
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["verdict"] == "ready"


def test_report_and_summary_content() -> None:
    _build_chain()
    assert _run().returncode == 0
    report = REPORT.read_text(encoding="utf-8")
    assert "| check | result |" in report
    assert "Verdict:" in report
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["type"] == "phase5c_ui_shell_verification"
    assert SHELL.relative_to(REPO_ROOT).as_posix() in data["checked_paths"]


# ── 10. output self-safety ────────────────────────────────────────────────────

def test_output_safety() -> None:
    _build_chain()
    assert _run().returncode == 0
    blob = REPORT.read_text(encoding="utf-8") + SUMMARY.read_text(encoding="utf-8")
    for token in (
        "http://",
        "https://",
        "file://",
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "import(",
        "<iframe",
        "<form",
        "<link",
        "/home/ubuntu/Affiliate-Ai",
        "vault/products",
        "vault/decisions",
        "tag=",
        "affiliate=",
    ):
        assert token not in blob, f"verifier output echoed forbidden token: {token}"


# ── 11. failed path (tampered shell) ──────────────────────────────────────────

def test_failed_path_tampered_shell() -> None:
    _build_chain()
    original = SHELL.read_text(encoding="utf-8")
    try:
        SHELL.write_text(original.replace("</body>", '<a href="http://x.example">x</a></body>'), encoding="utf-8")
        res = _run()
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        _build_chain()


# ── 12. warning path (missing source with visible notice) ─────────────────────

def test_warning_path_missing_source_with_notice() -> None:
    _build_chain()
    backup = PHASE4D_SOURCE.with_suffix(PHASE4D_SOURCE.suffix + ".bak")
    moved = False
    try:
        if PHASE4D_SOURCE.is_file():
            PHASE4D_SOURCE.rename(backup)
            moved = True
        # Rebuild 5B so the shell shows the missing-source notice.
        rb = subprocess.run(
            ["bash", str(PHASE5B_WRAPPER), WEEK], cwd=REPO_ROOT, capture_output=True, text=True, env=_base_env()
        )
        assert rb.returncode == 0, rb.stderr
        res = _run()
        assert res.returncode == 0, res.stderr
        assert "verdict: warning" in res.stdout
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        assert data["verdict"] == "warning"
    finally:
        if moved:
            backup.rename(PHASE4D_SOURCE)
        _build_chain()


# ── 13. missing shell ─────────────────────────────────────────────────────────

def test_missing_shell_fails() -> None:
    _build_chain()
    backup = SHELL.with_suffix(SHELL.suffix + ".bak")
    try:
        SHELL.rename(backup)
        res = _run()
        assert res.returncode != 0
        assert "verdict: failed" in res.stdout
    finally:
        if backup.is_file():
            backup.rename(SHELL)


# ── 14. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    _build_chain()
    res = subprocess.run(
        ["bash", str(WRAPPER)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=_base_env(),
    )
    assert res.returncode == 0, res.stderr
    assert "phase5c_status: success" in res.stdout


# ── 15-16. CI-C alignment + static boundary (wrapper) ─────────────────────────

def test_ci_c_alignment() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    assert "/home/ubuntu/Affiliate-Ai" not in text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in text
    for pattern in (r"\bcurl\b", r"\bwget\b", r"\bnc\b", r"\bnetcat\b", r"https?://"):
        assert not re.search(pattern, text), f"network token in wrapper: {pattern}"


def test_wrapper_no_approved_workflow_refs() -> None:
    text = WRAPPER.read_text(encoding="utf-8")
    for ref in (
        "run_phase2g",
        "run_phase2h",
        "run_phase2i",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ):
        assert ref not in text, f"wrapper references approved workflow: {ref}"


# ── 17. no forbidden body ingestion ───────────────────────────────────────────

def test_verifier_does_not_ingest_phase4_html_bodies() -> None:
    src = VERIFY.read_text(encoding="utf-8")
    # Only the Phase 5B shell body is read; link targets are existence-only.
    assert src.count(".read_text(") == 1
    assert "phase4b-ui-snapshot/index.html\").read_text" not in src
    assert "phase4c-snapshot-catalog/index.html\").read_text" not in src
