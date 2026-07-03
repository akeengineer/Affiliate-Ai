# Phase 9E — RBAC Design

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

### Purpose

Phase 9E defines a design-only role-based access control (RBAC) boundary after
Phase 9D. It describes the RBAC concept model, subject/role/permission/resource/
action/decision/obligation/denial models, and the mapping from RBAC roles to the
Phase 9B actor metadata schema, so a future local RBAC policy prototype
(Phase 9F) can be built without ever letting RBAC become approval.

Phase 9E does not implement RBAC runtime, policy engine, permission enforcement,
authentication, login, sessions, backend/API/database, key custody, production
signing, or production verification. It is docs/tests design-only.

### Scope

- docs/tests design-only
- RBAC concept model
- subject model
- role model
- permission model
- resource model
- action model
- decision model
- obligation model
- denial model
- audit event model
- policy versioning
- policy evaluation lifecycle design
- role-to-actor metadata mapping
- governance role mapping
- product workflow resources
- signature/export resources
- registry/attribution resources
- approval boundary preservation
- future local policy prototype boundary
- no runtime scripts
- no shell runner
- no policy engine implementation
- no RBAC enforcement
- no permission gate
- no authentication runtime
- no login
- no session runtime
- no user store
- no backend/API/database
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path

### Current trust boundary after Phase 9D

- Phase 9A defines identity boundary.
- Phase 9B defines actor metadata schema.
- Phase 9C implements local operator registry prototype.
- Phase 9D implements local actor attribution report prototype.
- Phase 9E defines RBAC design only.
- No RBAC runtime exists.
- No policy engine exists.
- No permission enforcement exists.
- No authentication runtime exists.
- Operator identity remains unauthenticated or operator-declared.
- Actor role labels are governance metadata only.
- RBAC design must not become approval.

### RBAC concept model

The RBAC concept model defines these conceptual elements:

- `subject`
- `role`
- `permission`
- `resource`
- `action`
- `condition`
- `decision`
- `obligation`
- `denial`
- `audit_event`

State:

- RBAC concept model is design-only.
- No runtime evaluator exists.
- No policy file is produced in Phase 9E.
- RBAC eligibility is not approval.

### Subject model

A subject is a future identity-bearing actor reference. Fields:

- `subject_id`
- `subject_actor_id`
- `subject_actor_type`
- `subject_identity_assurance`
- `subject_identity_source`
- `subject_role_labels`
- `subject_session_reference`
- `subject_registry_reference`
- `subject_attribution_reference`
- `approval_boundary_statement`

Rules:

- subject is not authentication by itself.
- subject is not approval.
- subject must map to Phase 9B actor metadata.
- subject may reference Phase 9C registry in future.
- subject may reference Phase 9D attribution in future.

### Role model

Roles, each with purpose, mapped actor_type, mapped actor_role_label, allowed
conceptual permissions, forbidden conceptual permissions, and approval boundary:

- `affiliate_operator` — purpose: run safe local operator commands; mapped
  actor_type: human_operator; mapped actor_role_label: operator; allowed
  conceptual permissions: read/list/build_report/validate; forbidden conceptual
  permissions: approve_selected_gate, execute_primitive; approval boundary:
  operator role is not approval.
- `affiliate_reviewer` — purpose: review evidence; mapped actor_type: reviewer;
  mapped actor_role_label: reviewer; allowed conceptual permissions:
  read/review/annotate; forbidden conceptual permissions: approve_selected_gate,
  execute_primitive; approval boundary: reviewer role is not approval.
- `affiliate_signer` — purpose: local prototype signing attribution; mapped
  actor_type: signer; mapped actor_role_label: signer; allowed conceptual
  permissions: sign_local_prototype/verify_local_prototype; forbidden conceptual
  permissions: approve_selected_gate, execute_primitive; approval boundary:
  signer role is not approval.
