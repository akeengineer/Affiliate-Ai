# Task 043 - Phase 7B Manual Approval Audit Verifier

## 1. Purpose

Implement a runtime read-only audit verifier that validates one JSON manual
approval audit artifact that a future single-gate manual approval wrapper would
produce. Phase 7B implements the Phase 7A plan against the Phase 6G contract and
remains read-only: it never reads or writes the vault, never executes an
approval primitive, never mutates the input, and never uses an approval flag.

## 2. Runtime scope

- runtime read-only verifier only
- reads exactly one audit artifact (the verification target)
- writes report/summary only under `tmp/phase7b-audit-verifier/`
- no approval wrapper, no approval mutation, no primitive execution
- no vault read/write, no network, no backend/API/database

## 3. Files

- `scripts/dev/verify_manual_approval_audit.py`
- `scripts/dev/run_phase7b_audit_verifier.sh`
- `tests/test_phase7b_audit_verifier.py`
- `codex/tasks/043-phase7b-audit-verifier.md`
- `.gitignore` (additive: `tmp/phase7b-audit-verifier/`)
- `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md` (additive)
- `docs/PROJECT_STATE.md` (additive)
- `docs/ROADMAP.md` (additive)

## 4. Input contract

One JSON audit artifact at a relative `tmp/` path (interpreted relative to repo
root). Absolute paths, traversal, vault paths, external URLs, and operator-local
paths are rejected before reading. The input is opened read-only and never
mutated or rewritten. Invalid JSON yields `invalid` and a non-zero exit. The 18
required fields are: `product_id`, `report_week`, `selected_gate`,
`primitive_name`, `operator`, `approval_reason`, `timestamp`,
`source_packet_path`, `verifier_path`, `execution_plan_path`,
`precondition_summary`, `result_summary`, `outcome`, `mutation_attempted`,
`gate_specific_approval_intent`, `approved_flag_name`, `wrapper_version`,
`audit_schema_version`.

## 5. Validation rules

- `selected_gate` in {promote, decision, finalization}
- `primitive_name` matches the gate: promote -> `promote_product_candidates.py`,
  decision -> `create_decision.py`, finalization -> `finalize_decision.py`
- `approved_flag_name` matches the gate: `APPROVE_PROMOTE`, `APPROVE_DECISION`,
  `APPROVE_FINALIZE`
- single gate only; multi-gate / global approval evidence is invalid
- `outcome` in {success, failure, blocked, prevented}
- `blocked`/`prevented` require `mutation_attempted` false; `success`/`failure`
  require an explicit boolean; missing or non-boolean is invalid
- `source_packet_path` under `tmp/phase6b-approval-review/`, `verifier_path`
  under `tmp/phase6c-approval-review-verifier/`, `execution_plan_path` under
  `tmp/phase6e-approval-execution-plan/`; referenced paths must be relative
  `tmp/` paths (no absolute, traversal, vault, external URL, or operator-local)
- `product_id` matches `^[a-z0-9-]+$` and `report_week` matches `^\d{4}-W\d{2}$`
  before being used in an output filename; otherwise a deterministic safe
  fallback filename is used
- the raw audit body is scanned for forbidden content, reported by category
  label only (approval assignment, run command form, primitive command form,
  external URL, secret marker, operator-local path, vault path, traversal
  marker, multi-gate/global approval)

## 6. Output contract

Outputs are written only under `tmp/phase7b-audit-verifier/` via a fail-closed
guarded directory check. Safe-field outputs are
`audit-verification-<product_id>-<report_week>-<selected_gate>.{json,md}`;
unsafe-field outputs fall back to `audit-verification-invalid.{json,md}`. The
JSON fields are: `type`, `generated_at`, `source_audit_path`,
`source_audit_sha256`, `source_audit_bytes`, `product_id`, `report_week`,
`selected_gate`, `required_fields`, `gate_consistency`, `path_safety`,
`mutation_consistency`, `forbidden_content`, `referenced_artifacts`, `warnings`,
`failures`, `verdict`, `statement`. `failures` and `forbidden_content` carry
category labels and field names only, never raw dangerous substrings. Both
report bodies pass an output self-safety scan before writing; on failure a safe
category-only invalid report is written instead.

## 7. Verdict and exit policy

- `valid`: all required fields present, all hard checks pass, no unsafe paths, no
  forbidden content, referenced artifacts exist
- `warning`: hard checks pass but a safe expected-shape referenced artifact is
  missing or its freshness is unavailable, or optional metadata is stale
- `invalid`: missing required field, invalid JSON, unsafe input path, unsafe
  referenced path, forbidden content, wrong primitive mapping, wrong approval
  flag mapping, mutation inconsistency, multi-gate/global approval evidence, or
  unsafe filename field
- exit: `valid` -> 0, `warning` -> 0, `invalid` -> non-zero
- design decision: a missing or stale referenced artifact is `warning` only when
  the referenced path is safe and of the expected shape; an unsafe referenced
  path is always `invalid`

## 8. Wrapper behavior

`run_phase7b_audit_verifier.sh` uses `set -euo pipefail`, derives `SCRIPT_DIR`
and `REPO_ROOT` from its own location, `cd`s to `REPO_ROOT` (cross-CWD safe),
enforces exactly one positional argument, rejects `APPROVE_PROMOTE`,
`APPROVE_DECISION`, `APPROVE_FINALIZE`, `ENABLE_AUTOPUBLISH`, and
`ENABLE_OPENAI_API_DIRECT` when set to `true`, selects a Python interpreter
(`.venv/bin/python` -> `python3` -> `python`), and execs the verifier with the
audit artifact path. It never executes an approval primitive.

## 9. Guardrails

Read-only; output only under `tmp/phase7b-audit-verifier/`; input read-only and
never rewritten; no vault read/write; no approval mutation; no primitive
execution; no network/API/database/FastAPI/frontend/dependency; forbidden
content reported by category label only; dangerous literals composed at runtime
so the source carries no contiguous forbidden token (CI-C static guard stays
green); Phase 6B/6C/6E behavior and the Phase 2G/2H/2I primitives are unchanged.

## 10. Test strategy

Subprocess-driven runtime tests build synthetic audit artifacts under `tmp/`
(no real vault, no real wrapper, no primitive execution) and cover valid,
warning, and invalid paths, referenced-path safety, forbidden-content
categories, mutation consistency, wrapper env-flag rejection, cross-CWD
execution, output-under-tmp, output self-safety with category-only evidence,
no-vault-write, and no-primitive-execution, plus `py_compile`, `bash -n`, and a
`.gitignore` coverage check.

## 11. Verification commands

```
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
python -m py_compile scripts/dev/verify_manual_approval_audit.py
bash -n scripts/dev/run_phase7b_audit_verifier.sh
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 12. Known limitations

- No real audit artifact exists yet; a future single-gate wrapper implementation
  produces one and must be a separate, explicitly approved phase.
- No auth/operator identity implementation exists.
- Reference freshness is existence-based; no recorded reference hash exists in
  the current audit field set.

## 13. Final status target

`phase7b_status: success`
