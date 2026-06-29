from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORT_SCRIPT = REPO_ROOT / "scripts/dev/import_product_candidates.py"
TASK_FILE = REPO_ROOT / "codex/tasks/007-phase2d-manual-import.md"
SAMPLE_CSV = REPO_ROOT / "vault/samples/import/product-candidates.csv"
OUTPUT_ROOT = REPO_ROOT / "tmp/phase2d-import"
PRODUCTS_DIR = OUTPUT_ROOT / "products"
PHASE2E_OUTPUT_ROOT = REPO_ROOT / "tmp/phase2e-import-score-report"
PHASE2E_PRODUCTS_DIR = PHASE2E_OUTPUT_ROOT / "products"
SCORE_SCRIPT = REPO_ROOT / "scripts/dev/score_product.py"
REPORT_SCRIPT = REPO_ROOT / "scripts/dev/generate_weekly_report.py"


def run_import(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(IMPORT_SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_score(note_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCORE_SCRIPT), str(note_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


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


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([",".join(row) for row in rows]) + "\n",
        encoding="utf-8",
    )


def test_phase2d_import_artifacts_exist() -> None:
    assert TASK_FILE.is_file()
    assert SAMPLE_CSV.is_file()
    assert IMPORT_SCRIPT.is_file()
    assert os.access(IMPORT_SCRIPT, os.X_OK)


def test_import_product_candidates_dry_run_writes_nothing() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)

    completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(PRODUCTS_DIR),
        "--dry-run",
    )

    assert completed.returncode == 0, completed.stderr
    assert "phase2d_import: dry_run" in completed.stdout
    assert "validated_rows: 1" in completed.stdout
    assert not PRODUCTS_DIR.exists()


def test_import_product_candidates_writes_markdown_notes() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)

    completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode == 0, completed.stderr
    assert "phase2d_import: success" in completed.stdout
    assert "imported_rows: 1" in completed.stdout

    note_path = PRODUCTS_DIR / "prod-laptop-stand.md"
    assert note_path.is_file()
    frontmatter_text = note_path.read_text(encoding="utf-8").split("---\n", 2)[1]
    frontmatter = yaml.safe_load(frontmatter_text)
    assert frontmatter["type"] == "product_candidate"
    assert frontmatter["product_id"] == "prod-laptop-stand"
    assert frontmatter["status"] == "draft"
    assert frontmatter["demand_score"] == 83
    assert frontmatter["product_url"] == "https://example.com/products/laptop-stand"


def test_import_product_candidates_allows_phase2e_output_root() -> None:
    shutil.rmtree(PHASE2E_OUTPUT_ROOT, ignore_errors=True)

    completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(PHASE2E_PRODUCTS_DIR),
    )

    assert completed.returncode == 0, completed.stderr
    assert "phase2d_import: success" in completed.stdout
    assert (PHASE2E_PRODUCTS_DIR / "prod-laptop-stand.md").is_file()


