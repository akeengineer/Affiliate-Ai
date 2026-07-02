# Task 056 — Phase 8E Audit Export Pack

phase8e_status: success

phase7d_runtime_readiness: implemented_manual_gate

durable_audit_store_status: export_pack

## Purpose

Implement a read-only audit export pack that bundles or summarizes existing
local audit evidence from Phase 8B (JSONL store), Phase 8C (verification
report), and Phase 8D (query result) into a single reviewable export
manifest and Markdown summary. Phase 8E never appends to or mutates any
source evidence file and changes no Phase 7D wrapper, Phase 8B ingest, or
Phase 8C/8D behavior.

## Scope

Phase 8E is read-only against `audit-records.jsonl`, the Phase 8C
verification report, and the Phase 8D query report. It never appends to or
modifies any source evidence file, changes no Phase 7D wrapper behavior,
changes no Phase 8B ingest behavior, changes no Phase 8C verifier behavior,
changes no Phase 8D query behavior, executes no primitive, performs no vault
read/write, connects to no backend/API/database/S3/DynamoDB/SQLite/external
service, and adds no new mutation path.

## Files

- `codex/tasks/056-phase8e-audit-export-pack.md`
- `docs/PHASE8E_AUDIT_EXPORT_PACK.md`
- `scripts/dev/build_phase8e_audit_export_pack.py`
- `scripts/dev/run_phase8e_audit_export.sh`
- `tests/test_phase8e_audit_export_pack.py`
- additive updates to `docs/ROADMAP.md`
- additive updates to `docs/PROJECT_STATE.md`
- additive updates to `docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`
- additive updates to `docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`
- additive update to `.gitignore` (`tmp/phase8e-audit-export/`,
  `tmp/phase8e-test-input/`)

## Status model

- `success`: the export script and shell runner exist, export is read-only
  over all source evidence, the manifest/summary/optional evidence copies
  behave as specified, output is confined to `tmp/phase8e-audit-export/`,
  additive documentation pointers exist, protected runtime files (Phase
  6-8D) stay unchanged, the shell runner is mode `100755` on disk and in the
  git index, and `phase7d_runtime_readiness` remains
  `implemented_manual_gate`.
- `failed`: the export pack appends to or mutates any source evidence file,
  writes outside `tmp/phase8e-audit-export/`, accepts an unsafe evidence/
  export-dir path, mis-copies evidence, or a protected runtime surface
  changes.

## Read-only export objective

Provide a deterministic, read-only packaging step over existing Phase
8B/8C/8D local evidence for operator/reviewer distribution, without
implementing a database, backend, signing, or distribution service, and
without adding any new mutation path.

## Input evidence contract

- Phase 8B JSONL store: `tmp/phase8b-audit-store/audit-records.jsonl`
  (default); missing is allowed and produces an empty export pack
- Phase 8C verification report: `audit-store-verification.json`/`.md`
  under `tmp/phase8c-audit-report/` (default); missing is allowed and
  recorded as missing evidence
- Phase 8D query result: `audit-query-result.json`/`.md` under
  `tmp/phase8d-audit-query/` (default); missing is allowed and recorded as
  missing evidence
- all five inputs are opened read-only; none is ever written to

## Path safety model

Evidence-path rules (apply to all five inputs):

- must resolve under the repository root
- must not resolve under `vault/`, `docs/`, `scripts/`, `tests/`, or `codex/`
- symlinks are rejected
- path traversal is rejected
- absolute paths outside the repository are rejected
- a safety violation on any explicitly-checked path produces a non-zero
  exit and no manifest is written; a merely-missing default path is not an
  error

Export-dir rules:

- default: `tmp/phase8e-audit-export`
- must resolve under `tmp/phase8e-audit-export` only
- created if missing
- a custom export dir outside `tmp/phase8e-audit-export` is rejected with a
  non-zero exit and no manifest is written

## Export manifest model

The manifest carries: `phase8e_status`, `durable_audit_store_status`,
`phase7d_runtime_readiness`, `export_status`, `export_dir`, `generated_at`,
`include_copies`, `source_evidence`, `missing_evidence`, `source_hashes`,
`record_count`, `invalid_line_count`, `warning_count`,
`verification_status`, `query_status`, `summaries`, `copied_files`,
`safety_statement`, and `limitations`. Each `source_evidence` entry carries
`label`, `path`, `exists`, `allowed`, `sha256`, `size_bytes`, and
`copied_to`. `summaries` groups all valid store records by `product_id`,
`report_week`, `selected_gate`, `operator`, `primitive_outcome`, and
`manual_review_status`.

## Export summary model

The Markdown summary carries the same status/count fields as the manifest
plus a source-evidence table, a missing-evidence table, a source-hashes
list, the reporting summary tables, a copied-files section (or an explicit
"not requested" note when `--include-copies` was not set), a safety
statement, and known limitations.

## Source file hash model

`source_hashes` and each `source_evidence[].sha256` are the sha256 of the
existing file's raw bytes, computed once and reused both for the manifest
and, when `--include-copies` is set, for the copy written to
`tmp/phase8e-audit-export/evidence/`. Because the copy is a direct
byte-for-byte write of the exact bytes already hashed, the copy is
byte-identical to the source by construction.

## Optional evidence copy model

`--include-copies` copies every existing, safety-validated input into
`tmp/phase8e-audit-export/evidence/` under its documented destination
filename. A missing input is skipped, not copied as an empty file. No copy
is ever attempted from a path that failed safety validation, because such a
path aborts the run before evidence collection begins.

