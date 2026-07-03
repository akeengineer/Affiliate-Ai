# Task 073 — Phase 9G Phase 9 Acceptance Pack

phase9g_status: success

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

Phase 9G closes Phase 9 by producing the final acceptance pack for the
identity, actor metadata, local registry, actor attribution, RBAC design, and
local advisory RBAC policy prototype work. Phase 9G is docs/tests only and adds
no runtime behavior.

## 2. Scope

- docs/tests acceptance pack only
- Phase 9A–9F summary
- safe demo scenarios
- acceptance, full-suite readiness, PR readiness, and merge readiness checklists
- runtime safety, identity boundary, actor metadata, registry, attribution, RBAC
  advisory, approval boundary, protected runtime, and artifact safety checklists
- known limitations and recommended next major phase
- no new runtime scripts, no shell runner, no auth runtime, no RBAC
  enforcement, no backend/API/database, no key/cert files, no wrapper behavior
  change, no primitive execution, no vault read/write, no production deployment

## 3. Files

- `codex/tasks/073-phase9g-phase9-acceptance-pack.md`
- `docs/PHASE9G_PHASE9_ACCEPTANCE_PACK.md`
- `tests/test_phase9g_phase9_acceptance_pack.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`
- additive updates to `docs/PHASE9E_RBAC_DESIGN.md`
- additive updates to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive updates to `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`

No Phase 9G runtime script or shell runner is added.

## 4. Status model

- `phase9g_status: success` — the acceptance pack, task, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — unchanged.
- `identity_boundary_status: design_only` — unchanged.
- `actor_metadata_schema_status: design_only` — unchanged.
- `actor_metadata_runtime_status: local_registry_prototype` — unchanged.
- `local_operator_registry_status: prototype_local_only` — unchanged.
- `actor_attribution_status: local_report_prototype` — unchanged.
- `rbac_design_status: design_only` — unchanged.
- `rbac_policy_status: local_advisory_prototype` — unchanged.
- `rbac_runtime_status: local_advisory_prototype` — unchanged.
- `rbac_enforcement_status: not_implemented` — unchanged.
- `identity_runtime_status: not_implemented` — unchanged.
- `authentication_runtime_status: not_implemented` — unchanged.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `phase9_branch_workflow: enabled` — Phase 9G closes the Phase 9 branch.

## 5. Phase 9 acceptance objective

Provide a single acceptance reference summarizing Phase 9A–9F, defining safe
demo scenarios, checklists, and PR/merge readiness, while guaranteeing the
acceptance pack itself never becomes approval.

## 6. Current trust boundary after Phase 9F

Phase 9A defines the identity boundary; Phase 9B defines the actor metadata
schema; Phase 9C implements a local registry prototype; Phase 9D implements a
local attribution report prototype; Phase 9E defines the RBAC boundary; Phase 9F
implements a local advisory RBAC policy prototype; Phase 9G adds acceptance
evidence only. No authentication runtime, RBAC enforcement, production policy
engine, backend/API/database, or key management runtime exists. Operator
identity remains unauthenticated or operator-declared.

## 7. Phase 9 component summary

Summarizes 9A–9G with artifact category, runtime status, safety boundary, and
approval boundary for each component.

## 8. Phase 9A acceptance summary

Design-only identity boundary; `identity_boundary_status: design_only`;
operator identity is not approval.

## 9. Phase 9B acceptance summary

Design-only actor metadata schema; `actor_metadata_schema_status: design_only`;
schema validity is not approval.

## 10. Phase 9C acceptance summary

Local operator registry prototype; `local_operator_registry_status:
prototype_local_only`; registry presence is not authentication or approval.

## 11. Phase 9D acceptance summary

Local actor attribution report prototype; `actor_attribution_status:
local_report_prototype`; actor attribution is not authentication or approval.

## 12. Phase 9E acceptance summary

Design-only RBAC boundary; `rbac_design_status: design_only`; RBAC eligibility
is not approval.

## 13. Phase 9F acceptance summary

