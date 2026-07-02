# Phase 7G Operator Acceptance / Safe Demo Pack

phase7g_status: success

phase7d_runtime_readiness: implemented_manual_gate

### Purpose

This document defines the safe operator acceptance/demo pack for the live Phase
7D wrapper.

### Scope

- safe demo / acceptance only
- no runtime wrapper behavior change
- no approval logic change
- no primitive execution by default
- no vault write
- no new mutation path
- no backend/API/database/network

### Safe demo scenarios

- no-execute / dry-run prevented path
- emergency stop prevented path, verified as protected guard inventory because
  dynamically reaching it would require forbidden runtime execution intent
- missing evidence prevented/blocked path
- wrong approval flag rejection, verified as protected guard inventory without
  supplying any approval
- approve-all rejection
- chain/next-gate rejection
- invalid gate rejection
- audit artifact presence with `mutation_attempted` false
- Phase 7B verifier handoff note

The demo runner executes only no-execute, prevented, blocked, and invalid wrapper
paths. Execution-adjacent guards are inspected statically from the unchanged
wrapper so the demo cannot cross the manual gate.

### Operator checklist before real execution

- confirm selected gate
- confirm product_id
- confirm report_week
- confirm Phase 6B packet exists
- confirm Phase 6C verifier ready
- confirm Phase 6E plan exists
- confirm selected gate plan_ready
- confirm emergency stop inactive
- confirm operator identity
- confirm reason
- confirm intent
- confirm exact confirmation string
- confirm only matching approval flag is truthy
- confirm no global approval
- confirm no approve-all
- confirm no chain or next-gate request
- confirm non-production sample first

This checklist intentionally provides no truthy assignment examples.

### Manual review checklist after failure

- inspect result audit
- inspect intent audit
- inspect wrapper exit code
- confirm whether primitive was invoked
- confirm whether partial completion occurred
- do not rerun automatically
- do not run next gate
- do not rollback automatically
- require operator review before retry

### Phase 7B verifier handoff

- Phase 7B verifier remains read-only.
- The verifier can inspect an audit artifact separately.
- A verifier result of valid is not approval.
- The verifier does not trigger next gate.

Phase 7G records this handoff as an inventory note. It does not automatically
run verification as part of an approval flow and includes no executable example
with an approval flag set truthy.

### Phase 7H runbook handoff

Phase 7H hardens the real-use procedure with
`docs/PHASE7H_OPERATOR_RUNBOOK.md`.
The runbook is operator-facing only, adds no runtime behavior change, and does
not alter Phase 7D wrapper behavior or approval logic.

### No-mutation guarantee

The pack supplies no runtime execution intent, invokes no primitive, does not
write the vault, and introduces no new mutation path. Its non-production
fixtures, scenario records, and summaries remain in gitignored temporary
directories. The runner removes its temporary Phase 6 evidence and safe Phase
7D result audits when it exits.

### Acceptance summary

The summary builder reads safe scenario JSON records only from
`tmp/phase7g-operator-acceptance/` and writes:

- `tmp/phase7g-operator-acceptance/operator-acceptance-summary.json`
- `tmp/phase7g-operator-acceptance/operator-acceptance-summary.md`

Both outputs include Phase 7G status, Phase 7D runtime readiness, scenarios,
expected results, observed exit codes, audit artifacts found, safety statement,
operator checklist, manual-review checklist, and the next recommended phase.

### What remains out of scope

- no backend/API/database
- no marketplace connector
- no autopublish
- no campaign launch
- no production deployment
- no durable audit store
- no scheduled approval automation
- no multi-gate workflow
- no automatic finalization
- no external API integration
