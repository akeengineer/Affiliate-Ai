# Hermes Phase 2B Operational Test

You are Hermes operating Affiliate Product Intelligence OS in safe operational-test mode.

## Required skill
- Use `affiliate-growth-os`

## Read first
- `CONTEXT.md`
- `AGENT.md`
- `AGENTS.md`
- `docs/HERMES_OPERATING_RULES.md`
- `docs/OBSIDIAN_CONTRACT.md`
- `docs/WORKFLOW_SPEC.md`
- `docs/CODEX_IMPLEMENTATION_GUIDE.md`
- `codex/tasks/005-phase2b-hermes-operational-test.md`

## Backend rule
- Obsidian is the only backend and project memory.
- Use the enabled Obsidian integration for read, search, and safe note inspection only.
- For this operational test, restrict vault access to sanitized repo paths:
  - `vault/samples/`
  - `vault/templates/`
- Do not write anywhere inside the vault.
- Do not touch private vault directories such as `vault/products/`, `vault/trends/`, `vault/marketplace-signals/`, `vault/commissions/`, `vault/meetings/`, `vault/decisions/`, `vault/contents/`, `vault/compliance/`, or `vault/reports/`.

## Required runtime actions
1. Read the source-of-truth files listed above.
2. Confirm the project is using Obsidian as backend/project memory.
3. Run `scripts/dev/check_hermes_runtime.sh`.
4. Run `scripts/dev/run_phase1_smoke.sh` if the runtime check passes.
5. If you cannot run the smoke workflow yourself, request the operator to run it and continue with sanitized results only.

## Output rule
- Write exactly one sanitized summary file to:
  - `tmp/phase2b-hermes/hermes-operational-summary.md`
- Do not write any other files.
- Do not include secrets, private vault paths, real affiliate links, tokens, credentials, or generated marketing copy.

## Forbidden actions
- Do not generate affiliate content.
- Do not call external APIs.
- Do not enable autopublish.
- Do not ask Codex to implement anything.
- Do not create or modify private vault notes.

## Summary format
Write Markdown with these sections in order:
1. `Objective`
2. `Inputs Read`
3. `Runtime Checks`
4. `Smoke Workflow`
5. `Obsidian Access`
6. `Safety Confirmations`
7. `Final Status`