- `affiliate_key_owner` — purpose: key governance accountability; mapped
  actor_type: key_owner; mapped actor_role_label: key_owner; allowed conceptual
  permissions: manage_key_governance_metadata; forbidden conceptual permissions:
  execute_primitive; approval boundary: key ownership is not approval.
- `affiliate_key_custodian` — purpose: key custody governance; mapped
  actor_type: key_custodian; mapped actor_role_label: key_custodian; allowed
  conceptual permissions: manage_key_governance_metadata; forbidden conceptual
  permissions: execute_primitive; approval boundary: key custody is not approval.
- `affiliate_security_owner` — purpose: policy accountability; mapped
  actor_type: security_owner; mapped actor_role_label: security_owner; allowed
  conceptual permissions: manage_policy_design; forbidden conceptual
  permissions: execute_primitive; approval boundary: security ownership is not
  approval.
- `affiliate_system_owner` — purpose: system accountability; mapped actor_type:
  system_owner; mapped actor_role_label: system_owner; allowed conceptual
  permissions: read/review; forbidden conceptual permissions: execute_primitive;
  approval boundary: system ownership is not approval.
- `affiliate_emergency_revocation_authority` — purpose: future revocation
  governance; mapped actor_type: emergency_revocation_authority; mapped
  actor_role_label: emergency_revocation_authority; allowed conceptual
  permissions: manage_key_governance_metadata; forbidden conceptual permissions:
  execute_primitive; approval boundary: revocation authority is not product
  approval.
- `affiliate_auditor` — purpose: read-only audit review; mapped actor_type:
  reviewer or human_operator; mapped actor_role_label: auditor; allowed
  conceptual permissions: read/list/review; forbidden conceptual permissions:
  approve_selected_gate, execute_primitive; approval boundary: auditor role is
  not approval.
- `affiliate_test_operator` — purpose: test-only fixtures; mapped actor_type:
  test_fixture; mapped actor_role_label: test; allowed conceptual permissions:
  test_generate_fixture; forbidden conceptual permissions: approve_selected_gate,
  execute_primitive; approval boundary: test operator is not approval.
- `affiliate_automation_placeholder` — purpose: reserved automation marker;
  mapped actor_type: automation_placeholder; mapped actor_role_label:
  automation; allowed conceptual permissions: none-enabled; forbidden conceptual
  permissions: all runtime automation; approval boundary: automation placeholder
  is not approval.

Role is not runtime permission in Phase 9E.

### Permission model

Permission shape:

- `permission_id`
- `permission_description`
- `resource_type`
- `allowed_actions`
- `denied_actions`
- `required_identity_assurance`
- `required_actor_role_labels`
- `obligations`
- `approval_boundary_statement`

State:

- permission is design-only.
- permission does not approve product action.
- permission does not execute primitive.
- permission does not trigger wrapper.

### Resource model

Resource types, each with purpose, allowed conceptual actions, forbidden
conceptual actions, mutation boundary, and approval boundary:

- `product_candidate`
- `scoring_report`
- `weekly_report`
- `promotion_gate`
- `manual_decision`
- `finalization_decision`
- `phase7d_selected_gate`
- `audit_store_record`
- `audit_store_report`
- `audit_export_pack`
- `export_integrity_report`
- `detached_signature_envelope`
- `signature_verifier_report`
- `signature_incident_runbook`
- `final_acceptance_pack`
- `actor_registry`
- `actor_attribution_report`
- `rbac_policy`
- `test_fixture`

For every resource, the allowed conceptual actions are read/review-oriented,
forbidden conceptual actions include `execute_primitive` and
`approve_selected_gate`, the mutation boundary is "no mutation from RBAC design",
and the approval boundary is "RBAC decision is not product approval".

### Action model

Action categories (conceptual only):

