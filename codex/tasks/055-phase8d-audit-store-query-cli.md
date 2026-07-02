# Task 055 — Phase 8D Audit Store Query CLI over JSONL

phase8d_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: jsonl_query_cli

## Purpose

Implement a read-only query CLI over the Phase 8B local append-only JSONL
audit store. Phase 8D filters, sorts, and limits records by product/week/
gate/operator/outcome/review-status/incident/hash-status and writes a
read-only query result. It never appends to or mutates the source JSONL and
changes no Phase 7D wrapper, Phase 8B ingest, or Phase 8C verifier behavior.

## Scope

Phase 8D is read-only against `audit-records.jsonl`. It never appends to or
modifies the store, changes no Phase 7D wrapper behavior, changes no Phase
8B ingest behavior, changes no Phase 8C verifier behavior, executes no
primitive, performs no vault read/write, connects to no backend/API/
database/S3/DynamoDB/SQLite/external service, and adds no new mutation path.

## Files

- `codex/tasks/055-phase8d-audit-store-query-cli.md`
- `docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`
- `scripts/dev/query_phase8d_audit_store.py`
- `scripts/dev/run_phase8d_audit_query.sh`
- `tests/test_phase8d_audit_store_query_cli.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`
- additive updates to `docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`
- additive update to `.gitignore` (`tmp/phase8d-audit-query/`,
  `tmp/phase8d-test-input/`)

## Status model

- `success`: the query CLI and shell runner exist, querying is read-only over
  the JSONL store, filters/sorting/limit behave as specified, output is
  confined to `tmp/phase8d-audit-query/`, additive documentation pointers
  exist, protected runtime files (Phase 6-8C) stay unchanged, the shell
  runner is mode `100755` on disk and in the git index, and
  `phase7d_runtime_readiness` remains `implemented_manual_gate`.
- `failed`: the query CLI appends to or mutates the source JSONL, writes
  outside `tmp/phase8d-audit-query/`, accepts an unsafe store/report path,
  mis-filters or mis-sorts records, or a protected runtime surface changes.

## Read-only query objective

Provide a deterministic, read-only lookup CLI over the Phase 8B JSONL audit
store for evidence retrieval by operators, without implementing a database,
backend, or query service, and without adding any new mutation path.

## Input store contract

- default input: `tmp/phase8b-audit-store/audit-records.jsonl`
- a missing store path is not an error; it produces an empty query result
  (`query_status: empty`, `total_records_read: 0`, `matched_records: 0`)
- an existing store path must be a file
- the store is opened read-only and never written to

## Path safety model

Store-path rules:

- must resolve under the repository root
- must not resolve under `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/`
- symlinks are rejected
- path traversal is rejected
- absolute paths outside the repository are rejected
- a store-path safety violation produces a non-zero exit and no report is
  written

Report-dir rules:

- default: `tmp/phase8d-audit-query`
- must resolve under `tmp/phase8d-audit-query` only
- created if missing
- a custom report dir outside `tmp/phase8d-audit-query` is rejected with a
  non-zero exit and no report is written

## Query filter model

All provided filters combine with AND semantics over: `product_id`,
`report_week`, `selected_gate`, `operator`, `primitive_outcome`,
`manual_review_status`, `incident_id`, and `hash_status`.

`hash_status` is computed best-effort per record using the same canonical
JSON hash model as Phase 8B/8C (record content with `record_hash` and
`audit_record_id` excluded): `valid` if the recomputed hash matches the
stored `record_hash`, `invalid` if `record_hash` is present but does not
match, and `unknown` if the record has no `record_hash` to verify against.

## Sorting model

- default sort field: `phase8b_ingested_at`; `created_at` is also supported
- ascending by default; `--descending` reverses the order
- a record missing the sort field sorts as an empty string
- an invalid `--sort-by` value is rejected by argument parsing (non-zero
  exit)

## Limit/pagination model

- default limit: 100
- valid range: 1 to 1000 inclusive
- an out-of-range or non-integer `--limit` is rejected by argument parsing
  (non-zero exit)
- `returned_records` is `min(matched_records, limit)`; the CLI does not
  paginate beyond a single limited page

## Output result layout

- `tmp/phase8d-audit-query/audit-query-result.json`
- `tmp/phase8d-audit-query/audit-query-result.md`

## Invalid-line handling

