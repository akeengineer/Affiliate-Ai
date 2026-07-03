# Phase 9A — Operator Identity Boundary Design

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

### Purpose

Phase 9A designs the operator identity boundary after Phase 8. It defines how a
future identity, RBAC, and audit-attribution stage should interpret operator,
reviewer, signer, and actor identity so that identity is always separated from
approval.

Phase 9A does not implement authentication, RBAC, login, backend, database, key
custody, production signing, or production verification. It is a design package
only: docs/tests design-only.

### Scope

Phase 9A covers, as design only:

- docs/tests design-only
- operator identity boundary
- actor identity model
- operator/reviewer/signer/actor identity interpretation
- identity assurance levels
- identity evidence model
- identity-to-action attribution
- approval actor attribution boundary
- signature actor attribution boundary
- reviewer action attribution boundary
- key governance role attribution boundary
- future RBAC boundary
- future authentication provider boundary
- future audit event actor fields
- privacy and PII minimization
- non-repudiation limitations

Phase 9A explicitly excludes, and adds:

- no runtime scripts
- no shell runner
- no authentication runtime
- no RBAC runtime
- no login
- no OAuth/OIDC/SAML
- no backend/API/database
- no key management runtime
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no new mutation path

### Current trust boundary after Phase 8

- Phase 7D remains the selected-gate manual approval boundary.
- Phase 8L signing is local prototype only.
- Phase 8M verification is local prototype only.
- Phase 8N runbook is docs-only.
- Phase 8O final acceptance is evidence only.
- No authenticated operator identity exists.
- No RBAC runtime exists.
- No key management runtime exists.
- No governed key custody exists.
- No enterprise non-repudiation exists.
- Operator identity is currently unauthenticated or operator-declared.
- Identity boundary design must not turn identity metadata into approval.

### Actor identity model

Phase 9A defines the following actor types. For each, the model states the
purpose, allowed interpretation, forbidden interpretation, identity assurance
expectation, audit attribution use, and approval boundary.

- `human_operator`
  - purpose: a human running local safe commands and reviewing evidence.
  - allowed interpretation: attribution of who performed a documented action.
  - forbidden interpretation: proof of approval, proof of authorization, or a
    runtime permission.
  - identity assurance expectation: unauthenticated or operator_declared today.
  - audit attribution use: records the acting operator on an evidence record.
  - approval boundary: operator identity is not approval.

- `reviewer`
  - purpose: a human reviewing evidence, runbook incidents, or acceptance packs.
  - allowed interpretation: attribution of who reviewed an artifact.
  - forbidden interpretation: approval, sign-off authority, or automation
    trigger.
  - identity assurance expectation: unauthenticated or operator_declared today.
  - audit attribution use: records the reviewer on a review record.
  - approval boundary: reviewer identity is not approval.

- `signer`
  - purpose: the declared identity associated with a Phase 8L local prototype
    signature.
  - allowed interpretation: attribution metadata for a prototype signature.
  - forbidden interpretation: strong identity, non-repudiation, or approval.
  - identity assurance expectation: unauthenticated or operator_declared today.
  - audit attribution use: records the declared signer on a signature envelope.
  - approval boundary: signer identity is not approval.

- `key_owner`
  - purpose: governance label for the party accountable for a signing key.
  - allowed interpretation: a governance role label only.
  - forbidden interpretation: runtime permission or approval.
  - identity assurance expectation: governance-declared, design-only.
  - audit attribution use: documents key accountability.
  - approval boundary: key ownership is not approval.

- `key_custodian`
  - purpose: governance label for the party operating key custody controls.
  - allowed interpretation: a governance role label only.
  - forbidden interpretation: runtime permission or approval.
  - identity assurance expectation: governance-declared, design-only.
  - audit attribution use: documents custody accountability.
  - approval boundary: key custody role is not approval.

