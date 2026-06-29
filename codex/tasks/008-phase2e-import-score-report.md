# Task 008 - Phase 2E Import Score Report

## Objective

Add one safe command that imports sanitized CSV product candidates, scores the imported Markdown notes, and generates a weekly report entirely under `tmp/phase2e-import-score-report/`.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/OBSIDIAN_CONTRACT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- scripts/dev/import_product_candidates.py
- scripts/dev/score_product.py
- scripts/dev/generate_weekly_report.py
- scripts/dev/run_phase1_smoke.sh
- tests/test_import_product_candidates.py
- tests/test_score_product.py
- tests/test_weekly_report.py

## Scope

Create:

- `codex/tasks/008-phase2e-import-score-report.md`
- `scripts/dev/run_phase2e_import_score_report.sh`
- `tests/test_phase2e_import_score_report.py`

Update:

- `.gitignore`

## Requirements

- Read a sanitized CSV path from the command line.
- Fail fast if `ENABLE_AUTOPUBLISH=true`.
- Clear and recreate `tmp/phase2e-import-score-report/` before writing outputs.
- Import notes via `scripts/dev/import_product_candidates.py`.
- Score imported notes via `scripts/dev/score_product.py`.
- Generate the weekly report via `scripts/dev/generate_weekly_report.py`.
- Write imported notes to `tmp/phase2e-import-score-report/products/`.
- Write score JSON files to `tmp/phase2e-import-score-report/scores/`.
- Write one report to `tmp/phase2e-import-score-report/weekly-report-<week>.md`.
- Validate the report frontmatter includes `type: weekly_report`.
- Print a concise operational summary.
- Do not write to private vault directories.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not implement autopublish.
- Do not add a database, FastAPI, or UI.
- Do not duplicate scoring logic or report logic.

## Acceptance criteria

- `bash -n scripts/dev/run_phase2e_import_score_report.sh` exits `0`.
- `bash scripts/dev/run_phase2e_import_score_report.sh vault/samples/import/product-candidates.csv 2026-W26` exits `0`.
- `tmp/phase2e-import-score-report/products/`, `tmp/phase2e-import-score-report/scores/`, and `tmp/phase2e-import-score-report/weekly-report-2026-W26.md` are created.
- Score JSON count equals imported product note count.
- The report contains `type: weekly_report`.
- The sample imported product scores as `small_batch_test`.
- No private vault paths are written.

## Tests required

- `python -m pytest -q tests/test_phase2e_import_score_report.py`
- `python -m pytest -q`