## Missing evidence behavior

- `empty`: the Phase 8B store is missing, or has zero valid records
- `success`: at least one valid record, no invalid lines/reports, and no
  missing optional evidence
- `warning`: missing optional evidence, invalid JSONL lines, or invalid
  optional report JSON, with at least one valid record present
- `invalid` is reserved for a critical path/export-dir validation failure,
  which is a hard failure (non-zero exit, no manifest written), not a
  manifest field value

## Failure behavior

`success`, `warning`, and `empty` all exit `0`. Only a critical evidence-path
safety violation or an export-dir rejection exits non-zero, and in that case
no manifest or summary is written.

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
- no Phase 8D query behavior change
- no approve-all, no global approval, no multi-gate execution
- no next-gate automation, no chain execution
- no affiliate content generation, no autopublish, no campaign launch
- no marketplace connector, no production deployment
- no archive signing or encryption
- no automated distribution

## Phase 8B ingest boundary

Phase 8E does not modify, wrap, call, or execute
`scripts/dev/ingest_phase8b_audit_record.py` or
`scripts/dev/run_phase8b_audit_ingest.sh`. It only reads the JSONL file that
ingest produces.

## Phase 8C verifier boundary

Phase 8E does not modify, wrap, call, or execute
`scripts/dev/verify_phase8c_audit_store.py` or
`scripts/dev/run_phase8c_audit_report.sh`. It only reads the verification
report those scripts produce, if present, and extracts `verification_status`
for the manifest.

## Phase 8D query boundary

Phase 8E does not modify, wrap, call, or execute
`scripts/dev/query_phase8d_audit_store.py` or
`scripts/dev/run_phase8d_audit_query.sh`. It only reads the query result
those scripts produce, if present, and extracts `query_status` for the
manifest.

## Phase 7D wrapper boundary

Phase 8E does not modify, wrap, call, or execute
`scripts/dev/run_phase7d_single_gate_wrapper.sh` or
`scripts/dev/execute_single_gate_approval.py`.
`phase7d_runtime_readiness` remains `implemented_manual_gate`.

## Operator/reviewer use model

1. use Phase 8B to ingest existing audit artifacts.
2. use Phase 8C to verify/report store integrity.
3. use Phase 8D to query relevant records.
4. use Phase 8E to create a reviewable export pack summarizing the above.
5. treat a Phase 8E export as evidence packaging, never as approval.
6. treat a Phase 8E `warning` result as a signal to run Phase 8C/8D and
   review manually before distributing the export pack.

## Test strategy

Deterministic tests: file/status existence; scope/safety token coverage;
static safety of the export script and shell runner (no subprocess/sqlite3/
boto3/requests/httpx/urllib imports, no FastAPI, no primitive calls, no
vault writes, no `--execute`, no approval flags set truthy, no wrapper/
primitive/Phase 7B/Phase 8B/Phase 8C/Phase 8D calls); executable-mode and
`bash -n`/`py_compile` checks; missing-evidence behavior (missing store);
export behavior without copies against a real Phase 8B/8C/8D fixture chain
(manifest fields, summaries, source hashes, source-file immutability);
export behavior with `--include-copies` (evidence directory contents,
byte-identical copies, populated `copied_files`); warning behavior (invalid
JSONL line, invalid optional report JSON, missing optional evidence);
path-safety rejections; documentation regression; protected runtime file
hash regression (including Phase 8B ingest and Phase 8C/8D scripts);
shell-runner permission checks (filesystem mode and git index mode); and a
static-safety scan over only the new Phase 8E task/doc/script files.

## Acceptance criteria

- export script and shell runner exist and are executable/well-formed
- export is strictly read-only over all source evidence
- the manifest, summary, and optional evidence copies behave as specified
  against a real Phase 8B/8C/8D fixture chain
- missing-evidence and warning handling behave as specified
- unsafe evidence/export-dir paths are rejected appropriately
- design doc contains `phase8e_status: success`,
  `phase7d_runtime_readiness: implemented_manual_gate`, and
  `durable_audit_store_status: export_pack`
- ROADMAP, PROJECT_STATE, the Phase 8D doc, and the Phase 8C doc all
  reference Phase 8E additively
- protected Phase 6B/6C/6E/7B/7D/7G/8B/8C/8D runtime files remain unchanged
- no backend/API/database file is added
- all runtime writes are confined to `tmp/phase8e-audit-export/`
- the shell runner is mode `100755` on disk and in the git index

## Verification commands

```text
source .venv/bin/activate
umask 022

python -m pytest -q tests/test_phase8e_audit_export_pack.py
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

python -m py_compile scripts/dev/build_phase8e_audit_export_pack.py
bash -n scripts/dev/run_phase8e_audit_export.sh

chmod 755 scripts/dev/run_phase8e_audit_export.sh
test "$(stat -c '%a' scripts/dev/run_phase8e_audit_export.sh)" = "755"
git ls-files -s scripts/dev/run_phase8e_audit_export.sh | grep "^100755 "

find scripts/dev -type f -name "*.sh" -exec chmod 755 {} \;

env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q

grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
git diff --check
git status --short --branch
```

## Known limitations

Phase 8E is a local tmp export only: no archive signing, no encryption, no
SQLite index, no S3/DynamoDB, no backend/API, no authenticated identity, no
production deployment, no retention enforcement, no automated distribution,
and no automatic remediation.

## Final status target

phase8e_status: success
