# Task 061 — Phase 8J Detached Signature Verifier Design

phase8j_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: detached_signature_verifier_design

signing_implementation_status: design_only

signature_runtime_status: not_implemented

signature_verifier_runtime_status: not_implemented

major_phase_branch_workflow: enabled

## Purpose

Phase 8J designs the future detached signature verifier flow for signed
Phase 8E export packs. Phase 8J is docs/tests design-only: it defines a
verifier input contract, a signature envelope validation model, a signed
payload descriptor validation model, a signed payload hash validation
model, a bundle-hash/manifest-hash cross-check model, a key metadata
validation model, a signer identity assurance interpretation, a
revocation/rotation interpretation model, a signature status transition
model, a verification status model, a failure taxonomy mapping, a reviewer
action mapping, and a deterministic verification report schema. Phase 8J
does not implement signature verification runtime.

## Scope

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
- no runtime script of any kind (no `scripts/dev/run_phase8j*.sh`)
- no change to Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, or
  8B/8C/8D/8E/8G/8H runtime behavior

## Files

- `codex/tasks/061-phase8j-detached-signature-verifier-design.md`
- `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`
- `tests/test_phase8j_detached_signature_verifier_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`
- additive updates to `docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`
- additive updates to `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`

## Status model

- `phase8j_status: success` — the detached signature verifier design exists,
  additive documentation pointers exist, and protected runtime files stay
  unchanged.
- `phase7d_runtime_readiness: implemented_manual_gate` — the Phase 7D
  single-gate manual approval wrapper remains the only implemented
  approval runtime; Phase 8J does not change it.
- `durable_audit_store_status: detached_signature_verifier_design` — the
  durable audit store status token advances to reflect that a detached
  signature verifier design now exists.
- `signing_implementation_status: design_only` — no signing implementation
  exists anywhere in the repository.
- `signature_runtime_status: not_implemented` — no detached signature
  runtime exists.
- `signature_verifier_runtime_status: not_implemented` — no signature
  verifier runtime exists; this phase is design only.
- `major_phase_branch_workflow: enabled` — Phase 8J follows the major-phase
  checkpoint-commit-only workflow; no PR is opened for this sub-phase
  alone.

## Detached signature verifier design objective

Provide a complete, implementation-ready design for a future detached
signature verifier over the Phase 8I signature envelope and signed payload
descriptor, so a later phase can implement verification against a stable
schema, without implementing any verifier, signing, or key-management code
in this phase.

## Current trust boundary

- Phase 8E creates export packs
- Phase 8G/8H verify hash-only export integrity
- Phase 8I finalizes detached signature design
- no signature verifier runtime exists
- no signing runtime exists
- no authenticated operator identity exists
- no enterprise non-repudiation exists
- signature verifier design must not turn signature evidence into approval
- durable audit remains a local/tmp workflow

## Signature verifier input contract

Future inputs: detached signature envelope, signed payload descriptor,
Phase 8E export manifest, Phase 8G/8H export integrity verification report,
key metadata record, optional revocation metadata, optional rotation
metadata, signing policy metadata. All inputs are evidence; inputs must not
include private keys, secrets, or approval flags; verifier inputs must not
mutate source evidence or trigger approval.

## Signature envelope validation model

Envelope fields: `signature_schema_version`, `signed_payload_sha256`,
`signed_payload_descriptor_path`, `detached_signature_path`,
`signature_algorithm`, `signature_encoding`, `key_id`, `signer_id`,
`signer_role`, `signer_identity_assurance`, `signing_policy_version`,
`signing_timestamp_utc`, `signature_status`, `verification_status`,
`revocation_status`, `rotation_epoch`, `approval_boundary_statement`.
Validation checks: required fields present, schema version supported,
algorithm/encoding allowed by policy, `key_id` and signer metadata
present, `approval_boundary_statement` present, envelope path separation
from the export manifest, no private key material, no approval flags, no
mutation intent.

## Signed payload descriptor validation model

