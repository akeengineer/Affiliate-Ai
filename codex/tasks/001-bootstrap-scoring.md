# Task 001 — Bootstrap Product Scoring

## Objective

Implement a deterministic product scoring utility that reads Obsidian-compatible product candidate notes and calculates Product Opportunity Score.

## Read first

- AGENTS.md
- docs/SCORING_SPEC.md
- docs/OBSIDIAN_CONTRACT.md

## Scope

Create:

- `scripts/dev/score_product.py`
- `tests/test_score_product.py`

## Requirements

- Parse YAML frontmatter from Markdown files.
- Validate score inputs are 0-100.
- Calculate Product Opportunity Score using `docs/SCORING_SPEC.md`.
- Return decision: `launch`, `small_batch_test`, `watchlist`, or `reject`.
- No external API calls.
- No database.

## Acceptance criteria

- Unit tests cover all thresholds.
- Missing optional signals reduce confidence or fail validation according to implementation notes.
- Script can run against a sample markdown file.