- `security_owner`
  - purpose: governance label for the party accountable for signing policy.
  - allowed interpretation: a governance role label only.
  - forbidden interpretation: runtime permission or approval.
  - identity assurance expectation: governance-declared, design-only.
  - audit attribution use: documents policy accountability.
  - approval boundary: security ownership is not approval.

- `system_owner`
  - purpose: governance label for the party accountable for the overall system.
  - allowed interpretation: a governance role label only.
  - forbidden interpretation: runtime permission or approval.
  - identity assurance expectation: governance-declared, design-only.
  - audit attribution use: documents system accountability.
  - approval boundary: system ownership is not approval.

- `emergency_revocation_authority`
  - purpose: governance label for the party who could authorize revocation in a
    future governed key runtime.
  - allowed interpretation: a governance role label only.
  - forbidden interpretation: runtime permission or approval.
  - identity assurance expectation: governance-declared, design-only.
  - audit attribution use: documents revocation accountability.
  - approval boundary: revocation authority is not product approval.

- `system_process`
  - purpose: a non-human process that produced an artifact (documented only).
  - allowed interpretation: attribution of automated evidence generation.
  - forbidden interpretation: a way to bypass manual approval.
  - identity assurance expectation: system-observed, design-only.
  - audit attribution use: separates machine-produced from human-produced
    evidence.
  - approval boundary: system actor is not approval.

- `test_fixture`
  - purpose: a test-only actor used in fixtures.
  - allowed interpretation: attribution of test-produced artifacts.
  - forbidden interpretation: a real operator, reviewer, or signer.
  - identity assurance expectation: test-only, never production.
  - audit attribution use: clearly marks test evidence.
  - approval boundary: test fixture actor is not approval.

### Operator ID model

Fields:

- `operator_id`
- `operator_display_label`
- `operator_role_label`
- `operator_identity_assurance`
- `operator_identity_source`
- `operator_session_reference`
- `operator_attestation`
- `operator_action_scope`
- `operator_timestamp_utc`
- `approval_boundary_statement`

Rules:

- `operator_id` is attribution only.
- `operator_id` is not approval.
- `operator_id` must not be treated as authenticated unless identity assurance
  supports it.
- `operator_id` must not trigger wrapper or primitives.

### Reviewer ID model

Fields:

- `reviewer_id`
- `reviewer_display_label`
- `reviewer_role_label`
- `reviewer_identity_assurance`
- `reviewer_identity_source`
- `reviewer_review_scope`
- `reviewer_action`
- `reviewer_timestamp_utc`
- `approval_boundary_statement`

Rules:

- `reviewer_id` is attribution only.
- `reviewer_id` is not approval.
- `reviewer_action` is guidance only.
- reviewer identity must not execute primitives.
- reviewer identity must not trigger wrapper.

### Signer ID model

Fields:

- `signer_id`
- `signer_display_label`
- `signer_role`
- `signer_identity_assurance`
- `signer_identity_source`
- `signer_to_key_binding_reference`
- `signer_action_scope`
- `signing_policy_version`
- `approval_boundary_statement`

Rules:

- `signer_id` is attribution only.
- `signer_id` is not approval.
- signer metadata does not prove strong identity in Phase 9A.
- signer identity must not imply non-repudiation without future authenticated
  identity and governed key custody.
- signer identity must not trigger wrapper or primitives.

### Actor ID model

A normalized `actor_id` model unifies the specific identities above:

- `actor_id`
- `actor_type`
- `actor_display_label`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_role_labels`
- `actor_action_scope`
- `actor_session_reference`
- `actor_attestation`
- `actor_timestamp_utc`
- `approval_boundary_statement`

Rules:

- `actor_id` is attribution only.
- `actor_id` must not contain secrets.
- `actor_id` must avoid unnecessary PII.
- `actor_id` must not be approval.
- `actor_id` must not trigger runtime action.

### Service/system actor model

- `system_process` actor: a documented non-human producer of evidence.
- `test_fixture` actor: a test-only actor used only in fixtures.
- automation actor placeholder: reserved for a future phase and not enabled.

Rules:

- system actor is attribution only.
- system actor must be clearly separated from human actor.
- system actor must not be used to bypass manual approval.
- automation actor is not enabled in Phase 9A.

### Identity assurance levels

For each level the model states its meaning, evidence source, allowed use,
forbidden use, non-repudiation strength, and recommended phase.

- `unauthenticated`
  - meaning: no identity evidence collected.
  - evidence source: none.
  - allowed use: coarse attribution placeholder.
  - forbidden use: any approval or authorization decision.
  - non-repudiation strength: none.
  - recommended phase: current baseline.

- `operator_declared`
  - meaning: the operator states a label with no verification.
  - evidence source: operator declaration.
  - allowed use: weak attribution.
  - forbidden use: approval, authorization, or non-repudiation.
  - non-repudiation strength: weak/none.
  - recommended phase: current baseline.

- `local_machine_observed`
  - meaning: a label observed from the local machine environment.
  - evidence source: local environment observation.
  - allowed use: attribution hint only.
  - forbidden use: approval or strong identity.
  - non-repudiation strength: weak.
  - recommended phase: future prototype.

- `local_config_verified`
  - meaning: a label matched against local configuration.
  - evidence source: local configuration.
  - allowed use: attribution hint only.
  - forbidden use: approval or strong identity.
  - non-repudiation strength: weak.
  - recommended phase: future prototype.

- `repository_config_verified`
  - meaning: a label matched against a repository operator registry.
  - evidence source: repository configuration.
  - allowed use: attribution with weak trust.
  - forbidden use: approval or strong identity.
  - non-repudiation strength: weak/moderate.
  - recommended phase: future prototype.

- `external_identity_verified`
  - meaning: identity verified by an external identity provider.
  - evidence source: an external provider claim.
  - allowed use: stronger attribution.
  - forbidden use: approval by itself.
  - non-repudiation strength: moderate.
  - recommended phase: future integration.

- `enterprise_identity_verified`
  - meaning: identity verified against an enterprise directory.
  - evidence source: an enterprise directory claim.
  - allowed use: stronger attribution and audit.
  - forbidden use: approval by itself.
  - non-repudiation strength: strong-with-controls.
  - recommended phase: future integration.

- `hardware_backed`
  - meaning: identity bound to a hardware-backed credential.
  - evidence source: a hardware attestation.
  - allowed use: strongest attribution and audit.
  - forbidden use: approval by itself.
  - non-repudiation strength: strongest-with-controls.
  - recommended phase: future integration.

Current expected level is unauthenticated or operator_declared.

### Identity evidence model

For each evidence type the model states trust strength, privacy risk, mutation
risk, audit use, and phase availability.

- `terminal_user_label` — trust strength: low; privacy risk: low/medium;
  mutation risk: none (read-only concept); audit use: weak attribution hint;
  phase availability: future.
- `git_user_config` — trust strength: low; privacy risk: medium; mutation risk:
  none; audit use: weak attribution hint; phase availability: future.
- `environment_operator_label` — trust strength: low; privacy risk: low;
  mutation risk: none; audit use: weak attribution hint; phase availability:
  future.
- `local_config_operator_label` — trust strength: low/medium; privacy risk:
  low; mutation risk: none; audit use: attribution hint; phase availability:
  future.
- `repository_operator_registry` — trust strength: medium; privacy risk:
  medium; mutation risk: none; audit use: attribution; phase availability:
  future.
- `signed_identity_assertion` — trust strength: medium/high; privacy risk:
  medium; mutation risk: none; audit use: stronger attribution; phase
  availability: future.
- `external_idp_claim` — trust strength: high; privacy risk: medium/high;
  mutation risk: none; audit use: strong attribution; phase availability:
  future.
- `enterprise_directory_claim` — trust strength: high; privacy risk: high;
  mutation risk: none; audit use: strong attribution; phase availability:
  future.
- `hardware_key_attestation` — trust strength: highest; privacy risk: medium;
  mutation risk: none; audit use: strongest attribution; phase availability:
  future.

Phase 9A implements none of them at runtime.

### Identity-to-action attribution model

Identity attribution records who performed or reviewed an action, not whether
the action is approved. For each action the model defines the actor field,
attribution requirement, identity assurance requirement, approval boundary, and
mutation boundary.

- export pack generation — actor field: `actor_id` (`system_process` or
  `human_operator`); attribution requirement: recommended; identity assurance
  requirement: operator_declared acceptable; approval boundary: attribution is
  not approval; mutation boundary: no mutation beyond documented tmp evidence.
- export integrity verification — actor field: `actor_id`; attribution
  requirement: recommended; identity assurance requirement: operator_declared
  acceptable; approval boundary: verification is not approval; mutation
  boundary: none.
- local signing prototype — actor field: `signer_id`; attribution requirement:
  recommended; identity assurance requirement: operator_declared acceptable;
  approval boundary: signer identity is not approval; mutation boundary: none.
- local verifier prototype — actor field: `actor_id`; attribution requirement:
  recommended; identity assurance requirement: operator_declared acceptable;
  approval boundary: verification passed is not approval; mutation boundary:
  none.
- runbook review — actor field: `reviewer_id`; attribution requirement:
  recommended; identity assurance requirement: operator_declared acceptable;
  approval boundary: reviewer identity is not approval; mutation boundary: none.
- final acceptance review — actor field: `reviewer_id`; attribution
  requirement: recommended; identity assurance requirement: operator_declared
  acceptable; approval boundary: final acceptance remains not approval; mutation
  boundary: none.
- selected-gate manual approval — actor field: `approval_actor_id` (future
  only); attribution requirement: future; identity assurance requirement:
  future; approval boundary: approval remains Phase 7D selected-gate manual
  boundary; mutation boundary: unchanged Phase 7D boundary.
- primitive execution — actor field: none in Phase 9A; attribution requirement:
  n/a; identity assurance requirement: n/a; approval boundary: identity must not
  trigger primitive execution; mutation boundary: none.

### Approval actor attribution boundary

A future approval event may include actor fields:

- `approval_actor_id`
- `approval_actor_type`
- `approval_actor_identity_assurance`
- `approval_actor_session_reference`
- `approval_timestamp_utc`
- `approval_scope`
- `approval_boundary_statement`

Rules:

- Phase 9A does not implement approval event changes.
- Approval actor fields are future-only.
- Actor attribution does not approve anything by itself.
- Approval remains Phase 7D selected-gate manual boundary.

### Signature actor attribution boundary

Phase 8L/8M signer and reviewer fields should map to future actor fields:
`signer_id` maps to `actor_id` with `actor_type: signer`, and reviewer fields
map to `actor_id` with `actor_type: reviewer`.

Rules:

- `signer_id` is not approval.
- signer identity is not non-repudiation without future stronger assurance.
- verified signature remains not approval.
- signature actor attribution must not trigger wrapper or next gate.

### Reviewer action attribution boundary

Reviewer action should be attributed with:

- `reviewer_actor_id`
- `reviewer_actor_type`
- `reviewer_identity_assurance`
- `reviewer_action`
- `reviewer_action_scope`
- `reviewer_timestamp_utc`

Rules:

- reviewer action remains guidance only.
- reviewer action must not approve.
- reviewer action must not execute primitives.

### Key governance role attribution boundary

Phase 8K governance roles map to attribution labels only:

- `key_owner`
- `key_custodian`
- `security_owner`
- `system_owner`
- `emergency_revocation_authority`

Rules:

- roles are governance labels only.
- role label is not runtime permission.
- role label is not approval.
- key role must not trigger wrapper or primitive execution.

### Future RBAC boundary

Future RBAC concepts (design only):

- `permission`
- `role`
- `policy`
- `subject`
- `resource`
- `action`
- `decision`
- `obligation`
- `audit event`

Rules:

- Phase 9A does not implement RBAC.
- RBAC decision is not product approval.
- RBAC eligibility must not bypass selected-gate manual approval.
- Future RBAC must be tested separately.

### Future authentication provider boundary

Future provider categories (design only):

- local config identity
- OS identity
- Git identity
- OIDC provider
- SAML provider
- enterprise directory
- hardware-backed identity

Rules:

- Phase 9A implements none of these providers.
- no OAuth/OIDC/SAML runtime.
- no external URLs.
- no network behavior.
- no user store.
- no session store.

### Future session boundary

Future session fields (design only):

- `session_id`
- `session_started_at_utc`
- `session_expires_at_utc`
- `session_identity_assurance`
- `session_subject_id`
- `session_provider`
- `session_audit_reference`

Rules:

- Phase 9A does not implement sessions.
- session is not approval.
- session must not trigger wrapper or primitives.

### Future audit event actor fields

Fields to be added in a future phase (design only):

- `audit_event_id`
- `actor_id`
- `actor_type`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_session_reference`
- `action_type`
- `action_scope`
- `action_timestamp_utc`
- `action_result`
- `approval_boundary_statement`

