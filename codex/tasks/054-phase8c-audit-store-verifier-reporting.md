# Task 054 — Phase 8C Audit Store Verifier / Reporting over JSONL

phase8c_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: jsonl_verifier_reporting

## Purpose

Implement a read-only verifier/reporting utility over the Phase 8B local
append-only JSONL audit store. Phase 8C recomputes per-record hashes,
validates hash-chain continuity, detects duplicates and malformed lines, and
produces reporting summaries grouped by product/week/gate/operator/outcome/
review status. It never appends to or mutates the source JSONL and changes no
Phase 7D wrapper or Phase 8B ingest behavior.

## Scope

Phase 8C is read-only against `audit-records.jsonl`. It never appends to or
modifies the store, changes no Phase 7D wrapper behavior, changes no Phase 8B
ingest behavior, executes no primitive, performs no vault read/write,
connects to no backend/API/database/S3/DynamoDB/SQLite/external service,
adds no new mutation path, adds no next-gate automation, and adds no chain
execution.

## Files

- `codex/tasks/054-phase8c-audit-store-verifier-reporting.md`
- `docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`
- `scripts/dev/verify_phase8c_audit_store.py`
- `scripts/dev/run_phase8c_audit_report.sh`
- `tests/test_phase8c_audit_store_verifier_reporting.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`
- additive updates to `docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`
- additive update to `.gitignore` (`tmp/phase8c-audit-report/`)

## Status model

- `success`: the verifier and shell runner exist, verification is read-only
  over the JSONL store, hash-chain/duplicate/malformed-line detection behaves
  as specified, report output is confined to `tmp/phase8c-audit-report/`,
  additive documentation pointers exist, protected runtime files (including
  the Phase 8B ingest script) stay unchanged, and
  `phase7d_runtime_readiness` remains `implemented_manual_gate`.
- `failed`: the verifier appends to or mutates the source JSONL, writes
  outside `tmp/phase8c-audit-report/`, accepts an unsafe store/report path,
  misses a genuine hash-chain break, or a protected runtime surface changes.

## Read-only verification objective

Provide a deterministic, read-only integrity check and reporting summary over
the Phase 8B JSONL audit store, without implementing a database, backend, or
query service, and without adding any new mutation path to the audit
pipeline.

## Input store contract

- default input: `tmp/phase8b-audit-store/audit-records.jsonl`
- a missing store path is not an error; it produces an empty report
  (`verification_status: empty`, `record_count: 0`, `issue_count: 0`,
  `hash_chain_valid: true`)
- an existing store path must be a file
- the store is opened read-only and never written to

## Path safety model

Store-path rules:

- must resolve under the repository root
- must not resolve under `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/`
- should normally be under `tmp/phase8b-audit-store/`
- symlinks are rejected
- path traversal is rejected
- absolute paths outside the repository are rejected
- a store-path safety violation (not a merely-missing file) produces an
  `invalid` report and a non-zero exit

Report-dir rules:

- default: `tmp/phase8c-audit-report`
- must resolve under `tmp/phase8c-audit-report` only
- created if missing
- a custom report dir outside `tmp/phase8c-audit-report` is rejected with a
  non-zero exit and no report is written

## Hash-chain verification model

- `record_hash` is recomputed over canonical JSON (`sort_keys=True`,
  `separators=(",", ":")`, `ensure_ascii=False`) of the record with
  `record_hash` and `audit_record_id` both excluded, matching the Phase 8B
  ingest hash model exactly.
- the first parsed record must have `previous_record_hash` null.
- each following parsed record's `previous_record_hash` must equal the
  immediately prior record's stored `record_hash`.
- `hash_chain_valid` is `false` if any record fails hash recomputation or
  chain continuity.
- the store is never edited during verification.

## Duplicate detection model

- duplicate `audit_record_id` is reported and counted.
- duplicate `artifact_hash` is reported and counted.
- duplicate `record_hash` is reported and counted.
- verification continues after a duplicate is detected; duplicates do not
  abort the run.

## JSONL validation model

- blank lines are ignored.
- an invalid-JSON line is recorded as an `invalid_json` issue and skipped.
- a JSON line that is not an object is recorded as a `not_object` issue and
  skipped.
- a parsed record missing one of the required reporting fields
  (`audit_record_id`, `audit_schema_version`, `source_phase`, `product_id`,
  `report_week`, `selected_gate`, `operator`, `primitive_outcome`,
  `artifact_hash`, `previous_record_hash`, `record_hash`,
  `manual_review_status`, `created_at`, `phase8b_ingested_at`) is recorded as
  a `missing_required_field` issue but still counted and included in
  reporting summaries.

## Reporting model

