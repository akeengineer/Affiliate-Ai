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
- Phase 8C — Audit Store Verifier / Reporting over JSONL — **complete / done**
  (read-only verifier/reporting over the Phase 8B JSONL store; recomputes
  hashes, validates hash-chain continuity, detects duplicates and malformed
  lines, and reports by product/week/gate/operator/outcome/review status;
  adds `scripts/dev/verify_phase8c_audit_store.py` and
  `scripts/dev/run_phase8c_audit_report.sh`; no backend/API/database). See
  `docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`.
- Phase 8D — Audit Store Query CLI over JSONL — **complete / done** (read-only
  query CLI over the Phase 8B JSONL store; filters by product/week/gate/
  operator/outcome/review-status/incident/hash-status, sorts, and limits
  results; adds `scripts/dev/query_phase8d_audit_store.py` and
  `scripts/dev/run_phase8d_audit_query.sh`; no backend/API/database). See
  `docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`.
- Phase 8E — Audit Export Pack — **complete / done** (read-only export pack
  bundling/summarizing Phase 8B/8C/8D local evidence into a reviewable
  manifest and Markdown summary, with optional byte-identical evidence
  copies; adds `scripts/dev/build_phase8e_audit_export_pack.py` and
  `scripts/dev/run_phase8e_audit_export.sh`; no backend/API/database). See
  `docs/PHASE8E_AUDIT_EXPORT_PACK.md`.
- Phase 8F — Export Integrity / Signing Design — **complete / done**
  (docs/tests design-only; proposes a manifest hash model, an evidence file
  hash model, a bundle hash model, a detached signature model, a signing
  key ownership policy, key storage options, a verification ceremony, and a
  tamper-evidence model; implements no signing, no verifier, and no key
  management). See `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`.
- Phase 8G — Export Integrity Verifier Prototype — **complete / done** (local
  hash-only verifier over Phase 8E export manifests; recomputes evidence
  sha256/size, copied-evidence hashes, a canonical bundle hash, and a
  best-effort manifest hash; adds
  `scripts/dev/verify_phase8g_export_integrity.py` and
  `scripts/dev/run_phase8g_export_integrity.sh`; no signing, no keys, no
  backend/API/database). See `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`.
- Phase 8H — Export Integrity Verifier Hardening — **complete / done**
  (hardens the Phase 8G verifier in place with a stable report schema
  version, an issue taxonomy, a severity model, tamper-evidence incident
  classification, a reviewer action mapping, a Phase 8E manifest
  compatibility matrix, and a deterministic output contract; no new shell
  runner, no signing, no keys). See
  `docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`.
- Phase 8I — Detached Signature Design Finalization — **complete / done**
  (docs/tests design-only; finalizes a signed payload descriptor, a
  detached signature envelope schema, signer/key metadata models, a
  signature algorithm policy, a signing policy version model, key
  lifecycle/rotation/revocation policy, a verification ceremony, a
  signature failure taxonomy, and a signing event audit trail model;
  implements no signing, no verification, and no key management). See
  `docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`.
- Phase 8J — Detached Signature Verifier Design — **complete / done**
  (docs/tests design-only; designs the verifier-side envelope/descriptor/
  hash/key/revocation/rotation/status/failure-taxonomy/reviewer-action/
  report-schema interpretation for a future detached signature verifier;
  implements no verifier runtime). See
  `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`.
- Phase 8K — Key Management Design — **complete / done** (docs/tests
  design-only; designs key governance roles, a key metadata model, key
  custody options considered, key lifecycle/rotation/revocation/
  retirement/compromise policy, a key access control model, a key audit
  trail model, a signer-to-key binding model, a key policy version model,
  and a failure taxonomy mapping; implements no key management runtime,
  no key generation, and no signing). See
  `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`.
- Phase 8L — Local Detached Signature Prototype — **complete / done**
  (local-only prototype; produces a signed payload descriptor, a detached
  signature envelope, an HMAC-SHA256 prototype signature, and a Markdown
  summary under tmp/phase8l-detached-signature/; env-var prototype key
  only, no committed keys, no key generation, no KMS/Secrets Manager, no
  signature verifier runtime, and no wrapper/primitive/vault changes). See
  `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`.
