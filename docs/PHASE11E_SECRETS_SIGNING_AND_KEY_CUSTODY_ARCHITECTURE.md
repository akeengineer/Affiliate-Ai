# Phase 11E — Secrets, Signing, and Key Custody Architecture

phase11e_status: success

phase11d_status: success

phase11c_status: success

phase11b_status: success

phase11a_status: success

phase10f_status: success

phase7d_runtime_readiness: implemented_manual_gate

production_boundary_status: design_only

hardening_readiness_status: design_only

threat_model_status: design_only

security_control_mapping_status: design_only

ci_gate_enforcement_status: design_only

observability_readiness_status: design_only

audit_retention_readiness_status: design_only

secrets_architecture_readiness_status: design_only

signing_architecture_readiness_status: design_only

verifier_architecture_readiness_status: design_only

key_custody_readiness_status: design_only

governed_production_candidate_status: defined_not_approved

production_runtime_status: out_of_scope

observability_runtime_status: not_implemented

audit_storage_runtime_status: not_implemented

secrets_runtime_status: not_implemented

signing_runtime_status: not_implemented

verifier_runtime_status: not_implemented

authentication_runtime_status: not_implemented

rbac_enforcement_status: not_implemented

key_management_runtime_status: not_implemented

backend_api_database_status: not_implemented

phase11_branch_workflow: enabled

## 1. Phase 11E Purpose

Phase 11E defines secrets, signing, and key custody architecture readiness.

Phase 11E does not implement secrets runtime.

Phase 11E does not implement signing runtime.

Phase 11E does not implement verifier runtime.

Phase 11E does not add key material.

Phase 11E does not implement production runtime.

Phase 11E does not approve production promotion.

This document defines the future architecture for secrets handling, signing
boundaries, verifier separation, key custody, key rotation, revocation,
emergency response, operator approval requirements, and evidence requirements
before any local-only prototype can become a governed production candidate.

## 2. Relationship to Phase 11A, Phase 11B, Phase 11C, and Phase 11D

- Phase 11D defines observability and audit retention readiness.
- Phase 11C defines CI gate and protected boundary enforcement design.
- Phase 11B defines threat model and security control mapping.
- Phase 11A defines production boundary and hardening readiness.
- Phase 11E uses those four readiness layers to define how future secrets,
  signing, verifier, and key custody controls must remain bounded, auditable,
  and approval-preserving.
- Local-only prototypes remain local-only until governed promotion is explicitly approved.
- RBAC advisory context remains not enforcement.
- Approval remains the Phase 7D selected-gate manual boundary.
- Phase 10 acceptance remains readiness, not approval.
- Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.

## 3. Secrets Architecture Readiness Scope

Phase 11E is design-only and docs/tests-only. It defines future secret
classification, storage boundary expectations, redaction rules, operator review
obligations, and CI gate expectations for secrets-bearing workflows.

Phase 11E does not implement secrets runtime.

Phase 11E is secrets, signing, and key custody architecture readiness only.

## 4. Signing Architecture Readiness Scope

Phase 11E defines the future signing request boundary, signing approval
boundary, signing execution boundary, signature metadata requirements, and
artifact hash binding expectations needed before any governed production
candidate may rely on signatures.

Phase 11E does not implement signing runtime.

## 5. Verifier Architecture Readiness Scope

Phase 11E defines the future verifier trust boundary, verifier identity
requirements, signature rejection criteria, separation from signer custody, and
evidence expectations for verification outcomes.

Phase 11E does not implement verifier runtime.

## 6. Key Custody Readiness Scope

Phase 11E defines the future architecture for key ownership, custodian role,
private key custody, public verifier distribution, dual-control placeholder,
rotation schedule placeholder, emergency revocation, and key compromise
response.

Phase 11E does not add key material.

## 7. Secret Classification Model

Future secret classes must include:

- production secret
- development secret
- test fixture token
- placeholder value
- signing private key
- verification public key
- rotation token
- revocation marker
- break-glass credential
- audit export credential
- CI secret
- local-only prototype placeholder

Each class must carry a future owner, usage boundary, evidence requirement, and
redaction rule. No real secrets or key material may be committed.

## 8. Key Classification Model

The future key classification model must distinguish:

- production signing private key material
- development signing placeholder reference
- verification public key distribution material
- rotated key reference
- revoked key reference
- break-glass key reference
- audit-visible key metadata

