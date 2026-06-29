# Hermes Phase 2F — Import Score Report Orchestration

## Activation

Activate the `affiliate-growth-os` skill before proceeding.

## Read first

Read these project source-of-truth files before any action:

1. CONTEXT.md
2. AGENT.md
3. AGENTS.md
4. docs/HERMES_OPERATING_RULES.md
5. docs/WORKFLOW_SPEC.md
6. docs/OBSIDIAN_CONTRACT.md
7. hermes/skills/affiliate-growth-os/SKILL.md

## Objective

Orchestrate the Phase 2E import-score-report workflow safely.

## Guardrail checks — verify before running

Assert all of the following before proceeding:

- [ ] `ENABLE_AUTOPUBLISH` is `false` or unset.
- [ ] `ENABLE_OPENAI_API_DIRECT` is `false` or unset.
- [ ] `scripts/dev/run_phase2e_import_score_report.sh` exists and is executable.
- [ ] `codex/tasks/008-phase2e-import-score-report.md` exists.
- [ ] Working directory is `/home/ubuntu/Affiliate-Ai`.

If any guardrail fails, stop and report the failure. Do not proceed.

## Command to run

```bash
bash scripts/dev/run_phase2e_import_score_report.sh <input-csv> <report-week>
```

Example:

```bash
bash scripts/dev/run_phase2e_import_score_report.sh vault/samples/import/product-candidates.csv 2026-W26
```

## After Phase 2E succeeds

1. Read `tmp/phase2e-import-score-report/weekly-report-<week>.md`.
2. Extract: `imported_products` count, `score_json_files` count, `phase2e_status`.
3. Write sanitized operational summary to `tmp/phase2f-hermes/operational-summary-<week>.md`.

## Output — operational summary rules

The summary must:

- Include YAML frontmatter with `type: hermes_operational_summary`.
- Include `report_week`, `phase2e_status`, `imported_products`, `score_json_files`.
- Reference only the relative path `tmp/phase2e-import-score-report/weekly-report-<week>.md`.
- NOT reference private vault paths:
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
- NOT include affiliate content text or campaign copy.
- NOT include external API URLs.

## Hard stops — Hermes must NOT

- Write to any private vault directory.
- Call external APIs.
- Generate affiliate content or campaign copy.
- Ask Codex to implement new features.
- Enable autopublish.

## Output format — Hermes report

Produce a final report with:

1. Objective
2. Guardrails verified
3. Phase 2E execution result (imported_products, score_json_files, report path)
4. Operational summary path written
5. Status: `success` or `blocked` (with reason)
