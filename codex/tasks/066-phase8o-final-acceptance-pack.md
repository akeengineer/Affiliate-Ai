# Task 066 — Phase 8O Final Acceptance Pack

phase8o_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

runbook_runtime_status: docs_only

phase8_major_branch_status: ready_for_pr_after_full_suite

major_phase_branch_workflow: enabled

## Purpose

Phase 8O closes the Phase 8 signature governance workflow by producing
the final acceptance pack for the Phase 8J-8N major branch. Phase 8O
adds the final acceptance task, documentation, and tests that define the
local end-to-end evidence/signature/verifier/runbook acceptance posture
before the major Phase 8 PR.

Phase 8O does not implement production signing, production verification,
key management runtime, backend, database, or deployment.

## Scope

- local-only final acceptance pack
- final acceptance report
- final scenario matrix
- major Phase 8 PR readiness checklist
- full-suite readiness criteria
- missing input scenario
- signature not-ready scenario
- valid local prototype signature scenario
- signature mismatch scenario
- signed payload hash mismatch scenario
- no new signing model
- no new verifier model
- no production signing
- no production verifier
- no key management runtime
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

- `codex/tasks/066-phase8o-final-acceptance-pack.md`
- `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- `tests/test_phase8o_final_acceptance_pack.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to
  `docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`
- additive updates to
  `docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`
- additive updates to
  `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`

Note: no Phase 8O builder or shell runner is added. The final acceptance
pack is documentation/test driven only, which preserves the existing
runtime surface and avoids writing outside the established tmp roots.

## Status model

- `phase8o_status: success` — the Phase 8 final acceptance task,
  documentation, and tests exist, and focused/full verification
  expectations are documented.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains
  the Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — the
  documented Phase 8 posture now includes the final acceptance pack.
- `signing_implementation_status: prototype_local_only` — signing remains
  the Phase 8L local prototype only.
- `signature_runtime_status: local_prototype` — Phase 8L remains the only
  signature runtime.
- `signature_verifier_runtime_status: local_prototype` — Phase 8M remains
  the only verifier runtime.
- `key_management_runtime_status: not_implemented` — key management
  runtime does not exist.
- `runbook_runtime_status: docs_only` — runbook and final acceptance
  remain documentation-only guidance layers.
- `phase8_major_branch_status: ready_for_pr_after_full_suite` — the major
  branch is PR-ready only after the required focused checks and full suite
  pass.
- `major_phase_branch_workflow: enabled` — Phase 8O is the final local
  checkpoint before the major Phase 8 PR.

## Final acceptance objective

Provide a single final acceptance reference that demonstrates and
documents the complete local Phase 8 evidence/signature/verifier/runbook
flow, including the five required scenarios, the evidence that must be
preserved, the approval boundary that must never be crossed, the major
Phase 8 PR readiness checklist, and the requirement to run the full suite
before opening the branch PR.

## Current trust boundary

- Phase 8E creates export packs.
- Phase 8G/8H verify hash-only export integrity.
- Phase 8I finalizes detached signature design.
- Phase 8J designs verifier interpretation.
- Phase 8K designs key management governance.
- Phase 8L implements local-only signing prototype.
- Phase 8M implements local-only verifier prototype.
- Phase 8N provides incident runbook and review pack.
- Phase 8O finalizes local acceptance only.
- No production signing exists.
- No production verifier exists.
- No key management runtime exists.
- No authenticated operator identity exists.
- No enterprise non-repudiation exists.
- Durable audit remains local/tmp workflow.
- Final acceptance is evidence only, not approval.

## Final acceptance pack contents

Required pack contents:

- Phase 8 status summary
- Phase 8J-8N checkpoint summary
- scenario matrix
- acceptance results table
- evidence preservation checklist
- safety boundary statements
- protected runtime behavior statement
- full-suite readiness checklist
- PR readiness checklist
- known limitations

## Acceptance scenario matrix

Matrix rows:

- `missing_input`
- `signature_not_ready`
- `valid_local_prototype_signature`
- `signature_mismatch`
- `signed_payload_hash_mismatch`

Each row must map:

- scenario objective
- required prior artifacts
- operator action
- expected Phase 8L status if applicable
- expected Phase 8M status
- expected `verification_status`
- expected `signature_status`
- expected `incident_classification`
- expected `reviewer_action`
- expected exit behavior
- evidence to preserve
- approval boundary reminder

## Missing input scenario

