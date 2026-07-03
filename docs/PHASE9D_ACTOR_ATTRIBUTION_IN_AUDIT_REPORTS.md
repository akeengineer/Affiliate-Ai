# Phase 9D — Actor Attribution in Audit/Reports

phase9d_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

identity_runtime_status: not_implemented

rbac_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

phase9_branch_workflow: enabled

### Purpose

Phase 9D implements a local-only actor attribution report prototype for
audit/report evidence based on Phase 9C registry metadata. It reads an existing
Phase 9C operator registry and a local evidence/report reference file, attaches
selected actor metadata to each evidence reference, and emits an actor-attributed
report.

Phase 9D does not implement authentication, RBAC, login, sessions,
backend/API/database, key custody, production signing, or production
verification. It is a metadata-only, evidence-only local prototype.

### Scope

- local-only actor attribution report prototype
- consumes local Phase 9C operator registry
- consumes local evidence/report references
- emits actor-attributed report JSON/MD
- privacy/secret scan
- approval boundary enforcement
- deterministic local outputs
- no authentication runtime
- no RBAC runtime
- no login
- no session runtime
- no user store
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no Phase 8 runtime behavior change

### Runtime command

```text
bash scripts/dev/run_phase9d_actor_attribution_report.sh --registry <registry-json> --evidence <evidence-json> [--actor-id <actor_id>]
```

The command accepts no approval flags and no `--execute`.

### Attribution data model

- actor metadata source: an existing Phase 9C operator registry.
- evidence references: a local list of report/audit references.
- attributed records: each evidence reference joined with the selected actor.
- `actor_metadata`: the full selected actor record.
- `selected_actor_id`: the actor chosen for attribution.
- `evidence_id`: the identifier of each attributed evidence reference.
- `attribution_status`: per-record attribution marker.
- `approval_boundary_statement`: restated on every attributed record.

### Evidence reference model

Required evidence fields:

- `evidence_id`
- `evidence_type`
- `evidence_path`
- `evidence_phase`
- `evidence_purpose`

Evidence references are local metadata only.

### Actor selection model

- explicit `--actor-id` selects the matching registry actor.
- when `--actor-id` is omitted, the first actor by `actor_id` sort order is
  selected deterministically.
- actor not found: exit nonzero with `actor_attribution_status:
  failed_actor_not_found` and `attribution_report_status: not_built`.
- duplicate `actor_id`: the first deterministic record is selected, a warning
  issue is emitted, `duplicate_actor_count` increments, and
  `attribution_report_status` becomes `built_with_warnings`.

### Output layout

- `tmp/phase9d-actor-attribution/actor-attribution-report.json`
- `tmp/phase9d-actor-attribution/actor-attribution-report.md`

### Path safety

- registry and evidence paths must resolve under the repository root.
- registry and evidence paths must not be under `vault/`, `docs/`, `scripts/`,
  `codex/`, or `.git/`.
- registry and evidence paths must not be symlinks.
- paths must not use traversal or an absolute path outside the repo.
- `output-dir` must resolve to `tmp/phase9d-actor-attribution` or below it.
- the output directory is created if missing.

### Privacy and secret handling

- never write raw AFFILIATE_PHASE8L_PROTOTYPE_KEY
- never store private keys
- never store API keys
- never store OAuth/OIDC/SAML tokens
- never store database passwords
- avoid raw emails in `actor_id`
- avoid unnecessary PII
- sanitize display labels if needed

### Approval boundary

- actor attribution is not authentication
- actor attribution is not approval
- actor-attributed report is not approval
- registry presence is not authentication
- registry presence is not approval
- valid actor metadata is not approval
- actor metadata is not approval
- actor_id is not approval
- identity assurance is not approval
- identity source is not approval
- RBAC eligibility is not approval
- actor-attributed report is evidence only
- actor-attributed report must not trigger wrapper
- actor-attributed report must not execute primitives
- actor-attributed report must not trigger next gate
- actor-attributed report must not set approval flags
- approval remains Phase 7D selected-gate manual boundary

### Non-authentication boundary

- Attribution is not login.
- Attribution is not authenticated identity.
- Attribution is not session.
- Attribution is not user account.
- Future authentication requires separate phase.

### Non-RBAC boundary

