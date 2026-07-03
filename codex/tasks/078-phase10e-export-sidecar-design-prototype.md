# Task 078 — Phase 10E Export Sidecar Design/Prototype

phase10e_status: success

phase10d_status: success

phase10c_status: success

phase10b_status: success

phase10a_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

audit_actor_attribution_integration_status: derived_report_prototype

governed_runtime_integration_status: local_evidence_bundle_actor_report_and_export_sidecar_prototypes

integration_runtime_status: local_export_sidecar_prototype

local_evidence_bundle_status: prototype_local_only

actor_attributed_audit_report_status: prototype_local_only

export_sidecar_status: prototype_local_only

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

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

backend_api_database_status: not_implemented

phase10_branch_workflow: enabled

## 1. Purpose

Implement a local-only derived export sidecar prototype that reads one manifest,
references existing local export/evidence artifacts, hashes present files, and
emits deterministic JSON/Markdown without mutating any source artifact.

## 2. Scope

- local-only derived export sidecar prototype
- one local manifest input
- export source references
- optional evidence/actor/RBAC/signature/final-acceptance context references
- deterministic JSON/Markdown output
- SHA-256 hashing for present local files
- safe missing-file warnings
- unsafe path/secret/approval/execution rejection
- no export mutation
- no re-signing
- no authentication runtime
- no RBAC enforcement
- no backend/API/database
- no wrapper behavior change

## 3. Files

- `scripts/dev/build_phase10e_export_sidecar.py`
- `scripts/dev/run_phase10e_export_sidecar.sh`
- `tests/test_phase10e_export_sidecar.py`
- `docs/PHASE10E_EXPORT_SIDECAR_DESIGN_PROTOTYPE.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md`
- additive updates to `docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md`
- additive updates to `docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md`
- additive updates to `docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`
- additive updates to `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/PHASE9F_LOCAL_RBAC_POLICY_PROTOTYPE.md`
- additive updates to `docs/PHASE8E_AUDIT_EXPORT_PACK.md`
- additive updates to `docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`
- additive updates to `docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`
- additive updates to `docs/PHASE8L_LOCAL_DETACHED_SIGNATURE_PROTOTYPE.md`
- additive updates to `docs/PHASE8M_DETACHED_SIGNATURE_VERIFIER_PROTOTYPE.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- additive updates to `.gitignore`

## 4. Status model

Phase 10E sets `phase10e_status: success` and introduces
`export_sidecar_status: prototype_local_only` while keeping authentication,
RBAC enforcement, key management runtime, and backend/API/database at
`not_implemented`.

## 5. Phase 10E sidecar objective

Produce a deterministic derived sidecar that summarizes local export sources,
Phase 10C bundle context, Phase 10D actor-attributed audit context, optional
Phase 9 actor/RBAC context, signature/export-integrity context, and the Phase
7D manual approval boundary.

## 6. Current trust boundary after Phase 10D

Phase 10D already provides a derived actor-attributed audit report. Phase 10E
may consume that report and Phase 10C evidence bundle context, but approval
remains manual at Phase 7D and no authentication or RBAC enforcement runtime is
introduced here.

## 7. Derived export sidecar model

The sidecar is derived-only, advisory-only, evidence-only, and local-only.
Export sidecar is not approval.

## 8. Sidecar input manifest model

Required fields:

- `sidecar_schema_version`
- `sidecar_id`
- `sidecar_purpose`
- `export_references`
- `approval_boundary_statement`

`sidecar_schema_version` must equal `phase10e.export_sidecar.v1`.

## 9. Export source reference model

Required fields:

- `export_id`
- `export_type`
- `export_phase`
- `export_path`
- `export_purpose`
- `export_boundary_statement`

## 10. Evidence bundle reference model

Optional `evidence_bundle_reference` may summarize `bundle_id`, `bundle_status`,
`bundle_hash`, `evidence_reference_count`, `present_evidence_count`,
`missing_evidence_count`, and `approval_boundary_statement`.

## 11. Actor-attributed audit report reference model

Optional `actor_attributed_audit_report_reference` may summarize `report_id`,
`report_status`, `report_hash`, `audit_evidence_reference_count`,
`present_evidence_count`, `missing_evidence_count`,
`actor_context_summary`, `rbac_advisory_context_summary`, and
`approval_boundary_statement`.

## 12. Actor/RBAC context reference model

Optional `actor_attribution_context_reference` and
`rbac_advisory_context_reference` may summarize local actor and advisory RBAC
fields only. Actor context is not authentication. RBAC advisory context is not
enforcement.

## 13. Signature/export integrity context model

Optional `signature_context_reference` and
`export_integrity_context_reference` may summarize verification/integrity
fields only. Verified export is not approval. Verified signature remains not
approval.

## 14. Final acceptance context model

Optional `final_acceptance_context_reference` may summarize `phase8o_status`,
`final_acceptance_status`, `reviewer_action`, and
`approval_boundary_statement`. Final acceptance remains not approval.

## 15. Approval boundary reference model

Optional `approval_boundary_reference` may re-state the Phase 7D selected-gate
manual boundary.

## 16. Source immutability model

Manifest, export sources, and optional context files are read-only during
runtime.

## 17. Export manifest preservation model

Phase 10E may hash or reference a Phase 8E export manifest, but it must not
rewrite export manifests.

## 18. Export integrity preservation model

Phase 10E may read Phase 8G/8H integrity artifacts as inputs only. It must not
alter export integrity reports.

## 19. Signature preservation model

Phase 10E may read Phase 8L/8M signature artifacts as inputs only. It must not
re-sign exports, rotate keys, or introduce production signing.

## 20. Sidecar hash model

`sidecar_hash` is deterministic SHA-256 over normalized sidecar content
excluding `sidecar_hash` itself. Sidecar hash is integrity metadata only and is
not approval.

## 21. Sidecar output model

Output files:

- `tmp/phase10e-export-sidecar/export-sidecar.json`
- `tmp/phase10e-export-sidecar/export-sidecar.md`

## 22. Runtime command model

```bash
python scripts/dev/build_phase10e_export_sidecar.py \
  --manifest path/to/export-sidecar-manifest.json \
  --output-dir tmp/phase10e-export-sidecar