def test_import_product_candidates_rejects_missing_required_columns() -> None:
    input_csv = OUTPUT_ROOT / "input/missing-columns.csv"
    write_csv(
        input_csv,
        [
            ["product_id", "product_name", "marketplace", "currency", "demand_score"],
            ["prod-missing", "Missing Product", "TikTok Shop", "USD", "80"],
        ],
    )

    completed = run_import(
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode != 0
    assert "Missing required columns" in completed.stderr


def test_import_product_candidates_rejects_unknown_columns() -> None:
    input_csv = OUTPUT_ROOT / "input/unknown-columns.csv"
    write_csv(
        input_csv,
        [
            [
                "product_id",
                "product_name",
                "marketplace",
                "currency",
                "demand_score",
                "trend_velocity_score",
                "marketplace_rank_score",
                "commission_score",
                "content_fit_score",
                "competition_gap_score",
                "risk_score",
                "extra_field",
            ],
            [
                "prod-extra",
                "Extra Product",
                "TikTok Shop",
                "USD",
                "80",
                "80",
                "80",
                "80",
                "80",
                "80",
                "20",
                "boom",
            ],
        ],
    )

    completed = run_import(
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode != 0
    assert "Unknown columns" in completed.stderr


def test_import_product_candidates_rejects_out_of_range_scores() -> None:
    input_csv = OUTPUT_ROOT / "input/bad-scores.csv"
    write_csv(
        input_csv,
        [
            [
                "product_id",
                "product_name",
                "marketplace",
                "currency",
                "demand_score",
                "trend_velocity_score",
                "marketplace_rank_score",
                "commission_score",
                "content_fit_score",
                "competition_gap_score",
                "risk_score",
            ],
            [
                "prod-bad-score",
                "Bad Score Product",
                "TikTok Shop",
                "USD",
                "101",
                "80",
                "80",
                "80",
                "80",
                "80",
                "20",
            ],
        ],
    )

    completed = run_import(
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode != 0
    assert "demand_score" in completed.stderr
    assert "0-100" in completed.stderr


def test_import_product_candidates_rejects_duplicate_product_ids() -> None:
    input_csv = OUTPUT_ROOT / "input/duplicate-product-ids.csv"
    write_csv(
        input_csv,
        [
            [
                "product_id",
                "product_name",
                "marketplace",
                "currency",
                "demand_score",
                "trend_velocity_score",
                "marketplace_rank_score",
                "commission_score",
                "content_fit_score",
                "competition_gap_score",
                "risk_score",
            ],
            [
                "prod-dup",
                "Duplicate Product 1",
                "TikTok Shop",
                "USD",
                "80",
                "80",
                "80",
                "80",
                "80",
                "80",
                "20",
            ],
            [
                "prod-dup",
                "Duplicate Product 2",
                "TikTok Shop",
                "USD",
                "81",
                "81",
                "81",
                "81",
                "81",
                "81",
                "21",
            ],
        ],
    )

    completed = run_import(
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode != 0
    assert "Duplicate product_id" in completed.stderr


def test_import_product_candidates_rejects_unsafe_input_path(tmp_path: Path) -> None:
    input_csv = tmp_path / "outside.csv"
    write_csv(
        input_csv,
        [
            [
                "product_id",
                "product_name",
                "marketplace",
                "currency",
                "demand_score",
                "trend_velocity_score",
                "marketplace_rank_score",
                "commission_score",
                "content_fit_score",
                "competition_gap_score",
                "risk_score",
            ],
            [
                "prod-outside",
                "Outside Product",
                "TikTok Shop",
                "USD",
                "80",
                "80",
                "80",
                "80",
                "80",
                "80",
                "20",
            ],
        ],
    )

    completed = run_import(
        "--input-csv",
        str(input_csv),
        "--output-dir",
        str(PRODUCTS_DIR),
    )

    assert completed.returncode != 0
    assert "Unsafe input_csv path" in completed.stderr


def test_import_product_candidates_rejects_unsafe_output_path(tmp_path: Path) -> None:
    completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(tmp_path / "outside-products"),
    )

    assert completed.returncode != 0
    assert "Unsafe output_dir path" in completed.stderr


def test_import_product_candidates_rejects_vault_products_output_path() -> None:
    completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(REPO_ROOT / "vault/products"),
    )

    assert completed.returncode != 0
    assert "Unsafe output_dir path" in completed.stderr


def test_imported_note_scores_with_existing_score_script() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)
    import_completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(PRODUCTS_DIR),
    )
    assert import_completed.returncode == 0, import_completed.stderr

    note_path = PRODUCTS_DIR / "prod-laptop-stand.md"
    score_completed = run_score(note_path)
    assert score_completed.returncode == 0, score_completed.stderr

    payload = json.loads(score_completed.stdout)
    assert payload["product_id"] == "prod-laptop-stand"
    assert payload["score_decision"] == "small_batch_test"
    assert payload["confidence_score"] == 100


def test_imported_notes_work_with_weekly_report() -> None:
    shutil.rmtree(OUTPUT_ROOT, ignore_errors=True)
    import_completed = run_import(
        "--input-csv",
        str(SAMPLE_CSV),
        "--output-dir",
        str(PRODUCTS_DIR),
    )
    assert import_completed.returncode == 0, import_completed.stderr

    report_completed = run_report(OUTPUT_ROOT)
    assert report_completed.returncode == 0, report_completed.stderr
    assert "candidate_count: 1" in report_completed.stdout
    assert "Laptop Stand" in report_completed.stdout