- Phase 8M — Detached Signature Verifier Prototype — **complete / done**
  (local-only verifier prototype over Phase 8L outputs; recomputes signed
  payload hash, verifies HMAC-SHA256 prototype signature when the env-var
  prototype key is provided, validates descriptor/envelope schema, writes
  a deterministic verification report under
  tmp/phase8m-detached-signature-verifier/; no signing, no key generation,
  no KMS/Secrets Manager, no key management runtime, no
  wrapper/primitive/vault changes). See
  `docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`.
- Phase 8N — Signature Runbook / Incident Review Pack — **complete / done**
  (docs/tests/runbook-pack only; checkpoint-only within `feature/phase8-signature-governance-completion`; adds the operator safe-demo
  procedure, reviewer incident review procedure, evidence preservation
  checklist, escalation matrix, and incident-to-action matrix for the existing
  Phase 8L/8M local prototypes; no signing/verifier/key-management runtime,
  no wrapper/primitive/vault changes). See
  `docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`.
- Phase 8O — Phase 8 Final Acceptance Pack — **complete / done**
  (docs/tests-only final acceptance checkpoint; closes
  `feature/phase8-signature-governance-completion` locally by defining the
  final scenario matrix, final acceptance report shape, major Phase 8 PR
  readiness checklist, and full-suite requirement; no new signing model, no
  new verifier model, no key-management runtime, and no
  wrapper/primitive/vault changes). See
  `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`.

Phase 8O Phase 8 Final Acceptance Pack is the final local checkpoint for
the major Phase 8 branch.

Phase 8A is docs/tests-task only. It changes no Phase 7D wrapper behavior,
executes no primitive, performs no vault read/write, and adds no
backend/API/database. `durable_audit_store_status` is `design_only`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8B is ingest-only. It changes no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `local_append_only_prototype`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8C is read-only against the JSONL store. It changes no Phase 7D wrapper
behavior, changes no Phase 8B ingest behavior, executes no primitive, performs
no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `jsonl_verifier_reporting`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8D is read-only against the JSONL store. It changes no Phase 7D wrapper
behavior, changes no Phase 8B ingest behavior, changes no Phase 8C verifier
behavior, executes no primitive, performs no vault read/write, and adds no
backend/API/database. `durable_audit_store_status` is now `jsonl_query_cli`,
and `phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8E is read-only against all source evidence. It changes no Phase 7D
wrapper behavior, changes no Phase 8B ingest behavior, changes no Phase 8C
verifier behavior, changes no Phase 8D query behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `export_pack`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8F is docs/tests design-only. It implements no signing, no key
generation, no private key handling, and no encryption; it changes no Phase
8E export behavior and no Phase 7D wrapper behavior, executes no primitive,
performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `export_integrity_signing_design`,
`signing_implementation_status` is `design_only`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8G is a local hash-only verifier. It implements no signing, no key
generation, no private key handling, and no encryption; it changes no Phase
8E export behavior and no Phase 7D wrapper behavior, executes no primitive,
performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `export_integrity_verifier`,
`signing_implementation_status` remains `not_implemented`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8H hardens the Phase 8G verifier in place. It implements no signing,
no key generation, no private key handling, and no encryption; it changes
no Phase 8E export behavior and no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `export_integrity_verifier_hardened`,
`signing_implementation_status` remains `not_implemented`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8I is docs/tests design-only. It implements no signing, no signature
verification, no key generation, no private key handling, and no
encryption; it changes no Phase 8G/8H verifier runtime behavior, no Phase
8E export behavior, and no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `detached_signature_design_finalized`,
`signing_implementation_status` remains `design_only`,
`signature_runtime_status` is `not_implemented`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8J is docs/tests design-only. It implements no signature verifier,
no signing, no key generation, no private key handling, and no
encryption; it changes no Phase 8G/8H verifier runtime behavior, no Phase
8E export behavior, and no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `detached_signature_verifier_design`,
`signature_verifier_runtime_status` is `not_implemented`,
`major_phase_branch_workflow` is `enabled`, and `phase7d_runtime_readiness`
remains `implemented_manual_gate`.

Phase 8K is docs/tests design-only. It implements no key management
runtime, no key generation, no signing, no signature verification, and no
encryption; it changes no Phase 8G/8H verifier runtime behavior, no Phase
8E export behavior, and no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `key_management_design`,
`key_management_runtime_status` is `not_implemented`,
`major_phase_branch_workflow` is `enabled`, and `phase7d_runtime_readiness`
remains `implemented_manual_gate`.

Phase 8L adds a local-only detached signature prototype. It commits no
private/public/certificate keys, generates no keys, implements no
KMS/Secrets Manager/backend/API/database, implements no signature
verifier runtime, changes no Phase 8G/8H verifier runtime behavior, no
Phase 8E export behavior, and no Phase 7D wrapper behavior, executes no
primitive, performs no vault read/write, and writes only under
tmp/phase8l-detached-signature. `durable_audit_store_status` is now
`local_detached_signature_prototype`, `signing_implementation_status` is
`prototype_local_only`, `signature_runtime_status` is `local_prototype`,
`signature_verifier_runtime_status` and `key_management_runtime_status`
remain `not_implemented`, `major_phase_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

