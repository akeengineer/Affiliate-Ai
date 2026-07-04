# Phase 11C — CI Gate and Protected Boundary Enforcement Design

## 1. Phase 11C Purpose

Phase 11C defines CI gate and protected boundary enforcement design.

Phase 11C does not implement CI/CD runtime.

Phase 11C does not implement production runtime.

Phase 11C does not approve production promotion.

This document specifies future CI gates and protected boundary checks required
before any local-only prototype can become a governed production candidate.

## 2. Relationship to Phase 11A and Phase 11B

- Phase 11A defines production boundary and hardening readiness.
- Phase 11B defines threat model and security control mapping.
- Phase 11C uses 11A boundaries and 11B threat/control mapping as inputs to
  define the CI gate model and protected boundary enforcement criteria.
- Phase 10 acceptance remains readiness, not approval.
- Approval remains the Phase 7D selected-gate manual boundary.

## 3. CI Gate Design Scope

Phase 11C designs the gate model only. It does not add GitHub Actions workflows,
CI/CD deployment pipelines, deployment manifests, cloud infrastructure, or
network services.

The designed gates will be implemented in a future approved phase.

## 4. Protected Boundary Design Scope

Phase 11C designs the protected boundary checks only. It does not enforce them
at runtime, does not add RBAC enforcement, and does not add production policy
engine behavior.

## 5. Gate Categories

Future CI gate categories:

- full test suite gate
- focused regression gate
- secret scanning gate
- protected-hash gate
- permission/index gate
- hardcoded path gate
- docs/state pointer consistency gate
- boundary wording gate
- no-runtime-added gate
- no-production-capability-added gate
- dependency/supply-chain gate
- artifact integrity gate
- approval-boundary drift gate
- local-only prototype containment gate
- promotion-readiness evidence gate

## 6. Required Gate Evidence

Each gate must produce:

- gate name
- gate category
- pass/fail/skip result
- evidence artifact path (relative tmp/ or test output)
- timestamp
- relevant file list
- blocking condition met (true/false)
- operator action required (if blocking)

## 7. Boundary Enforcement Design

Boundary enforcement is designed as fail-closed checks that:

- block promotion readiness if a protected boundary is violated
- require explicit operator review before override
- capture evidence of every violation
- never silently pass
- never use warning-only bypass for protected boundaries

## 8. Promotion-Blocking Criteria

A local-only prototype must not be promoted to production candidate if:

- any protected boundary check fails
- required gate evidence is missing
- approval-boundary drift is detected
- unauthorized runtime capability was introduced
- secret leakage is detected
- artifact integrity check fails
- dependency/supply-chain check fails
- Phase 7D selected-gate manual boundary is weakened
- manual approval does not override missing protected evidence unless
  explicitly approved in a later production phase

## 9. Failure Handling Model

- fail-closed gate behavior
- no silent pass
- no warning-only bypass for protected boundaries
- explicit operator review requirement
- evidence capture requirement
- known-failure classification
- retry criteria: fix the violation and re-run the gate
- escalation criteria: if fix is not possible, escalate to explicit approval
  for the specific boundary relaxation
- manual approval does not override missing protected evidence unless explicitly
  approved in a later production phase

## 10. Required Future CI Gates

These gates will be implemented in a future approved phase:

- `gate:full-suite` — all tests pass
- `gate:focused-regression` — phase-specific regression tests pass
- `gate:secret-scan` — no secret patterns in tracked files
- `gate:protected-hash` — protected file hashes match expected values
- `gate:permission-index` — shell runners are 100755 in git index
- `gate:hardcoded-path` — no hardcoded operator paths in scripts
- `gate:docs-state-pointer` — docs/state pointers are consistent
- `gate:boundary-wording` — canonical boundary phrases are present
- `gate:no-runtime-added` — no unauthorized runtime was introduced
- `gate:no-production-capability` — no production capability was added
- `gate:dependency-supply-chain` — no unauthorized dependency was added
- `gate:artifact-integrity` — audit/export artifacts have valid hashes
- `gate:approval-boundary-drift` — approval boundary language is unchanged
- `gate:local-prototype-containment` — local prototypes remain local
- `gate:promotion-readiness-evidence` — all promotion evidence is present

## 11. Required Future Protected Boundary Checks

Future protected checks:

- Phase 7D manual approval boundary preservation
- Phase 10 local advisory prototype boundary preservation
- Phase 11A production boundary readiness preservation
- Phase 11B threat/control mapping preservation
- no auth runtime introduced without approval
- no RBAC enforcement introduced without approval
- no production policy engine introduced without approval
- no backend/API/database introduced without approval
- no key/cert/secrets committed
- no signing/verifier runtime introduced without approval
- no vault write introduced without approval
- no primitive execution introduced outside selected-gate boundary
- no export mutation or re-signing
- no production deployment path introduced
- no CI/CD deployment pipeline introduced

