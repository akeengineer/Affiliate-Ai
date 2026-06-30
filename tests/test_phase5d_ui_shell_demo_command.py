from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ORCH = REPO_ROOT / "scripts/dev/run_phase5d_ui_shell_demo.sh"
WRITER = REPO_ROOT / "scripts/dev/build_ui_shell_demo_summary.py"
TASK_FILE = REPO_ROOT / "codex/tasks/032-phase5d-ui-shell-demo-command.md"
DOC = REPO_ROOT / "docs/UI_SHELL.md"
GITIGNORE = REPO_ROOT / ".gitignore"

OUT_DIR = REPO_ROOT / "tmp/phase5d-ui-shell-demo"
SUMMARY = OUT_DIR / "ui-shell-demo-summary.json"
REPORT = OUT_DIR / "UI_SHELL_DEMO.md"
PHASE5C_SUMMARY = REPO_ROOT / "tmp/phase5c-ui-shell-verifier/verification-summary.json"

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
        ["bash", str(ORCH), *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=env or _base_env(),
    )


def _writer(*args: str):
    return subprocess.run(
        ["python", str(WRITER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=_base_env(),
    )


# ── 1-5. existence / syntax / gitignore ───────────────────────────────────────

def test_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert DOC.is_file()
    assert ORCH.is_file()
    assert WRITER.is_file()


def test_orchestrator_executable() -> None:
    assert os.access(ORCH, os.X_OK)


def test_orchestrator_syntax_ok() -> None:
    res = subprocess.run(["bash", "-n", str(ORCH)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_writer_compiles() -> None:
    res = subprocess.run(["python", "-m", "py_compile", str(WRITER)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_gitignore_includes_phase5d() -> None:
    assert "tmp/phase5d-ui-shell-demo/" in GITIGNORE.read_text(encoding="utf-8")


# ── 6-8. argument + guardrail validation ──────────────────────────────────────

def test_invalid_week_fails() -> None:
    assert _run("2026W26").returncode != 0


def test_wrong_arg_count_fails() -> None:
    assert _run().returncode != 0
    assert _run(WEEK, "extra").returncode != 0


@pytest.mark.parametrize("flag", GUARDRAIL_FLAGS)
def test_guardrail_flags_fail(flag: str) -> None:
    assert _run(WEEK, env=_base_env(**{flag: "true"})).returncode != 0


# ── 9-10. end-to-end ready + content ──────────────────────────────────────────

def test_end_to_end_ready() -> None:
    res = _run(WEEK)
    assert res.returncode == 0, res.stderr
    for token in (
        "ui_shell_demo_step: phase4e -> PASS",
        "ui_shell_demo_step: phase5b -> PASS",
        "ui_shell_demo_step: phase5c -> PASS",
        "ui_shell_verdict: ready",
        "ui_shell_demo_status: ready",
        "phase5d_status: success",
    ):
        assert token in res.stdout, f"missing line: {token}"
    assert SUMMARY.is_file()
    assert REPORT.is_file()
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["status"] == "ready"


def test_summary_and_report_content() -> None:
    assert _run(WEEK).returncode == 0
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert data["type"] == "phase5d_ui_shell_demo"
    assert data["report_week"] == WEEK
    assert set(data["steps"]) == {"phase4e", "phase5b", "phase5c"}
    assert data["artifacts"]["phase5b_shell"] == "tmp/phase5b-ui-shell/index.html"
    report = REPORT.read_text(encoding="utf-8")
    assert "Commands run" in report
    assert "Guardrails" in report


# ── 11. output self-safety ────────────────────────────────────────────────────

def test_output_safety() -> None:
    assert _run(WEEK).returncode == 0
    blob = SUMMARY.read_text(encoding="utf-8") + REPORT.read_text(encoding="utf-8")
    for token in (
        "http://",
        "https://",
        "file://",
        "/home/ubuntu/Affiliate-Ai",
        "vault/products",
        "vault/decisions",
        "tag=",
        "affiliate=",
        "<script",
        "run_phase2g",
        "promote_product_candidates.py",
        "create_decision.py",
        "finalize_decision.py",
    ):
        assert token not in blob, f"output echoed forbidden token: {token}"


# ── 12. verdict mapping unit tests (writer in isolation) ──────────────────────

def test_writer_ready() -> None:
    res = _writer("--week", WEEK, "--phase4e", "PASS", "--phase5b", "PASS", "--phase5c", "PASS", "--verdict", "ready")
    assert res.returncode == 0
    assert "ui_shell_demo_status: ready" in res.stdout
    assert "phase5d_status: success" in res.stdout
    assert json.loads(SUMMARY.read_text(encoding="utf-8"))["status"] == "ready"


def test_writer_warning() -> None:
    res = _writer("--week", WEEK, "--phase4e", "PASS", "--phase5b", "PASS", "--phase5c", "PASS", "--verdict", "warning")
    assert res.returncode == 0
    assert "ui_shell_demo_status: warning" in res.stdout
    assert "phase5d_status: success" in res.stdout
    assert json.loads(SUMMARY.read_text(encoding="utf-8"))["status"] == "warning"


def test_writer_failed_verdict() -> None:
    res = _writer("--week", WEEK, "--phase4e", "PASS", "--phase5b", "PASS", "--phase5c", "PASS", "--verdict", "failed")
    assert res.returncode == 1
    assert "ui_shell_demo_status: failed" in res.stdout
    assert "phase5d_status: failed" in res.stdout
    assert json.loads(SUMMARY.read_text(encoding="utf-8"))["status"] == "failed"


def test_writer_step_fail_overrides_ready() -> None:
    res = _writer("--week", WEEK, "--phase4e", "PASS", "--phase5b", "FAIL", "--phase5c", "PASS", "--verdict", "ready")
    assert res.returncode == 1
    assert "ui_shell_demo_status: failed" in res.stdout
    assert "phase5d_status: failed" in res.stdout


# ── 13. failed path via orchestrator (guardrail flag) ─────────────────────────

def test_failed_path_guardrail() -> None:
    res = _run(WEEK, env=_base_env(ENABLE_AUTOPUBLISH="true"))
    assert res.returncode != 0


# ── 14. no bypass of Phase 5C ─────────────────────────────────────────────────

def test_orchestrator_runs_phase5c() -> None:
    assert "run_phase5c_ui_shell_verifier.sh" in ORCH.read_text(encoding="utf-8")


def test_end_to_end_creates_phase5c_summary() -> None:
    PHASE5C_SUMMARY.unlink(missing_ok=True)
    assert _run(WEEK).returncode == 0
    assert PHASE5C_SUMMARY.is_file()


# ── 15. cross-CWD ─────────────────────────────────────────────────────────────

def test_cross_cwd(tmp_path: Path) -> None:
    res = subprocess.run(
        ["bash", str(ORCH), WEEK],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=_base_env(),
    )
    assert res.returncode == 0, res.stderr
    assert "phase5d_status: success" in res.stdout


# ── 16. CI-C alignment ────────────────────────────────────────────────────────

def test_ci_c_alignment() -> None:
    text = ORCH.read_text(encoding="utf-8")
    assert "/home/ubuntu/Affiliate-Ai" not in text
    assert 'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' in text
    for pattern in (r"\bcurl\b", r"\bwget\b", r"\bnc\b", r"\bnetcat\b", r"https?://"):
        assert not re.search(pattern, text), f"network token in orchestrator: {pattern}"


# ── 17. static boundary: no approved-workflow refs in source ──────────────────

def test_no_approved_workflow_refs() -> None:
    for path in (ORCH, WRITER):
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
