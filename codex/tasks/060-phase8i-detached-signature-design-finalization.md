# Task 060 — Phase 8I Detached Signature Design Finalization

phase8i_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: detached_signature_design_finalized

signing_implementation_status: design_only

signature_runtime_status: not_implemented

## Purpose

Finalize detached signature governance for future Phase 8E export-pack
signing. Phase 8I is docs/tests design-only: it defines a signed payload
descriptor, a detached signature envelope schema, signer/key metadata
models, a signature algorithm policy, a signing policy version model, key
lifecycle/rotation/revocation policy, a verification ceremony, a signature
failure taxonomy, and a signing event audit trail model. Phase 8I
implements no signing, no signature verification, and no key management.

## Scope

Phase 8I is docs/tests design-only. It adds a design document and a
docs-contract test, adds no runtime script, changes no Phase 8G/8H verifier
runtime behavior, changes no Phase 8E export behavior, changes no Phase 7D
wrapper behavior, changes no approval logic, executes no primitive,
performs no vault read/write, adds no new mutation path, and adds no
backend/API/database/network behavior. It generates no keys and handles no
private key material.

## Files

- `codex/tasks/060-phase8i-detached-signature-design-finalization.md`
- `docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`
- `tests/test_phase8i_detached_signature_design_finalization.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`
- additive updates to `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`
- additive updates to `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`

## Status model

- `success`: the detached signature design exists, additive documentation
  pointers exist, `phase7d_runtime_readiness` remains
  `implemented_manual_gate`, `signing_implementation_status` is
  `design_only`, `signature_runtime_status` is `not_implemented`, no
  runtime/signing/key/certificate file is added, and protected runtime
  files stay unchanged.
- `failed`: required design coverage is missing, additive docs regress, a
  runtime script or key material is added, or a protected runtime surface
  changes.

## Detached signature design objective

Provide a complete, implementation-ready design for a future detached
signature layer over Phase 8G/8H verification reports, so that a later
phase can implement signing/verification against a stable schema, without
implementing any signing, verification, or key management code in this
phase.

## Current trust boundary

- Phase 8E creates export packs
- Phase 8G/8H verify hash-only integrity
- Phase 8H reviewer action is review guidance only
- no signing runtime exists
- no authenticated operator identity exists
- no non-repudiation exists
- detached signature design must not turn evidence into approval
- durable audit remains a local/tmp workflow

## Signed payload descriptor model

Proposed canonical descriptor fields: `payload_schema_version`,
`export_manifest_path`, `export_manifest_sha256`, `bundle_hash`,
`computed_manifest_hash`, `report_schema_version`,
`issue_taxonomy_version`, `compatibility_matrix_version`,
`verifier_hardening_status`, `verification_status`,
`compatibility_result`, `incident_classification`, `reviewer_action`,
`reviewer_action_required`, `generated_from_phase`, `generated_by_tool`,
`created_at_utc`. Canonical JSON, deterministic ordering, no private key
material, no secrets, no approval flags. Evidence only, not approval.

## Detached signature envelope schema

Proposed future envelope fields: `signature_schema_version`,
`signed_payload_sha256`, `signed_payload_descriptor_path`,
`detached_signature_path`, `signature_algorithm`, `signature_encoding`,
`key_id`, `signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `signing_timestamp_utc`, `signature_status`,
`verification_status`, `revocation_status`, `rotation_epoch`,
`approval_boundary_statement`. Allowed `signature_status` values:
`not_present`, `present`, `malformed`, `unsupported_algorithm`,
`key_not_found`, `verification_failed`, `verification_passed`,
`revoked_key`, `expired_key`, `policy_mismatch`. Stored separately from
the export manifest; never mutates source evidence; never triggers
approval, the wrapper, or the next gate. No signing command examples or
executable code are included.

## Signing target model

The signing target is `signed_payload_sha256`, not raw evidence bytes. The
signed payload descriptor references `bundle_hash` and
`computed_manifest_hash`. The signing target is stable, deterministic, free
of volatile timestamps beyond the payload's own `created_at_utc`, free of
private key material, and not approval.

## Bundle hash signing model

`bundle_hash` remains a hash-only evidence integrity anchor. A future
signature signs a descriptor that includes `bundle_hash`. A `bundle_hash`
mismatch invalidates signing eligibility and requires manual review; a
future implementation must reject or flag as untrusted a signature over a
mismatched bundle. `bundle_hash` does not approve anything.

## Signer metadata model

Fields: `signer_id`, `signer_role`, `signer_identity_assurance`,
`signer_contact_reference`, `signer_org_unit`,
`signer_approval_authority_claim`. Signer metadata avoids sensitive
personal data where possible, is not a substitute for authenticated
identity, and is never treated as approval;
`signer_approval_authority_claim` is descriptive only until identity/
authorization is implemented.

## Key identifier model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_owner`,
`key_purpose`, `key_scope`, `key_created_at`, `key_expires_at`,
`key_status`. Allowed `key_status` values: `active`, `retired`, `revoked`,
`expired`, `unknown`. Private keys are never committed, never placed in
tmp export packs, and never written to docs. Key identifiers are metadata
only, not proof of identity without verification.

