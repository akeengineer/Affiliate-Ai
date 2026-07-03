# Task 070 — Phase 9D Actor Attribution in Audit/Reports

phase9d_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: phase8_final_acceptance_pack

identity_boundary_status: design_only

actor_metadata_schema_status: design_only

actor_metadata_runtime_status: local_registry_prototype

local_operator_registry_status: prototype_local_only

actor_attribution_status: local_report_prototype

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

Phase 9D adds a local-only actor attribution report prototype that consumes
Phase 9C local operator registry output and annotates local audit/report
evidence with actor attribution metadata — all metadata-only and evidence-only.

## 2. Scope

- local-only actor attribution report prototype (standard library only)
- reads an existing Phase 9C `operator-registry.json`
- reads a local evidence/report reference file
- attaches selected actor metadata to each evidence reference
- deterministic actor-attributed report JSON and Markdown
- privacy/secret scan and approval boundary enforcement
- outputs only under `tmp/phase9d-actor-attribution/`
- no authentication, RBAC, login, sessions, user store
- no backend/API/database, no network, no database drivers
- no key management runtime, no key/cert files
- no Phase 9C registry change, no Phase 8 runtime change, no Phase 7D change
- no primitive execution, no vault read/write

## 3. Files

- `scripts/dev/build_phase9d_actor_attribution_report.py`
- `scripts/dev/run_phase9d_actor_attribution_report.sh`
- `tests/test_phase9d_actor_attribution_report_prototype.py`
- `codex/tasks/070-phase9d-actor-attribution-in-audit-reports.md`
- `docs/PHASE9D_ACTOR_ATTRIBUTION_IN_AUDIT_REPORTS.md`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE9C_LOCAL_OPERATOR_REGISTRY_PROTOTYPE.md`
- additive updates to `docs/PHASE9B_ACTOR_METADATA_SCHEMA_DESIGN.md`
- additive updates to `docs/PHASE9A_OPERATOR_IDENTITY_BOUNDARY_DESIGN.md`
- additive updates to `docs/PHASE8O_FINAL_ACCEPTANCE_PACK.md`
- `.gitignore` (add Phase 9D tmp roots)

## 4. Status model

- `phase9d_status: success` — the prototype, runner, task, doc, and tests exist.
- `phase7d_runtime_readiness: implemented_manual_gate` — approval remains the
  Phase 7D selected-gate manual boundary.
- `durable_audit_store_status: phase8_final_acceptance_pack` — unchanged.
- `identity_boundary_status: design_only` — unchanged.
- `actor_metadata_schema_status: design_only` — unchanged.
- `actor_metadata_runtime_status: local_registry_prototype` — Phase 9C registry
  prototype remains.
- `local_operator_registry_status: prototype_local_only` — unchanged.
- `actor_attribution_status: local_report_prototype` — a local attribution
  report prototype now exists.
- `identity_runtime_status: not_implemented` — no identity runtime.
- `rbac_runtime_status: not_implemented` — no RBAC runtime.
- `authentication_runtime_status: not_implemented` — no authentication runtime.
- `operator_identity_assurance_status: unauthenticated_or_operator_declared` —
  unchanged.
- `signing_implementation_status: prototype_local_only` — unchanged.
- `signature_runtime_status: local_prototype` — unchanged.
- `signature_verifier_runtime_status: local_prototype` — unchanged.
- `key_management_runtime_status: not_implemented` — unchanged.
- `phase9_branch_workflow: enabled` — Phase 9D continues the Phase 9 branch.

## 5. Actor attribution objective

Provide a local, deterministic, evidence-only report that joins Phase 9C actor
metadata to local audit/report evidence references for attribution, never
becoming authentication or approval.

## 6. Current trust boundary after Phase 9C

Phase 9A defines the identity boundary; Phase 9B defines the schema; Phase 9C
adds a local registry prototype; Phase 9D adds a local attribution report
prototype only. No identity, authentication, RBAC, session, user store, or key
management runtime exists. Operator identity remains unauthenticated or
operator-declared.

## 7. Actor attribution data model

Attributed records join each evidence reference (`evidence_id`, `evidence_type`,
`evidence_path`, `evidence_phase`, `evidence_purpose`) with the selected actor
(`actor_metadata`, `actor_id`, `actor_type`, `actor_identity_assurance`,
`actor_identity_source`, `actor_role_labels`), plus `attribution_status` and
`approval_boundary_statement`.

## 8. Attribution input contract

Registry is a JSON object with actor records under `actor_metadata`,
`actor_registry`, `records`, `registry_records`, or `operators`. Evidence is a
JSON object (with `evidence_references`/`reports`/`audit_records`/`artifacts`) or
a JSON array. Missing/invalid/empty inputs exit nonzero.

## 9. Attribution output contract

Deterministic JSON (`sort_keys=True`, `indent=2`) and Markdown reports carrying
the required status fields, counts, severity counts, reviewer action, incident
classification, approval boundary statement, safety statement, limitations,
issues, and attributed records.

## 10. Attribution command model

`--registry` (default `tmp/phase9c-local-operator-registry/operator-registry.json`),
`--evidence` (required), `--actor-id` (optional), `--output-dir` (default
`tmp/phase9d-actor-attribution`). No approval flags and no `--execute`.

## 11. Registry compatibility model

The registry reader accepts the Phase 9C `actor_registry` container plus
`actor_metadata`, `records`, `registry_records`, and `operators` for
compatibility. Each actor record should include `actor_id`, `actor_type`,
`actor_display_label`, `actor_role_labels`, `actor_identity_assurance`,
`actor_identity_source`, `actor_action_scope`, `privacy_classification`, and
`approval_boundary_statement`.

## 12. Report/evidence reference model

Each evidence reference must include `evidence_id`, `evidence_type`,
`evidence_path`, `evidence_phase`, and `evidence_purpose`; a missing field is
`evidence_reference_missing_field`.

## 13. Attribution binding model

For each evidence reference an attributed record binds the evidence fields to the
selected actor metadata and restates the approval boundary statement.

## 14. Actor selection model

Explicit `--actor-id` selects the matching actor; without it, the first actor by
`actor_id` sort order is selected deterministically.

## 15. Missing actor behavior

If the registry contains no actor records, exit nonzero with
`registry_actor_missing`.

## 16. Unknown actor behavior

If `--actor-id` does not match any registry actor, exit nonzero with
`actor_not_found`, `actor_attribution_status: failed_actor_not_found`, and
`attribution_report_status: not_built`.

## 17. Duplicate actor behavior

Duplicate `actor_id` records do not crash; the first deterministic record is
selected, a warning issue is emitted, `duplicate_actor_count` increments, and the
report status is `built_with_warnings` with `manual_review_required`.

## 18. Privacy and secret scan model

Registry and evidence string fields are scanned for secret-like markers
(private-key headers, `API_KEY=`, `SECRET=`, `TOKEN=`, `PASSWORD=`,
`AWS_SECRET_ACCESS_KEY`, `ssh-rsa`, OAuth `access_token`/`id_token`/
`refresh_token`, raw `AFFILIATE_PHASE8L_PROTOTYPE_KEY`) and external URL schemes;
raw emails are flagged as unnecessary PII. Matches are critical/reject.

## 19. Approval boundary enforcement model

The selected actor's `approval_boundary_statement` must include an approval
boundary phrase; approval flag fields (`approved`, `is_approved`,
`approval_granted`, `auto_approve`, `approve_all`, `next_gate`, `execute`) and
primitive-execution-intent fields must not be truthy in the actor or evidence.

## 20. Deterministic output model

JSON is written with `sort_keys=True` and `indent=2`; no wall-clock timestamp is
generated, so outputs are reproducible.

## 21. Path safety model

Registry and evidence paths must resolve under the repo root, must not be under
`vault/`/`docs/`/`scripts/`/`codex/`/`.git/`, and must not be symlinks; the
output directory must resolve to `tmp/phase9d-actor-attribution` or below.

## 22. Runtime safety model

Standard library only; no network, database, subprocess, shell execution, key
generation, vault access, wrapper call, primitive call, or Phase 8 runtime call;
no mutation outside the tmp output directory.

## 23. Non-authentication boundary

Attribution is not login, not authenticated identity, not a session, and not a
user account. Future authentication requires a separate phase.

## 24. Non-RBAC boundary

Attribution role labels are governance metadata only; role label is not runtime
permission; attribution enforces no permissions. Future RBAC requires a separate
phase.

## 25. Non-approval boundary

Actor attribution is not authentication and not approval; registry presence is
not approval; valid actor metadata is not approval; the attributed report is
evidence only and must not trigger the wrapper, execute primitives, trigger the
next gate, or set approval flags. Approval remains the Phase 7D selected-gate
manual boundary.

## 26. Compatibility with Phase 9C

Phase 9D consumes Phase 9C registry output and does not modify Phase 9C runtime.

## 27. Compatibility with Phase 9B

Phase 9D uses the Phase 9B conceptual actor metadata schema fields; schema
validity remains not approval.

## 28. Compatibility with Phase 9A

Phase 9D follows the Phase 9A identity boundary; operator identity remains
unauthenticated or operator-declared.

## 29. Compatibility with Phase 8O/8L/8M

Phase 9D can attribute local evidence/report references from final acceptance,
signing, or verifier outputs; it does not modify Phase 8 runtime. Signature
verification remains not approval; final acceptance remains not approval.

## 30. Compatibility with Phase 7D

Phase 7D remains the selected-gate manual approval runtime; Phase 9D does not
modify Phase 7D; attribution records must not approve and must not execute
primitives.

## 31. Failure taxonomy

`registry_missing`, `evidence_missing`, `invalid_registry_json`,
`invalid_evidence_json`, `invalid_registry_shape`, `invalid_evidence_shape`,
`registry_actor_missing`, `actor_not_found`, `duplicate_actor_id`,
`evidence_reference_missing_field`, `actor_metadata_contains_secret`,
`evidence_metadata_contains_secret`, `actor_metadata_contains_unnecessary_pii`,
`approval_boundary_statement_missing`, `approval_flag_present`,
`primitive_execution_intent_present`, `unsafe_path`. Each maps to a severity
(`info`, `warning`, `critical`), an incident classification (`none`,
`actor_attribution_not_available`, `actor_metadata_schema_failure`,
`identity_assurance_review_required`, `identity_policy_review_required`,
`privacy_review_required`, `actor_scope_review_required`,
`evidence_reference_failure`), and a reviewer action (`no_action_required`,
`manual_review_required`, `reject_actor_metadata_until_resolved`,
`reject_attribution_until_resolved`).

## 32. Reviewer action mapping

`no_action_required`, `manual_review_required`,
`reject_actor_metadata_until_resolved`, `reject_attribution_until_resolved`.
Reviewer action is guidance only, is not approval, and must not trigger the
wrapper, execute primitives, or trigger the next gate.

## 33. Non-goals

Phase 9D does not implement authentication, RBAC, login, sessions, user store,
OAuth/OIDC/SAML runtime, backend/API/database, key custody, production signing,
or production verifier; does not modify Phase 9C registry runtime, Phase 8
runtime, or the Phase 7D wrapper; executes no primitives; writes no vault;
approves nothing; triggers no next gate; adds no chain execution; and creates no
production deployment.

## 34. Test strategy

`tests/test_phase9d_actor_attribution_report_prototype.py` verifies file
existence and status, scope safety, runtime static safety, valid attribution
behavior, deterministic actor selection, duplicate handling, missing/invalid
registry and evidence behavior, actor-not-found behavior, privacy/approval
validation, report schema, path safety, documentation regressions, protected
runtime file integrity, static safety on new Phase 9D files, and repo-wide
artifact safety.

## 35. Acceptance criteria

- prototype, runner, task, doc, and tests exist
- runner is mode 100755
- valid attribution builds a report and exits 0
- deterministic first-actor selection when `--actor-id` is omitted
- duplicate handling produces a warning and exits 0
- missing/invalid registry or evidence and actor-not-found exit nonzero
- privacy/secret and approval failures reject and exit nonzero
- ROADMAP, PROJECT_STATE, PHASE9C, PHASE9B, PHASE9A, and PHASE8O reference
  Phase 9D
- protected runtime files remain unchanged
- actor attribution remains not authentication and not approval
- approval remains Phase 7D selected-gate manual boundary

## 36. Focused verification commands

```text
source .venv/bin/activate
umask 022
python -m pytest -q tests/test_phase9d_actor_attribution_report_prototype.py
python -m pytest -q tests/test_phase9c_local_operator_registry_prototype.py
python -m pytest -q tests/test_phase9b_actor_metadata_schema_design.py
python -m pytest -q tests/test_phase9a_operator_identity_boundary_design.py
python -m pytest -q tests/test_phase8o_final_acceptance_pack.py
python -m pytest -q tests/test_phase8m_detached_signature_verifier_prototype.py
python -m pytest -q tests/test_phase8l_local_detached_signature_prototype.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m py_compile scripts/dev/build_phase9d_actor_attribution_report.py
bash -n scripts/dev/run_phase9d_actor_attribution_report.sh
chmod 755 scripts/dev/run_phase9d_actor_attribution_report.sh
test "$(stat -c '%a' scripts/dev/run_phase9d_actor_attribution_report.sh)" = "755"
git ls-files -s scripts/dev/run_phase9d_actor_attribution_report.sh | grep "^100755 "
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## 37. Known limitations

- local prototype only
- no authentication, no RBAC, no login, no session runtime, no user store, no
  backend/API/database, no key custody, no strong non-repudiation, no production
  deployment

## 38. Final status target

phase9d_status: success