## 12. Gate-to-Threat Mapping

| Threat | Phase 11B Control | Required CI Gate | Protected Boundary Check | Required Evidence | Blocking Condition | Deferred Phase |
|--------|-------------------|------------------|--------------------------|-------------------|--------------------|----------------|
| unauthorized operator action | operator identity boundary | gate:approval-boundary-drift | Phase 7D manual approval boundary preservation | audit artifact with operator field | approval boundary weakened | Phase 11D+ |
| forged approval event | audit integrity control | gate:artifact-integrity | Phase 7D manual approval boundary preservation | hash-chain verification report | audit hash mismatch | Phase 11D+ |
| RBAC advisory context misread as enforcement | RBAC advisory-only control | gate:boundary-wording | Phase 10 local advisory prototype boundary | canonical wording check | RBAC enforcement language found | Phase 11D+ |
| artifact tampering | export integrity control | gate:artifact-integrity | no export mutation or re-signing | integrity verification report | hash mismatch detected | Phase 11D+ |
| unsigned or incorrectly trusted export | signing boundary control | gate:artifact-integrity | no signing/verifier runtime introduced without approval | signature verification report | signature invalid or missing | Phase 11D+ |
| primitive execution outside selected-gate boundary | selected-gate enforcement | gate:no-runtime-added | no primitive execution introduced outside selected-gate boundary | Phase 7D audit artifact | unauthorized primitive invocation detected | Phase 11D+ |
| secret leakage | secret scanning control | gate:secret-scan | no key/cert/secrets committed | secret scan report | secret pattern found in tracked file | Phase 11D+ |
| key misuse | key custody control | gate:no-production-capability | no signing/verifier runtime introduced without approval | key custody audit | unauthorized key operation detected | Phase 11D+ |
| policy bypass | policy enforcement control | gate:approval-boundary-drift | no production policy engine introduced without approval | boundary wording check | policy bypass language found | Phase 11D+ |
| audit evidence mutation | audit integrity control | gate:protected-hash | no vault write introduced without approval | protected hash comparison | protected hash changed unexpectedly | Phase 11D+ |
| path traversal | path safety control | gate:hardcoded-path | no hardcoded operator paths in scripts | grep scan report | hardcoded path found | Phase 11D+ |
| hardcoded environment assumptions | environment portability control | gate:hardcoded-path | no hardcoded operator paths in scripts | CI runner path check | environment assumption detected | Phase 11D+ |
| dependency or supply-chain compromise | dependency control | gate:dependency-supply-chain | no unauthorized dependency was added | dependency diff report | unauthorized dependency found | Phase 11D+ |
| CI guardrail bypass | CI gate control | gate:full-suite | all gates must pass | full suite result | any gate failed | Phase 11D+ |
| observability blind spot | observability control | gate:promotion-readiness-evidence | all promotion evidence is present | evidence inventory | evidence missing | Phase 11D+ |
| backup/recovery gap | recovery control | gate:promotion-readiness-evidence | all promotion evidence is present | recovery posture report | recovery evidence missing | Phase 11D+ |
| local-only prototype promoted without approval | promotion control | gate:local-prototype-containment | local prototypes remain local | promotion evidence | unauthorized promotion detected | Phase 11D+ |

## 13. Gate-to-Control Mapping

| Gate | Purpose | Existing Evidence Source | Future Evidence Requirement | Failure Mode | Required Operator Action | Production Promotion Impact |
|------|---------|--------------------------|-----------------------------|--------------|--------------------------|-----------------------------|
| gate:full-suite | all tests pass | pytest output | CI artifact with pass count | test failure | fix failing test | blocks promotion |
| gate:focused-regression | phase regression passes | pytest focused output | per-phase evidence | regression failure | fix regression | blocks promotion |
| gate:secret-scan | no secrets in tracked files | Local Secret Guard workflow | secret scan report artifact | secret found | remove secret, rotate | blocks promotion |
| gate:protected-hash | protected files unchanged | git diff | hash comparison artifact | unexpected change | review and approve change | blocks promotion |
| gate:permission-index | runners are 100755 | git ls-files -s | permission check artifact | wrong mode | fix permission | blocks promotion |
| gate:hardcoded-path | no hardcoded paths | grep scan | scan report artifact | path found | remove hardcoded path | blocks promotion |
| gate:docs-state-pointer | docs are consistent | test assertions | consistency report | pointer mismatch | fix pointer | blocks promotion |
| gate:boundary-wording | canonical phrases present | test assertions | wording check artifact | phrase missing | restore phrase | blocks promotion |
| gate:no-runtime-added | no unauthorized runtime | git diff file list | runtime check artifact | runtime file found | remove or get approval | blocks promotion |
| gate:no-production-capability | no production capability | git diff + grep | capability check artifact | capability found | remove or get approval | blocks promotion |
| gate:dependency-supply-chain | no unauthorized deps | dependency diff | supply-chain report | dep found | remove or get approval | blocks promotion |
| gate:artifact-integrity | artifacts have valid hashes | Phase 8G/8H reports | integrity report artifact | hash mismatch | investigate tampering | blocks promotion |
| gate:approval-boundary-drift | approval language preserved | test assertions | drift check artifact | drift detected | restore boundary | blocks promotion |
| gate:local-prototype-containment | prototypes remain local | runtime check | containment artifact | escape detected | revert promotion | blocks promotion |
| gate:promotion-readiness-evidence | all evidence present | evidence inventory | readiness artifact | evidence missing | produce evidence | blocks promotion |

