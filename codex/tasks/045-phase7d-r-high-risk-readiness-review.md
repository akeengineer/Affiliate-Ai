# Task 045 - Phase 7D-R High-risk Implementation Readiness Review

## 1. Purpose

Define the readiness review checklist and final implementation constraints for
the future Phase 7D runtime single-gate manual approval wrapper. Phase 7D-R is
the final review gate before any runtime wrapper that may call approval
primitives. It is docs/tests/task-only and implements no wrapper.

## 2. Scope

- Author the high-risk readiness review and a docs-contract test.
- Additively update ROADMAP, PROJECT_STATE, the single-gate wrapper
  implementation plan, and RELEASE_SNAPSHOT_PHASE6.
- Reference primitive file names, approval flag names, and the future wrapper
  command name as names only; never execute, modify, or include approval
  primitive command forms.

## 3. Files

- `codex/tasks/045-phase7d-r-high-risk-readiness-review.md`
- `docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md`
- `tests/test_phase7d_r_high_risk_readiness_review.py`
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md` (additive)
- `docs/RELEASE_SNAPSHOT_PHASE6.md` (additive future pointer)

## 4. Naming decision

The review uses `docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md` because
it is not another implementation plan; it is the readiness review gate before
the future high-risk Phase 7D runtime implementation.

## 5. Readiness objective

The review answers whether Phase 7D may execute one primitive at all, the exact
preconditions before execution, the exact approval flag semantics, the exact
vault write boundary, the audit artifact required for success/failure/blocked/
prevented, what must happen on primitive failure, what must never happen, how
the Phase 7B verifier is used afterward, and what must be tested before Phase 7D
can merge.

## 6. Readiness status model

`ready_for_implementation` when all review categories are explicitly accepted;
`blocked` (the default runtime readiness status after Phase 7D-R) when a required
category is incomplete or ambiguous; `rejected` when the review identifies an
unsafe design permitting multi-gate execution, global approval, primitive
execution without preconditions, or unaudited mutation. Phase 7D-R completion
does not authorize Phase 7D runtime implementation; runtime implementation
remains blocked until the user explicitly approves proceeding to Phase 7D.

## 7. Primitive invocation policy

At most one primitive per invocation, via an explicit allowlist mapping only,
never from an untrusted gate string; no execution if the gate is unknown, the
selected gate is not `plan_ready`, the Phase 6C verdict is not `ready`, the
Phase 6E overall verdict is `failed`, the matching approval flag is missing, an
unrelated approval flag is truthy, multiple approval flags are truthy, or
global/approve-all evidence exists; never auto-run the next gate, chain execute,
or retry silently.

## 8. Selected-gate-only enforcement

Exactly one gate from {`promote`, `decision`, `finalization`}; the selected gate
must exist in Phase 6E `per_gate_plan` with `plan_ready` true and empty/null
`blocked_reason`; Phase 6E overall `blocked` is acceptable only if the selected
gate itself is ready; Phase 6E overall `failed` is always rejected; decision
requires promote completion evidence; finalization requires decision completion
evidence and `compliance_status` approved.

## 9. Approval flag semantics

Exactly one matching gate-specific approval flag (`APPROVE_PROMOTE`,
`APPROVE_DECISION`, `APPROVE_FINALIZE`); reject a missing matching flag, an
unrelated truthy flag, multiple truthy flags, any global approval flag, an
approve-all intent, approval flag persistence, an approval flag from config, and
an approval flag embedded in an artifact body; never write an approval flag
truthy assignment into the audit; record `approved_flag_name` only as a name.
This differs from the Phase 6C reject-all wrapper and must not copy that logic.

## 10. Precondition evidence contract

Validate: Phase 6B packet exists/safe with `dry_run` true; Phase 6C output
exists/safe with `verdict` `ready`; Phase 6E plan exists/safe with `dry_run`
true and overall verdict not `failed`; the selected gate exists in
`per_gate_plan` with `plan_ready` true and empty/null `blocked_reason`;
`product_id`/`report_week` match across operator input, Phase 6B, Phase 6C, and
Phase 6E; operator identity and approval reason non-empty and not placeholders;
gate-specific approval intent present; referenced paths relative `tmp/`; no
leakage tokens in input evidence.

## 11. Audit-before/after behavior

Write an audit artifact for every outcome (`success`, `failure`, `blocked`,
`prevented`) with all 18 Phase 7B required fields. A prevented/blocked audit is
written before execution when safe; a success/failure audit after the result is
known; a primitive failure produces a failure audit. The audit must not include
an approval primitive command form, an approval flag truthy assignment, a secret
marker, an external URL scheme, or an operator-local path; the default location
is a relative `tmp/` path; a durable location is out of scope unless a future
phase approves it. Crash-window mitigation: write an intent/pre-execution record
before mutation and a result/post-execution record after; never claim success
without both post-mutation state and the result audit; on write failure surface
partial completion and require manual review.

## 12. Vault write boundary

Phase 7D is the first possible mutation phase: no vault write on a failed
precondition; no vault write on prevented/blocked except an audit under `tmp/`;
a vault write may occur only inside the selected primitive after all
preconditions pass; the wrapper itself must not write product/decision/
finalization vault artifacts unless that is already the selected primitive
behavior; no vault write outside the selected primitive path; no durable audit
in the vault without separate approval; all non-audit runtime output stays under
`tmp/`.

## 13. Failure and rollback posture

Fail closed on a failed precondition; produce a prevented/blocked audit where
safe; stop after a primitive failure and produce a failure audit; never retry
silently, rollback automatically, run a compensating primitive automatically, or
auto-run the next gate; keep partial completion visible; document the rerun
procedure; require manual review after a primitive failure.

## 14. Emergency stop and dry-run decision

Decide whether Phase 7D includes a default dry-run mode, an explicit execution
flag, a kill-switch environment variable, an emergency-stop file, an operator
confirmation string, and a wrapper-level dry-run report before mutation.
Required policy: Phase 7D defaults to dry-run or prevented mode unless a matching
gate approval flag and an operator confirmation are both present; runtime
implementation remains blocked until this policy is explicitly accepted.

## 15. Phase 7B verifier integration

Phase 7D writes a Phase 7B-compatible audit, prints its path, and recommends
verification afterward; it does not auto-run the verifier by default if that
couples mutation to verification; the verifier stays read-only, never triggers
the next gate, and a `valid` result is never treated as approval or used to
infer approval. Stated as policy, not as an executable command.

## 16. Forbidden under all conditions

Phase 7D must never execute more than one gate, execute a primitive from an
untrusted dynamic string, execute without matching gate approval, execute when
Phase 6C is not ready or the selected gate is not `plan_ready` or Phase 6E is
failed, auto-run the next gate, retry silently, rollback automatically, infer
approval, accept global approval / approve-all / a multi-gate request, use
backend/API/database/network, autopublish, campaign launch, marketplace submit,
generate affiliate links, or write a durable audit into the vault without
separate approval.

## 17. Future Phase 7D implementation checklist

Wrapper exists/executable; rejects unsafe flags; accepts exactly one gate;
rejects multi-gate; validates Phase 6B/6C/6E evidence; validates selected-gate
readiness; validates the matching flag only; uses an explicit primitive
allowlist; executes at most one primitive; writes an audit for all outcomes;
audit passes the Phase 7B verifier; no vault write on a failed precondition; no
primitive execution on a failed precondition; a primitive failure stops
execution; no next gate; no chain execution; no backend/API/database/network;
cross-CWD execution; output self-safety; full suite passes.

## 18. Documentation update scope

Additive only: ROADMAP marks Phase 7D-R complete (readiness review) and keeps
Phase 7D as future high-risk; PROJECT_STATE points to the readiness review and
states no runtime wrapper yet; the single-gate wrapper implementation plan points
to the readiness review; RELEASE_SNAPSHOT_PHASE6 gets a future pointer only, with
no Phase 6 release matrix rewrite.

## 19. No-execution and static-safety rules

The two new Phase 7D-R files (this task and the readiness review) must not
contain approval flag truthy assignments, bash wrapper invocation forms for
Phase 2G/2H/2I, python invocation forms for the primitive scripts, external URL
schemes, contiguous operator-local paths, or secret markers. Primitive file
names, approval flag names, and the proposed future wrapper command name remain
allowed as names only. Forbidden content is described with phrases such as
external URL scheme, approval flag truthy assignment, secret marker,
operator-local path, and approval primitive command form.

## 20. Test strategy

Deterministic docs-contract tests: task + readiness doc exist; task has
`phase7d_r_status: success`; readiness doc has `phase7d_runtime_readiness:
blocked`; readiness review only; no Phase 7D wrapper scripts exist; readiness
status model; runtime blocked until explicit approval; primitive invocation
policy with explicit allowlist and no untrusted dynamic invocation; selected-
gate-only enforcement with allowed gates, `per_gate_plan`, `plan_ready`, blocked
nuance, and overall-failed rejection; approval flag semantics; precondition
evidence contract; audit behavior for all outcomes with the 18 Phase 7B fields;
crash-window mitigation; vault write boundary; failure/rollback posture;
emergency stop/dry-run decision; Phase 7B verifier integration; forbidden-under-
all-conditions; the Phase 7D implementation checklist; the ROADMAP/PROJECT_STATE/
plan/RELEASE_SNAPSHOT_PHASE6 pointers; ROADMAP/PROJECT_STATE token regression; a
no-execution guard and static-safety scan over only the two new Phase 7D-R files.

## 21. Acceptance criteria

- Readiness doc, task, and test exist; the test passes.
- Task status is `phase7d_r_status: success` and runtime readiness is
  `phase7d_runtime_readiness: blocked`.
- Phase 7C/7B/7A, Phase 6H->6A, and Phase 5E/3E tests still pass; full suite
  passes.
- No runtime wrapper added; no Phase 7D scripts created; no hardcoded operator
  path in scripts.
- No approval mutation, vault read/write, or primitive execution is introduced.

## 22. Verification commands

```
python -m pytest -q tests/test_phase7d_r_high_risk_readiness_review.py
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

Run test groups one at a time; several tests share `tmp/` artifacts and must not
run concurrently.

## 23. Known limitations

- Readiness review only; no runtime wrapper, command, or approval mutation
  exists.
- No durable audit store yet.
- Phase 7D runtime readiness remains blocked until explicit user approval;
  Phase 7D is the future high-risk runtime implementation phase.

## 24. Final status target

`phase7d_r_status: success`

`phase7d_runtime_readiness: blocked`
