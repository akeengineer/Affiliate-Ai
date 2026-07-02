# Phase 7H Operator Runbook

phase7h_status: success

phase7d_runtime_readiness: implemented_manual_gate

### Purpose

This document is the hardened operator runbook for safe use of the live Phase
7D selected-gate manual wrapper.

Phase 7H does not change runtime behavior.

### Scope

- docs/tests/task-only
- operator runbook only
- no runtime wrapper behavior change
- no approval logic change
- no primitive execution
- no vault read/write
- no new mutation path
- no backend/API/database/network

### Current runtime state

- Phase 7D wrapper exists
- Phase 7G safe demo pack exists
- phase7d_runtime_readiness is implemented_manual_gate
- runtime is selected-gate-only
- runtime is manual-gated
- runtime is not approve-all
- runtime is not automatic
- no next-gate automation
- no chain execution

### Pre-execution checklist

Operator must confirm:

- selected gate is exactly one of promote, decision, finalization
- product_id is correct
- report_week is correct
- Phase 6B approval review packet exists
- Phase 6C verifier output is ready
- Phase 6E execution plan exists
- selected gate is plan_ready
- selected gate plan_ready
- selected gate is not blocked
- emergency stop is inactive
- operator identity is correct
- approval reason is clear
- intent is clear
- confirmation string is exact
- only the matching approval flag is truthy
- no unrelated approval flag is truthy
- no global approval
- no approve-all
- no approve-all intent
- no chain or next-gate request
- non-production/sample run has been performed first

Do not provide approval flag truthy assignment examples.

### Safe execution ceremony

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

Avoid executable command examples with approval flags set truthy.

### Evidence verification checklist

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

### Approval flag handling policy

- exactly one matching gate-specific flag may be truthy during real execution
- all unrelated gate flags must be false/unset
- no global approval flag is accepted
- no approve-all is accepted
- approval flags must not be persisted in config
- approval flags must not be written into audit artifacts
- approval flags must not be shared in logs/screenshots
- operator must clear approval flags after execution

Do not include truthy assignment examples.

### Emergency stop procedure

- emergency stop must be checked before execution
- if emergency stop is active, do not execute
- if an incident occurs, activate emergency stop before investigation
- emergency stop overrides approval
- after emergency stop, perform manual review before retry
- document what was attempted and what audit artifacts exist

### Audit verification procedure

- wrapper writes audit artifacts under tmp
- Phase 7B verifier remains read-only
- Phase 7B verifier can inspect audit artifact separately
- verifier valid is not approval
- verifier does not trigger next gate
- operator should record verifier output
- if audit verification fails, do not auto-rerun
- manual review is required

Avoid executable command examples with approval flags set truthy.

### Failure/manual-review procedure

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

### Retry policy

- retry is never automatic
- retry requires fresh operator decision
- retry requires checking current evidence again
- retry requires checking audit artifacts from previous attempt
- retry requires emergency stop inactive
- retry must target the same selected gate only unless a new phase/approval
  exists
- retry must not skip Phase 7B audit verification

### Partial-completion handling

- partial completion means primitive may have mutated state but audit/result
  flow did not fully complete
- do not run another gate
- do not rerun immediately
- inspect vault state manually
- inspect available audit artifacts
- record manual findings
- require senior/operator approval before any retry or repair
- do not attempt automatic rollback

### Incident response and escalation

- activate emergency stop
- preserve tmp audit artifacts
- preserve terminal output/logs
- record operator, product_id, report_week, selected gate, timestamp
- identify whether primitive executed
- identify whether vault changed
- stop all related gate executions
- escalate to owner/senior reviewer
- do not resume until incident review is complete

### Post-execution recordkeeping

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

### Hard never-do list

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

### Phase 8A durable audit store design

Phase 8A durable audit store design exists in
`docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`. The durable audit store is not
implemented yet; Phase 8A is design only. This runbook is unchanged by Phase
8A beyond this pointer.

### Known limitations

- CLI/local runbook only
- operator identity is not authenticated
- durable audit store is not implemented
- audit outputs are tmp-local
- no backend/API/database
- no marketplace connector
- no autopublish
- no production deployment
