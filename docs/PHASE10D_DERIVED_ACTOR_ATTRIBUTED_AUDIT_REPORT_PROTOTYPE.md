# Phase 10D — Derived Actor-Attributed Audit Report Prototype

phase10d_status: success

phase10c_status: success

phase10b_status: success

phase10a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

audit_actor_attribution_integration_status: derived_report_prototype

governed_runtime_integration_status: local_evidence_bundle_and_actor_report_prototypes

integration_runtime_status: local_derived_report_prototype

local_evidence_bundle_status: prototype_local_only

actor_attributed_audit_report_status: prototype_local_only

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

Phase 10D implements a local-only derived actor-attributed audit report
prototype. It correlates local audit evidence with optional actor attribution,
advisory RBAC, evidence bundle, signature, final acceptance, and approval
boundary context while preserving source immutability.

Phase 10D does not implement audit store mutation, authentication, RBAC
enforcement, backend/API/database, key custody, production signing, production
verification, or approval automation.

### Scope

- local-only derived actor-attributed audit report prototype
- local manifest input
- local audit evidence references
- actor attribution context reference
- RBAC advisory context reference
- evidence bundle context reference
- signature/final acceptance context references
- approval boundary reference
- deterministic local JSON/MD output
- SHA-256 file hashes for present local evidence
- missing-safe evidence references
- safe summary extraction from JSON context files
- privacy/secret scan
- path safety
- no source mutation
- no audit record rewrite
- no hash-chain rewrite
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no Phase 8 runtime behavior change
- no Phase 9 runtime behavior change
- no Phase 10C runtime behavior change

### Runtime command

```bash
bash scripts/dev/run_phase10d_actor_attributed_audit_report.sh --manifest <manifest-json>
```

Do not include approval flags or `--execute`.

### Manifest model

Required manifest fields:

- `report_schema_version`
- `report_id`
- `report_purpose`
- `audit_evidence_references`
- `approval_boundary_statement`

`report_schema_version` must be `phase10d.actor_attributed_audit_report.v1`.
Manifest is local-only, manifest is not approval, and the manifest must not
contain approval flags or primitive execution intent.

### Audit evidence reference model

Fields:

- `evidence_id`
- `evidence_type`
- `evidence_phase`
- `evidence_path`
- `evidence_purpose`
- `evidence_boundary_statement`
- `evidence_status`
- `evidence_sha256`
- `evidence_size_bytes`

Evidence hash is not approval. Evidence reference is not approval. Missing
evidence is warning when path is safe. Unsafe evidence path is critical.

### Actor context summary

Actor context fields:

- `actor_attribution_context`
- `actor_id`
- `actor_type`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_role_labels`
- `actor_attribution_status`
- `approval_boundary_statement`

Actor context is not authentication. Actor context is not approval. Actor
summary is evidence only.

### RBAC advisory context summary

RBAC advisory fields:

- `rbac_advisory_context`
- `advisory_decision`
- `decision_reason`
- `obligations`
- `denial_reasons`
- `rbac_policy_status`
- `rbac_enforcement_status`
- `approval_boundary_statement`

RBAC advisory context is not enforcement. RBAC allow decision is not approval.
RBAC advisory summary is evidence only.

### Evidence bundle context summary

Evidence bundle fields:

- `evidence_bundle_context`
- `bundle_id`
- `bundle_status`
- `bundle_hash`
- `evidence_reference_count`
- `present_evidence_count`
- `missing_evidence_count`
- `approval_boundary_statement`

Bundle validity is not approval. Bundle summary is evidence only.

### Source immutability

Phase 10D reads source files only. It performs no source mutation, no audit
record rewrite, and no hash-chain rewrite.

### Path safety

Manifest and evidence/context paths must resolve under the repo root. They must
not resolve under `vault/`, `docs/`, `scripts/`, `codex/`, or `.git/`, and
references must not be symlinks. Output must remain under
`tmp/phase10d-actor-attributed-audit-report/`.

### Non-authentication boundary

Audit actor attribution is not authentication. Actor metadata validity is not
approval. Registry presence is not authentication.

### Non-RBAC-enforcement boundary

RBAC advisory context is not enforcement. `rbac_enforcement_status` remains
`not_implemented`. RBAC advisory decision is not approval.

### Non-approval boundary

Derived actor-attributed audit report is not approval.

Audit actor attribution is not approval.

Evidence hash is not approval.

Audit hash-chain validity is not approval.

Signature verification remains not approval.

Final acceptance remains not approval.

Approval remains Phase 7D selected-gate manual boundary.

### Compatibility with Phase 10C

Phase 10D may reference the local evidence bundle prototype at
`docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md` as context only and
does not modify Phase 10C runtime behavior.

### Compatibility with Phase 10B

Phase 10D follows `docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`
and implements a derived report only, not audit store actor-field mutation.

### Compatibility with Phase 10A

Phase 10D remains inside the governed readiness boundary from
`docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`.

### Compatibility with Phase 9G/9F/9D/9C

Phase 10D may reference Phase 9 acceptance, local advisory RBAC, actor
attribution, and local registry outputs as evidence context only.

### Compatibility with Phase 8O/8M/8G/8E/8D/8C/8B

Phase 10D may reference Phase 8 final acceptance, signature verification,
export integrity, export pack, audit query, audit store report, and append-only
audit store artifacts as local evidence only.

Canonical Phase 8B artifact:

- `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

Canonical Phase 8B focused test:

- `tests/test_phase8b_local_append_only_audit_store.py`

Canonical Phase 8D artifact:

- `docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`

Canonical Phase 8D focused test:

- `tests/test_phase8d_audit_store_query_cli.py`

Compatibility note:

- earlier wording may refer to
  `PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md`, but the canonical
  Phase 8B document is `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

### Compatibility with Phase 7D

Phase 10D does not call the wrapper, does not set approval flags, does not
trigger next gate, and preserves the selected-gate manual boundary.

### Failure taxonomy

Success:

- `report_status: built`
- `reviewer_action: no_action_required`
- `incident_classification: none`

Warnings:

- `report_status: built_with_warnings`
- `reviewer_action: manual_review_required`
- `incident_classification: evidence_review_required`

Reject:

- `report_status: not_built`
- `incident_classification` may be `runtime_scope_violation`,
  `privacy_review_required`, `approval_boundary_review_required`, or
  `primitive_execution_blocked`

### Reviewer action mapping

- `no_action_required` — all referenced inputs are present and valid.
- `manual_review_required` — safe missing evidence or optional context exists.
- `reject_actor_attributed_report_until_resolved` — secret-like metadata,
  manifest errors, or approval-boundary failures block the derived report.
- `reject_runtime_scope_until_resolved` — unsafe path or execution/enforcement
  scope expansion blocks the derived report.

Reviewer action is guidance only and is not approval.

### Known limitations

- local prototype only
- derived actor-attributed audit report only
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no key management runtime
- no audit store mutation
- no wrapper execution
- no primitive execution

