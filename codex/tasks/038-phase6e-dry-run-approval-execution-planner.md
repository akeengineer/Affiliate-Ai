# Task 038 - Phase 6E Dry-run Manual Approval Execution Planner

## 1. Purpose

Generate a dry-run execution plan from the Phase 6B packet and Phase 6C verifier
output, using the Phase 6D boundary doc as a contract reference. The planner
shows what a future manual approval command would require before executing; it
executes nothing and writes nothing to the vault.

## 2. Scope

- A Python stdlib planner and a bash wrapper.
- Output only under `tmp/phase6e-approval-execution-plan/`.
- Read the Phase 6B packet JSON and Phase 6C verifier JSON; reference the
  Phase 6D boundary doc by existence/size/hash only.
- Docs and tests. No change to Phase 6B/6C, Phase 2G/2H/2I, Phase 4/5, or
  scoring behavior.

## 3. Files

- `codex/tasks/038-phase6e-dry-run-approval-execution-planner.md`
- `scripts/dev/build_approval_execution_plan.py`
- `scripts/dev/run_phase6e_approval_execution_plan.sh`
- `tests/test_phase6e_dry_run_approval_execution_planner.py`
- `docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md` (additive section)
- `.gitignore` (+ `tmp/phase6e-approval-execution-plan/`)
- `scripts/dev/README.md` (one index entry)

## 4. Command design

```
bash scripts/dev/run_phase6e_approval_execution_plan.sh <product_id> <week>
```

Two args; validate `product_id` `^[a-z0-9-]+$` and `week` `^[0-9]{4}-W[0-9]{2}$`;
derive repo root and `cd "$REPO_ROOT"`; reject `ENABLE_AUTOPUBLISH`,
`ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`, `APPROVE_DECISION`,
`APPROVE_FINALIZE`; select `.venv/bin/python` -> `python3` -> `python`; exec the
planner. Prints `execution_plan_json:`, `execution_plan_md:`, `verdict:`,
`phase6e_status:`. Exit 0 for `ready`/`blocked`, non-zero for `failed`.

## 5. Data sources and read policy

Body-readable: the Phase 6B packet JSON and Phase 6C verifier JSON. The Phase 6D
boundary doc is referenced by existence/size/sha256 only (never parsed). The
planner never reads the vault, the primitive script bodies, the Phase 6B/6C
Markdown, raw score/report/dashboard bodies, the network, or any path outside
the repo.

## 6. Output structure

`tmp/phase6e-approval-execution-plan/execution-plan-<product_id>-<week>.json`
(`type`, ids, generated_at, `dry_run`, packet/verifier/boundary paths,
boundary_doc meta, verifier_verdict, preconditions{}, proposed_gate_sequence,
per_gate_plan{promote,decision,finalization}, required_future_operator_inputs,
audit_preview, blockers, verdict, statement) and the `.md` mirror (precondition
table, gate-plan table, audit preview, blockers, dry-run statement, guardrail
footer).

## 7. Precondition model

Hard preconditions: Phase 6B packet exists; Phase 6C verifier exists; Phase 6C
verdict is `ready` or `warning` (`failed`/missing -> planner `failed`);
product_id/report_week match across args, packet, and verifier; packet
`dry_run` is true; packet has no approval execution signal; Phase 6C
`no_leakage`, `sources_tmp_only`, and `finalization_consistent` are true;
boundary doc exists; gate order defined; finalization blocked unless
`compliance_status == "approved"`.

## 8. Gate planning logic

Order promote -> decision -> finalization. promote plan-ready iff hard
preconditions pass and `gates.promote_gate_ready`; decision iff promote ready and
`gates.decision_gate_ready`; finalization iff decision ready,
`gates.finalization_gate_ready`, and `compliance_status == "approved"`. The
normal current case has `compliance_status` not approved, so finalization is
blocked and the verdict is `blocked`.

## 9. Verdict/status policy

Precedence `failed > blocked > ready`. `failed`: missing packet/verifier/
boundary, id mismatch, packet not dry-run, Phase 6C verdict `failed`, leakage/
sources/finalization checks not confirmed, packet approval execution signal, or
invalid input. `blocked`: hard preconditions pass but one or more gates are
blocked, or Phase 6C verdict is `warning`. `ready`: hard preconditions pass,
Phase 6C verdict `ready`, and all three gates plan-ready. `ready`/`blocked` exit
0 (`phase6e_status: success`); `failed` exits non-zero (`phase6e_status:
failed`).

## 10. Guardrails

- output only under `tmp/phase6e-approval-execution-plan/` (guarded dir)
- output self-safety scan rejects external URLs, `file://`, operator path,
  `vault/`, `input_path`, `note_refs`, `next_allowed_action`, approval execution
  strings, primitive command forms, affiliate/secret markers, and script/JS
  markup; bare primitive file names and bare flag names are allowed
- wrapper rejects approval flags; read-only; no vault; no network; no primitive
  execution
- boundary doc is hashed, never parsed
- self-reference: denylist literals composed so the source carries no contiguous
  operator-path, approval execution, or primitive command-form literal

## 11. Test strategy

Deterministic pytest: existence/exec/`bash -n`/`py_compile`/`.gitignore`;
invalid product_id/week/arg-count; guardrail + approval flags; end-to-end normal
case (`verdict: blocked`); JSON content; output self-safety; failed path (Phase
6C `failed`/missing); warning path (Phase 6C `warning` -> blocked); finalization
blocked rule; gate order; boundary-doc hash; cross-CWD; CI-C alignment; static
boundary; no vault write; no forbidden body ingestion.

## 12. Acceptance criteria

- The 5D -> 6B -> 6C -> 6E chain exits 0 with `verdict: blocked` and
  `phase6e_status: success` while compliance is not approved.
- A Phase 6C `failed`/missing input yields `verdict: failed` and exit 1; a Phase
  6C `warning` yields `verdict: blocked` and exit 0.
- Focused Phase 6E, 6D, 6C, 6B, and 6A tests pass; full suite passes.
- No vault write; no primitive execution; no hardcoded operator path.

## 13. Verification commands

```
bash -n scripts/dev/run_phase6e_approval_execution_plan.sh
python -m py_compile scripts/dev/build_approval_execution_plan.py
python -m pytest -q tests/test_phase6e_dry_run_approval_execution_planner.py
python -m pytest -q tests/test_phase6d_manual_approval_execution_boundary.py tests/test_phase6c_approval_review_packet_verifier.py tests/test_phase6b_dry_run_approval_review_packet.py tests/test_phase6a_manual_approved_workflow_boundary.py
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
bash scripts/dev/run_phase6b_approval_review_packet.sh prod-laptop-stand 2026-W26
bash scripts/dev/run_phase6c_approval_review_verifier.sh prod-laptop-stand 2026-W26
bash scripts/dev/run_phase6e_approval_execution_plan.sh prod-laptop-stand 2026-W26
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 14. Known limitations

- Plan only; it approves nothing and authorizes no mutation.
- The normal verdict is `blocked` while `compliance_status` is not approved;
  `ready` requires a future approved compliance status.
- The boundary doc is referenced by hash only, not validated by content.

## 15. Final status target

`phase6e_status: success`