Failed protected boundary gates must block production promotion readiness.

## 14. Manual Approval Boundary Preservation

- Approval remains the Phase 7D selected-gate manual boundary.
- No CI gate result can approve a mutation.
- CI gates provide evidence and blocking, not approval.
- Manual approval does not override missing protected evidence unless explicitly
  approved in a later production phase.

## 15. Local-Only Prototype Protection

- Local-only prototypes remain local-only until governed promotion is explicitly approved.
- The local-only prototype containment gate detects unauthorized promotion.
- All Phase 8/9/10 runtime prototypes remain local-only.
- Production authentication, RBAC enforcement, key custody, backend/API/database,
  production signing, verifier runtime, and production policy engine remain out
  of scope unless explicitly approved.

## 16. Production Candidate Readiness Criteria

A local-only prototype reaches production candidate readiness when:

- all 15 CI gates pass
- all protected boundary checks pass
- threat/control mapping is current
- hardening requirements from Phase 11A are addressed
- explicit phase-specific approval is received
- Phase 7D selected-gate manual boundary is preserved

## 17. Non-Goals and Forbidden Implementations

Phase 11C does not add:

- GitHub Actions workflow
- CI/CD deployment pipeline
- deployment manifest
- cloud infrastructure
- network service
- authentication runtime
- login/session/user store
- RBAC enforcement
- production policy engine
- backend/API/database files
- production signing runtime
- verifier runtime
- key/cert files
- key custody runtime
- vault write
- primitive execution
- export mutation
- re-signing
- production secrets
- production authorization
- production promotion approval

## 18. Acceptance Criteria

- This document exists with all required sections (1-22)
- Task file exists with `phase11c_status: success`
- Tests pass
- No CI/CD runtime introduced
- No production runtime introduced
- No deployment manifest introduced
- No GitHub Actions workflow introduced by Phase 11C
- docs/state pointers reference Phase 11C
- RBAC advisory context remains not enforcement
- Approval remains the Phase 7D selected-gate manual boundary

## 19. Safe Demo Scenarios

Operator can demonstrate Phase 11C by:

1. showing this design document exists
2. showing the gate-to-threat mapping table
3. showing the gate-to-control mapping table
4. showing the failure handling model
5. showing the promotion-blocking criteria
6. confirming no CI/CD runtime was added
7. confirming no production runtime was added
8. running Phase 11C focused tests

## 20. Operator Checklist

- [ ] Phase 11C design document reviewed
- [ ] Gate categories understood
- [ ] Protected boundary checks understood
- [ ] Gate-to-threat mapping reviewed
- [ ] Gate-to-control mapping reviewed
- [ ] Failure handling model understood
- [ ] Promotion-blocking criteria understood
- [ ] No CI/CD runtime was introduced
- [ ] No production runtime was introduced
- [ ] Phase 7D approval boundary preserved
- [ ] Phase 11C tests pass

## 21. Recommended Next Step

Implement Phase 11D — Observability and Audit Retention Readiness.

Phase 11D should define the future observability model, audit retention
expectations, evidence lifecycle, incident traceability, and operational
telemetry required for governed promotion readiness.

Phase 11D must remain docs/tests-only and must not add observability runtime,
audit storage runtime, production runtime, production CI/CD, deployment
pipeline, cloud infrastructure, or production enforcement.

## 22. Recommended Next Major Subphase

Phase 11D — Observability and Audit Retention Readiness

Phase 11D should be approved separately and should remain docs/tests-only until
a later explicitly approved phase authorizes runtime implementation.
