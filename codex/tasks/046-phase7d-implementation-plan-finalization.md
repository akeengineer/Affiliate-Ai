# Task 046 - Phase 7D Implementation Plan Finalization

## 1. Purpose

Finalize the concrete implementation blueprint for a future Phase 7D runtime
single-gate manual approval wrapper. Phase 7D-P is docs/tests/task-only and does
not implement, enable, or authorize the wrapper.

## 2. Scope

- Finalize the future implementation blueprint.
- Add deterministic docs-contract tests.
- Update existing project documents additively.
- Add no runtime wrapper, runtime command, approval mutation, primitive
  execution, vault read/write, backend, API, database, or network behavior.

## 3. Files

- `codex/tasks/046-phase7d-implementation-plan-finalization.md`
- `docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`
- `tests/test_phase7d_implementation_plan_finalization.py`
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)
- `docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md` (additive)
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md` (additive)
- `docs/RELEASE_SNAPSHOT_PHASE6.md` (additive)

## 4. Status model

Task completion and runtime authorization are independent:

- `phase7d_plan_finalization_status: success` means the blueprint and its
  docs-contract protections are complete.
- `phase7d_runtime_readiness: blocked` means no runtime implementation is
  authorized.

## 5. Implementation blueprint objective

Translate the Phase 7D-R high-risk readiness review into an implementation-ready
future design with explicit files, interfaces, validation order, invocation
containment, audit ordering, Phase 7B handoff, tests, failure behavior, and
merge gates. This task finalizes the plan only.

## 6. Future file/function plan

The proposed future runtime files are a strict shell entrypoint, a Python core,
and isolated runtime tests. The shell entrypoint will validate its interface and
delegate to Python. The Python core will expose focused parsing, evidence
validation, approval validation, audit writing, allowlisted primitive
selection, and orchestration functions. Phase 7D-P creates none of those future
files.

## 7. Future wrapper CLI contract

The proposed-only interface accepts one gate, one product identifier, one report
week, operator identity, approval reason, and gate-specific intent. It rejects
missing, placeholder, repeated, unrelated, global, multi-gate, approve-all, and
chain intent. The future command is not added by this task.

## 8. Future Python core design

The core will parse typed inputs, validate safe evidence paths and identity
consistency, load the Phase 6B/6C/6E artifacts, enforce selected-gate readiness
and ordering, enforce exactly one matching approval flag, honor emergency stop
and dry-run policy, write audits in the required order, and select at most one
primitive through an explicit allowlist. It will never dynamically resolve a
primitive from untrusted input or run a next gate.

## 9. Future validation pipeline

Validation is ordered: CLI inputs; evidence discovery and path safety;
product/report consistency; Phase 6B packet; Phase 6C verifier; Phase 6E plan;
selected-gate readiness and ordering; approval flag; emergency stop, dry-run,
and confirmation; intent audit; one primitive; result audit; Phase 7B handoff.
No mutation or vault write occurs until every pre-execution validation passes.

## 10. Future primitive invocation strategy

The explicit mapping is promote to `promote_product_candidates.py`, decision to
`create_decision.py`, and finalization to `finalize_decision.py`. These are file
name references, not command forms. No dynamic import, shell evaluation,
arbitrary subprocess target, or untrusted command construction is permitted.
Primitive failure stops execution, and no chain or next gate is allowed.

## 11. Future audit write-order strategy

Write an intent/pre-execution audit before mutation when safe, then a
result/post-execution audit after the primitive result is known. Success requires
both post-mutation state and the result audit. If mutation succeeds but the
result audit fails, expose partial completion and require manual review. Audits
cover success, failure, blocked, and prevented outcomes under relative `tmp/`.

## 12. Future Phase 7B verifier handoff

The future wrapper prints the audit path. The read-only Phase 7B verifier may be
run separately by an operator or CI. It is not an approval source, mutation
trigger, next-gate trigger, or default wrapper sub-step.

## 13. Future test fixture strategy

Use isolated temporary Phase 6B, Phase 6C, Phase 6E, audit, and vault fixtures.
Failure fixtures must never call real mutation primitives. Controlled success
tests must make primitive selection observable and prove exactly one target was
selected while all others were untouched. Shared artifact tests run
sequentially.

## 14. Future no-mutation test strategy

Snapshot the fixture vault before and after every failed-precondition,
prevented, blocked, emergency-stop, and dry-run case. Assert no primitive call,
no input rewrite, no vault change, and output only under the test `tmp/` root.

## 15. Future failure-mode strategy

Fail closed for malformed inputs, unsafe paths, mismatched evidence, unready
plans, invalid approval state, ordering failures, and active emergency stop.
Primitive failure writes a failure audit and stops. Audit failure after
successful mutation exposes partial completion. No silent retry, automatic
rollback, compensating primitive, next gate, or chain execution is allowed.

## 16. Future emergency stop and dry-run strategy

Default to dry-run or prevented mode. Execution will require the matching
gate-specific approval flag plus operator confirmation. Emergency stop
overrides approval. Dry-run reports what would execute without executing.
Runtime readiness stays blocked until this strategy is separately accepted.

## 17. Security/static-safety rules

The two new Phase 7D-P documents contain no approval flag truthy assignments,
approval primitive command forms, Phase 2G/2H/2I wrapper invocation forms,
external URL schemes, contiguous operator-local repository paths, private-key
material, credential variable markers, or raw secrets. Runtime files and
dependency files are forbidden in this phase. Primitive and approval flag names
are references only.

## 18. Documentation update scope

Update ROADMAP, PROJECT_STATE, the Phase 7D-R review, the Phase 7C plan, and the
Phase 6 release snapshot additively. Preserve historical contracts and release
matrices. Each pointer states that Phase 7D-P finalizes the blueprint while
runtime readiness remains blocked and no wrapper or mutation exists.

## 19. Acceptance criteria

- Task, blueprint, and deterministic contract tests exist.
- Both status tokens express plan success and blocked runtime readiness.
- All blueprint sections and future safety rules are explicit.
- Existing Phase 7D-R through Phase 3E regressions pass.
- The full suite passes.
- No runtime wrapper file, runtime behavior change, approval mutation, primitive
  execution, or vault read/write is introduced.
- Only the expected docs/test/task files change.

## 20. Verification commands

Run sequentially from the repository virtual environment:

```text
python -m pytest -q tests/test_phase7d_implementation_plan_finalization.py
python -m pytest -q tests/test_phase7d_r_high_risk_readiness_review.py
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git status --short --branch
```

Do not run test groups concurrently because shared `tmp/` artifacts can race.

## 21. Known limitations

- No runtime wrapper, approval command, or approval mutation exists.
- No durable audit store or authenticated operator identity exists.
- No backend, API, database, marketplace connector, autopublish, campaign
  launch, or production deployment exists.
- Phase 7D runtime implementation remains future high-risk work.

## 22. Final status target

`phase7d_plan_finalization_status: success`

`phase7d_runtime_readiness: blocked`
