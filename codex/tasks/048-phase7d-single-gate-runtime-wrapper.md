# Task 048 - Phase 7D Runtime Single-gate Manual Approval Wrapper

## Purpose

Implement the explicitly approved high-risk Phase 7D runtime single-gate manual
approval wrapper.

## Explicit user approval phrase received

`approve Phase 7D runtime implementation`

## Scope

- Implement only the Phase 7D runtime wrapper.
- Preserve selected-gate-only execution.
- Preserve explicit manual approval semantics.
- Preserve audit-before/audit-after behavior.
- Add no backend, API, database, marketplace connector, autopublish, or
  production deployment behavior.

## Files

- `scripts/dev/run_phase7d_single_gate_wrapper.sh`
- `scripts/dev/execute_single_gate_approval.py`
- `tests/test_phase7d_single_gate_wrapper.py`
- `codex/tasks/048-phase7d-single-gate-runtime-wrapper.md`
- `.gitignore`
- `docs/PROJECT_STATE.md`
- `docs/ROADMAP.md`
- `docs/RELEASE_SNAPSHOT_PHASE7.md`
- `docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`

## Status model

- `phase7d_status: success`
- `phase7d_runtime_readiness: implemented_manual_gate`

## Runtime command

```text
bash scripts/dev/run_phase7d_single_gate_wrapper.sh <gate> <product_id> <report_week> --operator <operator> --reason <reason> --intent <intent> [--execute] [--confirm <confirmation>]
```

## Validation pipeline

1. CLI validation
2. Evidence path discovery
3. Evidence path safety validation
4. Phase 6B/6C/6E JSON loading
5. Evidence precondition validation
6. Selected-gate validation
7. Approval flag validation
8. Emergency stop validation
9. Intent audit write
10. Single primitive invocation
11. Result audit write

## Approval semantics

- Decision gate is evidence-derived, not operator-supplied.
- No approve-all.
- No global approval.
- No multi-gate execution.
- No next-gate automation.
- No chain execution.

## Emergency stop

- `AFFILIATE_PHASE7D_EMERGENCY_STOP`
- `tmp/phase7d-single-gate-wrapper/EMERGENCY_STOP`

## Audit strategy

- Intent audit before primitive execution when all preconditions pass.
- Result audit after primitive outcome is known.
- Prevented and blocked outcomes produce no-mutation result audits.
- Audit output remains under `tmp/phase7d-single-gate-wrapper/`.

## Primitive invocation policy

- Explicit allowlist only.
- No dynamic primitive command construction.
- No shell eval.
- At most one primitive per invocation.
- Wrapper itself never writes product, decision, or finalization vault artifacts.

## Phase 7B handoff

- Print the audit artifact path.
- Do not auto-run Phase 7B.
- Do not infer approval from Phase 7B output.

## Tests

- Focused Phase 7D runtime wrapper tests.
- Read-only/prevented path shell tests.
- Monkeypatched success-path tests.
- Regression coverage for prior Phase 7 artifacts after readiness-token update.

## Acceptance criteria

- Wrapper added intentionally.
- Runtime readiness changed intentionally to `implemented_manual_gate`.
- No approve-all, no chain, no next-gate.
- No primitive execution in tests except monkeypatch/controlled hook.
- Full suite passes in isolated execution.

## Known limitations

- Operator authentication is still not implemented.
- Durable audit storage is still out of scope.
- Every mutation still requires gate-specific approval and confirmation.

## Final status

`phase7d_status: success`

`phase7d_runtime_readiness: implemented_manual_gate`