Descriptor fields (Phase 8I's descriptor fields): `payload_schema_version`,
`export_manifest_path`, `export_manifest_sha256`, `bundle_hash`,
`computed_manifest_hash`, `report_schema_version`,
`issue_taxonomy_version`, `compatibility_matrix_version`,
`verifier_hardening_status`, `verification_status`,
`compatibility_result`, `incident_classification`, `reviewer_action`,
`reviewer_action_required`, `generated_from_phase`, `generated_by_tool`,
`created_at_utc`. Validation checks: canonical JSON, deterministic
ordering, required fields present, references to the Phase 8H report
schema/manifest hash/bundle hash, no secrets, no approval flags; the
descriptor is not approval.

## Signed payload hash validation model

Canonical descriptor bytes are the hashing input; `signed_payload_sha256`
is computed from the canonical descriptor and compared with the envelope
`signed_payload_sha256`; a mismatch means `signature_integrity_failure`.
Hash match is necessary but not approval and must not trigger the wrapper
or the next gate.

## Bundle hash and manifest hash cross-check model

`export_manifest_sha256` cross-checks against the Phase 8E manifest bytes;
`computed_manifest_hash` cross-checks against the Phase 8H report if
available; `bundle_hash` cross-checks against the Phase 8G/8H
`computed_bundle_hash`. A mismatch is classified separately from missing
optional context, and both map to a reviewer action. `bundle_hash` match
and `manifest_hash` match do not approve anything; cross-check success is
evidence integrity only.

## Key metadata validation model

Fields: `key_id`, `key_version`, `key_fingerprint`, `key_owner`,
`key_purpose`, `key_scope`, `key_created_at`, `key_expires_at`,
`key_status`. Allowed `key_status` values: `active`, `retired`, `revoked`,
`expired`, `unknown`. Key metadata is evidence only, is not private key
material, does not prove signer identity without authenticated identity,
and does not approve anything.

## Signer identity assurance interpretation

`signer_identity_assurance` values: `unauthenticated`,
`operator_declared`, `local_registry_verified`,
`enterprise_identity_verified`, `hardware_backed`. The current expected
level is `unauthenticated` or `operator_declared` until Phase 9 identity
work. Signer identity assurance is interpretation only, does not approve
anything, and low assurance requires manual review.

## Revocation and rotation interpretation model

`revocation_status` values: `not_checked`, `not_revoked`, `revoked`,
`unknown`. Rotation interpretation values: `current_epoch`,
`previous_epoch_allowed`, `stale_epoch`, `unknown_epoch`. A revoked key
requires manual review or rejection of the signature until resolved;
unknown revocation and a stale rotation epoch require manual review. A
revocation/rotation result must not delete evidence or trigger
rollback/execution.

## Signature status transition model

Status progression values: `not_present`, `present`, `malformed`,
`unsupported_algorithm`, `key_not_found`, `verification_failed`,
`verification_passed`, `revoked_key`, `expired_key`, `policy_mismatch`.
Allowed transitions: not_present -> present; present -> malformed; present
-> unsupported_algorithm; present -> key_not_found; present ->
verification_failed; present -> verification_passed; verification_passed
-> revoked_key; verification_passed -> expired_key; verification_passed ->
policy_mismatch. Transition to `verification_passed` is not approval;
transition failure is review evidence only; a status transition must not
trigger the next gate.

## Verification status model

Verifier output status values: `empty`, `valid`, `warning`, `invalid`.
`empty` if the signature is not present and optional in the current
design; `valid` if all checks pass with no warnings; `warning` if a
reviewable mismatch or missing optional context exists; `invalid` if the
envelope/descriptor is malformed or a critical policy/path failure exists.
A `valid` `verification_status` is not approval; an `invalid`
`verification_status` must not trigger rollback/execution.

## Failure taxonomy mapping

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

## Reviewer action mapping

`no_action_required` for an absent optional signature in design-only/
current local mode; `manual_review_required` for mismatches, an unknown
signer, an unknown key status, or a policy mismatch;
`reject_signature_until_resolved` for a malformed signature, an
unsupported algorithm, a revoked/expired key, or a verification failure.
Reviewer action is guidance only, is not approval, and must not execute a
primitive, trigger the wrapper, or trigger the next gate.

## Verification report schema

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
`limitations`. The report schema is future design only, must be
deterministic in a future implementation, and must not contain private
keys, secrets, or approval flags.

## Approval boundary

A signature verifier result is not approval. A verified signature is not
approval. A signed export is not approval. Signature verification is not
primitive execution. Signature verification must not trigger wrapper
execution. Signature verification must not trigger next gate.
Signature verification must not set or imply approval flags. Reviewer
action remains review guidance only. A signature verification report is
evidence only, not approval. Approval remains the Phase 7D selected-gate
manual boundary.

## Non-repudiation limitation

Without authenticated identity or governed key custody, strong
non-repudiation is not available; without a revocation/rotation process,
signature trust is incomplete. A local-only signature verifier would
provide tamper-evidence, not enterprise non-repudiation, and signature
verification must not be overclaimed.

## Privacy and secret handling

No private keys in the repository or export pack; no secrets or approval
flags in the descriptor, envelope, or report; no API keys or affiliate
secrets; no raw terminal dump containing secrets; signer metadata avoids
unnecessary personal data; verification logs/screenshots must be
sanitized.

## Non-goals

Phase 8J does not implement signature verifier runtime, signing, key
generation, private key handling, encryption, KMS/Secrets Manager, or
backend/API/database. It does not modify Phase 8G/8H verifier runtime
behavior, Phase 8E export behavior, or Phase 7D wrapper behavior, execute
primitives, approve anything, trigger the next gate, add chain execution,
or create a production deployment.

## Phase 8I design boundary

Phase 8I remains the signature design source for the descriptor, envelope,
and key lifecycle. Phase 8J designs verifier-side interpretation only,
does not change Phase 8I files except an additive pointer, and does not
implement runtime.

## Phase 8H verifier boundary

Phase 8H remains the hash-only export integrity verifier; Phase 8J does
not change Phase 8H runtime. A future signature verifier depends on the
Phase 8H report schema. Phase 8H reviewer action remains review guidance
only.

## Phase 8E export boundary

The Phase 8E export pack remains read-only packaging. Phase 8J does not
change Phase 8E runtime. A future signature verifier must not mutate
export evidence, and a future signature envelope must stay separate from
the export manifest.

## Phase 7D approval boundary

Approval remains the Phase 7D selected-gate manual boundary. Signature
verification must not call the Phase 7D wrapper, must not call primitives,
must not write the vault, and must not trigger the next gate.

## Future implementation path

- Phase 8K: Key Management Design
- Phase 8L: Local Detached Signature Prototype
- Phase 8M: Detached Signature Verifier Prototype
- Phase 8N: Signature Runbook / Incident Review Pack
- Phase 8O: Phase 8 Final Acceptance Pack

None of the above are implemented in Phase 8J.

## Test strategy

Deterministic docs-contract tests in
`tests/test_phase8j_detached_signature_verifier_design.py` enforce: file
existence for the task and design doc; presence of all required status
tokens; presence of scope-safety tokens (no signing/verifier/key/
encryption/KMS/backend/API/database/network/wrapper/approval/primitive/
vault/next-gate/chain implementation); presence of every required design
section; field-name and enum coverage for the envelope, descriptor, key
metadata, signer identity assurance, revocation/rotation, signature
status transition, verification status, and failure taxonomy models;
doc cross-reference regression across ROADMAP/PROJECT_STATE/PHASE8I/
PHASE8H/PHASE8G; protected-runtime-file non-modification; and a static
safety scan of the two new Phase 8J files rejecting secrets, private-key
material, and executable command examples.

## Acceptance criteria

- task exists
- design doc exists
- design doc contains `phase8j_status: success`
- design doc contains `phase7d_runtime_readiness: implemented_manual_gate`
- design doc contains
  `durable_audit_store_status: detached_signature_verifier_design`
- design doc contains `signing_implementation_status: design_only`
- design doc contains `signature_runtime_status: not_implemented`
- design doc contains `signature_verifier_runtime_status: not_implemented`
- design doc contains `major_phase_branch_workflow: enabled`
- design doc states docs/tests design-only
- design doc states no signature-verifier/signing/key-generation/private-
  key-handling/encryption/KMS/Secrets-Manager implementation
- design doc states no Phase 8G/8H verifier behavior change
- design doc states no Phase 8E export behavior change
- design doc states no Phase 7D wrapper behavior change
- design doc states no primitive execution and no vault read/write
- ROADMAP, PROJECT_STATE, PHASE8I, PHASE8H, and PHASE8G all reference
  Phase 8J additively
- protected Phase 2G/2H/2I, 6B/6C/6E, 7B, 7D wrapper, and
  8B/8C/8D/8E/8G/8H runtime files remain unchanged
- no new runtime, signing, key, certificate, database, backend, API, or
  package.json file is added by Phase 8J

## Focused verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
python -m pytest -q tests/test_phase8i_detached_signature_design_finalization.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
```

## Major-phase checkpoint policy

Phase 8J is part of `feature/phase8-signature-governance-completion`. Phase
8J should create a checkpoint commit only; no PR should be opened after
Phase 8J alone. The full suite is deferred to major Phase 8 completion
unless focused tests fail or protected runtime changes occur. Focused
tests must pass before moving to Phase 8K.

## Known limitations

Phase 8J is design only. No signature verifier runtime, signing, or
key-management implementation exists. No encryption, no authenticated
operator identity, no non-repudiation, no backend/API/database, and no
production deployment exist.

## Final status target

phase8j_status: success
