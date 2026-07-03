# Phase 9G — Phase 9 Acceptance Pack

phase9g_status: success

phase9a_status: success

phase9b_status: success

phase9c_status: success

phase9d_status: success

phase9e_status: success

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

Phase 9G closes Phase 9 by providing the acceptance pack for identity, actor
metadata, local registry, actor attribution, RBAC design, and the local
advisory RBAC policy prototype.

Phase 9G does not add runtime behavior.

### Scope

- docs/tests acceptance pack
- Phase 9A–9F summary
- safe demo scenarios
- acceptance criteria
- full-suite readiness checklist
- PR readiness checklist
- merge readiness checklist
- runtime safety checklist
- identity boundary checklist
- actor metadata checklist
- registry checklist
- attribution checklist
- RBAC advisory checklist
- approval boundary checklist
- protected runtime compatibility checklist
- artifact safety checklist
- known limitations
- no new runtime scripts
- no shell runner
- no auth runtime
- no RBAC enforcement
- no backend/API/database
- no key/cert files
- no wrapper behavior change
- no primitive execution
- no vault read/write
- no production deployment

### Current trust boundary after Phase 9F

- Phase 9A defines identity boundary.
- Phase 9B defines actor metadata schema.
- Phase 9C implements local operator registry prototype.
- Phase 9D implements local actor attribution report prototype.
- Phase 9E defines RBAC boundary.
- Phase 9F implements local advisory RBAC policy prototype.
- Phase 9G adds acceptance evidence only.
- No authentication runtime exists.
- No RBAC enforcement exists.
- No production policy engine exists.
- No backend/API/database exists.
- No key management runtime exists.
- Operator identity remains unauthenticated or operator-declared.
- Approval remains Phase 7D selected-gate manual boundary.

### Phase 9 component summary

| Component | Artifact category | Runtime status | Safety boundary | Approval boundary |
|---|---|---|---|---|
| 9A Operator Identity Boundary Design | docs/tests design | `identity_boundary_status: design_only` | no runtime | operator identity is not approval |
| 9B Actor Metadata Schema Design | docs/tests design | `actor_metadata_schema_status: design_only` | no runtime | actor metadata is not approval |
| 9C Local Operator Registry Prototype | local Python + shell prototype | `actor_metadata_runtime_status: local_registry_prototype`, `local_operator_registry_status: prototype_local_only` | writes only under `tmp/phase9c-local-operator-registry/` | registry presence is not authentication or approval |
| 9D Actor Attribution in Audit/Reports | local Python + shell prototype | `actor_attribution_status: local_report_prototype` | writes only under `tmp/phase9d-actor-attribution/` | actor attribution is not authentication or approval |
| 9E RBAC Design | docs/tests design | `rbac_design_status: design_only` | no runtime | RBAC eligibility is not approval |
| 9F Local RBAC Policy Prototype | local Python + shell prototype | `rbac_policy_status: local_advisory_prototype`, `rbac_runtime_status: local_advisory_prototype`, `rbac_enforcement_status: not_implemented` | writes only under `tmp/phase9f-local-rbac-policy/` | RBAC advisory decision is not approval; RBAC advisory report is evidence only |
| 9G Phase 9 Acceptance Pack | docs/tests acceptance | `phase9g_status: success` | no runtime added | acceptance pack is not approval |

### Safe demo scenarios

1. **Valid local operator registry build**
   - purpose: demonstrate deterministic local registry construction.
   - input artifacts: a local JSON file of conceptual actor_metadata records.
   - conceptual command:
     `bash scripts/dev/run_phase9c_local_operator_registry.sh --input tmp/phase9c-test-input/operators.json --mode build`
   - expected output: `operator-registry.json` and reports under
     `tmp/phase9c-local-operator-registry/`, `registry_status: built`.
   - safety boundary: writes only under `tmp/phase9c-local-operator-registry/`.
   - approval boundary: registry presence is not authentication or approval.

