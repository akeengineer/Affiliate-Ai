# Task 074 — Phase 10A Governed Runtime Integration Readiness Design

phase10a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

rbac_design_status: design_only

rbac_policy_status: local_advisory_prototype

rbac_runtime_status: local_advisory_prototype

rbac_enforcement_status: not_implemented

governed_runtime_integration_status: design_only

integration_runtime_status: not_implemented

identity_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

backend_api_database_status: not_implemented

phase10_branch_workflow: enabled

## 1. Purpose

Phase 10A defines the governed runtime integration readiness boundary after
Phase 9. It designs how future local-only evidence binding may safely connect
Phase 8 evidence/signature artifacts and Phase 9 actor/RBAC governance context
without implementing integration runtime, authentication, RBAC enforcement,
backend/API/database behavior, key custody, production signing, or production
verification.

## 2. Scope

- docs/tests design-only
- governed integration readiness model
- evidence source model
- actor context source model
- advisory RBAC context source model
- signature context source model
- approval boundary source model
- integration readiness package model
- future integration input contract
- future integration output contract
- evidence binding model
- actor binding model
- RBAC advisory binding model
- signature binding model
- approval boundary preservation model
- compatibility with Phase 9G/9F/9D/9C
- compatibility with Phase 8O/8M/8L/8E
- compatibility with Phase 7D
- runtime safety model
- no runtime scripts
- no shell runner
- no integration runtime
- no authentication runtime
- no RBAC enforcement
- no production policy engine
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path

## 3. Files

- `codex/tasks/074-phase10a-governed-runtime-integration-readiness-design.md`
- `docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`
- `tests/test_phase10a_governed_runtime_integration_readiness_design.py`
- additive update to `docs/ROADMAP.md`
- additive update to `docs/PROJECT_STATE.md`
- additive update to `docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md`
- additive update to `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`
- additive update to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive update to `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive update to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`

No runtime scripts, shell runners, integration modules, auth modules, RBAC
enforcement modules, policy-engine files, backend/API/database files, workflow
files, deployment files, `package.json`, key files, or certificate files are
added.

## 4. Status model

- `phase10a_status: success` — task, design doc, tests, and additive references
  exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  authoritative selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — Phase 8 evidence
  state remains unchanged.
- `identity_boundary_status: design_only` — identity interpretation remains a
  design artifact.
- `actor_metadata_schema_status: design_only` — actor schema remains design-only.
- `actor_metadata_runtime_status: local_registry_prototype` — actor metadata
  runtime remains local registry prototype only.
- `local_operator_registry_status: prototype_local_only` — registry remains a
  local prototype.
- `actor_attribution_status: local_report_prototype` — actor attribution remains
  a local evidence report prototype.
- `rbac_design_status: design_only` — RBAC boundary remains design-only.
- `rbac_policy_status: local_advisory_prototype` — RBAC policy remains advisory.
- `rbac_runtime_status: local_advisory_prototype` — no enforcement runtime is
  added.
- `rbac_enforcement_status: not_implemented` — unchanged.
- `governed_runtime_integration_status: design_only` — new Phase 10A status.
- `integration_runtime_status: not_implemented` — no runtime integration exists.
- `identity_runtime_status: not_implemented` — unchanged.
- `authentication_runtime_status: not_implemented` — unchanged.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `backend_api_database_status: not_implemented` — no backend/API/database is
  introduced.
- `phase10_branch_workflow: enabled` — Phase 10 follows major-phase branch
  workflow.

## 5. Phase 10A integration readiness objective

Define a design-only package that future local-only phases may use to bind
evidence, actor, advisory RBAC, signature, and approval-boundary context into a
single readiness report while preserving evidence-only semantics, advisory-only
RBAC semantics, and the Phase 7D selected-gate manual approval boundary.

## 6. Current trust boundary after Phase 9

- Phase 7D remains selected-gate manual approval runtime.
- Phase 8 provides audit/signature/final acceptance evidence.
- Phase 9 provides identity boundary, actor metadata schema, local registry
  prototype, local actor attribution, RBAC design, and local advisory RBAC
  prototype.
- Phase 10A defines readiness only.
- No integration runtime exists.
- No authentication runtime exists.
- No RBAC enforcement exists.
- No production policy engine exists.
- No backend/API/database exists.
- No key management runtime exists.
- Operator identity remains unauthenticated or operator-declared.
- Advisory outputs remain evidence only.
- Approval remains Phase 7D selected-gate manual boundary.

## 7. Governed integration concept model

Concepts:

- `evidence_source`
- `actor_context`
- `rbac_advisory_context`
- `signature_context`
- `approval_boundary_context`
- `integration_readiness_package`
- `integration_binding`
- `compatibility_check`
- `safety_check`
- `reviewer_action`
- `acceptance_evidence`

State:

- The model is design-only.
- No runtime evaluator exists in Phase 10A.
- No integration package is produced in Phase 10A.
- Integration readiness is not approval.

## 8. Evidence source model

Future evidence sources:

- `phase8e_audit_export_pack`
- `phase8g_export_integrity_report`
- `phase8m_signature_verifier_report`
- `phase8o_final_acceptance_pack`
- `phase9d_actor_attribution_report`
- `phase9f_local_rbac_advisory_report`
- `phase7d_selected_gate_evidence`

For each source define:

- source purpose
- expected local path family
- trust level
- mutation boundary
- approval boundary

## 9. Actor context source model

Actor context sources:

- `phase9c_local_operator_registry`
- `phase9d_actor_attribution_report`
- `future_actor_metadata_fields`

State:

- actor context is not authentication
- actor context is not approval
- actor context must not trigger wrapper/primitives

## 10. Advisory RBAC context source model

RBAC context sources:

- `phase9e_rbac_design`
- `phase9f_local_rbac_policy_report`
- `future_rbac_advisory_report`

State:

- RBAC advisory context is not enforcement
- RBAC allow decision is not approval
- RBAC advisory report is evidence only
- RBAC advisory context must not trigger wrapper/primitives

## 11. Signature context source model

Signature context sources:

- `phase8l_local_detached_signature`
- `phase8m_signature_verifier_report`
- `phase8n_signature_incident_runbook`
- `phase8o_final_acceptance_pack`

State:

- signature verification remains not approval
- local signing/verifier remain prototypes
- no production signing exists
- no key management runtime exists

## 12. Approval boundary source model

Approval boundary source:

- `phase7d_selected_gate_manual_boundary`
- `approval_boundary_statement`
- `selected_gate_manual_approval_evidence`

State:

- approval boundary is authoritative only in Phase 7D selected-gate manual boundary
- evidence and advisory context cannot create approval
- integration readiness cannot approve

## 13. Integration readiness package model

Future package fields:

- `package_schema_version`
- `evidence_sources`
- `actor_context`
- `rbac_advisory_context`
- `signature_context`
- `approval_boundary_context`
- `compatibility_checks`
- `safety_checks`
- `reviewer_action`
- `approval_boundary_statement`
- `limitations`

State:

- Phase 10A does not implement this package.
- Future package is evidence only.
- Package validity is not approval.

## 14. Future integration input contract

Conceptual future inputs:

- `audit_export_manifest`
- `export_integrity_report`
- `signature_verifier_report`
- `final_acceptance_pack`
- `local_operator_registry`
- `actor_attribution_report`
- `rbac_advisory_report`
- `selected_gate_boundary_reference`

State:

- Phase 10A does not read these at runtime.
- Future input validation must be local-first.

## 15. Future integration output contract

Conceptual future outputs:

- `governed_integration_readiness_report.json`
- `governed_integration_readiness_report.md`
- `integration_compatibility_matrix`
- `integration_safety_findings`
- `integration_limitations`
- `reviewer_action`

State:

- Phase 10A does not create runtime output.
- Future output must remain evidence only.

## 16. Evidence binding model

Binding fields:

- `evidence_id`
- `evidence_type`
- `evidence_phase`
- `evidence_path`
- `evidence_hash_reference`
- `evidence_integrity_status`
- `evidence_signature_status`
- `approval_boundary_statement`

State:

- evidence binding is not approval
- evidence hash is not approval
- evidence signature is not approval

## 17. Actor binding model

Binding fields:

- `actor_id`
- `actor_type`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_role_labels`
- `actor_registry_reference`
- `actor_attribution_reference`
- `approval_boundary_statement`

State:

- actor binding is not authentication
- actor binding is not approval
- actor binding must not imply non-repudiation

## 18. RBAC advisory binding model

Binding fields:

- `advisory_decision`
- `decision_reason`
- `matched_permission_ids`
- `denied_permission_ids`
- `obligations`
- `denial_reasons`
- `rbac_policy_status`
- `rbac_enforcement_status`
- `approval_boundary_statement`

State:

- RBAC advisory binding is not enforcement
- advisory allow is not approval
- advisory deny is not incident by itself

## 19. Signature binding model

Binding fields:

- `signature_runtime_status`
- `signature_verifier_runtime_status`
- `signing_implementation_status`
- `signature_verification_status`
- `signed_payload_hash_status`
- `key_management_runtime_status`
- `approval_boundary_statement`

State:

- verified signature is not approval
- signature verifier result is not approval
- local signature status is prototype only

## 20. Approval boundary preservation model

- governed integration readiness is not runtime integration
- integration design is not approval
- evidence bundle is not approval
- evidence binding is not approval
- actor binding is not authentication
- actor binding is not approval
- RBAC advisory binding is not enforcement
- RBAC advisory decision is not approval
- advisory allow decision is not approval
- signature verification remains not approval
- final acceptance remains not approval
- approval remains Phase 7D selected-gate manual boundary
- integration readiness must not trigger wrapper
- integration readiness must not execute primitives
- integration readiness must not trigger next gate
- integration readiness must not set approval flags

## 21. Compatibility with Phase 9G

- Phase 10A follows Phase 9G acceptance boundaries.
- Phase 10A does not reopen Phase 9 acceptance semantics.

## 22. Compatibility with Phase 9F

- Phase 10A may reference Phase 9F advisory RBAC reports conceptually.
- Phase 10A does not modify Phase 9F runtime.
- RBAC advisory reports remain evidence only.

## 23. Compatibility with Phase 9D

- Phase 10A may reference Phase 9D actor attribution reports conceptually.
- Phase 10A does not modify Phase 9D runtime.
- Actor attribution remains not approval.

## 24. Compatibility with Phase 9C

- Phase 10A may reference Phase 9C local registry conceptually.
- Phase 10A does not modify Phase 9C runtime.
- Registry presence remains not authentication or approval.

## 25. Compatibility with Phase 8O/8M/8L/8E

- Phase 10A may reference Phase 8 evidence/signature outputs conceptually.
- Phase 10A does not modify Phase 8 runtime.
- Signature verification remains not approval.
- Final acceptance remains not approval.

## 26. Compatibility with Phase 7D

- Phase 7D remains selected-gate manual approval runtime.
- Phase 10A does not modify Phase 7D.
- Integration readiness must not approve.
- Integration readiness must not execute primitives.

## 27. Runtime safety model

- Phase 10A adds no runtime.
- Future runtime must be local-only unless explicitly changed.
- Future runtime must not call Phase 7D wrapper.
- Future runtime must not execute primitives.
- Future runtime must not write vault.
- Future runtime must not mutate Phase 8 or Phase 9 source outputs.
- Future runtime must write only to its own tmp output root.
- Future runtime must be advisory/evidence only unless a later phase explicitly changes scope.

## 28. Non-authentication boundary

- Phase 10A does not authenticate.
- Registry context is not login.
- Actor context is not session.
- Future authentication requires separate design and explicit scope.

## 29. Non-RBAC-enforcement boundary

- Phase 10A does not enforce RBAC.
- RBAC advisory context is not enforcement.
- Advisory allow does not authorize execution.
- Future enforcement requires separate design and explicit scope.

## 30. Non-approval boundary

- Integration readiness does not approve.
- Evidence does not approve.
- Actor attribution does not approve.
- RBAC advisory does not approve.
- Signature verification does not approve.
- Approval remains separate selected-gate manual act.

## 31. Future Phase 10B boundary

- Future Phase 10B may design actor attribution integration with audit store outputs.
- Phase 10B should remain docs/tests design-only unless explicitly changed.
- Phase 10B must preserve Phase 7D approval boundary.
- Phase 10B must not implement authentication or RBAC enforcement.

## 32. Failure taxonomy

For each failure type map severity, incident_classification, and reviewer_action.

Failure types:

- `evidence_source_missing`
- `evidence_source_untrusted`
- `actor_context_missing`
- `actor_context_untrusted`
- `rbac_advisory_context_missing`
- `rbac_advisory_context_untrusted`
- `signature_context_missing`
- `signature_context_untrusted`
- `approval_boundary_missing`
- `compatibility_check_failed`
- `safety_check_failed`
- `identity_assurance_insufficient`
- `rbac_enforcement_confusion`
- `approval_inference_detected`
- `primitive_execution_intent_detected`
- `vault_mutation_intent_detected`
- `backend_integration_out_of_scope`
- `authentication_runtime_out_of_scope`
- `key_management_runtime_out_of_scope`

Allowed severities:

- `info`
- `warning`
- `critical`

Allowed incident classifications:

- `none`
- `integration_readiness_review_required`
- `evidence_review_required`
- `actor_context_review_required`
- `rbac_advisory_review_required`
- `signature_review_required`
- `approval_boundary_review_required`
- `runtime_scope_violation`
- `primitive_execution_blocked`
- `vault_mutation_blocked`

Allowed reviewer actions:

- `no_action_required`
- `manual_review_required`
- `reject_integration_until_resolved`
- `reject_runtime_scope_until_resolved`

## 33. Reviewer action mapping

- `no_action_required`
- `manual_review_required`
- `reject_integration_until_resolved`
- `reject_runtime_scope_until_resolved`

Rules:

- reviewer action is guidance only
- reviewer action is not approval
- reviewer action must not trigger wrapper
- reviewer action must not execute primitives
- reviewer action must not trigger next gate

## 34. Non-goals

Phase 10A does not:

- implement integration runtime
- implement evidence bundle runtime
- implement actor attribution integration runtime
- implement RBAC integration runtime
- implement authentication
- implement RBAC enforcement
- implement production policy engine
- implement login
- implement sessions
- implement user store
- implement OIDC/OAuth/SAML
- implement external identity provider
- implement backend/API/database
- implement key custody
- implement production signing
- implement production verifier
- modify Phase 9F runtime
- modify Phase 9D runtime
- modify Phase 9C runtime
- modify Phase 8 runtime
- modify Phase 7D wrapper
- execute primitives
- write vault
- approve anything
- trigger next gate
- add chain execution
- create production deployment

## 35. Test strategy

Use focused docs/tests verification:

- validate file existence and status tokens
- validate scope safety tokens
- validate required sections
- validate concept, source, package, binding, and compatibility assertions
- validate documentation regression references
- validate protected runtime file hashes remain unchanged
- validate static safety over new Phase 10A task/doc only
- validate repo-wide artifact safety

## 36. Acceptance criteria

- task exists
- design doc exists
- test exists
- no Phase 10A runtime script exists
- no Phase 10A shell runner exists
- task contains `phase10a_status: success`
- doc contains `phase10a_status: success`
- doc contains `governed_runtime_integration_status: design_only`
- doc contains `integration_runtime_status: not_implemented`
- doc contains `rbac_enforcement_status: not_implemented`
- doc contains `authentication_runtime_status: not_implemented`
- doc contains `backend_api_database_status: not_implemented`
- doc contains `key_management_runtime_status: not_implemented`
- doc contains `phase10_branch_workflow: enabled`
- no protected runtime behavior changes occur
- no integration runtime exists
- no authentication exists
- no RBAC enforcement exists
- approval remains Phase 7D selected-gate manual boundary

## 37. Focused verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase10a_governed_runtime_integration_readiness_design.py
python -m pytest -q tests/test_phase9g_phase9_acceptance_pack.py
python -m pytest -q tests/test_phase9f_local_rbac_policy_prototype.py
python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
test "$(stat -c '%a' scripts/dev/run_phase9f_local_rbac_policy.sh)" = "755"
git ls-files -s scripts/dev/run_phase9f_local_rbac_policy.sh | grep "^100755 "
test "$(stat -c '%a' scripts/dev/run_phase9d_actor_attribution_report.sh)" = "755"
git ls-files -s scripts/dev/run_phase9d_actor_attribution_report.sh | grep "^100755 "
test "$(stat -c '%a' scripts/dev/run_phase9c_local_operator_registry.sh)" = "755"
git ls-files -s scripts/dev/run_phase9c_local_operator_registry.sh | grep "^100755 "
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

Expected:

- Phase 10A tests pass.
- Phase 9G/9F/9D/9C focused regressions pass.
- Phase 8O/8M/8L focused regressions pass.
- Phase 7D wrapper regression passes.
- no hardcoded operator path in scripts.
- no Phase 9F behavior change.
- no Phase 9D behavior change.
- no Phase 9C behavior change.
- no Phase 8M verifier behavior change.
- no Phase 8L signing behavior change.
- no Phase 7D wrapper behavior change.
- no auth runtime.
- no RBAC enforcement.
- no integration runtime.
- no production policy engine.
- no authentication.
- no session runtime.
- no user store.
- no backend/API/database files.
- no key files.
- no primitive execution.
- no vault write.
- no Phase 10A runtime script.
- no Phase 10A shell runner.
- existing runner modes remain 755 / 100755.
- governed integration readiness is not runtime integration.
- integration design is not approval.
- approval remains Phase 7D selected-gate manual boundary.

## 38. Known limitations

- design only
- no integration runtime
- no evidence bundle runtime
- no actor/RBAC integration runtime
- no authentication
- no RBAC enforcement
- no production policy engine
- no login
- no session runtime
- no user store
- no enterprise identity
- no governed key custody
- no strong non-repudiation
- no backend/API/database
- no production deployment
- local prototype context only

## 39. Final status target

`phase10a_status: success`
