# Phase 7D Runtime Wrapper Implementation Blueprint

```text
phase7d_plan_finalization_status: success
phase7d_runtime_readiness: blocked
```

### Purpose

This document translates the Phase 7D-R readiness review into a concrete
implementation blueprint for the future runtime single-gate manual approval
wrapper. It finalizes implementation intent only. Runtime implementation remains
blocked and requires separate explicit acceptance.

### Scope

- implementation blueprint only
- docs/tests/task-only
- no runtime wrapper
- no runtime command
- no approval mutation
- no primitive execution
- no vault reads or writes
- no backend, API, database, or network behavior

Phase 7D-P does not change runtime behavior, execute Phase 2G/2H/2I, generate
affiliate content, autopublish, launch campaigns, or add production services.

### Future runtime files

These files are proposed only:

- `scripts/dev/run_phase7d_single_gate_wrapper.sh`
- `scripts/dev/execute_single_gate_approval.py`
- `tests/test_phase7d_single_gate_wrapper.py`

Phase 7D-P does not create these files. Their names define the future review
surface; they are not present runtime capabilities.

### Future wrapper CLI contract

The proposed future command shape is:

```text
bash scripts/dev/run_phase7d_single_gate_wrapper.sh <gate> <product_id> <report_week> --operator <operator> --reason <reason> --intent <intent>
```

This shape is proposed-only. Phase 7D-P must not add this command. It contains
no approval primitive command forms and no approval flag assignments.

The future interface must:

- accept exactly one gate: `promote`, `decision`, or `finalization`
- reject zero or multiple gates
- reject missing or placeholder operator, reason, or intent
- provide no global approval or approve-all mode
- provide no approve-all option
- permit no multiple-gate request
- permit no chain execution or automatic next gate

### Future wrapper shell behavior

The future shell wrapper should:

- set strict shell mode
- resolve the repository root dynamically and change to it
- enforce the required positional and named arguments
- reject multiple gate values
- reject missing operator, reason, or intent
- reject placeholder operator, reason, or intent
- choose a Python interpreter using the repository's established convention
- call the Python core file
- not execute primitives directly in shell
- keep primitive invocation inside the Python core allowlist only
- support cross-CWD execution

The shell layer owns process setup and interface validation, not business logic
or primitive selection.

### Future Python core design

The future Python core should:

- parse gate, product_id, report_week, operator, reason, and intent
- validate the product_id pattern
- validate the report_week pattern
- validate the selected gate enum
- load the Phase 6B packet
- load the Phase 6C verifier output
- load the Phase 6E execution plan
- validate evidence path safety
- validate product and report consistency across Phase 6B, Phase 6C, Phase 6E,
  and operator input
- validate Phase 6B `dry_run` is true
- validate Phase 6C verdict is `ready`
- validate Phase 6E `dry_run` is true
- reject Phase 6E overall `failed`
- validate the selected gate exists in `per_gate_plan`
- validate selected gate `plan_ready` is true
- validate selected gate `blocked_reason` is empty or null
- validate ordering evidence:
  - decision requires promote completion evidence
  - finalization requires decision completion evidence
  - finalization requires `compliance_status` approved
- validate approval flag semantics
- validate emergency stop, dry-run, and operator confirmation policy
- write an intent/pre-execution audit when safe
- invoke at most one primitive through the explicit allowlist after all checks
  pass
- write a result/post-execution audit
- print the audit artifact path
- never run Phase 7B as a mutation trigger
- never run the next gate

Suggested function boundaries are argument parsing, evidence discovery, safe JSON
loading, cross-artifact consistency, phase-specific validation, selected-gate
validation, approval-state validation, audit construction/writing, allowlisted
primitive selection, and top-level orchestration.

### Future validation pipeline

The pipeline order is mandatory:

1. CLI argument validation
2. Input path and evidence discovery
3. Evidence safety validation
4. Product/report consistency validation
5. Phase 6B packet validation
6. Phase 6C verifier validation
7. Phase 6E execution plan validation
8. Selected-gate readiness validation
9. Approval flag validation
10. Emergency stop / dry-run / operator confirmation validation
11. Intent audit write
12. Single primitive invocation
13. Result audit write
14. Phase 7B handoff note

Any failed validation before primitive execution results in a prevented or
blocked audit where safe. No primitive execution occurs before all validations pass.
No vault write occurs before all validations pass. A relative `tmp/` audit is
not a vault write.

### Future primitive invocation strategy

The allowlist mapping is:

- `promote` -> `promote_product_candidates.py`
- `decision` -> `create_decision.py`
- `finalization` -> `finalize_decision.py`

Rules:

- explicit dictionary/allowlist only
- no dynamic import from the gate string
- no shell eval
- no arbitrary subprocess target
- no untrusted string command construction
- at most one primitive
- primitive invocation only after all validations pass
- primitive failure stops execution
- no next gate
- no chain execution

The names above are references only. This blueprint contains no Python command
forms for the primitives.

### Future approval flag strategy

The selected gate maps by name to `APPROVE_PROMOTE`, `APPROVE_DECISION`, or
`APPROVE_FINALIZE`. The future wrapper must:

- require exactly one matching approval flag
- reject a missing matching flag
- reject an unrelated truthy flag
- reject multiple truthy flags
- reject global approval
- reject approve-all
- reject approval flag persistence
- reject an approval flag loaded from configuration
- reject an approval flag embedded in an artifact body
- never persist an approval flag in wrapper state

An audit may record only `approved_flag_name`. It must never record a truthy
approval assignment. Flag names in this blueprint are policy references only.

### Future audit strategy

The future wrapper writes audit artifacts for:

- `success`
- `failure`
- `blocked`
- `prevented`

Every audit includes:

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

Write-order rules:

- write the intent/pre-execution audit before mutation when safe
- write the result/post-execution audit after the primitive result is known
- make prevented or blocked outcomes visible before any possible primitive call
- make primitive failure visible in a failure result audit
- make no success claim unless post-mutation state and result audit are both
  produced
- primitive succeeds but result audit fails means partial completion visible and manual review required

Location and content rules:

- use a default relative `tmp/` output
- keep a durable audit store out of scope
- write no durable audit in the vault without separate approval
- include no raw secrets, command forms, external URL schemes, operator-local
  paths, or vault paths
- produce an artifact validatable by the Phase 7B verifier
- keep every evidence reference a relative `tmp/` path compatible with Phase 7B

### Future Phase 7B handoff

- the wrapper prints the audit artifact path
- an operator or CI may run the Phase 7B verifier manually as a separate,
  non-mutating step
- the wrapper does not auto-run Phase 7B by default
- Phase 7B `valid` is not approval and does not infer approval
- Phase 7B does not trigger the next gate
- Phase 7B remains read-only

This section intentionally contains no executable verifier example. Verification
is evidence review, never a mutation trigger.

### Future test implementation strategy

#### Group A: no-mutation precondition failures

- missing or unsafe Phase 6B packet
- Phase 6B `dry_run` false
- missing or not-ready Phase 6C output
- missing or failed Phase 6E plan
- product or report-week mismatch
- selected gate missing, not `plan_ready`, or blocked
- missing or placeholder operator, reason, or intent
- missing matching approval flag
- unrelated truthy flag or multiple truthy flags
- global approval or approve-all evidence
- emergency stop active

#### Group B: single-gate success paths

- promote success executes only the promote primitive
- decision success executes only the decision primitive
- finalization success executes only the finalization primitive

#### Group C: ordering and compliance

- decision without promote completion evidence is prevented
- finalization without decision completion evidence is prevented
- finalization without approved compliance is prevented

#### Group D: primitive failure

- primitive failure writes a failure audit
- primitive failure stops execution
- no next gate runs
- manual review is required

#### Group E: audit/verifier

- prevented, blocked, success, and failure audits are Phase 7B-compatible
- audit output contains no forbidden raw tokens
- input evidence is not rewritten

#### Group F: containment and hygiene

- no vault write on a failed precondition
- no primitive execution on a failed precondition
- no vault write outside the selected primitive path
- output remains under `tmp/`
- cross-CWD execution works
- shell syntax, `py_compile`, focused tests, and full suite pass

### Future mocking/subprocess strategy

- tests must not call real mutation primitives for failure or precondition cases
- controlled success-path fixtures may use explicit monkeypatch or subprocess
  wrappers only when the target and effects are isolated
- primitive invocation should be isolated and observable
- each success test proves exactly one primitive was selected
- each success test proves unselected primitives were not called
- no-mutation tests snapshot the vault before/after
- tests must run isolated, not concurrently, because shared `tmp/` artifacts can
  race

### Future emergency stop and dry-run strategy

- default mode must be dry-run/prevented unless explicit execution approval is
  present
- execution requires the matching approval flag and operator confirmation
- emergency stop should override approval and prevent primitive execution
- a dry-run report should show what would execute without executing
- runtime readiness remains blocked until this strategy is explicitly accepted
  before Phase 7D runtime implementation

### Future merge checklist

- wrapper files added intentionally
- wrapper entrypoint executable
- Python core `py_compile` passes
- shell syntax validation passes
- no dynamic primitive execution
- explicit allowlist only
- exactly one gate accepted
- matching approval flag semantics tested
- Phase 6B/6C/6E preconditions tested
- selected-gate readiness tested
- audit write-order tested
- crash-window mitigation tested
- Phase 7B compatibility tested
- no primitive on failed precondition
- no vault write on failed precondition
- no next gate
- no chain execution
- no backend, API, database, or network behavior
- no autopublish, campaign, or marketplace behavior
- full suite passes

### Known limitations

- no runtime wrapper yet
- no approval mutation yet
- no Phase 7D command yet
- no durable audit store yet
- no auth/operator identity implementation
- no backend, API, or database
- no marketplace connector
- no autopublish
- no production deployment
- Phase 7D runtime readiness remains blocked

### Phase 7E release-state pointer

Phase 7E records the runtime blocked release state. See
`docs/RELEASE_SNAPSHOT_PHASE7.md`. Runtime readiness remains blocked, and no
runtime wrapper exists in Phase 7E.
