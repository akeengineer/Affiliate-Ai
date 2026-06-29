# Task 017 - Phase 3C Operator Command Center CLI

## Objective

Provide one safe operator entrypoint that routes to existing safe wrappers.
It implements no business logic, writes no vault, calls no external APIs, and
never routes to the approved Phase 2G/2H/2I vault-writing workflows.

## Design decisions (confirmed)

- Bash-only dispatcher at `scripts/dev/command_center.sh`.
- No Python core; no `run_phase3c_` prefix (this is an operator entrypoint,
  not a one-shot phase proof wrapper).
- Routes only to: `run_phase2_full_dry_run.sh` (2E/2F/2J), Phase 3A, Phase 3B.
- No new tmp directory; `.gitignore` is not modified.

## Read first

- AGENTS.md
- CONTEXT.md
- scripts/dev/run_phase2_full_dry_run.sh
- scripts/dev/run_phase3a_dashboard_summary.sh
- scripts/dev/run_phase3b_portfolio_dashboard.sh

## Scope

Create:

- `codex/tasks/017-phase3c-operator-command-center.md`
- `scripts/dev/command_center.sh`
- `tests/test_phase3c_operator_command_center.py`

Update:

- `scripts/dev/README.md` (script index entry)

Do not modify Phase 2, Phase 3A, or Phase 3B workflows unless a real bug is found.

## Commands

```
bash scripts/dev/command_center.sh <command> [args...]

help                                       Print usage and exit 0
status                                     Read-only runtime inventory
doctor                                     Validate scripts/wrappers/guardrail flags
dry-run <csv_path> <week> <product_id>     exec run_phase2_full_dry_run.sh
product <product_id> <week> [--write]      exec run_phase3a_dashboard_summary.sh
portfolio <week> [--top N] [--write]       exec run_phase3b_portfolio_dashboard.sh
```

## Guardrails

- Action commands (dry-run/product/portfolio) fail before routing if
  `ENABLE_AUTOPUBLISH=true` or `ENABLE_OPENAI_API_DIRECT=true`.
- `doctor` FAILs (non-zero) if any of `ENABLE_AUTOPUBLISH`,
  `ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`, `APPROVE_DECISION`,
  `APPROVE_FINALIZE` is set to `true`.
- Validate `week` (`^[0-9]{4}-W[0-9]{2}$`) and `product_id` (`^[a-z0-9-]+$`).
- Quote every argument; use safe bash arrays under `set -euo pipefail`.
- Never set/export `APPROVE_*`; never route to 2G/2H/2I; no vault writes.
- `status`/`doctor` emit key-value fields only — no vault paths or bodies.

## Tests

`tests/test_phase3c_operator_command_center.py` covers help/usage, unknown
command, status keys + no vault paths, doctor pass/fail (including unsafe env
flags), routing of dry-run/product/portfolio (including `--write`/`--top`
pass-through), input validation, static checks that no 2G/2H/2I or vault-write
scripts are referenced, and that no vault files are created.
