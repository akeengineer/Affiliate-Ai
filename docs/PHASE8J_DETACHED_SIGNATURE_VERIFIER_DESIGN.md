# Phase 8J — Detached Signature Verifier Design

```text
phase8j_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: detached_signature_verifier_design
signing_implementation_status: design_only
signature_runtime_status: not_implemented
signature_verifier_runtime_status: not_implemented
major_phase_branch_workflow: enabled
```

### Purpose

Phase 8J designs the future detached signature verifier flow for signed
export packs: a verifier input contract, a signature envelope validation
model, a signed payload descriptor validation model, a signed payload hash
validation model, a bundle-hash/manifest-hash cross-check model, a key
metadata validation model, a signer identity assurance interpretation, a
revocation/rotation interpretation model, a signature status transition
model, a verification status model, a failure taxonomy mapping, a reviewer
action mapping, and a deterministic verification report schema. Phase 8J
does not implement signature verification runtime.

### Scope

- docs/tests design-only
- no signature verifier implementation
- no signing implementation
- no detached signature runtime implementation
- no key generation
- no private key handling
- no public key runtime handling beyond design references
- no encryption implementation
- no KMS implementation
- no Secrets Manager implementation
- no backend/FastAPI/API routes/database/SQLite/S3/DynamoDB
- no external APIs/URLs/network behavior
- no runtime wrapper behavior change
- no approval logic change
- no primitive execution
- no vault reads/writes
- no next-gate automation/chain execution/approve-all/global approval/
  multi-gate execution
- no affiliate content generation/autopublish/campaign launch/marketplace
  connector/production deployment
- no Node/npm/package.json/frontend framework/JavaScript
- no shell runner of any kind (no `scripts/dev/run_phase8j*.sh`)
- Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, and 8B/8C/8D/8E/8G/8H runtime
  behavior are unchanged

### Current trust boundary

- Phase 8E creates export packs
- Phase 8G/8H verify hash-only export integrity
- Phase 8I finalizes detached signature design
- no signature verifier runtime exists
- no signing runtime exists
- no authenticated operator identity exists
- no enterprise non-repudiation exists
- signature verifier design must not turn signature evidence into approval
- durable audit remains a local/tmp workflow

### Design objectives

Detached signature verifier design must eventually support:

- `signature envelope validation`
- `signed payload descriptor validation`
- `signed_payload_sha256` validation
- `bundle_hash` cross-check
- `manifest_hash` cross-check
- key metadata validation
- signer identity assurance interpretation
- revocation interpretation
- rotation interpretation
- `signature_status` transition model
- `verification_status` model
- failure taxonomy mapping
- reviewer action mapping
- deterministic verification report schema
- approval boundary

### Signature verifier input contract

Future inputs to the detached signature verifier:

- detached signature envelope
- signed payload descriptor
- Phase 8E export manifest
- Phase 8G/8H export integrity verification report
- key metadata record
- optional revocation metadata
- optional rotation metadata
- signing policy metadata

Rules:

- all inputs are evidence
- inputs must not include private keys
- inputs must not include secrets
- inputs must not include approval flags
- verifier inputs must not mutate source evidence
- verifier inputs must not trigger approval

### Signature envelope validation model

Future envelope fields: `signature_schema_version`,
`signed_payload_sha256`, `signed_payload_descriptor_path`,
`detached_signature_path`, `signature_algorithm`, `signature_encoding`,
`key_id`, `signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `signing_timestamp_utc`, `signature_status`,
`verification_status`, `revocation_status`, `rotation_epoch`,
`approval_boundary_statement`.

Validation checks:

- required fields present
- schema version supported
- signature algorithm allowed by policy
- encoding allowed by policy
- `key_id` present
- signer metadata present
- `approval_boundary_statement` present
- envelope path separation from export manifest
- no private key material
- no approval flags
- no mutation intent

### Signed payload descriptor validation model

Descriptor fields (Phase 8I's descriptor fields): `payload_schema_version`,
`export_manifest_path`, `export_manifest_sha256`, `bundle_hash`,
`computed_manifest_hash`, `report_schema_version`,
`issue_taxonomy_version`, `compatibility_matrix_version`,
`verifier_hardening_status`, `verification_status`,
`compatibility_result`, `incident_classification`, `reviewer_action`,
`reviewer_action_required`, `generated_from_phase`, `generated_by_tool`,
`created_at_utc`.

Validation checks:

- descriptor is canonical JSON
- deterministic ordering
- required fields present
- descriptor references the Phase 8H report schema
- descriptor references the export manifest hash
- descriptor references the bundle hash
- descriptor contains no secrets
- descriptor contains no approval flags
- descriptor is not approval

### Signed payload hash validation model

- canonical descriptor bytes are the hashing input
- `signed_payload_sha256` is computed from the canonical descriptor
- the computed hash is compared with the envelope `signed_payload_sha256`
- a mismatch means `signature_integrity_failure`
- hash match is necessary but not approval
- hash match must not trigger the wrapper
- hash match must not trigger the next gate

### Bundle hash and manifest hash cross-check model

- `export_manifest_sha256` cross-checks against the Phase 8E manifest bytes
- `computed_manifest_hash` cross-checks against the Phase 8H report if
  available
- `bundle_hash` cross-checks against the Phase 8G/8H `computed_bundle_hash`
- a mismatch is classified as a signature integrity failure
- missing optional context is classified separately from a mismatch
- both classifications map to a reviewer action

Rules:

- `bundle_hash` match does not approve anything
- `manifest_hash` match does not approve anything
- cross-check success is evidence integrity only

### Key metadata validation model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_owner`,
`key_purpose`, `key_scope`, `key_created_at`, `key_expires_at`,
`key_status`.

