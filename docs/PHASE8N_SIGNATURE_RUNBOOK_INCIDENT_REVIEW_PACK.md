# Phase 8N — Signature Runbook / Incident Review Pack

```text
phase8n_status: success
phase7d_runtime_readiness: implemented_manual_gate
durable_audit_store_status: signature_runbook_incident_review_pack
signing_implementation_status: prototype_local_only
signature_runtime_status: local_prototype
signature_verifier_runtime_status: local_prototype
key_management_runtime_status: not_implemented
runbook_runtime_status: docs_only
major_phase_branch_workflow: enabled
```

### Purpose

Phase 8N creates a signature runbook and incident review pack for the
Phase 8L local detached signature prototype and the Phase 8M local
detached signature verifier prototype workflows.

Phase 8N does not implement signing, verification, key management,
backend, database, or production deployment. It is runbook-only and is
not approval.

### Scope

- docs/tests/runbook-pack only
- signature incident runbook
- incident review pack checklist
- operator safe-demo procedure
- reviewer decision checklist
- escalation matrix
- evidence preservation checklist
- incident-to-action matrix
- Phase 8O handoff criteria
- no new runtime scripts
- no signing implementation
- no verifier implementation
- no key management implementation
- no key generation
- no KMS/Secrets Manager
- no backend/API/database
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path
- no next-gate automation
- no chain execution

### Current trust boundary

- Phase 8L provides local-only prototype signing.
- Phase 8M provides local-only prototype verification.
- Phase 8K remains design-only key management governance.
- No key management runtime exists.
- No authenticated operator identity exists.
- No governed key custody exists.
- No enterprise non-repudiation exists.
- Durable audit remains local/tmp workflow.
- Phase 8N is runbook-only.
- Incident review is guidance only, not approval.

### Operator safe-demo procedure

1. Confirm branch and clean working tree.
2. Confirm Phase 8E export pack exists.
3. Confirm Phase 8G/8H integrity report exists.
4. Run Phase 8L signing prototype with or without
   AFFILIATE_PHASE8L_PROTOTYPE_KEY depending test scenario by using
   `bash scripts/dev/run_phase8l_detached_signature.sh`.
5. Confirm Phase 8L outputs under `tmp/phase8l-detached-signature/`.
6. Run Phase 8M verifier prototype with matching, missing, or mismatched
   AFFILIATE_PHASE8L_PROTOTYPE_KEY depending scenario by using
   `bash scripts/dev/run_phase8m_detached_signature_verifier.sh`.
7. Confirm Phase 8M outputs under `tmp/phase8m-detached-signature-verifier/`.
8. Review `signature_verification_status`.
9. Review `verification_status`.
10. Review `signature_status`.
11. Review `incident_classification`.
12. Review `reviewer_action`.
13. Preserve evidence.
14. Do not treat any result as approval.
15. Do not run wrapper or primitives from this runbook.

No key samples are included. No secret samples are included. No
external commands beyond existing local project runners are included.

### Reviewer incident review procedure

1. Read Phase 8M verification JSON.
2. Read Phase 8M Markdown summary.
3. Confirm report status tokens.
4. Confirm descriptor/envelope paths.
5. Confirm `output_dir` boundary.
6. Confirm `issues` array.
7. Confirm `failure_count` and `severity_counts`.
8. Confirm `incident_classification`.
9. Confirm `reviewer_action`.
10. Apply incident classification matrix.
11. Apply evidence preservation checklist.
12. Escalate if required.
13. Record review notes outside vault unless future approved store exists.
14. Never approve solely from signature verification.
15. Never trigger Phase 7D wrapper from incident review.

### Evidence preservation checklist

- Phase 8E export manifest
- Phase 8G/8H integrity report
- Phase 8L signed payload descriptor
- Phase 8L detached signature envelope
- Phase 8L summary JSON/MD
- Phase 8M verification JSON/MD
- command invocation metadata without secrets
- environment key presence indicator only, never raw key
- timestamp
- operator/reviewer notes
- incident classification
- reviewer action
- affected product/week/gate if available

Rules:

- preserve evidence without mutating source artifacts
- do not copy raw prototype key
- do not write vault in Phase 8N
- do not delete failed evidence

