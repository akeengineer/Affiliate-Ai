# Task 009 - Phase 2F Hermes Import Score Report

## Objective

Prove Hermes can safely orchestrate the Phase 2E import-score-report workflow by:
1. Running all guardrail checks.
2. Invoking `scripts/dev/run_phase2e_import_score_report.sh`.
3. Writing a sanitized operational summary to `tmp/phase2f-hermes/`.
4. Validating the summary contains no private vault paths.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/HERMES_OPERATING_RULES.md
- docs/OBSIDIAN_CONTRACT.md
- docs/WORKFLOW_SPEC.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- hermes/skills/affiliate-growth-os/SKILL.md
- scripts/dev/check_hermes_runtime.sh
- scripts/dev/run_phase2e_import_score_report.sh
- tests/test_phase2b_hermes_runtime.py

## Scope

Create:

- `codex/tasks/009-phase2f-hermes-import-score-report.md`
- `prompts/workflows/hermes-phase2f-import-score-report.md`
- `scripts/dev/run_phase2f_hermes_orchestration.sh`
- `tests/test_phase2f_hermes_orchestration.py`

Do not modify Phase 2E files unless a real bug is found.

## Requirements

- Accept `<input-csv>` and `<report-week>` from the command line.
- Fail fast if `ENABLE_AUTOPUBLISH=true`.
- Fail fast if `ENABLE_OPENAI_API_DIRECT=true`.
- Fail fast if Phase 2E script is missing or not executable.
- Run `scripts/dev/run_phase2e_import_score_report.sh` with provided args.
- Extract `imported_products` and `score_json_files` from Phase 2E stdout.
- Write sanitized operational summary to `tmp/phase2f-hermes/operational-summary-<week>.md`.
- Validate summary frontmatter contains `type: hermes_operational_summary`.
- Validate summary does not reference private vault paths:
  - vault/products
  - vault/trends
  - vault/marketplace-signals
  - vault/commissions
  - vault/meetings
  - vault/decisions
  - vault/contents
  - vault/compliance
  - vault/reports
  - vault/.obsidian
- Print `phase2f_status: success`.
- Do not write to private vault directories.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not implement autopublish.
- Do not add a database, FastAPI, or UI.

## Acceptance criteria

- `bash -n scripts/dev/run_phase2f_hermes_orchestration.sh` exits `0`.
- `bash scripts/dev/run_phase2f_hermes_orchestration.sh vault/samples/import/product-candidates.csv 2026-W26` exits `0`.
- `tmp/phase2f-hermes/operational-summary-2026-W26.md` is created.
- Summary frontmatter contains `type: hermes_operational_summary`.
- Summary contains no private vault paths.
- `ENABLE_AUTOPUBLISH=true` → exit non-zero.
- `ENABLE_OPENAI_API_DIRECT=true` → exit non-zero.

## Tests required

- `python -m pytest -q tests/test_phase2f_hermes_orchestration.py`
- `python -m pytest -q`
