# Task 042 - Phase 7A Manual Approval Audit Verifier Implementation Plan

## 1. Purpose

Author the implementation plan for a future runtime read-only audit verifier
that validates one manual approval audit artifact produced by a future
single-gate manual approval wrapper. Phase 7A consumes the Phase 6G boundary
contract and is docs/tests/task-only; it implements no runtime verifier and
executes nothing.

## 2. Scope

- Author the audit verifier implementation plan and a docs-contract test.
- Additively update ROADMAP, PROJECT_STATE, and RELEASE_SNAPSHOT_PHASE6.
- Reference primitive file names, approval flag names, and future verifier
  command names as names only; never execute, modify, or include approval
  primitive command forms.

## 3. Files

- `codex/tasks/042-phase7a-audit-verifier-implementation-plan.md`
- `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md`
- `tests/test_phase7a_audit_verifier_implementation_plan.py`
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)
- `docs/RELEASE_SNAPSHOT_PHASE6.md` (additive future pointer)

No runtime scripts, verifiers, wrappers, mutation commands, or approval commands
are created or modified.

## 4. Implementation objective

The future verifier must read one audit artifact, validate schema fields,
validate gate consistency, validate primitive and flag mapping, validate
`mutation_attempted` consistency, validate referenced artifact paths, detect
unsafe content, produce verifier output under `tmp/`, and return `valid`,
`warning`, or `invalid` — never executing primitives, never mutating the vault,
and never approving, promoting, deciding, or finalizing.

## 5. Future runtime command shape

The future verifier command names are proposed future names only:
`run_phase7b_audit_verifier.sh` and `verify_manual_approval_audit`. No runtime
command exists in Phase 7A, Phase 7A must not add these files, no approval
primitive command forms are included, and the future verifier must accept
exactly one audit artifact path.

## 6. Audit input contract

Input is one JSON audit artifact at a relative `tmp/` path (no absolute, no
traversal, no vault path, no external URL, no operator-local path), read-only,
never modified by the verifier. Required audit fields: `product_id`,
`report_week`, `selected_gate`, `primitive_name`, `operator`, `approval_reason`,
`timestamp`, `source_packet_path`, `verifier_path`, `execution_plan_path`,
`precondition_summary`, `result_summary`, `outcome`, `mutation_attempted`,
`gate_specific_approval_intent`, `approved_flag_name`, `wrapper_version`,
`audit_schema_version`.

## 7. Validation rules

`selected_gate` in {promote, decision, finalization}; `primitive_name` matches
the gate (promote -> `promote_product_candidates.py`, decision ->
`create_decision.py`, finalization -> `finalize_decision.py`);
`approved_flag_name` matches the gate (`APPROVE_PROMOTE`, `APPROVE_DECISION`,
`APPROVE_FINALIZE`); only one gate; no multi-gate list, global approval,
approve-all, automatic next-gate, chain execution, hidden promotion, or
UI-direct approval; `outcome` in {success, failure, blocked, prevented};
`blocked`/`prevented` means `mutation_attempted` false; `success`/`failure` means
`mutation_attempted` explicit; `source_packet_path`/`verifier_path`/
`execution_plan_path` reference Phase 6B/6C/6E artifacts under `tmp/`; referenced
paths are relative `tmp/` paths (no absolute, no traversal, no vault); the audit
contains no approval command forms, external URLs, secret markers, or
operator-local paths.

## 8. Output contract

Output is written under `tmp/phase7b-audit-verifier/` as a JSON report and a
Markdown report. Planned JSON fields: `type`, `generated_at`,
`source_audit_path`, `source_audit_sha256`, `source_audit_bytes`, `product_id`,
`report_week`, `selected_gate`, `required_fields`, `gate_consistency`,
`path_safety`, `mutation_consistency`, `forbidden_content`,
`referenced_artifacts`, `warnings`, `failures`, `verdict`, `statement`. Verdict
is `valid`, `warning`, or `invalid`; `valid`/`warning` exit 0, `invalid` exits
non-zero.

## 9. Failure and safety behavior

The future verifier fails closed on missing input, invalid JSON, missing
required field, unsafe path, command form, and leakage; and never executes
primitives, never mutates the vault, never rewrites the audit artifact, never
triggers the wrapper, never infers approval, never normalizes unsafe content
into safe content, and always reports evidence.

## 10. Future Phase 7B test plan

valid promote/decision/finalization -> `valid`; missing required field, wrong
primitive, wrong approved flag, blocked/prevented with `mutation_attempted`
true, success with missing `mutation_attempted`, unsafe absolute path, traversal
path, vault path, external URL, secret marker, approval command form, multi-gate
evidence, global approval evidence -> `invalid`; stale referenced artifact hash
and optional metadata -> `warning`; plus cross-CWD execution, output
self-safety, no vault write, and no primitive execution guards.

## 11. Documentation update scope

Additive only: ROADMAP marks Phase 7A as the implementation plan and Phase 7B as
the future implementation; PROJECT_STATE points to the plan; RELEASE_SNAPSHOT_
PHASE6 gets a future pointer only, with no Phase 6 release matrix rewrite.

## 12. No-execution and static-safety rules

The two new Phase 7A files (this task and the plan doc) must not contain
approval flag truthy assignments, bash wrapper invocation forms for Phase
2G/2H/2I, python invocation forms for the primitive scripts, external URLs,
contiguous operator-local paths, or secret markers. Primitive file names,
approval flag names, and the future verifier command names remain allowed as
names only.

## 13. Test strategy

Deterministic docs-contract tests: task + plan doc exist; task has
`phase7a_status: success`; plan is docs/tests/task-only; no Phase 7A runtime
script; no `verify_manual_approval_audit.py` or `run_phase7b_audit_verifier.sh`;
plan states no runtime command exists in 7A; objective; proposed command shape;
exactly one audit artifact path; input contract and the 18 required fields;
validation rules; mutation consistency; path rules; output contract and verdict
policy; fail-closed behavior; safety statements; the future Phase 7B test plan;
ROADMAP/PROJECT_STATE/RELEASE_SNAPSHOT_PHASE6 pointers; ROADMAP/PROJECT_STATE
token regression; a no-execution guard and static-safety scan over only the two
new Phase 7A files.

## 14. Acceptance criteria

- Plan doc, task, and test exist; the test passes.
- Phase 6H/6G/6F/6E/6D/6C/6B/6A and Phase 5E/3E tests still pass; full suite
  passes.
- No runtime script changed; no runtime verifier or wrapper added; no hardcoded
  operator path in scripts.
- No approval mutation, vault read/write, or primitive execution is introduced.

## 15. Verification commands

```
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 16. Known limitations

- Implementation plan only; no runtime verifier, wrapper, command, or mutation
  exists.
- No audit artifact exists until a future wrapper implementation exists.
- Future Phase 7B+ are separate implementation phases under their own approval.

## 17. Final status target

`phase7a_status: success`
