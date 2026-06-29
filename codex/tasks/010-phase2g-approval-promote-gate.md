# Task 010 - Phase 2G Approval Promote Gate

## Objective

Add an approval gate that validates and promotes product_candidate notes from
`tmp/phase2e-import-score-report/products/` into `vault/products/`, enriching
each promoted note with computed score fields from the Phase 2E score JSON.

Default mode is dry-run. Promotion requires an explicit `--approve` flag.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/OBSIDIAN_CONTRACT.md
- docs/WORKFLOW_SPEC.md
- docs/HERMES_OPERATING_RULES.md
- scripts/dev/import_product_candidates.py
- scripts/dev/score_product.py
- scripts/dev/run_phase2e_import_score_report.sh
- scripts/dev/run_phase2f_hermes_orchestration.sh
- tests/test_import_product_candidates.py
- tests/test_phase2e_import_score_report.py

## Scope

Create:

- `codex/tasks/010-phase2g-approval-promote-gate.md`
- `scripts/dev/promote_product_candidates.py`
- `scripts/dev/run_phase2g_approval_promote.sh`
- `tests/test_phase2g_approval_promote.py`

Update:

- `.gitignore`

Do not modify Phase 2E or 2F unless a real bug is found.

## Requirements

- Accept `--source-dir` (Phase 2E output root) and `--report-week` from CLI.
- Default mode is dry-run: validate notes, write audit, do not write to vault.
- `--approve` flag enables promotion to `vault/products/`.
- Validate each note:
  - `type: product_candidate`
  - All required frontmatter fields present (OBSIDIAN_CONTRACT)
  - All score fields numeric 0-100
  - `product_id` matches `^[a-z0-9-]+$`
  - Corresponding `scores/<product_id>.json` exists (Phase 2E ran)
  - `score_decision` is not `reject`
  - `product_url`, if present, has no affiliate tracking patterns
  - No field value contains secrets patterns
  - Destination `vault/products/<product_id>.md` does not already exist
- On approval, write enriched note to `vault/products/<product_id>.md`:
  - Embed `product_opportunity_score`, `score_decision`, `confidence_score`,
    `missing_signal_count`, `last_scored_at` from score JSON
  - Set `status: scored`
  - Update `updated_at` to promotion timestamp
  - Preserve all other original fields in template order
- Write audit summary to `tmp/phase2g-approval-promote/audit-<week>.md`
  with `type: phase2g_audit`.
- Print `phase2g_status: dry_run_complete` or `phase2g_status: success`.
- Fail fast if any note is rejected (validate ALL before promoting ANY).
- `source_dir` must be under `tmp/`.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not implement autopublish.
- Do not add a database, FastAPI, or UI.

## Acceptance criteria

- `python -m py_compile scripts/dev/promote_product_candidates.py` exits `0`.
- Dry-run with Phase 2E sample output → exit `0`, `phase2g_status: dry_run_complete`.
- Dry-run creates `tmp/phase2g-approval-promote/audit-2026-W26.md` with
  `type: phase2g_audit` and `mode: dry_run`.
- Dry-run does NOT create any file under `vault/products/`.
- `--approve` run → exit `0`, enriched note in `vault/products/`, `phase2g_status: success`.
- Promoted note has `type: product_candidate`, `status: scored`, `product_opportunity_score`.
- Duplicate promote (destination exists) → exit non-zero, no overwrite.
- Note with affiliate URL pattern → rejected, exit non-zero.
- Note with `score_decision: reject` → not promoted, exit non-zero.
- `ENABLE_AUTOPUBLISH=true` → bash wrapper exits non-zero, no vault writes.

## Tests required

- `python -m pytest -q tests/test_phase2g_approval_promote.py`
- `python -m pytest -q`
