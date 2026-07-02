# Task 051 — Phase 7H Operator Runbook Hardening

phase7h_status: success

phase7d_runtime_readiness: implemented_manual_gate

## Purpose

Create the hardened operator runbook for safe real-world use of the live Phase
7D selected-gate manual wrapper.

## Scope

Phase 7H is docs/tests/task-only. It adds operator runbook guidance only,
changes no runtime wrapper behavior, changes no approval logic, executes no
primitive, performs no vault read/write, adds no new runtime command, adds no
new mutation path, and adds no backend/API/database/network behavior.

## Files

- `codex/tasks/051-phase7h-operator-runbook-hardening.md`
- `docs/PHASE7H_OPERATOR_RUNBOOK.md`
- `tests/test_phase7h_operator_runbook_hardening.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md`
- additive updates to `docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md`

## Status model

- `success`: the hardened operator runbook exists, additive documentation
  pointers exist, Phase 7D runtime readiness remains
  `implemented_manual_gate`, and protected runtime files stay unchanged.
- `failed`: required runbook coverage is missing, additive docs regress, or a
  protected runtime surface changes.

## Operator runbook objective

Provide a deterministic, operator-facing safety procedure for using the live
Phase 7D selected-gate wrapper without widening the runtime boundary or adding a
new mutation path.

## Pre-execution checklist

The runbook must require the operator to confirm all of the following:

- selected gate is exactly one of promote, decision, finalization
- product_id is correct
- report_week is correct
- Phase 6B approval review packet exists
- Phase 6C verifier output is ready
- Phase 6E execution plan exists
- selected gate is plan_ready
- selected gate is not blocked
- emergency stop is inactive
- operator identity is correct
- approval reason is clear
- intent is clear
- confirmation string is exact
- only the matching approval flag is truthy
- no unrelated approval flag is truthy
- no global approval
- no approve-all intent
- no chain or next-gate request
- non-production/sample run has been performed first

The runbook must not provide approval flag truthy assignment examples.

## Safe execution ceremony

The runbook must define this step-by-step operator ceremony:

1. start from latest main
2. run full suite or relevant acceptance suite
3. run Phase 7G safe demo pack
4. inspect Phase 6B/6C/6E evidence
5. verify selected gate readiness
6. verify emergency stop state
7. prepare operator reason and intent
8. prepare exact confirmation string
9. set only the matching approval flag in the operator shell
10. execute one gate only
11. record audit artifact path
12. run Phase 7B audit verifier separately
13. archive or record audit outputs manually until durable audit store exists

The runbook must avoid executable command examples with approval flags set
truthy.

## Evidence verification checklist

The runbook must document these evidence checks:

- Phase 6B packet path
- Phase 6B dry_run true
- Phase 6C verdict ready
- Phase 6E dry_run true
- Phase 6E overall verdict not failed
- selected gate in per_gate_plan
- selected gate plan_ready true
- selected gate blocked_reason empty/null
- product_id and report_week consistency
- decision gate score decision comes from evidence
- finalization requires decision evidence and approved compliance status

## Approval flag handling policy

The runbook must state:

- exactly one matching gate-specific flag may be truthy during real execution
- all unrelated gate flags must be false/unset
- no global approval flag is accepted
- no approve-all is accepted
- approval flags must not be persisted in config
- approval flags must not be written into audit artifacts
- approval flags must not be shared in logs/screenshots
- operator must clear approval flags after execution

The runbook must not include truthy assignment examples.

## Emergency stop procedure

The runbook must state:

- emergency stop must be checked before execution
- if emergency stop is active, do not execute
- if an incident occurs, activate emergency stop before investigation
- emergency stop overrides approval
- after emergency stop, perform manual review before retry
- document what was attempted and what audit artifacts exist

## Audit verification procedure

The runbook must state:

- wrapper writes audit artifacts under tmp
- Phase 7B verifier remains read-only
- Phase 7B verifier can inspect audit artifact separately
- verifier valid is not approval
- verifier does not trigger next gate
- operator should record verifier output
- if audit verification fails, do not auto-rerun
- manual review is required

Avoid executable command examples with approval flags set truthy.

## Failure/manual-review procedure

The runbook must state:

- inspect wrapper exit code
- inspect intent audit
- inspect result audit
- determine whether primitive was invoked
- determine whether partial completion occurred
- inspect primitive result summary
- do not run next gate
- do not rollback automatically
- do not retry silently
- require manual review before retry
- document decision to retry or stop

## Retry policy

The runbook must state:

- retry is never automatic
- retry requires fresh operator decision
- retry requires checking current evidence again
- retry requires checking audit artifacts from previous attempt
- retry requires emergency stop inactive
- retry must target the same selected gate only unless a new phase/approval
  exists
- retry must not skip Phase 7B audit verification

## Partial-completion handling

The runbook must state:

- partial completion means primitive may have mutated state but audit/result
  flow did not fully complete
- do not run another gate
- do not rerun immediately
- inspect vault state manually
- inspect available audit artifacts
- record manual findings
- require senior/operator approval before any retry or repair
- do not attempt automatic rollback

## Incident response and escalation

The runbook must state:

- activate emergency stop
- preserve tmp audit artifacts
- preserve terminal output/logs
- record operator, product_id, report_week, selected gate, timestamp
- identify whether primitive executed
- identify whether vault changed
- stop all related gate executions
- escalate to owner/senior reviewer
- do not resume until incident review is complete

## Post-execution recordkeeping

The runbook must state:

- record selected gate
- record product_id
- record report_week
- record operator
- record reason and intent
- record audit artifact path
- record Phase 7B verifier result
- record primitive outcome
- record manual review outcome if any
- note that durable audit store is not yet implemented

## Hard never-do list

The runbook must state:

- never approve-all
- never use global approval
- never request multiple gates
- never run next gate automatically
- never chain execution
- never ignore emergency stop
- never run with production data before sample acceptance
- never paste approval flags into docs/logs/screenshots
- never retry silently
- never rollback automatically
- never treat Phase 7B valid as approval
- never use backend/API/database/autopublish/marketplace/production behavior in
  Phase 7H

## Documentation update scope

Update ROADMAP, PROJECT_STATE, the Phase 7G operator acceptance document, and
the Phase 7 runtime live snapshot additively. Mark Phase 7H complete as
Operator Runbook Hardening and recommend Phase 8A Durable Audit Store Design
next.

## No-execution/static-safety rules

The new Phase 7H task and runbook files must contain no approval flag truthy
assignments, no primitive invocation forms, no external URL schemes, no
operator-local repository paths, no secret markers, no private-key material,
and no backend/API/database/network command forms. Wrapper inventory references
and Phase 7B verifier references are allowed as non-executable inventory only.

## Test strategy

Tests must verify file/status contracts, runbook scope and runtime-state tokens,
checklist coverage, specific safety assertions, additive documentation
references, protected runtime hashes, absence of new runtime scripts, and static
safety of the new Phase 7H task/runbook files only.

## Acceptance criteria

- task exists
- runbook exists
- runbook contains `phase7h_status: success`
- runbook contains `phase7d_runtime_readiness: implemented_manual_gate`
- runbook states docs/tests/task-only
- runbook states no runtime wrapper behavior change
- runbook states no approval logic change
- runbook states no primitive execution
- runbook states no vault read/write
- runbook states no new mutation path
- runbook states Phase 7D wrapper exists
- runbook states Phase 7G safe demo pack exists
- runbook states selected-gate-only and manual-gated
- runbook states no approve-all, no next-gate automation, and no chain
  execution
- ROADMAP, PROJECT_STATE, Phase 7G docs, and the live snapshot all reference
  Phase 7H additively
- protected Phase 7B/7D/7G runtime files remain unchanged
- no new runtime script or mutation command is added by Phase 7H

## Verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase7h_operator_runbook_hardening.py
python -m pytest -q tests/test_phase7g_operator_acceptance_demo_pack.py
python -m pytest -q tests/test_phase7f_runtime_wrapper_live_snapshot.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m pytest -q tests/test_phase7e_release_snapshot_runtime_blocked.py
python -m pytest -q tests/test_phase7d_implementation_plan_finalization.py
```

## Known limitations

Phase 7H is CLI/local runbook hardening only. Operator identity is not
authenticated, durable audit storage is not implemented, audit outputs are
tmp-local, and there is still no backend/API/database, marketplace connector,
autopublish, or production deployment.

## Final status target

phase7h_status: success