## Signature algorithm policy

Design-only fields: `supported_algorithm_policy_version`,
`allowed_algorithms`, `disallowed_algorithms`, `minimum_key_strength`,
`hash_algorithm`, `signature_encoding`. Phase 8I selects no final
production algorithm and includes no executable algorithm commands; a
disallowed weak algorithm encountered later must require manual review.

## Signing policy version model

Fields: `signing_policy_version`, `policy_effective_at`, `policy_owner`,
`allowed_signer_roles`, `required_identity_assurance`,
`required_verifier_schema_version`, `required_manifest_schema_version`,
`required_bundle_hash_presence`, `approval_boundary_statement`. The
signing policy controls signature eligibility, never authorizes approval
execution, and a policy mismatch requires manual review.

## Key lifecycle model

Lifecycle states: `proposed`, `active`, `rotating`, `retired`, `revoked`,
`expired`. Lifecycle must be governed before implementation; rotation and
revocation must be auditable; lost/compromised key handling requires
incident review; a lifecycle event does not trigger approval.

## Rotation policy

Covers rotation trigger, cadence, owner, overlap window, previous-key
validation, migration handling, and stale-signature handling. Rotation
must not invalidate historical evidence automatically and must not trigger
re-signing automatically without manual review.

## Revocation policy

Covers revocation trigger, authority, effective time, affected-signature
review, historical-evidence treatment, an emergency revocation path, and
manual review requirements. Revoked-key signatures require manual review;
revocation must not delete evidence and must not trigger rollback or
execution.

## Verification ceremony

1. generate the Phase 8E export pack
2. run the Phase 8G/8H hardened verifier
3. confirm `verification_status`, `compatibility_result`,
   `incident_classification`, `reviewer_action`
4. build the signed payload descriptor
5. compute `signed_payload_sha256`
6. evaluate signing policy eligibility
7. create the detached signature (future implementation)
8. record the signing event audit trail
9. verify the detached signature (future implementation)
10. record the verification result
11. require manual review on any mismatch or failure
12. never treat the signature or its verification as approval

## Signature failure taxonomy

Failure types: `signature_missing`, `signature_malformed`,
`unsupported_algorithm`, `signed_payload_hash_mismatch`,
`bundle_hash_mismatch`, `manifest_hash_mismatch`, `key_not_found`,
`key_revoked`, `key_expired`, `key_status_unknown`,
`signing_policy_mismatch`, `signer_identity_unverified`,
`signature_verification_failed`, `signature_replay_suspected`,
`signature_metadata_incomplete`. Severity values: `info`, `warning`,
`critical`. Reviewer action values: `no_action_required`,
`manual_review_required`, `reject_signature_until_resolved`. Incident
classification values: `none`, `signature_not_available`,
`signature_integrity_failure`, `key_lifecycle_review_required`,
`policy_review_required`, `signer_identity_review_required`,
`replay_review_required`. Every failure type maps to exactly one severity,
reviewer action, and incident classification, documented in the design
doc's mapping table.

## Signing event audit trail model

Future fields: `signing_event_id`, `signature_schema_version`,
`signed_payload_sha256`, `bundle_hash`, `manifest_hash`, `key_id`,
`signer_id`, `signer_role`, `signing_policy_version`,
`signing_timestamp_utc`, `signature_status`, `verification_status`,
`reviewer_action`, `approval_boundary_statement`. The audit trail is
evidence only: it never executes a primitive, never triggers the wrapper,
never mutates the Phase 8B audit store absent a future explicitly-approved
append-only design, and is never stored in the vault by Phase 8I.

## Non-repudiation limitation

Without authenticated identity or governed key custody, strong
non-repudiation is not available; without a revocation/rotation process,
signature trust is incomplete. A local-only prototype provides
tamper-evidence, not enterprise non-repudiation, and signature strength
must not be overclaimed.

## Privacy and secret handling

No private keys in the repository or export pack; no secrets or approval
flags in the payload descriptor; no API keys or affiliate secrets; no raw
terminal dump containing secrets; signer metadata avoids unnecessary
personal data; signing logs/screenshots must be sanitized.

## Non-goals

