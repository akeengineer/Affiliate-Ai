# Phase 9C — Local Operator Registry Prototype

phase9c_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

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

Phase 9C implements a local-only operator registry prototype for actor metadata
records based on Phase 9A (identity boundary) and Phase 9B (actor metadata
schema). It validates a local subset of the Phase 9B conceptual `actor_metadata`
schema, can build a deterministic local registry file, and emits local registry
reports.

Phase 9C does not implement authentication, RBAC, login, sessions,
backend/API/database, key custody, production signing, or production
verification. It is a metadata-only, evidence-only local prototype.

### Scope

- local-only operator registry prototype
- actor metadata validation subset
- local registry JSON output
- local registry report output
- list/report mode over local registry
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
bash scripts/dev/run_phase9c_local_operator_registry.sh --input <local-json> --mode build
```

Modes:

- `validate` — validate records and write a validation report only; the registry
  file is not written.
- `build` — validate records, write the registry JSON, and write the registry
  report.
- `list` — read the existing registry JSON and write a list report.
- `report` — read the existing registry JSON and write a registry report.

The command accepts no approval flags and no `--execute`.

### Registry data model

Input: a local JSON file of conceptual Phase 9B `actor_metadata` records (a
single object, an object with a top-level `actor_metadata` list, or an array).

Outputs, written only under `tmp/phase9c-local-operator-registry/`:

- `operator-registry.json`
- `operator-registry-report.json`
- `operator-registry-report.md`
- `operator-registry-list.json`
- `operator-registry-list.md`

Outputs are local evidence only.

### Actor metadata validation subset

Required fields:

- `actor_schema_version`
- `actor_id`
- `actor_type`
- `actor_display_label`
- `actor_role_labels`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_session_reference`
- `actor_attestation`
- `actor_action_scope`
- `identity_evidence_references`
- `actor_timestamp_utc`
- `privacy_classification`
- `approval_boundary_statement`

Allowed `actor_schema_version`: `phase9b.actor_metadata.v1`.

Allowed `actor_type`: `human_operator`, `reviewer`, `signer`, `key_owner`,
`key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`, `system_process`, `test_fixture`,
`automation_placeholder`.

Allowed `actor_role_labels`: `operator`, `reviewer`, `signer`, `key_owner`,
`key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`, `automation`, `test`.

Allowed `actor_identity_assurance`: `unauthenticated`, `operator_declared`,
`local_machine_observed`, `local_config_verified`, `repository_config_verified`,
`external_identity_verified`, `enterprise_identity_verified`, `hardware_backed`.

Allowed `actor_identity_source`: `none`, `terminal_user_label`,
`git_user_config`, `environment_operator_label`, `local_config_operator_label`,
`repository_operator_registry`, `signed_identity_assertion`, `external_idp_claim`,
`enterprise_directory_claim`, `hardware_key_attestation`.

Allowed `actor_action_scope.action_category`: `export_pack_generation`,
`export_integrity_verification`, `local_signature_creation`,
`local_signature_verification`, `incident_review`, `final_acceptance_review`,
`selected_gate_manual_approval`, `primitive_execution`, `key_governance_review`,
`test_fixture_generation`.

`actor_id` must match `^actor_[a-z0-9_-]{3,64}$`, must not contain whitespace,
`@`, URL schemes, secret-like markers, or approval-like literals.

### Path safety

- input path must resolve under the repository root.
- input path must not be under `vault/`, `docs/`, `scripts/`, `codex/`, or
  `.git/`.
- input path must not be a symlink.
- input path must not use path traversal or an absolute path outside the repo.
- `output-dir` must resolve to `tmp/phase9c-local-operator-registry` or below it.
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

- local operator registry is not authentication
- registry presence is not authentication
- local operator registry is not approval
- registry presence is not approval
- valid actor metadata is not approval
- actor metadata is not approval
- actor attribution is not approval
- actor_id is not approval
- identity assurance is not approval
- identity source is not approval
- RBAC eligibility is not approval
- registry report is evidence only
- registry report must not trigger wrapper
- registry report must not execute primitives
- registry report must not trigger next gate
- registry report must not set approval flags
- approval remains Phase 7D selected-gate manual boundary

### Non-authentication boundary