Local advisory RBAC policy prototype; `rbac_policy_status:
local_advisory_prototype`, `rbac_runtime_status: local_advisory_prototype`,
`rbac_enforcement_status: not_implemented`; RBAC allow decision is not approval.

## 14. Safe demo scenarios

Nine safe demo scenarios: valid local operator registry build, registry
secret/privacy rejection, actor attribution report build, actor attribution
actor-not-found rejection, RBAC advisory allow, RBAC explicit deny precedence,
RBAC `execute_primitive` hard block, `approve_selected_gate` advisory-only with
the `require_phase7d_selected_gate` obligation, and final acceptance evidence
attribution without approval inference. Each scenario states purpose, input
artifacts, a local-only conceptual command, expected output, safety boundary,
and approval boundary; no scenario command includes approval flags,
`--execute`, wrapper calls, primitive calls, network calls, backend/API/database
calls, or key commands.

## 15. Acceptance criteria

Phase 9A–9F checkpoints exist; the Phase 9G acceptance doc and tests exist and
pass; Phase 9A–9F, Phase 8O/8M/8L, and Phase 7D focused regressions pass; the
full suite passes before PR; no new runtime is added in Phase 9G; no
auth/RBAC-enforcement/policy-engine/backend/API/database/key-cert runtime
exists; no primitive execution or vault write occurs; no wrapper or Phase 8/9C/
9D/9F runtime behavior changes; approval boundary statements are preserved.

## 16. Full-suite readiness checklist

Run focused checks first; normalize shell runner permissions to 755; verify git
index 100755 for the 9F/9D/9C/8M/8L/8G runners; run the full suite
(`env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q`); confirm it
passes; run `git diff --check`; run the hardcoded path grep over scripts;
confirm the worktree is clean after the checkpoint commit; fix only local
chmod drift before a rerun.

## 17. PR readiness checklist

Branch `feature/phase9-identity-boundary` targeting `main`; recommended title
`complete Phase 9 identity and RBAC governance workflow`; PR body includes the
Phase 9A–9G summary, focused test results, full-suite result, local-only
prototype status, no-authentication/no-RBAC-enforcement/no-backend-API-database/
no-key-cert statements, no wrapper/primitive/vault mutation, the Phase 7D
approval boundary statement, and known limitations; do not merge until CI is
green.

## 18. Merge readiness checklist

CI green; no requested changes; no merge conflicts; PR body complete; full
suite reported; runtime safety, approval boundary, protected files, and
artifact safety reviewed; squash merge recommended; delete the feature branch
after merge and sync main.

## 19. Runtime safety checklist

Phase 9G adds no runtime script or shell runner; Phase 9F remains advisory-only;
Phase 9D remains attribution-only; Phase 9C remains local registry
metadata-only; no auth runtime, RBAC enforcement, policy engine,
backend/API/database, package.json, workflow/deployment files, key/cert files,
external APIs, network behavior, primitive execution, or vault write exists.

## 20. Identity boundary checklist

Identity boundary is design-only; operator identity remains unauthenticated or
operator-declared; authenticated/operator/reviewer/signer identity and actor
attribution are all not approval.

## 21. Actor metadata checklist

Actor metadata schema exists; schema validity, `actor_id`, identity assurance,
identity source, and session reference are all not approval; an approval
boundary statement is required.

## 22. Registry checklist

Local operator registry is `prototype_local_only`; registry presence is not
authentication or approval; valid actor metadata is not approval; the registry
report is evidence only; registry writes only under
`tmp/phase9c-local-operator-registry/`.

## 23. Attribution checklist

Actor attribution is `local_report_prototype`; actor attribution is not
authentication or approval; the attributed report is evidence only; attribution
writes only under `tmp/phase9d-actor-attribution/`.

## 24. RBAC advisory checklist

