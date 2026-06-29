# Task 015 - Phase 3A CLI Dashboard Summary

## Objective

Provide a single, read-only, operator-facing CLI summary of one product's
lifecycle state, joined across existing Phase 2 artifacts (and optional,
gitignored vault business memory).

The dashboard reads only. It never writes to the vault, never calls external
APIs, and never generates affiliate content. By default it prints to stdout;
with `--write` it also emits a tmp artifact.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- scripts/dev/score_product.py
- scripts/dev/run_phase2j_governance_orchestration.sh

## Scope

Create:

- `codex/tasks/015-phase3a-cli-dashboard-summary.md`
- `scripts/dev/dashboard_summary.py`
- `scripts/dev/run_phase3a_dashboard_summary.sh`
- `tests/test_phase3a_cli_dashboard_summary.py`

Update:

- `.gitignore` (ignore `tmp/phase3a-dashboard/`)
- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2 workflows unless a real bug is found.

## Inputs

Required anchor:

- `tmp/phase2e-import-score-report/scores/<product_id>.json`

Optional (degraded to `missing`/`unknown` when absent):

- `tmp/phase2e-import-score-report/weekly-report-<week>.md`
- `tmp/phase2f-hermes/operational-summary-<week>.md`
- `tmp/phase2j-hermes-governance/governance-summary-<week>.md`
- `vault/products/<product_id>.md` (existence + status only)
- `vault/decisions/dec-<product_id>-<week>.md` (existence + status only)

## Command

```
python scripts/dev/dashboard_summary.py --product-id <id> --week <YYYY-Www> [--write]
bash scripts/dev/run_phase3a_dashboard_summary.sh <id> <YYYY-Www> [--write]
```

## Output

Stdout prints the 12 dashboard fields as `key: value`, then `phase3a_status: success`.
With `--write`, also prints `dashboard_path` and writes
`tmp/phase3a-dashboard/dashboard-<product_id>-<week>.md`.

## Guardrails

- Fail if `ENABLE_AUTOPUBLISH=true` or `ENABLE_OPENAI_API_DIRECT=true`.
- Validate `product_id` (`^[a-z0-9-]+$`) and `week` (`^[0-9]{4}-W[0-9]{2}$`).
- No vault writes. No external APIs. No affiliate content. No UI/API/database.
- Output must not contain private vault paths, affiliate URL patterns,
  secret patterns, or affiliate content markers.

## Tests

`tests/test_phase3a_cli_dashboard_summary.py` covers existence/executability,
happy path, `--write`, degraded mode, missing/invalid inputs, scrubbing,
no-vault-write, optional vault decision derivation, and wrapper guardrails.