### Incident classification matrix

| incident_classification | meaning | common trigger | severity | reviewer_action | escalation target | evidence to preserve | approval boundary reminder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `none` | No signature incident detected in the local prototype workflow. | `verified_local_prototype` with no warnings. | `info` | `no_action_required` | `reviewer` | verification JSON/MD and referenced Phase 8L/8E/8G evidence | verified signature is not approval |
| `signature_not_available` | Signature evidence is missing, intentionally skipped, or not yet reviewable. | missing Phase 8L artifacts, missing prototype key, `not_ready`, or `not_present`. | `info` or `warning` | `no_action_required` or `manual_review_required` | `operator` or `reviewer` | missing-input report, warning report, and source artifact paths | incident review is not approval |
| `signature_integrity_failure` | Signature evidence exists but integrity checks failed. | invalid input, hash mismatch, HMAC mismatch, or missing signature value. | `critical` | `reject_signature_until_resolved` | `security_owner` and/or `system_owner` | descriptor, envelope, verification JSON/MD, command metadata, notes | verification passed is not approval |
| `key_lifecycle_review_required` | Key lifecycle context requires manual review. | revocation or rotation warning, stale lifecycle metadata. | `warning` | `manual_review_required` | `key_owner` and `key_custodian` | envelope metadata, verification JSON/MD, historical evidence | key metadata is not approval |
| `policy_review_required` | Signature policy or schema interpretation is unsupported or incomplete. | unsupported algorithm/encoding, schema mismatch, design-policy gap. | `warning` or `critical` | `manual_review_required` or `reject_signature_until_resolved` | `system_owner` and `security_owner` | envelope, descriptor, verifier report, policy notes | runbook action is not approval |
| `signer_identity_review_required` | Signer identity metadata is too weak for stronger trust claims. | unauthenticated or operator-declared signer metadata. | `warning` | `manual_review_required` | `reviewer` or `system_owner` | signer/key metadata, verification report, notes | reviewer action is not approval |
| `replay_review_required` | Replay or reuse of signature evidence is suspected. | duplicate/reused descriptor+envelope pair or suspicious repeated artifact set. | `critical` | `reject_signature_until_resolved` | `security_owner` and `emergency_revocation_authority` | all referenced evidence plus timeline notes | signature verifier result is not approval |

### Signature verification outcome matrix

| signature_verification_status | verification_status | signature_status | severity | incident_classification | reviewer_action | operator response | reviewer response | escalation requirement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `skipped_missing_signature_inputs` | `empty` | `not_present` | `info` | `signature_not_available` | `no_action_required` | verify Phase 8L outputs and safe paths; rerun Phase 8L only if appropriate | preserve missing-input report and avoid approval | escalate to `operator` only if unexpected |
| `skipped_signature_not_ready` | `warning` | `not_ready` | `warning` | `signature_not_available` | `manual_review_required` | confirm intentionally skipped signing or missing key scenario | preserve report; not_ready is not approval | escalate to `operator` if scenario was not intentional |
| `skipped_signature_not_present` | `empty` | `not_present` | `info` | `signature_not_available` | `manual_review_required` | confirm no signature was expected in the scenario | preserve report and note gap | escalate to `operator` if signature should have existed |
| `skipped_missing_prototype_key` | `warning` | `present` | `warning` | `signature_not_available` | `manual_review_required` | decide whether this is an expected safe-demo scenario; rerun locally if needed | preserve warning report and do not approve | escalate to `operator`/`reviewer` if unexpected |
| `verified_local_prototype` | `valid` | `verification_passed` | `info` | `none` | `no_action_required` | preserve outputs and stop at evidence review | note that verification passed is not approval | no escalation required |
| `failed_invalid_input` | `invalid` | `malformed` or `not_present` | `critical` | `signature_integrity_failure` | `reject_signature_until_resolved` | stop and preserve corrupted artifacts | reject signature until resolved | escalate to `system_owner` |
| `failed_schema_validation` | `invalid` | `malformed` or `present` | `critical` | `policy_review_required` | `reject_signature_until_resolved` | preserve invalid artifacts before any rerun | reject signature until resolved | escalate to `system_owner` |
| `failed_signed_payload_hash_mismatch` | `invalid` | `verification_failed` | `critical` | `signature_integrity_failure` | `reject_signature_until_resolved` | compare descriptor hash and envelope hash after preserving evidence | reject signature until resolved | escalate to `security_owner` and `system_owner` |
| `failed_unsupported_algorithm` | `invalid` | `unsupported_algorithm` | `critical` | `policy_review_required` | `reject_signature_until_resolved` | preserve envelope and confirm expected policy values | reject until resolved; do not introduce external signing tools | escalate to `system_owner` and `security_owner` |
| `failed_unsupported_encoding` | `invalid` | `unsupported_algorithm` or `present` | `critical` | `policy_review_required` | `reject_signature_until_resolved` | preserve envelope and confirm expected policy values | reject until resolved; do not introduce external signing tools | escalate to `system_owner` and `security_owner` |
| `failed_missing_signature_value` | `invalid` | `present` | `critical` | `signature_integrity_failure` | `reject_signature_until_resolved` | preserve envelope and confirm Phase 8L output state | reject signature until resolved | escalate to `system_owner` |
| `failed_signature_mismatch` | `invalid` | `verification_failed` | `critical` | `signature_integrity_failure` | `reject_signature_until_resolved` | confirm correct prototype key was used without exposing key | reject signature until resolved | escalate to `security_owner` |

