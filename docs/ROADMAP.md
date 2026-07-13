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

## 1a. Implementation Track 1 status

- Track 1A — backend/API/database runtime selection record — **complete / done**
- Track 1B — backend/API/database product slice plan — **complete / done**
- Track 1C — local backend/API skeleton — **complete / done**
- Track 1D — database/storage runtime — **complete / done**
- Track 1E — Product Core API — **complete / done**
- Track 1F — Minimal Usable UI / Operator Flow — **complete / done**
- Track 1G — End-to-End Demo Pack — **complete / done**
- Track 1H — MVP Acceptance Pack — **complete / done**

Track 1F implements the minimal usable UI/operator flow for the first usable
local product slice. See `docs/TRACK1F_MINIMAL_USABLE_UI_OPERATOR_FLOW.md`.

Track 1G implements the end-to-end demo pack for the first usable local product
slice. See `docs/TRACK1G_END_TO_END_DEMO_PACK.md`.

Track 1H creates the MVP Acceptance Pack for the first usable local product
slice, closes Implementation Track 1 — Backend/API/Database Usable Product
Slice, and accepts the slice for local/demo operation only. See
`docs/TRACK1H_MVP_ACCEPTANCE_PACK.md`.

Recommended next major track: Implementation Track 2 — Local Product
Intelligence Expansion, only after Track 1H is merged and only with explicit
future approval for any expanded runtime scope.

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

## 1f. Phase 9 — operator identity / RBAC / audit attribution

- Phase 9A — Operator Identity Boundary Design — **complete / current**
  (docs/tests design-only; opens the Phase 9 identity/RBAC stage by defining the
  operator identity boundary, the actor identity model, operator/reviewer/
  signer/actor identity interpretation, identity assurance levels, an identity
  evidence model, identity-to-action attribution, approval/signature/reviewer/
  key-role attribution boundaries, future RBAC/authentication-provider/session/
  audit-actor fields, privacy and PII minimization, non-repudiation limitations,
  and a migration path; implements no authentication, RBAC, login, session,
  backend/API/database, or key management runtime). See
  `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`.

Phase 9A is docs/tests design-only. It changes no Phase 7D wrapper behavior and
no Phase 8 runtime, executes no primitive, performs no vault read/write, and
adds no backend/API/database. `identity_boundary_status` is `design_only`,
`identity_runtime_status`, `rbac_runtime_status`, and
`authentication_runtime_status` are `not_implemented`,
`operator_identity_assurance_status` is `unauthenticated_or_operator_declared`,
`phase9_branch_workflow` is `enabled`, and `phase7d_runtime_readiness` remains
`implemented_manual_gate`. Operator identity, authenticated identity, reviewer
identity, signer identity, actor attribution, RBAC eligibility, identity
assurance, and key ownership are all **not approval**; approval remains the
Phase 7D selected-gate manual boundary.

- Phase 9B — Actor Metadata Schema Design — **complete / current**
  (docs/tests design-only; translates the Phase 9A identity boundary into a
  concrete conceptual `actor_metadata` schema contract — top-level object,
  normalized `actor_id`, `actor_type`/role/`identity_assurance`/`identity_source`
  enums, `action_scope`, session/attestation/evidence-reference models, schema
  versioning, compatibility with Phase 9A/7D/8L/8M/8N/8O, privacy/PII and secret
  handling constraints, a validation failure taxonomy, and future validation/
  registry/audit boundaries; implements no schema validator, actor registry,
  authentication, RBAC, session, backend/API/database, or key management
  runtime). See `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`.