- Attribution role labels are governance metadata only.
- Role label is not runtime permission.
- Attribution does not enforce permissions.
- Future RBAC requires separate phase.

### Compatibility with Phase 9C

- Phase 9D consumes Phase 9C registry output.
- Phase 9D does not modify Phase 9C runtime.
- Registry presence remains not authentication or approval.

### Compatibility with Phase 9B

- Phase 9D uses the Phase 9B conceptual actor metadata schema fields.
- Schema validity remains not approval.

### Compatibility with Phase 9A

- Phase 9D follows the Phase 9A identity boundary.
- Operator identity remains unauthenticated or operator-declared.

### Compatibility with Phase 8O/8L/8M

- Phase 9D can attribute local evidence/report references from final acceptance,
  signing, or verifier outputs.
- Phase 9D does not modify Phase 8 runtime.
- Signature verification remains not approval.
- Final acceptance remains not approval.

### Compatibility with Phase 7D

- Phase 7D remains the selected-gate manual approval runtime.
- Phase 9D does not modify Phase 7D.
- Actor attribution records must not approve.
- Actor attribution records must not execute primitives.

### Failure taxonomy

Each failure type maps to a severity, an incident classification, and a reviewer
action.

- `registry_missing` — critical; actor_attribution_not_available;
  reject_attribution_until_resolved.
- `evidence_missing` — critical; actor_attribution_not_available;
  reject_attribution_until_resolved.
- `invalid_registry_json` — critical; actor_metadata_schema_failure;
  reject_attribution_until_resolved.
- `invalid_evidence_json` — critical; evidence_reference_failure;
  reject_attribution_until_resolved.
- `invalid_registry_shape` — critical; actor_metadata_schema_failure;
  reject_attribution_until_resolved.
- `invalid_evidence_shape` — critical; evidence_reference_failure;
  reject_attribution_until_resolved.
- `registry_actor_missing` — critical; actor_attribution_not_available;
  reject_attribution_until_resolved.
- `actor_not_found` — critical; actor_attribution_not_available;
  manual_review_required.
- `duplicate_actor_id` — warning; actor_metadata_schema_failure;
  manual_review_required.
- `evidence_reference_missing_field` — critical; evidence_reference_failure;
  reject_attribution_until_resolved.
- `actor_metadata_contains_secret` — critical; privacy_review_required;
  reject_actor_metadata_until_resolved.
- `evidence_metadata_contains_secret` — critical; privacy_review_required;
  reject_attribution_until_resolved.
- `actor_metadata_contains_unnecessary_pii` — warning; privacy_review_required;
  reject_actor_metadata_until_resolved.
- `approval_boundary_statement_missing` — warning; identity_policy_review_required;
  reject_actor_metadata_until_resolved.
- `approval_flag_present` — critical; actor_metadata_schema_failure;
  reject_attribution_until_resolved.
- `primitive_execution_intent_present` — critical; actor_metadata_schema_failure;
  reject_attribution_until_resolved.
- `unsafe_path` — critical; actor_attribution_not_available;
  reject_attribution_until_resolved.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `actor_attribution_not_available`,
`actor_metadata_schema_failure`, `identity_assurance_review_required`,
`identity_policy_review_required`, `privacy_review_required`,
`actor_scope_review_required`, `evidence_reference_failure`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the attribution.
- `reject_actor_metadata_until_resolved` — the actor metadata must be rejected
  until resolved.
- `reject_attribution_until_resolved` — the attribution must be rejected until
  resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Known limitations

- local prototype only
- no authentication
- no RBAC
- no login
- no session runtime
- no user store
- no backend/API/database
- no key custody
- no strong non-repudiation
- no production deployment

### Phase 9E RBAC design

Phase 9E RBAC design now exists at `docs/PHASE9E_RBAC_DESIGN.md`. Phase 9E uses
this attribution report as future subject/evidence context for RBAC decisions.
Phase 9E does not modify this attribution runtime; RBAC design is not enforcement
and RBAC eligibility is not approval.

### Phase 9F local RBAC policy prototype

Phase 9F local RBAC policy prototype now exists at
`docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`. Phase 9F may consume this
attribution report as optional advisory context. Phase 9F does not modify this
attribution runtime; actor attribution remains not authentication or approval.