```

Wrapper:

```bash
bash scripts/dev/run_phase10e_export_sidecar.sh --manifest <manifest-json>
```

## 23. Path safety model

Manifest and reference paths must resolve under the repo root, must not resolve
under `vault/`, `docs/`, `scripts/`, `codex/`, or `.git/`, and must not be
symlinks. Output must remain under `tmp/phase10e-export-sidecar/`.

## 24. Privacy and secret scan model

Secret-like strings, raw email addresses, external URLs, approval flags, and
execution intent are rejected as critical issues.

## 25. Non-authentication boundary

Actor context is not authentication. Actor attribution is not authentication.

## 26. Non-RBAC-enforcement boundary

RBAC advisory context is not enforcement. `rbac_enforcement_status` remains
`not_implemented`.

## 27. Non-approval boundary

Export sidecar is not approval.

Export sidecar validity is not approval.

Export sidecar inclusion is not approval.

Export sidecar hash is not approval.

Export manifest hash is not approval.

Verified export is not approval.

Signed export is not approval.

Verified signature remains not approval.

Signature verifier result is not approval.

Final acceptance remains not approval.

Actor-attributed audit report is not approval.

RBAC allow decision is not approval.

Evidence bundle validity is not approval.

Approval remains Phase 7D selected-gate manual boundary.

## 28. Compatibility with Phase 10D

Phase 10E may read `docs/PHASE10D_DERIVED_ACTOR_ATTRIBUTED_AUDIT_REPORT_PROTOTYPE.md`
artifacts as context only and does not modify Phase 10D runtime behavior.

## 29. Compatibility with Phase 10C

Phase 10E may read `docs/PHASE10C_LOCAL_EVIDENCE_BUNDLE_ACTOR_RBAC_CONTEXT.md`
artifacts as context only and does not modify Phase 10C runtime behavior.

## 30. Compatibility with Phase 10B

Phase 10E follows
`docs/PHASE10B_ACTOR_ATTRIBUTION_AUDIT_STORE_INTEGRATION_PLAN.md` and remains
derived-only. It does not mutate audit store actor fields.

## 31. Compatibility with Phase 10A

Phase 10E remains inside the governed readiness boundary from
`docs/PHASE10A_GOVERNED_RUNTIME_INTEGRATION_READINESS_DESIGN.md`.

## 32. Compatibility with Phase 9G/9F/9D/9C

Phase 10E may reference local operator registry, actor attribution, and
advisory RBAC outputs as evidence context only.

## 33. Compatibility with Phase 8O/8M/8L/8H/8G/8E

Phase 10E may reference final acceptance, signature verification, detached
signature, integrity verifier, and export pack artifacts as local evidence
only.

Canonical Phase 8B artifact:

- `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`

Canonical Phase 8B focused test:

- `tests/test_phase8b_local_append_only_audit_store.py`

Compatibility note:
earlier task wording may refer to
`PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE_PROTOTYPE.md`, but the canonical Phase
8B document is `PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`.

## 34. Compatibility with Phase 7D

Phase 10E may reference the Phase 7D boundary, but it does not invoke the
wrapper, approval primitives, or next-gate execution.

## 35. Failure taxonomy

- `built`
- `built_with_warnings`
- `not_built`

Critical failures reject unsafe paths, secrets, approval flags, and execution
intent. Safe missing references produce warnings and exit 0.

## 36. Reviewer action mapping

- `no_action_required`
- `manual_review_required`
- `reject_export_sidecar_until_resolved`
- `reject_runtime_scope_until_resolved`

## 37. Non-goals

- authentication runtime
- RBAC enforcement runtime
- backend/API/database
- key custody or production signing
- export mutation
- wrapper execution
- primitive execution
- approval automation

## 38. Test strategy

Use TDD. Add `tests/test_phase10e_export_sidecar.py` first, verify RED, then
implement minimal runtime and doc/state updates until the focused regressions
are green.

## 39. Acceptance criteria

- valid local manifest builds deterministic JSON/Markdown under
  `tmp/phase10e-export-sidecar/`
- present references include SHA-256, size, and relative path
- safe missing references produce warnings and exit 0
- unsafe paths, secrets, approval flags, or execution intent produce
  `not_built` and nonzero exit
- source artifacts remain unchanged

## 40. Focused verification commands

```bash
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase10e_export_sidecar.py
python -m pytest -q tests/test_phase10d_actor_attributed_audit_report.py
python -m pytest -q tests/test_phase10c_local_evidence_bundle.py
python -m pytest -q tests/test_phase10b_actor_attribution_audit_store_integration_plan.py
python -m pytest -q tests/test_phase10a_governed_runtime_integration_readiness_design.py
python -m pytest -q tests/test_phase9f_local_rbac_policy_prototype.py
python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase8h_export_integrity_verifier_hardening.py
python -m pytest -q tests/test_phase8g_export_integrity_verifier.py
python -m pytest -q tests/test_phase8e_audit_export_pack.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py

python -m py_compile scripts/dev/build_phase10e_export_sidecar.py
bash -n scripts/dev/run_phase10e_export_sidecar.sh
```

## 41. Known limitations

- local-only prototype
- derived export sidecar only
- no auth runtime
- no RBAC enforcement
- no backend/API/database
- no export mutation

## 42. Final status target

`phase10e_status: success`