The model must separate secret-bearing material from distributable verification
material and from metadata-only records. No key material in repository is
allowed at any readiness stage.

## 9. Signing Boundary Model

The future signing boundary model must define:

- signing request boundary
- signing approval boundary
- signing execution boundary
- artifact hash binding
- signature metadata requirements
- signer identity requirements
- rejection criteria
- re-signing prohibition unless explicitly approved
- export mutation prohibition
- production signing deferred to later approved phase

Only an approved, evidence-bearing request may cross from a future signing
request boundary into a future signing execution boundary.

## 10. Verifier Separation Model

The future verifier separation model must define:

- verifier trust boundary
- verifier identity requirements
- signer/verifier separation
- public verifier distribution
- rejection criteria when signer and verifier provenance diverge
- separation between custody records and verification decisions

Verifier handling must remain independently reviewable from any future signing
execution path.

## 11. Custody and Separation of Duties

Future custody and separation-of-duties requirements must include:

- signer/verifier separation
- private key custody
- public verifier distribution
- key ownership
- custodian role
- operator approval
- dual-control placeholder
- audit evidence for key events
- no key material in repository
- no vault write before explicit approval

No single future operator role may both create approval evidence and unilaterally
assert custody sufficiency without an independent review path.

## 12. Rotation Readiness Requirements

Future rotation readiness requirements must include:

- rotation schedule placeholder
- pre-rotation approval evidence
- post-rotation verifier distribution evidence
- artifact hash binding continuity
- signer identity continuity rules
- operator review of affected trust metadata

Rotation remains deferred until a later explicitly approved runtime phase.

## 13. Revocation Readiness Requirements

Future revocation readiness requirements must include:

- emergency revocation
- revocation marker lifecycle
- revocation evidence package
- affected artifact and verifier impact review
- explicit operator review requirement
- revocation escalation requirement

Revocation remains a readiness definition only in Phase 11E.

## 14. Emergency Key Response Model

The future emergency key response model must define:

- key compromise response
- immediate containment expectation
- emergency revocation trigger
- emergency evidence capture
- review ownership
- recovery or replacement approval path

Emergency response must fail closed when compromise evidence is missing or
ambiguous.

## 15. Break-Glass Boundary

Future break-glass handling must be a constrained exception path for a
break-glass credential, with:

- explicit incident declaration
- named custodian accountability
- limited-duration access expectation
- mandatory evidence capture
- mandatory follow-up review
- mandatory revocation or rotation review after use

Break-glass may not become a standing production authorization path.

## 16. Secret Redaction and Exposure Prevention

Future redaction and exposure-prevention rules must include:

- no raw secret disclosure in evidence
- no raw key material disclosure in evidence
- stable redaction rationale
- exposure classification for accidental disclosure
- explicit marking when evidence is partially redacted
- operator review before evidence sharing

Secret-bearing values must be represented only as placeholders or metadata-safe
references in repository-controlled artifacts.

## 17. Test Fixture Safety Requirements

Test fixture safety requirements must include:

- test fixture token values must be inert and non-routable
- placeholder value usage for examples and demos
- no test secrets that resemble real credentials
- no certificate files
- no key files
- no secret fixture files
- local-only prototype placeholder usage for demos

Documentation and tests must remain safe to publish in Git.

## 18. Audit Evidence Requirements

Future audit evidence requirements must include:

- audit evidence for key events
- signer identity evidence
- verifier identity evidence
- artifact hash binding evidence
- custody transfer or review evidence
- rotation evidence
- revocation evidence
- break-glass evidence
- CI gate evidence for secret and key checks
- incident evidence package requirement

No future key-sensitive decision may be treated as complete without auditable
evidence references.

## 19. Observability Requirements for Key Events

Future observability requirements for key events must include:

- signing requested
- signing approved or rejected
- verification requested
- verification accepted or rejected
- key rotation initiated
- key rotation completed
- revocation declared
- break-glass invoked
- secret scan result
- custody review completed

These are readiness requirements for key events only. Phase 11E does not add
logging runtime, metrics runtime, or tracing runtime.

## 20. CI Gate Requirements for Secrets and Keys

Future CI gate requirements for secrets and keys must include:

- secret scanning gate
- key material detection gate
- fixture safety gate
- protected-boundary wording gate
- signer/verifier separation review gate
- artifact hash binding evidence gate
- revocation evidence completeness gate
- no-runtime-added gate

No future CI signal may be treated as production approval by itself.

