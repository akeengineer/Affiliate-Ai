# Phase 8I — Detached Signature Design Finalization

```text
phase8i_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: detached_signature_design_finalized
signing_implementation_status: design_only
signature_runtime_status: not_implemented
```

### Purpose

Phase 8I finalizes detached signature governance for future export-pack
signing: a signed payload descriptor, a detached signature envelope schema,
signer/key metadata models, a signature algorithm policy, a signing policy
version model, key lifecycle/rotation/revocation policy, a verification
ceremony, a signature failure taxonomy, and a signing event audit trail
model. Phase 8I does not implement signing or signature verification.

### Scope

- docs/tests design-only
- no signing implementation
- no signature verifier implementation
- no detached signature runtime implementation
- no key generation
- no private key handling
- no encryption implementation
- no KMS/Secrets Manager implementation
- no backend/API/database
- no runtime script
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Current trust boundary

- Phase 8E creates export packs
- Phase 8G/8H verify hash-only integrity
- Phase 8H reviewer action is review guidance only
- no signing runtime exists
- no authenticated operator identity exists
- no non-repudiation exists
- detached signature design must not turn evidence into approval
- durable audit remains a local/tmp workflow

### Design objectives

Detached signature governance must eventually support:

- signed payload descriptor
- detached signature envelope
- `bundle_hash` signing target
- `manifest_hash` reference
- report schema version reference
- signer metadata
- key identifier
- signature algorithm policy
- signing policy version
- signing timestamp
- key lifecycle controls
- rotation policy
- revocation policy
- verification ceremony
- failure taxonomy
- signing event audit trail
- an explicit approval boundary

### Signed payload descriptor model

The canonical signed payload descriptor contains:

- `payload_schema_version`
- `export_manifest_path`
- `export_manifest_sha256`
- `bundle_hash`
- `computed_manifest_hash`
- `report_schema_version`
- `issue_taxonomy_version`
- `compatibility_matrix_version`
- `verifier_hardening_status`
- `verification_status`
- `compatibility_result`
- `incident_classification`
- `reviewer_action`
- `reviewer_action_required`
- `generated_from_phase`
- `generated_by_tool`
- `created_at_utc`

Rules:

- the payload descriptor must be canonical JSON (`sort_keys=True`,
  `separators=(",", ":")`, `ensure_ascii=False`), matching the convention
  already used by Phase 8B/8C/8D/8E/8G/8H
- the payload descriptor must use deterministic field ordering
- the payload descriptor must not include private key material
- the payload descriptor must not include secrets
- the payload descriptor must not include approval flags
- the payload descriptor is evidence only
- the payload descriptor is not approval

### Detached signature envelope schema

Future detached signature envelope fields:

- `signature_schema_version`
- `signed_payload_sha256`
- `signed_payload_descriptor_path`
- `detached_signature_path`
- `signature_algorithm`
- `signature_encoding`
- `key_id`
- `signer_id`
- `signer_role`
- `signer_identity_assurance`
- `signing_policy_version`
- `signing_timestamp_utc`
- `signature_status`
- `verification_status`
- `revocation_status`
- `rotation_epoch`
- `approval_boundary_statement`

Allowed future `signature_status` values: `not_present`, `present`,
`malformed`, `unsupported_algorithm`, `key_not_found`,
`verification_failed`, `verification_passed`, `revoked_key`,
`expired_key`, `policy_mismatch`.

Rules:

- the signature envelope must be stored separately from the export
  manifest
- the signature envelope must not mutate source evidence
- the signature envelope must not trigger approval
- the signature envelope must not trigger the wrapper
- the signature envelope must not trigger the next gate

This section describes the envelope's required shape and properties only;
it includes no signing command examples or executable code.

### Signing target model

- the preferred signing target is the signed payload descriptor's hash
  (`signed_payload_sha256`), not the raw evidence bytes
- the signed payload descriptor should reference `bundle_hash` and
  `computed_manifest_hash`
- the signing target must be stable and deterministic
- the signing target must not include volatile timestamps except the
  explicit `created_at_utc` field already inside the canonical payload
- the signing target must not include private key material
- the signing target is not approval

### Bundle hash signing model

- `bundle_hash` (from Phase 8G/8H) remains a hash-only evidence integrity
  anchor
- a future signature should sign a descriptor that includes `bundle_hash`
- a `bundle_hash` mismatch invalidates signing eligibility
- a `bundle_hash` mismatch requires manual review
- a future implementation must reject signing (or flag as untrusted) a
  signature produced over a mismatched bundle
- `bundle_hash` does not approve anything

### Signer metadata model

Fields: `signer_id`, `signer_role`, `signer_identity_assurance`,
`signer_contact_reference`, `signer_org_unit`,
`signer_approval_authority_claim`.

Rules:

- signer metadata must avoid sensitive personal data where possible
- signer metadata is not a substitute for authenticated identity
- `signer_approval_authority_claim` is descriptive only until an identity/
  authorization system is implemented
- signer metadata must not be treated as approval

### Key identifier model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_owner`,
`key_purpose`, `key_scope`, `key_created_at`, `key_expires_at`,
`key_status`.

Allowed `key_status` values: `active`, `retired`, `revoked`, `expired`,
`unknown`.

