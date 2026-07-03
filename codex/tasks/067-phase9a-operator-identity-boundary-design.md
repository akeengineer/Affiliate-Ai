# Task 067 — Phase 9A Operator Identity Boundary Design

phase9a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

identity_runtime_status: not_implemented

rbac_runtime_status: not_implemented

authentication_runtime_status: not_implemented

operator_identity_assurance_status: unauthenticated_or_operator_declared

signing_implementation_status: prototype_local_only

signature_runtime_status: local_prototype

signature_verifier_runtime_status: local_prototype

key_management_runtime_status: not_implemented

phase9_branch_workflow: enabled

## 1. Purpose

Phase 9A designs the operator identity boundary after Phase 8 so that a future
identity/RBAC/audit-attribution stage can interpret operator, reviewer, signer,
and actor identity without ever treating identity as approval. Phase 9A is
docs/tests design-only.

## 2. Scope

- docs/tests design-only
- operator identity boundary
- actor identity model
- operator/reviewer/signer/actor identity interpretation
- identity assurance levels
- identity evidence model
- identity-to-action attribution
- approval/signature/reviewer/key-role attribution boundaries
- future RBAC, authentication provider, session, and audit actor fields
- privacy and PII minimization
- non-repudiation limitations
- no runtime scripts, no shell runner, no authentication runtime, no RBAC
  runtime, no login, no OAuth/OIDC/SAML, no backend/API/database, no key
  management runtime, no wrapper behavior change, no primitive execution, no
  vault read/write, no new mutation path

## 3. Files

- `codex/tasks/067-phase9a-operator-identity-boundary-design.md`
- `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- `tests/test_phase9a_operator_identity_boundary_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- additive updates to `docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`

No Phase 9A runtime script or shell runner is added. The identity boundary is
documentation/test driven only.

## 4. Status model

- `phase9a_status: success` — the task, design doc, and tests exist and focused
  verification expectations are documented.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — Phase 8 posture
  is unchanged.
- `identity_boundary_status: design_only` — the identity boundary is designed,
  not implemented.
- `identity_runtime_status: not_implemented` — no identity runtime exists.
- `rbac_runtime_status: not_implemented` — no RBAC runtime exists.
- `authentication_runtime_status: not_implemented` — no authentication runtime
  exists.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  operator identity is currently unauthenticated or operator-declared.
- `signing_implementation_status: prototype_local_only` — signing remains the
  Phase 8L local prototype.
- `signature_runtime_status: local_prototype` — Phase 8L remains the only
  signature runtime.
- `signature_verifier_runtime_status: local_prototype` — Phase 8M remains the
  only verifier runtime.
- `key_management_runtime_status: not_implemented` — key management runtime does
  not exist.
- `phase9_branch_workflow: enabled` — Phase 9A opens the Phase 9 identity/RBAC
  stage on a dedicated branch.

## 5. Operator identity boundary objective

Provide a single design reference defining who acts, who reviews, who signs, and
who owns keys, and how those identities are attributed in future audit/report
outputs, while guaranteeing that identity never becomes approval.

## 6. Current trust boundary after Phase 8

- Phase 7D remains the selected-gate manual approval boundary.
- Phase 8L signing is local prototype only.
- Phase 8M verification is local prototype only.
- Phase 8N runbook is docs-only.
- Phase 8O final acceptance is evidence only.
- No authenticated operator identity, RBAC runtime, key management runtime,
  governed key custody, or enterprise non-repudiation exists.
- Operator identity is currently unauthenticated or operator-declared.

## 7. Actor identity model

Defines `human_operator`, `reviewer`, `signer`, `key_owner`, `key_custodian`,
`security_owner`, `system_owner`, `emergency_revocation_authority`,
`system_process`, and `test_fixture`. For each actor: purpose, allowed
interpretation, forbidden interpretation, identity assurance expectation, audit
attribution use, and approval boundary.

## 8. Operator ID model

Fields: `operator_id`, `operator_display_label`, `operator_role_label`,
`operator_identity_assurance`, `operator_identity_source`,
`operator_session_reference`, `operator_attestation`, `operator_action_scope`,
`operator_timestamp_utc`, `approval_boundary_statement`. `operator_id` is
attribution only and is not approval.

## 9. Reviewer ID model

Fields: `reviewer_id`, `reviewer_display_label`, `reviewer_role_label`,
`reviewer_identity_assurance`, `reviewer_identity_source`,
`reviewer_review_scope`, `reviewer_action`, `reviewer_timestamp_utc`,
`approval_boundary_statement`. `reviewer_id` is attribution only, `reviewer_action`
is guidance only, and neither approves.

## 10. Signer ID model