- run Phase 8M without Phase 8L descriptor/envelope
- expected `signature_verification_status: skipped_missing_signature_inputs`
- expected `verification_status: empty`
- expected `signature_status: not_present`
- expected exit `0`
- do not fabricate descriptor/envelope
- do not approve

## Signature not-ready scenario

- run Phase 8L without `AFFILIATE_PHASE8L_PROTOTYPE_KEY`
- run Phase 8M against the not-ready envelope
- expected Phase 8L `signing_status: skipped_missing_prototype_key`
- expected Phase 8M
  `signature_verification_status: skipped_signature_not_ready`
- expected `verification_status: warning`
- expected `signature_status: not_ready`
- expected exit `0`
- do not approve

## Valid local prototype signature scenario

- run Phase 8L with `AFFILIATE_PHASE8L_PROTOTYPE_KEY` in a controlled
  local environment
- run Phase 8M with the same environment key
- expected Phase 8L `signing_status: signed_local_prototype`
- expected Phase 8M
  `signature_verification_status: verified_local_prototype`
- expected `verification_status: valid`
- expected `signature_status: verification_passed`
- expected `signed_payload_hash_status: match`
- expected `reviewer_action: no_action_required`
- expected exit `0`
- verified signature is not approval
- verification passed is not approval

## Signature mismatch scenario

- sign with key A and verify with key B in a controlled local environment
- expected Phase 8M
  `signature_verification_status: failed_signature_mismatch`
- expected `verification_status: invalid`
- expected `signature_status: verification_failed`
- expected `incident_classification: signature_integrity_failure`
- expected `reviewer_action: reject_signature_until_resolved`
- expected nonzero exit
- preserve evidence
- do not approve

## Signed payload hash mismatch scenario

- tamper descriptor after Phase 8L envelope creation in a controlled test
  fixture only
- expected Phase 8M
  `signature_verification_status: failed_signed_payload_hash_mismatch`
- expected `signed_payload_hash_status: mismatch`
- expected `verification_status: invalid`
- expected `signature_status: verification_failed`
- expected `incident_classification: signature_integrity_failure`
- expected `reviewer_action: reject_signature_until_resolved`
- expected nonzero exit
- preserve evidence
- do not approve

## Evidence preservation requirements

Include:

- Phase 8E export manifest
- Phase 8G/8H integrity report
- Phase 8L signed payload descriptor
- Phase 8L detached signature envelope
- Phase 8L summary JSON/MD
- Phase 8M verification JSON/MD
- Phase 8N runbook reference
- scenario name
- command metadata without secrets
- prototype key presence indicator only, never raw key
- expected status
- actual status
- result
- reviewer action
- incident classification
- limitations

Rules:

- preserve evidence without mutating source artifacts
- do not write raw prototype key
- do not write vault
- do not delete failed evidence

## Final report schema

Local/documented report fields:

- `phase8o_status`
- `durable_audit_store_status`
- `phase7d_runtime_readiness`
- `signing_implementation_status`
- `signature_runtime_status`
- `signature_verifier_runtime_status`
- `key_management_runtime_status`
- `runbook_runtime_status`
- `phase8_major_branch_status`
- `major_phase_branch_workflow`
- `scenario_count`
- `passed_scenarios`
- `failed_scenarios`
- `scenario_results`
- `protected_runtime_status`
- `full_suite_required`
- `full_suite_status`
- `pr_readiness_status`
- `approval_boundary_statement`
- `safety_statement`
- `limitations`

## Major Phase 8 PR readiness checklist

- 8J checkpoint exists
- 8K checkpoint exists
- 8L checkpoint exists
- 8M checkpoint exists
- 8N checkpoint exists
- 8O checkpoint exists
- focused 8O tests pass
- 8M/8L/8K/8J regressions pass
- 8H/8G regressions pass
- 8E export regression passes
- 7D wrapper regression passes
- full suite passes
- shell runner permissions correct
- hardcoded path grep clean
- git diff --check clean
- no key/cert files
- no backend/API/database files
- no package.json
- no primitive execution
- no vault write
- no approval inference
- PR body states local prototype only
- PR body states signature/verified signature/final acceptance is not approval

## Full-suite requirement

- Unlike Phase 8J-8N, Phase 8O closes the major Phase 8 branch.
- Full suite must be run after Phase 8O focused verification passes.
- Full suite command:
  `env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q`
- Major Phase 8 PR must not be opened until full suite passes.

## Merge readiness criteria

