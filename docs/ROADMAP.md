# Roadmap

## 1. Roadmap principles

- **Keep guardrails.** No database, FastAPI, UI implementation, external APIs,
  affiliate content generation, autopublish, or campaign launch is added without
  an explicit, approved phase that revisits these constraints.
- **Local-first until the UI/API boundary is explicit.** No server process is
  introduced until a phase defines and approves that boundary.
- **Read-only before write-capable workflows.** New surfaces read existing
  artifacts before they are allowed to mutate anything.
- **Manual approval before automation.** Any vault write or governance action
  stays human-gated; automation is not added ahead of an approved design.
- **No autopublish.** Publishing and campaign launch remain out of scope.

## 1b. Completed phases (Phase 4-5 UI shell line)

The static, read-only UI shell line is **complete**. The sections below capture
the original direction; the as-built phases are:

- Phase 4A — local static read-only UI mock — **complete / done**
- Phase 4B — UI snapshot pack — **complete / done**
- Phase 4C — static snapshot catalog — **complete / done**
- Phase 4D — static demo bundle verifier — **complete / done**
- Phase 4E — demo bundle operator command — **complete / done**
- Phase 5A — UI shell boundary plan — **complete / done**
- Phase 5B — local static read-only UI shell prototype — **complete / done**
- Phase 5C — UI shell verifier / acceptance gate — **complete / done**
- Phase 5D — UI shell demo bundle command — **complete / done**

All of the above remain **read-only** and **manual-approved** only; a marketplace
connector and any write-capable surface stay deferred to a future, separately
approved phase. See `docs/RELEASE_SNAPSHOT_PHASE5.md`.

## 1c. Phase 6 — manual-approved workflow boundary

- Phase 6A — manual-approved workflow boundary plan — **complete / done**
  (docs/tests/task-only). See `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md`.
- Phase 6B — dry-run approval review packet — **complete / done**.
- Phase 6C — approval review packet verifier — **complete / done**.
- Phase 6D — manual approval execution boundary plan — **complete / done**
  (boundary-only; defines the contract, executes nothing). See
  `docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md`.
- Phase 6E — dry-run approval execution planner — **complete / done**.
- Phase 6F — single-gate manual approval wrapper boundary plan — **complete /
  done** (boundary-only; defines the contract, executes nothing). See
  `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`.
- Phase 6G — manual approval audit verifier boundary plan — **complete / done**
  (boundary-only; defines the contract, executes nothing). See
  `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md`.
- Phase 6H — release snapshot update — **complete / done**
  (docs/tests/task-only). See `docs/RELEASE_SNAPSHOT_PHASE6.md`.
- A future single-gate wrapper implementation remains **separate and explicitly
  approved**.
- A future audit verifier implementation remains **separate and explicitly
  approved**.

Phase 6 stays **read-only** until a human gate is explicitly invoked; all vault
writes remain **manual-approved** behind the existing approval flags. No
approval mutation is added in Phase 6A-6H.

## 1d. Phase 7 — audit verifier and single-gate wrapper implementation

- Phase 7A — manual approval audit verifier implementation plan — **complete /
  done** (docs/tests/task-only; plans the runtime verifier, implements nothing).
  See `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md`.
- Phase 7B — read-only audit verifier implementation — **complete / done**
  (runtime read-only; `scripts/dev/verify_manual_approval_audit.py` wrapped by
  `scripts/dev/run_phase7b_audit_verifier.sh`; writes only under
  `tmp/phase7b-audit-verifier/`).
- Phase 7C — single-gate manual approval wrapper implementation plan —
  **complete / done** (docs/tests/task-only; plans the runtime wrapper,
  implements nothing). See
  `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`.
- Phase 7D-R — high-risk implementation readiness review — **complete / done**
  (docs/tests/task-only; the final review gate before Phase 7D). See
  `docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md`. Runtime readiness
  remains `blocked` until explicit user approval.
- Phase 7D-P — implementation plan finalization — **complete / done**
  (docs/tests/task-only; finalizes the implementation blueprint and implements
  nothing). See
  `docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`. Runtime readiness
  remains `blocked`.
- Phase 7E — release snapshot / runtime blocked state report —
  **complete / done** (docs/tests/task-only; records what is available now,
  what remains blocked, and the explicit approval requirement before any future
  Phase 7D runtime implementation). See `docs/RELEASE_SNAPSHOT_PHASE7.md`.
