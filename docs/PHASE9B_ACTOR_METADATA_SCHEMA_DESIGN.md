# Phase 9B — Actor Metadata Schema Design

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

### Purpose

Phase 9B defines a design-only actor metadata schema contract after Phase 9A. It
translates the Phase 9A operator identity boundary into a concrete conceptual
actor metadata object that future phases can adopt, while keeping identity
strictly separated from approval.

Phase 9B does not implement schema validation runtime, actor registry,
authentication, RBAC, backend, database, login, key custody, production signing,
or production verification. It is docs/tests design-only.

### Scope

Phase 9B covers, as design only:

- docs/tests design-only
- actor metadata schema contract
- actor metadata JSON object shape
- normalized actor_id schema
- operator/reviewer/signer actor profiles
- actor_type enum
- actor_role_labels model
- identity_assurance enum
- identity_source enum
- action_scope model
- session_reference placeholder
- identity evidence reference model
- approval_boundary_statement requirement
- privacy/PII constraints
- secret handling constraints
- schema versioning
- compatibility with Phase 9A
- compatibility with Phase 7D
- compatibility with Phase 8L/8M/8N/8O
- future validation boundary
- future registry boundary
- future audit/report mapping

Phase 9B explicitly excludes, and adds:

- no runtime scripts
- no shell runner
- no schema validator implementation
- no actor registry
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

### Current trust boundary after Phase 9A

- Phase 9A defines identity boundary only.
- Phase 9B defines schema contract only.
- No identity runtime exists.
- No actor metadata runtime exists.
- No actor registry exists.
- No authentication runtime exists.
- No RBAC runtime exists.
- No key management runtime exists.
- Operator identity remains unauthenticated or operator-declared.
- Actor metadata is attribution only.
- Actor metadata must not become approval.

### Actor metadata schema overview

Phase 9B defines the design-only actor metadata object as a canonical conceptual
JSON shape for future phases. The conceptual object name is `actor_metadata`.

Required conceptual top-level fields:

- `actor_schema_version`
- `actor_id`
- `actor_type`
- `actor_display_label`
- `actor_role_labels`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_session_reference`
- `actor_attestation`
- `actor_action_scope`
- `identity_evidence_references`
- `actor_timestamp_utc`
- `privacy_classification`
- `approval_boundary_statement`

State:

- This is design-only.
- No runtime validator exists.
- No JSON schema file is produced in Phase 9B.
- Schema validity is not approval.

### Actor metadata top-level object

For each field: type, required/optional, allowed values or format, purpose,
forbidden content, approval boundary rule.

- `actor_schema_version` — type: string; required; format: `phase9b.actor_metadata.v1`;
  purpose: identifies the schema version; forbidden content: secrets; approval
  boundary rule: version is not approval.
- `actor_id` — type: string; required; format: `actor_<stable-pseudonymous-id>`;
  purpose: stable pseudonymous attribution; forbidden content: secrets, raw
  email, PII; approval boundary rule: `actor_id` is not approval.
- `actor_type` — type: string enum; required; allowed values: the actor_type
  enum; purpose: classifies the actor; forbidden content: freeform values;
  approval boundary rule: actor type is not approval.
- `actor_display_label` — type: string; optional; format: human-readable label;
  purpose: display only; forbidden content: secrets, unnecessary PII; approval
  boundary rule: display label is not approval.
- `actor_role_labels` — type: list of strings; optional; allowed values: the
  role label set; purpose: governance labels; forbidden content: runtime
  permissions; approval boundary rule: role labels are not approval.
- `actor_identity_assurance` — type: string enum; required; allowed values: the
  identity_assurance enum; purpose: records assurance; forbidden content: proof
  claims beyond evidence; approval boundary rule: identity assurance is not
  approval.
- `actor_identity_source` — type: string enum; required; allowed values: the
  identity_source enum; purpose: records evidence source; forbidden content:
  secrets; approval boundary rule: identity source is not approval.
- `actor_session_reference` — type: object; optional; format: the session
  placeholder shape; purpose: future session linkage; forbidden content:
  secrets; approval boundary rule: session reference is not approval.
- `actor_attestation` — type: object; optional; format: attestation reference;
  purpose: optional operator statement; forbidden content: raw secrets, private
  keys; approval boundary rule: attestation is not approval.
- `actor_action_scope` — type: object; required; format: the action_scope model;
  purpose: attribution of an action; forbidden content: permissions; approval
  boundary rule: action scope is not approval.
- `identity_evidence_references` — type: list of objects; optional; format: the
  evidence reference model; purpose: references to evidence; forbidden content:
  raw secrets, unnecessary PII; approval boundary rule: evidence reference is
  not approval.
- `actor_timestamp_utc` — type: string; required; format: UTC timestamp;
  purpose: records action time; forbidden content: secrets; approval boundary
  rule: timestamp is not approval.
- `privacy_classification` — type: string; required; allowed values: privacy
  levels; purpose: records privacy handling; forbidden content: secrets;
  approval boundary rule: classification is not approval.
- `approval_boundary_statement` — type: string; required; allowed values: an
  approval boundary statement; purpose: restates the boundary; forbidden
  content: approval flags; approval boundary rule: this field is not approval.

### actor_id schema

- preferred format: `actor_<stable-pseudonymous-id>`
- allowed characters: lowercase letters, digits, underscore, hyphen
- length guidance: short and stable, roughly 8 to 64 characters
- no whitespace
- no raw email by default
- no secrets
- no API keys
- no access tokens
- no private key fragments
- no unnecessary PII

Rules:

- `actor_id` is stable attribution only.
- `actor_id` is not approval.
- `actor_id` must not be used as authentication proof.
- `actor_id` must not trigger wrapper or primitives.

### actor_type enum

Allowed values, each with purpose, allowed use, forbidden use, approval boundary:

- `human_operator` — purpose: a human running safe commands; allowed use:
  attribution; forbidden use: approval or authorization; approval boundary:
  operator metadata is not approval.
- `reviewer` — purpose: a human reviewing evidence; allowed use: attribution;
  forbidden use: approval; approval boundary: reviewer metadata is not approval.
- `signer` — purpose: declared identity of a prototype signature; allowed use:
  attribution; forbidden use: non-repudiation or approval; approval boundary:
  signer metadata is not approval.
- `key_owner` — purpose: governance accountability for a key; allowed use:
  governance label; forbidden use: runtime permission or approval; approval
  boundary: key ownership is not approval.
- `key_custodian` — purpose: governance custody role; allowed use: governance
  label; forbidden use: runtime permission or approval; approval boundary: key
  custody is not approval.
- `security_owner` — purpose: policy accountability; allowed use: governance
  label; forbidden use: runtime permission or approval; approval boundary:
  security ownership is not approval.
- `system_owner` — purpose: system accountability; allowed use: governance
  label; forbidden use: runtime permission or approval; approval boundary:
  system ownership is not approval.
- `emergency_revocation_authority` — purpose: future revocation accountability;
  allowed use: governance label; forbidden use: runtime permission or approval;
  approval boundary: revocation authority is not product approval.
- `system_process` — purpose: non-human evidence producer; allowed use:
  attribution; forbidden use: bypassing manual approval; approval boundary:
  system actor is not approval.
- `test_fixture` — purpose: test-only actor; allowed use: test attribution;
  forbidden use: a real operator/reviewer/signer; approval boundary: test
  fixture actor is not approval.
- `automation_placeholder` — purpose: reserved for a future automation actor;
  allowed use: reserved marker only; forbidden use: any runtime automation;
  approval boundary: automation placeholder is not approval.

### actor_display_label model

- human-readable label.
- may be mutable.
- not a stable identifier.
- must avoid unnecessary PII.
- must not contain secrets.
- must not be used as proof of identity.

### actor_role_labels model

- a list of governance role labels.
- design-only.
- allowed labels:
  - `operator`
  - `reviewer`
  - `signer`
  - `key_owner`
  - `key_custodian`
  - `security_owner`
  - `system_owner`
  - `emergency_revocation_authority`
  - `automation`
  - `test`
- role label is not runtime permission.
- role label is not approval.

### actor_identity_assurance enum

For each level: meaning, evidence requirement, allowed use, forbidden use,
non-repudiation strength, recommended phase.

- `unauthenticated` — meaning: no evidence; evidence requirement: none; allowed
  use: coarse placeholder; forbidden use: any approval; non-repudiation
  strength: none; recommended phase: current baseline.
- `operator_declared` — meaning: unverified declaration; evidence requirement:
  operator declaration; allowed use: weak attribution; forbidden use: approval;
  non-repudiation strength: weak/none; recommended phase: current baseline.
- `local_machine_observed` — meaning: observed from local machine; evidence
  requirement: local observation; allowed use: attribution hint; forbidden use:
  approval; non-repudiation strength: weak; recommended phase: future prototype.
- `local_config_verified` — meaning: matched local config; evidence requirement:
  local configuration; allowed use: attribution hint; forbidden use: approval;
  non-repudiation strength: weak; recommended phase: future prototype.
- `repository_config_verified` — meaning: matched repository registry; evidence
  requirement: repository configuration; allowed use: attribution; forbidden
  use: approval; non-repudiation strength: weak/moderate; recommended phase:
  future prototype.
- `external_identity_verified` — meaning: external provider verified; evidence
  requirement: external provider claim; allowed use: stronger attribution;
  forbidden use: approval by itself; non-repudiation strength: moderate;
  recommended phase: future integration.
- `enterprise_identity_verified` — meaning: enterprise directory verified;
  evidence requirement: enterprise directory claim; allowed use: strong
  attribution; forbidden use: approval by itself; non-repudiation strength:
  strong-with-controls; recommended phase: future integration.
- `hardware_backed` — meaning: hardware-backed credential; evidence requirement:
  hardware attestation; allowed use: strongest attribution; forbidden use:
  approval by itself; non-repudiation strength: strongest-with-controls;
  recommended phase: future integration.

Current expected values are unauthenticated or operator_declared.

### actor_identity_source enum

For each source: trust strength, privacy risk, mutation risk, runtime
availability, phase availability.

- `none` — trust strength: none; privacy risk: none; mutation risk: none;
  runtime availability: n/a; phase availability: current baseline.
- `terminal_user_label` — trust strength: low; privacy risk: low/medium;
  mutation risk: none; runtime availability: none; phase availability: future.
- `git_user_config` — trust strength: low; privacy risk: medium; mutation risk:
  none; runtime availability: none; phase availability: future.
- `environment_operator_label` — trust strength: low; privacy risk: low;
  mutation risk: none; runtime availability: none; phase availability: future.
- `local_config_operator_label` — trust strength: low/medium; privacy risk: low;
  mutation risk: none; runtime availability: none; phase availability: future.
- `repository_operator_registry` — trust strength: medium; privacy risk: medium;
  mutation risk: none; runtime availability: none; phase availability: future.
- `signed_identity_assertion` — trust strength: medium/high; privacy risk:
  medium; mutation risk: none; runtime availability: none; phase availability:
  future.
- `external_idp_claim` — trust strength: high; privacy risk: medium/high;
  mutation risk: none; runtime availability: none; phase availability: future.
- `enterprise_directory_claim` — trust strength: high; privacy risk: high;
  mutation risk: none; runtime availability: none; phase availability: future.
- `hardware_key_attestation` — trust strength: highest; privacy risk: medium;
  mutation risk: none; runtime availability: none; phase availability: future.

Phase 9B implements none of these sources at runtime.

### actor_session_reference model

- optional field.
- future placeholder only.
- suggested shape:
  - `session_id`
  - `session_started_at_utc`
  - `session_expires_at_utc`
  - `session_identity_assurance`
  - `session_provider`
- Phase 9B does not implement session runtime.
- session reference is not approval.
- session reference must not trigger wrapper/primitives.

### actor_attestation model

- an operator statement or future attestation reference.
- optional.
- must not include raw secrets.
- must not include private keys.
- may include `attestation_type`.
- may include `attestation_reference`.
- attestation is not approval.
- attestation is not strong non-repudiation without future controls.

### actor_action_scope model

- `action_category`.
- `product_id` optional.
- `week` optional.
- `gate` optional.
- report/export reference optional.
- signature reference optional.
- approval reference optional.
- allowed scope values:
  - `export_pack_generation`
  - `export_integrity_verification`
  - `local_signature_creation`
  - `local_signature_verification`
  - `incident_review`
  - `final_acceptance_review`
  - `selected_gate_manual_approval`
  - `primitive_execution`
  - `key_governance_review`
  - `test_fixture_generation`

Rules:

- action_scope is attribution only.
- action_scope is not permission.
- action_scope is not approval.

### identity_evidence_reference model

- a list of evidence references.
- each reference contains:
  - `evidence_type`
  - `evidence_reference`
  - `evidence_trust_level`
  - `evidence_privacy_classification`
  - `evidence_timestamp_utc`
- evidence references must not contain raw secrets.
- evidence references must not contain unnecessary PII.
- evidence reference is not approval.

### approval_boundary_statement field

Must always include one of:

- actor metadata is not approval
- actor attribution is not approval
- identity assurance is not approval
- approval remains Phase 7D selected-gate manual boundary

The field is required for all future actor metadata records.

### Operator metadata profile

- `actor_type`: `human_operator`.
- expected role label: `operator`.
- current assurance: unauthenticated or operator_declared.
- allowed actions: safe read-only commands, evidence generation, review.
- forbidden actions: triggering approval, executing primitives, bypassing gates.
- approval boundary: operator metadata is not approval.

### Reviewer metadata profile

- `actor_type`: `reviewer`.
- expected role label: `reviewer`.
- current assurance: unauthenticated or operator_declared.
- `reviewer_action` attribution is recorded on review records.
- allowed actions: reviewing evidence, runbook incidents, acceptance packs.
- forbidden actions: approving, executing primitives, triggering the next gate.
- reviewer action remains guidance only.

### Signer metadata profile

- `actor_type`: `signer`.
- expected role label: `signer`.
- compatibility with Phase 8L `signer_id`.
- signer metadata is not approval.
- signer metadata is not non-repudiation.
- verified signature remains not approval.

### Key governance actor profile

Profiles for `key_owner`, `key_custodian`, `security_owner`, `system_owner`,
`emergency_revocation_authority`.

Rules:

- key role label is governance only.
- key role label is not runtime permission.
- key role label is not approval.
- no key runtime exists.

### System/test actor profile

Profiles for `system_process`, `test_fixture`, `automation_placeholder`.

Rules:

- system/test actors are clearly separated from human actors.
- automation_placeholder is not enabled.
- system/test actor must not bypass manual approval.

### Schema versioning model

- `actor_schema_version` initial value: `phase9b.actor_metadata.v1`.
- version compatibility policy: additive fields keep the same major version;
  breaking changes require a new version.
- breaking vs additive fields: adding optional fields is additive; removing or
  retyping required fields is breaking.
- required `approval_boundary_statement` preservation: every version must keep
  the `approval_boundary_statement` field.
- backward compatibility for Phase 8 signer/reviewer labels: existing Phase 8L
  `signer_id` and Phase 8M reviewer/signer labels map forward without loss.

### Schema compatibility model

- Phase 9A actor boundary compatibility: the schema realizes the Phase 9A actor
  types and assurance levels without changing their semantics.
- Phase 7D approval event compatibility: future approval events may carry actor
  metadata, but actor metadata does not create approval.
- Phase 8L signer metadata compatibility: `signer_id` maps to a signer
  `actor_metadata` record.
- Phase 8M verifier report compatibility: reviewer/signer report fields map to
  `actor_metadata`.
- Phase 8N runbook reviewer action compatibility: reviewer action maps to a
  reviewer `actor_metadata` record.
- Phase 8O final acceptance compatibility: final acceptance review maps to a
  reviewer/actor `actor_metadata` record.
- future Phase 9C registry compatibility: a future local operator registry can
  index `actor_id` without becoming authentication.
- future Phase 9D audit/report attribution compatibility: audit/report outputs
  can embed `actor_metadata` as attribution only.

### Privacy and PII constraints

- prefer pseudonymous `actor_id`.
- avoid email unless future enterprise identity requires it.
- separate display label from stable `actor_id`.
- no secrets in actor metadata.
- no access tokens.
- no private key material.
- no API keys.
- avoid raw terminal dumps.
- minimize personal data.
- support future redaction.

### Secret handling constraints

- actor metadata must never contain raw AFFILIATE_PHASE8L_PROTOTYPE_KEY.
- actor metadata must never contain private keys.
- actor metadata must never contain certificates.
- actor metadata must never contain API keys.
- actor metadata must never contain OAuth/OIDC/SAML tokens.
- actor metadata must never contain database passwords.
- actor metadata must never contain affiliate credentials.

### Future validation boundary

- Phase 9B does not implement validation runtime.
- Future validator must be local-first.
- Future validator must not approve.
- Future validator must not trigger wrapper/primitives.
- Future validator must reject secrets and unnecessary PII.
- Future validator must preserve the approval boundary.

### Future registry boundary

- Phase 9B does not implement registry.
- Future local operator registry belongs to Phase 9C or later.
- Registry record is not authentication.
- Registry presence is not approval.
- Registry must not trigger wrapper/primitives.

### Future audit/report mapping

Future mapping to audit/report fields:

- `actor_metadata`
- `actor_id`
- `actor_type`
- `actor_identity_assurance`
- `actor_identity_source`
- `actor_action_scope`
- `actor_session_reference`
- `actor_timestamp_utc`
- `approval_boundary_statement`

State:

- Phase 9B does not modify audit/report runtime.
- Future actor metadata is attribution only.
- Audit attribution is not approval.

### Compatibility with Phase 9A

- Phase 9A defines the identity boundary.
- Phase 9B defines the schema contract based on Phase 9A.
- Phase 9B does not change Phase 9A semantics.

### Compatibility with Phase 7D

- Phase 7D remains the selected-gate manual approval runtime.
- Future actor metadata may annotate approval events.
- Actor metadata does not create approval.
- Actor metadata must not execute primitives.

### Compatibility with Phase 8L/8M/8N/8O

- Phase 8L `signer_id` maps to future signer actor metadata.
- Phase 8M signer/reviewer metadata maps to future actor metadata.
- Phase 8N reviewer action maps to future reviewer actor metadata.
- Phase 8O final acceptance review maps to future reviewer/actor metadata.
- Phase 9B does not modify Phase 8 runtime.

### Failure taxonomy

Each failure type maps to a severity, an incident classification, and a reviewer
action.

- `actor_schema_version_missing` — severity: warning; incident_classification:
  actor_metadata_schema_failure; reviewer_action: manual_review_required.
- `actor_id_missing` — severity: warning; incident_classification:
  actor_metadata_schema_failure; reviewer_action: manual_review_required.
- `actor_id_invalid_format` — severity: warning; incident_classification:
  actor_metadata_schema_failure; reviewer_action: manual_review_required.
- `actor_type_missing` — severity: warning; incident_classification:
  actor_metadata_schema_failure; reviewer_action: manual_review_required.
- `actor_type_unknown` — severity: warning; incident_classification:
  actor_metadata_schema_failure; reviewer_action: manual_review_required.
- `actor_identity_assurance_missing` — severity: warning;
  incident_classification: identity_assurance_review_required; reviewer_action:
  manual_review_required.
- `actor_identity_assurance_insufficient` — severity: warning;
  incident_classification: identity_assurance_review_required; reviewer_action:
  manual_review_required.
- `actor_identity_source_unknown` — severity: warning; incident_classification:
  identity_policy_review_required; reviewer_action: manual_review_required.
- `actor_role_label_unknown` — severity: warning; incident_classification:
  identity_policy_review_required; reviewer_action: manual_review_required.
- `actor_scope_invalid` — severity: warning; incident_classification:
  actor_scope_review_required; reviewer_action: manual_review_required.
- `actor_session_reference_invalid` — severity: warning;
  incident_classification: actor_metadata_schema_failure; reviewer_action:
  manual_review_required.
- `identity_evidence_reference_invalid` — severity: warning;
  incident_classification: actor_metadata_schema_failure; reviewer_action:
  manual_review_required.
- `identity_metadata_contains_secret` — severity: critical;
  incident_classification: privacy_review_required; reviewer_action:
  reject_actor_metadata_until_resolved.
- `identity_metadata_contains_unnecessary_pii` — severity: warning;
  incident_classification: privacy_review_required; reviewer_action:
  manual_review_required.
- `approval_boundary_statement_missing` — severity: warning;
  incident_classification: identity_policy_review_required; reviewer_action:
  manual_review_required.

Allowed severities: `info`, `warning`, `critical`.

Allowed incident classifications: `none`, `actor_metadata_not_available`,
`actor_metadata_schema_failure`, `identity_assurance_review_required`,
`identity_policy_review_required`, `privacy_review_required`,
`actor_scope_review_required`.

Allowed reviewer actions: `no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`.

### Reviewer action mapping

- `no_action_required` — no reviewer follow-up needed.
- `manual_review_required` — a reviewer must inspect the actor metadata.
- `reject_actor_metadata_until_resolved` — the actor metadata must be rejected
  until the issue is resolved.

Rules:

- reviewer action is guidance only.
- reviewer action is not approval.
- reviewer action must not trigger wrapper.
- reviewer action must not execute primitives.
- reviewer action must not trigger next gate.

### Approval boundary

- actor metadata is not approval.
- actor attribution is not approval.
- actor_id is not approval.
- operator metadata is not approval.
- reviewer metadata is not approval.
- signer metadata is not approval.
- identity assurance is not approval.
- identity source is not approval.
- session reference is not approval.
- schema validity is not approval.
- RBAC eligibility is not approval.
- signature verification remains not approval.
- final acceptance remains not approval.
- approval remains Phase 7D selected-gate manual boundary.
- actor metadata must not trigger wrapper.
- actor metadata must not execute primitives.
- actor metadata must not trigger next gate.
- actor metadata must not set approval flags.

### Non-goals

Phase 9B does not:

- implement actor metadata runtime.
- implement schema validator.
- implement local operator registry.
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
- no runtime actor metadata validation.
- no local registry.
- no authenticated operator.
- no RBAC runtime.
- no session runtime.
- no user store.
- no enterprise identity.
- no governed key custody.
- no strong non-repudiation.
- no backend/API/database.
- no production deployment.

### Phase 9C local operator registry

Phase 9C local operator registry prototype now exists at
`docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`. Phase 9C implements a local
validation subset of this schema and a deterministic local registry. Registry
presence is not authentication and is not approval; valid actor metadata is not
approval.

### Phase 9D actor attribution

Phase 9D actor attribution report prototype now exists at
`docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`. Phase 9D uses these actor
metadata fields for local report attribution. Attribution validity is not
approval.

### Phase 9E RBAC design

Phase 9E RBAC design now exists at `docs/PHASE9E_RBAC_DESIGN.md`. Phase 9E maps
RBAC subjects and roles to these actor metadata fields. Role label remains not
runtime permission, and RBAC eligibility is not approval.

### Phase 9F local RBAC policy prototype

Phase 9F local RBAC policy prototype now exists at
`docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`. Phase 9F maps request subjects to
these actor metadata fields. Schema validity remains not approval.