Allowed `key_status` values: `active`, `retired`, `revoked`, `expired`,
`unknown`.

Rules:

- key metadata is evidence only
- key metadata is not private key material
- key metadata does not prove signer identity without authenticated
  identity
- key metadata does not approve anything

### Signer identity assurance interpretation

`signer_identity_assurance` values: `unauthenticated`,
`operator_declared`, `local_registry_verified`,
`enterprise_identity_verified`, `hardware_backed`.

Rules:

- the current expected level is `unauthenticated` or `operator_declared`
  until Phase 9 identity work
- signer identity assurance is interpretation only
- signer identity assurance does not approve anything
- low assurance requires manual review

### Revocation and rotation interpretation model

`revocation_status` values: `not_checked`, `not_revoked`, `revoked`,
`unknown`.

Rotation interpretation values: `current_epoch`, `previous_epoch_allowed`,
`stale_epoch`, `unknown_epoch`.

Rules:

- a revoked key requires manual review or rejection of the signature until
  resolved
- unknown revocation requires manual review
- a stale rotation epoch requires manual review
- a revocation/rotation result must not delete evidence
- a revocation/rotation result must not trigger rollback/execution

### Signature status transition model

Status progression values: `not_present`, `present`, `malformed`,
`unsupported_algorithm`, `key_not_found`, `verification_failed`,
`verification_passed`, `revoked_key`, `expired_key`, `policy_mismatch`.

Allowed transitions:

- `not_present` -> `present`
- `present` -> `malformed`
- `present` -> `unsupported_algorithm`
- `present` -> `key_not_found`
- `present` -> `verification_failed`
- `present` -> `verification_passed`
- `verification_passed` -> `revoked_key`
- `verification_passed` -> `expired_key`
- `verification_passed` -> `policy_mismatch`

Rules:

- transition to `verification_passed` is not approval
- transition failure is review evidence only
- a status transition must not trigger the next gate

### Verification status model

Verifier output status values: `empty`, `valid`, `warning`, `invalid`.

Mapping:

- `empty` if the signature is not present and optional in the current
  design
- `valid` if all checks pass and no warnings exist
- `warning` if a reviewable mismatch or missing optional context exists
- `invalid` if the envelope/descriptor is malformed or a critical
  policy/path failure exists

Rules:

- a `valid` `verification_status` is not approval
- an `invalid` `verification_status` must not trigger rollback/execution

### Failure taxonomy mapping

Failure types: `signature_missing`, `signature_malformed`,
`unsupported_algorithm`, `signed_payload_hash_mismatch`,
`bundle_hash_mismatch`, `manifest_hash_mismatch`, `key_not_found`,
`key_revoked`, `key_expired`, `key_status_unknown`,
`signing_policy_mismatch`, `signer_identity_unverified`,
`signature_verification_failed`, `signature_replay_suspected`,
`signature_metadata_incomplete`.

Severity values: `info`, `warning`, `critical`.

Reviewer action values: `no_action_required`, `manual_review_required`,
`reject_signature_until_resolved`.

Incident classification values: `none`, `signature_not_available`,
`signature_integrity_failure`, `key_lifecycle_review_required`,
`policy_review_required`, `signer_identity_review_required`,
`replay_review_required`.

Mapping (failure type -> severity / reviewer_action / incident_classification):

| failure type | severity | reviewer_action | incident_classification |
| --- | --- | --- | --- |
| `signature_missing` | `info` | `no_action_required` | `signature_not_available` |
| `signature_malformed` | `critical` | `reject_signature_until_resolved` | `signature_integrity_failure` |
| `unsupported_algorithm` | `critical` | `reject_signature_until_resolved` | `policy_review_required` |
| `signed_payload_hash_mismatch` | `critical` | `reject_signature_until_resolved` | `signature_integrity_failure` |
| `bundle_hash_mismatch` | `critical` | `reject_signature_until_resolved` | `signature_integrity_failure` |
| `manifest_hash_mismatch` | `critical` | `reject_signature_until_resolved` | `signature_integrity_failure` |
| `key_not_found` | `warning` | `manual_review_required` | `key_lifecycle_review_required` |
| `key_revoked` | `critical` | `reject_signature_until_resolved` | `key_lifecycle_review_required` |
| `key_expired` | `warning` | `manual_review_required` | `key_lifecycle_review_required` |
| `key_status_unknown` | `warning` | `manual_review_required` | `key_lifecycle_review_required` |
| `signing_policy_mismatch` | `warning` | `manual_review_required` | `policy_review_required` |
| `signer_identity_unverified` | `warning` | `manual_review_required` | `signer_identity_review_required` |
| `signature_verification_failed` | `critical` | `reject_signature_until_resolved` | `signature_integrity_failure` |
| `signature_replay_suspected` | `critical` | `reject_signature_until_resolved` | `replay_review_required` |
| `signature_metadata_incomplete` | `warning` | `manual_review_required` | `policy_review_required` |

