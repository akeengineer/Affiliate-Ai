# Phase 9F — Local RBAC Policy Prototype

phase9f_status: success

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

identity_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

phase9_branch_workflow: enabled

### Purpose

Phase 9F implements a local-only advisory RBAC policy prototype based on
Phase 9E. It reads a local RBAC policy JSON and a local subject/resource/action
request JSON, optionally consults an existing Phase 9C operator registry and/or
Phase 9D actor attribution report as advisory context, evaluates advisory RBAC
eligibility deterministically, and writes an advisory decision report.

Phase 9F does not implement RBAC enforcement, authentication, login, sessions,
backend/API/database, key custody, production signing, or production
verification.

### Scope

- local-only advisory RBAC policy prototype
- local policy input
- local request input
- optional Phase 9C registry context
- optional Phase 9D attribution context
- advisory decision report JSON/MD
- explicit deny/allow/conditional_allow/no-match behavior
- identity assurance comparison
- privacy/secret scan
- approval boundary enforcement
- deterministic local outputs
- no RBAC enforcement
- no authentication runtime
- no login
- no session runtime
- no user store
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no Phase 8 runtime behavior change
- no Phase 9C/9D runtime behavior change

### Runtime command

```text
bash scripts/dev/run_phase9f_local_rbac_policy.sh --policy <policy-json> --request <request-json> [--registry <registry-json>] [--attribution <attribution-json>]
```

The command accepts no approval flags and no `--execute`.

### Policy input model

Required policy fields:

- `policy_version`
- `policy_status`
- `policy_mode`
- `permissions`
- `approval_boundary_statement`

Required permission fields:

- `permission_id`
- `effect`
- `roles`
- `resources`
- `actions`
- `required_identity_assurance`
- `obligations`
- `approval_boundary_statement`

State:

- `policy_version` must be `phase9f.local_rbac_policy.v1`.
- `policy_mode` must be `advisory_only`.
- `policy_status` must be `local_advisory_prototype`.
- policy file is local input only.
- policy file is not production policy.
- policy is not approval.

### Request input model

Required request fields:

- `request_id`
- `subject`
- `resource`
- `action`
- `approval_boundary_statement`

Required subject fields:

- `subject_id`
- `subject_actor_id`
- `subject_actor_type`
- `subject_identity_assurance`
- `subject_identity_source`
- `subject_role_labels`

Required resource fields:

- `resource_type`
- `resource_id`

Request is local evaluation input only.

### Decision model

Decisions and reasons:

- `allow` / `policy_allow`
- `deny` / `explicit_deny`
- `deny` / `no_matching_permission`
- `conditional_allow` / `insufficient_identity_assurance`
- `deny` / `primitive_execution_blocked`

Rules:

- explicit deny takes precedence.
- allow is advisory only.
- allow is not approval.
- conditional_allow requires manual review.
- `execute_primitive` is always blocked.
- `approve_selected_gate` may only produce advisory eligibility and the
  obligation `require_phase7d_selected_gate`.
- no decision executes action.

### Obligation model

Obligations:

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

Obligations are advisory only.

### Optional registry context

- registry is optional.
- registry is used only for advisory subject lookup.
- registry presence is not authentication.
- registry presence is not approval.
- registry is not mutated.

### Optional attribution context

- attribution report is optional.
- attribution is advisory evidence context only.
- actor attribution is not authentication.
- actor attribution is not approval.
- attribution report is not mutated.

### Output layout

- `tmp/phase9f-local-rbac-policy/local-rbac-decision-report.json`
- `tmp/phase9f-local-rbac-policy/local-rbac-decision-report.md`

### Path safety

- policy, request, optional registry, and optional attribution paths must
  resolve under the repository root.
- these paths must not be under `vault/`, `docs/`, `scripts/`, `codex/`, or
  `.git/`.
- these paths must not be symlinks.
- paths must not use traversal or an absolute path outside the repo.
- `output-dir` must resolve to `tmp/phase9f-local-rbac-policy` or below it.
- the output directory is created if missing.

### Privacy and secret handling

- never write raw AFFILIATE_PHASE8L_PROTOTYPE_KEY
- never store private keys
- never store API keys
- never store OAuth/OIDC/SAML tokens
- never store database passwords
- avoid raw emails in `actor_id` or `subject_actor_id`
- avoid unnecessary PII
- sanitize labels if needed

### Approval boundary

- local RBAC policy prototype is not enforcement
- RBAC policy is not approval
- RBAC eligibility is not approval
- RBAC advisory decision is not approval
- RBAC allow decision is not approval
- RBAC deny decision is not incident by itself
- RBAC advisory report is evidence only
- role label is not runtime permission
- actor metadata is not approval
- actor attribution is not approval
- registry presence is not authentication
- registry presence is not approval
- authentication is not approval
- signature verification remains not approval
- final acceptance remains not approval
- allow must not trigger wrapper
- allow must not execute primitives
- allow must not trigger next gate
- allow must not set approval flags
- approval remains Phase 7D selected-gate manual boundary

### Non-enforcement boundary

- Phase 9F does not enforce permissions.
- Phase 9F does not block or allow runtime actions.
- Phase 9F produces advisory reports only.
- No output may be used as direct execution authorization.

