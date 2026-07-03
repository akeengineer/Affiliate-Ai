# Phase 10C — Local Evidence Bundle with Actor/RBAC Context

phase10c_status: success

phase10b_status: success

phase10a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

audit_actor_attribution_integration_status: design_only

governed_runtime_integration_status: local_evidence_bundle_prototype

integration_runtime_status: local_evidence_bundle_prototype

local_evidence_bundle_status: prototype_local_only

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

Phase 10C implements a local-only derived evidence bundle runtime prototype. It
reads one local manifest, validates safe evidence/context references, hashes
present files, treats safe missing files as warnings, rejects unsafe paths,
secrets, approval flags, and execution intent, and emits deterministic JSON +
Markdown only under `tmp/phase10c-local-evidence-bundle/`.

Local evidence bundle is not approval. Evidence bundle validity is not
approval. Actor context is not authentication. RBAC advisory context is not
enforcement. RBAC allow decision is not approval. Signature verification
remains not approval. Approval remains Phase 7D selected-gate manual boundary.

### Scope

- local-only derived evidence bundle runtime prototype
- standard library only
- read one local manifest
- validate safe evidence/context references
- hash present files
- safe missing files
- built_with_warnings
- reject unsafe paths
- reject secrets
- reject approval flags
- reject execution intent
- emit deterministic JSON + Markdown
- no audit store mutation
- no integration enforcement
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no wrapper behavior change
- no primitive execution
- no vault read/write

### Runtime command

```bash
python scripts/dev/build_phase10c_local_evidence_bundle.py \
  --manifest path/to/evidence-bundle-manifest.json \
  --output-dir tmp/phase10c-local-evidence-bundle
```

Wrapper:

```bash
scripts/dev/run_phase10c_local_evidence_bundle.sh --manifest path/to/evidence-bundle-manifest.json
```

### Manifest model

Required fields:

- `bundle_schema_version`
- `bundle_id`
- `bundle_purpose`
- `evidence_references`
- `approval_boundary_statement`

Rules:

- `bundle_schema_version` must equal `phase10c.local_evidence_bundle.v1`
- `evidence_references` must be a list
- secret-like metadata is rejected
- truthy approval flags are rejected
- primitive/execute/next_gate intent is rejected

### Evidence reference model

Required fields:

- `evidence_id`
- `evidence_type`
- `evidence_phase`
- `evidence_path`
- `evidence_purpose`
- `evidence_boundary_statement`

Allowed evidence types:

- `audit_export_pack`
- `export_integrity_report`
- `detached_signature_envelope`
- `signature_verifier_report`
- `final_acceptance_pack`
- `local_operator_registry`
- `actor_attribution_report`
- `local_rbac_advisory_report`
- `selected_gate_boundary_reference`
- `audit_store_report`
- `audit_query_result`
- `test_fixture`

Allowed evidence phases include `phase7d`, `phase8b`, `phase8c`, `phase8d`,
`phase8e`, `phase8g`, `phase8l`, `phase8m`, `phase8o`, `phase9c`, `phase9d`,
`phase9f`, `phase9g`, `phase10a`, `phase10b`, `phase10c`, and `test_fixture`.

Present evidence records `sha256`, `size_bytes`, `relative_path`, and
`evidence_status: present`.

### Optional context references

Optional fields:

- `actor_context_reference`
- `rbac_advisory_context_reference`
- `signature_context_reference`
- `approval_boundary_reference`

Each optional context uses:

- `reference_type`
- `reference_path`
- `reference_boundary_statement`

Present optional context records `sha256`, `size_bytes`, `relative_path`, and
`reference_status: present`. Safe missing optional context becomes a warning.

### Output layout

- `tmp/phase10c-local-evidence-bundle/local-evidence-bundle.json`
- `tmp/phase10c-local-evidence-bundle/local-evidence-bundle.md`

JSON is deterministic with `sort_keys=True` and `indent=2`.

`bundle_hash` is deterministic and excludes `bundle_hash` itself.

### Source immutability

- source evidence files are read-only
- actor/RBAC/signature context files are read-only
- Phase 8/9/7D source artifacts remain unchanged
- no audit record rewrite
- no hash-chain rewrite

### Path safety

- manifest path must resolve under the repo root
- manifest path must not resolve under `vault/`, `docs/`, `scripts/`,
  `codex/`, or `.git/`
- evidence/context references may resolve only under `tmp/` or `tests/fixtures/`
- references must not be symlinks
- unsafe path is `not_built`
- output-dir must resolve to `tmp/phase10c-local-evidence-bundle` or below it