- `read`
- `list`
- `build_report`
- `validate`
- `export`
- `sign_local_prototype`
- `verify_local_prototype`
- `review`
- `annotate`
- `register_actor`
- `attribute_actor`
- `approve_selected_gate`
- `execute_primitive`
- `manage_key_governance_metadata`
- `manage_policy_design`
- `test_generate_fixture`

State:

- action labels are conceptual only in Phase 9E.
- action labels do not execute anything.
- `approve_selected_gate` remains Phase 7D only.
- `execute_primitive` remains protected and must not be triggered by RBAC design.

### Decision model

Decisions:

- `allow` — meaning: subject is conceptually eligible; allowed use: advisory
  eligibility; forbidden use: product approval or execution; approval boundary:
  allow is not product approval.
- `deny` — meaning: subject is not conceptually eligible; allowed use: advisory
  denial; forbidden use: treating denial as an incident by itself; approval
  boundary: deny is advisory.
- `conditional_allow` — meaning: eligible subject to obligations; allowed use:
  advisory with obligations; forbidden use: bypassing manual approval; approval
  boundary: conditional_allow must not bypass manual approval.
- `manual_review_required` — meaning: a reviewer must decide; allowed use:
  advisory routing; forbidden use: approval; approval boundary: review is not
  approval.
- `not_applicable` — meaning: no RBAC decision applies; allowed use: advisory;
  forbidden use: approval; approval boundary: not applicable is not approval.

Rules:

- allow is not product approval.
- allow must not trigger wrapper.
- allow must not execute primitive.
- deny is not incident by itself.
- conditional_allow must not bypass manual approval.

### Obligation model

Obligations (design-only):

- `require_actor_attribution`
- `require_manual_review`
- `require_phase7d_selected_gate`
- `require_signature_verification_review`
- `require_final_acceptance_review`
- `require_privacy_review`
- `require_key_governance_review`
- `require_incident_review`
- `require_audit_record`
- `require_no_primitive_execution`

Obligations are design-only.

### Denial model

Denial reasons (advisory in Phase 9E):

- `subject_missing`
- `role_missing`
- `permission_missing`
- `insufficient_identity_assurance`
- `resource_not_allowed`
- `action_not_allowed`
- `approval_boundary_required`
- `actor_attribution_required`
- `privacy_review_required`
- `key_governance_review_required`
- `primitive_execution_blocked`
- `next_gate_blocked`

Denial is advisory in Phase 9E.

### Audit event model

Future RBAC audit event fields:

- `rbac_event_id`
- `policy_version`
- `subject_id`
- `subject_actor_id`
- `resource_type`
- `resource_id`
- `action`
- `decision`
- `obligations`
- `denial_reasons`
- `reviewer_action`
- `actor_attribution_reference`
- `approval_boundary_statement`
- `event_timestamp_utc`

State:

- Phase 9E does not implement audit event runtime.
- RBAC audit event is not approval.

### Policy versioning model

- initial future policy version: `phase9f.local_rbac_policy.v1`.
- design version: `phase9e.rbac_design.v1`.
- additive policy changes keep the major version.
- breaking policy changes require a new version.
- compatibility with `actor_schema_version` `phase9b.actor_metadata.v1`.
- compatibility with Phase 9C registry.
- compatibility with Phase 9D attribution report.

### Policy evaluation lifecycle design

Future lifecycle:

1. load local policy
2. load subject actor metadata
3. load requested resource/action
4. evaluate role mapping
5. evaluate identity assurance requirement
6. evaluate resource/action permission
7. produce decision
8. attach obligations
9. write local advisory report
10. preserve approval boundary

Phase 9E implements none of this runtime.

### Role-to-actor metadata mapping

