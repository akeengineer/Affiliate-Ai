# Task 044 - Phase 7C Single-gate Manual Approval Wrapper Implementation Plan

## 1. Purpose

Author the implementation plan for a future runtime single-gate manual approval
wrapper that executes exactly one selected gate per invocation. Phase 7C
consumes the Phase 6F boundary contract and is docs/tests/task-only; it
implements no runtime wrapper and executes nothing. Phase 7D, not Phase 7C, is
the future high-risk runtime implementation phase.

## 2. Scope

- Author the wrapper implementation plan and a docs-contract test.
- Additively update ROADMAP, PROJECT_STATE, the single-gate boundary, and
  RELEASE_SNAPSHOT_PHASE6.
- Reference primitive file names, approval flag names, and the future wrapper
  command name as names only; never execute, modify, or include approval
  primitive command forms.

## 3. Files

- `codex/tasks/044-phase7c-single-gate-wrapper-implementation-plan.md`
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`
- `tests/test_phase7c_single_gate_wrapper_implementation_plan.py`
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md` (additive pointer)
- `docs/RELEASE_SNAPSHOT_PHASE6.md` (additive future pointer)

No runtime scripts, wrappers, mutation commands, or approval commands are
created or modified.

## 4. Naming decision

The implementation plan uses the symmetric name
`docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`, mirroring
`docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md` and matching the Phase 7A
audit verifier implementation plan convention.

## 5. Implementation objective

The future wrapper accepts exactly one selected gate plus `product_id` and
`report_week`; requires operator identity, approval reason, and gate-specific
approval intent; requires a Phase 6B packet, Phase 6C verifier output with a
`ready` verdict, and a Phase 6E execution plan; requires the selected gate to be
present in Phase 6E `per_gate_plan` with `plan_ready` true and not blocked;
requires only the matching approval flag and rejects unrelated/multiple/global/
approve-all flags and chain execution; executes at most one primitive; writes
one audit artifact; and allows the Phase 7B verifier to validate that artifact.

## 6. Future command shape

The future wrapper command name is a proposed future name only:
`run_phase7d_single_gate_wrapper.sh`. No runtime wrapper exists in Phase 7C,
Phase 7C must not add that file, no approval primitive command forms are
included, and the future wrapper accepts exactly one gate and provides no
approve-all mode.

## 7. Precondition contract

The future wrapper validates: Phase 6B packet exists/safe with `dry_run` true;
Phase 6C output exists/safe with `verdict` `ready`; Phase 6E plan exists/safe
with `dry_run` true and overall verdict not `failed`; the selected gate exists
in `per_gate_plan` with `plan_ready` true and empty/null `blocked_reason`;
`product_id`/`report_week` match across operator input, Phase 6B, Phase 6C, and
Phase 6E; decision requires promote completion evidence; finalization requires
decision completion evidence and `compliance_status` `approved`; operator
identity and approval reason are non-empty and not placeholders; gate-specific
approval intent is present; no leakage tokens appear in inputs; referenced paths
are relative `tmp/` paths only. Nuance: the Phase 6E overall verdict may be
`blocked` because another gate is blocked, so readiness is decided by the
selected gate's readiness, not the overall verdict; an overall `failed` verdict
is rejected.

## 8. Gate-to-primitive mapping

promote -> `promote_product_candidates.py`, decision -> `create_decision.py`,
finalization -> `finalize_decision.py`. Phase 7C references names only; Phase 7D
executes at most one mapped primitive, must not invoke primitives by a dynamic
untrusted string, and must use an explicit allowlist mapping; an unknown gate
means prevented / no primitive execution.

## 9. Approval flag policy

Exactly one matching gate-specific approval flag is required (`APPROVE_PROMOTE`,
`APPROVE_DECISION`, `APPROVE_FINALIZE`). The wrapper rejects a missing matching
flag, an unrelated approval flag, multiple approval flags, a global approval
flag, an approve-all intent, approval flag persistence, an approval flag in a
config file, an approval flag in an artifact body, and any truthy approval flag
not matching the selected gate. Phase 7C includes no approval flag truthy
assignments.

## 10. Audit artifact contract

