# Task 025 - Phase 5A Local Read-only UI Shell Boundary Plan

## 1. Purpose

Define the boundary, architecture rules, data contract, allowed inputs, and
forbidden actions for a **future** local read-only UI shell, before any shell
code is written. This is a documentation and contract-test phase only. It does
not implement a UI shell, a frontend framework, a backend, or any runtime
script.

## 2. Scope

- Author boundary and plan documentation for a future read-only UI shell.
- Author docs-contract pytest tests that enforce that boundary in text.
- Establish the layering rule: governed vault layer, scrubbed read-only tmp
  projections, and a future shell that is a local view over approved static
  projections only.
- Do not build, run, or wire any UI shell in Phase 5A.

## 3. Files

Create exactly:

- `codex/tasks/025-phase5a-ui-shell-boundary-plan.md`
- `docs/UI_SHELL_BOUNDARY.md`
- `docs/PHASE5_READONLY_UI_SHELL_PLAN.md`
- `tests/test_phase5a_ui_shell_boundary_plan.py`

Do not create runtime outputs. Do not create new tmp paths. Do not edit
`.gitignore`. Do not add scripts. Do not modify Phase 2/3/4 workflows,
`command_center.sh`, or any demo bundle scripts.

## 4. Hard constraints

- docs/tests only
- no UI shell implementation
- no frontend framework (no Next.js, no React, no Vite)
- no package.json and no npm-based install step
- no backend, no server, no API routes, no FastAPI
- no database
- no external URLs
- no vault reads
- no vault writes
- no approval mutation
- no raw artifact export
- no Phase 2G/2H/2I triggering
- no marketplace connector

## 5. Future UI shell boundary

- The vault is the governed source layer and is never read or written by a
  future UI shell.
- The tmp artifacts are scrubbed, read-only projections.
- A future UI shell is a local view over approved static projections only.
- The future shell may display status and link to local static files with
  relative links; it must never mutate state.
- Full boundary rules live in `docs/UI_SHELL_BOUNDARY.md`.

## 6. Data contract

Preferred future data sources (Phase 4 outputs as source of truth):

- `tmp/phase4b-ui-snapshot/manifest.json`
- `tmp/phase4b-ui-snapshot/index.html` (static local demo target only)
- `tmp/phase4c-snapshot-catalog/catalog.json`
- `tmp/phase4d-demo-verifier/verification-summary.json`
- `tmp/phase4e-demo-bundle/demo-bundle-summary.json`

Legacy/reference-only data sources (not read directly without a later guardrail
test and documented reason):

- `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md`
- `tmp/phase3a-dashboard/dashboard-*-<week>.md`
- `tmp/phase2e-import-score-report/scores/*.json`

If score JSON is ever used as a fallback, `input_path` and `note_refs` must
never be emitted.

## 7. Forbidden actions

- approvals, promote, create decision, finalize decision
- vault reads or vault writes
- editing artifacts or exporting raw artifact bodies
- affiliate content generation, autopublish, campaign launch
- calling external APIs or external URLs
- ingesting marketplace data or wiring marketplace connectors
- triggering Phase 2G/2H/2I approved workflows

## 8. Acceptance criteria

- All four files exist.
- `docs/UI_SHELL_BOUNDARY.md` and `docs/PHASE5_READONLY_UI_SHELL_PLAN.md`
  document the layering rule, preferred and legacy data sources, allowed and
  forbidden functions, forbidden implementation choices, and security
  guardrails.
- The docs state that Phase 5A is docs/tests only and that no UI shell is
  implemented yet.
- The docs list future subphases 5B, 5C, 5D, and 5E.
- `tests/test_phase5a_ui_shell_boundary_plan.py` passes.
- The full suite stays green.
- Only four files change; no `.gitignore` change; no runtime script added; no
  frontend/backend files added.

## 9. Verification commands

```
python -m pytest -q tests/test_phase5a_ui_shell_boundary_plan.py
python -m pytest -q
git status --short --branch
```

The current static demo command remains:

```
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
```

## 10. Known limitations

- Boundary documentation only; there is no UI shell yet.
- No live refresh and no production deployment.
- The contract is enforced in text by docs-contract tests, not by a running
  shell.

## 11. Final status target

`phase5a_status: success`
