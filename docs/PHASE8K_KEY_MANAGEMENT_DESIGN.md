# Phase 8K — Key Management Design

```text
phase8k_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: key_management_design
signing_implementation_status: design_only
signature_runtime_status: not_implemented
signature_verifier_runtime_status: not_implemented
key_management_runtime_status: not_implemented
major_phase_branch_workflow: enabled
```

### Purpose

Phase 8K designs key management governance for future detached-signature
workflows: key governance roles, a key metadata model, a key custody model,
a key lifecycle model, key creation/activation/rotation/revocation/
retirement/compromise policy, key storage options considered, a key access
control model, a key audit trail model, a signer-to-key binding model, a
key policy version model, compatibility with the Phase 8I signature
envelope and the Phase 8J verifier design, a failure taxonomy mapping, and
a reviewer action mapping. Phase 8K does not implement key management
runtime, key generation, signing, or signature verification.

### Scope

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

### Current key trust boundary

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

### Key governance roles

Design-only governance roles: `key_owner`, `key_custodian`, `signer`,
`reviewer`, `security_owner`, `system_owner`,
`emergency_revocation_authority`.

Rules:

- roles are governance design only
- roles do not grant runtime permissions in Phase 8K
- role assignment is not approval
- the `signer` role is not approval
- the `reviewer` role remains review guidance only until identity/RBAC
  phases

### Key metadata model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_algorithm_family`,
`key_purpose`, `key_scope`, `key_owner`, `key_custodian`,
`key_created_at_utc`, `key_activated_at_utc`, `key_expires_at_utc`,
`key_rotated_at_utc`, `key_revoked_at_utc`, `key_status`,
`key_status_reason`, `signing_policy_version`, `rotation_epoch`,
`revocation_reference`, `approval_boundary_statement`.

Allowed `key_status` values: `proposed`, `active`, `rotating`, `retired`,
`revoked`, `expired`, `compromised`, `unknown`.

Rules:

- key metadata must not include private key material
- key metadata must not include secrets
- key metadata must not include approval flags
- key metadata is not proof of signer identity without identity assurance
- key metadata is not approval

### Key custody model

Design-only custody models: `local_offline_key`, `os_keychain`,
`hardware_security_key`, `cloud_kms`, `enterprise_secrets_manager`.

| custody model | strengths | weaknesses | operational fit | risk profile | recommended phase | implementation status |
| --- | --- | --- | --- | --- | --- | --- |
| `local_offline_key` | simple, no external dependency | weak operational security, easy to lose or leak | local prototype only | high | Phase 8L | not_implemented |
| `os_keychain` | OS-native protection, moderate convenience | platform-specific, no centralized governance | single-operator local use | medium-high | Phase 8L | not_implemented |
| `hardware_security_key` | strong key isolation, phishing-resistant | hardware dependency, provisioning overhead | individual signer custody | medium | Phase 8M or later | not_implemented |
| `cloud_kms` | centralized governance, audit-friendly | requires provider integration and identity work | team/enterprise custody | medium | Phase 9 or later | not_implemented |
| `enterprise_secrets_manager` | centralized secret lifecycle, access policy support | requires provider integration and identity work | team/enterprise custody | medium | Phase 9 or later | not_implemented |

Rules:

- Phase 8K implements none of these custody options
- no provider-specific commands are included
- no executable KMS/Secrets Manager examples are included
- no key-generation commands are included
- no private key storage examples are included

### Key lifecycle model

Lifecycle states: `proposed`, `active`, `rotating`, `retired`, `revoked`,
`expired`, `compromised`, `unknown`.

Allowed transitions:

- `proposed` -> `active`
- `active` -> `rotating`
- `rotating` -> `active`
- `active` -> `retired`
- `active` -> `revoked`
- `active` -> `expired`
- `active` -> `compromised`
- `rotating` -> `revoked`
- `retired` -> `revoked`
- `expired` -> `revoked`
- `compromised` -> `revoked`
- `unknown` -> `manual_review_required`

Rules:

- a lifecycle state change is governance metadata only
- a lifecycle state change must not trigger approval
- a lifecycle state change must not trigger the wrapper
- a lifecycle state change must not trigger the next gate

