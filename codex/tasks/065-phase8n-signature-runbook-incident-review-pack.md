# Task 065 — Phase 8N Signature Runbook / Incident Review Pack

phase8n_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: signature_runbook_incident_review_pack

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

runbook_runtime_status: docs_only

major_phase_branch_workflow: enabled

## Purpose

Phase 8N creates the operator/reviewer signature incident runbook and
incident review pack for the Phase 8L local detached signature prototype
and the Phase 8M local detached signature verifier prototype. Phase 8N is
docs/tests/runbook-pack only and does not add signing runtime, verifier
runtime, key management runtime, backend/API/database behavior, or
production deployment.

## Scope

- docs/tests/runbook-pack only
- signature incident runbook
- incident review pack checklist
- operator safe-demo procedure
- reviewer decision checklist
- escalation matrix
- evidence preservation checklist
- incident-to-action matrix
- final handoff criteria for Phase 8O Final Acceptance Pack
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

## Files

- `codex/tasks/065-phase8n-signature-runbook-incident-review-pack.md`
- `docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`
- `tests/test_phase8n_signature_runbook_incident_review_pack.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to
  `docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`
- additive updates to
  `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`

## Status model

- `phase8n_status: success` — the runbook/task/tests/docs pointers exist,
  and protected runtime files remain unchanged.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status:
  signature_runbook_incident_review_pack` — the durable audit store
  posture advances to documented incident-review guidance.
- `signing_implementation_status: prototype_local_only` — signing remains
  the Phase 8L local prototype only.
- `signature_runtime_status: local_prototype` — signing runtime remains
  the existing Phase 8L local prototype only.
- `signature_verifier_runtime_status: local_prototype` — verifier runtime
  remains the existing Phase 8M local prototype only.
- `key_management_runtime_status: not_implemented` — key management
  runtime still does not exist.
- `runbook_runtime_status: docs_only` — Phase 8N adds no runtime and no
  mutation path.
- `major_phase_branch_workflow: enabled` — Phase 8N follows the
  checkpoint-only branch workflow.

## Signature incident runbook objective

Provide deterministic operator/reviewer guidance for interpreting Phase 8L
and Phase 8M prototype outputs, preserving evidence, classifying
incidents, and escalating when needed without turning any signature result
into approval and without executing wrapper or primitive flows.

## Current trust boundary

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

## Operator safe-demo procedure

Use the existing local runners only: Phase 8L
`bash scripts/dev/run_phase8l_detached_signature.sh` and Phase 8M
`bash scripts/dev/run_phase8m_detached_signature_verifier.sh`.

## Reviewer incident review procedure

Review the Phase 8M JSON/Markdown outputs, apply the incident
classification matrix, preserve evidence, escalate when required, record
notes outside vault, never approve solely from signature verification, and
never trigger the Phase 7D wrapper from incident review.

## Evidence preservation checklist

Preserve the Phase 8E export manifest, Phase 8G/8H integrity report,
Phase 8L descriptor/envelope/summary artifacts, Phase 8M verification
artifacts, command metadata without secrets, environment key presence
indicator only, timestamp, notes, incident classification, reviewer
action, and affected product/week/gate if available. Preserve evidence
without mutating source artifacts, do not copy raw prototype key, do not
write vault in Phase 8N, and do not delete failed evidence.

## Incident classification matrix

Matrix rows: `none`, `signature_not_available`,
`signature_integrity_failure`, `key_lifecycle_review_required`,
`policy_review_required`, `signer_identity_review_required`,
`replay_review_required`. Each row maps meaning, common trigger,
severity, reviewer_action, escalation target, evidence to preserve, and
approval boundary reminder.

## Signature verification outcome matrix

Matrix rows: `skipped_missing_signature_inputs`,
`skipped_signature_not_ready`, `skipped_signature_not_present`,
`skipped_missing_prototype_key`, `verified_local_prototype`,
`failed_invalid_input`, `failed_schema_validation`,
`failed_signed_payload_hash_mismatch`, `failed_unsupported_algorithm`,
`failed_unsupported_encoding`, `failed_missing_signature_value`,
`failed_signature_mismatch`. Each row maps verification_status,
signature_status, severity, incident_classification, reviewer_action,
operator response, reviewer response, and escalation requirement.

## Missing input procedure