Reporting summaries group all parsed records by `product_id`, `report_week`,
`selected_gate`, `operator`, `primitive_outcome`, and
`manual_review_status`.

`verification_status` is `valid` when `record_count > 0`, `issue_count == 0`,
and `hash_chain_valid` is `true`; `warning` when the store has non-blank
content and either `issue_count > 0` or `hash_chain_valid` is `false`
(including a store with only invalid/non-object lines and zero records);
`empty` when the store is missing or has zero non-blank lines;
`invalid` when a critical path/store failure prevented
verification.

## Output report layout

- `tmp/phase8c-audit-report/audit-store-verification.json`
- `tmp/phase8c-audit-report/audit-store-verification.md`

## Failure behavior

`valid`, `warning`, and `empty` all exit `0`. Only a critical store-path
safety violation (unsafe input path) or a report-dir rejection exits
non-zero; a report-dir rejection additionally means no report is written,
since there is no verified-safe location to write one.

## Non-goals

- no database, no SQLite implementation, no S3 implementation, no DynamoDB
  implementation
- no backend, no FastAPI, no API routes
- no external APIs, no external URLs, no network behavior
- no new runtime mutation path
- no primitive execution
- no vault read/write
- no Phase 7D wrapper behavior change
- no Phase 8B ingest behavior change
- no approve-all, no global approval, no multi-gate execution
- no next-gate automation, no chain execution
- no affiliate content generation, no autopublish, no campaign launch
- no marketplace connector, no production deployment

## Phase 8B ingest boundary

Phase 8C does not modify, wrap, call, or execute
`scripts/dev/ingest_phase8b_audit_record.py` or
`scripts/dev/run_phase8b_audit_ingest.sh`. It only reads the JSONL file that
ingest produces. `durable_audit_store_status` moves from
`local_append_only_prototype` to `jsonl_verifier_reporting` to reflect the
addition of the read-only verifier, not a change to the writer.

## Phase 7D wrapper boundary

Phase 8C does not modify, wrap, call, or execute
`scripts/dev/run_phase7d_single_gate_wrapper.sh` or
`scripts/dev/execute_single_gate_approval.py`.
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

## Phase 7B verifier compatibility

Phase 8C does not modify or call
`scripts/dev/run_phase7b_audit_verifier.sh` or
`scripts/dev/verify_manual_approval_audit.py`. Phase 7B remains
artifact-level verification of one audit artifact; Phase 8C is store-level
verification of the accumulated JSONL. A Phase 8C `valid` result is not
approval.

## Operator runbook integration

No runtime-ceremony changes are made; Phase 8C is referenced additively from
`docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md` and
`docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md` as the read-only verifier that
now exists over the Phase 8B store.

## Test strategy

Deterministic tests: file/status existence; scope/safety token coverage;
static safety of the verifier script and shell runner (no subprocess/
sqlite3/boto3/requests/httpx/urllib imports, no FastAPI, no primitive calls,
no vault writes, no `--execute`, no approval flags set truthy, no wrapper/
primitive/verifier calls); executable-mode and `bash -n`/`py_compile`
checks; empty-store behavior; valid-store behavior against real Phase 8B
output; hash-mismatch and chain-mismatch detection; duplicate detection
(audit_record_id/artifact_hash/record_hash); invalid-JSON/non-object/
missing-field handling; path-safety rejections; documentation regression;
protected runtime file hash regression (including the Phase 8B ingest
script); and a static-safety scan over only the new Phase 8C task/doc/script
files.

## Acceptance criteria

- verifier script and shell runner exist and are executable/well-formed
- verification is strictly read-only over the JSONL store
- hash recomputation and chain continuity checks are correct against real
  Phase 8B output
- duplicate and malformed-line detection behave as specified
- unsafe store/report paths are rejected appropriately
- design doc contains `phase8c_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`, and
  `durable_audit_store_status: jsonl_verifier_reporting`
- ROADMAP, PROJECT_STATE, the Phase 8B doc, and the Phase 8A design doc all
  reference Phase 8C additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B runtime files remain unchanged
- no backend/API/database file is added
- all runtime writes are confined to `tmp/phase8c-audit-report/`

## Verification commands

```text
source .venv/bin/activate

python -m pytest -q tests/test_phase8c_audit_store_verifier_reporting.py
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

python -m py_compile scripts/dev/verify_phase8c_audit_store.py
bash -n scripts/dev/run_phase8c_audit_report.sh

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8C is a local tmp report only: no SQLite index, no S3/DynamoDB, no
backend/API, no authenticated identity, no production deployment, no
retention enforcement, no advanced query CLI, and no automatic remediation.

## Final status target

phase8c_status: success
