# Task 014 - Phase 2K Operating Manual / Runbook

## Objective

Create a human/operator runbook that explains how to operate the Phase 2
governance pipeline (2D -> 2E -> 2F -> 2G -> 2H -> 2I -> 2J) end-to-end safely.

This is a documentation + safe-orchestration task. It introduces no new approval
behavior and no new runtime capability beyond a convenience dry-run wrapper that
only calls existing safe dry-run workflows.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/HERMES_OPERATING_RULES.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- scripts/dev/run_phase2e_import_score_report.sh
- scripts/dev/run_phase2f_hermes_orchestration.sh
- scripts/dev/run_phase2g_approval_promote.sh
- scripts/dev/run_phase2h_decision_review.sh
- scripts/dev/run_phase2i_decision_finalization.sh
- scripts/dev/run_phase2j_governance_orchestration.sh

## Scope

Create:

- `codex/tasks/014-phase2k-operating-manual.md`
- `docs/PHASE2_OPERATING_MANUAL.md`
- `docs/PHASE2_GOVERNANCE_FLOW.md`
- `scripts/dev/run_phase2_full_dry_run.sh`
- `tests/test_phase2k_docs_contract.py`

Modify:

- `.gitignore` only if a new tmp output directory is introduced (none is — the
  dry-run wrapper reuses existing tmp dirs).

Do not modify Phase 2E/2F/2G/2H/2I/2J scripts unless a real bug is found.

## Requirements

- `docs/PHASE2_OPERATING_MANUAL.md` documents purpose, capability summary, hard
  guardrails, the full workflow map, exact command examples, dry-run vs approved
  mode, runtime output paths, private vault output paths, commit policy,
  troubleshooting, cleanup, PR/Git hygiene, operator checklists, and known gaps.
- `docs/PHASE2_GOVERNANCE_FLOW.md` documents the end-to-end Mermaid flow, the
  state-transition diagram, approval gates, why Phase 2J is dry-run only, why
  `decision_status`/`finalization_status` are `not_executed` in Phase 2J,
  business-memory boundaries, the security model, and future phases.
- `scripts/dev/run_phase2_full_dry_run.sh` runs only safe dry-run workflows
  (2E, 2F, 2J), fails on `ENABLE_AUTOPUBLISH=true` / `ENABLE_OPENAI_API_DIRECT=true`,
  never runs approved 2G/2H/2I, never writes vault, and prints a concise summary.

## Acceptance criteria

- `bash -n scripts/dev/run_phase2_full_dry_run.sh` exits `0`.
- Default dry-run -> exit `0`, prints `phase2e_status`, `phase2f_status`,
  `phase2j_status`, `final_status: success`.
- Default dry-run writes no `vault/products/<id>.md` or `vault/decisions/*`.
- `ENABLE_AUTOPUBLISH=true` -> exit non-zero.
- Docs contain the strings asserted by the contract test.

## Tests required

- `python -m pytest -q tests/test_phase2k_docs_contract.py`
- `python -m pytest -q`
