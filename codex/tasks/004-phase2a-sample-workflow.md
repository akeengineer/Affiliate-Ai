# Task 004 — Phase 2A Sample Workflow

## Objective

Add a single-command smoke workflow for sanitized Phase 1 sample artifacts.

## Read first

- AGENTS.md
- docs/OBSIDIAN_CONTRACT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- scripts/dev/score_product.py
- scripts/dev/generate_weekly_report.py

## Scope

Create:

- `scripts/dev/run_phase1_smoke.sh`

Optional:

- `tests/test_phase1_smoke.py`

## Requirements

- Read only `vault/samples/products/*.md`.
- Write score JSON files to `tmp/phase1-smoke/scores/`.
- Write one weekly report to `tmp/phase1-smoke/weekly-report-<week>.md`.
- Validate the report frontmatter includes `type: weekly_report`.
- Run `python -m pytest -q`.
- Print a concise operational summary.
- Do not write to private vault directories.
- Do not call external APIs.
- Do not add a database.