- `affiliate_operator -> human_operator/operator`
- `affiliate_reviewer -> reviewer/reviewer`
- `affiliate_signer -> signer/signer`
- `affiliate_key_owner -> key_owner/key_owner`
- `affiliate_key_custodian -> key_custodian/key_custodian`
- `affiliate_security_owner -> security_owner/security_owner`
- `affiliate_system_owner -> system_owner/system_owner`
- `affiliate_emergency_revocation_authority -> emergency_revocation_authority/emergency_revocation_authority`
- `affiliate_auditor -> reviewer or human_operator/auditor`
- `affiliate_test_operator -> test_fixture/test`
- `affiliate_automation_placeholder -> automation_placeholder/automation`

Mappings are governance metadata only.

### Governance role mapping

Phase 8K/9B governance role labels:

- `key_owner`
- `key_custodian`
- `security_owner`
- `system_owner`
- `emergency_revocation_authority`
- `operator`
- `reviewer`
- `signer`
- `automation`
- `test`

State:

- governance role label is not runtime permission.
- governance role label is not approval.
- governance role label must not trigger wrapper/primitives.

### Product workflow resource model

Conceptual permission boundaries for:

- `score_product`
- `generate_weekly_report`
- `import_csv`
- `promote_candidate`
- `create_manual_decision`
- `finalize_decision`
- `selected_gate_wrapper`

State:

- `selected_gate_wrapper` remains Phase 7D selected manual approval boundary.
- RBAC design does not call these scripts.

### Signature/export resource model

Conceptual permission boundaries for:

- build audit export pack
- verify export integrity
- local detached signature creation
- local detached signature verification
- signature incident review
- final acceptance review

State:

- signature verification remains not approval.
- final acceptance remains not approval.
- local signing/verifier prototypes remain local only.
- RBAC design does not call Phase 8 scripts.

### Registry/attribution resource model

Conceptual permission boundaries for:

- local operator registry build/list/report
- actor attribution report build
- actor metadata validation
- actor attribution review

State:

- registry presence is not authentication.
- actor attribution is not approval.
- RBAC design does not call Phase 9C/9D scripts.

### Approval boundary preservation

- RBAC design is not RBAC enforcement.
- RBAC runtime is not implemented.
- RBAC policy is not approval.
- RBAC eligibility is not approval.
- RBAC decision is not product approval.
- allow decision is not approval.
- role label is not runtime permission.
- governance role label is not approval.
- actor metadata is not approval.
- actor attribution is not approval.
- registry presence is not authentication.
- registry presence is not approval.
- authentication is not approval.
- signature verification remains not approval.
- final acceptance remains not approval.
- approval remains Phase 7D selected-gate manual boundary.
- RBAC design must not trigger wrapper.
- RBAC design must not execute primitives.
- RBAC design must not trigger next gate.
- RBAC design must not set approval flags.

### Non-authentication boundary

- Phase 9E does not authenticate subjects.
- Phase 9E does not verify identity.
- Subject model is not login.
- Subject model is not session.
- Future authentication requires separate phase.

### Non-approval boundary

- RBAC governs future eligibility only.
- Eligibility does not approve business action.
- Approval remains a separate selected-gate manual act.
- Future RBAC cannot bypass Phase 7D.

### Future local policy prototype boundary

- Future Phase 9F may add local RBAC policy prototype.
- Phase 9F must remain local-only unless explicitly changed later.
- Phase 9F must not implement authentication.
- Phase 9F must not call wrapper/primitives.
- Phase 9F must produce advisory decisions only.
- Phase 9F must preserve Phase 7D approval boundary.

### Compatibility with Phase 9D

- Phase 9E uses Phase 9D attribution report as future subject/evidence context.
- Phase 9E does not modify Phase 9D runtime.
- Actor attribution remains not authentication or approval.

### Compatibility with Phase 9C

- Phase 9E uses Phase 9C registry as future subject source.
- Phase 9E does not modify Phase 9C runtime.
- Registry presence remains not authentication or approval.

### Compatibility with Phase 9B

- Phase 9E maps roles and subjects to Phase 9B actor metadata schema.
- Schema validity remains not approval.

### Compatibility with Phase 9A

