# Task 039 - Phase 6F Single-gate Manual Approval Wrapper Boundary Plan

## 1. Purpose

Define the contract for a future manual approval wrapper that may execute
exactly one selected gate per invocation, after the read-only evidence chain
(Phase 6B packet + Phase 6C verifier + Phase 6E execution plan) is complete and
verified. Phase 6F defines the boundary only and implements no wrapper.

## 2. Scope

- Author the single-gate wrapper boundary contract and a docs-contract test.
- Additively note the boundary in the execution boundary doc, ROADMAP, and
  PROJECT_STATE.
- Reference primitive file names and approval flag names as names only; never
  execute, modify, or include command forms for them.

## 3. Files

- `codex/tasks/039-phase6f-single-gate-manual-approval-wrapper-boundary.md`
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`
- `tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py`
- `docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md` (additive pointer)
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)

No runtime scripts, wrappers, mutation commands, or approval commands are
created or modified.

## 4. Required preconditions

A future wrapper must require, before any gate may execute: Phase 6B packet,
Phase 6C verifier output, and Phase 6E execution plan all exist; Phase 6C verdict
is `ready`; Phase 6E verdict is `blocked` or `ready` (not `failed`);
`product_id` and `report_week` match across operator input, packet, verifier, and
plan; packet and plan both have `dry_run: true`; Phase 6C no-leakage,
sources-tmp-only, and finalization-consistency checks passed; the selected gate
exists in the Phase 6E `per_gate_plan` and is `plan_ready` unless explicitly
documented as blocked; operator identity is recorded; approval reason is provided
and is not a placeholder; gate-specific approval intent is provided.

## 5. Single-gate execution policy

A future wrapper may execute exactly one selected gate per run. Allowed gate
names: `promote`, `decision`, `finalization`. No chain execution, no approve-all
mode, no automatic next-gate execution, no direct execution from the UI shell,
no skipping the required order. Decision requires promote completion evidence;
finalization requires decision completion evidence and `compliance_status`
approved. Readiness is not authorization to mutate.

## 6. Gate-to-primitive mapping

promote -> `promote_product_candidates.py`, decision -> `create_decision.py`,
finalization -> `finalize_decision.py` (names only; no command forms; no
primitive execution and no wrapper implementation in Phase 6F).

## 7. Approval flag policy

Flag names only: `APPROVE_PROMOTE`, `APPROVE_DECISION`, `APPROVE_FINALIZE`. A
future wrapper must require only the flag matching the selected gate and must
reject unrelated flags, multiple flags, and global approval intent. No
approve-all flag; per-run and per-gate; non-persistent; no truthy assignment
example.

## 8. Audit model

Every future wrapper invocation writes one audit artifact with `product_id`,
`report_week`, `selected_gate`, `primitive_name`, `operator`, `approval_reason`,
`timestamp`, `source_packet_path`, `verifier_path`, `execution_plan_path`,
`precondition_summary`, `result_summary`, and `outcome`. Audit records success,
failure, and blocked/prevented execution, shows whether mutation was attempted,
and is written under `tmp/` first unless a future phase approves another
location.

## 9. Failure and safety model

A failed precondition means no primitive execution; a failed primitive stops and
audits; no automatic rollback; no silent retry; no overwrite unless the
primitive enforces it; partial completion remains visible; rerun policy is
explicit; non-idempotent risks are documented; prevented/failed/partial state is
never hidden.

## 10. Forbidden automation

Autopublish, campaign launch, affiliate link generation, marketplace connector,
external API submit, hidden promotion, UI-direct approval, global approve,
multi-gate execution, approve-all mode, automatic next-gate execution,
finalization without compliance approved, vault write without explicit
gate-specific approval, backend/API/database, network calls, and silent retry
after a failed gate are forbidden.

## 11. Future roadmap

Phase 6G may implement an audit verifier; Phase 6H may update the release
snapshot. Any actual wrapper implementation and any backend/API/database/
marketplace implementation must each be a separate, explicitly approved phase.

## 12. Test strategy

Deterministic docs-contract tests: task + boundary doc exist; boundary-only
scope; no Phase 6F runtime script; 6B/6C/6E preconditions, `ready`/non-`failed`
requirements, and 6E plan; single-gate-only policy with the three gate names;
rejection of global/multi-gate/approve-all/auto-next; UI-direct prohibition;
order rules; primitive references; flag policy (only matching flag, reject
unrelated/multiple); audit fields incl. mutation-attempted; failure/safety
model; forbidden automation; a no-execution guard and static safety scanning
only the two new Phase 6F files; ROADMAP/PROJECT_STATE token regression.

## 13. Acceptance criteria

- Boundary doc, task, and test exist; the test passes.
- Phase 6E/6D/6C/6B/6A and Phase 5E/3E tests still pass; full suite passes.
- No runtime script changed; no hardcoded operator path in scripts.
- No approval mutation, vault write, or primitive execution is introduced.

## 14. Verification commands

```
python -m pytest -q tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py
python -m pytest -q tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 15. Known limitations

- Boundary documentation only; no wrapper, gate execution, or mutation exists.
- Future Phase 6G+ are separate implementation phases under their own approval.

## 16. Final status target

`phase6f_status: success`
