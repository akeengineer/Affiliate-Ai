# Task 013 - Phase 2J Hermes Governance Orchestration Proof

## Objective

Prove Hermes can safely orchestrate and summarize the completed governance chain
`Phase 2E -> Phase 2G -> Phase 2H -> Phase 2I` in a single, safe dry-run.

Live execution: Phase 2E (tmp-only) and Phase 2G dry-run (no vault write).
Static verification: Phase 2H and Phase 2I scripts + guardrail wrappers.
No vault writes. No approved simulation.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/HERMES_OPERATING_RULES.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- hermes/skills/affiliate-growth-os/SKILL.md
- scripts/dev/run_phase2e_import_score_report.sh
- scripts/dev/promote_product_candidates.py
- scripts/dev/run_phase2g_approval_promote.sh
- scripts/dev/create_decision.py
- scripts/dev/run_phase2h_decision_review.sh
- scripts/dev/finalize_decision.py
- scripts/dev/run_phase2i_decision_finalization.sh

## Scope

Create:

- `codex/tasks/013-phase2j-hermes-governance-orchestration.md`
- `prompts/workflows/hermes-phase2j-governance-orchestration.md`
- `scripts/dev/run_phase2j_governance_orchestration.sh`
- `tests/test_phase2j_governance_orchestration.py`

Update:

- `.gitignore`

Do not modify Phase 2E/2G/2H/2I unless a real bug is found.

## Why 2H/2I are static-verified, not executed

Phase 2H reads `vault/products/<id>.md` (only created by 2G `--approve`) and
Phase 2I reads `vault/decisions/<id>.md` (only created by 2H `--approve`).
Executing them live requires vault writes, which are disallowed by default.
The proof therefore runs the tmp-safe stages live (2E + 2G dry-run) and
statically verifies 2H/2I, reporting honest `not_executed` statuses. The value
of the proof is demonstrating that every approval gate halts progression.

## Requirements

- Accept `<input-csv> <report-week> <product-id>` from CLI.
- `product-id` must match `^[a-z0-9-]+$` (path-traversal guard).
- Fail on `ENABLE_AUTOPUBLISH=true` or `ENABLE_OPENAI_API_DIRECT=true` before
  creating any output.
- Verify all four phase scripts exist:
  - `scripts/dev/run_phase2e_import_score_report.sh` (executable)
  - `scripts/dev/promote_product_candidates.py`
  - `scripts/dev/create_decision.py`
  - `scripts/dev/finalize_decision.py`
- Verify all three guardrail wrappers exist and are executable:
  - `scripts/dev/run_phase2g_approval_promote.sh`
  - `scripts/dev/run_phase2h_decision_review.sh`
  - `scripts/dev/run_phase2i_decision_finalization.sh`
- Run Phase 2E live (tmp-only); require `final_status: success`.
- Require the target `product-id` to have a scored JSON from Phase 2E.
- Run Phase 2G via its wrapper in dry-run (no `APPROVE_PROMOTE`); require
  `phase2g_status: dry_run_complete`.
- Do not execute Phase 2H or Phase 2I.
- Write sanitized governance summary to
  `tmp/phase2j-hermes-governance/governance-summary-<report-week>.md`.
- Validate summary frontmatter `type: hermes_governance_summary`.
- Summary must not reference any private vault path.
- Do not write `vault/products/` or `vault/decisions/`.
- Do not call external APIs, generate content, launch campaigns, or autopublish.

## Governance summary schema

```yaml
type: hermes_governance_summary
report_week: <week>
mode: dry_run
product_id: <product_id>
score_decision: <from Phase 2E score JSON>
promoted_status: dry_run_not_promoted
decision_status: not_executed
finalization_status: not_executed
compliance_gate_status: not_evaluated
next_allowed_action: "<text>"
created_at: "<UTC ISO>"
status: complete
```

## Acceptance criteria

- `bash -n scripts/dev/run_phase2j_governance_orchestration.sh` exits `0`.
- Default run -> exit `0`, `phase2j_status: success`, summary file exists with
  `type: hermes_governance_summary`.
- Default run writes no `vault/products/` or `vault/decisions/` artifact.
- Summary references no private vault path, no affiliate content markers, no
  external URLs.
- `ENABLE_AUTOPUBLISH=true` -> exit non-zero, output dir not created.
- `ENABLE_OPENAI_API_DIRECT=true` -> exit non-zero, output dir not created.
- Invalid `product-id` -> exit non-zero.

## Tests required

- `python -m pytest -q tests/test_phase2j_governance_orchestration.py`
- `python -m pytest -q`