- Phase 9E preserves Phase 9A identity boundary.
- Operator identity remains unauthenticated or operator-declared.

### Compatibility with Phase 8O/8L/8M

- Phase 9E defines conceptual permissions around final acceptance, signing, and
  verification.
- Phase 9E does not modify Phase 8 runtime.
- Signature verification remains not approval.
- Final acceptance remains not approval.

### Compatibility with Phase 7D

- Phase 7D remains selected-gate manual approval runtime.
- RBAC design does not modify Phase 7D.
- RBAC design must not execute primitives.
- RBAC design must not approve anything.

### Failure taxonomy

Each failure type maps to a severity, an incident classification, and a reviewer
action.

- `subject_missing` — warning; rbac_policy_review_required; manual_review_required.
- `subject_unknown` — warning; rbac_policy_review_required; manual_review_required.
- `subject_identity_assurance_insufficient` — warning;
  identity_assurance_review_required; manual_review_required.
- `role_missing` — warning; rbac_policy_review_required; manual_review_required.
- `role_unknown` — warning; rbac_policy_review_required; manual_review_required.
- `permission_missing` — warning; rbac_policy_review_required;
  manual_review_required.
- `permission_unknown` — warning; rbac_policy_review_required;
  manual_review_required.
- `resource_unknown` — warning; rbac_policy_review_required;
  manual_review_required.
- `action_unknown` — warning; rbac_policy_review_required;
  manual_review_required.
- `policy_version_missing` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `policy_version_incompatible` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `obligation_unmet` — warning; approval_boundary_review_required;
  manual_review_required.
- `approval_boundary_required` — critical; approval_boundary_review_required;
  reject_action_until_resolved.
- `actor_attribution_required` — warning; actor_scope_review_required;
  manual_review_required.
- `privacy_review_required` — critical; privacy_review_required;
  reject_action_until_resolved.
- `primitive_execution_blocked` — critical; primitive_execution_blocked;
  reject_action_until_resolved.
- `next_gate_blocked` — critical; next_gate_blocked; reject_action_until_resolved.
- `approval_flag_present` — critical; approval_boundary_review_required;
  reject_action_until_resolved.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `rbac_policy_review_required`,
`identity_assurance_review_required`, `actor_scope_review_required`,
`approval_boundary_review_required`, `privacy_review_required`,
`primitive_execution_blocked`, `next_gate_blocked`.

Allowed reviewer actions: `no_action_required`, `manual_review_required`,
`reject_rbac_policy_until_resolved`, `reject_action_until_resolved`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the RBAC design context.
- `reject_rbac_policy_until_resolved` — the RBAC policy design must be rejected
  until resolved.
- `reject_action_until_resolved` — the requested action must be rejected until
  resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Non-goals

Phase 9E does not:

- implement RBAC runtime.
- implement policy engine.
- implement permission enforcement.
- implement local policy prototype.
- implement authentication.
- implement login.
- implement sessions.
- implement user store.
- implement OIDC/OAuth/SAML.
- implement external identity provider.
- implement backend/API/database.
- implement key custody.
- implement production signing.
- implement production verifier.
- modify Phase 9C runtime.
- modify Phase 9D runtime.
- modify Phase 7D wrapper.
- modify Phase 8 runtime.
- execute primitives.
- write vault.
- approve anything.
- trigger next gate.
- add chain execution.
- create production deployment.

### Known limitations

- design only
- no RBAC runtime
- no policy engine
- no permission enforcement
- no local policy prototype
- no authentication
- no login
- no session runtime
- no user store
- no enterprise identity
- no governed key custody
- no strong non-repudiation
- no backend/API/database
- no production deployment

### Phase 9F local RBAC policy prototype

Phase 9F local RBAC policy prototype now exists at
`docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`. Phase 9F implements a local
advisory subset of this design. Phase 9F does not implement enforcement; RBAC
allow decisions and RBAC eligibility remain not approval.