## 21. Threat-to-Key-Control Mapping

| Threat | Required Key/Secret Control | Required Evidence | Approval Requirement | CI Gate Dependency | Deferred Implementation Phase |
| --- | --- | --- | --- | --- | --- |
| unauthorized signing request | signing request boundary + signer identity requirements | request record tied to artifact hash binding | explicit operator approval before execution | secret scanning gate + artifact hash binding evidence gate | Later approved production phase |
| secret leakage | secret redaction and exposure prevention + CI secret handling rules | scan result and redaction review record | reviewer acknowledgment required | secret scanning gate | Later approved production phase |
| key misuse | private key custody + signer/verifier separation | custody review evidence and signer identity evidence | custodian plus operator approval | key material detection gate + signer/verifier separation review gate | Later approved production phase |
| verifier confusion | verifier trust boundary + verifier identity requirements | verifier provenance evidence | explicit reviewer approval | protected-boundary wording gate | Later approved production phase |
| compromise without revocation | emergency revocation + key compromise response | incident evidence package and revocation marker review | explicit incident approval path | revocation evidence completeness gate | Later approved production phase |
| local-only prototype promoted without approval | local-only prototype protection + manual approval boundary preservation | containment evidence and selected-gate review evidence | Approval remains the Phase 7D selected-gate manual boundary. | no-runtime-added gate | Later approved production phase |

## 22. Signing-to-Evidence Mapping

| Signing Event | Required Metadata | Required Evidence | Required Observability Signal | Rejection Condition | Production Promotion Impact |
| --- | --- | --- | --- | --- | --- |
| signing requested | signer identity, artifact hash, request purpose | request evidence package | signing requested | missing signer identity or missing artifact hash binding | blocks promotion readiness |
| signing approved | reviewer identity, approval rationale, requested artifact reference | approval evidence package | signing approved or rejected | approval boundary ambiguity | blocks promotion readiness |
| signing executed | signature metadata, execution timestamp, signer identity reference | execution evidence package | signing execution recorded | missing protected key evidence | blocks promotion readiness |
| verification requested | verifier identity, artifact hash, signature reference | verification request evidence | verification requested | verifier provenance missing | blocks promotion readiness |
| verification rejected | rejection rationale, affected artifact reference, incident link | rejection evidence package | verification accepted or rejected | rejection evidence missing | blocks promotion readiness |
| re-sign request detected | prior signature reference, mutation context, reviewer rationale | prohibition review evidence | signing requested | re-signing prohibition unless explicitly approved violated | blocks promotion readiness |

## 23. Custody-to-Approval Mapping

| Custody Event | Required Custodian | Required Approval | Required Evidence | Separation Requirement | Emergency Handling Requirement |
| --- | --- | --- | --- | --- | --- |
| key assignment | named custodian role | operator approval | custody assignment evidence | custodian may not self-approve | compromise path documented before activation |
| verifier distribution | verifier distribution owner | reviewer approval | distribution evidence package | separate from private key custody | emergency rollback or replacement path documented |
| rotation review | current custodian plus successor reviewer | dual-control placeholder approval | rotation review evidence | independent review from signer usage | emergency pause path documented |
| revocation declaration | incident custodian | explicit incident approval | revocation evidence package | separate from routine signer operations | emergency revocation required |
| break-glass use | break-glass custodian | explicit operator approval | incident evidence package | separate from ordinary custody actions | immediate post-use review and revocation/rotation assessment required |
| compromise response closure | incident reviewer | formal closure approval | recovery evidence package | independent closure review | emergency handling record required |

## 24. Failure Handling and Escalation

Failure handling must require:

- fail-closed missing key evidence
- fail-closed secret scan finding
- fail-closed signing ambiguity
- fail-closed verifier ambiguity
- no silent signing acceptance
- no warning-only bypass for key custody issues
- explicit operator review requirement
- incident evidence package requirement
- revocation escalation requirement
- manual approval does not override missing protected key evidence unless explicitly approved in a later production phase

Retry criteria: repeat review only after the missing evidence source is
understood and the affected boundary is re-evaluated. Escalation criteria:
escalate when signer identity, verifier provenance, custody record,
revocation status, or artifact hash binding cannot be proven within the current
review cycle.

## 25. Manual Approval Boundary Preservation

- Approval remains the Phase 7D selected-gate manual boundary.
- Signing readiness evidence supports review, blocking, and traceability, not approval.
- No secret, signer, verifier, or custody signal may be treated as approval by itself.
- Manual approval does not override missing protected key evidence unless explicitly approved in a later production phase.