### Key creation policy

Fields: `creation_request_id`, `requested_by`, `request_reason`,
`key_purpose`, `key_scope`, `key_owner`, `key_custodian`,
`approval_boundary_statement`, `minimum_review_requirements`.

Rules:

- Phase 8K does not create keys
- a creation request is not key generation
- creation approval is not Phase 7D product approval
- key creation must be separately governed before runtime

### Key activation policy

Design fields and prerequisites: activation prerequisites, an identity
assurance prerequisite, a signer-role prerequisite, a policy-version
prerequisite, a reviewer prerequisite, and an activation audit trail
requirement.

Rules:

- an active key does not approve an export
- an active key only means eligible for a future signature flow

### Key rotation policy

Fields: `rotation_trigger`, `rotation_cadence`, `rotation_owner`,
`overlap_window`, `previous_key_validation_policy`,
`stale_signature_policy`, `historical_signature_policy`,
`rotation_audit_event`.

Rules:

- rotation must not delete historical evidence
- rotation must not automatically re-sign historical exports
- rotation must not trigger the wrapper or execution

### Key revocation policy

Fields: `revocation_trigger`, `revocation_authority`,
`revocation_effective_at_utc`, `revocation_reason`,
`affected_signature_review`, `historical_evidence_treatment`,
`emergency_revocation_path`, `revocation_audit_event`.

Rules:

- revoked key signatures require manual review or rejection of the
  signature until resolved
- revocation must not delete evidence
- revocation must not trigger rollback
- revocation must not trigger primitive execution

### Key retirement policy

Fields: `retirement_trigger`, `retirement_owner`,
`retirement_effective_at_utc`, `historical_validation_policy`, an
archival requirement, and a retirement audit event.

Rules:

- a retired key may remain valid for historical verification depending on
  policy
- retirement must not erase evidence

### Key compromise policy

Fields: `compromise_detection_source`, `compromise_severity`, an emergency
revocation reference, `affected_signature_scope`, `incident_review_owner`,
containment steps, and evidence preservation requirements.

Rules:

- `compromised` key status requires manual review
- compromise must not delete evidence
- compromise must not trigger automatic rollback or execution
- compromise must not auto-revoke without a governed policy in a future
  implementation

### Key storage options considered

Comparison of local offline key, OS keychain, hardware security key, cloud
KMS, and enterprise secrets manager storage:

| storage option | strengths | weaknesses | operational fit | security posture | implementation complexity | recommended phase |
| --- | --- | --- | --- | --- | --- | --- |
| local offline key | simplest option, no network dependency | weakest security posture, no centralized recovery | single-operator prototype | low | low | Phase 8L |
| OS keychain | native OS protection | not portable across machines, no team governance | single-operator local use | medium | low | Phase 8L |
| hardware security key | strong isolation, phishing-resistant | provisioning and recovery overhead | individual signer custody | high | medium | Phase 8M or later |
| cloud KMS | centralized governance and audit support | requires provider integration and identity work | team/enterprise custody | high | high | Phase 9 or later |
| enterprise secrets manager | centralized lifecycle and access policy | requires provider integration and identity work | team/enterprise custody | high | high | Phase 9 or later |

Rules:

- Phase 8K is design only and implements no storage option
- no commands are included
- no provider-specific URLs are included

### Key access control model

Design-only permissions: `key_read_metadata_permission`,
`key_sign_permission`, `key_rotate_permission`, `key_revoke_permission`,
`key_retire_permission`, `key_review_permission`,
`emergency_revoke_permission`.

Rules:

- permissions are design-only
- permissions require future identity/RBAC work
- `key_sign_permission` does not approve product decisions
- `key_revoke_permission` does not delete evidence

### Key audit trail model

Future audit fields: `key_event_id`, `key_id`, `key_version`,
`key_event_type`, `key_status_before`, `key_status_after`, `actor_id`,
`actor_role`, `reason`, `policy_version`, `event_timestamp_utc`,
`evidence_reference`, `approval_boundary_statement`.

Allowed `key_event_type` values: `key_creation_requested`,
`key_activated`, `key_rotated`, `key_retired`, `key_revoked`,
`key_expired`, `key_compromise_reported`, `key_metadata_reviewed`.

