# Single-gate Manual Approval Wrapper Boundary (Phase 6F)

## Purpose

Phase 6F defines the contract for a **future** manual approval wrapper that may
execute exactly one selected gate per invocation, after the read-only evidence
chain (Phase 6B packet + Phase 6C verifier + Phase 6E execution plan) is complete
and verified. It defines the boundary only; it implements no wrapper and
executes nothing.

## Scope

- boundary-only; docs/tests/task-only
- no runtime command
- no vault read/write
- no primitive execution
- no approval mutation
- no chain execution
- no global approve

Primitive file names and approval flag names are referenced as names only; this
document contains no command forms and no approval flag assignments.

## Required preconditions before any future single-gate wrapper

A future wrapper must require **all** of these before any gate may execute:

- Phase 6B packet exists.
- Phase 6C verifier output exists.
- Phase 6E execution plan exists.
- Phase 6C verdict is `ready`.
- Phase 6E verdict is `blocked` or `ready`, not `failed`.
- `product_id` matches across operator input, Phase 6B packet, Phase 6C
  verifier, and Phase 6E plan.
- `report_week` matches across operator input, Phase 6B packet, Phase 6C
  verifier, and Phase 6E plan.
- Phase 6B packet has `dry_run: true`.
- Phase 6E plan has `dry_run: true`.
- Phase 6C no-leakage checks passed.
- Phase 6C sources-tmp-only checks passed.
- Phase 6C finalization consistency check passed.
- the selected gate exists in the Phase 6E `per_gate_plan`.
- the selected gate is `plan_ready` unless the gate is explicitly documented as
  blocked and prevented.
- operator identity is recorded.
- approval reason is provided and is not a placeholder.
- gate-specific approval intent is provided.

## Single-gate execution policy

- a future wrapper may execute exactly one selected gate per run
- allowed gate names:
  - `promote`
  - `decision`
  - `finalization`
- no chain execution
- no approve-all mode
- no automatic next-gate execution
- no direct execution from the UI shell
- no skipping the required order
- decision requires promote completion evidence
- finalization requires decision completion evidence
- finalization requires `compliance_status` to be `approved`
- readiness is not authorization to mutate

## Gate-to-primitive mapping

Gates map to primitives (names only):

- promote gate -> `promote_product_candidates.py`
- decision gate -> `create_decision.py`
- finalization gate -> `finalize_decision.py`

Rules:

- names are references only
- no command forms
- no direct primitive execution in Phase 6F
- no wrapper implementation in Phase 6F

## Approval flag policy

Flag names only:

- `APPROVE_PROMOTE`
- `APPROVE_DECISION`
- `APPROVE_FINALIZE`

Rules:

- a future wrapper must require only the flag matching the selected gate
- a future wrapper must reject unrelated approval flags
- a future wrapper must reject multiple approval flags
- a future wrapper must reject global approval intent
- no approve-all flag
- flags are per-run and per-gate
- flags must not be persistent
- no command example may assign a truthy value to these flags

## Audit model

Every future wrapper invocation must write one audit artifact with the fields:

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

Rules:

- audit must record success
- audit must record failure
- audit must record blocked or prevented execution
- audit must show whether mutation was attempted
- audit is written under `tmp/` first unless a future phase explicitly approves
  another location
- audit must be machine-readable and operator-readable in a future
  implementation

## Failure and safety model

- a failed precondition means no primitive execution
- a failed primitive means stop and audit
- no automatic rollback
- no silent retry
- no overwrite unless the existing primitive already enforces it
- partial completion must remain visible
- rerun policy must be explicit
- non-idempotent risks must be documented
- a future implementation must not hide prevented, failed, or partially
  completed state

## Forbidden automation

The following are forbidden behaviors, not commands to run:

- autopublish
- campaign launch
- affiliate link generation
- marketplace connector
- external API submit
- hidden promotion
- UI-direct approval
- global approve
- multi-gate execution
- approve-all mode
- automatic next-gate execution
- finalization without compliance approved
- vault write without explicit gate-specific approval
- backend / API / database
- network calls
- silent retry after a failed gate

## Future roadmap

- Phase 6G may implement an audit verifier.
- Phase 6H may update the release snapshot.
- Any actual wrapper implementation must be a separate, explicitly approved
  phase.
- Any backend, API, database, or marketplace implementation must be a separate
  approved phase.

## Phase 6G audit verifier boundary

Phase 6G is **boundary-only**: it defines the contract for a future audit
verifier in
[`MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md`](MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md).
No runtime audit verifier exists yet. Phase 6G defines the future audit
verification expectations for audit artifacts produced by a future single-gate
wrapper; its audit verifier schema is a verifier-level superset of the Phase 6F
audit model.

## Known limitations

- Boundary documentation only; no wrapper, gate execution, or mutation exists.
- Operator identity is a placeholder; no authentication exists.
- Future Phase 6G+ are separate implementation phases under their own approval.
