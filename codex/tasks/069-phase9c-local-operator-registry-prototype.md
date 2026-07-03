# Task 069 — Phase 9C Local Operator Registry Prototype

phase9c_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

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

Phase 9C implements a local-only operator registry prototype for conceptual
Phase 9B actor metadata records, based on the Phase 9A identity boundary. It
validates a local subset of the schema, can build a deterministic local registry
file, and emits local registry reports — all metadata-only and evidence-only.

## 2. Scope

- local-only operator registry prototype (standard library only)
- actor metadata validation subset over Phase 9B fields/enums
- deterministic local registry JSON and reports
- validate/build/list/report modes
- privacy/secret scan and approval boundary enforcement
- outputs only under `tmp/phase9c-local-operator-registry/`
- no authentication, RBAC, login, sessions, user store
- no backend/API/database, no network, no database drivers
- no key management runtime, no key/cert files
- no Phase 7D wrapper change, no Phase 8 runtime change
- no primitive execution, no vault read/write

## 3. Files

- `scripts/dev/manage_phase9c_local_operator_registry.py`
- `scripts/dev/run_phase9c_local_operator_registry.sh`
- `tests/test_phase9c_local_operator_registry_prototype.py`
- `codex/tasks/069-phase9c-local-operator-registry-prototype.md`
- `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- `.gitignore` (add Phase 9C tmp roots)

## 4. Status model

- `phase9c_status: success` — the prototype, runner, task, doc, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — Phase 8 posture
  unchanged.
- `identity_boundary_status: design_only` — Phase 9A boundary remains design-only.
- `actor_metadata_schema_status: design_only` — Phase 9B schema remains
  design-only.
- `actor_metadata_runtime_status: local_registry_prototype` — a local registry
  prototype now exists.
- `local_operator_registry_status: prototype_local_only` — local prototype only.
- `identity_runtime_status: not_implemented` — no identity runtime exists.
- `rbac_runtime_status: not_implemented` — no RBAC runtime exists.
- `authentication_runtime_status: not_implemented` — no authentication runtime.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `phase9_branch_workflow: enabled` — Phase 9C continues the Phase 9 branch.

## 5. Local operator registry objective

Provide a local, deterministic, evidence-only registry over conceptual actor
metadata records that validates the Phase 9B subset, records attribution, and
never becomes authentication or approval.

## 6. Current trust boundary after Phase 9B

Phase 9A defines the identity boundary; Phase 9B defines the schema contract;
Phase 9C adds a local validation/registry prototype only. No identity,
authentication, RBAC, session, user store, or key management runtime exists.
Operator identity remains unauthenticated or operator-declared.

## 7. Local registry data model

Input actor metadata records; outputs `operator-registry.json`,
`operator-registry-report.json`, `operator-registry-report.md`,
`operator-registry-list.json`, `operator-registry-list.md` under
`tmp/phase9c-local-operator-registry/`. Outputs are local evidence only.

## 8. Registry input contract

Input is a JSON object (single record or `{ "actor_metadata": [...] }`) or a JSON
array of records. Missing input path, invalid JSON, and non-object/non-array
scalars are nonzero-exit failures.

## 9. Registry output contract

Deterministic JSON (`sort_keys=True`, `indent=2`) and Markdown reports carrying
the required status fields, counts, severity counts, reviewer action, incident
classification, approval boundary statement, safety statement, limitations, and
issues.

## 10. Registry command model

`--input`, `--output-dir` (default `tmp/phase9c-local-operator-registry`),
`--mode` (`validate`|`build`|`list`|`report`, default `build`). No approval
flags and no `--execute`.

## 11. Actor metadata validation subset

Validates the 14 required Phase 9B fields and the allowed enums for
`actor_schema_version`, `actor_type`, `actor_role_labels`,
`actor_identity_assurance`, `actor_identity_source`, and
`actor_action_scope.action_category`.

## 12. actor_id validation

Must match `^actor_[a-z0-9_-]{3,64}$`; no whitespace, `@`, URL scheme,
secret-like markers, or approval-like literals.

## 13. actor_type validation

Value must be one of the allowed actor types; otherwise `actor_type_unknown`.

## 14. identity assurance validation

Value must be one of the allowed assurance levels; otherwise
`actor_identity_assurance_insufficient`. Missing field is
`actor_identity_assurance_missing`.

## 15. identity source validation

Value must be one of the allowed sources; otherwise
`actor_identity_source_unknown`.

## 16. role label validation

`actor_role_labels` must be a list of allowed labels; otherwise
`actor_role_label_unknown`.

## 17. action scope validation

`actor_action_scope.action_category` must be one of the allowed scope values;
otherwise `actor_scope_invalid`.

## 18. privacy and secret scan model

All string fields are scanned for secret-like markers (private-key headers,
`API_KEY=`, `SECRET=`, `TOKEN=`, `PASSWORD=`, `AWS_SECRET_ACCESS_KEY`, `ssh-rsa`,
OAuth `access_token`/`id_token`/`refresh_token`, raw
`AFFILIATE_PHASE8L_PROTOTYPE_KEY`) and external URL schemes; raw emails are
flagged as unnecessary PII. Matches are critical/reject.

## 19. approval boundary enforcement model

`approval_boundary_statement` must include an approval boundary phrase; approval
flag fields (`approved`, `is_approved`, `approval_granted`, `auto_approve`,
`approve_all`, `next_gate`, `execute`) and primitive-execution-intent fields must
not be truthy.

## 20. deterministic output model

JSON is written with `sort_keys=True` and `indent=2`; no wall-clock timestamp is
generated, so build/list/report outputs are reproducible.

## 21. duplicate actor handling

Duplicate `actor_id` records do not crash; the first valid record is kept
deterministically; `duplicate_actor_count` is reported and a warning issue with
`manual_review_required` is emitted.

## 22. list/report behavior

`list` reads the existing registry and writes an actor listing; `report` reads
the existing registry and rewrites the registry report. Neither mutates outside
the output directory.

## 23. path safety model

Input must resolve under the repo root, must not be under
`vault/`/`docs/`/`scripts/`/`codex/`/`.git/`, and must not be a symlink; the
output directory must resolve to `tmp/phase9c-local-operator-registry` or below.

## 24. Runtime safety model

Standard library only; no network, database, subprocess, shell execution, key
generation, vault access, wrapper call, primitive call, or Phase 8 runtime call;
no mutation outside the tmp output directory.

## 25. Non-authentication boundary

A registry record is not login, not authenticated identity, not a session, and
not a user account. Future authentication requires a separate phase.

## 26. Non-RBAC boundary

Registry role labels are governance metadata only; role label is not runtime
permission; the registry enforces no permissions. Future RBAC requires a separate
phase.

## 27. Non-approval boundary

Local operator registry is not authentication and not approval; registry presence
is not approval; valid actor metadata is not approval; the registry report is
evidence only and must not trigger the wrapper, execute primitives, trigger the
next gate, or set approval flags. Approval remains the Phase 7D selected-gate
manual boundary.

## 28. Compatibility with Phase 9B

Phase 9C implements a local validation subset of the Phase 9B conceptual actor
metadata schema and does not change the Phase 9B schema contract.

## 29. Compatibility with Phase 9A

Phase 9C follows the Phase 9A identity boundary; operator identity remains
unauthenticated or operator-declared.

## 30. Compatibility with Phase 8O/8L/8M

Phase 9C may provide future actor metadata for Phase 8 final acceptance, signing,
or verifier attribution; it does not modify Phase 8 runtime. Signature
verification remains not approval; final acceptance remains not approval.

## 31. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; Phase 9C does not
modify Phase 7D; registry records must not approve and must not execute
primitives.

## 32. Failure taxonomy

`input_missing`, `invalid_json`, `invalid_input_shape`,
`actor_schema_version_missing`, `actor_id_missing`, `actor_id_invalid_format`,
`actor_type_missing`, `actor_type_unknown`, `actor_identity_assurance_missing`,
`actor_identity_assurance_insufficient`, `actor_identity_source_unknown`,
`actor_role_label_unknown`, `actor_scope_invalid`,
`actor_session_reference_invalid`, `identity_evidence_reference_invalid`,
`identity_metadata_contains_secret`, `identity_metadata_contains_unnecessary_pii`,
`approval_boundary_statement_missing`, `approval_flag_present`,
`primitive_execution_intent_present`, `duplicate_actor_id`, `unsafe_path`. Each
maps to a severity (`info`, `warning`, `critical`), an incident classification
(`none`, `actor_metadata_not_available`, `actor_metadata_schema_failure`,
`identity_assurance_review_required`, `identity_policy_review_required`,
`privacy_review_required`, `actor_scope_review_required`), and a reviewer action
(`no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`).

## 33. Reviewer action mapping

`no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`. Reviewer action is guidance only, is not
approval, and must not trigger the wrapper, execute primitives, or trigger the
next gate.

## 34. Non-goals

Phase 9C does not implement authentication, RBAC, login, sessions, user store,
OAuth/OIDC/SAML runtime, backend/API/database, key custody, production signing,
or production verifier; does not modify the Phase 7D wrapper or Phase 8 runtime;
executes no primitives; writes no vault; approves nothing; triggers no next gate;
adds no chain execution; and creates no production deployment.

## 35. Test strategy

`tests/test_phase9c_local_operator_registry_prototype.py` verifies file existence
and status, scope safety, runtime static safety, build/validate/list/report
behavior, input/enum/field/actor_id/privacy/approval validation, duplicate
handling, report schema, path safety, documentation regressions, protected
runtime file integrity, static safety on new Phase 9C files, and repo-wide
artifact safety.

## 36. Acceptance criteria

- prototype, runner, task, doc, and tests exist
- runner is mode 100755
- build mode produces a valid registry and report, exit 0
- validate mode writes a validation report without a registry file, exit 0
- list/report modes read the registry and write reports
- invalid/enum/field/actor_id/privacy/approval failures reject and exit nonzero
- duplicate handling produces a warning and exit 0
- ROADMAP, PROJECT_STATE, PHASE9B, PHASE9A, and PHASE8O reference Phase 9C
- protected runtime files remain unchanged
- local operator registry remains not authentication and not approval
- approval remains Phase 7D selected-gate manual boundary

## 37. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase9b_actor_metadata_schema_design.py
python -m pytest -q tests/test_phase9a_operator_identity_boundary_design.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m py_compile scripts/dev/manage_phase9c_local_operator_registry.py
bash -n scripts/dev/run_phase9c_local_operator_registry.sh
chmod 755 scripts/dev/run_phase9c_local_operator_registry.sh
test "$(stat -c '%a' scripts/dev/run_phase9c_local_operator_registry.sh)" = "755"
git ls-files -s scripts/dev/run_phase9c_local_operator_registry.sh | grep "^100755 "
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## 38. Known limitations

- local prototype only
- no authentication, no RBAC, no login, no session runtime, no user store, no
  backend/API/database, no key custody, no strong non-repudiation, no production
  deployment

## 39. Final status target

phase9c_status: success