- blank lines are ignored
- an invalid-JSON line is recorded as a warning and skipped
- a JSON line that is not an object is recorded as a warning and skipped
- valid object records remain query candidates regardless of warnings
  elsewhere in the store
- `query_status` is `warning` whenever `invalid_line_count > 0`, even if
  matches were found, so an operator notices the store needs Phase 8C
  attention

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
- no Phase 8C verifier behavior change
- no approve-all, no global approval, no multi-gate execution
- no next-gate automation, no chain execution
- no affiliate content generation, no autopublish, no campaign launch
- no marketplace connector, no production deployment

## Phase 8B ingest boundary

Phase 8D does not modify, wrap, call, or execute
`scripts/dev/ingest_phase8b_audit_record.py` or
`scripts/dev/run_phase8b_audit_ingest.sh`. It only reads the JSONL file that
ingest produces.

## Phase 8C verifier boundary

Phase 8D does not modify, wrap, call, or execute
`scripts/dev/verify_phase8c_audit_store.py` or
`scripts/dev/run_phase8c_audit_report.sh`. Phase 8D's per-record
`hash_status` filter is a convenience for evidence lookup, not a
replacement for a full Phase 8C hash-chain verification pass.
`durable_audit_store_status` moves from `jsonl_verifier_reporting` to
`jsonl_query_cli` to reflect the addition of the read-only query CLI, not a
change to the verifier.

## Phase 7D wrapper boundary

Phase 8D does not modify, wrap, call, or execute
`scripts/dev/run_phase7d_single_gate_wrapper.sh` or
`scripts/dev/execute_single_gate_approval.py`.
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

## Operator use model

1. use Phase 8B to ingest existing audit artifacts.
2. use Phase 8C to verify/report store integrity.
3. use Phase 8D to query records by product/week/gate/operator/outcome/
   review-status/incident/hash-status for evidence lookup.
4. treat a Phase 8D `success`/`no_matches` result as a lookup outcome only,
   never as approval.
5. treat a Phase 8D `warning` result as a signal to run Phase 8C and review
   manually.

## Test strategy

Deterministic tests: file/status existence; scope/safety token coverage;
static safety of the query script and shell runner (no subprocess/sqlite3/
boto3/requests/httpx/urllib imports, no FastAPI, no primitive calls, no
vault writes, no `--execute`, no approval flags set truthy, no wrapper/
primitive/Phase 7B/Phase 8B/Phase 8C calls); executable-mode and
`bash -n`/`py_compile` checks; missing-store behavior; per-filter query
behavior against a real fixture store; AND-combination of filters; no-match
handling; sorting (both fields, both directions) and limit enforcement
including rejection of invalid limit/sort values; invalid-line/non-object
warning handling; hash-status classification (valid/invalid/unknown);
path-safety rejections; documentation regression; protected runtime file
hash regression (including Phase 8B ingest and Phase 8C verifier scripts);
shell-runner permission checks (filesystem mode and git index mode); and a
static-safety scan over only the new Phase 8D task/doc/script files.

## Acceptance criteria

- query script and shell runner exist and are executable/well-formed
- querying is strictly read-only over the JSONL store
- filters, sorting, and limit behave as specified against real Phase 8B
  output
- invalid-line handling and hash-status classification behave as specified
- unsafe store/report paths are rejected appropriately
- design doc contains `phase8d_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`, and
  `durable_audit_store_status: jsonl_query_cli`
- ROADMAP, PROJECT_STATE, the Phase 8C doc, and the Phase 8B doc all
  reference Phase 8D additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C runtime files remain unchanged
- no backend/API/database file is added
- all runtime writes are confined to `tmp/phase8d-audit-query/`
- the shell runner is mode `100755` on disk and in the git index

## Verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase8d_audit_store_query_cli.py
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

python -m py_compile scripts/dev/query_phase8d_audit_store.py
bash -n scripts/dev/run_phase8d_audit_query.sh

chmod 755 scripts/dev/run_phase8d_audit_query.sh
test "$(stat -c '%a' scripts/dev/run_phase8d_audit_query.sh)" = "755"
git ls-files -s scripts/dev/run_phase8d_audit_query.sh | grep "^100755 "

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8D is a local tmp query report only: no SQLite index, no S3/DynamoDB,
no backend/API, no authenticated identity, no production deployment, no
retention enforcement, no full-text search, no pagination cursor, and no
automatic remediation.

## Final status target

phase8d_status: success