### Reviewer action mapping

- `no_action_required` for an absent optional signature in design-only/
  current local mode
- `manual_review_required` for mismatches, an unknown signer, an unknown
  key status, or a policy mismatch
- `reject_signature_until_resolved` for a malformed signature, an
  unsupported algorithm, a revoked/expired key, or a verification failure

Rules:

- reviewer action is guidance only
- reviewer action is not approval
- reviewer action must not execute a primitive
- reviewer action must not trigger the wrapper
- reviewer action must not trigger the next gate

### Verification report schema

Future report top-level fields: `phase8j_status`,
`signature_verifier_runtime_status`, `signing_implementation_status`,
`signature_verification_status`, `signature_status`,
`verification_status`, `signature_schema_version`,
`signed_payload_sha256`, `computed_signed_payload_sha256`,
`bundle_hash_status`, `manifest_hash_status`, `key_status`,
`revocation_status`, `rotation_status`, `signer_identity_assurance`,
`failure_count`, `severity_counts`, `incident_classification`,
`reviewer_action`, `reviewer_action_required`,
`approval_boundary_statement`, `issues`, `safety_statement`,
`limitations`.

Rules:

- the report schema is future design only
- the report schema must be deterministic in a future implementation
- the report schema must not contain private keys
- the report schema must not contain secrets
- the report schema must not contain approval flags

### Approval boundary

- a signature verifier result is not approval
- a verified signature is not approval
- a signed export is not approval
- signer metadata is not approval
- signature verification is not primitive execution
- signature verification must not bypass the selected-gate manual
  approval boundary
- signature verification must not trigger wrapper execution
- signature verification must not trigger next gate
- signature verification must not set or imply approval flags
- reviewer action remains review guidance only
- a signature verification report is evidence only, not approval
- approval remains the Phase 7D selected-gate manual boundary

### Non-repudiation limitation

- without authenticated identity, strong non-repudiation is not available
- without governed key custody, strong non-repudiation is not available
- without a revocation/rotation process, signature trust is incomplete
- a local-only signature verifier would provide tamper-evidence, not
  enterprise non-repudiation
- signature verification must not be overclaimed

### Privacy and secret handling

- no private keys in the repository
- no private keys in the export pack
- no secrets in the descriptor, envelope, or report
- no approval flags in the descriptor, envelope, or report
- no API keys
- no affiliate secrets
- no raw terminal dump if it contains secrets
- signer metadata should avoid unnecessary personal data
- verification logs/screenshots must be sanitized

### Non-goals

Phase 8J does not:

- implement signature verifier runtime
- implement signing
- generate keys
- handle private keys
- implement encryption
- implement KMS/Secrets Manager
- implement backend/API/database
- modify Phase 8G/8H verifier runtime behavior
- modify Phase 8E export behavior
- modify Phase 7D wrapper behavior
- execute primitives
- approve anything
- trigger the next gate
- add chain execution
- create a production deployment

### Phase 8I design boundary

- Phase 8I remains the signature design source for the descriptor,
  envelope, and key lifecycle
- Phase 8J designs verifier-side interpretation
- Phase 8J does not change Phase 8I files except an additive pointer
- Phase 8J does not implement runtime

### Phase 8H verifier boundary

- Phase 8H remains the hash-only export integrity verifier
- Phase 8J does not change Phase 8H runtime
- a future signature verifier depends on the Phase 8H report schema
- Phase 8H reviewer action remains review guidance only

### Phase 8E export boundary

- the Phase 8E export pack remains read-only packaging
- Phase 8J does not change Phase 8E runtime
- a future signature verifier must not mutate export evidence
- a future signature envelope must stay separate from the export manifest

### Phase 7D approval boundary

- approval remains the Phase 7D selected-gate manual boundary
- signature verification must not call the Phase 7D wrapper
- signature verification must not call primitives
- signature verification must not write the vault
- signature verification must not trigger the next gate

### Future implementation path

- Phase 8K: Key Management Design
- Phase 8L: Local Detached Signature Prototype
- Phase 8M: Detached Signature Verifier Prototype
- Phase 8N: Signature Runbook / Incident Review Pack
- Phase 8O: Phase 8 Final Acceptance Pack

None of the above are implemented in Phase 8J.

### Major-phase checkpoint policy

Phase 8J is part of `feature/phase8-signature-governance-completion`. Phase
8J should create a checkpoint commit only; no PR should be opened after
Phase 8J alone. The full suite is deferred to major Phase 8 completion
unless focused tests fail or protected runtime changes occur. Focused tests
must pass before moving to Phase 8K.

### Known limitations

- design only
- no signature verifier runtime
- no signing implementation
- no key management
- no encryption
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
