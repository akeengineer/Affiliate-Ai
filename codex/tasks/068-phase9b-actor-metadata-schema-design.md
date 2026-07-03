# Task 068 — Phase 9B Actor Metadata Schema Design

phase9b_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: not_implemented

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

Phase 9B translates the Phase 9A operator identity boundary into a concrete
design-only actor metadata schema contract so future phases can attribute
operator, reviewer, and signer actions without treating identity as approval.
Phase 9B is docs/tests design-only.

## 2. Scope

- docs/tests design-only
- actor metadata schema contract and JSON object shape
- normalized actor_id schema
- operator/reviewer/signer/key/system actor profiles
- actor_type enum, actor_role_labels model
- identity_assurance enum, identity_source enum
- action_scope model, session_reference placeholder
- identity evidence reference model, approval_boundary_statement requirement
- privacy/PII and secret handling constraints
- schema versioning and compatibility with Phase 9A/7D/8L/8M/8N/8O
- future validation, registry, and audit/report boundaries
- no runtime scripts, no shell runner, no schema validator implementation, no
  actor registry, no authentication runtime, no RBAC runtime, no login, no
  OAuth/OIDC/SAML, no backend/API/database, no key management runtime, no
  wrapper behavior change, no primitive execution, no vault read/write, no new
  mutation path

## 3. Files

- `codex/tasks/068-phase9b-actor-metadata-schema-design.md`
- `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- `tests/test_phase9b_actor_metadata_schema_design.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- additive updates to `docs/PHASE8N_SIGNATURE_RUNBOOK_INCIDENT_REVIEW_PACK.md`
- additive updates to `docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`
- additive updates to `docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`

No Phase 9B runtime script or shell runner is added. The actor metadata schema
is documentation/test driven only.

## 4. Status model

- `phase9b_status: success` — the task, design doc, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — Phase 8 posture
  is unchanged.
- `identity_boundary_status: design_only` — Phase 9A identity boundary remains
  design-only.
- `actor_metadata_schema_status: design_only` — the actor metadata schema is
  designed, not implemented.
- `actor_metadata_runtime_status: not_implemented` — no actor metadata runtime
  exists.
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
- `phase9_branch_workflow: enabled` — Phase 9B continues the Phase 9 branch.

## 5. Actor metadata schema objective

Provide a single conceptual actor metadata object and field contract that future
phases can adopt for attribution, guaranteeing that schema validity and actor
metadata never become approval.

## 6. Current trust boundary after Phase 9A

Phase 9A defines the identity boundary only; Phase 9B defines the schema
contract only. No identity, actor metadata, actor registry, authentication,
RBAC, or key management runtime exists. Operator identity remains unauthenticated
or operator-declared, and actor metadata is attribution only.

## 7. Actor metadata schema overview

Defines the conceptual `actor_metadata` object with the required top-level
fields. Design-only: no runtime validator, no JSON schema file, and schema
validity is not approval.

## 8. Actor metadata top-level object

Defines, per field, the type, required/optional status, allowed values or
format, purpose, forbidden content, and approval boundary rule.

## 9. actor_id schema

Preferred format `actor_<stable-pseudonymous-id>`; lowercase letters, digits,
underscore, hyphen; no whitespace, no raw email, no secrets, no API keys, no
access tokens, no private key fragments, no unnecessary PII. `actor_id` is
stable attribution only, is not approval, is not authentication proof, and must
not trigger wrapper or primitives.

## 10. actor_type enum

`human_operator`, `reviewer`, `signer`, `key_owner`, `key_custodian`,
`security_owner`, `system_owner`, `emergency_revocation_authority`,
`system_process`, `test_fixture`, `automation_placeholder`. Each defines
purpose, allowed use, forbidden use, and approval boundary.

## 11. actor_display_label model

Human-readable label, possibly mutable, not a stable identifier, avoids
unnecessary PII, contains no secrets, and is not proof of identity.

## 12. actor_role_labels model

List of governance role labels (`operator`, `reviewer`, `signer`, `key_owner`,
`key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`, `automation`, `test`). Role label is not
runtime permission and is not approval.

## 13. actor_identity_assurance enum

`unauthenticated`, `operator_declared`, `local_machine_observed`,
`local_config_verified`, `repository_config_verified`,
`external_identity_verified`, `enterprise_identity_verified`, `hardware_backed`.
Each defines meaning, evidence requirement, allowed use, forbidden use,
non-repudiation strength, and recommended phase. Current expected values are
unauthenticated or operator_declared.

## 14. actor_identity_source enum

