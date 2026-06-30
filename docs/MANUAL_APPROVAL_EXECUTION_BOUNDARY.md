# Manual Approval Execution Boundary (Phase 6D)

## Purpose

Phase 6D defines the contract for a **future** manual approval execution command
that may run the existing manual-approved primitives after the read-only
evidence chain (Phase 6B packet + Phase 6C verifier) is complete and verified.
It defines the boundary only; it implements no command and executes nothing.

## Scope

- boundary-only; docs/tests/task-only
- no runtime command
- no vault read/write
- no primitive execution
- no approval mutation

Primitive file names are referenced as future targets only; this document
contains no command forms and no approval flag assignments.

## Required preconditions before future approval execution

A future approval execution command must require **all** of the following before
any gate may execute:

- Phase 6B packet exists.
- Phase 6C verifier output exists.
- Phase 6C verdict is `ready`.
- Phase 6C `warning` and `failed` are not sufficient for mutation.
- `product_id` matches across operator input, Phase 6B packet, and Phase 6C
  verifier.
- `report_week` matches across operator input, Phase 6B packet, and Phase 6C
  verifier.
- Phase 6B packet has `dry_run: true`.
- Phase 6C no-leakage checks passed.
- Phase 6C sources-tmp-only checks passed.
- Phase 6C finalization consistency check passed.
- operator approval reason is provided and is not a placeholder.
- operator identity placeholder or future identity is recorded.
- source packet path is recorded.
- verifier path is recorded.

## Execution sequence policy

Mandatory future sequence:

```text
promote -> decision -> finalization
```

Gates map to primitives (names only):

- promote gate -> `promote_product_candidates.py`
- decision gate -> `create_decision.py`
- finalization gate -> `finalize_decision.py`

Rules:

- no gate skipping
- no out-of-order execution
- no direct execution from the UI shell
- no finalization unless `compliance_status` is `approved`
- each gate must re-check its own preconditions
- a failed gate stops the sequence
- partial completion must be visible in audit
- readiness is not authorization to mutate

## Flag policy

Flag names only:

- `APPROVE_PROMOTE`
- `APPROVE_DECISION`
- `APPROVE_FINALIZE`

Rules:

- flags are names only in Phase 6D
- no command example may assign a truthy value to these flags
- future approval must be explicit
- approval must be per-gate
- no broad/global approval
- no approve-all flag
- flags are per-run and must not be persistent
- a future command must reject ambiguous or global approval intent

## Audit model

Every future approved step must write an immutable-style audit artifact with the
fields:

- `product_id`
- `report_week`
- `gate_name`
- `primitive_name`
- `operator`
- `approval_reason`
- `timestamp`
- `source_packet_path`
- `verifier_path`
- `precondition_summary`
- `result_summary`

Rules:

- the audit artifact is written under `tmp/` first unless a future phase
  explicitly approves a vault/audit location
- audit must record success
- audit must record failure
- audit must record partial completion
- audit must be machine-readable and operator-readable in a future
  implementation
- an approved write must be explicit and logged

## Failure and rollback model

- no automatic rollback is assumed
- no overwrite unless the existing primitive already enforces it
- a failed gate stops the sequence
- partial completion must be visible in audit
- rerun policy must be explicit
- non-idempotent risks must be documented
- double-write risks must be avoided
- a future implementation must not hide partially completed state

## Forbidden automation

The following are forbidden behaviors, not commands to run:

- autopublish
- campaign launch
- affiliate link generation
- marketplace connector
- external API submit
- hidden promotion
- UI-direct approval
- finalization without compliance approved
- vault write without explicit gate-specific approval
- backend / API / database
- network calls
- broad/global approval
- skipped gate execution
- silent retry after a failed gate

## Future roadmap

- Phase 6E may implement a dry-run execution planner.
- Phase 6F may implement a single-gate manual approval wrapper.
- Phase 6G may implement an audit verifier.
- Phase 6H may update the release snapshot.

Any backend, API, database, or marketplace implementation must be a separate
approved phase, outside this boundary.

## Phase 6E dry-run execution planner

Phase 6E implements a read-only dry-run planner over the Phase 6B packet and
Phase 6C verifier, using this boundary as a contract reference
(existence/size/hash only). It shows what a future manual approval command would
require; it executes nothing.

```bash
bash scripts/dev/run_phase6e_approval_execution_plan.sh prod-laptop-stand 2026-W26
```

Outputs:

- `tmp/phase6e-approval-execution-plan/execution-plan-prod-laptop-stand-2026-W26.json`
- `tmp/phase6e-approval-execution-plan/execution-plan-prod-laptop-stand-2026-W26.md`

Verdict policy:

- `ready` = all gates plan-ready
- `blocked` = hard preconditions pass but one or more gates are blocked
- `failed` = invalid evidence or guardrail failure

The normal current verdict is expected to be `blocked` while `compliance_status`
is not approved (the finalization gate stays blocked). The planner is
**read-only**: no vault reads or writes, no approval mutation, no primitive
execution, no approval flag use, and no command form for the Phase 2G/2H/2I
primitives.

## Phase 6F single-gate wrapper boundary

Phase 6F is **boundary-only**: it defines the contract for a future single-gate
manual approval wrapper in
[`SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`](SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md).
No runtime single-gate wrapper exists yet. A future wrapper requires the Phase 6B
packet, a Phase 6C `ready` verifier verdict, and a Phase 6E execution plan as
evidence preconditions, and may execute exactly one gate per invocation.

## Known limitations

- Boundary documentation only; no execution command, gate, or mutation exists.
- Operator identity is a placeholder; no authentication exists.
- Future Phase 6F+ are separate implementation phases under their own approval.
