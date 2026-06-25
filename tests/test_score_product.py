from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCORE_SCRIPT = REPO_ROOT / "scripts/dev/score_product.py"
SAMPLE_NOTE = REPO_ROOT / "vault/samples/products/smart-desk-pad.md"


def run_score(note_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCORE_SCRIPT), str(note_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def make_product_note(
    tmp_path: Path,
    *,
    demand_score: int = 80,
    trend_velocity_score: int = 80,
    marketplace_rank_score: int = 80,
    commission_score: int = 80,
    content_fit_score: int = 80,
    competition_gap_score: int = 80,
    risk_score: int = 20,
    trend_signal_note: str = "signals/trend.md",
    marketplace_signal_note: str = "signals/marketplace.md",
    commission_signal_note: str = "signals/commission.md",
    compliance_result_note: str = "compliance/result.md",
) -> Path:
    note_path = tmp_path / "product.md"
    note_path.write_text(
        "\n".join(
            [
                "---",
                "type: product_candidate",
                "product_id: prod-test",
                "product_name: Test Product",
                "marketplace: TikTok Shop",
                "currency: USD",
                f"demand_score: {demand_score}",
                f"trend_velocity_score: {trend_velocity_score}",
                f"marketplace_rank_score: {marketplace_rank_score}",
                f"commission_score: {commission_score}",
                f"content_fit_score: {content_fit_score}",
                f"competition_gap_score: {competition_gap_score}",
                f"risk_score: {risk_score}",
                f"trend_signal_note: {trend_signal_note}",
                f"marketplace_signal_note: {marketplace_signal_note}",
                f"commission_signal_note: {commission_signal_note}",
                f"compliance_result_note: {compliance_result_note}",
                "status: draft",
                "created_at: 2026-06-25T15:00:00Z",
                "updated_at: 2026-06-25T15:00:00Z",
                "---",
                "",
                "# Test Product",
            ]
        ),
        encoding="utf-8",
    )
    return note_path


@pytest.mark.parametrize(
    ("scores", "expected_decision"),
    [
        (
            {
                "demand_score": 90,
                "trend_velocity_score": 90,
                "marketplace_rank_score": 90,
                "commission_score": 90,
                "content_fit_score": 90,
                "competition_gap_score": 90,
                "risk_score": 10,
            },
            "launch",
        ),
        (
            {
                "demand_score": 80,
                "trend_velocity_score": 80,
                "marketplace_rank_score": 80,
                "commission_score": 80,
                "content_fit_score": 80,
                "competition_gap_score": 80,
                "risk_score": 20,
            },
            "small_batch_test",
        ),
        (
            {
                "demand_score": 70,
                "trend_velocity_score": 70,
                "marketplace_rank_score": 70,
                "commission_score": 70,
                "content_fit_score": 70,
                "competition_gap_score": 70,
                "risk_score": 30,
            },
            "watchlist",
        ),
        (
            {
                "demand_score": 50,
                "trend_velocity_score": 50,
                "marketplace_rank_score": 50,
                "commission_score": 50,
                "content_fit_score": 50,
                "competition_gap_score": 50,
                "risk_score": 50,
            },
            "reject",
        ),
    ],
)
def test_score_product_decision_thresholds(
    tmp_path: Path, scores: dict[str, int], expected_decision: str
) -> None:
    note_path = make_product_note(tmp_path, **scores)

    completed = run_score(note_path)

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["score_decision"] == expected_decision


def test_score_product_rejects_out_of_range_values(tmp_path: Path) -> None:
    note_path = make_product_note(tmp_path, demand_score=101)

    completed = run_score(note_path)

    assert completed.returncode != 0
    assert "demand_score" in completed.stderr
    assert "0-100" in completed.stderr


def test_score_product_reduces_confidence_for_missing_signal_refs(tmp_path: Path) -> None:
    note_path = make_product_note(
        tmp_path,
        trend_signal_note="",
        commission_signal_note="",
        compliance_result_note="",
    )

    completed = run_score(note_path)

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["confidence_score"] == 50
    assert payload["missing_signal_count"] == 3
    assert payload["missing_signals"] == [
        "trend_signal_note",
        "commission_signal_note",
        "compliance_result_note",
    ]


def test_score_product_rejects_malformed_frontmatter(tmp_path: Path) -> None:
    note_path = tmp_path / "broken.md"
    note_path.write_text("type: product_candidate\nproduct_id: missing-fence", encoding="utf-8")

    completed = run_score(note_path)

    assert completed.returncode != 0
    assert "frontmatter" in completed.stderr.lower()


def test_score_product_reads_sample_note() -> None:
    completed = run_score(SAMPLE_NOTE)

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["product_id"] == "prod-smart-desk-pad"
    assert payload["score_decision"] == "small_batch_test"
    assert payload["confidence_score"] == 100
