from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/dev/run_phase2f_hermes_orchestration.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/009-phase2f-hermes-import-score-report.md"
PROMPT_FILE = REPO_ROOT / "prompts/workflows/hermes-phase2f-import-score-report.md"
SAMPLE_CSV = REPO_ROOT / "vault/samples/import/product-candidates.csv"
OUTPUT_DIR = REPO_ROOT / "tmp/phase2f-hermes"
SUMMARY_PATH = OUTPUT_DIR / "operational-summary-2026-W26.md"

PRIVATE_VAULT_PATHS = [
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
]


def run_phase2f(*, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), str(SAMPLE_CSV), "2026-W26"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_phase2f_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert PROMPT_FILE.is_file()
    assert SCRIPT_PATH.is_file()
    assert os.access(SCRIPT_PATH, os.X_OK)


def test_run_phase2f_orchestration_passes() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    completed = run_phase2f(env=os.environ.copy())

    assert completed.returncode == 0, completed.stderr
    assert "phase2f_status: success" in completed.stdout
    assert "summary_path:" in completed.stdout
    assert SUMMARY_PATH.is_file()


def test_run_phase2f_summary_has_correct_frontmatter() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    run_phase2f(env=os.environ.copy())

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "type: hermes_operational_summary" in text
    assert "report_week: 2026-W26" in text
    assert "phase2e_status: success" in text


def test_run_phase2f_summary_has_no_private_vault_paths() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    run_phase2f(env=os.environ.copy())

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    for private_path in PRIVATE_VAULT_PATHS:
        assert private_path not in text, f"Summary references private vault path: {private_path}"


def test_run_phase2f_fails_when_autopublish_true() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    completed = run_phase2f(env={**os.environ, "ENABLE_AUTOPUBLISH": "true"})

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in completed.stderr
    assert not OUTPUT_DIR.exists()


def test_run_phase2f_fails_when_openai_direct_enabled() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    completed = run_phase2f(env={**os.environ, "ENABLE_OPENAI_API_DIRECT": "true"})

    assert completed.returncode != 0
    assert "ENABLE_OPENAI_API_DIRECT=true is not allowed" in completed.stderr
    assert not OUTPUT_DIR.exists()


def test_run_phase2f_summary_has_no_affiliate_content_markers() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    run_phase2f(env=os.environ.copy())

    text = SUMMARY_PATH.read_text(encoding="utf-8")
    content_markers = [
        "content_draft",
        "campaign_copy",
        "tiktok_script",
        "hook_text",
        "blog_post",
        "autopublish",
    ]
    for marker in content_markers:
        assert marker not in text, f"Summary contains affiliate content marker: {marker}"