For `skipped_missing_signature_inputs`: verify Phase 8L outputs exist,
verify safe path, rerun Phase 8L only if appropriate, do not fabricate
descriptor/envelope, do not approve, and preserve the missing-input
report.

## Missing prototype key procedure

For `skipped_missing_prototype_key`: verify the envelope reports
signature present, decide whether this is an expected safe-demo scenario,
rerun verifier with prototype key only in a controlled local environment
if needed, never write raw key, do not approve, and preserve the warning
report.

## Signature not-ready procedure

For `skipped_signature_not_ready`: confirm Phase 8L signing was
intentionally skipped, confirm missing key scenario, do not treat
not_ready as failure of evidence integrity, not_ready is not approval, do
not approve, and preserve the report.

## Invalid descriptor/envelope procedure

For `failed_invalid_input` and `failed_schema_validation`: stop reviewer
flow, preserve corrupted/invalid artifacts, compare with expected Phase 8L
schema, rerun Phase 8L only after preserving failure evidence, reject
signature until resolved, do not approve, and escalate to operator/system
owner.

## Signed payload hash mismatch procedure

For `failed_signed_payload_hash_mismatch`: treat as critical
signature_integrity_failure, preserve descriptor/envelope before rerun,
compare descriptor hash and envelope signed_payload_sha256, check for
post-signature descriptor mutation, reject signature until resolved,
escalate to security_owner and system_owner, do not approve, and do not
call wrapper/primitives.

## Signature HMAC mismatch procedure

For `failed_signature_mismatch`: treat as critical
signature_integrity_failure, preserve evidence, confirm correct prototype
key was used without exposing key, confirm envelope detached_signature_value,
suspect wrong key or tampered envelope, reject signature until resolved,
escalate to security_owner, do not approve, and do not call
wrapper/primitives.

## Unsupported algorithm/encoding procedure

For `failed_unsupported_algorithm` and `failed_unsupported_encoding`:
treat as policy review issue, preserve envelope, confirm expected
algorithm/encoding values, reject signature until resolved, escalate to
system_owner/security_owner, do not introduce external signing tools, and
do not approve.

## Missing signature value procedure

For `failed_missing_signature_value`: preserve envelope, confirm Phase 8L
output state, rerun Phase 8L only after evidence preservation, reject
signature until resolved, and do not approve.

## Key metadata review procedure

For key metadata warnings: review `key_id`, `key_version`, signer
metadata, and `signer_identity_assurance`; confirm Phase 8K remains
design-only; do not treat key metadata as identity proof; and do not
approve.

## Revocation/rotation review procedure

For revocation/rotation warnings: review `revocation_status`,
`rotation_status` or `rotation_epoch`; confirm no governed
revocation/rotation runtime exists; classify as manual review unless
explicitly valid; do not delete historical evidence; and do not approve.

## Escalation matrix

Targets: `operator`, `reviewer`, `system_owner`, `security_owner`,
`key_owner`, `key_custodian`, `emergency_revocation_authority`.

Mappings:

- informational/no issue -> reviewer
- missing signature input -> operator
- missing prototype key -> operator/reviewer
- invalid descriptor/envelope -> system_owner
- signed payload hash mismatch -> security_owner + system_owner
- HMAC mismatch -> security_owner
- unsupported algorithm/encoding -> system_owner + security_owner
- key lifecycle issue -> key_owner + key_custodian
- suspected replay -> security_owner + emergency_revocation_authority

Roles are governance labels only until Phase 9 identity/RBAC.

## Reviewer action checklist

Allowed `reviewer_action` values: `no_action_required`,
`manual_review_required`, `reject_signature_until_resolved`. Reviewer
action is guidance only, reviewer action is not approval, reviewer action
must not execute primitive/wrapper/next gate, and the approval boundary
always remains Phase 7D selected-gate manual.

## Approval boundary checklist

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

## Security/privacy checklist

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

## Operator mistake recovery

Cover wrong key used, missing key, wrong descriptor path, wrong envelope
path, stale Phase 8L output, overwritten tmp output, invalid JSON, path
rejected by safety guard, and accidental command with wrong env. For each
case define immediate action, evidence preservation, rerun condition,
escalation if needed, and approval boundary reminder.

## Phase 8O handoff criteria