Rules:

- Phase 9A does not modify audit event runtime.
- future audit actor fields are attribution only.
- audit attribution is not approval.

### Privacy and PII minimization

- do not store unnecessary personal data.
- prefer pseudonymous `operator_id` over full legal name.
- avoid email unless required by future enterprise identity.
- never store secrets as identity metadata.
- avoid raw terminal dumps.
- sanitize logs.
- separate display labels from stable identifiers.
- support a later redaction strategy.

### Non-repudiation limitations

- unauthenticated identity provides no strong non-repudiation.
- operator_declared identity provides weak attribution only.
- local config identity can be spoofed.
- git config identity is not proof of human identity.
- external identity improves attribution but is not approval.
- enterprise non-repudiation requires authenticated identity, governed key
  custody, policy, audit trail, and revocation/rotation controls.
- Phase 9A implements none of the runtime controls.

### Migration path

Migration stages from operator_declared to authenticated identity:

- 9A: design-only identity boundary.
- 9B: actor metadata schema design.
- 9C: local operator registry prototype.
- 9D: actor attribution in audit/report outputs.
- 9E: RBAC design.
- 9F: local RBAC policy prototype.
- later: external identity provider integration.

All later phases must preserve the Phase 7D approval boundary.

### Compatibility with Phase 7D

