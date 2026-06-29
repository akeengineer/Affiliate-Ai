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