## 26. Local-Only Prototype Protection

- Local-only prototypes remain local-only until governed promotion is explicitly approved.
- Phase 11E preserves the local-only status of all existing prototype runtimes.
- Phase 11E does not widen any runtime boundary.
- Production authentication, RBAC enforcement, key custody, backend/API/database, production signing, verifier runtime, and production policy engine remain out of scope unless explicitly approved.

## 27. Production Candidate Readiness Criteria

A local-only prototype reaches production candidate readiness only when:

- secret classification model is documented and reviewed
- key classification model is documented and reviewed
- signing boundary model is documented and reviewed
- verifier separation model is documented and reviewed
- custody and separation of duties are documented and reviewed
- rotation readiness requirements are documented and reviewed
- revocation readiness requirements are documented and reviewed
- emergency key response model is documented and reviewed
- audit evidence requirements are documented and reviewed
- CI gate requirements for secrets and keys are documented and reviewed
- required mapping tables are current
- explicit phase-specific approval is received
- Phase 11E does not approve production promotion.

Meeting these criteria remains readiness, not approval.

## 28. Non-Goals and Forbidden Implementations

Phase 11E does not add:

- production secrets
- test secrets that resemble real credentials
- key files
- certificate files
- signing runtime
- verifier runtime
- vault write
- vault client runtime
- key custody runtime
- key rotation runtime
- revocation runtime
- authentication runtime
- login/session/user store
- RBAC enforcement
- production policy engine
- backend/API/database files
- logging runtime
- metrics runtime
- tracing runtime
- SIEM integration
- network service
- deployment manifest
- GitHub Actions workflow
- CI/CD deployment pipeline
- primitive execution
- export mutation
- re-signing
- production authorization
- production promotion approval

## 29. Acceptance Criteria

- This document exists with all required sections (1-33)
- Task file exists with `phase11e_status: success`
- Tests pass
- Required canonical wording exists
- Secret classification model is documented
- Key classification model is documented
- Signing boundary model is documented
- Verifier separation model is documented
- Custody and separation of duties are documented
- Rotation readiness is documented
- Revocation readiness is documented
- Emergency key response is documented
- Secret redaction and test fixture safety are documented
- Audit evidence requirements are documented
- CI gate requirements for secrets and keys are documented
- Required mapping tables exist
- Failure handling model is documented
- No Phase 11E runner is introduced
- No Phase 11E runtime file is introduced
- No key/cert file is introduced by Phase 11E
- No vault write/client runtime is introduced by Phase 11E
- No backend/API/database file is introduced by Phase 11E
- No deployment manifest is introduced by Phase 11E
- docs/state pointers reference Phase 11E

## 30. Safe Demo Scenarios

Operator can safely demonstrate Phase 11E by:

1. showing this readiness document exists
2. showing the secret classification model
3. showing the key classification model
4. showing the signing boundary and verifier separation models
5. showing the rotation, revocation, and emergency response sections
6. showing the three required mapping tables
7. confirming no secrets runtime was added
8. confirming no signing runtime or verifier runtime was added
9. running the Phase 11E focused docs-contract test

## 31. Operator Checklist

- [ ] Phase 11E readiness document reviewed
- [ ] Secret classification model reviewed
- [ ] Key classification model reviewed
- [ ] Signing boundary model reviewed
- [ ] Verifier separation model reviewed
- [ ] Custody and separation of duties reviewed
- [ ] Rotation readiness requirements reviewed
- [ ] Revocation readiness requirements reviewed
- [ ] Emergency key response model reviewed
- [ ] Mapping tables reviewed
- [ ] Failure handling and escalation reviewed
- [ ] No secrets runtime was introduced
- [ ] No signing runtime was introduced
- [ ] No verifier runtime was introduced
- [ ] Approval boundary preserved
- [ ] Phase 11E tests pass

## 32. Recommended Next Step

Implement Phase 11F — Backup, Recovery, and Key Escrow Readiness.

Phase 11F should define the future backup, recovery, escrow, and restore
governance model for secrets- and key-adjacent evidence without adding runtime.

## 33. Recommended Next Major Subphase

Phase 11F — Backup, Recovery, and Key Escrow Readiness

Phase 11F should be approved separately and should remain docs/tests-only until
a later explicitly approved phase authorizes runtime implementation.