- Phase 7D remains the selected-gate manual approval runtime.
- Phase 9A does not modify Phase 7D.
- future actor attribution may annotate approval events.
- actor attribution must not create approval.
- actor attribution must not execute primitives.

### Compatibility with Phase 8L/8M/8N/8O

- Phase 8L `signer_id` remains local prototype metadata.
- Phase 8M reviewer/signer metadata remains evidence only.
- Phase 8N reviewer action remains guidance only.
- Phase 8O final acceptance remains evidence only.
- Phase 9A designs future identity interpretation for these fields.
- Phase 9A does not modify Phase 8 runtime.

### Failure taxonomy

Each identity failure type maps to a severity, an incident classification, and a
reviewer action.

- `actor_missing` — severity: warning; incident_classification:
  identity_not_available; reviewer_action: manual_review_required.
- `actor_ambiguous` — severity: warning; incident_classification:
  identity_assurance_review_required; reviewer_action: manual_review_required.
- `identity_assurance_missing` — severity: warning; incident_classification:
  identity_assurance_review_required; reviewer_action: manual_review_required.
- `identity_assurance_insufficient` — severity: warning;
  incident_classification: identity_assurance_review_required; reviewer_action:
  manual_review_required.
- `actor_role_unknown` — severity: warning; incident_classification:
  identity_policy_review_required; reviewer_action: manual_review_required.