- focused 8O tests pass
- Phase 8M/8L/8K/8J regressions pass
- Phase 8H/8G regressions pass
- Phase 8E export regression passes
- Phase 7D wrapper regression passes
- full suite passes
- no protected runtime behavior changes except sanctioned 8L/8M/optional
  8O additions
- no backend/API/database files
- no key/cert files
- no approval inference
- worktree clean
- one major Phase 8 PR opened from
  `feature/phase8-signature-governance-completion`

## Non-goals

Phase 8O does not:

- implement new signing model
- implement new verifier model
- implement production signing
- implement production verification
- implement key management
- generate keys
- handle private keys
- create key files
- create certificate files
- implement encryption
- implement KMS/Secrets Manager
- implement backend/API/database
- modify Phase 8M verifier runtime behavior
- modify Phase 8L signing runtime behavior
- modify Phase 8G/8H verifier runtime behavior
- modify Phase 8E export behavior
- modify Phase 7D wrapper behavior
- execute primitives
- approve anything
- trigger next gate
- add chain execution
- create production deployment

## Phase 8N runbook boundary

- Phase 8N remains runbook-only.
- Phase 8O uses Phase 8N as incident review reference.
- Phase 8O does not modify the runbook except an additive pointer.

## Phase 8M verifier prototype boundary

- Phase 8M remains local-only verifier prototype.
- Phase 8O validates verifier scenarios without modifying verifier runtime.
- Phase 8O adds no new verifier model.

## Phase 8L signing prototype boundary

- Phase 8L remains local-only signing prototype.
- Phase 8O validates signing scenarios without modifying signing runtime.
- Phase 8O adds no new signing model.

## Phase 8K key management boundary

- Phase 8K remains design-only key management governance.
- `key_management_runtime_status` remains `not_implemented`.

## Phase 8J verifier design boundary

- Phase 8J remains design-only verifier interpretation source.

## Phase 8H verifier boundary

- Phase 8H remains hash-only export integrity verifier.
- Phase 8O must not modify Phase 8H runtime.

## Phase 8E export boundary

- Phase 8E remains export pack builder.
- Phase 8O must not modify Phase 8E runtime.

## Phase 7D approval boundary

- approval remains Phase 7D selected-gate manual boundary
- Phase 8O does not call Phase 7D wrapper except via regression tests
- Phase 8O does not call primitives
- Phase 8O does not write vault
- Phase 8O does not trigger next gate
- final acceptance is not approval

## Test strategy

`tests/test_phase8o_final_acceptance_pack.py` verifies file existence and
status tokens, scope safety, required sections, scenario matrix content,
scenario-specific expectations, evidence preservation rules, final report
schema, PR/merge readiness criteria, full-suite requirements, approval
boundary reminders, documentation cross-references, protected runtime
hashes, static safety on new Phase 8O files, and repo-wide artifact
safety. No Phase 8O runtime builder/runner is added; the acceptance pack
is documentation/test driven only.

## Acceptance criteria

- task exists
- final acceptance doc exists
- test exists
- task contains `phase8o_status: success`
- doc contains all required status tokens
- doc states the local-only final acceptance pack scope and scenario set
- doc contains all required sections
- doc captures the missing input, not_ready, valid signature, signature
  mismatch, and signed payload hash mismatch scenarios
- doc captures evidence preservation rules and final report schema
- doc captures PR readiness, full-suite requirement, and merge readiness
- ROADMAP, PROJECT_STATE, PHASE8N, PHASE8M, PHASE8L, PHASE8K, and PHASE8J
  reference Phase 8O additively
- protected runtime files remain unchanged
- no new signing model, verifier model, key-management implementation, or
  runtime files are added
- final acceptance remains not approval

## Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8n_signature_runbook_incident_review_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase8k_key_management_design.py
python -m pytest -q tests/test_phase8j_detached_signature_verifier_design.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m pytest -q tests/test_phase8e_audit_export_pack.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
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

## Full verification commands

```text
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
git diff --check
git status --short --branch
```

## Major-phase checkpoint policy

- Phase 8O is part of `feature/phase8-signature-governance-completion`.
- Phase 8O should create a checkpoint commit.
- Phase 8O closes major Phase 8 local work.
- Full suite is required after Phase 8O focused verification.
- After full suite passes, open one PR for the major Phase 8 branch.

## Known limitations

- local final acceptance only
- no production signing
- no production verifier
- no key management runtime
- no governed key custody
- no authenticated operator identity
- no enterprise non-repudiation
- no backend/API/database
- no production deployment
- no marketplace integration
- no autopublish

## Final status target

phase8o_status: success