2. **Registry secret/privacy rejection**
   - purpose: demonstrate the privacy/secret scan rejects unsafe input.
   - input artifacts: an actor record containing a secret-like marker.
   - conceptual command: same registry build command against the unsafe fixture.
   - expected output: nonzero exit, `validation_status: invalid`,
     `identity_metadata_contains_secret` issue.
   - safety boundary: no secret is persisted to a registry file.
   - approval boundary: rejection is advisory only, not an incident by itself.

3. **Actor attribution report build**
   - purpose: demonstrate joining registry actors to evidence references.
   - input artifacts: an existing `operator-registry.json` and a local evidence
     reference file.
   - conceptual command:
     `bash scripts/dev/run_phase9d_actor_attribution_report.sh --registry tmp/phase9c-local-operator-registry/operator-registry.json --evidence tmp/phase9d-test-input/evidence-references.json --actor-id actor_local_operator`
   - expected output: `actor-attribution-report.json`/`.md` under
     `tmp/phase9d-actor-attribution/`, `attribution_report_status: built`.
   - safety boundary: writes only under `tmp/phase9d-actor-attribution/`.
   - approval boundary: attributed report is evidence only.

4. **Actor attribution actor-not-found rejection**
   - purpose: demonstrate deterministic failure when the requested actor is
     absent from the registry.
   - input artifacts: the same registry, with `--actor-id` set to an unknown
     value.
   - conceptual command: the same attribution report command with a bad
     `--actor-id`.
   - expected output: nonzero exit,
     `actor_attribution_status: failed_actor_not_found`, `actor_not_found`
     issue.
   - safety boundary: no report is falsely marked built.
   - approval boundary: rejection is advisory only.

5. **RBAC advisory allow**
   - purpose: demonstrate an advisory allow decision.
   - input artifacts: a local RBAC policy JSON and a request JSON matching an
     allow permission.
   - conceptual command:
     `bash scripts/dev/run_phase9f_local_rbac_policy.sh --policy tmp/phase9f-test-input/local-rbac-policy.json --request tmp/phase9f-test-input/rbac-request.json`
   - expected output: `advisory_decision: allow`,
     `decision_reason: policy_allow`.
   - safety boundary: no wrapper, primitive, or vault call occurs.
   - approval boundary: allow is advisory only, not approval.

6. **RBAC explicit deny precedence**
   - purpose: demonstrate that an explicit deny permission always overrides a
     matching allow permission.
   - input artifacts: a policy with both a matching allow and a matching deny
     permission for the same request.
   - conceptual command: the same evaluator command against that policy.
   - expected output: `advisory_decision: deny`,
     `decision_reason: explicit_deny`.
   - safety boundary: deny does not trigger remediation or incident automation.
   - approval boundary: deny is not an incident by itself.

7. **RBAC execute_primitive hard block**
   - purpose: demonstrate that `execute_primitive` is always denied regardless
     of policy content.
   - input artifacts: a request with `action: execute_primitive`.
   - conceptual command: the same evaluator command against that request.
   - expected output: `advisory_decision: deny`,
     `decision_reason: primitive_execution_blocked`,
     `reviewer_action: reject_action_until_resolved`.
   - safety boundary: no primitive is executed by the evaluator.
   - approval boundary: the block itself is not approval or enforcement.

8. **`approve_selected_gate` advisory-only with `require_phase7d_selected_gate` obligation**
   - purpose: demonstrate that RBAC eligibility for the Phase 7D gate action
     remains advisory only.
   - input artifacts: a policy allowing `approve_selected_gate` for a reviewer
     role, and a matching request.
   - conceptual command: the same evaluator command against that request.
   - expected output: `advisory_decision: allow` with obligation
     `require_phase7d_selected_gate`; the Phase 7D wrapper is never called.
   - safety boundary: no wrapper invocation occurs from the evaluator.
   - approval boundary: allow is not approval; approval remains the Phase 7D
     selected-gate manual boundary.