Phase 8I does not implement signing, a signature verification script, key
generation, private key handling, encryption, KMS/Secrets Manager, or
backend/API/database. It does not modify Phase 8G/8H verifier runtime
behavior, Phase 8E export behavior, or Phase 7D wrapper behavior, execute
primitives, approve anything, trigger the next gate, add chain execution,
or create a production deployment.

## Phase 8H verifier boundary

Phase 8H remains hash-only; Phase 8I does not change Phase 8H runtime. A
future signature design depends on the Phase 8H report schema
(`report_schema_version`, `bundle_hash`, `computed_manifest_hash`,
`incident_classification`, `reviewer_action`). Phase 8H reviewer action
remains review guidance only.

## Phase 8E export boundary

The Phase 8E export pack remains read-only packaging. Phase 8I does not
change Phase 8E runtime. A future signature must not mutate export
evidence and a future signature envelope must be stored separately from
the export manifest.

## Phase 7D approval boundary

A signature is not approval; a verified signature is not approval; a
signed export is not approval; signer metadata is not approval; reviewer
action is not approval. Signing must not bypass the selected-gate manual
approval boundary, must not set approval flags, must not trigger the
wrapper, and must not trigger the next gate. Approval remains the Phase 7D
selected-gate manual boundary.

## Future implementation path

- Phase 8J: Detached Signature Verifier Design
- Phase 8K: Local Detached Signature Prototype (local-only, no approval
  integration)
- Phase 8L: Key Management Design
- Phase 8M: Revocation/Rotation Runbook
- Phase 8N: Optional Enterprise KMS Integration Design

None of the above are implemented in Phase 8I.

## Test strategy

Deterministic docs-contract tests: task and design doc exist; no Phase 8I
runtime script exists; required status tokens exist; scope/non-goal tokens
exist; current-trust-boundary and design-objective coverage; every required
design section exists; signed payload descriptor field coverage; detached
signature envelope field and `signature_status` enum coverage; key
lifecycle/rotation/revocation coverage; signature failure taxonomy coverage
(all failure types, severities, reviewer actions, incident classifications);
approval-boundary assertion coverage; ROADMAP/PROJECT_STATE/PHASE8H/
PHASE8G/PHASE8F pointers; ROADMAP/PROJECT_STATE token regression; protected
runtime file hash regression; absence of any Phase 8I runtime/signing/key/
certificate/database/backend/API/package.json file; and a static-safety
scan over only the two new Phase 8I files.

## Acceptance criteria

- task exists
- design doc exists
- design doc contains `phase8i_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains
  `durable_audit_store_status: detached_signature_design_finalized`
- design doc contains `signing_implementation_status: design_only`
- design doc contains `signature_runtime_status: not_implemented`
- design doc states docs/tests design-only
- design doc states no signing/signature-verifier/key-generation/private-
  key-handling/encryption/KMS/Secrets-Manager implementation
- design doc states no Phase 8G/8H verifier behavior change
- design doc states no Phase 8E export behavior change
- design doc states no Phase 7D wrapper behavior change
- design doc states no primitive execution and no vault read/write
- design doc states no new mutation path
- ROADMAP, PROJECT_STATE, PHASE8H, PHASE8G, and PHASE8F all reference
  Phase 8I additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C/8D/8E/8G/8H runtime files remain
  unchanged
- no new runtime, signing, key, certificate, database, backend, API, or
  package.json file is added by Phase 8I

## Verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase8i_detached_signature_design_finalization.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m pytest -q tests/test_phase8f_export_integrity_signing_design.py
python -m pytest -q tests/test_phase8e_audit_export_pack.py
python -m pytest -q tests/test_phase8d_audit_store_query_cli.py
python -m pytest -q tests/test_phase8c_audit_store_verifier_reporting.py
python -m pytest -q tests/test_phase8b_local_append_only_audit_store.py
python -m pytest -q tests/test_phase8a_durable_audit_store_design.py
python -m pytest -q tests/test_phase7h_operator_runbook_hardening.py
python -m pytest -q tests/test_phase7g_operator_acceptance_demo_pack.py
python -m pytest -q tests/test_phase7f_runtime_wrapper_live_snapshot.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m pytest -q tests/test_phase7e_release_snapshot_runtime_blocked.py
python -m pytest -q tests/test_phase7d_implementation_plan_finalization.py
python -m pytest -q tests/test_phase7d_r_high_risk_readiness_review.py
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
test "$(stat -c '%a' scripts/dev/run_phase8g_export_integrity.sh)" = "755"
git ls-files -s scripts/dev/run_phase8g_export_integrity.sh | grep "^100755 "

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8I is design only. No signing, signature verifier, or key-management
implementation exists. No encryption, no authenticated operator identity,
no non-repudiation, no backend/API/database, and no production deployment
exist.

## Final status target

phase8i_status: success
