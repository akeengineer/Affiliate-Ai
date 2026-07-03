# Task 076 — Phase 10C Local Evidence Bundle with Actor/RBAC Context

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

## 1. Purpose

Phase 10C implements a local-only derived evidence bundle runtime prototype
after Phase 10B and Phase 10A. It reads one local manifest, validates safe
evidence/context references, hashes present files, treats safe missing files as
warnings, rejects unsafe paths/secrets/approval flags/execution intent, and
emits deterministic JSON + Markdown only under
`tmp/phase10c-local-evidence-bundle/`.

## 2. Scope

- local-only derived evidence bundle runtime prototype
- standard library only
- read one local manifest
- validate safe evidence/context references
- hash present files
- safe missing files become `built_with_warnings`
- reject unsafe paths
- reject secrets
- reject approval flags
- reject primitive/execute/next_gate intent
- emit deterministic JSON + Markdown
- preserve all Phase 8/9/7D source artifacts unchanged
- no audit store mutation
- no integration enforcement
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no wrapper behavior change
- no primitive execution
- no vault read/write

## 3. Files

- `scripts/dev/build_phase10c_local_evidence_bundle.py`
- `scripts/dev/run_phase10c_local_evidence_bundle.sh`
- `tests/test_phase10c_local_evidence_bundle.py`
- `docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`
- additive updates to `docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`
- additive updates to `docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md`
- additive updates to `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`
- additive updates to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- additive updates to `.gitignore`

## 4. Runtime command

Primary CLI:

```bash
python scripts/dev/build_phase10c_local_evidence_bundle.py \
  --manifest path/to/evidence-bundle-manifest.json \
  --output-dir tmp/phase10c-local-evidence-bundle
```

Shell wrapper:

```bash
scripts/dev/run_phase10c_local_evidence_bundle.sh --manifest path/to/evidence-bundle-manifest.json
```

Focused verification commands:

```bash
python -m pytest -q tests/test_phase10c_local_evidence_bundle.py
python -m pytest -q tests/test_phase10b_actor_attribution_audit_store_integration_plan.py
python -m pytest -q tests/test_phase10a_governed_runtime_integration_readiness_design.py
python -m pytest -q tests/test_phase8b_local_append_only_audit_store.py
```

## 5. Manifest model

Required manifest fields:

- `bundle_schema_version`
- `bundle_id`
- `bundle_purpose`
- `evidence_references`
- `approval_boundary_statement`

Required rules:

- `bundle_schema_version` must equal `phase10c.local_evidence_bundle.v1`
- `evidence_references` must be a list
- manifest must reject truthy `approved`, `is_approved`, `approval_granted`,
  `auto_approve`, `approve_all`
- manifest must reject truthy `next_gate`, `execute`, `enforcement_enabled`
- manifest must reject primitive execution intent
- manifest must reject secret-like metadata

## 6. Evidence reference model

Required evidence fields:

- `evidence_id`
- `evidence_type`
- `evidence_phase`
- `evidence_path`
- `evidence_purpose`
- `evidence_boundary_statement`

Present evidence must record:

- `sha256`
- `size_bytes`
- `relative_path`
- `evidence_status: present`

Safe missing evidence must produce:

- `evidence_status: missing`
- warning issue
- `bundle_status: built_with_warnings`
- `reviewer_action: manual_review_required`
- exit `0`

Unsafe evidence must produce:

- `bundle_status: not_built`
- nonzero exit

## 7. Optional context references

Optional context objects:

- `actor_context_reference`
- `rbac_advisory_context_reference`
- `signature_context_reference`
- `approval_boundary_reference`

Each object uses:

- `reference_type`
- `reference_path`
- `reference_boundary_statement`

## 8. Output layout

- `tmp/phase10c-local-evidence-bundle/local-evidence-bundle.json`
- `tmp/phase10c-local-evidence-bundle/local-evidence-bundle.md`

JSON must use deterministic `sort_keys=True` and `indent=2`.

`bundle_hash` must be deterministic and exclude `bundle_hash` itself.

## 9. Path safety