9. **Final acceptance evidence attribution without approval inference**
   - purpose: demonstrate that attributing a Phase 8O final acceptance evidence
     reference to an actor does not imply approval.
   - input artifacts: an evidence reference describing a Phase 8O final
     acceptance artifact, attributed via the Phase 9D tool.
   - conceptual command: the Phase 9D attribution report command with an
     evidence reference of `evidence_phase: phase8o`.
   - expected output: an attributed record with
     `attribution_status: attributed`; the report explicitly states final
     acceptance remains not approval.
   - safety boundary: no Phase 8O runtime file is touched.
   - approval boundary: final acceptance remains not approval; attribution is
     not approval.

All scenario commands are local-only and never include approval flags,
`--execute`, wrapper calls, primitive calls, network calls, backend/API/database
calls, or key commands.

### Acceptance criteria

- Phase 9A–9F checkpoints exist.
- Phase 9G acceptance doc exists.
- Phase 9G tests pass.
- Phase 9A/9B/9C/9D/9E/9F focused regressions pass.
- Phase 8O/8M/8L focused regressions pass.
- Phase 7D focused regression passes.
- full suite passes before PR.
- no new runtime in 9G.
- no auth runtime.
- no RBAC enforcement.
- no production policy engine.
- no backend/API/database.
- no key/cert files.
- no primitive execution.
- no vault write.
- no wrapper behavior change.
- no Phase 8 runtime behavior change.
- no Phase 9C/9D/9F runtime behavior change.
- approval boundary statements preserved.

### Full-suite readiness checklist

- run focused checks first.
- normalize shell runner permissions to 755.
- verify git index 100755 for 9F/9D/9C/8M/8L/8G runners.
- run full suite:
  `env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q`
- confirm full suite passes.
- run `git diff --check`.
- run hardcoded path grep over scripts.
- confirm worktree clean after checkpoint commit.
- if permission drift occurs, fix local chmod only before rerun.

### PR readiness checklist

- branch is `feature/phase9-identity-boundary`.
- base is `main`.
- PR title recommendation: `complete Phase 9 identity and RBAC governance workflow`.
- PR body must include:
  - Phase 9A–9G summary
  - focused test results
  - full-suite result
  - local-only prototype status
  - no authentication runtime
  - no RBAC enforcement
  - no backend/API/database
  - no key/cert files
  - no wrapper/primitive/vault mutation
  - approval remains Phase 7D selected-gate manual boundary
  - known limitations
- do not merge until CI is green.

### Merge readiness checklist

- CI checks green.
- no requested changes.
- no merge conflict.
- PR body complete.
- full suite reported.
- runtime safety reviewed.
- approval boundary reviewed.
- protected files reviewed.
- artifact safety reviewed.
- squash merge recommended.
- delete feature branch after merge and main sync.

### Runtime safety checklist

- Phase 9G added no runtime scripts.
- Phase 9G added no shell runner.
- Phase 9F remains advisory-only.
- Phase 9D remains attribution-only.
- Phase 9C remains local registry metadata-only.
- no auth runtime.
- no RBAC enforcement.
- no policy engine.
- no backend/API/database.
- no package.json.
- no workflow/deployment.
- no key/cert files.
- no external APIs.
- no network.
- no primitive execution.
- no vault write.

### Identity boundary checklist

- identity boundary is design-only.
- operator identity remains unauthenticated or operator-declared.
- authenticated identity is not approval.
- operator identity is not approval.
- reviewer identity is not approval.
- signer identity is not approval.
- actor attribution is not approval.

### Actor metadata checklist

- actor metadata schema exists.
- schema validity is not approval.
- actor_id is not approval.
- identity assurance is not approval.
- identity source is not approval.
- session reference is not approval.
- approval boundary statement required.

### Registry checklist