Phase 9B is docs/tests design-only. It changes no Phase 7D wrapper behavior and
no Phase 8 runtime, executes no primitive, performs no vault read/write, and
adds no backend/API/database. `actor_metadata_schema_status` is `design_only`,
`actor_metadata_runtime_status` is `not_implemented`, `identity_runtime_status`,
`rbac_runtime_status`, and `authentication_runtime_status` remain
`not_implemented`, `phase9_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Actor metadata,
actor attribution, identity assurance, RBAC eligibility, and schema validity are
all **not approval**; approval remains the Phase 7D selected-gate manual
boundary.

- Phase 9C — Local Operator Registry Prototype — **complete / current**
  (local-only, metadata-only prototype; adds
  `scripts/dev/manage_phase9c_local_operator_registry.py` and
  `scripts/dev/run_phase9c_local_operator_registry.sh` that validate a local
  subset of the Phase 9B conceptual `actor_metadata` schema, build a
  deterministic local registry, and emit list/report evidence only under
  `tmp/phase9c-local-operator-registry/`; standard library only, no network,
  no database, no authentication, no RBAC, no login/session/user store, no
  backend/API/database, and no key management runtime). See
  `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`.

Phase 9C is a local metadata-only prototype. It changes no Phase 7D wrapper
behavior and no Phase 8 runtime, executes no primitive, performs no vault
read/write, and adds no backend/API/database. `actor_metadata_runtime_status`
is `local_registry_prototype`, `local_operator_registry_status` is
`prototype_local_only`, `identity_runtime_status`, `rbac_runtime_status`, and
`authentication_runtime_status` remain `not_implemented`, `phase9_branch_workflow`
is `enabled`, and `phase7d_runtime_readiness` remains `implemented_manual_gate`.
Local operator registry is not authentication, registry presence is not
approval, and valid actor metadata is not approval; approval remains the Phase
7D selected-gate manual boundary.

- Phase 9D — Actor Attribution in Audit/Reports — **complete / current**
  (local-only, metadata-only prototype; adds
  `scripts/dev/build_phase9d_actor_attribution_report.py` and
  `scripts/dev/run_phase9d_actor_attribution_report.sh` that consume a Phase 9C
  `operator-registry.json` and a local evidence/report reference file, attach
  selected actor metadata to each evidence reference, and emit an
  actor-attributed report only under `tmp/phase9d-actor-attribution/`; standard
  library only, no network, no database, no authentication, no RBAC, no
  login/session/user store, no backend/API/database, and no key management
  runtime). See `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`.

Phase 9D is a local metadata-only prototype. It changes no Phase 9C registry
behavior, no Phase 7D wrapper behavior, and no Phase 8 runtime, executes no
primitive, performs no vault read/write, and adds no backend/API/database.
`actor_attribution_status` is `local_report_prototype`,
`actor_metadata_runtime_status` remains `local_registry_prototype`,
`local_operator_registry_status` remains `prototype_local_only`,
`identity_runtime_status`, `rbac_runtime_status`, and
`authentication_runtime_status` remain `not_implemented`, `phase9_branch_workflow`
is `enabled`, and `phase7d_runtime_readiness` remains `implemented_manual_gate`.
Actor attribution is not authentication, actor attribution is not approval, and
the attributed report is evidence only; approval remains the Phase 7D
selected-gate manual boundary.

- Phase 9E — RBAC Design — **complete / current**
  (docs/tests design-only; designs the role-based access control boundary —
  subject/role/permission/resource/action/decision/obligation/denial/audit-event
  models, policy versioning, a policy evaluation lifecycle design, role-to-actor
  metadata mapping, governance role mapping, and conceptual permission
  boundaries for product-workflow, signature/export, and registry/attribution
  resources; implements no RBAC runtime, policy engine, permission enforcement,
  authentication, session, backend/API/database, or key management runtime). See
  `docs/PHASE9E_RBAC_DESIGN.md`.

Phase 9E is docs/tests design-only. It changes no Phase 9C/9D runtime, no Phase
7D wrapper behavior, and no Phase 8 runtime, executes no primitive, performs no
vault read/write, and adds no backend/API/database. `rbac_design_status` is
`design_only`, `rbac_runtime_status` remains `not_implemented`,
`actor_attribution_status` remains `local_report_prototype`,
`actor_metadata_runtime_status` remains `local_registry_prototype`,
`identity_runtime_status` and `authentication_runtime_status` remain
`not_implemented`, `phase9_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`. RBAC design is not
RBAC enforcement, RBAC eligibility is not approval, and an RBAC decision is not
product approval; approval remains the Phase 7D selected-gate manual boundary.

- Phase 9F — Local RBAC Policy Prototype — **complete / current**
  (local-only, advisory-only prototype; adds
  `scripts/dev/evaluate_phase9f_local_rbac_policy.py` and
  `scripts/dev/run_phase9f_local_rbac_policy.sh` that evaluate a local
  subject/resource/action request against a local RBAC policy JSON — with
  optional advisory context from a Phase 9C registry and/or a Phase 9D
  attribution report — and write a deterministic advisory decision report only
  under `tmp/phase9f-local-rbac-policy/`; standard library only, no network, no
  database, no RBAC enforcement, no authentication, no login/session/user
  store, no backend/API/database, and no key management runtime). See
  `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`.

Phase 9F is a local advisory-only prototype. It changes no Phase 9C/9D runtime,
no Phase 7D wrapper behavior, and no Phase 8 runtime, executes no primitive,
performs no vault read/write, and adds no backend/API/database.
`rbac_policy_status` is `local_advisory_prototype`, `rbac_runtime_status` is
`local_advisory_prototype`, `rbac_enforcement_status` remains `not_implemented`,
`actor_attribution_status` remains `local_report_prototype`,
`actor_metadata_runtime_status` remains `local_registry_prototype`,
`identity_runtime_status` and `authentication_runtime_status` remain
`not_implemented`, `phase9_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`. The local RBAC
policy prototype is not enforcement, an RBAC allow decision is not approval, and
RBAC eligibility is not approval; approval remains the Phase 7D selected-gate
manual boundary.

- Phase 9G — Phase 9 Acceptance Pack — **complete / current** (docs/tests
  acceptance pack only; closes Phase 9 by summarizing Phase 9A–9F, defining
  nine safe local-only demo scenarios, acceptance/full-suite-readiness/PR-
  readiness/merge-readiness checklists, and runtime-safety/identity/actor-
  metadata/registry/attribution/RBAC-advisory/approval-boundary/protected-
  runtime/artifact-safety checklists; adds no runtime scripts, no shell
  runners, and no new runtime behavior). See
  `docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md`.

Phase 9G is docs/tests only. It changes no Phase 9C/9D/9F runtime, no Phase 7D
wrapper behavior, and no Phase 8 runtime, executes no primitive, performs no
vault read/write, and adds no backend/API/database. `phase9g_status` is
`success`, `rbac_policy_status` and `rbac_runtime_status` remain
`local_advisory_prototype`, `rbac_enforcement_status`,
`identity_runtime_status`, and `authentication_runtime_status` remain
`not_implemented`, `phase9_branch_workflow` is `enabled`, and
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 9
(9A–9G) is now **complete pending full-suite verification and PR**. The Phase
9 acceptance pack, RBAC allow decisions, and RBAC advisory reports are all
**not approval**; approval remains the Phase 7D selected-gate manual boundary.

## 1g. Phase 10 — governed runtime integration readiness

- Phase 10A — Governed Runtime Integration Readiness Design — **complete / current**
  (docs/tests design-only; defines the governed integration readiness model,
  evidence source model, actor context model, advisory RBAC context model,
  signature context model, approval boundary model, future input/output
  contracts, evidence/actor/RBAC/signature binding models, compatibility and
  safety checks, reviewer action mapping, and a failure taxonomy for future
  local-first integration; implements no integration runtime, no
  authentication, no RBAC enforcement, no backend/API/database, and no key
  management runtime). See
  `docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`.

Phase 10A is docs/tests design-only. It changes no Phase 9C/9D/9F runtime, no
Phase 8 runtime, and no Phase 7D wrapper behavior, executes no primitive,
performs no vault read/write, and adds no backend/API/database.
`governed_runtime_integration_status` is `design_only`,
`integration_runtime_status`, `rbac_enforcement_status`,
`authentication_runtime_status`, `backend_api_database_status`, and
`key_management_runtime_status` are `not_implemented`,
`phase10_branch_workflow` is `enabled`, and `phase7d_runtime_readiness`
remains `implemented_manual_gate`. Governed integration readiness is not
runtime integration, integration design is not approval, and approval remains
the Phase 7D selected-gate manual boundary.

- Phase 10B — Actor Attribution Integration Plan for Audit Store — **complete**
  (docs/tests design-only; narrows Phase 10A toward future audit-store actor
  attribution by defining an audit actor context model, future audit actor field
  model, source binding models, append-only and hash-chain compatibility rules,
  future audit report/export contracts, migration and privacy rules, and an
  audit actor integration failure taxonomy; implements no audit store runtime
  change, no integration runtime, no authentication, no RBAC enforcement, and
  no backend/API/database). See
  `docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`.

Phase 10B is docs/tests design-only. It changes no Phase 8B/8C/8D/8E/8G/8M
runtime, no Phase 9C/9D/9F runtime, and no Phase 7D wrapper behavior, executes
no primitive, performs no vault read/write, and adds no backend/API/database.
`audit_actor_attribution_integration_status` is `design_only`,
`governed_runtime_integration_status` remains `design_only`,
`integration_runtime_status`, `rbac_enforcement_status`,
`authentication_runtime_status`, `backend_api_database_status`, and
`key_management_runtime_status` remain `not_implemented`, and
`phase10_branch_workflow` remains `enabled`. Actor attribution integration plan
is not runtime integration, audit actor attribution is not authentication,
audit actor attribution is not approval, and approval remains the Phase 7D
selected-gate manual boundary.

- Phase 10C — Local Evidence Bundle with Actor/RBAC Context — **complete / current**
  (local-only derived evidence bundle runtime prototype; standard library only;
  reads one local manifest, validates safe evidence/context references, hashes
  present files, treats safe missing files as warnings, rejects unsafe paths,
  secrets, approval flags, and execution intent, and emits deterministic JSON +
  Markdown only under `tmp/phase10c-local-evidence-bundle/`; preserves Phase 8,
  Phase 9, and Phase 7D source artifacts unchanged). See
  `docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md`.

Phase 10C is explicitly local-only. It changes no Phase 8B/8C/8D/8E/8G/8L/8M/8O
runtime, no Phase 9C/9D/9F runtime, and no Phase 7D wrapper behavior, executes
no primitive, performs no vault read/write, and adds no backend/API/database.
`governed_runtime_integration_status` and `integration_runtime_status` are now
`local_evidence_bundle_prototype`, `local_evidence_bundle_status` is
`prototype_local_only`, `audit_actor_attribution_integration_status` remains
`design_only`, `rbac_enforcement_status`, `authentication_runtime_status`,
`backend_api_database_status`, and `key_management_runtime_status` remain
`not_implemented`, and `phase10_branch_workflow` remains `enabled`. Local
evidence bundle is not approval, evidence bundle validity is not approval, and
approval remains the Phase 7D selected-gate manual boundary while preserving
the read-only and manual-approved guardrails established through Phase 5 and
Phase 7D.

- Phase 10D — Derived Actor-Attributed Audit Report Prototype — **complete / current**
  (local-only derived actor-attributed audit report prototype; standard library
  only; reads one local manifest, hashes present audit evidence/context files,
  extracts safe summary fields from optional actor/RBAC/evidence-bundle JSON,
  treats safe missing references as warnings, rejects unsafe paths, secrets,
  approval flags, and execution intent, and writes deterministic JSON +
  Markdown only under `tmp/phase10d-actor-attributed-audit-report/`; preserves
  Phase 8, Phase 9, Phase 10C, and Phase 7D source/runtime artifacts
  unchanged). See
  `docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md`.

Phase 10D is explicitly local-only. It changes no Phase 8B/8C/8D/8E/8G/8L/8M/8O
runtime, no Phase 9C/9D/9F runtime, no Phase 10C runtime, and no Phase 7D
wrapper behavior, executes no primitive, performs no vault read/write, and adds
no backend/API/database. `audit_actor_attribution_integration_status` is now
`derived_report_prototype`, `governed_runtime_integration_status` is now
`local_evidence_bundle_and_actor_report_prototypes`,
`integration_runtime_status` is now `local_derived_report_prototype`,
`local_evidence_bundle_status` remains `prototype_local_only`,
`actor_attributed_audit_report_status` is `prototype_local_only`,
`rbac_enforcement_status`, `authentication_runtime_status`,
`backend_api_database_status`, and `key_management_runtime_status` remain
`not_implemented`, and `phase10_branch_workflow` remains `enabled`. Derived
actor-attributed audit report is not approval, audit actor attribution is not
authentication, RBAC advisory context is not enforcement, and approval remains
the Phase 7D selected-gate manual boundary while preserving the read-only and
manual-approved guardrails established through Phase 5 and Phase 7D.

Phase 10E — Export Sidecar Design/Prototype is the next recommended phase. It
should remain local-only, preserve Phase 8 append-only source artifacts
unchanged, and continue to avoid production auth/RBAC/key/backend runtime.
Earlier wording may refer to a "Derived Actor-Attributed Export Pack
Prototype", but the canonical Phase 10E artifact is
`docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md`.

Phase 10E is now implemented as a local-only derived export sidecar prototype
documented in `docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md`. It reads one
local manifest, hashes present export/context files, treats safe missing
references as warnings, rejects unsafe paths, secrets, approval flags, and
execution intent, writes deterministic JSON/Markdown only under
`tmp/phase10e-export-sidecar/`, preserves Phase 8/9/10C/10D/7D source/runtime
artifacts unchanged, and keeps approval at the Phase 7D selected-gate manual
boundary. Export sidecar is not approval, verified export is not approval, and
signed export is not approval.

Phase 10F is now implemented as the docs/tests-only acceptance layer for Phase
10 and is documented in `docs/PHASE10F_PHASE10_ACCEPTANCE_PACK.md`. Phase 10F
closes Phase 10, adds acceptance evidence only, adds no runtime, does not
modify Phase 10C/10D/10E runtime behavior, and prepares Phase 10 for
full-suite verification, PR review, and merge. Immediate next step: Complete
Phase 10 PR readiness. Strategic next major phase: Phase 11 — Production
Boundary and Hardening Readiness.

## 1h. Phase 11 — production boundary and hardening readiness

- Phase 11A — Production Boundary and Hardening Readiness Definition —
  **complete / current**
  (docs/tests design-only; defines the production boundary, local-only
  prototype inventory, governed production candidate criteria, hardening
  requirements, CI gate model, observability model, secrets/key custody design,
  backup/recovery posture, and controlled promotion path; implements no
  production runtime, no authentication runtime, no RBAC enforcement, no
  backend/API/database, no production signing, no verifier runtime, and no key
  custody runtime). See
  `docs/PHASE11A_PRODUCTION_BOUNDARY_AND_HARDENING_READINESS.md`.

Phase 11A defines production boundary and hardening readiness. Phase 11A does
not implement production runtime. Phase 11A does not approve production
promotion. Local-only prototypes remain local-only until governed promotion is
explicitly approved. RBAC advisory context remains not enforcement. Approval
remains the Phase 7D selected-gate manual boundary. Phase 10 acceptance
remains readiness, not approval. `production_boundary_status` and
`hardening_readiness_status` are `design_only`,
`governed_production_candidate_status` is `defined_not_approved`,
`production_runtime_status` is `out_of_scope`,
`observability_runtime_status`, `secrets_key_custody_runtime_status`,
`backup_recovery_runtime_status`, `authentication_runtime_status`,
`rbac_enforcement_status`, `key_management_runtime_status`, and
`backend_api_database_status` are `not_implemented`, and
`phase11_branch_workflow` is `enabled`. Production authentication, RBAC
enforcement, key custody, backend/API/database, production signing, verifier
runtime, and production policy engine remain out of scope unless explicitly
approved.

- Phase 11B — Threat Model and Security Control Mapping —
  **complete / current**
  (docs/tests design-only; defines threat modeling scope, assets and security
  objectives, trust boundaries, threat actors, abuse cases, threat categories,
  security control objectives, a control mapping matrix, residual risks, and
  explicit approval/control requirements; implements no production runtime, no
  authentication runtime, no RBAC enforcement, no backend/API/database, no
  production signing, no verifier runtime, and no key custody runtime). See
  `docs/PHASE11B_THREAT_MODEL_SECURITY_CONTROL_MAPPING.md`.

Phase 11B defines threat model and security control mapping. Phase 11B does
not implement production runtime. Phase 11B does not approve production
promotion. Phase 11A defines production boundary and hardening readiness.
Local-only prototypes remain local-only until governed promotion is explicitly
approved. RBAC advisory context remains not enforcement. Approval remains the
Phase 7D selected-gate manual boundary. Phase 10 acceptance remains readiness,
not approval. `threat_model_status` and `security_control_mapping_status` are
`design_only`, `production_runtime_status` is `out_of_scope`,
`observability_runtime_status`, `secrets_key_custody_runtime_status`,
`backup_recovery_runtime_status`, `authentication_runtime_status`,
`rbac_enforcement_status`, `key_management_runtime_status`, and
`backend_api_database_status` are `not_implemented`, and
`phase11_branch_workflow` is `enabled`. Production authentication, RBAC
enforcement, key custody, backend/API/database, production signing, verifier
runtime, and production policy engine remain out of scope unless explicitly
approved.

- Phase 11C — CI Gate and Protected Boundary Enforcement Design —
  **complete / current**
  (docs/tests design-only; defines future CI gate categories, protected
  boundary checks, gate-to-threat mapping, gate-to-control mapping, and
  promotion-blocking criteria; implements no CI/CD runtime, no production
  runtime, no deployment manifest, and no GitHub Actions workflow). See
  `docs/PHASE11C_CI_GATE_PROTECTED_BOUNDARY_ENFORCEMENT_DESIGN.md`.

Phase 11C defines CI gate and protected boundary enforcement design. Phase 11C
does not implement CI/CD runtime. Phase 11C does not implement production
runtime. Phase 11C does not approve production promotion. Phase 11B defines
threat model and security control mapping. Phase 11A defines production
boundary and hardening readiness. Local-only prototypes remain local-only until
governed promotion is explicitly approved. RBAC advisory context remains not
enforcement. Approval remains the Phase 7D selected-gate manual boundary.
Phase 10 acceptance remains readiness, not approval.

- Phase 11D — Observability and Audit Retention Readiness —
  **complete / current**
  (docs/tests design-only; defines the future observability model, audit
  retention expectations, evidence lifecycle, incident traceability,
  operational telemetry requirements, and audit-readiness controls; implements
  no observability runtime, no audit storage runtime, no production runtime,
  no deployment manifest, and no GitHub Actions workflow). See
  `docs/PHASE11D_OBSERVABILITY_AND_AUDIT_RETENTION_READINESS.md`.

Phase 11D defines observability and audit retention readiness. Phase 11D does
not implement observability runtime. Phase 11D does not implement audit
storage runtime. Phase 11D does not implement production runtime. Phase 11D
does not approve production promotion. Phase 11C defines CI gate and protected
boundary enforcement design. Phase 11B defines threat model and security
control mapping. Phase 11A defines production boundary and hardening
readiness. Local-only prototypes remain local-only until governed promotion is
explicitly approved. RBAC advisory context remains not enforcement. Approval
remains the Phase 7D selected-gate manual boundary. Phase 10 acceptance
remains readiness, not approval.

- Phase 11E — Secrets, Signing, and Key Custody Architecture —
  **complete / current**
  (docs/tests design-only; defines the future secrets classification model,
  signing boundaries, verifier separation model, key custody requirements,
  rotation/revocation/emergency response readiness, and evidence/approval
  boundaries; implements no secrets runtime, no signing runtime, no verifier
  runtime, no key material, no production runtime, no deployment manifest, and
  no GitHub Actions workflow). See
  `docs/PHASE11E_SECRETS_SIGNING_AND_KEY_CUSTODY_ARCHITECTURE.md`.

Phase 11E defines secrets, signing, and key custody architecture readiness.
Phase 11E does not implement secrets runtime. Phase 11E does not implement
signing runtime. Phase 11E does not implement verifier runtime. Phase 11E does
not add key material. Phase 11E does not implement production runtime. Phase
11E does not approve production promotion. Phase 11D defines observability and
audit retention readiness. Phase 11C defines CI gate and protected boundary
enforcement design. Phase 11B defines threat model and security control
mapping. Phase 11A defines production boundary and hardening readiness.
Local-only prototypes remain local-only until governed promotion is explicitly
approved. RBAC advisory context remains not enforcement. Approval remains the
Phase 7D selected-gate manual boundary. Phase 10 acceptance remains readiness,
not approval.

- Phase 11F — Backup, Recovery, and Promotion Runbook —
  **complete / current**
  (docs/tests design-only; defines the future backup object classification,
  recovery object classification, RPO/RTO placeholder model, restore
  validation expectations, rollback criteria, controlled promotion runbook,
  and promotion evidence package; implements no backup runtime, no restore
  runtime, no deployment runtime, no production promotion automation, no
  production runtime, no deployment manifest, and no GitHub Actions
  workflow). See
  `docs/PHASE11F_BACKUP_RECOVERY_AND_PROMOTION_RUNBOOK.md`.

Phase 11F defines backup, recovery, and promotion runbook readiness. Phase
11F does not implement backup runtime. Phase 11F does not implement restore
runtime. Phase 11F does not implement deployment runtime. Phase 11F does not
implement production promotion automation. Phase 11F does not implement
production runtime. Phase 11F does not approve production promotion. Phase
11E defines secrets, signing, and key custody architecture readiness. Phase
11D defines observability and audit retention readiness. Phase 11C defines CI
gate and protected boundary enforcement design. Phase 11B defines threat
model and security control mapping. Phase 11A defines production boundary and
hardening readiness. Local-only prototypes remain local-only until governed
promotion is explicitly approved. RBAC advisory context remains not
enforcement. Approval remains the Phase 7D selected-gate manual boundary.
Phase 10 acceptance remains readiness, not approval.

- Phase 11G — Phase 11 Acceptance Pack —
  **complete / current**
  (docs/tests acceptance-pack only; summarizes and verifies the Phase 11A–11F
  readiness chain, confirms cross-phase non-goals and manual-boundary
  preservation, and prepares Phase 11 for PR/merge completion; implements no
  production runtime, no production promotion approval, no deployment manifest,
  and no GitHub Actions workflow). See
  `docs/PHASE11G_PHASE11_ACCEPTANCE_PACK.md`.

Phase 11G is the Phase 11 acceptance pack. Phase 11G does not implement
production runtime. Phase 11G does not approve production promotion. Phase
11A defines production boundary and hardening readiness. Phase 11B defines
threat model and security control mapping. Phase 11C defines CI gate and
protected boundary enforcement design. Phase 11D defines observability and
audit retention readiness. Phase 11E defines secrets, signing, and key
custody architecture readiness. Phase 11F defines backup, recovery, and
promotion runbook readiness. Local-only prototypes remain local-only until
governed promotion is explicitly approved. RBAC advisory context remains not
enforcement. Approval remains the Phase 7D selected-gate manual boundary.
Phase 10 acceptance remains readiness, not approval. Phase 11 acceptance
remains readiness, not approval.

- Phase 12A — Governed Production Candidate Implementation Plan —
  **planned / current**
  (docs/tests planning-only layer; translates the Phase 11 readiness chain into
  candidate runtime domains, implementation sequencing, approval gates,
  evidence requirements, rollback strategy, and promotion constraints; implements
  no production runtime, no authentication runtime, no backend/API/database, no
  deployment runtime, no production promotion automation, no deployment
  manifest, and no GitHub Actions workflow). See
  `docs/PHASE12A_GOVERNED_PRODUCTION_CANDIDATE_IMPLEMENTATION_PLAN.md`.

Phase 12A defines governed production candidate implementation planning. Phase
12A does not implement production runtime. Phase 12A does not approve
production promotion. Phase 12A does not implement authentication runtime.
Phase 12A does not implement RBAC enforcement. Phase 12A does not implement
key custody runtime. Phase 12A does not implement backend/API/database. Phase
12A does not implement production signing. Phase 12A does not implement
verifier runtime. Phase 12A does not implement production policy engine. Phase
12A does not implement deployment runtime. Phase 12A does not implement
production promotion automation. Phase 11 acceptance remains readiness, not
approval. Phase 10 acceptance remains readiness, not approval. Local-only
prototypes remain local-only until governed promotion is explicitly approved.
RBAC advisory context remains not enforcement. Approval remains the Phase 7D
selected-gate manual boundary.

- Phase 12B — Runtime Boundary Approval and Implementation Scope —
  **planned / current**
  (docs/tests runtime-boundary-approval-only layer; classifies future runtime
  domains as proposed, deferred, or out of scope; defines approval gates,
  required evidence, candidate-domain and deferred-domain matrices, and
  implementation-readiness constraints; implements no production runtime, no
  authentication runtime, no backend/API/database, no deployment runtime, no
  production promotion automation, no deployment manifest, and no GitHub
  Actions workflow). See
  `docs/PHASE12B_RUNTIME_BOUNDARY_APPROVAL_AND_IMPLEMENTATION_SCOPE.md`.

Phase 12B defines runtime boundary approval and implementation scope. Phase
12B does not implement production runtime. Phase 12B does not approve
production promotion. Phase 12B does not grant implementation approval. Phase
12B does not implement authentication runtime. Phase 12B does not implement
RBAC enforcement. Phase 12B does not implement key custody runtime. Phase 12B
does not implement backend/API/database. Phase 12B does not implement
production signing. Phase 12B does not implement verifier runtime. Phase 12B
does not implement production policy engine. Phase 12B does not implement
deployment runtime. Phase 12B does not implement production promotion
automation. Phase 12A defines governed production candidate implementation
planning. Phase 11 acceptance remains readiness, not approval. Phase 10
acceptance remains readiness, not approval. Local-only prototypes remain
local-only until governed promotion is explicitly approved. RBAC advisory
context remains not enforcement. Approval remains the Phase 7D selected-gate
manual boundary.

- Phase 12C — Implementation Approval Evidence Package —
  **planned / current**
  (docs/tests evidence-package-only layer; defines required evidence classes,
  approval request contents, reviewer and operator expectations, blocking
  conditions, traceability and attestation rules, and approval-evidence
  matrices for future runtime domains; implements no production runtime, no
  authentication runtime, no backend/API/database, no deployment runtime, no
  production promotion automation, no deployment manifest, and no GitHub
  Actions workflow). See
  `docs/PHASE12C_IMPLEMENTATION_APPROVAL_EVIDENCE_PACKAGE.md`.

Phase 12C defines implementation approval evidence package requirements. Phase
12C does not implement production runtime. Phase 12C does not approve
production promotion. Phase 12C does not grant implementation approval. Phase
12C does not implement authentication runtime. Phase 12C does not implement
RBAC enforcement. Phase 12C does not implement key custody runtime. Phase 12C
does not implement backend/API/database. Phase 12C does not implement
production signing. Phase 12C does not implement verifier runtime. Phase 12C
does not implement production policy engine. Phase 12C does not implement
deployment runtime. Phase 12C does not implement production promotion
automation. Phase 12B defines runtime boundary approval and implementation
scope. Phase 12A defines governed production candidate implementation
planning. Phase 11 acceptance remains readiness, not approval. Phase 10
acceptance remains readiness, not approval. Local-only prototypes remain
local-only until governed promotion is explicitly approved. RBAC advisory
context remains not enforcement. Approval remains the Phase 7D selected-gate
manual boundary.

- Phase 12D — Explicit Runtime Implementation Approval Gate —
  **planned / current**
  (docs/tests gate-only layer; evaluates explicit implementation approval
  readiness, required evidence, reviewer responsibilities, denied/deferred
  outcomes, fail-closed gate behavior, and implementation authorization
  records for future runtime domains; implements no production runtime, no
  authentication runtime, no backend/API/database, no deployment runtime, no
  production promotion automation, no deployment manifest, and no GitHub
  Actions workflow). See
  `docs/PHASE12D_EXPLICIT_RUNTIME_IMPLEMENTATION_APPROVAL_GATE.md`.

Phase 12D defines the explicit runtime implementation approval gate. Phase
12D does not implement production runtime. Phase 12D does not approve
production promotion. Phase 12D does not bypass the Phase 7D selected-gate
manual boundary. Phase 12D does not implement authentication runtime. Phase
12D does not implement RBAC enforcement. Phase 12D does not implement key
custody runtime. Phase 12D does not implement backend/API/database. Phase 12D
does not implement production signing. Phase 12D does not implement verifier
runtime. Phase 12D does not implement production policy engine. Phase 12D
does not implement deployment runtime. Phase 12D does not implement
production promotion automation. Phase 12C defines implementation approval
evidence package requirements. Phase 12B defines runtime boundary approval and
implementation scope. Phase 12A defines governed production candidate
implementation planning. Phase 11 acceptance remains readiness, not approval.
Phase 10 acceptance remains readiness, not approval. Local-only prototypes
remain local-only until governed promotion is explicitly approved. RBAC
advisory context remains not enforcement. Approval remains the Phase 7D
selected-gate manual boundary.

- Phase 12E — Approved Runtime Domain Implementation Preparation —
  **planned / current**
  (docs/tests preparation-only layer; prepares implementation scope
  statements, runtime boundary constraints, required controls, test strategy,
  observability, rollback expectations, audit evidence expectations, and
  operator checkpoints for a later approved runtime domain without selecting
  a target when explicit Phase 12D approval is still pending; implements no
  production runtime, no authentication runtime, no backend/API/database, no
  deployment runtime, no CI/CD runtime, no production promotion automation,
  no deployment manifest, and no GitHub Actions workflow). See
  `docs/PHASE12E_APPROVED_RUNTIME_DOMAIN_IMPLEMENTATION_PREPARATION.md`.

Phase 12E defines approved runtime domain implementation preparation. Phase
12E does not implement production runtime. Phase 12E does not approve
production promotion. Phase 12E does not bypass the Phase 7D selected-gate
manual boundary. Phase 12E does not implement authentication runtime. Phase
12E does not implement RBAC enforcement. Phase 12E does not implement key
custody runtime. Phase 12E does not implement backend/API/database. Phase 12E
does not implement production signing. Phase 12E does not implement verifier
runtime. Phase 12E does not implement production policy engine. Phase 12E
does not implement deployment runtime. Phase 12E does not implement
production promotion automation. Phase 12D defines the explicit runtime
implementation approval gate. Phase 12C defines implementation approval
evidence package requirements. Phase 12B defines runtime boundary approval
and implementation scope. Phase 12A defines governed production candidate
implementation planning. Phase 11 acceptance remains readiness, not approval.
Phase 10 acceptance remains readiness, not approval. Local-only prototypes
remain local-only until governed promotion is explicitly approved. RBAC
advisory context remains not enforcement. Approval remains the Phase 7D
selected-gate manual boundary.

- Phase 12F — Controlled Runtime Implementation Readiness Pack —
  **planned / current**
  (docs/tests readiness-only layer; verifies implementation scope, required
  controls, test strategy readiness, observability readiness, rollback
  readiness, evidence expectations, operator checkpoints, and readiness
  blockers while keeping the runtime target generic when explicit Phase 12D
  approval is still pending; implements no production runtime, no
  authentication runtime, no backend/API/database, no deployment runtime, no
  CI/CD runtime, no production promotion automation, no deployment manifest,
  and no GitHub Actions workflow). See
  `docs/PHASE12F_CONTROLLED_RUNTIME_IMPLEMENTATION_READINESS_PACK.md`.
- Phase 12G — Phase 12 Acceptance Pack — **complete / done**
  (docs/tests-only acceptance/readiness pack; verifies the full Phase 12A
  through Phase 12F chain and introduces no runtime implementation or
  approval). See `docs/PHASE12G_PHASE12_ACCEPTANCE_PACK.md`.
- Phase 13 — Explicit Implementation Approval Record and Runtime Domain
  Selection — **complete / done**
  (docs/tests-only approval-record layer; defines the explicit implementation
  approval record and runtime domain selection process, preserves the default
  fail-closed state, and introduces no runtime implementation, production
  promotion approval, backend/API/database, deployment runtime, CI/CD runtime,
  or GitHub Actions workflow). See
  `docs/PHASE13_EXPLICIT_IMPLEMENTATION_APPROVAL_RECORD_AND_RUNTIME_DOMAIN_SELECTION.md`.
- Phase 14 — Selected Runtime Domain Implementation Plan Blocked State —
  **complete / done**
  (docs/tests-only blocked planning layer; documents the blocked selected
  runtime domain implementation planning state because Phase 13 did not record
  explicit operator approval for exactly one runtime domain, does not select
  or infer a runtime domain, does not grant implementation approval, and
  introduces no runtime implementation, production promotion approval,
  backend/API/database, deployment runtime, CI/CD runtime, or GitHub Actions
  workflow). See
  `docs/PHASE14_SELECTED_RUNTIME_DOMAIN_IMPLEMENTATION_PLAN_BLOCKED.md`.
- Track 1A — Backend/API/Database Runtime Selection Record —
  **complete / done**
  (docs/tests-only runtime-domain-selection layer; explicitly selects
  backend/API/database runtime as the first runtime domain for a usable
  product slice, exits the governance-only loop, starts Implementation Track 1,
  preserves the Phase 7D selected-gate manual boundary, and introduces no
  runtime implementation, production promotion approval, production deployment
  approval, backend/API/database code, deployment runtime, or GitHub Actions
  workflow). See
  `docs/TRACK1A_BACKEND_API_DATABASE_RUNTIME_SELECTION_RECORD.md`.
- Track 1B — Backend/API/Database Product Slice Plan —
  **complete / done**
  (docs/tests-only product-slice-planning layer; defines the first usable local
  backend/API/database product slice plan, continues Implementation Track 1,
  preserves the Phase 7D selected-gate manual boundary, and introduces no
  runtime implementation, production promotion approval, production deployment
  approval, backend/API/database implementation files, deployment runtime, or
  GitHub Actions workflow). See
  `docs/TRACK1B_BACKEND_API_DATABASE_PRODUCT_SLICE_PLAN.md`.
- Track 1C — Local Backend/API Skeleton —
  **complete / current**
  (local-only backend/API skeleton layer; implements the first local runtime
  step in Implementation Track 1 with service startup, local configuration
  loading, GET /health, GET /version, and GET /runtime/status, preserves the
  Phase 7D selected-gate manual boundary, and introduces no database/storage
  runtime, CRUD runtime, insight generation, deployment runtime, or GitHub
  Actions workflow). See `docs/TRACK1C_LOCAL_BACKEND_API_SKELETON.md`.

Phase 12F defines controlled runtime implementation readiness. Phase 12F does
not implement production runtime. Phase 12F does not approve production
promotion. Phase 12F does not bypass the Phase 7D selected-gate manual
boundary. Phase 12F does not implement authentication runtime. Phase 12F
does not implement RBAC enforcement. Phase 12F does not implement key
custody runtime. Phase 12F does not implement backend/API/database. Phase 12F
does not implement production signing. Phase 12F does not implement verifier
runtime. Phase 12F does not implement production policy engine. Phase 12F
does not implement deployment runtime. Phase 12F does not implement
production promotion automation. Phase 12E defines approved runtime domain
implementation preparation. Phase 12D defines the explicit runtime
implementation approval gate. Phase 12C defines implementation approval
evidence package requirements. Phase 12B defines runtime boundary approval
and implementation scope. Phase 12A defines governed production candidate
implementation planning. Phase 11 acceptance remains readiness, not approval.
Phase 10 acceptance remains readiness, not approval. Local-only prototypes
remain local-only until governed promotion is explicitly approved. RBAC
advisory context remains not enforcement. Approval remains the Phase 7D
selected-gate manual boundary.

Phase 13 defines the explicit implementation approval record and runtime
domain selection process. Phase 13 does not implement production runtime by
default. Phase 13 does not approve production promotion. Phase 13 does not
bypass the Phase 7D selected-gate manual boundary. Phase 13 does not
auto-select a runtime domain. Phase 13 does not infer implementation approval
from Phase 12 acceptance. Phase 13 does not infer production promotion
approval from implementation approval. Phase 13 treats missing or ambiguous
approval as fail-closed.

Phase 14 documents the blocked selected runtime domain implementation planning
state. Phase 14 is blocked because Phase 13 did not record explicit operator
approval for exactly one runtime domain. Phase 14 does not select or infer a
runtime domain. Phase 14 does not auto-select a runtime domain. Phase 14 does
not grant implementation approval. Phase 14 does not implement production
runtime. Phase 14 does not approve production promotion. Phase 14 does not
bypass the Phase 7D selected-gate manual boundary. Phase 14 treats missing or
ambiguous runtime domain approval as fail-closed.

Track 1A selects backend/API/database runtime as the first runtime domain for a usable product slice.

Track 1A exits the governance-only loop and starts Implementation Track 1.

Track 1A does not implement runtime code.

Track 1A does not approve production promotion.

Track 1A does not approve production deployment.

Track 1A preserves the Phase 7D selected-gate manual boundary.

Track 1B defines the backend/API/database product slice implementation plan for the first usable local product slice.

Track 1B continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1B does not implement runtime code.

Track 1B does not add backend/API/database implementation files.

Track 1B does not approve production promotion.

Track 1B does not approve production deployment.

Track 1B preserves the Phase 7D selected-gate manual boundary.

Track 1C implements the local backend/API skeleton for the first usable local product slice.

Track 1C is the first runtime implementation step in Implementation Track 1.

Track 1C implements local service startup, local configuration loading, GET /health, GET /version, and GET /runtime/status.

Track 1C does not implement database/storage runtime.

Track 1C does not implement Product or AffiliateOffer CRUD.

Track 1C does not implement insight generation.

Track 1C does not approve production promotion.

Track 1C does not approve production deployment.

Track 1C preserves the Phase 7D selected-gate manual boundary.

Track 1D — Database/Storage Runtime — see
`docs/TRACK1D_DATABASE_STORAGE_RUNTIME.md`.

Track 1D implements the local database/storage runtime for the first usable local product slice.

Track 1D uses SQLite for local-first MVP storage.

Track 1D continues Implementation Track 1 — Backend/API/Database Usable Product Slice.

Track 1D is an explicit local product-slice runtime exception to the earlier Phase 1 Obsidian-only/no-database constraint.

The Track 1D exception is limited to SQLite local-first MVP storage for Implementation Track 1.

The Track 1D exception does not approve production database runtime.

The Track 1D exception does not approve production promotion.

The Track 1D exception does not approve production deployment.

Track 1D does not implement Product or AffiliateOffer full CRUD API.

Track 1D does not implement insight generation.

Track 1D does not implement recommendation runtime.

Track 1D preserves the Phase 7D selected-gate manual boundary.

Track 1E — Product Core API — see `docs/TRACK1E_PRODUCT_CORE_API.md`.

Track 1E implements the Product Core API for the first usable local product slice.

Track 1E evolves the Track 1D SQLite local-first schema only within the local product-slice runtime boundary.

Track 1E schema evolution does not approve production database runtime.

Track 1E schema evolution does not approve PostgreSQL or Aurora runtime.

Track 1E schema evolution remains limited to SQLite local-first MVP storage.

Track 1E continues to use the Track 1D repository/data access boundary.

Track 1E does not implement insight generation.

Track 1E does not implement recommendation runtime.

Track 1E does not approve production promotion.

Track 1E does not approve production deployment.

Track 1E preserves the Phase 7D selected-gate manual boundary.

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
- production boundary review

## 7. Phase 11C — CI Gate and Protected Boundary Enforcement Design

- docs/tests-only CI gate model and protected boundary enforcement design.
- defines future CI gate categories, protected boundary checks, gate-to-threat
  mapping, gate-to-control mapping, and promotion-blocking criteria.
- Phase 11C defines CI gate and protected boundary enforcement design.
- Phase 11C does not implement CI/CD runtime.
- Phase 11C does not implement production runtime.
- Phase 11C does not approve production promotion.
- Approval remains the Phase 7D selected-gate manual boundary.
- Recommended next major subphase = Phase 11E Secrets, Signing, and Key Custody Architecture.