This matrix is the incident-to-action matrix for the current local
prototype workflow.

### Missing input procedure

For `skipped_missing_signature_inputs`:

- verify Phase 8L outputs exist
- verify safe path
- rerun Phase 8L only if appropriate
- do not fabricate descriptor/envelope
- do not approve
- preserve missing-input report

### Missing prototype key procedure

For `skipped_missing_prototype_key`:

- verify the envelope reports signature present
- decide whether this is an expected safe demo scenario
- rerun verifier with prototype key only in controlled local environment if needed
- never write raw key
- do not approve
- preserve warning report

### Signature not-ready procedure

For `skipped_signature_not_ready`:

- confirm Phase 8L signing was intentionally skipped
- confirm missing key scenario
- do not treat not_ready as failure of evidence integrity
- not_ready is not approval
- do not approve
- preserve report

### Invalid descriptor/envelope procedure

For `failed_invalid_input` and `failed_schema_validation`:

- stop reviewer flow
- preserve corrupted/invalid artifacts
- compare with expected Phase 8L schema
- rerun Phase 8L only after preserving failure evidence
- reject signature until resolved
- do not approve
- escalate to operator/system owner

### Signed payload hash mismatch procedure

For `failed_signed_payload_hash_mismatch`:

- treat as critical signature_integrity_failure
- preserve descriptor/envelope before any rerun
- compare descriptor hash and envelope signed_payload_sha256
- check for post-signature descriptor mutation
- reject signature until resolved
- escalate to security_owner and system_owner
- do not approve
- do not call wrapper/primitives

### Signature HMAC mismatch procedure

For `failed_signature_mismatch`:

- treat as critical signature_integrity_failure
- preserve evidence
- confirm correct prototype key was used without exposing key
- confirm envelope detached_signature_value
- suspect wrong key or tampered envelope
- reject signature until resolved
- escalate to security_owner
- do not approve
- do not call wrapper/primitives

### Unsupported algorithm/encoding procedure

For `failed_unsupported_algorithm` and `failed_unsupported_encoding`:

- treat as policy review issue
- preserve envelope
- confirm algorithm/encoding expected values
- reject signature until resolved
- escalate to system_owner/security_owner
- do not introduce external signing tools
- do not approve

### Missing signature value procedure

For `failed_missing_signature_value`:

- preserve envelope
- confirm Phase 8L output state
- rerun Phase 8L only after evidence preservation
- reject signature until resolved
- do not approve

### Key metadata review procedure

For key metadata warnings:

- review `key_id`
- review `key_version`
- review signer metadata
- review `signer_identity_assurance`
- confirm Phase 8K remains design-only
- key metadata is not identity proof
- do not treat key metadata as identity proof
- do not approve

