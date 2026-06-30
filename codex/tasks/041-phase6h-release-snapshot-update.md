# Task 041 - Phase 6H Release Snapshot Update

## 1. Purpose

Summarize the completed Phase 6A-6G work in a Phase 6 release snapshot and
additively update repository state, roadmap, demo, and acceptance docs, while
preserving every existing token contract. Docs/tests/task-only: no runtime
behavior change and no new script.

## 2. Scope

- Add a Phase 6 release snapshot document.
- Additively update PROJECT_STATE, ROADMAP, DEMO, and ACCEPTANCE.
- Add a docs-contract test for the Phase 6 snapshot.
- Reference the safe read-only chain commands and primitive names as names only;
  include no approval execution command forms.

## 3. Files

- `codex/tasks/041-phase6h-release-snapshot-update.md`
- `docs/RELEASE_SNAPSHOT_PHASE6.md` (new)
- `tests/test_phase6h_release_snapshot.py` (new)
- `docs/PROJECT_STATE.md` (additive)
- `docs/ROADMAP.md` (additive)
- `docs/DEMO.md` (additive)
- `docs/ACCEPTANCE.md` (additive)

Not modified: runtime scripts, Phase 2G/2H/2I scripts, Phase 6B/6C/6E
implementations, the Phase 3/5 release snapshot files, dependency files, and
GitHub workflows.

## 4. Release snapshot scope

`docs/RELEASE_SNAPSHOT_PHASE6.md` documents the Phase 6A-6G matrix (all
complete), the safe read-only chain `5D -> 6B -> 6C -> 6E` and its commands, the
Phase 6 guardrails (still manual-approved/read-only, no runtime approval wrapper,
no runtime audit verifier, no vault read/write, no approval mutation, Phase
2G/2H/2I unchanged, 6F/6G boundary-only, wrapper and audit-verifier
implementations as separate future phases, backend/API/database/marketplace out
of scope), the output folders, the test posture, limitations, and next steps.

## 5. Documentation update scope

- PROJECT_STATE: add a pointer to `docs/RELEASE_SNAPSHOT_PHASE6.md` and a Phase 6
  summary note; preserve all existing token contracts.
- ROADMAP: mark Phase 6H complete and note the future wrapper/audit-verifier
  implementations as separate; preserve `Phase 5`, `read-only`, `manual-approved`.
- DEMO: add a "Phase 6 read-only approval chain" section.
- ACCEPTANCE: add a "Phase 6 read-only approval chain acceptance" section.

## 6. Token contracts to preserve

ROADMAP: `Phase 5`, `read-only`, `manual-approved`. PROJECT_STATE:
`Current architecture`, `no database`, `no FastAPI`, `no UI`, `no external APIs`,
`no autopublish`. The Phase 3E and Phase 5E snapshot docs and their tests are not
touched.

## 7. No-execution and static-safety rules

The new Phase 6H files (the snapshot and this task) must not contain approval
execution command forms (`APPROVE_*` truthy assignments, bash wrapper
invocations for Phase 2G/2H/2I, or python invocations of the primitive scripts),
external URLs, the contiguous operator path, or secret markers. Safe read-only
chain command names and bare primitive/flag names are allowed. The
no-execution/static-safety scan covers only the two new Phase 6H files.

## 8. Test strategy

Deterministic docs-contract tests: snapshot + task exist; `phase6h_status:
success`; snapshot mentions Phase 6A-6G; safe chain documented; guardrail
statements (no runtime wrapper/audit verifier, no vault rw, no approval mutation,
no Phase 2G/2H/2I execution, primitives unchanged, 6F/6G boundary-only, separate
future implementations, backend/etc out of scope); PROJECT_STATE pointer; ROADMAP
6H complete; DEMO/ACCEPTANCE sections; token regression; no Phase 6H runtime
script; no-execution and static-safety scans of the two new files only.

## 9. Acceptance criteria

- Snapshot, task, and test exist; the test passes.
- Phase 6A-6G, Phase 5E, and Phase 3E tests still pass; full suite passes.
- No runtime script changed; no hardcoded operator path in scripts.
- No approval mutation, vault write, or primitive execution is introduced.

## 10. Verification commands

```
python -m pytest -q tests/test_phase6h_release_snapshot.py
python -m pytest -q tests/test_phase6g_manual_approval_audit_verifier_boundary.py tests/test_phase6f_single_gate_manual_approval_wrapper_boundary.py tests/test_phase6e_dry_run_approval_execution_planner.py tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
python -m pytest -q tests/test_phase5e_release_snapshot.py tests/test_phase3e_release_snapshot.py
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 11. Known limitations

- Documentation snapshot only; it records state and changes no behavior.
- No actual approval wrapper or audit verifier exists; both are separate future
  phases under their own approval.

## 12. Final status target

`phase6h_status: success`