RBAC design is `design_only`; policy status and runtime status are
`local_advisory_prototype`; enforcement status is `not_implemented`; the local
RBAC policy prototype is not enforcement; allow decision and eligibility are not
approval; the advisory report is evidence only; explicit deny precedence is
advisory only; `execute_primitive` is hard-blocked; `approve_selected_gate`
advisory allow still requires the Phase 7D selected-gate manual boundary.

## 25. Approval boundary preservation

The acceptance pack, its evidence, identity boundary, actor metadata, actor
attribution, registry presence, RBAC policy/eligibility/decision/report, and
authenticated identity are all not approval; signature verification and final
acceptance remain not approval; approval remains the Phase 7D selected-gate
manual boundary; the acceptance pack must not trigger the wrapper, execute
primitives, trigger the next gate, or set approval flags.

## 26. Compatibility with Phase 9C

Phase 9G validates that the registry remains not authentication or approval and
does not modify Phase 9C runtime.

## 27. Compatibility with Phase 9B

Phase 9G validates that schema validity remains not approval.

## 28. Compatibility with Phase 9A

Phase 9G validates that identity remains not approval.

## 29. Compatibility with Phase 8O/8L/8M

Phase 9 extends acceptance evidence with identity/RBAC governance but does not
modify Phase 8O/8L/8M runtime; signature verification and final acceptance
remain not approval.

## 30. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; Phase 9G does not
modify Phase 7D.

## 31. Failure taxonomy

Not applicable at runtime (Phase 9G is docs/tests only); acceptance criteria
failures are tracked via the acceptance/full-suite/PR/merge readiness
checklists above.

## 32. Reviewer action mapping

Not applicable at runtime; PR review follows the standard PR/merge readiness
checklists.

## 33. Non-goals

Phase 9G does not add runtime scripts or shell runners, does not modify Phase
9C/9D/9F runtime, Phase 8 runtime, or the Phase 7D wrapper, does not implement
authentication, RBAC enforcement, a production policy engine, login, sessions, a
user store, OAuth/OIDC/SAML runtime, or backend/API/database behavior, executes
no primitives, writes no vault, and creates no production deployment.

## 34. Test strategy

`tests/test_phase9g_phase9_acceptance_pack.py` verifies file existence and
status, scope safety, required sections, component summary assertions, safe
demo scenario assertions, acceptance/full-suite/PR/merge readiness assertions,
runtime safety assertions, identity/actor/registry/attribution assertions, RBAC
advisory assertions, approval boundary assertions, protected runtime
compatibility, artifact safety, documentation regressions, and static safety on
new Phase 9G files only. No Phase 9G runtime script or shell runner is added.

## 35. Acceptance criteria (final)

- task, doc, and tests exist and pass
- Phase 9A–9F, Phase 8O/8M/8L, and Phase 7D focused regressions pass
- full suite passes before PR
- protected runtime files remain unchanged
- no Phase 9G runtime script/shell runner/auth/RBAC-enforcement/backend/key
  files are added
- Phase 9 acceptance pack, RBAC allow decision, and RBAC advisory report remain
  not approval / evidence only
- approval remains Phase 7D selected-gate manual boundary

## 36. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9g_phase9_acceptance_pack.py
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
find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## 37. Full-suite verification command

```text
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
```

If the full suite fails only because a shell runner filesystem mode drifted to
`0775`, do not create hotfix logic: run
`find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;`, verify
filesystem `755` and git index `100755` for the 9F/9D/9C/8M/8L/8G runners, and
rerun the full suite.

## 38. Known limitations

- no authentication, no RBAC enforcement, no production policy engine, no
  login, no session runtime, no user store, no enterprise identity, no
  governed key custody, no strong non-repudiation, no backend/API/database, no
  production deployment
- local prototypes only, advisory reports only
- approval remains manual Phase 7D boundary

## 39. Recommended next major phase

Phase 10 — Governed Runtime Integration Readiness. Phase 10 should not
immediately implement production auth/RBAC; it should first decide whether to
harden the local identity/RBAC prototypes, connect actor attribution into audit
store outputs, or design production authentication integration.

## 40. Final status target

phase9g_status: success