Phase 8M adds a local-only detached signature verifier prototype over
Phase 8L outputs. It signs nothing, commits no keys, generates no keys,
implements no KMS/Secrets Manager/backend/API/database, implements no
key management runtime, changes no Phase 8L signing runtime behavior, no
Phase 8G/8H verifier runtime behavior, no Phase 8E export behavior, and
no Phase 7D wrapper behavior, executes no primitive, performs no vault
read/write, and writes only under tmp/phase8m-detached-signature-verifier.
`durable_audit_store_status` is now `detached_signature_verifier_prototype`,
`signature_verifier_runtime_status` is now `local_prototype`,
`signing_implementation_status` remains `prototype_local_only`,
`signature_runtime_status` remains `local_prototype`,
`key_management_runtime_status` remains `not_implemented`,
`major_phase_branch_workflow` is `enabled`, and `phase7d_runtime_readiness`
remains `implemented_manual_gate`.

Phase 8N adds the signature runbook / incident review pack for the
existing Phase 8L and Phase 8M local prototypes. It is docs/tests/
runbook-pack only, is checkpoint-only within
`feature/phase8-signature-governance-completion`, adds no signing,
verifier, or key-management runtime, changes no Phase 8L/8M/8G/8H/8E/7D
runtime behavior, executes no primitive, performs no vault read/write,
and adds no backend/API/database. `durable_audit_store_status` is now
`signature_runbook_incident_review_pack`,
`signing_implementation_status` remains `prototype_local_only`,
`signature_runtime_status` remains `local_prototype`,
`signature_verifier_runtime_status` remains `local_prototype`,
`key_management_runtime_status` remains `not_implemented`,
`runbook_runtime_status` is `docs_only`, `major_phase_branch_workflow` is
`enabled`, and `phase7d_runtime_readiness` remains
`implemented_manual_gate`.

Phase 8O closes `feature/phase8-signature-governance-completion` locally
as the final Phase 8 acceptance checkpoint. It is docs/tests-only, adds
no runtime code, changes no Phase 8L/8M/8G/8H/8E/7D behavior, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`durable_audit_store_status` is now `phase8_final_acceptance_pack`,
`signing_implementation_status` remains `prototype_local_only`,
`signature_runtime_status` remains `local_prototype`,
`signature_verifier_runtime_status` remains `local_prototype`,
`key_management_runtime_status` remains `not_implemented`,
`runbook_runtime_status` remains `docs_only`,
`phase8_major_branch_status` is `ready_for_pr_after_full_suite`,
`major_phase_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

open one major Phase 8 PR after full suite passes.

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
