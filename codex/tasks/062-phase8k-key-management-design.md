# Task 062 — Phase 8K Key Management Design

phase8k_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: key_management_design

signing_implementation_status: design_only

signature_runtime_status: not_implemented

signature_verifier_runtime_status: not_implemented

key_management_runtime_status: not_implemented

major_phase_branch_workflow: enabled

## Purpose

Phase 8K designs key management governance for future detached-signature
workflows: key governance roles, a key metadata model, a key custody
model, a key lifecycle model, key creation/activation/rotation/
revocation/retirement/compromise policy, key storage options considered,
a key access control model, a key audit trail model, a signer-to-key
binding model, a key policy version model, compatibility with the
Phase 8I signature envelope and the Phase 8J verifier design, a failure
taxonomy mapping, and a reviewer action mapping. Phase 8K does not
implement key management runtime, key generation, signing, or signature
verification.

## Scope

- docs/tests design-only
- no key management implementation
- no key generation
- no private key handling
- no public key runtime handling beyond design references
- no key file creation
- no certificate file creation
- no signing implementation
- no signature verifier implementation
- no detached signature runtime implementation
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

## Files

- `codex/tasks/062-phase8k-key-management-design.md`
- `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- `tests/test_phase8k_key_management_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`
- additive updates to `docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`
- additive updates to `docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`

## Status model

- `phase8k_status: success` — the key management design exists, additive
  documentation pointers exist, and protected runtime files stay
  unchanged.
- `phase7d_runtime_readiness: implemented_manual_gate` — the Phase 7D
  single-gate manual approval wrapper remains the only implemented
  approval runtime; Phase 8K does not change it.
- `durable_audit_store_status: key_management_design` — the durable audit
  store status token advances to reflect that a key management design now
  exists.
- `signing_implementation_status: design_only` — no signing implementation
  exists anywhere in the repository.
- `signature_runtime_status: not_implemented` — no detached signature
  runtime exists.
- `signature_verifier_runtime_status: not_implemented` — no signature
  verifier runtime exists.
- `key_management_runtime_status: not_implemented` — no key management
  runtime exists; this phase is design only.
- `major_phase_branch_workflow: enabled` — Phase 8K follows the
  major-phase checkpoint-commit-only workflow; no PR is opened for this
  sub-phase alone.

## Key management design objective

Provide a complete, implementation-ready design for future key
governance over the Phase 8I signature envelope and the Phase 8J
verifier design, so a later phase can implement key management against a
stable governance model, without implementing any key generation,
signing, verification, or storage code in this phase.

## Current key trust boundary

- Phase 8I finalized detached signature design
- Phase 8J designs detached signature verifier interpretation
- no signing runtime exists
- no signature verifier runtime exists
- no key management runtime exists
- no authenticated operator identity exists
- no governed key custody exists
- no enterprise non-repudiation exists
- key metadata design must not turn signature evidence into approval
- durable audit remains a local/tmp workflow

## Key governance roles

Design-only governance roles: `key_owner`, `key_custodian`, `signer`,
`reviewer`, `security_owner`, `system_owner`,
`emergency_revocation_authority`. Roles are governance design only; roles
do not grant runtime permissions in Phase 8K; role assignment is not
approval; the `signer` role is not approval; the `reviewer` role remains
review guidance only until identity/RBAC phases.

## Key metadata model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_algorithm_family`,
`key_purpose`, `key_scope`, `key_owner`, `key_custodian`,
`key_created_at_utc`, `key_activated_at_utc`, `key_expires_at_utc`,
`key_rotated_at_utc`, `key_revoked_at_utc`, `key_status`,
`key_status_reason`, `signing_policy_version`, `rotation_epoch`,
`revocation_reference`, `approval_boundary_statement`. Allowed
`key_status` values: `proposed`, `active`, `rotating`, `retired`,
`revoked`, `expired`, `compromised`, `unknown`. Key metadata must not
include private key material or secrets, is not proof of signer identity
without identity assurance, and is not approval.

## Key custody model

