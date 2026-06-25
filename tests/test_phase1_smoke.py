from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_SCRIPT = REPO_ROOT / "scripts/dev/run_phase1_smoke.sh"
OUTPUT_ROOT = REPO_ROOT / "tmp/phase1-smoke"


def test_run_phase1_smoke_creates_score_outputs_and_report() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)

    completed = subprocess.run(
        ["bash", str(SMOKE_SCRIPT), "2026-W26"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTEST_ADDOPTS": '-k "not phase1_smoke"',
        },
    )

    assert completed.returncode == 0, completed.stderr
    assert "scored_products: 1" in completed.stdout
    assert "pytest: passed" in completed.stdout
    assert "final_status: success" in completed.stdout

    score_path = OUTPUT_ROOT / "scores/smart-desk-pad.json"
    report_path = OUTPUT_ROOT / "weekly-report-2026-W26.md"
    assert score_path.exists()
    assert report_path.exists()

    payload = json.loads(score_path.read_text(encoding="utf-8"))
    assert payload["product_id"] == "prod-smart-desk-pad"
    report_text = report_path.read_text(encoding="utf-8")
    assert report_text.startswith("---\n")
    assert "type: weekly_report" in report_text