### Privacy and secret handling

Reject secret-like or privacy-unsafe strings such as:

- `AFFILIATE_PHASE8L_PROTOTYPE_KEY`
- `BEGIN PRIVATE KEY`
- `BEGIN RSA PRIVATE KEY`
- `BEGIN OPENSSH PRIVATE KEY`
- `API_KEY=`
- `SECRET=`
- `TOKEN=`
- `PASSWORD=`
- `AWS_SECRET_ACCESS_KEY`
- `ssh-rsa`
- `OAuth access_token`
- `id_token`
- `refresh_token`
- external URL schemes
- raw email in bundle metadata

Secret-like metadata is `not_built` and nonzero.

### Approval boundary

Required approval boundary statements:

- local evidence bundle is not approval
- evidence bundle validity is not approval
- approval remains Phase 7D selected-gate manual boundary

Required evidence boundary statements:

- evidence reference is not approval
- evidence hash is not approval
- approval remains Phase 7D selected-gate manual boundary

Truthiness of `approved`, `is_approved`, `approval_granted`, `auto_approve`,
`approve_all`, `next_gate`, `execute`, or `enforcement_enabled` is rejected.

### Non-authentication boundary

Actor context is not authentication. Actor metadata runtime remains
`local_registry_prototype`, identity runtime remains `not_implemented`, and
authentication runtime remains `not_implemented`.

### Non-RBAC-enforcement boundary

RBAC advisory context is not enforcement. `rbac_policy_status` and
`rbac_runtime_status` remain `local_advisory_prototype`, while
`rbac_enforcement_status` remains `not_implemented`.

### Non-approval boundary

Local evidence bundle is not approval.

Evidence bundle validity is not approval.

RBAC allow decision is not approval.

Signature verification remains not approval.

Approval remains Phase 7D selected-gate manual boundary.

### Compatibility with Phase 10B

Phase 10C follows `docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`.
It implements a local derived evidence bundle only, not audit store actor
attribution runtime, and does not mutate source audit artifacts.

### Compatibility with Phase 10A

Phase 10C follows `docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`.
It turns governed readiness into a local evidence bundle prototype without
implementing authentication, RBAC enforcement, backend/API/database, or key
management runtime.

### Compatibility with Phase 9G/9F/9D/9C

Phase 10C may reference Phase 9 acceptance, advisory RBAC, actor attribution,
and local operator registry evidence context. Those source artifacts remain
evidence only and unchanged.

### Compatibility with Phase 8O/8M/8G/8E/8C/8B

Phase 10C may reference final acceptance, signature verification, export
integrity, export pack, audit store report, and append-only audit store
artifacts as local evidence context only.

Canonical Phase 8B artifact:

- `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

Canonical Phase 8B focused test:

- `tests/test_phase8b_local_append_only_audit_store.py`

Compatibility note:

- earlier task wording may refer to
  `PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md`, but the canonical
  Phase 8B document is `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`
- canonical Phase 8B document: `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

### Compatibility with Phase 7D

Phase 10C preserves the selected-gate manual approval boundary. It does not
call the wrapper, does not call approval primitives, and does not change manual
approval semantics.

### Failure taxonomy

Success outcomes:

- `bundle_status: built`
- `reviewer_action: no_action_required`
- `incident_classification: none`

Warning outcomes:

- `bundle_status: built_with_warnings`
- `reviewer_action: manual_review_required`
- `incident_classification: evidence_review_required`

Reject outcomes:

- `bundle_status: not_built`
- `incident_classification` may be `runtime_scope_violation`,
  `privacy_review_required`, `approval_boundary_review_required`, or
  `primitive_execution_blocked`

### Reviewer action mapping

- `no_action_required` — all references are present and valid.
- `manual_review_required` — safe missing evidence or safe missing context
  requires human review.
- `reject_evidence_bundle_until_resolved` — invalid manifest, secret-like
  metadata, or approval boundary failure blocks the bundle.
- `reject_runtime_scope_until_resolved` — unsafe path or execution/enforcement
  scope expansion blocks the bundle.

Reviewer action is guidance only and is not approval.

### Known limitations

- local prototype only
- derived evidence bundle only
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no key management runtime
- no audit store mutation
- no wrapper execution
- no primitive execution

### Phase 10D derived actor-attributed audit report prototype

Phase 10D derived actor-attributed audit report prototype now exists at
`docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md`. Phase 10D
may consume local evidence bundle output as context only, does not modify Phase
10C runtime behavior, and keeps approval at the Phase 7D selected-gate manual
boundary.
