# Task 053 — Phase 8B Local Append-only Audit Store Prototype

phase8b_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: local_append_only_prototype

## Purpose

Implement the first runtime durable-audit prototype from
`docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`: a local, ingest-only,
append-only JSONL audit store. Phase 8B reads one existing audit artifact
and appends one normalized, hash-chained durable audit record to a local
gitignored JSONL store. It changes no Phase 7D wrapper behavior and executes
no approval primitive.

## Scope

Phase 8B is ingest-only. It reads exactly one existing audit artifact and
appends a normalized record to a local ignored JSONL store. It changes no
Phase 7D wrapper behavior, changes no approval logic, executes no primitive,
performs no vault read/write, connects to no backend/API/database/S3/
DynamoDB/SQLite/external service, adds no new mutation path, adds no
next-gate automation, and adds no chain execution.

## Files

- `codex/tasks/053-phase8b-local-append-only-audit-store.md`
- `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`
- `scripts/dev/ingest_phase8b_audit_record.py`
- `scripts/dev/run_phase8b_audit_ingest.sh`
- `tests/test_phase8b_local_append_only_audit_store.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`
- additive updates to `docs/PHASE7H_OPERATOR_RUNBOOK.md`
- additive update to `.gitignore` (`tmp/phase8b-audit-store/`)

## Status model

- `success`: the ingest script and shell runner exist, ingest is read-only
  over the source artifact and append-only over the JSONL store, hash-chain
  integrity holds, path-safety rejections behave as specified, additive
  documentation pointers exist, protected runtime files stay unchanged, and
  `phase7d_runtime_readiness` remains `implemented_manual_gate`.
- `failed`: ingest mutates the source artifact, writes outside
  `tmp/phase8b-audit-store/`, accepts an unsafe input/store path, breaks the
  hash chain, or a protected runtime surface changes.

## Local append-only objective

Provide a deterministic, local, append-only JSONL audit record store that an
operator can populate by ingesting existing Phase 7D-compatible audit
artifacts, without implementing a database, backend, or network-facing
service.

## Ingest-only boundary

- Phase 8B only reads a caller-provided audit artifact path and appends to
  the local JSONL store.
- Phase 8B never calls the Phase 7D wrapper.
- Phase 8B never executes an approval primitive.
- Phase 8B never runs the Phase 7B verifier automatically.
- Phase 8B never writes the vault.
- Phase 8B never mutates the source audit artifact.

## Input audit artifact contract

- must be an existing JSON object (not an array, not a scalar)
- accepted with flexible/best-effort keys; Phase 7D-compatible artifacts are
  supported but perfect shape is not required
- extracted fields (best-effort, `null` if absent): `product_id`,
  `report_week`, `selected_gate`, `operator`, `approval_reason`,
  `approval_intent` (also accepts `gate_specific_approval_intent`),
  `execution_mode`, `emergency_stop_state`, `mutation_attempted`,
  `primitive_name`, `primitive_outcome` (also accepts `outcome`),
  `precondition_summary`, `result_summary`, `wrapper_version`,
  `audit_schema_version`, `created_at` (also accepts `timestamp`),
  `completed_at`
- ingest must not fail because an optional field is absent
- ingest must fail if the file is not a valid JSON object

## Path safety model

Input path rules:

- path must exist and be a file
- path must resolve under the repository root
- path must not resolve under `vault/`, `docs/`, `scripts/`, `tests/`, or
  `codex/`
- path should normally be under `tmp/`
- symlinks are rejected
- path traversal is rejected
- absolute paths outside the repository are rejected
- hidden path segments are rejected unless the path is under `tmp/`

Store path rules:

- default store dir: `tmp/phase8b-audit-store`
- the store dir must resolve under `tmp/phase8b-audit-store` only
- the store dir is created if missing
- a custom store dir outside `tmp/phase8b-audit-store` is rejected

## Record normalization model

The normalized record carries every field listed in
`docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md` under "Record model".
Extraction uses flexible aliases so Phase 7D-compatible artifacts (using
`outcome`, `timestamp`, `gate_specific_approval_intent`,
`source_packet_path`, `verifier_path`, `execution_plan_path`) normalize
correctly alongside artifacts that already use the Phase 8A field names.

## Hash-chain model

- `artifact_hash` = sha256 of the source artifact's raw bytes.
- `previous_record_hash` = `record_hash` of the last valid JSONL line, or
  `null` if the store is empty.
- `record_hash` = sha256 of canonical JSON (`sort_keys=True`,
  `separators=(",", ":")`, `ensure_ascii=False`) of the record with
  `record_hash` and `audit_record_id` both excluded.
- `audit_record_id` = `"audit-"` + first 16 hex characters of `record_hash`.
- one JSON object is appended per line; no existing line is ever edited.
- a same-`artifact_hash` re-ingest is a no-op (`duplicate_skipped`), not a
  second append.

## Store layout

- `tmp/phase8b-audit-store/audit-records.jsonl`
- `tmp/phase8b-audit-store/audit-ingest-summary.json`
- `tmp/phase8b-audit-store/audit-ingest-summary.md`

## Summary artifact model

