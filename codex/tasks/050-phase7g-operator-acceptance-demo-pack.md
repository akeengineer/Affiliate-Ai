# Task 050 — Phase 7G Operator Acceptance / Safe Demo Pack

phase7g_status: success

phase7d_runtime_readiness: implemented_manual_gate

## Purpose

Create an operator-facing safe acceptance/demo pack for the live Phase 7D
selected-gate wrapper.

## Scope

Phase 7G adds a safe demo runner, a deterministic acceptance-summary builder,
tests, and documentation. It changes no wrapper or approval behavior, creates no
new mutation path, and performs no primitive execution or business-memory write.

## Files

- `scripts/dev/run_phase7g_safe_demo_pack.sh`
- `scripts/dev/build_phase7g_operator_acceptance_summary.py`
- `tests/test_phase7g_operator_acceptance_demo_pack.py`
- `codex/tasks/050-phase7g-operator-acceptance-demo-pack.md`
- `docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md`
- additive updates to ROADMAP, PROJECT_STATE, the Phase 7 live snapshot, and
  `.gitignore`

## Status model

- `success`: every safe scenario produced its expected prevented, blocked,
  invalid, artifact-inspection, or inventory result.
- `failed`: any scenario differs from its expected result or indicates primitive
  success.
- Runtime readiness remains `implemented_manual_gate`; Phase 7G does not widen
  that boundary.

## Operator acceptance objective

Give an operator a repeatable proof that the live wrapper rejects or blocks
unsafe and incomplete requests before any real execution is considered.

## Safe demo scenarios

The pack covers no-execute prevention, emergency-stop guard inventory, missing
evidence blocking, wrong approval flag guard inventory, approve-all text
rejection, chain/next-gate rejection, invalid gate rejection, safe audit
artifact inspection, and a Phase 7B verifier handoff note.

## Demo runner behavior

The strict-mode shell runner resolves its own location and repository root,
selects the repository virtual-environment interpreter when available, supports
cross-CWD use, creates temporary non-production evidence, scrubs approval
environment variables, and writes demo records only under
`tmp/phase7g-operator-acceptance/`. Temporary evidence and safe Phase 7D result
audits are removed on exit.

## Acceptance summary behavior

The Python builder reads only scenario records under the Phase 7G output
directory. It rejects missing, failed, or primitive-success records and writes
JSON and Markdown summaries containing statuses, scenarios, expected results,
observed exit codes, audit inventory, safety statement, operator checklist,
manual-review checklist, and next-phase recommendation.

## Phase 7D wrapper integration

The runner invokes the unchanged Phase 7D wrapper only for no-execute,
prevented, blocked, or invalid requests. Guards that would require runtime
execution intent are verified by static inventory against the protected wrapper
source instead of being exercised dynamically.

## Phase 7B verifier handoff

The pack records that the read-only verifier remains available for separate
audit inspection. Verifier validity is not approval and does not trigger another
gate.

## No-mutation guarantee

The demo supplies no runtime execution intent, directly calls no primitive,
does not read or write business memory, and introduces no new approval or
mutation path. Temporary files are limited to gitignored `tmp` locations.

## Operator checklist

Before any separately authorized real execution, verify the selected gate,
identifiers, Phase 6 evidence, selected-gate readiness, emergency stop,
operator identity, reason, intent, exact confirmation, matching flag semantics,
absence of global or chained requests, and use a non-production sample first.

## Failure/manual-review checklist

Inspect result and intent audits plus the wrapper exit code; establish whether a
primitive was invoked or partial completion occurred; never rerun, advance, or
roll back automatically; require operator review before retry.

## Documentation update scope

Add the Phase 7G operating document and make additive state pointers in ROADMAP,
PROJECT_STATE, and the Phase 7 runtime-live snapshot.

## No-execution/static-safety rules

New Phase 7G files contain no approval flag truthy assignments, executable
primitive command forms, external URL schemes, operator-local repository paths,
secret material, backend/API/database/network commands, or JavaScript.
Primitive and approval flag names may appear only as non-executable inventory.

## Test strategy

Tests verify file/status contracts, protected runtime hashes, shell/Python
syntax, cross-CWD execution, expected scenario outcomes, summaries, unchanged
business-memory contents, additive documentation tokens, and static safety of
new Phase 7G files.

## Acceptance criteria

- All nine safe scenarios pass.
- JSON and Markdown summaries report Phase 7G success and current Phase 7D
  readiness.
- No scenario reports primitive success.
- Protected Phase 7D and Phase 7B runtime files retain their baseline hashes.
- The business-memory file tree is byte-for-byte unchanged.
- Focused and full regression suites pass.

## Verification commands

```text
source .venv/bin/activate
python -m pytest -q tests/test_phase7g_operator_acceptance_demo_pack.py
python -m py_compile scripts/dev/build_phase7g_operator_acceptance_summary.py
bash -n scripts/dev/run_phase7g_safe_demo_pack.sh
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
git diff --check
git status --short --branch
```

## Known limitations

The pack is local-only, uses non-production temporary inputs, does not perform a
successful approval run, does not authenticate operators, and does not provide
a durable audit store or automated retry.

## Final status target

phase7g_status: success
