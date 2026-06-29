from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/dev/run_phase2e_import_score_report.sh"
TASK_FILE = REPO_ROOT / "codex/tasks/008-phase2e-import-score-report.md"
SAMPLE_CSV = REPO_ROOT / "vault/samples/import/product-candidates.csv"
OUTPUT_ROOT = REPO_ROOT / "tmp/phase2e-import-score-report"
PRODUCTS_DIR = OUTPUT_ROOT / "products"
SCORES_DIR = OUTPUT_ROOT / "scores"
REPORT_PATH = OUTPUT_ROOT / "weekly-report-2026-W26.md"


def run_phase2e(*, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), str(SAMPLE_CSV), "2026-W26"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_phase2e_import_score_report_creates_products_scores_and_report() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)

    completed = run_phase2e(env=os.environ.copy())

    assert completed.returncode == 0, completed.stderr
    assert TASK_FILE.is_file()
    assert "imported_products: 1" in completed.stdout
    assert "score_json_files: 1" in completed.stdout
    assert f"report_path: {REPORT_PATH}" in completed.stdout
    assert "final_status: success" in completed.stdout

    product_notes = sorted(PRODUCTS_DIR.glob("*.md"))
    score_files = sorted(SCORES_DIR.glob("*.json"))
    assert len(product_notes) == 1
    assert len(score_files) == 1
    assert REPORT_PATH.is_file()

    payload = json.loads(score_files[0].read_text(encoding="utf-8"))
    assert payload["product_id"] == "prod-laptop-stand"
    assert payload["score_decision"] == "small_batch_test"

    report_text = REPORT_PATH.read_text(encoding="utf-8")
    assert report_text.startswith("---\n")
    assert "type: weekly_report" in report_text


def test_phase2e_import_score_report_rejects_autopublish_enabled() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)

    completed = run_phase2e(
        env={
            **os.environ,
            "ENABLE_AUTOPUBLISH": "true",
        }
    )

    assert completed.returncode != 0
    assert "ENABLE_AUTOPUBLISH=true is not allowed" in completed.stderr
    assert not OUTPUT_ROOT.exists()
