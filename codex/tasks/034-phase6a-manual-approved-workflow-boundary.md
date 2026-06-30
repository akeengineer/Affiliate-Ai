# Task 034 - Phase 6A Manual Approved Workflow Boundary Plan

## 1. Purpose

Define the boundary and contract for future manual-approved workflows — how
read-only artifacts may move into human-gated approval review — without
executing, adding, or modifying any approval mutation. Docs/tests/task-only.

## 2. Scope

- Author the manual-approved workflow boundary contract and a docs-contract test.
- Additively note the boundary in ROADMAP and PROJECT_STATE.
- Reference the existing Phase 2G/2H/2I primitives as future targets only; never
  execute, modify, or give runnable approval-flag examples for them.

## 3. Files

- `codex/tasks/034-phase6a-manual-approved-workflow-boundary.md`
- `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md`
- `tests/test_phase6a_manual_approved_workflow_boundary.py`
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)

No runtime scripts are created or modified.

## 4. Boundary model

```text
read-only tmp artifacts
-> approval review packet under tmp
-> human gate
-> existing manual-approved primitive
-> vault write only when explicit approval is provided
```

Phase 6A defines this chain as a contract; it builds no packet, no gate, and no
mutation.

## 5. Source artifacts allowed

Read-only `tmp/` inputs only: Phase 2E score JSON / weekly report, Phase 2F
Hermes summary, Phase 2J governance summary, Phase 3A dashboard, Phase 3B
portfolio, Phase 4E demo bundle summary, Phase 5D UI shell demo summary, and the
Phase 5C verifier verdict. No vault read is introduced.

## 6. Approval gates

Three human gates map to existing primitives (references only): promote gate
(`promote_product_candidates.py`, flag `APPROVE_PROMOTE`), decision gate
(`create_decision.py`, flag `APPROVE_DECISION`), finalization gate
(`finalize_decision.py`, flag `APPROVE_FINALIZE`). Mandatory order:
promote -> decision -> finalization. Finalization requires
`compliance_status: approved`.

## 7. Evidence requirements

A future review packet must carry: `product_id`, `report_week`,
`score_decision`, `product_opportunity_score`, `confidence_score`,
`compliance_status`, verifier status/verdict, Phase 4D verification status,
Phase 5C verdict, source artifact paths under `tmp/`, an operator identity
placeholder, an approval reason, and an ISO-8601 UTC timestamp. Incomplete
evidence blocks approval.

## 8. Forbidden automation

Autopublish, campaign launch, external API submit, affiliate link generation,
hidden/implicit promotion, direct approval from the UI shell, vault write without
an explicit approval flag, finalization without `compliance_status: approved`,
marketplace connector, backend/API/database, and network calls are forbidden.

## 9. Future Phase 6B-6E roadmap

- Phase 6B: dry-run approval review packet under `tmp/phase6b-...`
- Phase 6C: manual approval command wrapping existing primitives after explicit
  approval
- Phase 6D: audit verifier
- Phase 6E: release snapshot update

Backend/API/database/marketplace require separate future approval.

## 10. Audit artifact concept

Review packets live under `tmp/phase6x-...`, immutable-style Markdown/JSON, with
no vault mutation by default. Every approved write must be explicit and logged
with operator placeholder, approval reason, timestamp, source artifact paths,
gate name, and outcome.

## 11. Test strategy

Deterministic docs-contract tests: boundary doc + task exist; boundary-only
scope; gate names, approval flag names, primitive references, gate ordering,
evidence fields, source-artifact references, and forbidden automation are all
present; no Phase 6A runtime script exists; no execution examples appear (no
approval flag set to true, and no `run_phase2g`/`run_phase2h`/`run_phase2i`
wrapper invocation lines); ROADMAP/
PROJECT_STATE token contracts are preserved; static safety scans only the two
new Phase 6A files.

## 12. Acceptance criteria

- Boundary doc, task, and test exist; the test passes.
- Phase 5E and Phase 3E docs-contract tests still pass; full suite passes.
- No runtime script changed; no hardcoded operator path in scripts.
- No approval mutation, vault write, or primitive execution is introduced.

## 13. Verification commands

```
python -m pytest -q tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 14. Known limitations

- Boundary documentation only; no review packet, gate, or mutation exists yet.
- Future Phase 6B+ are separate implementation phases under their own approval.

## 15. Final status target

`phase6a_status: success`