- Phase 7D — high-risk single-gate manual approval wrapper implementation —
  **complete / done** (runtime manual-gated; adds
  `scripts/dev/run_phase7d_single_gate_wrapper.sh`,
  `scripts/dev/execute_single_gate_approval.py`, and
  `tests/test_phase7d_single_gate_wrapper.py`; selected-gate-only, evidence-first,
  safe vault-read supplements, no approve-all, no chain, no next-gate
  automation). Runtime readiness is now `implemented_manual_gate`.
- Phase 7F — runtime wrapper live state report — **complete / done**
  (docs/tests/task-only; documents the live post-Phase-7D state after the
  manual-gated wrapper exists, adds no runtime behavior, and records the safe
  demo posture). See `docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md`.
- Phase 7G — Operator Acceptance / Safe Demo Pack — **complete / done**
  (safe local acceptance only; runs prevented, blocked, invalid, and static
  guard checks without primitive execution or a new mutation path). See
  `docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md`.
- Phase 7H — Operator Runbook Hardening — **complete / done**
  (docs/tests/task-only; hardens live operator procedure without changing Phase
  7D wrapper behavior, approval logic, or the mutation boundary). See
  `docs/PHASE7H_OPERATOR_RUNBOOK.md`.

Phase 7A/7B/7C/7D-R stay **read-only** and **manual-approved**: no approval
wrapper, vault read/write, primitive execution, or approval mutation is added.
The mutation-capable wrapper work is deferred to Phase 7D, a future, separately
approved phase.

Phase 7D-P is also **read-only** and **manual-approved**. The runtime wrapper
remains high-risk; mutation-capable Phase 7D work is future, blocked, and
requires separate explicit manual approval.

Phase 7E remains the historical blocked-state release snapshot. Phase 7D runtime
implementation was later approved explicitly and is now present as a
single-gate manual-approved wrapper. The implementation remains intentionally
narrow: no approve-all, no global approval, no multi-gate execution, no next-gate
automation, and no chain execution.

Phase 7F records that live post-Phase-7D state as a separate docs-only release
snapshot. It does not add new runtime commands, approval paths, or automation.

Phase 7G adds the safe operator acceptance command and deterministic summaries.
It leaves Phase 7D wrapper behavior unchanged.

Phase 7H hardens the manual operator runbook for real-world use of the live
selected-gate wrapper. It is docs/tests/task-only, adds no new mutation path,
and leaves Phase 7D wrapper behavior unchanged.

Phase 8A Durable Audit Store Design is the next recommended phase.

## 1e. Phase 8 — durable audit store

- Phase 8A — Durable Audit Store Design — **complete / done** (docs/tests-task
  only; proposes an audit record schema, a storage abstraction, backend
  options, and a migration path from tmp-local audit output; implements no
  storage). See `docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`.
- Phase 8B — Local Append-only Audit Store Prototype — **complete / done**
  (local-first runtime prototype; ingest-only; reads one existing audit
  artifact and appends a normalized, hash-chained record to a local ignored
  JSONL store; adds `scripts/dev/ingest_phase8b_audit_record.py` and
  `scripts/dev/run_phase8b_audit_ingest.sh`; no backend/API/database). See
  `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`.

Phase 8A is docs/tests-task only. It changes no Phase 7D wrapper behavior,
executes no primitive, performs no vault read/write, and adds no
backend/API/database. `durable_audit_store_status` is `design_only`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8B is ingest-only. It changes no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `local_append_only_prototype`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8C Verifier/Reporting over JSONL is the next recommended phase.

## 2. Phase 4A — local read-only UI mock

- A static or local-only view rendered over existing tmp/vault artifacts.
- **read-only**; renders dashboards/portfolio snapshots only.
- no API.
- no database.
- no vault writes.

## 3. Phase 4B — UI shell over existing CLI artifacts

- Reads the Phase 3A dashboard and Phase 3B portfolio artifacts.
- still **read-only**.
- no approval mutation yet.
- no database; no external APIs.

## 4. Phase 4C — manual approval panels

- Wraps Phase 2G / 2H / 2I **only**, each behind explicit human approval.
- Preserves `APPROVE_*` semantics exactly (no implicit approval).
- **manual-approved** actions only.
- no autopublish.

## 5. Phase 5 — marketplace connector design

- **read-only / manual-approved only**.
- no scraping that violates marketplace terms.
- no external connector implementation until the design is reviewed and approved.
- no direct campaign launch.

## 6. Future production hardening

- auth
- audit log
- CI acceptance gate
- observability
- secrets management
- backup strategy
