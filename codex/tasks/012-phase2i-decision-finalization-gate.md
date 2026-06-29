# Task 012 - Phase 2I Decision Finalization Gate

## Objective

Validate an approved draft `decision` note in `vault/decisions/` and finalize it
safely. Finalization is the single sanctioned state transition
`status: draft -> status: complete`, performed in place on the existing note.

Default mode is dry-run. Mutating `vault/decisions/` requires `--approve`.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/OBSIDIAN_CONTRACT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- scripts/dev/create_decision.py
- scripts/dev/run_phase2h_decision_review.sh
- tests/test_phase2h_manual_decision_review.py

## Scope

Create:

- `codex/tasks/012-phase2i-decision-finalization-gate.md`
- `scripts/dev/finalize_decision.py`
- `scripts/dev/run_phase2i_decision_finalization.sh`
- `tests/test_phase2i_decision_finalization.py`

Update:

- `.gitignore`

Do not modify Phase 2H unless a real bug is found.

## Requirements

- Accept `--decision-id`, `--finalization-reason`, `--approve` from CLI.
- Source note is `vault/decisions/<decision_id>.md`.
- `decision_id` must match `^dec-[a-z0-9-]+-\d{4}-W\d{2}$` (path-traversal guard).
- Source note must have `type: decision` and `status: draft`.
- Required fields must exist and be non-empty: `decision_id`, `product_id`,
  `final_decision`, `score_decision`, `product_opportunity_score`,
  `confidence_score`, `missing_signal_count`, `compliance_status`, `status`,
  `created_at`, `updated_at`.
- Frontmatter `decision_id` must equal the CLI `--decision-id`.
- `final_decision` must be one of `launch`, `small_batch_test`, `watchlist`,
  `reject`.
- `product_opportunity_score` must be numeric `0-100`.
- `compliance_status` must equal `approved`. No compliance override hatch.
- `finalization_reason` is required, must not be whitespace-only, and must not
  contain affiliate URL or secret patterns.
- Default mode is dry-run: audit only, no vault mutation.
- `--approve` updates the existing note in place: `status: complete`,
  `finalized_at`, `finalization_reason`, bumped `updated_at`.
- Any source `status` other than `draft` must fail (no re-finalize).
- Preserve all other frontmatter keys and the markdown body byte-for-byte.
- Atomic write: temp file + `os.replace`.
- Audit always writes to
  `tmp/phase2i-decision-finalization/audit-<decision_id>.md`.
- Bash wrapper: fail on `ENABLE_AUTOPUBLISH=true` or
  `ENABLE_OPENAI_API_DIRECT=true`; require `FINALIZATION_REASON`; pass
  `--approve` only when `APPROVE_FINALIZE=true`.
- Do not call external APIs, generate content, launch campaigns, or autopublish.

## Audit artifact schema

```yaml
type: phase2i_audit
decision_id: <decision_id>
product_id: <product_id>
final_decision: <final_decision>
compliance_status: approved
mode: dry_run | approved
finalized_at: <ISO timestamp or "(dry-run)">
artifact_path: vault/decisions/<decision_id>.md
created_at: <UTC ISO>
status: complete
```

Audit body ends with:

- dry-run: `phase2i_status: dry_run_complete`
- approved: `phase2i_status: success`

## Acceptance criteria

- `python -m py_compile scripts/dev/finalize_decision.py` exits `0`.
- `bash -n scripts/dev/run_phase2i_decision_finalization.sh` exits `0`.
- Dry-run → exit `0`, `phase2i_status: dry_run_complete`, vault note unchanged.
- `--approve` → exit `0`, `phase2i_status: success`, note `status: complete` with
  `finalized_at` and `finalization_reason`.
- `status: complete` source → exit non-zero (no re-finalize).
- `type` not `decision` → exit non-zero.
- `compliance_status` not `approved` → exit non-zero.
- Missing required field → exit non-zero naming the field.
- Empty / affiliate / secret `finalization_reason` → exit non-zero.
- Nonexistent or invalid `decision_id` → exit non-zero.
- `ENABLE_AUTOPUBLISH=true` → bash wrapper exit non-zero.

## Tests required

- `python -m pytest -q tests/test_phase2i_decision_finalization.py`
- `python -m pytest -q`
