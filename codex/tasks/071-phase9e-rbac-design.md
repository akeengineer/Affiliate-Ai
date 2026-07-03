# Task 071 — Phase 9E RBAC Design

phase9e_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

rbac_design_status: design_only

rbac_runtime_status: not_implemented

identity_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

phase9_branch_workflow: enabled

## 1. Purpose

Phase 9E designs the role-based access control boundary for future local RBAC
policy prototype work, mapping RBAC subjects and roles onto the Phase 9B actor
metadata schema while guaranteeing that RBAC never becomes approval. Phase 9E is
docs/tests design-only.

## 2. Scope

- docs/tests design-only
- RBAC concept, subject, role, permission, resource, action, decision,
  obligation, denial, and audit event models
- policy versioning and policy evaluation lifecycle design
- role-to-actor metadata mapping and governance role mapping
- product workflow, signature/export, and registry/attribution resource models
- approval boundary preservation and future Phase 9F boundary
- no runtime scripts, no shell runner, no policy engine, no RBAC enforcement, no
  permission gate, no authentication runtime, no login, no session runtime, no
  user store, no backend/API/database, no wrapper behavior change, no primitive
  execution, no vault read/write, no new mutation path

## 3. Files

- `codex/tasks/071-phase9e-rbac-design.md`
- `docs/PHASE9E_RBAC_DESIGN.md`
- `tests/test_phase9e_rbac_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive updates to `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`

No Phase 9E runtime script or shell runner is added. The RBAC boundary is
documentation/test driven only.

## 4. Status model

- `phase9e_status: success` — the task, design doc, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — unchanged.
- `identity_boundary_status: design_only` — unchanged.
- `actor_metadata_schema_status: design_only` — unchanged.
- `actor_metadata_runtime_status: local_registry_prototype` — unchanged.
- `local_operator_registry_status: prototype_local_only` — unchanged.
- `actor_attribution_status: local_report_prototype` — unchanged.
- `rbac_design_status: design_only` — the RBAC boundary is designed, not
  implemented.
- `rbac_runtime_status: not_implemented` — no RBAC runtime exists.
- `identity_runtime_status: not_implemented` — no identity runtime exists.
- `authentication_runtime_status: not_implemented` — no authentication runtime.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `phase9_branch_workflow: enabled` — Phase 9E continues the Phase 9 branch.

## 5. RBAC design objective

Provide a single conceptual RBAC model — subjects, roles, permissions,
resources, actions, decisions, obligations, denials, and audit events — that a
future local policy prototype can adopt, guaranteeing RBAC eligibility and RBAC
decisions never become product approval.

## 6. Current trust boundary after Phase 9D

Phase 9A defines the identity boundary; Phase 9B defines the actor metadata
schema; Phase 9C implements a local registry prototype; Phase 9D implements a
local attribution report prototype; Phase 9E adds RBAC design only. No RBAC
runtime, policy engine, permission enforcement, or authentication runtime
exists. Operator identity remains unauthenticated or operator-declared.

## 7. RBAC concept model

Defines `subject`, `role`, `permission`, `resource`, `action`, `condition`,
`decision`, `obligation`, `denial`, and `audit_event`. Design-only: no runtime
evaluator, no policy file, and RBAC eligibility is not approval.

## 8. Subject model

Fields `subject_id`, `subject_actor_id`, `subject_actor_type`,
`subject_identity_assurance`, `subject_identity_source`, `subject_role_labels`,
`subject_session_reference`, `subject_registry_reference`,
`subject_attribution_reference`, `approval_boundary_statement`. Subject is not
authentication by itself, is not approval, and maps to Phase 9B actor metadata.

## 9. Role model

Roles `affiliate_operator`, `affiliate_reviewer`, `affiliate_signer`,
`affiliate_key_owner`, `affiliate_key_custodian`, `affiliate_security_owner`,
`affiliate_system_owner`, `affiliate_emergency_revocation_authority`,
`affiliate_auditor`, `affiliate_test_operator`, `affiliate_automation_placeholder`,
each with purpose, mapped actor_type, mapped actor_role_label, allowed/forbidden
conceptual permissions, and approval boundary. Role is not runtime permission in
Phase 9E.

## 10. Permission model

Shape `permission_id`, `permission_description`, `resource_type`,
`allowed_actions`, `denied_actions`, `required_identity_assurance`,
`required_actor_role_labels`, `obligations`, `approval_boundary_statement`.
Permission is design-only, does not approve product action, and does not execute
primitive.

## 11. Resource model

Resource types include `product_candidate`, `scoring_report`, `weekly_report`,
`promotion_gate`, `manual_decision`, `finalization_decision`,
`phase7d_selected_gate`, `audit_store_record`, `audit_store_report`,
`audit_export_pack`, `export_integrity_report`, `detached_signature_envelope`,
`signature_verifier_report`, `signature_incident_runbook`, `final_acceptance_pack`,
`actor_registry`, `actor_attribution_report`, `rbac_policy`, `test_fixture`.

## 12. Action model

Action categories `read`, `list`, `build_report`, `validate`, `export`,
`sign_local_prototype`, `verify_local_prototype`, `review`, `annotate`,
`register_actor`, `attribute_actor`, `approve_selected_gate`, `execute_primitive`,
`manage_key_governance_metadata`, `manage_policy_design`, `test_generate_fixture`.
`approve_selected_gate` remains Phase 7D only; `execute_primitive` remains
protected.

## 13. Decision model

Decisions `allow`, `deny`, `conditional_allow`, `manual_review_required`,
`not_applicable`. allow is not product approval; allow must not trigger wrapper
or execute primitive; conditional_allow must not bypass manual approval.

## 14. Obligation model

Obligations `require_actor_attribution`, `require_manual_review`,
`require_phase7d_selected_gate`, `require_signature_verification_review`,
`require_final_acceptance_review`, `require_privacy_review`,
`require_key_governance_review`, `require_incident_review`, `require_audit_record`,
`require_no_primitive_execution`. Design-only.

## 15. Denial model

Denial reasons `subject_missing`, `role_missing`, `permission_missing`,
`insufficient_identity_assurance`, `resource_not_allowed`, `action_not_allowed`,
`approval_boundary_required`, `actor_attribution_required`, `privacy_review_required`,
`key_governance_review_required`, `primitive_execution_blocked`, `next_gate_blocked`.
Advisory in Phase 9E.

## 16. Audit event model

Future RBAC audit event fields `rbac_event_id`, `policy_version`, `subject_id`,
`subject_actor_id`, `resource_type`, `resource_id`, `action`, `decision`,
`obligations`, `denial_reasons`, `reviewer_action`, `actor_attribution_reference`,
`approval_boundary_statement`, `event_timestamp_utc`. Not implemented at runtime;
RBAC audit event is not approval.

## 17. Policy versioning model

Design version `phase9e.rbac_design.v1`; initial future policy version
`phase9f.local_rbac_policy.v1`; additive vs breaking changes; compatible with
`actor_schema_version` `phase9b.actor_metadata.v1`, Phase 9C registry, and Phase
9D attribution report.

## 18. Policy evaluation lifecycle design

Future lifecycle: load local policy; load subject actor metadata; load requested
resource/action; evaluate role mapping; evaluate identity assurance requirement;
evaluate resource/action permission; produce decision; attach obligations; write
local advisory report; preserve approval boundary. Phase 9E implements none of
this runtime.

## 19. Role-to-actor metadata mapping

`affiliate_operator -> human_operator/operator`,
`affiliate_reviewer -> reviewer/reviewer`, `affiliate_signer -> signer/signer`,
`affiliate_key_owner -> key_owner/key_owner`,
`affiliate_key_custodian -> key_custodian/key_custodian`,
`affiliate_security_owner -> security_owner/security_owner`,
`affiliate_system_owner -> system_owner/system_owner`,
`affiliate_emergency_revocation_authority -> emergency_revocation_authority/emergency_revocation_authority`,
`affiliate_auditor -> reviewer or human_operator/auditor`,
`affiliate_test_operator -> test_fixture/test`,
`affiliate_automation_placeholder -> automation_placeholder/automation`. Governance
metadata only.

## 20. Governance role mapping

Phase 8K/9B labels `key_owner`, `key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`, `operator`, `reviewer`, `signer`, `automation`,
`test`. Governance role label is not runtime permission and is not approval.

## 21. Product workflow resource model

Conceptual permission boundaries for `score_product`, `generate_weekly_report`,
`import_csv`, `promote_candidate`, `create_manual_decision`, `finalize_decision`,
`selected_gate_wrapper`. `selected_gate_wrapper` remains Phase 7D selected manual
approval boundary; RBAC design does not call these scripts.

## 22. Signature/export resource model

Conceptual permission boundaries for build audit export pack, verify export
integrity, local detached signature creation, local detached signature
verification, signature incident review, final acceptance review. Signature
verification remains not approval; final acceptance remains not approval; RBAC
design does not call Phase 8 scripts.

## 23. Registry/attribution resource model

Conceptual permission boundaries for local operator registry build/list/report,
actor attribution report build, actor metadata validation, actor attribution
review. Registry presence is not authentication; actor attribution is not
approval; RBAC design does not call Phase 9C/9D scripts.

## 24. Approval boundary preservation

RBAC design is not enforcement; RBAC policy/eligibility/decision are not
approval; allow is not approval; role label is not runtime permission;
governance role label is not approval; approval remains Phase 7D selected-gate
manual boundary; RBAC design must not trigger wrapper, execute primitives,
trigger next gate, or set approval flags.

## 25. Non-authentication boundary

Phase 9E does not authenticate subjects or verify identity; the subject model is
not login and not session; future authentication requires a separate phase.

## 26. Non-approval boundary

RBAC governs future eligibility only; eligibility does not approve business
action; approval remains a separate selected-gate manual act; future RBAC cannot
bypass Phase 7D.

## 27. Future local policy prototype boundary

Future Phase 9F may add a local RBAC policy prototype; it must remain local-only
unless explicitly changed later, must not implement authentication, must not
call wrapper/primitives, must produce advisory decisions only, and must preserve
the Phase 7D approval boundary.

## 28. Compatibility with Phase 9D

Phase 9E uses Phase 9D attribution reports as future subject/evidence context and
does not modify Phase 9D runtime; actor attribution remains not authentication or
approval.

## 29. Compatibility with Phase 9C

Phase 9E uses Phase 9C registry as future subject source and does not modify
Phase 9C runtime; registry presence remains not authentication or approval.

## 30. Compatibility with Phase 9B

Phase 9E maps roles and subjects to the Phase 9B actor metadata schema; schema
validity remains not approval.

## 31. Compatibility with Phase 9A

Phase 9E preserves the Phase 9A identity boundary; operator identity remains
unauthenticated or operator-declared.

## 32. Compatibility with Phase 8O/8L/8M

Phase 9E defines conceptual permissions around final acceptance, signing, and
verification; it does not modify Phase 8 runtime. Signature verification remains
not approval; final acceptance remains not approval.

## 33. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; RBAC design does not
modify Phase 7D, must not execute primitives, and must not approve anything.

## 34. Failure taxonomy

`subject_missing`, `subject_unknown`, `subject_identity_assurance_insufficient`,
`role_missing`, `role_unknown`, `permission_missing`, `permission_unknown`,
`resource_unknown`, `action_unknown`, `policy_version_missing`,
`policy_version_incompatible`, `obligation_unmet`, `approval_boundary_required`,
`actor_attribution_required`, `privacy_review_required`,
`primitive_execution_blocked`, `next_gate_blocked`, `approval_flag_present`. Each
maps to a severity (`info`, `warning`, `critical`), an incident classification
(`none`, `rbac_policy_review_required`, `identity_assurance_review_required`,
`actor_scope_review_required`, `approval_boundary_review_required`,
`privacy_review_required`, `primitive_execution_blocked`, `next_gate_blocked`),
and a reviewer action (`no_action_required`, `manual_review_required`,
`reject_rbac_policy_until_resolved`, `reject_action_until_resolved`).

## 35. Reviewer action mapping

`no_action_required`, `manual_review_required`, `reject_rbac_policy_until_resolved`,
`reject_action_until_resolved`. Reviewer action is guidance only, is not approval,
and must not trigger the wrapper, execute primitives, or trigger the next gate.

## 36. Non-goals

Phase 9E does not implement RBAC runtime, policy engine, permission enforcement,
local policy prototype, authentication, login, sessions, user store,
OIDC/OAuth/SAML, external identity provider, backend/API/database, key custody,
production signing, or production verifier; does not modify Phase 9C/9D runtime,
Phase 8 runtime, or the Phase 7D wrapper; executes no primitives; writes no
vault; approves nothing; triggers no next gate; adds no chain execution; and
creates no production deployment.

## 37. Test strategy

`tests/test_phase9e_rbac_design.py` verifies file existence and status tokens,
scope safety, required sections, RBAC concept assertions, subject/role/permission/
resource/action assertions, decision/obligation/denial assertions, audit/policy
lifecycle assertions, role and governance mapping assertions, workflow/resource
compatibility assertions, approval boundary assertions, future Phase 9F boundary
assertions, compatibility assertions, failure taxonomy assertions, documentation
regressions, protected runtime file existence, static safety on new Phase 9E
files, and repo-wide artifact safety. No Phase 9E runtime script or shell runner
is added.

## 38. Acceptance criteria

- task exists and contains `phase9e_status: success`
- design doc exists and contains all required status tokens and sections
- test exists
- doc states docs/tests design-only scope and safety statements
- doc defines the RBAC concept, subject, role, permission, resource, action,
  decision, obligation, denial, and audit event models
- doc defines policy versioning, evaluation lifecycle, and role/governance
  mappings
- doc defines the failure taxonomy and reviewer action mapping
- doc states the approval boundary statements and future Phase 9F boundary
- ROADMAP, PROJECT_STATE, PHASE9D, PHASE9C, PHASE9B, PHASE9A, and PHASE8O
  reference Phase 9E additively
- protected runtime files remain unchanged
- no Phase 9E runtime script/shell runner/policy engine/policy file/auth/backend/
  key files are added
- RBAC design remains not enforcement and RBAC eligibility remains not approval
- approval remains Phase 7D selected-gate manual boundary

## 39. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9e_rbac_design.py
python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase9b_actor_metadata_schema_design.py
python -m pytest -q tests/test_phase9a_operator_identity_boundary_design.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## 40. Known limitations

- design only
- no RBAC runtime, no policy engine, no permission enforcement, no local policy
  prototype, no authentication, no login, no session runtime, no user store, no
  enterprise identity, no governed key custody, no strong non-repudiation, no
  backend/API/database, no production deployment

## 41. Final status target

phase9e_status: success