Require passing focused tests for Phase 8L, Phase 8M, Phase 8N, Phase
8G/8H, Phase 8E export, and Phase 7D wrapper regressions before final
acceptance, plus confirmation of no Phase 8N runtime changes, no
key/cert files, no backend/API/database, no primitive execution, no vault
write, and safe demonstration coverage for missing input, not_ready,
valid, mismatch, and hash mismatch scenarios.

## Non-goals

Phase 8N does not add runtime scripts, signing implementation, verifier
implementation, key management implementation, key generation, key/cert
files, KMS/Secrets Manager, backend/API/database, wrapper changes,
primitive execution, vault reads/writes, next-gate automation, chain
execution, affiliate content generation, autopublish, marketplace
submission, or production deployment.

## Phase 8M verifier prototype boundary

Phase 8M remains the verifier-side local prototype runtime. Phase 8N only
documents operator/reviewer procedures for verifier outcomes and does not
modify Phase 8M runtime behavior.

## Phase 8L signing prototype boundary

Phase 8L remains the signing-side local prototype runtime. Phase 8N only
documents operator/reviewer procedures for signing output states and does
not modify Phase 8L runtime behavior.

## Phase 8K key management boundary

Phase 8K remains design-only key management governance. Phase 8N uses key
roles/lifecycle labels for review guidance only. `key_management_runtime_status`
remains `not_implemented`.

## Phase 8J verifier design boundary

Phase 8J remains detached signature verifier design. Phase 8N turns
verifier interpretation into operator/reviewer procedures and remains
runbook-only.

## Phase 8H verifier boundary

Phase 8H remains the hash-only export integrity verifier. Phase 8N does
not modify Phase 8H runtime.

## Phase 8E export boundary

Phase 8E remains the export pack builder. Phase 8N does not modify Phase
8E runtime.

## Phase 7D approval boundary

Approval remains Phase 7D selected-gate manual boundary. Phase 8N does
not call the Phase 7D wrapper, does not call primitives, does not write
vault, and does not trigger the next gate.

## Test strategy

`tests/test_phase8n_signature_runbook_incident_review_pack.py` verifies
file existence/status, doc scope safety, required sections, ordered
operator/reviewer procedures, evidence preservation content, incident and
outcome matrices, procedure-specific guidance, escalation and reviewer
action semantics, approval boundary reminders, security/privacy handling,
operator mistake recovery, Phase 8O handoff criteria, documentation
cross-references, protected runtime file hashes, static safety on new
Phase 8N docs, and repo-wide artifact safety.

## Acceptance criteria

- task exists
- runbook doc exists
- test exists
- no Phase 8N runtime script exists
- task contains `phase8n_status: success`
- runbook doc contains all required status tokens
- runbook doc states docs/tests/runbook-pack only
- runbook doc states no new runtime scripts/signing/verifier/key
  management implementation
- runbook doc contains all required sections and matrices
- runbook doc preserves the approval boundary:
  verified signature remains not approval, verification passed remains
  not approval, reviewer action remains review guidance only
- ROADMAP, PROJECT_STATE, PHASE8M, PHASE8L, PHASE8K, and PHASE8J
  reference Phase 8N additively
- protected runtime files remain unchanged
- no backend/API/database file is added
- no key/cert file is added
- no package.json is added

## Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase8n_signature_runbook_incident_review_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase8k_key_management_design.py
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
test "$(stat -c '%a' scripts/dev/run_phase8m_detached_signature_verifier.sh)" = "755"
git ls-files -s scripts/dev/run_phase8m_detached_signature_verifier.sh | grep "^100755 "
test "$(stat -c '%a' scripts/dev/run_phase8l_detached_signature.sh)" = "755"
git ls-files -s scripts/dev/run_phase8l_detached_signature.sh | grep "^100755 "
test "$(stat -c '%a' scripts/dev/run_phase8g_export_integrity.sh)" = "755"
git ls-files -s scripts/dev/run_phase8g_export_integrity.sh | grep "^100755 "
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Major-phase checkpoint policy

Phase 8N is part of `feature/phase8-signature-governance-completion`.
Phase 8N should create a checkpoint commit only. No PR should be opened
after Phase 8N alone. Because Phase 8N does not add runtime code,
focused tests plus Phase 8M/8L/8K/8J regressions are required. Full
suite is deferred to Phase 8O final acceptance unless focused checks fail
or protected runtime changes occur.

## Known limitations

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

## Final status target

phase8n_status: success
