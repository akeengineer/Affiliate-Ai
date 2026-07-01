# Manual Approval Audit Verifier Implementation Plan (Phase 7A)

## Purpose

Phase 7A plans a future runtime **read-only** verifier that validates one manual
approval audit artifact produced by a future single-gate manual approval
wrapper. Phase 7A consumes the Phase 6G boundary contract from
[`MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md`](MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md)
as its source of truth and adds no new rules. Phase 7A remains
docs/tests/task-only: it plans the verifier but implements no runtime verifier
and executes nothing.

## Scope

- implementation plan only
- docs/tests/task-only
- no runtime verifier
- no runtime command
- no approval wrapper implementation
- no vault read/write
- no primitive execution
- no approval mutation
- no chain execution
- no global approve

Primitive file names, approval flag names, and future verifier command names are
referenced as names only; this document contains no command forms for approval
primitives and no approval flag assignments.

## Implementation objective

The future verifier must:

- read one audit artifact
- validate schema fields
- validate gate consistency
- validate primitive and flag mapping
- validate `mutation_attempted` consistency
- validate referenced artifact paths
- detect unsafe content
- produce verifier output under `tmp/`
- return `valid`, `warning`, or `invalid`
- never execute primitives
- never mutate vault
- never approve, promote, decide, or finalize

## Future runtime command shape

The future verifier command names are defined as **proposed future names only**.
The proposed future shapes are:

```text
bash scripts/dev/run_phase7b_audit_verifier.sh <audit_artifact_path>
```

```text
python -m scripts.dev.verify_manual_approval_audit <audit_artifact_path>
```

- these are proposed future names only
- no runtime command exists in Phase 7A
- Phase 7A must not add these files
- no approval primitive command forms are included
- the future verifier must accept exactly one audit artifact path

## Audit input contract

The future verifier input must be:

- one JSON audit artifact
- a path that is a relative `tmp/` path
- no absolute path
- no traversal
- no vault path
- no external URL
- no operator-local path
- a read-only input file
- the verifier must not modify the input

Required audit fields:

- `product_id`
- `report_week`
- `selected_gate`
- `primitive_name`
- `operator`
- `approval_reason`
- `timestamp`
- `source_packet_path`
- `verifier_path`
- `execution_plan_path`
- `precondition_summary`
- `result_summary`
- `outcome`
- `mutation_attempted`
- `gate_specific_approval_intent`
- `approved_flag_name`
- `wrapper_version`
- `audit_schema_version`

## Validation rules

The future verifier must validate:

- `selected_gate` is one of `promote`, `decision`, `finalization`
- `primitive_name` matches the selected gate:
  - promote -> `promote_product_candidates.py`
  - decision -> `create_decision.py`
  - finalization -> `finalize_decision.py`
- `approved_flag_name` matches the selected gate:
  - promote -> `APPROVE_PROMOTE`
  - decision -> `APPROVE_DECISION`
  - finalization -> `APPROVE_FINALIZE`
- only one gate is represented
- no multi-gate list
- no global approval
- no approve-all
- no automatic next-gate
- no chain execution
- no hidden promotion
- no UI-direct approval
- `outcome` is one of `success`, `failure`, `blocked`, `prevented`
- `blocked` or `prevented` means `mutation_attempted` is false
- `success` or `failure` means `mutation_attempted` must be explicit
- `source_packet_path` references a Phase 6B packet under `tmp/`
- `verifier_path` references a Phase 6C verifier output under `tmp/`
- `execution_plan_path` references a Phase 6E execution plan under `tmp/`
- referenced paths are relative `tmp/` paths
- referenced paths are not absolute
- referenced paths contain no traversal
- referenced paths contain no vault path
- the audit contains no approval command forms
- the audit contains no external URLs
- the audit contains no secret markers
- the audit contains no operator-local paths

## Output contract

The future verifier output must be written under:

```text
tmp/phase7b-audit-verifier/
```

Planned output files:

- a JSON verifier report
- a Markdown verifier report

Planned JSON fields:

- `type`
- `generated_at`
- `source_audit_path`
- `source_audit_sha256`
- `source_audit_bytes`
- `product_id`
- `report_week`
- `selected_gate`
- `required_fields`
- `gate_consistency`
- `path_safety`
- `mutation_consistency`
- `forbidden_content`
- `referenced_artifacts`
- `warnings`
- `failures`
- `verdict`
- `statement`

Verdict:

- `valid`
- `warning`
- `invalid`

Exit policy for the future implementation:

- `valid` exits 0
- `warning` exits 0
- `invalid` exits non-zero

## Failure and safety behavior

The future verifier must:

- fail closed on missing input
- fail closed on invalid JSON
- fail closed on missing required field
- fail closed on unsafe path
- fail closed on command form
- fail closed on leakage
- never execute primitives
- never mutate vault
- never rewrite audit artifact
- never trigger wrapper
- never infer approval
- never normalize unsafe content into safe content
- always report evidence

## Future Phase 7B test plan

Phase 7B must ship deterministic tests, using tmp-only fixtures:

- valid promote audit -> `valid`
- valid decision audit -> `valid`
- valid finalization audit -> `valid`
- missing required field -> `invalid`
- wrong primitive for selected gate -> `invalid`
- wrong approved flag for selected gate -> `invalid`
- blocked with `mutation_attempted` true -> `invalid`
- prevented with `mutation_attempted` true -> `invalid`
- success with missing `mutation_attempted` -> `invalid`
- unsafe absolute path -> `invalid`
- traversal path -> `invalid`
- vault path -> `invalid`
- external URL -> `invalid`
- secret marker -> `invalid`
- approval command form -> `invalid`
- multi-gate evidence -> `invalid`
- global approval evidence -> `invalid`
- stale referenced artifact hash -> `warning`
- optional metadata warning path -> `warning`
- cross-CWD execution
- output self-safety
- no vault write
- no primitive execution

## Documentation update scope

Phase 7A updates docs additively only:

- [`ROADMAP.md`](ROADMAP.md)
- [`PROJECT_STATE.md`](PROJECT_STATE.md)
- [`RELEASE_SNAPSHOT_PHASE6.md`](RELEASE_SNAPSHOT_PHASE6.md)

- ROADMAP marks Phase 7A as the implementation plan and Phase 7B as the future
  implementation.
- PROJECT_STATE points to this plan.
- RELEASE_SNAPSHOT_PHASE6 may include a future pointer only.
- No Phase 6 release matrix rewrite occurs.

## Phase 7B implementation status

Phase 7B implements this plan as a runtime **read-only** audit verifier:

- `scripts/dev/verify_manual_approval_audit.py` — the verifier core
- `scripts/dev/run_phase7b_audit_verifier.sh` — the guardrail wrapper

The Phase 7A plan above is retained as historical intent. Phase 7B remains
read-only and evidence-only: it reads one audit artifact, writes reports only
under `tmp/phase7b-audit-verifier/`, and never reads/writes the vault, executes
an approval primitive, mutates the input, or uses an approval flag. A future
single-gate manual approval wrapper (which would produce real audit artifacts)
remains a separate, explicitly approved phase.

## Known limitations

- No wrapper implementation yet (no real audit artifact exists until one does).
- No auth/operator identity implementation.
- No backend/API/database.
- No marketplace connector.
- No autopublish.
- No production deployment.