- `actor_scope_mismatch` — severity: warning; incident_classification:
  actor_scope_review_required; reviewer_action: manual_review_required.
- `session_missing` — severity: info; incident_classification:
  identity_not_available; reviewer_action: no_action_required.
- `session_expired` — severity: warning; incident_classification:
  identity_assurance_review_required; reviewer_action: manual_review_required.
- `provider_unavailable` — severity: warning; incident_classification:
  identity_not_available; reviewer_action: manual_review_required.
- `identity_claim_unverified` — severity: warning; incident_classification:
  identity_assurance_review_required; reviewer_action: manual_review_required.
- `identity_metadata_contains_secret` — severity: critical;
  incident_classification: privacy_review_required; reviewer_action:
  reject_identity_until_resolved.
- `identity_metadata_contains_unnecessary_pii` — severity: warning;
  incident_classification: privacy_review_required; reviewer_action:
  manual_review_required.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `identity_not_available`,
`identity_assurance_review_required`, `identity_policy_review_required`,
`privacy_review_required`, `actor_scope_review_required`.

Allowed reviewer actions: `no_action_required`, `manual_review_required`,
`reject_identity_until_resolved`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the identity evidence.
- `reject_identity_until_resolved` — the identity metadata must be rejected
  until the issue is resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Approval boundary

- operator identity is not approval.
- authenticated identity is not approval.
- reviewer identity is not approval.
- signer identity is not approval.
- actor attribution is not approval.
- RBAC eligibility is not approval.
- identity assurance is not approval.
- key ownership is not approval.
- signature verification remains not approval.
- final acceptance remains not approval.
- approval remains Phase 7D selected-gate manual boundary.
- identity metadata must not trigger wrapper.
- identity metadata must not execute primitives.
- identity metadata must not trigger next gate.
- identity metadata must not set approval flags.

### Non-goals

Phase 9A does not:

- implement authentication.
- implement RBAC.
- implement login.
- implement sessions.
- implement user store.
- implement OIDC/OAuth/SAML.
- implement external identity provider.
- implement backend/API/database.
- implement key custody.
- implement production signing.
- implement production verifier.
- modify Phase 7D wrapper.
- modify Phase 8 runtime.
- execute primitives.
- write vault.
- approve anything.
- trigger next gate.
- add chain execution.
- create production deployment.

### Known limitations

- design only.
- no runtime identity.
- no authenticated operator.
- no RBAC runtime.
- no session runtime.
- no user store.
- no enterprise identity.
- no governed key custody.
- no strong non-repudiation.
- no backend/API/database.
- no production deployment.

### Phase 9B actor metadata schema

Phase 9B actor metadata schema design now exists at
`docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`. Phase 9B defines the actor
metadata schema contract based on this Phase 9A identity boundary. Phase 9B does
not implement runtime identity or a registry; actor metadata remains attribution
only and is not approval.

### Phase 9C local operator registry

Phase 9C local operator registry prototype now exists at
`docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`. Phase 9C remains
unauthenticated/operator-declared and does not implement an authentication
runtime. Registry presence is not authentication and is not approval; approval
remains the Phase 7D selected-gate manual boundary.

### Phase 9D actor attribution

Phase 9D actor attribution report prototype now exists at
`docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`. Phase 9D remains
unauthenticated/operator-declared and does not implement an authentication
runtime. Actor attribution is not authentication and is not approval.

### Phase 9E RBAC design

Phase 9E RBAC design now exists at `docs/PHASE9E_RBAC_DESIGN.md`. Phase 9E
preserves this identity boundary and does not implement an authentication
runtime. RBAC design is not enforcement and RBAC eligibility is not approval.
