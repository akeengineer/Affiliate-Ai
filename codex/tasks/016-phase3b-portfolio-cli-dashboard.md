# Task 016 - Phase 3B Portfolio CLI Dashboard

## Objective

Provide a single, read-only, multi-product portfolio view for a report week.
It reads every score JSON under `tmp/phase2e-import-score-report/scores/`,
groups products by `score_decision`, ranks them, and reports portfolio-level
counts plus optional vault and Phase 3A enrichment.

The dashboard reads only. It never writes to the vault, never calls external
APIs, and never generates affiliate content. By default it prints to stdout;
with `--write` it also emits a tmp artifact.

## Week semantics (confirmed design)

- Score JSON files do not contain a week, and `scores/` is a flat,
  per-product directory.
- Phase 3B reads ALL `scores/*.json` and does NOT filter by week.
- `--week` is used only for: output artifact naming, optional Phase 3A
  artifact lookup, and vault decision lookup.
- Phase 3B does NOT cross-reference `weekly-report-<week>.md` for membership.

## Read first

- AGENTS.md
- CONTEXT.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- scripts/dev/score_product.py
- scripts/dev/dashboard_summary.py

## Scope

Create:

- `codex/tasks/016-phase3b-portfolio-cli-dashboard.md`
- `scripts/dev/portfolio_dashboard.py`
- `scripts/dev/run_phase3b_portfolio_dashboard.sh`
- `tests/test_phase3b_portfolio_cli_dashboard.py`

Update:

- `.gitignore` (ignore `tmp/phase3b-portfolio-dashboard/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 or Phase 3A workflows unless a real bug is found.

## Reuse from scripts/dev/dashboard_summary.py (import)

`assert_clean`, `_safe_frontmatter`, `_fm_str`, `_now_utc`,
`_check_guardrails`, `WEEK_RE`, `DashboardError`, and the scrub constants.

## Command

```
python scripts/dev/portfolio_dashboard.py --week <YYYY-Www> [--top N] [--write]
bash scripts/dev/run_phase3b_portfolio_dashboard.sh <YYYY-Www> [--top N] [--write]
```

`--top` defaults to 10 and must be an integer >= 1.

## Inputs

- Core: `tmp/phase2e-import-score-report/scores/*.json` (all files; whitelist
  `product_id`, `product_name`, `product_opportunity_score`, `score_decision`,
  `confidence_score`; never emit `input_path` or `note_refs`).
- Optional: `tmp/phase3a-dashboard/dashboard-<product_id>-<week>.md`
  (counted as `phase3a_artifact_count`).
- Optional vault (existence + status only):
  `vault/products/<product_id>.md`, `vault/decisions/dec-<product_id>-<week>.md`.

## Output

Stdout prints portfolio counts, a readable Top N products section, and
`phase3b_status: success`. With `--write`, also prints `portfolio_path` and
writes `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md`.

## Guardrails

- Fail if `ENABLE_AUTOPUBLISH=true` or `ENABLE_OPENAI_API_DIRECT=true`.
- Validate `week` (`^[0-9]{4}-W[0-9]{2}$`) and `--top` (int >= 1).
- Skip malformed/invalid score files (warn to stderr, increment
  `skipped_count`), never crash.
- No vault writes. No external APIs. No affiliate content. No UI/API/database.
- Output must not contain private vault paths, affiliate URL patterns,
  secret patterns, or affiliate content markers.

## Tests

`tests/test_phase3b_portfolio_cli_dashboard.py` covers existence/executability,
counts, grouping, ranking + tie-break, top-N limiting, default top_n, `--write`,
empty scores dir, skipped count, invalid inputs, Phase 3A/vault enrichment,
scrubbing (no `input_path`/`note_refs`/vault paths), no-vault-write, and
wrapper guardrails.
