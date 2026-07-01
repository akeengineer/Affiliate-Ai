# High-risk Single-gate Manual Approval Wrapper Readiness Review (Phase 7D-R)

This is the final high-risk readiness review gate before Phase 7D. It is
docs/tests/task-only:

- Phase 7D-R does not add a runtime wrapper.
- Phase 7D-R does not add approval mutation.
- Phase 7D-R does not execute approval primitives.
- Phase 7D-R is the final review gate before Phase 7D.
- Phase 7D is the future high-risk runtime implementation phase.

Status tokens:

```text
phase7d_r_status: success
phase7d_runtime_readiness: blocked
```

The review artifact is complete, but runtime implementation remains blocked
until the user explicitly approves proceeding to Phase 7D separately.

Historical follow-through note:

- this document remains the Phase 7D-R review artifact
- later Phase 7D runtime implementation approval was granted separately
- the implemented runtime state now lives in
  `codex/tasks/048-phase7d-single-gate-runtime-wrapper.md` and
  `docs/RELEASE_SNAPSHOT_PHASE7.md`

## Naming decision

This document uses the name
`docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md` because it is not
another implementation plan. It is the readiness review gate before the future
high-risk Phase 7D runtime implementation.

## Readiness objective

The review must answer:

- Is Phase 7D allowed to execute one primitive at all?
- What exact preconditions must pass before primitive execution?
- What exact approval flag semantics are allowed?
- What exact vault write boundary is permitted?
- What audit artifact must be written for success, failure, blocked, and
  prevented?
- What must happen if primitive execution fails?
- What must never happen under any condition?
- How must the Phase 7B verifier be used after wrapper execution?
- What must be tested before Phase 7D can merge?

## Readiness status model

`ready_for_implementation`

- all review categories are explicitly accepted

`blocked`

- a required review category is incomplete or ambiguous
- this is the default runtime readiness status after Phase 7D-R

`rejected`

- review identifies an unsafe design that would allow multi-gate execution,
  global approval, primitive execution without preconditions, or unaudited
  mutation

Required statement:

- Phase 7D-R completion does not authorize Phase 7D runtime implementation.
- Runtime implementation remains blocked until the user explicitly approves
  proceeding to Phase 7D.

## Primitive invocation policy

Future Phase 7D must:

- execute at most one primitive per invocation
- invoke a primitive only through an explicit allowlist mapping
- never build a primitive command from an untrusted gate string
- never execute a primitive if the gate is unknown
- never execute a primitive if the selected gate is not `plan_ready`
- never execute a primitive if the Phase 6C verdict is not `ready`
- never execute a primitive if the Phase 6E overall verdict is `failed`
- never execute a primitive if the matching approval flag is missing
- never execute a primitive if an unrelated approval flag is truthy
- never execute a primitive if multiple approval flags are truthy
- never execute a primitive if global approval or approve-all evidence exists
- never run the next gate automatically
- never run chain execution
- never retry silently

An unknown gate or any untrusted dynamic primitive invocation means prevented /
no primitive execution.

## Selected-gate-only enforcement

Future Phase 7D must:

- accept exactly one selected gate
- allowed gates:
  - `promote`
  - `decision`
  - `finalization`
- the selected gate must exist in Phase 6E `per_gate_plan`
- the selected gate `plan_ready` must be true
- the selected gate `blocked_reason` must be empty or null
- Phase 6E overall `blocked` may be acceptable only if the selected gate itself
  is ready
- Phase 6E overall `failed` is always rejected
- decision requires promote completion evidence
- finalization requires decision completion evidence
- finalization requires `compliance_status` approved

## Approval flag semantics

Future Phase 7D must:

- require exactly one matching gate-specific approval flag by gate:
  - promote uses `APPROVE_PROMOTE`
  - decision uses `APPROVE_DECISION`
  - finalization uses `APPROVE_FINALIZE`
