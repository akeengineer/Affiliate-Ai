# Task 033 - Phase 5E Release Snapshot Update

## 1. Purpose

Update project state, roadmap, release snapshot, demo, and acceptance docs so the
repository accurately reflects that Phase 4A-4E and Phase 5A-5D are complete.
Docs/tests/task only: no runtime behavior change, no new or modified scripts.

## 2. Scope

- Add a Phase 5 release snapshot document.
- Additively update PROJECT_STATE, ROADMAP, DEMO, and ACCEPTANCE docs.
- Add a docs-contract test for the Phase 5 snapshot.
- Preserve every token the existing Phase 3E contract test depends on.

## 3. Files

- `codex/tasks/033-phase5e-release-snapshot-update.md`
- `docs/RELEASE_SNAPSHOT_PHASE5.md` (new)
- `docs/PROJECT_STATE.md` (additive)
- `docs/ROADMAP.md` (additive)
- `docs/DEMO.md` (additive)
- `docs/ACCEPTANCE.md` (additive)
- `tests/test_phase5e_release_snapshot.py` (new)

Not modified: `scripts/dev/show_release_snapshot.sh`,
`docs/RELEASE_SNAPSHOT_PHASE3.md`, `tests/test_phase3e_release_snapshot.py`, and
all runtime scripts.

## 4. Release snapshot scope

`docs/RELEASE_SNAPSHOT_PHASE5.md` documents the completed UI shell line:
objective, phase matrix (Phase 4A-4E, Phase 5A-5D), operator commands, output
artifacts, the UI shell chain, verifier/acceptance gates, guardrails, verdict
policy (`ready`/`warning`/`failed`, `phase5d_status`, `ui_shell_demo_status`),
test posture, known limitations, and next steps.

## 5. Documentation update policy

- Additive edits only; do not delete existing token-contract content.
- Reframe `no UI` honestly: it means no UI framework or interactive server UI;
  Phase 5 provides a static read-only UI shell only.
- No external URLs, no operator-path literal, no secret/affiliate markers, and no
  command-style mention of approved Phase 2G/2H/2I scripts in the new docs.

## 6. Token compatibility constraints

PROJECT_STATE.md must keep the Phase 3E tokens: `Current architecture`,
`no database`, `no FastAPI`, `no UI`, `no external APIs`,
`no affiliate content generation`, `no autopublish`, `no campaign launch`,
`no vault writes by default`, the command tokens, and the artifact-map sections
(`tmp outputs`, `vault memory outputs`, `docs`, `scripts`). ROADMAP.md must keep
`Phase 4A`, `Phase 4B`, `Phase 4C`, `Phase 5`, `read-only`, `manual-approved`.

## 7. Test strategy

`tests/test_phase5e_release_snapshot.py` (deterministic, docs-contract only):
snapshot + task exist; phase tokens 4A-4E and 5A-5D; the four UI shell commands
and four outputs; verdict tokens; PROJECT_STATE Phase 5 capability tokens; ROADMAP
marks 5A-5D complete; a regression guard for the Phase 3E tokens; DEMO/ACCEPTANCE
references; static safety on the two new files. No brittle total-count assertion;
the Phase 3E test is left untouched.

## 8. Acceptance criteria

- `RELEASE_SNAPSHOT_PHASE5.md`, task 033, and the new test exist.
- Phase 5E and Phase 3E tests both pass; full suite passes.
- `show_release_snapshot.sh` still runs and surfaces the updated PROJECT_STATE.
- No runtime file changed; no hardcoded operator path in scripts.

## 9. Verification commands

```
python -m pytest -q tests/test_phase5e_release_snapshot.py
python -m pytest -q tests/test_phase3e_release_snapshot.py
bash scripts/dev/show_release_snapshot.sh | head -40
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 10. Known limitations

- Documentation snapshot only; it records state and changes no behavior.
- The UI shell is static and read-only; the snapshot reflects the demo chain at
  documentation time.

## 11. Final status target

`phase5e_status: success`
