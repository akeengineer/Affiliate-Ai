# Single-gate Manual Approval Wrapper Implementation Plan (Phase 7C)

## Purpose

Phase 7C plans a future runtime wrapper that executes exactly one selected
manual approval gate per invocation. Phase 7C consumes the Phase 6F boundary
contract from
[`SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`](SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md)
as its source of truth and adds no new rules. Phase 7C is docs/tests/task-only:
it plans the wrapper but implements no runtime wrapper and executes nothing.
Phase 7D, not Phase 7C, is the future high-risk runtime implementation phase.

## Scope

- implementation plan only
- docs/tests/task-only
- no runtime wrapper
- no runtime command
- no approval mutation
- no vault read/write
- no primitive execution
- no approval primitive execution
- no chain execution
- no global approve
- no multi-gate execution

Primitive file names, approval flag names, and future wrapper command names are
referenced as names only; this document contains no command forms for approval
primitives and no approval flag assignments.

## Naming decision

This implementation plan uses the symmetric name
`docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md` because it
mirrors `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`, matching the
convention already established by the Phase 7A audit verifier implementation
plan.

## Implementation objective

The future wrapper must:

- accept exactly one selected gate
- accept `product_id`
- accept `report_week`
- require operator identity
- require approval reason
- require gate-specific approval intent
- require a Phase 6B packet
- require Phase 6C verifier output with a `ready` verdict
- require a Phase 6E execution plan
- require the selected gate present in Phase 6E `per_gate_plan`
- require the selected gate `plan_ready` true
- require the selected gate not blocked
- require only the matching approval flag
- reject unrelated approval flags
- reject multiple approval flags
- reject global approval
- reject approve-all
- reject chain execution
- execute at most one primitive
- write one audit artifact
- allow the Phase 7B verifier to validate that audit artifact afterward

## Future command shape

The future wrapper command name is a proposed future name only:

```text
bash scripts/dev/run_phase7d_single_gate_wrapper.sh <gate> <product_id> <report_week> --operator <operator> --reason <reason>
```

- this is a proposed future name only
- no runtime wrapper exists in Phase 7C
- Phase 7C must not add this file
- no approval primitive command forms are included
- the future wrapper must accept exactly one gate
- the future wrapper must not accept multiple gates
- the future wrapper must not provide an approve-all mode

## Precondition contract

The future wrapper must validate before execution:

- the Phase 6B packet exists and is safe
- the Phase 6B packet has `dry_run` true
- the Phase 6C verifier output exists and is safe
- the Phase 6C verdict is `ready`
- the Phase 6E execution plan exists and is safe
- the Phase 6E plan has `dry_run` true
- the Phase 6E overall verdict is not `failed`
- the selected gate exists in Phase 6E `per_gate_plan`
- `per_gate_plan[selected_gate].plan_ready` is true
- `per_gate_plan[selected_gate].blocked_reason` is empty or null
- `product_id` matches across operator input, Phase 6B, Phase 6C, and Phase 6E
- `report_week` matches across operator input, Phase 6B, Phase 6C, and Phase 6E
- decision requires promote completion evidence
- finalization requires decision completion evidence
- finalization requires `compliance_status` to be `approved`
- operator identity is non-empty and not a placeholder
- approval reason is non-empty and not a placeholder
- gate-specific approval intent is present
- no leakage tokens appear in inputs
- referenced paths are relative `tmp/` paths only
- during Phase 7D only, vault writes must be limited to the selected primitive
  path

Important nuance:

- the Phase 6E overall verdict may be `blocked` because another gate is blocked
- the future wrapper must reject an overall `failed` verdict
- the future wrapper must decide readiness by the selected gate's readiness:
  - the selected gate exists in `per_gate_plan`
  - the selected gate `plan_ready` is true
  - the selected gate is not blocked

## Gate-to-primitive mapping

The future wrapper must map:

- promote -> `promote_product_candidates.py`
- decision -> `create_decision.py`
- finalization -> `finalize_decision.py`

Rules:

- Phase 7C references names only
- Phase 7C must not include command forms
- Phase 7D must execute at most one mapped primitive
- Phase 7D must not invoke primitives by a dynamic untrusted string
- Phase 7D must use an explicit allowlist mapping
- an unknown gate means prevented / no primitive execution

## Approval flag policy

The future wrapper must require exactly one matching gate-specific approval flag:

- promote requires `APPROVE_PROMOTE`
- decision requires `APPROVE_DECISION`
- finalization requires `APPROVE_FINALIZE`

The future wrapper must reject:

- a missing matching flag
- an unrelated approval flag
- multiple approval flags
- a global approval flag
- an approve-all intent
- approval flag persistence
- an approval flag in a config file
- an approval flag in an artifact body
- any truthy approval flag not matching the selected gate

Phase 7C must not include examples with approval flag truthy assignments.

## Audit artifact contract

The future wrapper must write one audit artifact for every invocation outcome:

- `success`
- `failure`
- `blocked`
- `prevented`

The audit artifact should be JSON and may optionally include Markdown. The audit
JSON must include all Phase 7B required fields:

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

Audit artifact rules:

- default to safe relative `tmp/` output
- a durable audit location requires a separate future explicitly approved phase
- no raw secrets
- no command forms
- no external URLs
- no operator-local paths
- no vault path unless a future durable-audit design explicitly approves it
- validatable by the Phase 7B audit verifier
- the audit may record the approval flag name but must not record an approval
  flag truthy assignment

Important Phase 7B integration rule: if the audit body includes an approval flag
truthy assignment, command forms, raw secrets, external URLs, operator-local
paths, or vault paths, the Phase 7B verifier should mark it invalid.

## Failure and safety behavior

The future wrapper must:

- fail closed before primitive execution if any precondition fails
- write a prevented or blocked audit artifact when safe to do so
- execute no primitive on a failed precondition
- execute at most one primitive after the approval gate passes
- stop after a primitive failure
- write a failure audit artifact after a primitive failure
- never auto-run the next gate
- never retry silently
- never rollback automatically
- never infer approval
- never normalize unsafe content into safe content
- keep partial completion visible
- make the rerun policy explicit

## Phase 7B verifier integration

Future flow after Phase 7D:

1. the wrapper executes or prevents one gate
2. the wrapper writes an audit artifact
3. an operator or CI may run the Phase 7B audit verifier against that artifact
4. the audit verifier remains read-only
5. the verifier result does not trigger the next gate
6. the verifier result does not infer approval
7. the audit path must be a relative `tmp/` path compatible with the Phase 7B
   input contract

## Future Phase 7D test plan

- promote gate success path executes the promote primitive only
- decision gate success path executes the decision primitive only
- finalization gate success path executes the finalization primitive only
- missing matching flag -> prevented / no primitive
- unrelated flag -> prevented / no primitive
- multiple flags -> prevented / no primitive
- global approval -> prevented / no primitive
- selected gate not in plan -> prevented / no primitive
- selected gate blocked -> prevented / no primitive
- Phase 6C not ready -> prevented / no primitive
- Phase 6E failed -> prevented / no primitive
- product/report mismatch -> prevented / no primitive
- finalization without compliance approved -> prevented / no primitive
- primitive failure -> failure audit and no next gate
- audit artifact produced for success/failure/blocked/prevented
- Phase 7B verifier validates the generated audit
- no auto next-gate
- no chain execution
- no vault write outside the primitive path
- no primitive execution on a failed precondition
- cross-CWD execution
- wrapper rejects unsafe env/config
- output self-safety
- docs token regression

## Documentation update scope

Phase 7C updates docs additively only:

- [`ROADMAP.md`](ROADMAP.md)
- [`PROJECT_STATE.md`](PROJECT_STATE.md)
- [`SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`](SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md)
- [`RELEASE_SNAPSHOT_PHASE6.md`](RELEASE_SNAPSHOT_PHASE6.md)

- ROADMAP marks Phase 7C as the complete implementation plan.
- ROADMAP marks Phase 7D as the future high-risk implementation.
- PROJECT_STATE points to this plan.
- The single-gate boundary points to this plan.
- RELEASE_SNAPSHOT_PHASE6 may include a future pointer only.
- No Phase 6 release matrix rewrite occurs.

## Phase 7D-R readiness review

Phase 7D-R completes the high-risk readiness review for this plan. See
[`HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md`](HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md).
No runtime wrapper exists in Phase 7D-R. Phase 7D remains blocked until explicit
user approval.

## Phase 7D-P implementation blueprint

Phase 7D-P finalizes the implementation blueprint for this future wrapper. See
[`PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`](PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md).
No runtime wrapper exists in Phase 7D-P. Phase 7D remains blocked until explicit
user approval.

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
