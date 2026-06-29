# Task 011 - Phase 2H Manual Review / Decision Workflow

## Objective

Create explicit decision artifacts for promoted product_candidate notes in
`vault/products/`. The operator supplies a decision (`launch`, `small_batch_test`,
`watchlist`, `reject`) and the script validates compatibility with the Phase 2E
score before writing a `decision` note.

Default mode is dry-run. Writing to `vault/decisions/` requires `--approve`.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/OBSIDIAN_CONTRACT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- scripts/dev/promote_product_candidates.py
- scripts/dev/run_phase2g_approval_promote.sh
- tests/test_phase2g_approval_promote.py

## Scope

Create:

- `codex/tasks/011-phase2h-manual-decision-review.md`
- `scripts/dev/create_decision.py`
- `scripts/dev/run_phase2h_decision_review.sh`
- `tests/test_phase2h_manual_decision_review.py`

Update:

- `.gitignore`

Do not modify Phase 2G unless a real bug is found.

## Requirements

- Accept `--product-id`, `--decision`, `--report-week` from CLI.
- Source note is `vault/products/<product_id>.md`.
- Source note must have `type: product_candidate`, `status: scored`, and all
  enriched score fields from Phase 2G promotion.
- Decision must be one of `launch`, `small_batch_test`, `watchlist`, `reject`.
- Decision levels: `launch=4`, `small_batch_test=3`, `watchlist=2`, `reject=1`.
- If `final_decision level > score_decision level`, `--override-reason` is required.
- `reject` final_decision is always allowed.
- `override_reason` must not contain affiliate URL or secret patterns.
- Default mode is dry-run: write decision artifact to
  `tmp/phase2h-decision-review/dec-<product_id>-<report_week>.md`.
- `--approve` writes to `vault/decisions/dec-<product_id>-<report_week>.md`.
- Audit always writes to `tmp/phase2h-decision-review/audit-<report_week>.md`.
- No overwrite: fail if destination exists.
- `source_dir` is always hardcoded to `vault/products/`.
- Bash wrapper: fail on `ENABLE_AUTOPUBLISH=true` or `ENABLE_OPENAI_API_DIRECT=true`.
- Bash wrapper: pass `--approve` only when `APPROVE_DECISION=true`.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not implement autopublish.

## Decision artifact schema

```yaml
type: decision
decision_id: dec-<product_id>-<report_week>
product_id: <product_id>
final_decision: <launch|small_batch_test|watchlist|reject>
score_decision: <from product note>
product_opportunity_score: <from product note>
confidence_score: <from product note>
missing_signal_count: <from product note>
vote_count: 0
compliance_status: pending
override_reason: null
decision_summary: "<text>"
required_actions: []
status: draft
created_at: "<UTC ISO>"
updated_at: "<UTC ISO>"
```

## Acceptance criteria

- `python -m py_compile scripts/dev/create_decision.py` exits `0`.
- `bash -n scripts/dev/run_phase2h_decision_review.sh` exits `0`.
- Dry-run → exit `0`, `phase2h_status: dry_run_complete`,
  `tmp/phase2h-decision-review/dec-*.md` exists.
- Dry-run does NOT write `vault/decisions/`.
- Dry-run audit has `type: phase2h_audit` and `mode: dry_run`.
- `--approve` → `vault/decisions/dec-*.md` exists, `phase2h_status: success`.
- Promoted artifact has `type: decision`, `final_decision`, `score_decision`,
  `product_opportunity_score`.
- Upgrade without `--override-reason` → exit non-zero.
- Upgrade with `--override-reason` → exit `0`.
- `status: draft` source → exit non-zero.
- Missing enriched fields → exit non-zero.
- Destination exists → exit non-zero, no overwrite.
- `ENABLE_AUTOPUBLISH=true` → bash wrapper exit non-zero.

## Tests required

- `python -m pytest -q tests/test_phase2h_manual_decision_review.py`
- `python -m pytest -q`