- reject a missing matching flag
- reject an unrelated truthy approval flag
- reject multiple truthy approval flags
- reject any global approval flag
- reject an approve-all intent
- reject approval flag persistence
- reject an approval flag loaded from config
- reject an approval flag embedded in an artifact body
- never write an approval flag truthy assignment into an audit artifact
- record `approved_flag_name` only as a name

Note: this differs from the Phase 6C read-only wrapper, which rejects every
approval flag. Phase 7D must accept exactly the one matching gate flag and
reject every other truthy approval flag; Phase 7D implementers must not copy the
Phase 6C reject-all logic.

## Precondition evidence contract

Future Phase 7D must validate:

- Phase 6B packet exists
- Phase 6B packet is safe
- Phase 6B packet `dry_run` is true
- Phase 6C verifier output exists
- Phase 6C verifier output is safe
- Phase 6C verdict is `ready`
- Phase 6E execution plan exists
- Phase 6E execution plan is safe
- Phase 6E `dry_run` is true
- Phase 6E overall verdict is not `failed`
- `product_id` matches across operator input, Phase 6B, Phase 6C, and Phase 6E
- `report_week` matches across operator input, Phase 6B, Phase 6C, and Phase 6E
- the selected gate exists in Phase 6E `per_gate_plan`
- the selected gate `plan_ready` is true
- the selected gate `blocked_reason` is empty or null
- operator identity is non-empty and not a placeholder
- approval reason is non-empty and not a placeholder
- a gate-specific approval intent is present
- referenced paths are relative `tmp/` paths
- no leakage tokens appear in input evidence

## Audit-before/after behavior

Future Phase 7D must write audit artifacts for all outcomes:

- `success`
- `failure`
- `blocked`
- `prevented`

The audit artifact must include all Phase 7B required fields:

- `product_id`
- `report_week`
- `selected_gate`
- `primitive_name`
- `operator`
- `approval_reason`
- `timestamp`
- `source_packet_path`
- `verifier_path`
- `execution_plan_path`
- `precondition_summary`
- `result_summary`
- `outcome`
- `mutation_attempted`
- `gate_specific_approval_intent`
- `approved_flag_name`
- `wrapper_version`
- `audit_schema_version`

Audit rules:

- a prevented or blocked audit should be written before primitive execution when
  safe
- a success or failure audit should be written after the primitive result is
  known
- a primitive failure must produce a failure audit
- an audit must not include an approval primitive command form
- an audit must not include an approval flag truthy assignment
- an audit must not include a secret marker
- an audit must not include an external URL scheme
- an audit must not include an operator-local path
- the default audit location must be a relative `tmp/` path
- a durable audit location is out of scope unless a future phase approves it

Crash-window mitigation:

- Phase 7D must write an intent / pre-execution audit record before mutation
  when safe.
- Phase 7D must write a result / post-execution audit record after the primitive
  result is known.
- Phase 7D must not claim success unless both the post-mutation state and the
  result audit record are produced.
- If the primitive succeeds but the result audit cannot be written, the wrapper
  must surface partial completion and require manual review.
- This prevents silent mutation without audit visibility.

## Vault write boundary

Future Phase 7D is the first possible mutation phase. It must define:

- no vault write on a failed precondition
- no vault write on a prevented or blocked outcome except an audit under `tmp/`
- a vault write may occur only inside the selected primitive after all wrapper
  preconditions pass
- the wrapper itself must not directly write product, decision, or finalization
  vault artifacts unless explicitly designed and tested
- the wrapper must not write to the product or decision vault areas directly
  unless that is already the selected primitive behavior
- no vault write outside the selected primitive path
- no durable audit in the vault in Phase 7D unless separately approved
- all non-audit runtime outputs must remain under `tmp/` unless the selected
  primitive itself writes as designed

## Failure and rollback posture

Future Phase 7D must:

- fail closed on a failed precondition
- produce a prevented or blocked audit where safe
- stop after a primitive failure
- produce a failure audit after a primitive failure
- never retry silently
- never rollback automatically
- never run a compensating primitive automatically
- never run the next gate automatically
- keep partial completion visible
- document the rerun procedure
- require manual review after a primitive failure