- Registry record is not login.
- Registry record is not authenticated identity.
- Registry record is not session.
- Registry record is not user account.
- Future authentication requires separate phase.

### Non-RBAC boundary

- Registry role labels are governance metadata only.
- Role label is not runtime permission.
- Registry does not enforce permissions.
- Future RBAC requires separate phase.

### Compatibility with Phase 9B

- Phase 9C implements a local validation subset of the Phase 9B conceptual actor
  metadata schema.
- Phase 9C does not change the Phase 9B schema contract.

### Compatibility with Phase 9A

- Phase 9C follows the Phase 9A identity boundary.
- Operator identity remains unauthenticated or operator-declared.

### Compatibility with Phase 8O/8L/8M

- Phase 9C may provide future actor metadata for Phase 8 final acceptance,
  signing, or verifier attribution.
- Phase 9C does not modify Phase 8 runtime.
- Signature verification remains not approval.
- Final acceptance remains not approval.

### Compatibility with Phase 7D

- Phase 7D remains the selected-gate manual approval runtime.
- Phase 9C does not modify Phase 7D.
- Registry records must not approve.
- Registry records must not execute primitives.

### Failure taxonomy

Each failure type maps to a severity, an incident classification, and a reviewer
action.

- `input_missing` — critical; actor_metadata_not_available;
  reject_actor_metadata_until_resolved.
- `invalid_json` — critical; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `invalid_input_shape` — critical; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_schema_version_missing` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_id_missing` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_id_invalid_format` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_type_missing` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_type_unknown` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `actor_identity_assurance_missing` — warning;
  identity_assurance_review_required; reject_actor_metadata_until_resolved.
- `actor_identity_assurance_insufficient` — warning;
  identity_assurance_review_required; reject_actor_metadata_until_resolved.
- `actor_identity_source_unknown` — warning; identity_policy_review_required;
  reject_actor_metadata_until_resolved.
- `actor_role_label_unknown` — warning; identity_policy_review_required;
  reject_actor_metadata_until_resolved.
- `actor_scope_invalid` — warning; actor_scope_review_required;
  reject_actor_metadata_until_resolved.
- `actor_session_reference_invalid` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `identity_evidence_reference_invalid` — warning; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `identity_metadata_contains_secret` — critical; privacy_review_required;
  reject_actor_metadata_until_resolved.
- `identity_metadata_contains_unnecessary_pii` — warning; privacy_review_required;
  reject_actor_metadata_until_resolved.
- `approval_boundary_statement_missing` — warning; identity_policy_review_required;
  reject_actor_metadata_until_resolved.
- `approval_flag_present` — critical; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `primitive_execution_intent_present` — critical; actor_metadata_schema_failure;
  reject_actor_metadata_until_resolved.
- `duplicate_actor_id` — warning; actor_metadata_schema_failure;
  manual_review_required.
- `unsafe_path` — critical; actor_metadata_not_available;
  reject_actor_metadata_until_resolved.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `actor_metadata_not_available`,
`actor_metadata_schema_failure`, `identity_assurance_review_required`,
`identity_policy_review_required`, `privacy_review_required`,
`actor_scope_review_required`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the actor metadata.
- `reject_actor_metadata_until_resolved` — the actor metadata must be rejected
  until resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Output layout

All outputs are written under `tmp/phase9c-local-operator-registry/`:

- `operator-registry.json`
- `operator-registry-report.json`
- `operator-registry-report.md`
- `operator-registry-list.json`
- `operator-registry-list.md`

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

### Phase 9D actor attribution

Phase 9D actor attribution report prototype now exists at
`docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`. Phase 9D consumes this
registry output for local actor attribution of audit/report evidence. Phase 9D
does not modify this registry runtime; actor attribution is not authentication
and is not approval.

### Phase 9E RBAC design

Phase 9E RBAC design now exists at `docs/PHASE9E_RBAC_DESIGN.md`. Phase 9E uses
these registry records as a future RBAC subject source. Phase 9E does not modify
this registry runtime; registry presence remains not authentication or approval.

### Phase 9F local RBAC policy prototype

Phase 9F local RBAC policy prototype now exists at
`docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`. Phase 9F may consume this
registry as optional advisory subject context. Phase 9F does not modify this
registry runtime; registry presence remains not authentication or approval.