Fields: `signer_id`, `signer_display_label`, `signer_role`,
`signer_identity_assurance`, `signer_identity_source`,
`signer_to_key_binding_reference`, `signer_action_scope`, `signing_policy_version`,
`approval_boundary_statement`. `signer_id` is attribution only, does not prove
strong identity in Phase 9A, and is not approval.

## 11. Actor ID model

Normalized fields: `actor_id`, `actor_type`, `actor_display_label`,
`actor_identity_assurance`, `actor_identity_source`, `actor_role_labels`,
`actor_action_scope`, `actor_session_reference`, `actor_attestation`,
`actor_timestamp_utc`, `approval_boundary_statement`. `actor_id` is attribution
only, contains no secrets, avoids unnecessary PII, and is not approval.

## 12. Service/system actor model

`system_process`, `test_fixture`, and an automation actor placeholder. System
actor is attribution only, is clearly separated from human actor, must not be
used to bypass manual approval, and the automation actor is not enabled in
Phase 9A.

## 13. Identity assurance levels

`unauthenticated`, `operator_declared`, `local_machine_observed`,
`local_config_verified`, `repository_config_verified`,
`external_identity_verified`, `enterprise_identity_verified`, `hardware_backed`.
Each has meaning, evidence source, allowed use, forbidden use, non-repudiation
strength, and recommended phase. Current expected level is unauthenticated or
operator_declared.

## 14. Identity evidence model

`terminal_user_label`, `git_user_config`, `environment_operator_label`,
`local_config_operator_label`, `repository_operator_registry`,
`signed_identity_assertion`, `external_idp_claim`, `enterprise_directory_claim`,
`hardware_key_attestation`. Each has trust strength, privacy risk, mutation
risk, audit use, and phase availability. Phase 9A implements none of them at
runtime.

## 15. Identity-to-action attribution model

Maps export pack generation, export integrity verification, local signing
prototype, local verifier prototype, runbook review, final acceptance review,
selected-gate manual approval, and primitive execution to an actor field,
attribution requirement, identity assurance requirement, approval boundary, and
mutation boundary. Identity attribution records who performed or reviewed an
action, not whether the action is approved.

## 16. Approval actor attribution boundary

Future approval actor fields (`approval_actor_id`, `approval_actor_type`,
`approval_actor_identity_assurance`, `approval_actor_session_reference`,
`approval_timestamp_utc`, `approval_scope`, `approval_boundary_statement`) are
future-only. Phase 9A does not implement approval event changes; actor
attribution does not approve anything.

## 17. Signature actor attribution boundary

Phase 8L/8M signer/reviewer fields map to future actor fields. `signer_id` is
not approval; signer identity is not non-repudiation without stronger assurance;
verified signature remains not approval; signature actor attribution must not
trigger wrapper or next gate.

## 18. Reviewer action attribution boundary

`reviewer_actor_id`, `reviewer_actor_type`, `reviewer_identity_assurance`,
`reviewer_action`, `reviewer_action_scope`, `reviewer_timestamp_utc`. Reviewer
action remains guidance only, does not approve, and does not execute primitives.

## 19. Key governance role attribution boundary

Phase 8K roles (`key_owner`, `key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`) are governance labels only, not runtime
permission, not approval, and must not trigger wrapper or primitive execution.

## 20. Future RBAC boundary

`permission`, `role`, `policy`, `subject`, `resource`, `action`, `decision`,
`obligation`, `audit event`. Phase 9A does not implement RBAC; RBAC decision is
not product approval; RBAC eligibility must not bypass selected-gate manual
approval; future RBAC must be tested separately.

## 21. Future authentication provider boundary

local config identity, OS identity, Git identity, OIDC provider, SAML provider,
enterprise directory, hardware-backed identity. Phase 9A implements none of
these providers; no OAuth/OIDC/SAML runtime, no external URLs, no network
behavior, no user store, no session store.

## 22. Future session boundary

`session_id`, `session_started_at_utc`, `session_expires_at_utc`,
`session_identity_assurance`, `session_subject_id`, `session_provider`,
`session_audit_reference`. Phase 9A does not implement sessions; session is not
approval; session must not trigger wrapper or primitives.

## 23. Future audit event actor fields

`audit_event_id`, `actor_id`, `actor_type`, `actor_identity_assurance`,
`actor_identity_source`, `actor_session_reference`, `action_type`,
`action_scope`, `action_timestamp_utc`, `action_result`,
`approval_boundary_statement`. Phase 9A does not modify audit event runtime;
future audit actor fields are attribution only; audit attribution is not
approval.

## 24. Privacy and PII minimization