## Emergency stop and dry-run decision

The readiness review must decide whether Phase 7D implementation must include:

- a default dry-run mode
- an explicit execution flag
- a kill-switch environment variable
- an emergency-stop file
- an operator confirmation string
- a wrapper-level dry-run report before mutation

Required policy:

- Phase 7D must default to dry-run or prevented mode unless a matching gate
  approval flag and an operator confirmation are both present.
- Runtime implementation remains blocked until this policy is explicitly accepted by the user before Phase 7D implementation.

## Phase 7B verifier integration

Future Phase 7D must:

- write an audit artifact compatible with Phase 7B
- print the audit artifact path
- recommend audit verification after the artifact is written
- not auto-run the Phase 7B verifier by default if doing so couples mutation to
  verification
- never let the Phase 7B verifier trigger the next gate
- never treat a verifier `valid` result as approval
- never infer approval from a verifier result
- keep the verifier read-only

This is stated as policy rather than as an executable command.

## Forbidden under all conditions

Future Phase 7D must never:

- execute more than one gate
- execute a primitive from an untrusted dynamic string
- execute a primitive without matching gate approval
- execute a primitive if Phase 6C is not ready
- execute a primitive if the selected gate is not `plan_ready`
- execute a primitive if Phase 6E is failed
- run the next gate automatically
- retry silently
- rollback automatically
- infer approval
- accept global approval
- accept approve-all
- accept a multi-gate request
- use backend/API/database/network
- autopublish
- campaign launch
- marketplace submit
- generate affiliate links
- write a durable audit into the vault without separate approval

## Future Phase 7D implementation checklist

Phase 7D must satisfy the following before merge:

- wrapper exists and is executable
- wrapper rejects unsafe flags
- wrapper accepts exactly one gate
- wrapper rejects multi-gate
- wrapper validates Phase 6B/6C/6E evidence
- wrapper validates selected-gate readiness
- wrapper validates the matching flag only
- wrapper uses an explicit primitive allowlist
- wrapper executes at most one primitive
- wrapper writes an audit artifact for all outcomes
- the audit passes the Phase 7B verifier
- no vault write on a failed precondition
- no primitive execution on a failed precondition
- a primitive failure stops execution
- no next gate
- no chain execution
- no backend/API/database/network
- cross-CWD execution
- output self-safety
- full suite passes

## Documentation update scope

Phase 7D-R updates docs additively only:

- [`ROADMAP.md`](ROADMAP.md)
- [`PROJECT_STATE.md`](PROJECT_STATE.md)
- [`SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`](SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md)
- [`RELEASE_SNAPSHOT_PHASE6.md`](RELEASE_SNAPSHOT_PHASE6.md)

- ROADMAP marks Phase 7D-R complete as the readiness review.
- ROADMAP keeps Phase 7D as the future high-risk implementation.
- PROJECT_STATE points to this readiness review.
- The single-gate wrapper implementation plan points to this readiness review.
- RELEASE_SNAPSHOT_PHASE6 may include a future pointer only.
- No Phase 6 release matrix rewrite occurs.

## Phase 7D-P implementation blueprint

Phase 7D-P finalizes the implementation blueprint derived from this review. See
[`PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`](PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md).
Runtime readiness remains blocked, and no runtime wrapper exists in Phase 7D-P.
This additive pointer does not change or authorize any readiness decision above.

## Phase 7D implementation follow-through

Phase 7D runtime implementation was later approved explicitly and carried this
review forward as the live single-gate manual approval wrapper boundary. That
later implementation does not change the historical scope of Phase 7D-R itself.

## Known limitations

- No runtime wrapper yet.
- No approval mutation yet.
- No Phase 7D command yet.
- No durable audit store yet.
- No auth/operator identity implementation.
- No backend/API/database.
- No marketplace connector.
- No autopublish.
- No production deployment.
- Phase 7D runtime readiness remains blocked.