Rules:

- the key audit trail is evidence only
- the key audit trail must not execute a primitive
- the key audit trail must not trigger the wrapper
- the key audit trail must not write the vault in Phase 8K
- a future append-only storage design must be designed separately

### Signer-to-key binding model

Fields: `signer_id`, `signer_role`, `signer_identity_assurance`, `key_id`,
`key_version`, `binding_status`, `binding_created_at_utc`,
`binding_expires_at_utc`, `binding_policy_version`.

Allowed `binding_status` values: `proposed`, `active`, `suspended`,
`revoked`, `expired`, `unknown`.

Rules:

- `binding_status` is not approval
- `binding_status` does not prove identity without identity assurance
- `binding_status` must not trigger the wrapper or the next gate

### Key policy version model

Fields: `key_policy_version`, `policy_effective_at_utc`, `policy_owner`,
`allowed_key_status_for_signing`, `allowed_signer_roles`,
`minimum_identity_assurance`, `allowed_storage_models`,
`rotation_requirement`, `revocation_requirement`,
`approval_boundary_statement`.

Rules:

- key policy controls signing eligibility only
- key policy does not authorize approval execution
- a key policy mismatch requires manual review

### Compatibility with Phase 8I signature envelope

Key management maps onto these Phase 8I envelope fields: `key_id`,
`signer_id`, `signer_role`, `signer_identity_assurance`,
`signing_policy_version`, `revocation_status`, `rotation_epoch`,
`approval_boundary_statement`.

Rules:

- the mapping is design-only and does not change the Phase 8I envelope
  schema
- the mapping does not imply approval

### Compatibility with Phase 8J verifier design

The verifier should interpret: `key_status`, `key_status_reason`,
`key_fingerprint`, `key_version`, signer-to-key binding,
`revocation_reference`, `rotation_epoch`, `key_policy_version`.

Rules:

- verifier interpretation is evidence only
- verifier interpretation is not approval

### Failure taxonomy mapping

Failure types: `key_metadata_missing`, `key_status_unknown`,
`key_not_active`, `key_revoked`, `key_expired`, `key_retired`,
`key_compromised`, `key_policy_mismatch`, `key_owner_missing`,
`key_custodian_missing`, `key_fingerprint_missing`,
`signer_binding_missing`, `signer_binding_revoked`,
`rotation_epoch_stale`, `revocation_reference_missing`,
`identity_assurance_insufficient`.

Severity values: `info`, `warning`, `critical`.

Incident classification values: `none`, `key_metadata_review_required`,
`key_lifecycle_review_required`, `key_compromise_review_required`,
`signer_binding_review_required`, `policy_review_required`.

Reviewer action values: `no_action_required`, `manual_review_required`,
`reject_signature_until_resolved`.

Mapping (failure type -> severity / incident_classification /
reviewer_action):

| failure type | severity | incident_classification | reviewer_action |
| --- | --- | --- | --- |
| `key_metadata_missing` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `key_status_unknown` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `key_not_active` | `warning` | `key_lifecycle_review_required` | `manual_review_required` |
| `key_revoked` | `critical` | `key_lifecycle_review_required` | `reject_signature_until_resolved` |
| `key_expired` | `critical` | `key_lifecycle_review_required` | `reject_signature_until_resolved` |
| `key_retired` | `warning` | `key_lifecycle_review_required` | `manual_review_required` |
| `key_compromised` | `critical` | `key_compromise_review_required` | `reject_signature_until_resolved` |
| `key_policy_mismatch` | `warning` | `policy_review_required` | `manual_review_required` |
| `key_owner_missing` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `key_custodian_missing` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `key_fingerprint_missing` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `signer_binding_missing` | `warning` | `signer_binding_review_required` | `manual_review_required` |
| `signer_binding_revoked` | `critical` | `signer_binding_review_required` | `reject_signature_until_resolved` |
| `rotation_epoch_stale` | `warning` | `key_lifecycle_review_required` | `manual_review_required` |
| `revocation_reference_missing` | `warning` | `key_metadata_review_required` | `manual_review_required` |
| `identity_assurance_insufficient` | `warning` | `signer_binding_review_required` | `manual_review_required` |