### Revocation/rotation review procedure

For revocation/rotation warnings:

- review `revocation_status`
- review `rotation_status` or `rotation_epoch`
- confirm no governed revocation/rotation runtime exists
- classify as manual review unless explicitly valid
- do not delete historical evidence
- do not approve

### Escalation matrix

Roles are governance labels only until Phase 9 identity/RBAC.

| incident | escalation target | expectation |
| --- | --- | --- |
| informational/no issue | `reviewer` | document outcome and preserve evidence only |
| missing signature input | `operator` | restore expected Phase 8L inputs or document intentional absence |
| missing prototype key | `operator` / `reviewer` | confirm whether safe-demo warning was intentional |
| invalid descriptor/envelope | `system_owner` | preserve artifacts and compare against expected Phase 8L schema |
| signed payload hash mismatch | `security_owner` + `system_owner` | treat as critical signature_integrity_failure |
| HMAC mismatch | `security_owner` | confirm key-selection mismatch or tamper suspicion |
| unsupported algorithm/encoding | `system_owner` + `security_owner` | resolve policy mismatch without adding tools |
| key lifecycle issue | `key_owner` + `key_custodian` | review revocation/rotation metadata and historical evidence |
| suspected replay | `security_owner` + `emergency_revocation_authority` | preserve full evidence set and assess containment |

### Reviewer action checklist

Reviewer action is guidance only.

| reviewer_action | allowed interpretation | forbidden interpretation | evidence action | escalation action | approval boundary |
| --- | --- | --- | --- | --- | --- |
| `no_action_required` | no additional incident response is needed beyond evidence preservation | approval, execution, or wrapper trigger | preserve JSON/MD outputs and linked evidence | none unless contradictory evidence appears | reviewer action is not approval |
| `manual_review_required` | human review is needed before the signature evidence can be trusted | implicit approval, auto-rerun, or next-gate permission | preserve evidence and add review notes | escalate per matrix if scenario is unexpected | runbook action is not approval |
| `reject_signature_until_resolved` | treat the signature evidence as unusable until corrected | product rejection, primitive execution, or approval mutation | preserve failure evidence before any rerun | escalate per matrix immediately | incident review is not approval |

Reviewer action must not execute primitive/wrapper/next gate.

### Approval boundary checklist

- verified signature is not approval
- verification passed is not approval
- signature verifier result is not approval
- signed export is not approval
- local prototype signature is not approval
- key metadata is not approval
- reviewer action is guidance only
- reviewer action is not approval
- runbook action is guidance only
- runbook action is not approval
- incident review is not approval
- signature workflow must not bypass selected-gate manual approval
- signature workflow must not set approval flags
- signature workflow must not trigger wrapper
- signature workflow must not trigger next gate
- approval remains Phase 7D selected-gate manual boundary

### Security/privacy checklist

- never write raw AFFILIATE_PHASE8L_PROTOTYPE_KEY
- never paste raw secrets into reports
- never commit key/cert files
- never copy private key material
- never include affiliate secrets
- never include API keys
- sanitize terminal logs
- preserve evidence without mutation
- avoid unnecessary personal data
- keep outputs in tmp paths only for current local workflow

### Operator mistake recovery

