# Phase 10B — Actor Attribution Audit Store Integration Plan

phase10b_status: success

phase10a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

audit_actor_attribution_integration_status: design_only

governed_runtime_integration_status: design_only

integration_runtime_status: not_implemented

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

rbac_policy_status: local_advisory_prototype

rbac_runtime_status: local_advisory_prototype

rbac_enforcement_status: not_implemented

identity_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

backend_api_database_status: not_implemented

phase10_branch_workflow: enabled

### Purpose

Phase 10B designs actor attribution integration for audit store artifacts after
Phase 10A. It defines how future local-only phases may integrate actor
attribution context from Phase 9 into Phase 8 audit records, verifier outputs,
query outputs, export packs, integrity reports, signature evidence, and final
acceptance evidence.

Phase 10B does not implement audit store runtime changes, integration runtime,
authentication, RBAC enforcement, backend/API/database, key custody,
production signing, or production verification.

### Scope

- docs/tests design-only
- audit store actor attribution concept model
- existing Phase 8 audit artifact model
- existing Phase 9 actor/RBAC context model
- future audit actor field model
- actor attribution source binding model
- RBAC advisory source binding model
- signature/evidence source binding model
- append-only compatibility model
- hash-chain compatibility model
- query/report compatibility model
- export pack compatibility model
- final acceptance compatibility model
- future integration package compatibility
- future audit record input contract
- future audit report output contract
- future audit export output contract
- migration and backward compatibility plan
- privacy and PII minimization model
- secret handling model
- approval boundary preservation model
- runtime safety model
- no runtime scripts
- no shell runner
- no audit store runtime changes
- no audit query runtime changes
- no audit export runtime changes
- no integration runtime
- no authentication runtime
- no RBAC enforcement
- no production policy engine
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path

### Current trust boundary after Phase 10A

- Phase 10A defines governed integration readiness only.
- Phase 10B defines actor attribution integration planning only.
- Phase 8 audit store/export/signature artifacts remain unchanged.
- Phase 9 actor/RBAC prototypes remain unchanged.
- No audit actor attribution runtime exists.
- No integration runtime exists.
- No authentication runtime exists.
- No RBAC enforcement exists.
- No backend/API/database exists.
- Approval remains Phase 7D selected-gate manual boundary.

### Audit store actor attribution concept model

Concepts:

- `audit_actor_context`
- `audit_actor_binding`
- `audit_actor_source`
- `actor_attribution_reference`
- `rbac_advisory_reference`
- `signature_evidence_reference`
- `approval_boundary_reference`
- `backward_compatible_audit_record`
- `actor_attributed_audit_report`
- `actor_attributed_audit_export`

State:

- concept model is design-only
- no audit actor fields are emitted in Phase 10B
- audit actor attribution is not authentication
- audit actor attribution is not approval

### Existing Phase 8 audit artifact model

Existing artifacts:

- `phase8b_audit_record_jsonl`
Current purpose: append-only durable audit evidence line store.
Current mutation boundary: append-only under `tmp/`.
Current integrity boundary: hash-chained record integrity.
Future actor attribution touchpoint: optional actor sidecar or derived actor summary.
Approval boundary: stored audit evidence is not approval.

- `phase8c_audit_store_verification_report`
Current purpose: read-only verification and reporting over the JSONL store.
Current mutation boundary: derived report only.
Current integrity boundary: recomputed hash-chain verification.
Future actor attribution touchpoint: optional actor-attributed derived report section.
Approval boundary: verification status is not approval.

- `phase8d_audit_query_result`
Current purpose: read-only filtered query result over store records.
Current mutation boundary: derived query output only.
Current integrity boundary: depends on source audit record integrity.
Future actor attribution touchpoint: actor filter and actor summary fields.
Approval boundary: query output is not approval.

- `phase8e_audit_export_manifest`
Current purpose: reviewable manifest for exported audit evidence.
Current mutation boundary: export artifact only.
Current integrity boundary: source hash references and manifest hash model.
Future actor attribution touchpoint: actor attribution sidecar reference.
Approval boundary: export manifest is not approval.

