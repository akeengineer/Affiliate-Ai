# Task 037 - Phase 6D Manual Approval Execution Boundary Plan

## 1. Purpose

Define the exact boundary for a future manual approval execution command that
may run the existing manual-approved primitives after the read-only evidence
chain (Phase 6B packet + Phase 6C verifier) is complete and verified. Phase 6D
defines the contract only and implements no command.

## 2. Scope

- Author the manual approval execution boundary contract and a docs-contract
  test.
- Additively note the boundary in the workflow boundary doc, ROADMAP, and
  PROJECT_STATE.
- Reference primitive file names as future targets only; never execute, modify,
  or include command forms for them.

## 3. Files

- `codex/tasks/037-phase6d-manual-approval-execution-boundary.md`
- `docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md`
- `tests/test_phase6d_manual_approval_execution_boundary.py`
- `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md` (additive pointer)
- `docs/ROADMAP.md` (additive)
- `docs/PROJECT_STATE.md` (additive)

No runtime scripts, wrappers, mutation commands, or approval commands are
created or modified.

## 4. Required preconditions

A future execution command must require, before any gate may execute: Phase 6B
packet exists; Phase 6C verifier output exists; Phase 6C verdict is `ready`
(`warning`/`failed` are not sufficient for mutation); `product_id` and
`report_week` match across operator input, the packet, and the verifier; the
packet has `dry_run: true`; Phase 6C no-leakage, sources-tmp-only, and
finalization-consistency checks passed; operator approval reason is provided and
is not a placeholder; operator identity is recorded; source packet path and
verifier path are recorded.

## 5. Execution sequence policy

Mandatory order promote -> decision -> finalization, mapped to the primitives
`promote_product_candidates.py`, `create_decision.py`, and
`finalize_decision.py` (names only). No gate skipping, no out-of-order
execution, no direct execution from the UI shell, no finalization unless
`compliance_status` is `approved`, each gate re-checks its preconditions, a
failed gate stops the sequence, and readiness is not authorization to mutate.

## 6. Flag policy

Flag names only: `APPROVE_PROMOTE`, `APPROVE_DECISION`, `APPROVE_FINALIZE`. No
truthy assignment example, explicit per-gate approval, no broad/global approval,
no approve-all flag, per-run and non-persistent.

## 7. Audit model

Every future approved step writes an immutable-style audit artifact with
`product_id`, `report_week`, `gate_name`, `primitive_name`, `operator`,
`approval_reason`, `timestamp`, `source_packet_path`, `verifier_path`,
`precondition_summary`, and `result_summary`. Audit is written under `tmp/`
first unless a future phase approves a vault/audit location, and records
success, failure, and partial completion.

## 8. Failure and rollback model

No automatic rollback; no overwrite unless the primitive enforces it; a failed
gate stops the sequence; partial completion is visible in audit; rerun policy is
explicit; non-idempotent and double-write risks are documented; partially
completed state is never hidden.

## 9. Forbidden automation

Autopublish, campaign launch, affiliate link generation, marketplace connector,
external API submit, hidden promotion, UI-direct approval, finalization without
compliance approved, vault write without explicit gate-specific approval,
backend/API/database, network calls, broad/global approval, skipped gate
execution, and silent retry after a failed gate are forbidden.

## 10. Future roadmap

Phase 6E may implement a dry-run execution planner; Phase 6F a single-gate
manual approval wrapper; Phase 6G an audit verifier; Phase 6H a release snapshot
update. Backend/API/database/marketplace require a separate approved phase.

## 11. Test strategy

Deterministic docs-contract tests: task + boundary doc exist; boundary-only
scope; no Phase 6D runtime script; 6B/6C preconditions and `ready` requirement;
gate names, flag names, primitive references, mandatory order, compliance gate,
UI-direct prohibition, per-gate approval, audit fields, failure/rollback model,
forbidden automation; a no-execution guard and static safety scanning only the
two new Phase 6D files; ROADMAP/PROJECT_STATE token regression.

## 12. Acceptance criteria

- Boundary doc, task, and test exist; the test passes.
- Phase 6C/6B/6A and Phase 5E/3E tests still pass; full suite passes.
- No runtime script changed; no hardcoded operator path in scripts.
- No approval mutation, vault write, or primitive execution is introduced.

## 13. Verification commands

```
python -m pytest -q tests/test_phase6d_manual_approval_execution_boundary.py
python -m pytest -q tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 14. Known limitations

- Boundary documentation only; no execution command, gate, or mutation exists.
- Future Phase 6E+ are separate implementation phases under their own approval.

## 15. Final status target

`phase6d_status: success`