- local operator registry is `prototype_local_only`.
- registry presence is not authentication.
- registry presence is not approval.
- valid actor metadata is not approval.
- registry report is evidence only.
- registry writes only under `tmp/phase9c-local-operator-registry/`.

### Attribution checklist

- actor attribution is `local_report_prototype`.
- actor attribution is not authentication.
- actor attribution is not approval.
- actor-attributed report is evidence only.
- attribution writes only under `tmp/phase9d-actor-attribution/`.

### RBAC advisory checklist

- RBAC design is `design_only`.
- RBAC policy status is `local_advisory_prototype`.
- RBAC runtime status is `local_advisory_prototype`.
- RBAC enforcement status is `not_implemented`.
- local RBAC policy prototype is not enforcement.
- RBAC allow decision is not approval.
- RBAC eligibility is not approval.
- RBAC advisory report is evidence only.
- explicit deny precedence is advisory only.
- `execute_primitive` is hard-blocked.
- `approve_selected_gate` advisory allow still requires the Phase 7D
  selected-gate manual boundary.

### Approval boundary checklist

- Phase 9 acceptance pack is not approval.
- acceptance pack evidence is not approval.
- identity boundary is not approval.
- actor metadata is not approval.
- actor attribution is not approval.
- local operator registry is not authentication.
- registry presence is not approval.
- local RBAC policy prototype is not enforcement.
- RBAC allow decision is not approval.
- RBAC eligibility is not approval.
- RBAC advisory decision is not approval.
- RBAC advisory report is evidence only.
- authenticated identity is not approval.
- signature verification remains not approval.
- final acceptance remains not approval.
- approval remains Phase 7D selected-gate manual boundary.
- acceptance pack must not trigger wrapper.
- acceptance pack must not execute primitives.
- acceptance pack must not trigger next gate.
- acceptance pack must not set approval flags.

### Protected runtime compatibility checklist

Protected runtime files:

- `scripts/dev/evaluate_phase9f_local_rbac_policy.py`
- `scripts/dev/run_phase9f_local_rbac_policy.sh`
- `scripts/dev/build_phase9d_actor_attribution_report.py`
- `scripts/dev/run_phase9d_actor_attribution_report.sh`
- `scripts/dev/manage_phase9c_local_operator_registry.py`
- `scripts/dev/run_phase9c_local_operator_registry.sh`
- `scripts/dev/verify_phase8m_detached_signature.py`
- `scripts/dev/run_phase8m_detached_signature_verifier.sh`
- `scripts/dev/build_phase8l_detached_signature.py`
- `scripts/dev/run_phase8l_detached_signature.sh`
- `scripts/dev/verify_phase8g_export_integrity.py`
- `scripts/dev/run_phase8g_export_integrity.sh`
- `scripts/dev/run_phase7d_single_gate_wrapper.sh`
- `scripts/dev/execute_single_gate_approval.py`

Phase 9G must not modify protected runtime files.

### Artifact safety checklist

- no `.pem`/`.key`/`.crt`/`.p12`/`.pfx` files.
- no `package.json`.
- no backend/API/database files.
- no `.sql`/`.sqlite`/`.db` files.
- no `.rego` files.
- no OPA policy files.
- no production policy runtime files.
- no OAuth/OIDC/SAML config files.
- no workflow/deployment files.
- no key/cert material.

### Known limitations

- no authentication.
- no RBAC enforcement.
- no production policy engine.
- no login.
- no session runtime.
- no user store.
- no enterprise identity.
- no governed key custody.
- no strong non-repudiation.
- no backend/API/database.
- no production deployment.
- local prototypes only.
- advisory reports only.
- approval remains manual Phase 7D boundary.

### Recommended next major phase

Recommended next major phase: **Phase 10 — Governed Runtime Integration
Readiness**.

Phase 10 should not immediately implement production auth/RBAC. It should first
decide whether to harden the local identity/RBAC prototypes, connect actor
attribution into audit store outputs, or design production authentication
integration.