Do not store unnecessary personal data; prefer pseudonymous `operator_id`; avoid
email unless required by future enterprise identity; never store secrets as
identity metadata; avoid raw terminal dumps; sanitize logs; separate display
labels from stable identifiers; support later redaction.

## 25. Non-repudiation limitations

Unauthenticated identity provides no strong non-repudiation; operator_declared
identity provides weak attribution only; local config identity can be spoofed;
git config identity is not proof of human identity; external identity improves
attribution but is not approval; enterprise non-repudiation requires
authenticated identity, governed key custody, policy, audit trail, and
revocation/rotation controls. Phase 9A implements none of the runtime controls.

## 26. Migration path from operator_declared to authenticated identity

9A design-only identity boundary; 9B actor metadata schema design; 9C local
operator registry prototype; 9D actor attribution in audit/report outputs; 9E
RBAC design; 9F local RBAC policy prototype; later external identity provider
integration. All later phases preserve the Phase 7D approval boundary.

## 27. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime. Phase 9A does not
modify Phase 7D. Future actor attribution may annotate approval events but must
not create approval and must not execute primitives.

## 28. Compatibility with Phase 8L/8M/8N/8O

Phase 8L `signer_id` remains local prototype metadata; Phase 8M reviewer/signer
metadata remains evidence only; Phase 8N reviewer action remains guidance only;
Phase 8O final acceptance remains evidence only. Phase 9A designs future
interpretation and does not modify Phase 8 runtime.

## 29. Failure taxonomy

`actor_missing`, `actor_ambiguous`, `identity_assurance_missing`,
`identity_assurance_insufficient`, `actor_role_unknown`, `actor_scope_mismatch`,
`session_missing`, `session_expired`, `provider_unavailable`,
`identity_claim_unverified`, `identity_metadata_contains_secret`,
`identity_metadata_contains_unnecessary_pii`. Each maps to a severity (`info`,
`warning`, `critical`), an incident classification (`none`,
`identity_not_available`, `identity_assurance_review_required`,
`identity_policy_review_required`, `privacy_review_required`,
`actor_scope_review_required`), and a reviewer action (`no_action_required`,
`manual_review_required`, `reject_identity_until_resolved`).

## 30. Reviewer action mapping

`no_action_required`, `manual_review_required`, `reject_identity_until_resolved`.
Reviewer action is guidance only, is not approval, and must not trigger wrapper,
execute primitives, or trigger the next gate.

## 31. Non-goals

Phase 9A does not implement authentication, RBAC, login, sessions, user store,
OIDC/OAuth/SAML, external identity provider, backend/API/database, key custody,
production signing, or production verifier; does not modify the Phase 7D wrapper
or Phase 8 runtime; executes no primitives; writes no vault; approves nothing;
triggers no next gate; adds no chain execution; and creates no production
deployment.

## 32. Test strategy

`tests/test_phase9a_operator_identity_boundary_design.py` verifies file
existence and status tokens, scope safety, required sections, actor model
assertions, identity model assertions, identity assurance and evidence
assertions, attribution boundary assertions, RBAC/auth/session boundary
assertions, privacy and non-repudiation assertions, migration path assertions,
compatibility assertions, failure taxonomy assertions, approval boundary
assertions, documentation regressions, protected runtime file existence, static
safety on new Phase 9A files, and repo-wide artifact safety. No Phase 9A runtime
script or shell runner is added.

## 33. Acceptance criteria

- task exists and contains `phase9a_status: success`
- design doc exists and contains all required status tokens and sections
- test exists
- doc states docs/tests design-only scope and safety statements
- doc defines actor, operator, reviewer, signer, and actor-id models
- doc defines identity assurance levels and identity evidence model
- doc defines identity-to-action attribution and attribution boundaries
- doc defines future RBAC, authentication provider, session, and audit actor
  fields
- doc defines privacy/PII minimization and non-repudiation limitations
- doc defines the failure taxonomy and reviewer action mapping
- doc states the approval boundary statements
- ROADMAP, PROJECT_STATE, PHASE8O, PHASE8N, PHASE8K, and PHASE8J reference
  Phase 9A additively
- protected runtime files remain unchanged
- no Phase 9A runtime script/shell runner/auth/RBAC/backend/key files are added
- operator identity, authenticated identity, reviewer identity, signer identity,
  actor attribution, RBAC eligibility, identity assurance, and key ownership
  remain not approval
- approval remains Phase 7D selected-gate manual boundary

## 34. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9a_operator_identity_boundary_design.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
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

## 35. Known limitations

- design only
- no runtime identity, no authenticated operator, no RBAC runtime, no session
  runtime, no user store, no enterprise identity, no governed key custody, no
  strong non-repudiation, no backend/API/database, no production deployment

## 36. Final status target

phase9a_status: success