- `phase8e_audit_export_summary`
Current purpose: Markdown export summary for reviewers.
Current mutation boundary: export summary only.
Current integrity boundary: sourced from manifest and read-only evidence.
Future actor attribution touchpoint: actor summary appendix or sidecar note.
Approval boundary: export summary is not approval.

- `phase8g_export_integrity_report`
Current purpose: hash-only export integrity evidence.
Current mutation boundary: derived integrity report only.
Current integrity boundary: manifest and evidence hash validation.
Future actor attribution touchpoint: actor sidecar hash verification reference.
Approval boundary: integrity passed is not approval.

- `phase8m_signature_verifier_report`
Current purpose: local prototype signature verification evidence.
Current mutation boundary: derived verifier report only.
Current integrity boundary: signature envelope and signed payload hash validation.
Future actor attribution touchpoint: reference to actor-attributed export sidecar evidence.
Approval boundary: signature verification remains not approval.

- `phase8o_final_acceptance_pack`
Current purpose: final acceptance evidence package for Phase 8.
Current mutation boundary: docs/tests final acceptance evidence only.
Current integrity boundary: references prior export, integrity, signature, and runbook evidence.
Future actor attribution touchpoint: reference to actor-attributed audit report evidence.
Approval boundary: final acceptance remains not approval.

### Existing Phase 9 actor/RBAC context model

Existing context artifacts:

- `phase9c_operator_registry`
Current purpose: local registry of conceptual actor metadata.
Current trust boundary: prototype local only.
Future audit integration role: source registry reference for actor bindings.
Approval boundary: registry presence is not approval.

- `phase9d_actor_attribution_report`
Current purpose: local actor attribution evidence over existing artifacts.
Current trust boundary: evidence-only attribution report.
Future audit integration role: source actor attribution reference for audit context binding.
Approval boundary: actor attribution is not approval.

- `phase9f_rbac_advisory_report`
Current purpose: local advisory RBAC evidence.
Current trust boundary: advisory-only policy result.
Future audit integration role: advisory decision sidecar or reference for audit evidence.
Approval boundary: RBAC advisory decision is not approval.

- `phase9g_acceptance_pack`
Current purpose: acceptance boundary and safe-demo reference for Phase 9.
Current trust boundary: docs/tests acceptance only.
Future audit integration role: compatibility boundary reference.
Approval boundary: acceptance pack is not approval.

### Future audit actor field model

Future optional fields:

- `audit_actor_schema_version`
- `audit_actor_id`
- `audit_actor_type`
- `audit_actor_identity_assurance`
- `audit_actor_identity_source`
- `audit_actor_role_labels`
- `audit_actor_registry_reference`
- `audit_actor_attribution_reference`
- `audit_rbac_advisory_reference`
- `audit_signature_evidence_reference`
- `audit_approval_boundary_reference`
- `audit_actor_privacy_classification`
- `audit_actor_added_at_phase`
- `audit_actor_boundary_statement`

Rules:

- fields are optional for backward compatibility
- fields are attribution-only
- fields must not affect hash-chain validation unless a future phase explicitly defines versioned hash inclusion
- fields must not imply authentication
- fields must not imply approval

### Actor attribution source binding model

Binding fields:

- `actor_source_type`
- `actor_source_path`
- `actor_source_hash_reference`
- `actor_id`
- `actor_type`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_role_labels`
- `actor_binding_status`
- `actor_boundary_statement`

State:

- actor source binding is not authentication
- actor source binding is not approval

### RBAC advisory source binding model

Binding fields:

- `rbac_source_type`
- `rbac_source_path`
- `rbac_source_hash_reference`
- `advisory_decision`
- `decision_reason`
- `obligations`
- `denial_reasons`
- `rbac_policy_status`
- `rbac_enforcement_status`
- `rbac_boundary_statement`

State:

- RBAC advisory source binding is not enforcement
- allow is not approval
- deny is not incident by itself

### Signature/evidence source binding model

Binding fields:

- `signature_source_type`
- `signature_source_path`
- `signature_source_hash_reference`
- `signature_verification_status`
- `signed_payload_hash_status`
- `export_integrity_status`
- `key_management_runtime_status`
- `signature_boundary_statement`

State:

- verified signature is not approval
- export integrity passed is not approval
- local signature/verifier remains prototype only

### Append-only compatibility model

- Phase 8B append-only JSONL must remain append-only.
- Future actor attribution should not rewrite existing audit records.
- Future attribution may be appended as separate actor attribution event records or emitted in derived reports.
- Existing audit record hashes must remain valid.
- Backfill must be report-only unless a later phase explicitly designs append-only backfill events.
- Phase 10B implements none of this runtime.

### Hash-chain compatibility model

- Existing hash-chain verification must remain valid.
- Actor attribution added after the fact must not invalidate old hash chains.
- Future hash inclusion must use explicit schema versioning.
- Derived actor-attributed reports must clearly separate source audit hash from derived actor context hash.
- Hash validity is not approval.

### Query/report compatibility model

- Future query/report outputs may support actor filters.
- Future actor filters may include actor_id, actor_type, identity_assurance, role label, advisory decision, and attribution source.
- Actor filters are search/report features only.
- Actor filters must not approve or execute anything.

### Export pack compatibility model

- Future export packs may include actor attribution sidecar files.
- Actor attribution sidecars must preserve source manifest hashes.
- Export pack inclusion is not approval.
- Signed export remains not approval.
- Verified export remains not approval.

### Final acceptance compatibility model

- Future final acceptance packs may reference actor-attributed audit reports.
- Final acceptance evidence remains not approval.
- Reviewer action remains guidance only.
- Approval remains Phase 7D selected-gate manual boundary.

### Future integration package compatibility

- Phase 10B aligns with Phase 10A readiness package model.
- Future Phase 10C may create a local evidence bundle with actor/RBAC context.
- Phase 10B does not implement bundle creation.

### Future audit record input contract

Conceptual future input fields:

- `audit_event_type`
- `audit_event_id`
- `audit_event_timestamp_utc`
- `source_phase`
- `source_artifact_reference`
- `actor_context_reference`
- `rbac_advisory_reference`
- `signature_evidence_reference`
- `approval_boundary_statement`

State Phase 10B does not modify runtime input contracts.

### Future audit report output contract

Conceptual future output fields:

- `report_schema_version`
- `source_audit_records`
- `actor_context_summary`
- `rbac_advisory_summary`
- `signature_evidence_summary`
- `actor_attributed_records`
- `actor_filter_summary`
- `approval_boundary_statement`
- `limitations`

State Phase 10B does not emit runtime reports.

### Future audit export output contract

Conceptual future output fields:

- `export_schema_version`
- `source_manifest_reference`
- `actor_attribution_sidecar_reference`
- `rbac_advisory_sidecar_reference`
- `signature_evidence_reference`
- `compatibility_matrix`
- `approval_boundary_statement`
- `limitations`

State Phase 10B does not emit runtime exports.

### Migration and backward compatibility plan

- Phase 10B design-only
- Phase 10C local evidence bundle design/prototype
- Phase 10D derived actor-attributed audit report prototype
- Phase 10E export sidecar design/prototype
- later schema versioning for audit actor fields
- existing Phase 8 artifacts must remain readable
- existing hash chains must remain valid
- actor attribution must be additive/derived unless later explicitly versioned
- approval boundary must be preserved

### Privacy and PII minimization model

- prefer pseudonymous actor_id
- avoid raw email
- avoid full legal name
- store actor_display_label only when needed
- separate stable actor_id from display label
- never store secrets as actor attribution metadata
- minimize registry-derived fields
- support future redaction

### Secret handling model

- actor attribution integration must never store raw AFFILIATE_PHASE8L_PROTOTYPE_KEY
- must never store private keys
- must never store API keys
- must never store OAuth/OIDC/SAML tokens
- must never store database passwords
- must never store affiliate credentials
- must reject secret-like metadata in future runtime

### Approval boundary preservation model

- actor attribution integration plan is not runtime integration
- audit actor attribution is not authentication
- audit actor attribution is not approval
- audit actor field presence is not approval
- actor metadata validity is not approval
- registry presence is not authentication
- registry presence is not approval
- RBAC advisory decision is not approval
- RBAC allow decision is not approval
- signature verification remains not approval
- final acceptance remains not approval
- integrated audit evidence is not approval
- approval remains Phase 7D selected-gate manual boundary
- integration plan must not trigger wrapper
- integration plan must not execute primitives
- integration plan must not trigger next gate
- integration plan must not set approval flags

### Runtime safety model

- Phase 10B adds no runtime.
- Future runtime must not rewrite existing audit records.
- Future runtime must not invalidate hash chains.
- Future runtime must not call Phase 7D wrapper.
- Future runtime must not execute primitives.
- Future runtime must not write vault.
- Future runtime must not mutate Phase 8 source outputs.
- Future runtime must not mutate Phase 9 source outputs.
- Future runtime must write only to its own tmp output root.
- Future runtime must remain advisory/evidence only unless a later phase explicitly changes scope.

### Non-authentication boundary

- Phase 10B does not authenticate.
- Actor source binding is not login.
- Registry reference is not session.
- Future authentication requires separate design and explicit scope.

### Non-RBAC-enforcement boundary

- Phase 10B does not enforce RBAC.
- RBAC advisory source binding is not enforcement.
- Advisory allow does not authorize execution.
- Future enforcement requires separate design and explicit scope.

### Non-approval boundary

- Actor-attributed audit evidence does not approve.
- Evidence does not approve.
- Actor attribution does not approve.
- RBAC advisory does not approve.
- Signature verification does not approve.
- Approval remains separate selected-gate manual act.

### Future Phase 10C boundary

- Future Phase 10C may define a local evidence bundle with actor/RBAC context.
- Phase 10C should remain local-only.
- Phase 10C must not mutate Phase 8 or Phase 9 source outputs.
- Phase 10C must preserve Phase 7D approval boundary.
- Phase 10C must not implement authentication or RBAC enforcement.

### Compatibility with Phase 10A

- Phase 10B follows Phase 10A governed readiness model.
- Phase 10B narrows readiness design toward audit store actor attribution.
- Phase 10B does not implement the readiness package runtime.

### Compatibility with Phase 9G/9D/9C/9F

- Phase 10B follows Phase 9G acceptance boundaries.
- Phase 10B may reference Phase 9D actor attribution conceptually.
- Phase 10B may reference Phase 9C registry conceptually.
- Phase 10B may reference Phase 9F advisory RBAC conceptually.
- Phase 10B does not modify Phase 9 runtime.
- Actor attribution remains evidence only.
- Registry presence remains not authentication.
- RBAC advisory report remains evidence only.

### Compatibility with Phase 8B/8C/8D/8E/8G/8M/8O

- Phase 10B may reference Phase 8 audit/export/signature/final acceptance artifacts conceptually.
- Phase 10B does not modify Phase 8 runtime.
- Phase 8B append-only behavior remains unchanged.
- Phase 8C verification behavior remains unchanged.
- Phase 8D query behavior remains unchanged.
- Phase 8E export behavior remains unchanged.
- Phase 8G/8M verification behavior remains unchanged.
- Signature verification remains not approval.
- Final acceptance remains not approval.

### Compatibility with Phase 7D

- Phase 7D remains selected-gate manual approval runtime.
- Phase 10B does not modify Phase 7D.
- Actor-attributed audit evidence must not approve.
- Actor-attributed audit evidence must not execute primitives.

### Failure taxonomy

- `audit_actor_context_missing` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `audit_actor_context_untrusted` — critical; `actor_context_review_required`; `reject_audit_actor_integration_until_resolved`.
- `audit_actor_schema_missing` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `audit_actor_schema_incompatible` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `source_audit_record_missing` — warning; `evidence_review_required`; `manual_review_required`.
- `source_hash_chain_unavailable` — warning; `evidence_review_required`; `manual_review_required`.
- `source_hash_chain_invalid` — critical; `evidence_review_required`; `reject_audit_actor_integration_until_resolved`.
- `actor_source_binding_missing` — warning; `actor_context_review_required`; `manual_review_required`.
- `actor_source_binding_untrusted` — critical; `actor_context_review_required`; `reject_audit_actor_integration_until_resolved`.
- `rbac_advisory_binding_missing` — warning; `rbac_advisory_review_required`; `manual_review_required`.
- `rbac_advisory_binding_untrusted` — critical; `rbac_advisory_review_required`; `reject_audit_actor_integration_until_resolved`.
- `signature_evidence_binding_missing` — warning; `signature_review_required`; `manual_review_required`.
- `signature_evidence_binding_untrusted` — critical; `signature_review_required`; `reject_audit_actor_integration_until_resolved`.
- `export_sidecar_missing` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `export_sidecar_incompatible` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `backward_compatibility_risk` — warning; `audit_actor_integration_review_required`; `manual_review_required`.
- `privacy_review_required` — warning; `privacy_review_required`; `manual_review_required`.
- `secret_metadata_detected` — critical; `privacy_review_required`; `reject_audit_actor_integration_until_resolved`.
- `approval_inference_detected` — critical; `approval_boundary_review_required`; `reject_runtime_scope_until_resolved`.
- `primitive_execution_intent_detected` — critical; `primitive_execution_blocked`; `reject_runtime_scope_until_resolved`.
- `vault_mutation_intent_detected` — critical; `vault_mutation_blocked`; `reject_runtime_scope_until_resolved`.
- `runtime_scope_violation` — critical; `runtime_scope_violation`; `reject_runtime_scope_until_resolved`.

Allowed severities:

- `info`
- `warning`
- `critical`

Allowed incident classifications:

- `none`
- `audit_actor_integration_review_required`
- `evidence_review_required`
- `actor_context_review_required`
- `rbac_advisory_review_required`
- `signature_review_required`
- `approval_boundary_review_required`
- `privacy_review_required`
- `runtime_scope_violation`
- `primitive_execution_blocked`
- `vault_mutation_blocked`

Allowed reviewer actions:

- `no_action_required`
- `manual_review_required`
- `reject_audit_actor_integration_until_resolved`
- `reject_runtime_scope_until_resolved`

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the integration evidence.
- `reject_audit_actor_integration_until_resolved` — actor attribution integration evidence is rejected until resolved.
- `reject_runtime_scope_until_resolved` — runtime scope expansion is rejected until resolved.

Rules:

- reviewer action is guidance only
- reviewer action is not approval
- reviewer action must not trigger wrapper
- reviewer action must not execute primitives
- reviewer action must not trigger next gate

### Non-goals

Phase 10B does not:

- implement audit actor attribution runtime
- implement audit store runtime changes
- implement audit report runtime changes
- implement audit export runtime changes
- implement integration runtime
- implement evidence bundle runtime
- implement authentication
- implement RBAC enforcement
- implement production policy engine
- implement login
- implement sessions
- implement user store
- implement OIDC/OAuth/SAML
- implement external identity provider
- implement backend/API/database
- implement key custody
- implement production signing
- implement production verifier
- modify Phase 9F runtime
- modify Phase 9D runtime
- modify Phase 9C runtime
- modify Phase 8 runtime
- modify Phase 7D wrapper
- execute primitives
- write vault
- approve anything
- trigger next gate
- add chain execution
- create production deployment

### Known limitations

- design only
- no audit actor attribution runtime
- no integration runtime
- no evidence bundle runtime
- no authentication
- no RBAC enforcement
- no production policy engine
- no login
- no session runtime
- no user store
- no enterprise identity
- no governed key custody
- no strong non-repudiation
- no backend/API/database
- no production deployment
- local prototype context only