| mistake case | immediate action | evidence preservation | rerun condition | escalation if needed | approval boundary reminder |
| --- | --- | --- | --- | --- | --- |
| wrong key used | stop and note which scenario was intended | preserve Phase 8M warning/failure outputs | rerun only after confirming local env selection | escalate to `security_owner` if mismatch remains unexplained | verification passed is not approval |
| missing key | confirm whether safe-demo warning was expected | preserve warning report and command metadata | rerun verifier locally only if controlled key use is required | escalate to `reviewer` if expectation was unclear | reviewer action is not approval |
| wrong descriptor path | stop and confirm safe path target | preserve path error and notes | rerun only with verified Phase 8L descriptor path | escalate to `operator` if repeated | runbook action is not approval |
| wrong envelope path | stop and confirm safe path target | preserve path error and notes | rerun only with verified Phase 8L envelope path | escalate to `operator` if repeated | incident review is not approval |
| stale Phase 8L output | compare timestamps and scenario intent | preserve stale output metadata before replacement | rerun Phase 8L only after preserving existing evidence | escalate to `system_owner` if state drift is recurring | signed export is not approval |
| overwritten tmp output | stop and preserve remaining artifacts plus notes | preserve surviving artifacts and timeline notes | rerun only when the evidence gap is documented | escalate to `reviewer` or `system_owner` if material evidence is lost | local prototype signature is not approval |
| invalid JSON | stop reviewer flow | preserve corrupted artifact bytes and notes | rerun Phase 8L only after evidence preservation | escalate to `system_owner` | signature verifier result is not approval |
| path rejected by safety guard | do not bypass the guard | preserve error output and intended path notes | rerun only with safe in-repo tmp paths | escalate to `operator` if path expectation is unclear | signature workflow must not bypass selected-gate manual approval |
| accidental command with wrong env | stop and document the env-state mistake without copying secrets | preserve command metadata and resulting outputs | rerun only after resetting local env correctly | escalate to `security_owner` if evidence trust is unclear | signature workflow must not set approval flags |

### Phase 8O handoff criteria

- Phase 8L signing prototype focused tests pass
- Phase 8M verifier prototype focused tests pass
- Phase 8N runbook tests pass
- Phase 8G/8H regressions pass
- Phase 8E export regression passes before Phase 8O final acceptance
- Phase 7D wrapper regression passes before Phase 8O final acceptance
- no runtime behavior changes in Phase 8N
- no key/cert files
- no backend/API/database
- no primitive execution
- no vault write
- final acceptance pack can demonstrate missing input, not_ready, valid,
  mismatch, and hash mismatch scenarios safely
- full suite is deferred until Phase 8O final acceptance

### Non-goals

Phase 8N does not add runtime scripts, signing implementation, verifier
implementation, key management implementation, key generation, key file
creation, certificate files, KMS/Secrets Manager, backend/API/database,
wrapper behavior changes, primitive execution, vault read/write, new
mutation paths, next-gate automation, chain execution, affiliate content
generation, autopublish, marketplace submission, or production
deployment.

### Phase 8M verifier prototype boundary

Phase 8M remains the local verifier-side implementation. Phase 8N adds
procedures for interpreting Phase 8M outcomes, points operators/reviewers
to evidence preservation and escalation decisions, does not modify
verifier runtime, and incident review remains not approval.

### Phase 8L signing prototype boundary

Phase 8L remains the local signing-side implementation. Phase 8N adds
procedures for interpreting Phase 8L output states and safe demo
scenarios, and does not modify signing runtime.

### Phase 8K key management boundary

Phase 8K remains design-only key management governance. Phase 8N
references key roles, key lifecycle labels, and review semantics only as
governance labels, and `key_management_runtime_status` remains
`not_implemented`.

### Phase 8J verifier design boundary

Phase 8J remains detached signature verifier design. Phase 8N turns
verifier interpretation into operator/reviewer procedures and remains
runbook-only.

### Phase 8H verifier boundary

Phase 8H remains hash-only export integrity verifier. Phase 8N does not
modify Phase 8H runtime.

### Phase 8E export boundary

Phase 8E remains export pack builder. Phase 8N does not modify Phase 8E
runtime.

### Phase 7D approval boundary

- approval remains the Phase 7D selected-gate manual boundary
- Phase 8N does not call Phase 7D wrapper
- Phase 8N does not call primitives
- Phase 8N does not write vault
- Phase 8N does not trigger next gate

### Major-phase checkpoint policy

Phase 8N is part of `feature/phase8-signature-governance-completion`.
Phase 8N should create a checkpoint commit only. No PR should be opened
after Phase 8N alone. Because Phase 8N does not add runtime code,
focused tests plus Phase 8M/8L/8K/8J regressions are required. Full
suite is deferred to Phase 8O final acceptance unless focused tests fail
or protected runtime changes unexpectedly.

### Known limitations

- runbook only
- no new runtime
- local prototype workflow only
- no production signing
- no production verifier
- no key management runtime
- no governed key custody
- no authenticated operator identity
- no non-repudiation
- no backend/API/database
- no production deployment