The JSON summary carries: `phase8b_status`, `durable_audit_store_status`,
`phase7d_runtime_readiness`, `ingest_status`, `audit_record_id`,
`source_audit_artifact_ref`, `store_path`, `summary_path`, `artifact_hash`,
`previous_record_hash`, `record_hash`, `duplicate`, `appended`,
`safety_statement`, `limitations`. The Markdown summary carries the same
information in human-readable form.

## Failure behavior

Ingest exits non-zero and appends nothing on: missing/non-file/symlinked/
traversal/outside-repo/rejected-root input paths, invalid JSON or a non-object
JSON body, a rejected custom store dir, and a corrupted/malformed existing
JSONL line (hash-chain read failure). Duplicate detection and a normal append
both exit `0`.

## Non-goals

- no database, no SQLite implementation, no S3 implementation, no DynamoDB
  implementation
- no backend, no FastAPI, no API routes
- no external APIs, no external URLs, no network behavior
- no new runtime mutation path
- no primitive execution
- no vault read/write
- no Phase 7D wrapper behavior change
- no approve-all, no global approval, no multi-gate execution
- no next-gate automation, no chain execution
- no affiliate content generation, no autopublish, no campaign launch
- no marketplace connector, no production deployment

## Phase 7D wrapper boundary

Phase 8B does not modify, wrap, call, or execute
`scripts/dev/run_phase7d_single_gate_wrapper.sh` or
`scripts/dev/execute_single_gate_approval.py`. It only reads an audit
artifact that such a wrapper run may have produced.
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

## Phase 7B verifier compatibility

Phase 8B does not modify or call
`scripts/dev/run_phase7b_audit_verifier.sh` or
`scripts/dev/verify_manual_approval_audit.py`. It may ingest a
`phase7b_verifier_ref` value if the source artifact carries one, but never
runs the verifier itself and never infers approval or validity from
ingestion.

## Operator runbook integration

`docs/PHASE7H_OPERATOR_RUNBOOK.md` gets an additive pointer stating Phase 8B
provides post-audit manual ingestion only and does not change the execution
ceremony or approval boundary defined in Phase 7H.

## Test strategy

Deterministic tests: file/status existence; scope/safety token coverage in
the design doc; static safety of the ingest script and shell runner (no
subprocess/sqlite3/boto3/requests/httpx/urllib imports, no FastAPI, no
primitive calls, no vault writes, no `--execute`, no approval flags set
truthy, no wrapper/primitive/verifier calls); executable-mode and
`bash -n`/`py_compile` checks; ingest behavior (first record, required
fields, hash correctness, summary artifacts, source-artifact immutability);
hash-chain behavior across two records; duplicate-skip behavior; path-safety
rejections (missing file, directory, invalid JSON, JSON array, vault/docs/
scripts/tests/codex sources, symlink, out-of-bounds store dir); documentation
regression; protected runtime file hash regression; and a static-safety scan
over only the new Phase 8B task/doc/script files.

## Acceptance criteria

- ingest script and shell runner exist and are executable/well-formed
- ingest is read-only over the source artifact and append-only over the
  JSONL store
- hash-chain fields are correct and self-verifiable
- duplicate ingestion is a no-op
- unsafe input/store paths are rejected with a non-zero exit
- design doc contains `phase8b_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`, and
  `durable_audit_store_status: local_append_only_prototype`
- ROADMAP, PROJECT_STATE, the Phase 8A design doc, and the Phase 7H runbook
  all reference Phase 8B additively
- protected Phase 6B/6C/6E/7B/7D/7G runtime files remain unchanged
- no backend/API/database file is added
- all runtime writes are confined to `tmp/phase8b-audit-store/`

## Verification commands

```text
source .venv/bin/activate

python -m pytest -q tests/test_phase8b_local_append_only_audit_store.py
python -m pytest -q tests/test_phase8a_durable_audit_store_design.py
python -m pytest -q tests/test_phase7h_operator_runbook_hardening.py
python -m pytest -q tests/test_phase7g_operator_acceptance_demo_pack.py
python -m pytest -q tests/test_phase7f_runtime_wrapper_live_snapshot.py
python -m pytest -q tests/test_phase7d_single_gate_wrapper.py
python -m pytest -q tests/test_phase7e_release_snapshot_runtime_blocked.py
python -m pytest -q tests/test_phase7d_implementation_plan_finalization.py
python -m pytest -q tests/test_phase7d_r_high_risk_readiness_review.py
python -m pytest -q tests/test_phase7c_single_gate_wrapper_implementation_plan.py
python -m pytest -q tests/test_phase7b_audit_verifier.py
python -m pytest -q tests/test_phase7a_audit_verifier_implementation_plan.py
python -m pytest -q tests/test_phase6h_release_snapshot.py tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py

python -m py_compile scripts/dev/ingest_phase8b_audit_record.py
bash -n scripts/dev/run_phase8b_audit_ingest.sh

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8B is a local tmp prototype only: JSONL only, no SQLite index, no S3/
DynamoDB backend, no backend/API, no authenticated operator identity, no
production deployment, no automatic migration, no retention enforcement, and
no query/reporting command yet.

## Final status target

phase8b_status: success
