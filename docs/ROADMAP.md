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
