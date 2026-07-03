# Phase 8M — Detached Signature Verifier Prototype

```text
phase8m_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: detached_signature_verifier_prototype
signing_implementation_status: prototype_local_only
signature_runtime_status: local_prototype
signature_verifier_runtime_status: local_prototype
key_management_runtime_status: not_implemented
major_phase_branch_workflow: enabled
```

### Purpose

Phase 8M implements a local-only detached signature verifier prototype for
Phase 8L outputs. It reads a Phase 8L signed payload descriptor and
detached signature envelope (and optionally the Phase 8L summary),
recomputes the signed payload hash, validates descriptor/envelope schema,
and — only when the in-memory prototype key is present — verifies the
HMAC-SHA256 prototype signature. This is prototype-only tooling; it is NOT
a production signature verifier and it is NOT approval.

### Scope

- local-only detached signature verifier prototype
- signed payload descriptor hash verification
- HMAC-SHA256 prototype signature verification only
- descriptor/envelope schema checks
- deterministic verification report
- no signing
- no committed private keys
- no key generation
- no KMS/Secrets Manager
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Runtime command

`bash scripts/dev/run_phase8m_detached_signature_verifier.sh [verification
options]` forwards its arguments to
`scripts/dev/verify_phase8m_detached_signature.py`. It includes no
approval flags and no `--execute`.

### Verification input contract

`scripts/dev/verify_phase8m_detached_signature.py` accepts
`--descriptor-path`, `--envelope-path`, `--summary-path`, and
`--output-dir`. Defaults: descriptor-path
`tmp/phase8l-detached-signature/signed-payload-descriptor.json`;
envelope-path
`tmp/phase8l-detached-signature/detached-signature-envelope.json`;
summary-path
`tmp/phase8l-detached-signature/detached-signature-summary.json`;
output-dir `tmp/phase8m-detached-signature-verifier`. The summary path is
optional context only; a missing or invalid summary never fails
verification. The prototype key is read only from the
`AFFILIATE_PHASE8L_PROTOTYPE_KEY` environment variable; when it is unset,
cryptographic verification is skipped with a warning rather than failing.

### Prototype key handling

- env var `AFFILIATE_PHASE8L_PROTOTYPE_KEY` used only in memory
- raw key never written to outputs
- raw key never logged
- no key files created
- no private key material committed
- missing env var skips cryptographic verification with warning
- this prototype key model is not production-grade key management

### Descriptor validation

The descriptor must be a JSON object containing all 24 required fields:
`payload_schema_version`, `export_manifest_path`, `export_manifest_sha256`,
`bundle_hash`, `computed_manifest_hash`, `report_schema_version`,
`issue_taxonomy_version`, `compatibility_matrix_version`,
`verifier_hardening_status`, `verification_status`, `compatibility_result`,
`incident_classification`, `reviewer_action`, `reviewer_action_required`,
`generated_from_phase`, `generated_by_tool`, `created_at_utc`,
`signing_policy_version`, `signer_id`, `signer_role`,
`signer_identity_assurance`, `key_id`, `key_version`,
`approval_boundary_statement`. A missing field raises a
`missing_descriptor_field` issue and fails schema validation.

### Envelope validation

The envelope must be a JSON object containing all 21 required fields:
`signature_schema_version`, `signed_payload_sha256`,
`signed_payload_descriptor_path`, `detached_signature_path`,
`signature_algorithm`, `signature_encoding`, `key_id`, `key_version`,
`signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `signing_timestamp_utc`, `signature_status`,
`signing_status`, `verification_status`, `revocation_status`,
`rotation_epoch`, `approval_boundary_statement`,
`signature_runtime_status`, `signing_implementation_status`. A missing
field raises a `missing_envelope_field` issue and fails schema validation.

### Signed payload hash verification

The verifier recomputes `computed_signed_payload_sha256` as the SHA-256
hex digest of the canonical JSON serialization of the descriptor
(`sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`) and
compares it to the envelope's `signed_payload_sha256`. A match sets
`signed_payload_hash_status: match`; a mismatch sets
`signed_payload_hash_status: mismatch`, fails verification with
`signature_verification_status: failed_signed_payload_hash_mismatch`, and
classifies the incident as `signature_integrity_failure`. A hash match is
necessary but is NOT approval.

### Prototype HMAC verification

Only `hmac-sha256-prototype` (`signature_algorithm`) and `hex`
(`signature_encoding`) are supported; any other value fails verification
as `failed_unsupported_algorithm` or `failed_unsupported_encoding`. When
the prototype key env var is missing, verification is skipped with
`skipped_missing_prototype_key` and a warning. When the envelope reports
`signature_status: not_ready` or `signing_status:
skipped_missing_prototype_key`, verification is skipped as
`skipped_signature_not_ready`. When the expected HMAC-SHA256 (computed
over the envelope's `signed_payload_sha256` using the in-memory prototype
key, via `hmac.compare_digest`) matches `detached_signature_value`,
verification succeeds as `verified_local_prototype`. A mismatch fails as
`failed_signature_mismatch`. Verification passed is NOT approval.

### Output layout

All outputs are written only under
`tmp/phase8m-detached-signature-verifier/`:

- `detached-signature-verification.json`
- `detached-signature-verification.md`

### Safety boundary

- verified signature is not approval
- verification passed is not approval
- signature verifier result is not approval
- valid verification_status is not approval
- signer metadata is not approval
- key metadata is not approval
- verification output is evidence only
- signature verification does not execute primitive
- does not call wrapper
- does not call Phase 8B/8C/8D/8E/8G/8L scripts
- does not trigger next gate
- does not set approval flags
- does not write vault
- writes only under tmp/phase8m-detached-signature-verifier

### Phase 8L signing prototype boundary

Phase 8M consumes Phase 8L descriptor/envelope outputs. Phase 8M does not
modify Phase 8L outputs. Phase 8M does not call the Phase 8L signing
script automatically. Phase 8M does not sign anything.

### Phase 8K key management boundary

Phase 8K is design-only. Phase 8M does not implement key management.
`key_management_runtime_status` remains `not_implemented`.

### Phase 8J verifier design boundary

Phase 8J is design source for verifier-side interpretation. Phase 8M is a
local-only prototype implementation of a narrow subset of that design.
Enterprise verification remains not implemented.

### Phase 8E export boundary

Phase 8M does not modify the Phase 8E export pack. Phase 8M does not call
Phase 8E export automatically.

### Phase 8G/8H verifier boundary

Phase 8M does not modify the Phase 8G/8H verifier. Phase 8M does not call
the Phase 8G verifier automatically.

### Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Phase 8M
does not call the Phase 7D wrapper, does not call primitives, does not
write the vault, and does not trigger the next gate.

Phase 8N Signature Runbook / Incident Review Pack now exists at
`docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`. Phase 8N
documents procedures for verifier outcomes, does not modify verifier
runtime, and incident review remains not approval.

### Major-phase checkpoint policy

Phase 8M is part of `feature/phase8-signature-governance-completion`.
Phase 8M should create a checkpoint commit only; no PR should be opened
after Phase 8M alone. Because Phase 8M adds runtime code, focused tests
plus Phase 8G-8L regressions and `py_compile`/`bash -n` are required. The
full suite is deferred to major Phase 8 completion unless focused tests
fail or protected runtime changes occur.

### Known limitations

- local prototype only
- HMAC-SHA256 prototype only
- no production signature verifier
- no production signing
- no key management runtime
- no governed key custody
- no encryption
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