Rules:

- private keys must never be committed
- private keys must never be placed in tmp export packs
- private keys must never be written to docs
- key identifiers are metadata only
- key identifiers are not proof of signer identity without verification

### Signature algorithm policy

Design-only algorithm policy fields: `supported_algorithm_policy_version`,
`allowed_algorithms`, `disallowed_algorithms`, `minimum_key_strength`,
`hash_algorithm`, `signature_encoding`.

Rules:

- Phase 8I does not select a final production algorithm
- Phase 8I may recommend future local prototype algorithm categories only,
  by conceptual name, without any executable command
- no executable algorithm commands are included
- a disallowed weak algorithm encountered in a future implementation must
  require manual review

### Signing policy version model

Fields: `signing_policy_version`, `policy_effective_at`, `policy_owner`,
`allowed_signer_roles`, `required_identity_assurance`,
`required_verifier_schema_version`, `required_manifest_schema_version`,
`required_bundle_hash_presence`, `approval_boundary_statement`.

Rules:

- the signing policy controls signature eligibility
- the signing policy does not authorize approval execution
- a signing policy mismatch requires manual review

### Key lifecycle model

Lifecycle states: `proposed`, `active`, `rotating`, `retired`, `revoked`,
`expired`.

Rules:

- key lifecycle must be governed before any implementation
- rotation and revocation must be auditable
- lost key handling requires incident review
- compromised key handling requires incident review
- a key lifecycle event does not trigger approval

### Rotation policy

Fields: rotation trigger, rotation cadence, rotation owner, overlap
window, previous key validation policy, migration handling, stale
signature handling.

Rules:

- rotation must not invalidate historical evidence automatically
- rotation must not trigger re-signing automatically without manual review

### Revocation policy

Fields: revocation trigger, revocation authority, revocation effective
time, affected signature review, historical evidence treatment, emergency
revocation path, manual review requirements.

Rules:

- revoked key signatures require manual review
- revocation must not delete evidence
- revocation must not trigger rollback/execution

### Verification ceremony

Future ceremony:

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

### Signature failure taxonomy

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

### Signing event audit trail model

Future audit trail fields: `signing_event_id`, `signature_schema_version`,
`signed_payload_sha256`, `bundle_hash`, `manifest_hash`, `key_id`,
`signer_id`, `signer_role`, `signing_policy_version`,
`signing_timestamp_utc`, `signature_status`, `verification_status`,
`reviewer_action`, `approval_boundary_statement`.

Rules:

- the signing event audit trail is evidence only
- the signing event audit trail must not execute a primitive
- the signing event audit trail must not trigger the wrapper
- the signing event audit trail must not mutate the Phase 8B audit store
  unless a future append-only design explicitly allows it
- the signing event audit trail must not be stored in the vault by Phase
  8I

### Non-repudiation limitation

- without authenticated identity, strong non-repudiation is not available
- without governed key custody, strong non-repudiation is not available
- without a revocation/rotation process, signature trust is incomplete
- a local-only signature prototype would provide tamper-evidence, not
  enterprise non-repudiation
- signature strength must not be overclaimed

### Privacy and secret handling

- no private keys in the repository
- no private keys in the export pack
- no secrets in the payload descriptor
- no approval flags in the payload descriptor
- no API keys
- no affiliate secrets
- no raw terminal dump if it contains secrets
- signer metadata should avoid unnecessary personal data
- signing logs/screenshots must be sanitized

### Non-goals

Phase 8I does not:

- implement signing
- implement a signature verification script
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

### Phase 8H verifier boundary

- Phase 8H remains hash-only
- Phase 8I does not change Phase 8H runtime
- a future signature design depends on the Phase 8H report schema
  (`report_schema_version`, `bundle_hash`, `computed_manifest_hash`,
  `incident_classification`, `reviewer_action`)
- Phase 8H reviewer action remains review guidance only

### Phase 8E export boundary

- the Phase 8E export pack remains read-only packaging
- Phase 8I does not change Phase 8E runtime
- a future signature must not mutate export evidence
- a future signature envelope must be stored separately from the export
  manifest

### Phase 7D approval boundary

- a signature is not approval
- a verified signature is not approval
- a signed export is not approval
- signer metadata is not approval
- reviewer action is not approval
- signing must not bypass the selected-gate manual approval boundary
- signing must not set approval flags
- signing must not trigger the wrapper
- signing must not trigger the next gate
- approval remains the Phase 7D selected-gate manual boundary

### Future implementation path

- Phase 8J: Detached Signature Verifier Design
  ([`PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`](PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md)
  now exists; it designs verifier-side interpretation only, does not
  implement verifier runtime, and a verified signature remains not
  approval)
- Phase 8K: Local Detached Signature Prototype, still local-only and no
  approval integration
- Phase 8L: Key Management Design
- Phase 8M: Revocation/Rotation Runbook
- Phase 8N: Optional Enterprise KMS Integration Design

None of the above are implemented in Phase 8I.

Phase 8K Key Management Design now exists at
`docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`; it refines key lifecycle,
custody, rotation, revocation, and signer-to-key binding governance, and
it remains design-only.

### Known limitations

- design only
- no signing implementation
- no signature verifier implementation
- no key management
- no encryption
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