`none`, `terminal_user_label`, `git_user_config`, `environment_operator_label`,
`local_config_operator_label`, `repository_operator_registry`,
`signed_identity_assertion`, `external_idp_claim`, `enterprise_directory_claim`,
`hardware_key_attestation`. Each defines trust strength, privacy risk, mutation
risk, runtime availability, and phase availability. Phase 9B implements none of
these sources at runtime.

## 15. actor_session_reference model

Optional future placeholder with suggested shape (`session_id`,
`session_started_at_utc`, `session_expires_at_utc`, `session_identity_assurance`,
`session_provider`). Phase 9B does not implement session runtime; session
reference is not approval and must not trigger wrapper/primitives.

## 16. actor_attestation model

Optional operator statement or attestation reference (`attestation_type`,
`attestation_reference`); no raw secrets, no private keys. Attestation is not
approval and is not strong non-repudiation without future controls.

## 17. actor_action_scope model

Action category with optional `product_id`, `week`, `gate`, report/export,
signature, and approval references. Allowed scope values: `export_pack_generation`,
`export_integrity_verification`, `local_signature_creation`,
`local_signature_verification`, `incident_review`, `final_acceptance_review`,
`selected_gate_manual_approval`, `primitive_execution`, `key_governance_review`,
`test_fixture_generation`. Action scope is attribution only, not permission, not
approval.

## 18. identity_evidence_reference model

List of references each with `evidence_type`, `evidence_reference`,
`evidence_trust_level`, `evidence_privacy_classification`,
`evidence_timestamp_utc`. Evidence references must not contain raw secrets or
unnecessary PII, and evidence reference is not approval.

## 19. approval_boundary_statement field

Required for all future actor metadata records; must include one of the approval
boundary statements (actor metadata is not approval / actor attribution is not
approval / identity assurance is not approval / approval remains Phase 7D
selected-gate manual boundary).

## 20. operator metadata profile

`actor_type: human_operator`, expected role label `operator`, current assurance
unauthenticated or operator_declared, with allowed/forbidden actions and the
operator-is-not-approval boundary.

## 21. reviewer metadata profile

`actor_type: reviewer`, expected role label `reviewer`, current assurance
unauthenticated or operator_declared, `reviewer_action` attribution, and reviewer
action remains guidance only.

## 22. signer metadata profile

`actor_type: signer`, expected role label `signer`, compatibility with Phase 8L
`signer_id`; signer metadata is not approval, is not non-repudiation, and
verified signature remains not approval.

## 23. key governance actor profile

Profiles for `key_owner`, `key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`. Key role label is governance only, not runtime
permission, not approval, and no key runtime exists.

## 24. system/test actor profile

Profiles for `system_process`, `test_fixture`, `automation_placeholder`.
System/test actors are separated from human actors; automation_placeholder is
not enabled; system/test actor must not bypass manual approval.

## 25. Schema versioning model

`actor_schema_version` initial value `phase9b.actor_metadata.v1`; version
compatibility policy; breaking vs additive fields; required
`approval_boundary_statement` preservation; backward compatibility for Phase 8
signer/reviewer labels.

## 26. Schema compatibility model

Compatibility rules for Phase 9A actor boundary, Phase 7D approval events,
Phase 8L signer metadata, Phase 8M verifier report, Phase 8N runbook reviewer
action, Phase 8O final acceptance, future Phase 9C registry, and future Phase 9D
audit/report attribution.

## 27. Privacy and PII constraints

Prefer pseudonymous `actor_id`; avoid email unless future enterprise identity
requires it; separate display label from stable `actor_id`; no secrets, access
tokens, private key material, or API keys; avoid raw terminal dumps; minimize
personal data; support future redaction.

## 28. Secret handling constraints

Actor metadata must never contain raw AFFILIATE_PHASE8L_PROTOTYPE_KEY, private
keys, certificates, API keys, OAuth/OIDC/SAML tokens, database passwords, or
affiliate credentials.

## 29. Future validation boundary

Phase 9B does not implement validation runtime; a future validator must be
local-first, must not approve, must not trigger wrapper/primitives, must reject
secrets and unnecessary PII, and must preserve the approval boundary.

## 30. Future registry boundary

Phase 9B does not implement registry; a future local operator registry belongs
to Phase 9C or later; registry record is not authentication; registry presence
is not approval; registry must not trigger wrapper/primitives.

## 31. Future audit/report mapping