Design-only custody models: `local_offline_key`, `os_keychain`,
`hardware_security_key`, `cloud_kms`, `enterprise_secrets_manager`, each
compared for strengths, weaknesses, operational fit, risk profile,
recommended phase, and implementation status. Phase 8K implements none of
these options; no provider-specific commands, key-generation commands, or
private key storage examples are included.

## Key lifecycle model

Lifecycle states: `proposed`, `active`, `rotating`, `retired`, `revoked`,
`expired`, `compromised`, `unknown`. Allowed transitions: proposed ->
active; active -> rotating; rotating -> active; active -> retired; active
-> revoked; active -> expired; active -> compromised; rotating ->
revoked; retired -> revoked; expired -> revoked; compromised -> revoked;
unknown -> manual_review_required. A lifecycle state change is governance
metadata only and must not trigger approval, the wrapper, or the next
gate.

## Key creation policy

Fields: `creation_request_id`, `requested_by`, `request_reason`,
`key_purpose`, `key_scope`, `key_owner`, `key_custodian`,
`approval_boundary_statement`, `minimum_review_requirements`. Phase 8K
does not create keys; a creation request is not key generation; creation
approval is not Phase 7D product approval; key creation must be
separately governed before runtime.

## Key activation policy

Activation prerequisites, an identity assurance prerequisite, a
signer-role prerequisite, a policy-version prerequisite, a reviewer
prerequisite, and an activation audit trail requirement. An active key
does not approve an export; an active key only means eligible for a
future signature flow.

## Key rotation policy

Fields: `rotation_trigger`, `rotation_cadence`, `rotation_owner`,
`overlap_window`, `previous_key_validation_policy`,
`stale_signature_policy`, `historical_signature_policy`,
`rotation_audit_event`. Rotation must not delete historical evidence,
must not automatically re-sign historical exports, and must not trigger
the wrapper or execution.

## Key revocation policy

Fields: `revocation_trigger`, `revocation_authority`,
`revocation_effective_at_utc`, `revocation_reason`,
`affected_signature_review`, `historical_evidence_treatment`,
`emergency_revocation_path`, `revocation_audit_event`. Revoked key
signatures require manual review or rejection until resolved; revocation
must not delete evidence, trigger rollback, or trigger primitive
execution.

## Key retirement policy

Fields: `retirement_trigger`, `retirement_owner`,
`retirement_effective_at_utc`, `historical_validation_policy`, an
archival requirement, and a retirement audit event. A retired key may
remain valid for historical verification depending on policy; retirement
must not erase evidence.

## Key compromise policy

Fields: `compromise_detection_source`, `compromise_severity`, an
emergency revocation reference, `affected_signature_scope`,
`incident_review_owner`, containment steps, and evidence preservation
requirements. `compromised` key status requires manual review; compromise
must not delete evidence, trigger automatic rollback/execution, or
auto-revoke without a governed policy in a future implementation.

## Key storage options considered

Comparison of local offline key, OS keychain, hardware security key,
cloud KMS, and enterprise secrets manager storage across strengths,
weaknesses, operational fit, security posture, implementation complexity,
and recommended phase. Phase 8K is design only and implements no storage
option; no commands or provider-specific URLs are included.

## Key access control model

Design-only permissions: `key_read_metadata_permission`,
`key_sign_permission`, `key_rotate_permission`, `key_revoke_permission`,
`key_retire_permission`, `key_review_permission`,
`emergency_revoke_permission`. Permissions are design-only and require
future identity/RBAC work; `key_sign_permission` does not approve product
decisions; `key_revoke_permission` does not delete evidence.

## Key audit trail model

Future audit fields: `key_event_id`, `key_id`, `key_version`,
`key_event_type`, `key_status_before`, `key_status_after`, `actor_id`,
`actor_role`, `reason`, `policy_version`, `event_timestamp_utc`,
`evidence_reference`, `approval_boundary_statement`. Allowed
`key_event_type` values: `key_creation_requested`, `key_activated`,
`key_rotated`, `key_retired`, `key_revoked`, `key_expired`,
`key_compromise_reported`, `key_metadata_reviewed`. The key audit trail
is evidence only; it must not execute a primitive, trigger the wrapper,
or write the vault in Phase 8K; a future append-only storage design must
be designed separately.

