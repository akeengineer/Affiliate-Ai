# Task 072 — Phase 9F Local RBAC Policy Prototype

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

## 1. Purpose

Phase 9F adds a local-only advisory RBAC policy prototype based on the
Phase 9E RBAC design. It evaluates a subject/resource/action request against a
local policy input and produces an advisory decision report — never
enforcement, never approval.

## 2. Scope

- local-only advisory RBAC policy prototype (standard library only)
- local policy JSON and local request JSON evaluation
- optional Phase 9C registry and Phase 9D attribution advisory context
- deterministic advisory decision report JSON and Markdown
- explicit deny precedence, allow, conditional_allow, no-match, and
  execute_primitive hard-block decision logic
- privacy/secret scan and approval boundary enforcement
- outputs only under `tmp/phase9f-local-rbac-policy/`
- no enforcement, no authentication, RBAC runtime permission gating, login,
  sessions, user store
- no backend/API/database, no network, no database drivers
- no key management runtime, no key/cert files
- no Phase 9C/9D/8/7D runtime change
- no primitive execution, no vault read/write

## 3. Files

- `scripts/dev/evaluate_phase9f_local_rbac_policy.py`
- `scripts/dev/run_phase9f_local_rbac_policy.sh`
- `tests/test_phase9f_local_rbac_policy_prototype.py`
- `codex/tasks/072-phase9f-local-rbac-policy-prototype.md`
- `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9E_RBAC_DESIGN.md`
- additive updates to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive updates to `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- `.gitignore` (add Phase 9F tmp roots)

## 4. Status model

- `phase9f_status: success` — the prototype, runner, task, doc, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — unchanged.
- `identity_boundary_status: design_only` — unchanged.
- `actor_metadata_schema_status: design_only` — unchanged.
- `actor_metadata_runtime_status: local_registry_prototype` — unchanged.
- `local_operator_registry_status: prototype_local_only` — unchanged.
- `actor_attribution_status: local_report_prototype` — unchanged.
- `rbac_design_status: design_only` — Phase 9E design remains design-only.
- `rbac_policy_status: local_advisory_prototype` — a local advisory policy
  prototype now exists.
- `rbac_runtime_status: local_advisory_prototype` — advisory runtime exists;
  enforcement does not.
- `rbac_enforcement_status: not_implemented` — no enforcement exists.
- `identity_runtime_status: not_implemented` — no identity runtime exists.
- `authentication_runtime_status: not_implemented` — no authentication runtime.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `phase9_branch_workflow: enabled` — Phase 9F continues the Phase 9 branch.

## 5. Local RBAC policy prototype objective

Provide a local, deterministic, advisory-only decision engine that evaluates a
subject/resource/action request against a local policy, guaranteeing every
decision remains advisory and never becomes enforcement or approval.

## 6. Current trust boundary after Phase 9E

Phase 9A defines the identity boundary; Phase 9B defines the schema; Phase 9C
adds a local registry prototype; Phase 9D adds a local attribution report
prototype; Phase 9E designs the RBAC boundary; Phase 9F adds a local advisory
policy evaluation prototype only. No RBAC enforcement, authentication, session,
or user store runtime exists. Operator identity remains unauthenticated or
operator-declared.

## 7. Local policy input model

Required fields `policy_version`, `policy_status`, `policy_mode`, `permissions`,
`approval_boundary_statement`; `policy_version` must be
`phase9f.local_rbac_policy.v1`, `policy_status` must be
`local_advisory_prototype`, `policy_mode` must be `advisory_only`.

## 8. Subject input model

Request `subject` requires `subject_id`, `subject_actor_id`,
`subject_actor_type`, `subject_identity_assurance`, `subject_identity_source`,
`subject_role_labels`.

## 9. Request input model

Required fields `request_id`, `subject`, `resource`, `action`,
`approval_boundary_statement`; `resource` requires `resource_type`,
`resource_id`; `action` must be an allowed action string.

## 10. Registry compatibility model

Optional `--registry` accepts a Phase 9C-style registry object with actor
records under `actor_metadata`, `actor_registry`, `records`,
`registry_records`, or `operators`; used only for advisory subject lookup;
never mutated.

## 11. Attribution compatibility model

Optional `--attribution` accepts a Phase 9D-style attribution report object;
used only as advisory evidence context; never mutated.

## 12. Policy rule model

Each permission has `permission_id`, `effect` (`allow`/`deny`), `roles`,
`resources`, `actions`, `required_identity_assurance`, `obligations`,
`approval_boundary_statement`.

## 13. Resource/action model

Allowed resource types and action values mirror the Phase 9E resource/action
model (19 resource types, 16 action values).

## 14. Decision model

`allow`/`policy_allow`, `deny`/`explicit_deny`, `deny`/`no_matching_permission`,
`conditional_allow`/`insufficient_identity_assurance`,
`deny`/`primitive_execution_blocked`. Explicit deny takes precedence; allow is
advisory only; `execute_primitive` is always blocked; `approve_selected_gate`
allow adds the `require_phase7d_selected_gate` obligation.

## 15. Obligation model

`require_actor_attribution`, `require_manual_review`,
`require_phase7d_selected_gate`, `require_signature_verification_review`,
`require_final_acceptance_review`, `require_privacy_review`,
`require_key_governance_review`, `require_incident_review`,
`require_audit_record`, `require_no_primitive_execution`. Advisory only.

## 16. Denial reason model

`explicit_deny`, `no_matching_permission`, `insufficient_identity_assurance`,
`primitive_execution_blocked`, plus input-validation denial reasons matching the
failure taxonomy.

## 17. Advisory report model

Deterministic JSON (`sort_keys=True`, `indent=2`) and Markdown reports carrying
status fields, `advisory_decision`, `decision_reason`, `matched_permission_ids`,
`denied_permission_ids`, `obligations`, `denial_reasons`, `reviewer_action`,
`incident_classification`, `severity_counts`, `approval_boundary_statement`,
`safety_statement`, `limitations`, `issues`, and the echoed
`request`/`subject`/`resource`/`action`.

## 18. Privacy and secret scan model

Policy, request, registry, and attribution string fields are scanned for
secret-like markers (private-key headers, `API_KEY=`, `SECRET=`, `TOKEN=`,
`PASSWORD=`, `AWS_SECRET_ACCESS_KEY`, `ssh-rsa`, OAuth
`access_token`/`id_token`/`refresh_token`, raw
`AFFILIATE_PHASE8L_PROTOTYPE_KEY`) and external URL schemes; raw emails in actor
IDs are flagged. Matches are critical/reject.

## 19. Approval boundary enforcement model

Policy and request `approval_boundary_statement` must include an approval
boundary phrase; approval flag fields and primitive-execution-intent fields must
not be truthy; `enforcement_enabled: true` is rejected; `policy_mode` other than
`advisory_only` is rejected.

## 20. Deterministic output model

JSON is written with `sort_keys=True` and `indent=2`; permissions are evaluated
in `permission_id` sort order; no wall-clock timestamp is generated.

## 21. Path safety model

Policy, request, optional registry, and optional attribution paths must resolve
under the repo root, must not be under
`vault/`/`docs/`/`scripts/`/`codex/`/`.git/`, and must not be symlinks; the
output directory must resolve to `tmp/phase9f-local-rbac-policy` or below.

## 22. Runtime safety model

Standard library only; no network, database, subprocess, shell execution, key
generation, vault access, wrapper call, primitive call, or Phase 8/9C/9D
runtime call; no mutation outside the tmp output directory.

## 23. Non-enforcement boundary

Phase 9F does not enforce permissions, does not block or allow runtime actions,
and produces advisory reports only; no output may be used as direct execution
authorization.

## 24. Non-authentication boundary

Phase 9F does not authenticate subjects or verify identity; registry context is
not login; attribution context is not session; future authentication requires a
separate phase.

## 25. Non-approval boundary

RBAC governs future eligibility only; eligibility does not approve business
action; allow does not approve; approval remains a separate selected-gate manual
act; future RBAC cannot bypass Phase 7D.

## 26. Compatibility with Phase 9E

Phase 9F implements a local advisory subset of the Phase 9E design and
preserves the Phase 9E non-enforcement boundary.

## 27. Compatibility with Phase 9D

Phase 9F may consume the Phase 9D attribution report as optional context and
does not modify Phase 9D runtime; actor attribution remains not authentication
or approval.

## 28. Compatibility with Phase 9C

Phase 9F may consume the Phase 9C registry as optional context and does not
modify Phase 9C runtime; registry presence remains not authentication or
approval.

## 29. Compatibility with Phase 9B

Phase 9F maps subjects to Phase 9B actor metadata fields; schema validity
remains not approval.

## 30. Compatibility with Phase 9A

Phase 9F preserves the Phase 9A identity boundary; operator identity remains
unauthenticated or operator-declared.

## 31. Compatibility with Phase 8O/8L/8M

Phase 9F can evaluate advisory eligibility for final acceptance, signing, and
verification review actions; it does not modify Phase 8 runtime. Signature
verification remains not approval; final acceptance remains not approval.

## 32. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; Phase 9F does not
modify Phase 7D; RBAC advisory decisions must not approve or execute
primitives; `approve_selected_gate` advisory allow still requires the Phase 7D
selected-gate manual boundary.

## 33. Failure taxonomy

`policy_missing`, `request_missing`, `invalid_policy_json`,
`invalid_request_json`, `invalid_policy_shape`, `invalid_request_shape`,
`policy_version_missing`, `policy_version_incompatible`, `policy_mode_invalid`,
`enforcement_enabled_present`, `permission_missing`, `permission_unknown`,
`subject_missing`, `subject_unknown`,
`subject_identity_assurance_insufficient`, `role_missing`, `role_unknown`,
`resource_unknown`, `action_unknown`, `obligation_unmet`,
`approval_boundary_required`, `privacy_review_required`,
`primitive_execution_blocked`, `next_gate_blocked`, `approval_flag_present`,
`unsafe_path`. Each maps to a severity (`info`, `warning`, `critical`), an
incident classification (`none`, `rbac_policy_review_required`,
`identity_assurance_review_required`, `actor_scope_review_required`,
`approval_boundary_review_required`, `privacy_review_required`,
`primitive_execution_blocked`, `next_gate_blocked`,
`rbac_decision_not_available`), and a reviewer action (`no_action_required`,
`manual_review_required`, `reject_rbac_policy_until_resolved`,
`reject_action_until_resolved`).

## 34. Reviewer action mapping

`no_action_required`, `manual_review_required`,
`reject_rbac_policy_until_resolved`, `reject_action_until_resolved`. Reviewer
action is guidance only, is not approval, and must not trigger the wrapper,
execute primitives, or trigger the next gate.

## 35. Non-goals

Phase 9F does not implement RBAC enforcement, a production policy engine,
authentication, login, sessions, user store, OAuth/OIDC/SAML runtime,
backend/API/database, key custody, production signing, or production verifier;
does not modify Phase 9C/9D runtime, Phase 8 runtime, or the Phase 7D wrapper;
executes no primitives; writes no vault; approves nothing; triggers no next
gate; adds no chain execution; and creates no production deployment.

## 36. Test strategy

`tests/test_phase9f_local_rbac_policy_prototype.py` verifies file existence and
status, scope safety, runtime static safety, valid allow behavior, explicit
deny precedence, no-matching-permission behavior, insufficient-assurance
conditional_allow, execute_primitive hard block, approve_selected_gate advisory
allow, optional registry/attribution context, invalid policy/request behavior,
policy/request field and enum validation, privacy/secret validation, approval
boundary validation, report schema, path safety, documentation regressions,
protected runtime file integrity, static safety on new Phase 9F files, and
repo-wide artifact safety.

## 37. Acceptance criteria

- prototype, runner, task, doc, and tests exist
- runner is mode 100755
- valid allow request produces `advisory_decision: allow`, exit 0
- explicit deny takes precedence over a matching allow
- no matching permission produces advisory deny
- insufficient identity assurance produces conditional_allow with manual review
- `execute_primitive` is always denied and blocked
- `approve_selected_gate` allow carries the `require_phase7d_selected_gate`
  obligation and never calls the wrapper
- optional registry/attribution context is advisory only and never mutated
- invalid/missing inputs and privacy/approval failures reject and exit nonzero
- ROADMAP, PROJECT_STATE, PHASE9E, PHASE9D, PHASE9C, PHASE9B, PHASE9A, and
  PHASE8O reference Phase 9F
- protected runtime files remain unchanged
- local RBAC policy prototype remains not enforcement and RBAC eligibility
  remains not approval
- approval remains Phase 7D selected-gate manual boundary

## 38. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9f_local_rbac_policy_prototype.py
python -m pytest -q tests/test_phase9e_rbac_design.py
python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase9b_actor_metadata_schema_design.py
python -m pytest -q tests/test_phase9a_operator_identity_boundary_design.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m py_compile scripts/dev/evaluate_phase9f_local_rbac_policy.py
bash -n scripts/dev/run_phase9f_local_rbac_policy.sh
chmod 755 scripts/dev/run_phase9f_local_rbac_policy.sh
test "$(stat -c '%a' scripts/dev/run_phase9f_local_rbac_policy.sh)" = "755"
git ls-files -s scripts/dev/run_phase9f_local_rbac_policy.sh | grep "^100755 "
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## 39. Known limitations

- local advisory prototype only
- no RBAC enforcement, no production policy engine, no authentication, no
  login, no session runtime, no user store, no enterprise identity, no
  governed key custody, no strong non-repudiation, no backend/API/database, no
  production deployment

## 40. Final status target

phase9f_status: success