Future mapping to audit/report actor fields (`actor_metadata`, `actor_id`,
`actor_type`, `actor_identity_assurance`, `actor_identity_source`,
`actor_action_scope`, `actor_session_reference`, `actor_timestamp_utc`,
`approval_boundary_statement`). Phase 9B does not modify audit/report runtime;
future actor metadata is attribution only; audit attribution is not approval.

## 32. Compatibility with Phase 9A

Phase 9A defines the identity boundary; Phase 9B defines the schema contract
based on Phase 9A and does not change Phase 9A semantics.

## 33. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; future actor
metadata may annotate approval events; actor metadata does not create approval
and must not execute primitives.

## 34. Compatibility with Phase 8L/8M/8N/8O

Phase 8L `signer_id`, Phase 8M signer/reviewer metadata, Phase 8N reviewer
action, and Phase 8O final acceptance review all map to future actor metadata.
Phase 9B does not modify Phase 8 runtime.

## 35. Failure taxonomy

`actor_schema_version_missing`, `actor_id_missing`, `actor_id_invalid_format`,
`actor_type_missing`, `actor_type_unknown`, `actor_identity_assurance_missing`,
`actor_identity_assurance_insufficient`, `actor_identity_source_unknown`,
`actor_role_label_unknown`, `actor_scope_invalid`,
`actor_session_reference_invalid`, `identity_evidence_reference_invalid`,
`identity_metadata_contains_secret`, `identity_metadata_contains_unnecessary_pii`,
`approval_boundary_statement_missing`. Each maps to a severity (`info`,
`warning`, `critical`), an incident classification (`none`,
`actor_metadata_not_available`, `actor_metadata_schema_failure`,
`identity_assurance_review_required`, `identity_policy_review_required`,
`privacy_review_required`, `actor_scope_review_required`), and a reviewer action
(`no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`).

## 36. Reviewer action mapping

`no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`. Reviewer action is guidance only, is not
approval, and must not trigger wrapper, execute primitives, or trigger the next
gate.

## 37. Approval boundary

Actor metadata, actor attribution, actor_id, operator metadata, reviewer
metadata, signer metadata, identity assurance, identity source, session
reference, schema validity, and RBAC eligibility are all not approval; signature
verification remains not approval; final acceptance remains not approval;
approval remains Phase 7D selected-gate manual boundary; actor metadata must not
trigger wrapper, execute primitives, trigger the next gate, or set approval
flags.

## 38. Non-goals

Phase 9B does not implement actor metadata runtime, schema validator, local
operator registry, authentication, RBAC, login, sessions, user store,
OIDC/OAuth/SAML, external identity provider, backend/API/database, key custody,
production signing, or production verifier; does not modify the Phase 7D wrapper
or Phase 8 runtime; executes no primitives; writes no vault; approves nothing;
triggers no next gate; adds no chain execution; and creates no production
deployment.

## 39. Test strategy

`tests/test_phase9b_actor_metadata_schema_design.py` verifies file existence and
status tokens, scope safety, required sections, top-level schema assertions,
actor_id assertions, actor_type/role assertions, identity assurance/source
assertions, session/attestation/action-scope assertions, identity evidence
assertions, profile assertions, versioning/compatibility assertions,
privacy/secret assertions, future boundary assertions, failure taxonomy
assertions, approval boundary assertions, documentation regressions, protected
runtime file existence, static safety on new Phase 9B files, and repo-wide
artifact safety. No Phase 9B runtime script or shell runner is added.

## 40. Acceptance criteria

- task exists and contains `phase9b_status: success`
- design doc exists and contains all required status tokens and sections
- test exists
- doc states docs/tests design-only scope and safety statements
- doc defines the actor metadata object, fields, enums, and profiles
- doc defines schema versioning, compatibility, privacy, and secret handling
- doc defines future validation/registry/audit boundaries
- doc defines the failure taxonomy and reviewer action mapping
- doc states the approval boundary statements
- ROADMAP, PROJECT_STATE, PHASE9A, PHASE8O, PHASE8N, PHASE8K, and PHASE8J
  reference Phase 9B additively
- protected runtime files remain unchanged
- no Phase 9B runtime script/shell runner/validator/registry/auth/RBAC/backend/
  key files are added
- actor metadata and schema validity remain not approval
- approval remains Phase 7D selected-gate manual boundary

## 41. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9b_actor_metadata_schema_design.py
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

## 42. Known limitations

- design only
- no runtime actor metadata validation, no local registry, no authenticated
  operator, no RBAC runtime, no session runtime, no user store, no enterprise
  identity, no governed key custody, no strong non-repudiation, no
  backend/API/database, no production deployment

## 43. Final status target

phase9b_status: success