- manifest path must resolve under repo root
- manifest path must not resolve under `vault/`, `docs/`, `scripts/`,
  `codex/`, or `.git/`
- evidence/context references may resolve only under `tmp/` or `tests/fixtures/`
- references must not be symlinks
- output-dir must resolve to `tmp/phase10c-local-evidence-bundle` or below it
- traversal and absolute paths outside repo must be rejected

## 10. Privacy and secret handling

Reject secret-like or privacy-unsafe strings such as:

- `AFFILIATE_PHASE8L_PROTOTYPE_KEY`
- `BEGIN PRIVATE KEY`
- `API_KEY=`
- `SECRET=`
- `TOKEN=`
- `PASSWORD=`
- `AWS_SECRET_ACCESS_KEY`
- `ssh-rsa`
- `id_token`
- `refresh_token`
- external URL schemes
- raw email in bundle metadata

## 11. Approval boundary

Required statements:

- local evidence bundle is not approval
- evidence bundle validity is not approval
- approval remains Phase 7D selected-gate manual boundary

Required evidence boundary phrases:

- evidence reference is not approval
- evidence hash is not approval
- approval remains Phase 7D selected-gate manual boundary

## 12. Final boundary

- Local evidence bundle is not approval
- Evidence bundle validity is not approval
- Actor context is not authentication
- RBAC advisory context is not enforcement
- RBAC allow decision is not approval
- Signature verification remains not approval
- Approval remains Phase 7D selected-gate manual boundary

## 13. Canonical Phase 8B references

Authoritative Phase 8B doc:

- `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

Authoritative Phase 8B test:

- `tests/test_phase8b_local_append_only_audit_store.py`

Compatibility note:

- earlier task wording may refer to
  `PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md`, but the canonical
  Phase 8B document is `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`
- canonical Phase 8B document: `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

Do not create new Phase 8B alias files in Phase 10C.

## 14. Protected runtime boundary

Phase 10C must not modify:

- `scripts/dev/ingest_phase8b_audit_record.py`
- `scripts/dev/run_phase8b_audit_ingest.sh`
- `scripts/dev/verify_phase8c_audit_store.py`
- `scripts/dev/run_phase8c_audit_report.sh`
- `scripts/dev/query_phase8d_audit_store.py`
- `scripts/dev/run_phase8d_audit_query.sh`
- `scripts/dev/build_phase8e_audit_export_pack.py`
- `scripts/dev/run_phase8e_audit_export.sh`
- `scripts/dev/verify_phase8g_export_integrity.py`
- `scripts/dev/run_phase8g_export_integrity.sh`
- `scripts/dev/build_phase8l_detached_signature.py`
- `scripts/dev/run_phase8l_detached_signature.sh`
- `scripts/dev/verify_phase8m_detached_signature.py`
- `scripts/dev/run_phase8m_detached_signature_verifier.sh`
- `scripts/dev/manage_phase9c_local_operator_registry.py`
- `scripts/dev/run_phase9c_local_operator_registry.sh`
- `scripts/dev/build_phase9d_actor_attribution_report.py`
- `scripts/dev/run_phase9d_actor_attribution_report.sh`
- `scripts/dev/evaluate_phase9f_local_rbac_policy.py`
- `scripts/dev/run_phase9f_local_rbac_policy.sh`
- `scripts/dev/run_phase7d_single_gate_wrapper.sh`
- `scripts/dev/execute_single_gate_approval.py`
- `scripts/dev/promote_product_candidates.py`
- `scripts/dev/create_decision.py`
- `scripts/dev/finalize_decision.py`

## 15. Verification expectations

- file existence/status coverage
- runtime static safety coverage
- valid/missing/invalid/path/privacy/approval/hash behavior coverage
- deterministic bundle hash coverage
- report schema coverage
- source immutability coverage
- documentation regression coverage
- protected runtime hash coverage

## 16. Non-goals

Phase 10C does not:

- implement audit store mutation
- implement integration enforcement
- implement authentication
- implement RBAC enforcement
- implement backend/API/database
- implement key management runtime
- implement wrapper execution
- execute primitives
- write vault
- approve anything
