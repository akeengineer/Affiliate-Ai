from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_SCRIPT = REPO_ROOT / "scripts/dev/generate_weekly_report.py"
SAMPLE_ROOT = REPO_ROOT / "vault/samples"


def run_report(input_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(REPORT_SCRIPT),
            "--input-dir",
            str(input_dir),
            "--report-week",
            "2026-W26",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_generate_weekly_report_from_sample_notes() -> None:
    completed = run_report(SAMPLE_ROOT)

    assert completed.returncode == 0, completed.stderr
    report = completed.stdout
    assert "type: weekly_report" in report
    assert "report_week: 2026-W26" in report
    assert "candidate_count: 1" in report
    assert "small_batch_test_count: 1" in report
    assert "## Small Batch Test" in report
    assert "Smart Desk Pad" in report
    assert "Votes: 3" in report
    assert "Compliance: approved" in report


def test_generate_weekly_report_shows_missing_signals(tmp_path: Path) -> None:
    products_dir = tmp_path / "products"
    votes_dir = tmp_path / "votes"
    compliance_dir = tmp_path / "compliance"
    products_dir.mkdir()
    votes_dir.mkdir()
    compliance_dir.mkdir()

    (products_dir / "product.md").write_text(
        "\n".join(
            [
                "---",
                "type: product_candidate",
                "product_id: prod-missing",
                "product_name: Missing Signals Product",
                "marketplace: TikTok Shop",
                "currency: USD",
                "demand_score: 78",
                "trend_velocity_score: 80",
                "marketplace_rank_score: 77",
                "commission_score: 74",
                "content_fit_score: 76",
                "competition_gap_score: 70",
                "risk_score: 28",
                "trend_signal_note: ",
                "marketplace_signal_note: signals/marketplace.md",
                "commission_signal_note: ",
                "compliance_result_note: ",
                "status: scored",
                "created_at: 2026-06-25T15:00:00Z",
                "updated_at: 2026-06-25T15:00:00Z",
                "---",
                "",
                "# Missing Signals Product",
            ]
        ),
        encoding="utf-8",
    )

    completed = run_report(tmp_path)

    assert completed.returncode == 0, completed.stderr
    report = completed.stdout
    assert "Missing signals: trend_signal_note, commission_signal_note, compliance_result_note" in report