### Reviewer action mapping

- `no_action_required` only for valid active key metadata with sufficient
  policy context
- `manual_review_required` for unknown, missing, or stale metadata
- `reject_signature_until_resolved` for a revoked, expired, or compromised
  key, or a revoked signer binding

Rules:

- reviewer action is guidance only
- reviewer action is not approval
- reviewer action must not execute a primitive
- reviewer action must not trigger the wrapper
- reviewer action must not trigger the next gate

### Approval boundary

- key metadata is not approval
- an active key is not approval
- a key owner is not approval
- a key custodian is not approval
- a signer-to-key binding is not approval
- key policy eligibility is not approval
- a signature created using an eligible key is not approval
- key management must not bypass the selected-gate manual approval
  boundary
- key management must not set approval flags
- key management must not trigger the wrapper
- key management must not trigger the next gate
- approval remains the Phase 7D selected-gate manual boundary

### Privacy and secret handling

- no private keys in the repository
- no private keys in the export pack
- no private keys in docs
- no secrets in key metadata
- no approval flags in key metadata
- no API keys
- no affiliate secrets
- no raw terminal dump if it contains secrets
- signer/key owner metadata should avoid unnecessary personal data
- key management logs/screenshots must be sanitized

### Non-goals

Phase 8K does not:

- implement key management runtime
- generate keys
- handle private keys
- create key files
- create certificate files
- implement signing
- implement signature verification
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

### Phase 8J verifier design boundary

- Phase 8J remains detached signature verifier design
- Phase 8K supplies key governance interpretation
- Phase 8K does not implement verifier runtime
- Phase 8K does not modify Phase 8J files except an additive pointer

### Phase 8I signature design boundary

- Phase 8I remains the detached signature envelope/payload design source
- Phase 8K refines key governance for Phase 8I fields
- Phase 8K does not implement signing runtime

### Phase 8H verifier boundary

- Phase 8H remains the hash-only export integrity verifier
- Phase 8K does not change Phase 8H runtime
- Phase 8H reviewer action remains review guidance only

### Phase 7D approval boundary

- approval remains the Phase 7D selected-gate manual boundary
- key management must not call the Phase 7D wrapper
- key management must not call primitives
- key management must not write the vault
- key management must not trigger the next gate

### Future implementation path

- Phase 8L: Local Detached Signature Prototype
- Phase 8M: Detached Signature Verifier Prototype
- Phase 8N: Signature Runbook / Incident Review Pack
- Phase 8O: Phase 8 Final Acceptance Pack
- Phase 9A: Operator Identity Boundary Design

None of the above are implemented in Phase 8K.

Phase 8L Local Detached Signature Prototype now exists at
[`PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`](PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md).
It uses an env-var prototype key only and does not implement key
management runtime; `key_management_runtime_status` remains
`not_implemented`. An active/prototype key is not approval.

Phase 8M Detached Signature Verifier Prototype now exists at
[`PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`](PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md).
Phase 8M does not implement key management runtime;
`key_management_runtime_status` remains `not_implemented`.

Phase 8N Signature Runbook / Incident Review Pack now exists at
[`PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`](PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md).
Phase 8N references key roles and lifecycle labels only as governance
labels, and `key_management_runtime_status` remains `not_implemented`.

Phase 8O Final Acceptance Pack now exists at
[`PHASE8O_FINAL_ACCEPTANCE_PACK.md`](PHASE8O_FINAL_ACCEPTANCE_PACK.md).
Phase 8O does not implement key management runtime.

### Major-phase checkpoint policy

Phase 8K is part of `feature/phase8-signature-governance-completion`. Phase
8K should create a checkpoint commit only; no PR should be opened after
Phase 8K alone. The full suite is deferred to major Phase 8 completion
unless focused tests fail or protected runtime changes occur. Focused
tests must pass before moving to Phase 8L.

### Known limitations

- design only
- no key management runtime
- no key generation
- no signing implementation
- no signature verifier runtime
- no encryption
- no authenticated operator identity
- no governed key custody implementation
- no non-repudiation
- no backend/API/database
- no production deployment
