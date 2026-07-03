# Phase 8L — Local Detached Signature Prototype

```text
phase8l_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: local_detached_signature_prototype
signing_implementation_status: prototype_local_only
signature_runtime_status: local_prototype
signature_verifier_runtime_status: not_implemented
key_management_runtime_status: not_implemented
major_phase_branch_workflow: enabled
```

### Purpose

Phase 8L implements a local-only detached signature prototype for Phase 8E
export packs. It reads a Phase 8E export manifest (and optionally a Phase
8G/8H integrity verification report), builds a canonical signed payload
descriptor, and — only when an in-memory prototype key is present — produces
a local HMAC-SHA256 prototype detached signature. This is prototype-only
tooling; it is NOT production non-repudiation and it is NOT approval.

### Scope

- local-only detached signature prototype
- signed payload descriptor generation
- detached signature envelope generation
- HMAC-SHA256 prototype signature only
- no committed private keys
- no key generation
- no KMS/Secrets Manager
- no backend/API/database
- no signature verifier implementation
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Runtime command

`bash scripts/dev/run_phase8l_detached_signature.sh [signature options]`
forwards its arguments to
`scripts/dev/build_phase8l_detached_signature.py`. It includes no approval
flags and no `--execute`.

### Prototype key handling

- env var `AFFILIATE_PHASE8L_PROTOTYPE_KEY` used only in memory
- raw key never written to outputs
- raw key never logged
- no key files created
- no private key material committed
- missing env var skips signing with `not_ready` status
- this prototype key model is not production-grade key management

### Signed payload descriptor

Fields: `payload_schema_version` (`phase8l.signed_payload_descriptor.v1`),
`export_manifest_path`, `export_manifest_sha256`, `bundle_hash`,
`computed_manifest_hash`, `report_schema_version`, `issue_taxonomy_version`,
`compatibility_matrix_version`, `verifier_hardening_status`,
`verification_status`, `compatibility_result`, `incident_classification`,
`reviewer_action`, `reviewer_action_required`, `generated_from_phase`
(`phase8l`), `generated_by_tool` (`build_phase8l_detached_signature.py`),
`created_at_utc`, `signing_policy_version`, `signer_id`, `signer_role`,
`signer_identity_assurance`, `key_id`, `key_version`,
`approval_boundary_statement`.

### Detached signature envelope

Fields: `signature_schema_version`
(`phase8l.detached_signature_envelope.v1`), `signed_payload_sha256`,
`signed_payload_descriptor_path`, `detached_signature_path`,
`signature_algorithm` (`hmac-sha256-prototype`), `signature_encoding`
(`hex`), `key_id`, `key_version`, `signer_id`, `signer_role`,
`signer_identity_assurance`, `signing_policy_version`,
`signing_timestamp_utc`, `signature_status`, `signing_status`,
`verification_status` (`not_verified`), `revocation_status`
(`not_checked`), `rotation_epoch` (`prototype`),
`approval_boundary_statement`, `signature_runtime_status`
(`local_prototype`), `signing_implementation_status`
(`prototype_local_only`), `detached_signature_value` (the HMAC hex digest
when signed, else `null`).

### Output layout

All outputs are written only under `tmp/phase8l-detached-signature/`:

- `signed-payload-descriptor.json`
- `detached-signature-envelope.json`
- `detached-signature-summary.json`
- `detached-signature-summary.md`

`detached-signature.sig` is additionally written only when a prototype
signature is produced (that is, when the prototype key env var is set).

### Safety boundary

- signature is not approval
- signed export is not approval
- local prototype signature is not approval
- active/prototype key is not approval
- signer metadata is not approval
- signing output is evidence only
- signature generation does not execute primitive
- signature generation does not call wrapper
- signature generation does not call Phase 8B/8C/8D/8E/8G scripts
- signature generation does not trigger next gate
- signature generation does not set approval flags
- signature generation does not write vault
- signature generation writes only under tmp/phase8l-detached-signature

### Phase 8K key management boundary

Phase 8K is design-only. Phase 8L does not implement key management. Phase
8L uses an env-var prototype key only. `key_management_runtime_status`
remains `not_implemented`.

### Phase 8J verifier boundary

Phase 8J is design-only. Phase 8L does not implement a signature verifier.
`signature_verifier_runtime_status` remains `not_implemented`.

### Phase 8E export boundary

Phase 8L consumes the Phase 8E export manifest. Phase 8L does not modify
the Phase 8E export pack. Phase 8L does not call Phase 8E export
automatically.

### Phase 8G/8H verifier boundary

Phase 8L may read a Phase 8G/8H integrity report if provided. Phase 8L
does not modify the Phase 8G/8H verifier. Phase 8L does not call the
Phase 8G verifier automatically.

### Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Phase 8L does
not call the Phase 7D wrapper, does not call primitives, does not write the
vault, and does not trigger the next gate.

### Major-phase checkpoint policy

Phase 8L is part of `feature/phase8-signature-governance-completion`. Phase
8L should create a checkpoint commit only; no PR should be opened after
Phase 8L alone. Because Phase 8L adds runtime code, focused tests plus
Phase 8G-8K regressions and `py_compile`/`bash -n` are required. The full
suite is deferred to major Phase 8 completion unless focused tests fail or
protected runtime changes occur.

### Known limitations

- local prototype only
- HMAC-SHA256 prototype only
- no production signing
- no signature verifier runtime
- no key management runtime
- no governed key custody
- no encryption
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
