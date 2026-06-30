# Task 036 - Phase 6C Approval Review Packet Verifier

## 1. Purpose

Verify the Phase 6B dry-run approval review packet and produce a read-only
verification report/summary, analogous to the Phase 4D and Phase 5C verifiers.
Read-only: no vault access, no approval mutation, no primitive execution, no
approval flag use.

## 2. Scope

- A Python stdlib verifier and a bash wrapper.
- Output only under `tmp/phase6c-approval-review-verifier/`.
- Validate the Phase 6B packet structure/safety and check listed sources by
  existence/size/hash only.
- Docs and tests. No change to Phase 6B builder, Phase 2G/2H/2I, Phase 4/5, or
  scoring behavior.

## 3. Files

- `codex/tasks/036-phase6c-approval-review-packet-verifier.md`
- `scripts/dev/verify_approval_review_packet.py`
- `scripts/dev/run_phase6c_approval_review_verifier.sh`
- `tests/test_phase6c_approval_review_packet_verifier.py`
- `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md` (additive section)
- `.gitignore` (+ `tmp/phase6c-approval-review-verifier/`)
- `scripts/dev/README.md` (one index entry)

## 4. Command design

```
bash scripts/dev/run_phase6c_approval_review_verifier.sh <product_id> <week>
```

Two args; validate `product_id` `^[a-z0-9-]+$` and `week` `^[0-9]{4}-W[0-9]{2}$`;
derive repo root and `cd "$REPO_ROOT"`; reject `ENABLE_AUTOPUBLISH`,
`ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`, `APPROVE_DECISION`,
`APPROVE_FINALIZE`; select `.venv/bin/python` -> `python3` -> `python`; exec the
verifier. Prints `verification_review_json:`, `verification_review_md:`,
`verdict:`, `phase6c_status:`. Exit 0 for `ready`/`warning`, non-zero for
`failed`.

## 5. Data sources and read policy

Body-readable targets: the Phase 6B packet JSON and Markdown
(`tmp/phase6b-approval-review/review-<product_id>-<week>.{json,md}`). Listed
sources in `packet["sources"]` are checked by existence/size/hash only
(`read_bytes` for hashing; never parsed or emitted). Every source path must be
relative, start with `tmp/`, contain no `..`, and contain no vault path. The
verifier never reads the vault, raw score/markdown/HTML bodies, the network, or
any path outside `tmp/`.

## 6. Output structure

`tmp/phase6c-approval-review-verifier/verification-review-<product_id>-<week>.json`
(`type=phase6c_approval_review_verification`, product_id, report_week,
generated_at, verdict, checks{}, warnings[], source_integrity[], packet_path)
and `...verification-review-<product_id>-<week>.md` (title, verdict, checks
table, warnings, source-integrity table, guardrail footer).

## 7. Verification rules

Hard checks (any false -> `failed`): `packet_json_exists`, `packet_md_exists`,
`packet_type_ok`, `dry_run_true`, `ids_match`, `evidence_present`,
`score_scalar_safe`, `compliance_safe`, `verifier_present`, `gates_complete`,
`finalization_consistent` (`finalization_gate_ready` false unless
`compliance_status == "approved"`), `sources_tmp_only`, `no_leakage`,
`no_approval_execution`, `readiness_note_ok`.

Soft warnings (`warning` when hard checks pass): a recorded-present source is now
missing; a source marked not present; current bytes/sha256 differ from the
packet snapshot. Hash/size mismatch is a warning, not a failure, to support
staleness detection.

## 8. Verdict/status policy

`ready` (all hard pass, no warnings) and `warning` (hard pass, >=1 warning) exit
0 with `phase6c_status: success`; `failed` (any hard fails) exits non-zero with
`phase6c_status: failed`.

## 9. Guardrails

- output only under `tmp/phase6c-approval-review-verifier/` (guarded dir)
- output self-safety scan rejects external URLs, `file://`, operator path,
  `vault/`, `input_path`, `note_refs`, `next_allowed_action`, approval execution
  strings, affiliate/secret markers, and script/JS markup before writing
- wrapper rejects approval flags; read-only; no vault; no network; no primitive
  execution
- self-reference: denylist literals composed so the source carries no contiguous
  operator-path or approval execution literal; the report uses labels

## 10. Test strategy

Deterministic pytest: existence/exec/`bash -n`/`py_compile`/`.gitignore`;
invalid product_id/week/arg-count; guardrail + approval flags; end-to-end ready;
JSON content; output self-safety; failed path (tampered packet); warning path
(changed source); missing packet; finalization-consistency; sources tmp-only;
cross-CWD; CI-C alignment; static boundary; no vault write; no forbidden body
ingestion.

## 11. Acceptance criteria

- `run_phase6c_approval_review_verifier.sh prod-laptop-stand 2026-W26` after the
  5D + 6B chain exits 0 with `verdict: ready` and `phase6c_status: success`.
- A tampered packet yields `verdict: failed` and exit 1; a changed source yields
  `verdict: warning` and exit 0.
- Focused Phase 6C, 6B, 6A, and CI-C tests pass; full suite passes.
- No vault write; no primitive execution; no hardcoded operator path.

## 12. Verification commands

```
bash -n scripts/dev/run_phase6c_approval_review_verifier.sh
python -m py_compile scripts/dev/verify_approval_review_packet.py
python -m pytest -q tests/test_phase6c_approval_review_packet_verifier.py
python -m pytest -q tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py tests/test_ci_c_runner_regression_guards.py
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
bash scripts/dev/run_phase6b_approval_review_packet.sh prod-laptop-stand 2026-W26
bash scripts/dev/run_phase6c_approval_review_verifier.sh prod-laptop-stand 2026-W26
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 13. Known limitations

- Verifies an existing packet only; does not rebuild Phase 6B.
- Source integrity is hash/size based; a changed source is a warning, not a
  failure, so older packet snapshots are not treated as corruption.

## 14. Final status target

`phase6c_status: success`