## Signer-to-key binding model

Fields: `signer_id`, `signer_role`, `signer_identity_assurance`,
`key_id`, `key_version`, `binding_status`, `binding_created_at_utc`,
`binding_expires_at_utc`, `binding_policy_version`. Allowed
`binding_status` values: `proposed`, `active`, `suspended`, `revoked`,
`expired`, `unknown`. `binding_status` is not approval, does not prove
identity without identity assurance, and must not trigger the wrapper or
the next gate.

## Key policy version model

Fields: `key_policy_version`, `policy_effective_at_utc`, `policy_owner`,
`allowed_key_status_for_signing`, `allowed_signer_roles`,
`minimum_identity_assurance`, `allowed_storage_models`,
`rotation_requirement`, `revocation_requirement`,
`approval_boundary_statement`. Key policy controls signing eligibility
only, does not authorize approval execution, and a mismatch requires
manual review.

## Compatibility with Phase 8I signature envelope

Key management maps onto these Phase 8I envelope fields: `key_id`,
`signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `revocation_status`, `rotation_epoch`,
`approval_boundary_statement`. The mapping is design-only and does not
change the Phase 8I envelope schema or imply approval.

## Compatibility with Phase 8J verifier design

The verifier should interpret: `key_status`, `key_status_reason`,
`key_fingerprint`, `key_version`, signer-to-key binding,
`revocation_reference`, `rotation_epoch`, `key_policy_version`. Verifier
interpretation is evidence only and is not approval.

## Failure taxonomy mapping

Failure types: `key_metadata_missing`, `key_status_unknown`,
`key_not_active`, `key_revoked`, `key_expired`, `key_retired`,
`key_compromised`, `key_policy_mismatch`, `key_owner_missing`,
`key_custodian_missing`, `key_fingerprint_missing`,
`signer_binding_missing`, `signer_binding_revoked`,
`rotation_epoch_stale`, `revocation_reference_missing`,
`identity_assurance_insufficient`. Severity values: `info`, `warning`,
`critical`. Incident classification values: `none`,
`key_metadata_review_required`, `key_lifecycle_review_required`,
`key_compromise_review_required`, `signer_binding_review_required`,
`policy_review_required`. Reviewer action values:
`no_action_required`, `manual_review_required`,
`reject_signature_until_resolved`. Every failure type maps to exactly one
severity, incident classification, and reviewer action, documented in
the design doc's mapping table.

## Reviewer action mapping

`no_action_required` only for valid active key metadata with sufficient
policy context; `manual_review_required` for unknown, missing, or stale
metadata; `reject_signature_until_resolved` for a revoked, expired, or
compromised key, or a revoked signer binding. Reviewer action is guidance
only, is not approval, and must not execute a primitive, trigger the
wrapper, or trigger the next gate.

## Approval boundary

Key metadata is not approval. An active key is not approval. A key owner
is not approval. A key custodian is not approval. A signer-to-key binding
is not approval. Key policy eligibility is not approval. A signature
created using an eligible key is not approval. Key management must not
bypass the selected-gate manual approval boundary, must not set approval
flags, must not trigger the wrapper, and must not trigger the next gate.
Approval remains the Phase 7D selected-gate manual boundary.

## Privacy and secret handling

No private keys in the repository, export pack, or docs; no secrets or
approval flags in key metadata; no API keys or affiliate secrets; no raw
terminal dump containing secrets; signer/key owner metadata should avoid
unnecessary personal data; key management logs/screenshots must be
sanitized.

## Non-goals

Phase 8K does not implement key management runtime, generate keys,
handle private keys, create key files, create certificate files,
implement signing, implement signature verification, implement
encryption, or implement KMS/Secrets Manager/backend/API/database. It
does not modify Phase 8G/8H verifier runtime behavior, Phase 8E export
behavior, or Phase 7D wrapper behavior, execute primitives, approve
anything, trigger the next gate, add chain execution, or create a
production deployment.

## Phase 8J verifier design boundary

Phase 8J remains detached signature verifier design; Phase 8K supplies
key governance interpretation, does not implement verifier runtime, and
does not modify Phase 8J files except an additive pointer.

## Phase 8I signature design boundary

Phase 8I remains the detached signature envelope/payload design source;
Phase 8K refines key governance for Phase 8I fields and does not
implement signing runtime.

## Phase 8H verifier boundary

Phase 8H remains the hash-only export integrity verifier; Phase 8K does
not change Phase 8H runtime; Phase 8H reviewer action remains review
guidance only.

## Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Key
management must not call the Phase 7D wrapper, must not call primitives,
must not write the vault, and must not trigger the next gate.

## Future implementation path

- Phase 8L: Local Detached Signature Prototype
- Phase 8M: Detached Signature Verifier Prototype
- Phase 8N: Signature Runbook / Incident Review Pack
- Phase 8O: Phase 8 Final Acceptance Pack
- Phase 9A: Operator Identity Boundary Design

None of the above are implemented in Phase 8K.

## Test strategy

Deterministic docs-contract tests in
`tests/test_phase8k_key_management_design.py` enforce: file existence for
the task and design doc; presence of all eight required status tokens;
presence of scope-safety tokens (no key-management/signing/verifier/
encryption/KMS/backend/API/database/wrapper/approval/primitive/vault/
next-gate/chain implementation); presence of every required design
section; field-name and enum coverage for governance roles, key metadata,
custody models, lifecycle states and transitions, access control, the
audit trail, signer-to-key binding, key policy version, the Phase 8I/8J
compatibility mappings, and the failure taxonomy; doc cross-reference
regression across ROADMAP/PROJECT_STATE/PHASE8J/PHASE8I/PHASE8F;
protected-runtime-file non-modification; and a static safety scan of the
two new Phase 8K files rejecting secrets, private-key material, and
executable command examples.

## Acceptance criteria

- task exists
- design doc exists
- design doc contains `phase8k_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains `durable_audit_store_status: key_management_design`
- design doc contains `signing_implementation_status: design_only`
- design doc contains `signature_runtime_status: not_implemented`
- design doc contains `signature_verifier_runtime_status: not_implemented`
- design doc contains `key_management_runtime_status: not_implemented`
- design doc contains `major_phase_branch_workflow: enabled`
- design doc states docs/tests design-only
- design doc states no key-management/signing/signature-verifier/
  key-generation/private-key-handling/encryption/KMS/Secrets-Manager
  implementation
