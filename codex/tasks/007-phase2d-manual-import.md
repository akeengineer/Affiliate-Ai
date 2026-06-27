# Task 007 - Phase 2D Manual Product Import

## Objective

Safely import manually prepared sanitized CSV product candidates into Obsidian-compatible `product_candidate` Markdown notes under `tmp/phase2d-import/`, so the existing scoring and weekly report tools can process them without private vault writes.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/OBSIDIAN_CONTRACT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- scripts/dev/score_product.py
- scripts/dev/generate_weekly_report.py
- tests/test_score_product.py
- tests/test_weekly_report.py

## Scope

Create:

- `codex/tasks/007-phase2d-manual-import.md`
- `scripts/dev/import_product_candidates.py`
- `tests/test_import_product_candidates.py`
- `vault/samples/import/product-candidates.csv`

Update:

- `.gitignore`

## Requirements

- Read sanitized CSV only from safe paths.
- Validate required columns before writing any note.
- Validate score fields as numeric values in `0-100`.
- Convert each valid row into one `product_candidate` Markdown note with YAML frontmatter compatible with `scripts/dev/score_product.py`.
- Support `--dry-run`.
- Default safe output root is `tmp/phase2d-import/products`.
- Do not write to `vault/products` by default.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not implement autopublish.
- Do not add a database, FastAPI, or UI.
- Do not add real affiliate links to samples.

## Acceptance criteria

- `python scripts/dev/import_product_candidates.py --input-csv vault/samples/import/product-candidates.csv --output-dir tmp/phase2d-import/products --dry-run` exits `0` and writes no notes.
- `python scripts/dev/import_product_candidates.py --input-csv vault/samples/import/product-candidates.csv --output-dir tmp/phase2d-import/products` exits `0` and writes Markdown notes under `tmp/phase2d-import/products/`.
- `python scripts/dev/score_product.py tmp/phase2d-import/products/<generated-note>.md` exits `0`.
- `python scripts/dev/generate_weekly_report.py --input-dir tmp/phase2d-import --report-week 2026-W26` exits `0`.
- `tmp/phase2d-import/` is ignored by git.

## Tests required

- `python -m pytest -q tests/test_import_product_candidates.py`
- `python -m pytest -q`