### Non-authentication boundary

- Phase 9F does not authenticate subjects.
- Phase 9F does not verify identity.
- Registry context is not login.
- Attribution context is not session.
- Future authentication requires separate phase.

### Non-approval boundary

- RBAC governs future eligibility only.
- Eligibility does not approve business action.
- Allow does not approve.
- Approval remains a separate selected-gate manual act.
- Future RBAC cannot bypass Phase 7D.

### Compatibility with Phase 9E

- Phase 9F implements a local advisory subset of the Phase 9E design.
- Phase 9F preserves the Phase 9E non-enforcement boundary.

### Compatibility with Phase 9D

- Phase 9F may consume the Phase 9D attribution report as optional context.
- Phase 9F does not modify Phase 9D runtime.
- Actor attribution remains not authentication or approval.

### Compatibility with Phase 9C

- Phase 9F may consume the Phase 9C registry as optional context.
- Phase 9F does not modify Phase 9C runtime.
- Registry presence remains not authentication or approval.

### Compatibility with Phase 9B

- Phase 9F maps subjects to Phase 9B actor metadata fields.
- Schema validity remains not approval.

### Compatibility with Phase 9A

- Phase 9F preserves the Phase 9A identity boundary.
- Operator identity remains unauthenticated or operator-declared.

### Compatibility with Phase 8O/8L/8M

- Phase 9F can evaluate advisory eligibility for final acceptance, signing, and
  verification review actions.
- Phase 9F does not modify Phase 8 runtime.
- Signature verification remains not approval.
- Final acceptance remains not approval.

### Compatibility with Phase 7D

- Phase 7D remains the selected-gate manual approval runtime.
- Phase 9F does not modify Phase 7D.
- RBAC advisory decision must not approve.
- RBAC advisory decision must not execute primitives.
- `approve_selected_gate` advisory allow still requires the Phase 7D
  selected-gate manual boundary.

### Failure taxonomy

Each failure type maps to a severity, an incident classification, and a
reviewer action.

- `policy_missing` — critical; rbac_decision_not_available;
  reject_rbac_policy_until_resolved.
- `request_missing` — critical; rbac_decision_not_available;
  reject_action_until_resolved.
- `invalid_policy_json` — critical; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `invalid_request_json` — critical; rbac_decision_not_available;
  reject_action_until_resolved.
- `invalid_policy_shape` — critical; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `invalid_request_shape` — critical; rbac_decision_not_available;
  reject_action_until_resolved.
- `policy_version_missing` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `policy_version_incompatible` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `policy_mode_invalid` — critical; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `enforcement_enabled_present` — critical; approval_boundary_review_required;
  reject_rbac_policy_until_resolved.
- `permission_missing` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `permission_unknown` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `subject_missing` — critical; rbac_decision_not_available;
  reject_action_until_resolved.
- `subject_unknown` — warning; actor_scope_review_required;
  manual_review_required.
- `subject_identity_assurance_insufficient` — warning;
  identity_assurance_review_required; manual_review_required.
- `role_missing` — warning; rbac_policy_review_required;
  reject_rbac_policy_until_resolved.
- `role_unknown` — warning; actor_scope_review_required; manual_review_required.
- `resource_unknown` — warning; actor_scope_review_required;
  reject_action_until_resolved.
- `action_unknown` — warning; actor_scope_review_required;
  reject_action_until_resolved.
- `obligation_unmet` — warning; approval_boundary_review_required;
  manual_review_required.
- `approval_boundary_required` — critical; approval_boundary_review_required;
  reject_action_until_resolved.
- `privacy_review_required` — critical; privacy_review_required;
  reject_action_until_resolved.
- `primitive_execution_blocked` — critical; primitive_execution_blocked;
  reject_action_until_resolved.
- `next_gate_blocked` — critical; next_gate_blocked; reject_action_until_resolved.
- `approval_flag_present` — critical; approval_boundary_review_required;
  reject_action_until_resolved.
- `unsafe_path` — critical; rbac_decision_not_available;
  reject_action_until_resolved.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `rbac_policy_review_required`,
`identity_assurance_review_required`, `actor_scope_review_required`,
`approval_boundary_review_required`, `privacy_review_required`,
`primitive_execution_blocked`, `next_gate_blocked`, `rbac_decision_not_available`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the RBAC decision context.
- `reject_rbac_policy_until_resolved` — the RBAC policy must be rejected until
  resolved.
- `reject_action_until_resolved` — the requested action must be rejected until
  resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Known limitations

- local advisory prototype only
- no RBAC enforcement
- no production policy engine
- no authentication
- no login
- no session runtime
- no user store
- no enterprise identity
- no governed key custody
- no strong non-repudiation
- no backend/API/database
- no production deployment

### Phase 9G Phase 9 acceptance pack

Phase 9G Phase 9 acceptance pack now exists at
`docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md`. Phase 9G validates this local RBAC
policy prototype as local advisory only. Phase 9F remains not enforcement.

### Phase 10A governed runtime integration readiness

Phase 10A governed runtime integration readiness design now exists at
`docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`. Phase 10A may
reference advisory RBAC outputs conceptually but does not modify Phase 9F
runtime.