- design doc states no Phase 8G/8H verifier behavior change
- design doc states no Phase 8E export behavior change
- design doc states no Phase 7D wrapper behavior change
- design doc states no primitive execution and no vault read/write
- ROADMAP, PROJECT_STATE, PHASE8J, PHASE8I, and PHASE8F all reference
  Phase 8K additively
- protected Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, and
  8B/8C/8D/8E/8G/8H runtime files remain unchanged
- no new runtime, signing, key, certificate, database, backend, API, or
  package.json file is added by Phase 8K

## Focused verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase8k_key_management_design.py
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
python -m pytest -q tests/test_phase8i_detached_signature_design_finalization.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
```

## Major-phase checkpoint policy

Phase 8K is part of `feature/phase8-signature-governance-completion`.
Phase 8K should create a checkpoint commit only; no PR should be opened
after Phase 8K alone. The full suite is deferred to major Phase 8
completion unless focused tests fail or protected runtime changes occur.
Focused tests must pass before moving to Phase 8L.

## Known limitations

Phase 8K is design only. No key management runtime, key generation,
signing, or signature verifier implementation exists. No encryption, no
authenticated operator identity, no governed key custody implementation,
no non-repudiation, no backend/API/database, and no production
deployment exist.

## Final status target

phase8k_status: success