The future wrapper writes one audit artifact for every outcome (`success`,
`failure`, `blocked`, `prevented`) as JSON (optionally Markdown) including all
18 Phase 7B required fields: `product_id`, `report_week`, `selected_gate`,
`primitive_name`, `operator`, `approval_reason`, `timestamp`,
`source_packet_path`, `verifier_path`, `execution_plan_path`,
`precondition_summary`, `result_summary`, `outcome`, `mutation_attempted`,
`gate_specific_approval_intent`, `approved_flag_name`, `wrapper_version`,
`audit_schema_version`. The audit defaults to safe relative `tmp/` output; a
durable audit location requires a separate approved phase; it contains no raw
secrets, command forms, external URLs, operator-local paths, or vault paths; it
records the approval flag name but not a truthy assignment; and it is
validatable by the Phase 7B audit verifier.

## 11. Failure and safety behavior

Fail closed before primitive execution on any failed precondition; write a
prevented/blocked audit when safe; execute no primitive on a failed
precondition; execute at most one primitive after the approval gate passes; stop
after a primitive failure and write a failure audit; never auto-run the next
gate, retry silently, rollback automatically, infer approval, or normalize
unsafe content into safe content; keep partial completion visible; make the
rerun policy explicit.

## 12. Phase 7B verifier integration

After Phase 7D, the wrapper executes or prevents one gate and writes an audit
artifact; an operator or CI may run the Phase 7B audit verifier against it; the
verifier remains read-only, does not trigger the next gate, and does not infer
approval; the audit path must be a relative `tmp/` path compatible with the
Phase 7B input contract.

## 13. Future Phase 7D test plan

Success paths execute only the selected gate's primitive; missing/unrelated/
multiple/global flags, gate-not-in-plan, gate-blocked, Phase 6C not ready, Phase
6E failed, product/report mismatch, and finalization without compliance approved
all yield prevented / no primitive; primitive failure yields a failure audit and
no next gate; an audit artifact is produced for every outcome; the Phase 7B
verifier validates the generated audit; plus no auto next-gate, no chain
execution, no vault write outside the primitive path, no primitive execution on
a failed precondition, cross-CWD execution, unsafe env/config rejection, output
self-safety, and docs token regression.

## 14. Documentation update scope

Additive only: ROADMAP marks Phase 7C complete (plan) and Phase 7D future
high-risk; PROJECT_STATE points to the plan and states no runtime wrapper yet;
the single-gate boundary points to the plan; RELEASE_SNAPSHOT_PHASE6 gets a
future pointer only, with no Phase 6 release matrix rewrite.

## 15. No-execution and static-safety rules

The two new Phase 7C files (this task and the plan doc) must not contain approval
flag truthy assignments, bash wrapper invocation forms for Phase 2G/2H/2I, python
invocation forms for the primitive scripts, external URLs, contiguous
operator-local paths, or secret markers. Primitive file names, approval flag
names, and the proposed future wrapper command name remain allowed as names only.

## 16. Test strategy

Deterministic docs-contract tests: task + plan doc exist; task has
`phase7c_status: success`; plan is docs/tests/task-only; no Phase 7D wrapper
scripts exist; plan states no runtime wrapper exists in 7C and names Phase 7D as
the future high-risk phase; objective; proposed command shape; exactly one gate;
allowed gate names; precondition contract (6B/6C/6E, per_gate_plan/plan_ready,
blocked nuance, id/week match, ordering, compliance); allowlist mapping; approval
flag policy; audit artifact contract with all 18 Phase 7B fields and Phase 7B
validatability; failure/safety behavior; Phase 7B integration; future Phase 7D
test plan; ROADMAP/PROJECT_STATE/boundary/RELEASE_SNAPSHOT_PHASE6 pointers;
ROADMAP/PROJECT_STATE token regression; a no-execution guard and static-safety
scan over only the two new Phase 7C files.

## 17. Acceptance criteria

- Plan doc, task, and test exist; the test passes.
- Phase 7B/7A, Phase 6H->6A, and Phase 5E/3E tests still pass; full suite passes.
- No runtime wrapper added; no Phase 7D scripts created; no hardcoded operator
  path in scripts.
- No approval mutation, vault read/write, or primitive execution is introduced.

## 18. Verification commands

```
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 19. Known limitations

- Implementation plan only; no runtime wrapper, command, or approval mutation
  exists.
- No durable audit store yet.
- Phase 7D is the future high-risk runtime implementation phase, separate and
  explicitly approved.

## 20. Final status target

`phase7c_status: success`
