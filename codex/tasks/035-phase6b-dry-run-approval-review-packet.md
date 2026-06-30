# Task 035 - Phase 6B Dry-run Approval Review Packet

## 1. Purpose

Build a dry-run approval review packet under `tmp/` that gathers whitelisted
evidence from existing read-only artifacts for future manual approval. Read-only
with respect to the vault and approval primitives: no mutation, no primitive
execution, no approval flag use.

## 2. Scope

- A Python stdlib packet builder and a bash wrapper.
- Output only under `tmp/phase6b-approval-review/`.
- Strict field whitelisting; never emit `input_path`, `note_refs`,
  `next_allowed_action`, paths, URLs, or secrets.
- Docs and tests. No change to Phase 2G/2H/2I, Phase 4/5, or scoring behavior.

## 3. Files

- `codex/tasks/035-phase6b-dry-run-approval-review-packet.md`
- `scripts/dev/build_approval_review_packet.py`
- `scripts/dev/run_phase6b_approval_review_packet.sh`
- `tests/test_phase6b_dry_run_approval_review_packet.py`
- `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md` (additive section)
- `.gitignore` (+ `tmp/phase6b-approval-review/`)
- `scripts/dev/README.md` (one index entry)

## 4. Command design

```
bash scripts/dev/run_phase6b_approval_review_packet.sh <product_id> <week>
```

Two args; validate `product_id` `^[a-z0-9-]+$` and `week` `^[0-9]{4}-W[0-9]{2}$`;
derive repo root and `cd "$REPO_ROOT"`; reject `ENABLE_AUTOPUBLISH`,
`ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`, `APPROVE_DECISION`,
`APPROVE_FINALIZE`; select `.venv/bin/python` -> `python3` -> `python`; exec the
builder. Prints `review_packet_json:`, `review_packet_md:`, `phase6b_status:`.

## 5. Data sources and read policy

- Phase 2E score JSON: parse, whitelist `score_decision`,
  `product_opportunity_score`, `confidence_score`, `missing_signal_count` only.
- Phase 2J governance summary: read frontmatter, whitelist `compliance_gate_status`,
  `promoted_status`, `decision_status`, `finalization_status`; never
  `next_allowed_action`.
- Phase 4D/4E/5C/5D JSON summaries: parse, whitelist status/verdict fields.
- Phase 2E report, Phase 2F summary, Phase 3A dashboard, Phase 3B portfolio:
  existence/sha256/size only — never ingest body.
- Never read the vault, raw score body beyond whitelist, raw markdown bodies, or
  raw HTML.

## 6. Evidence model

Aggregate only whitelisted scalars plus per-source `{name, path, present, bytes,
sha256}`. Missing sources are `present: false` and do not fail the command.
`compliance_status` derives from Phase 2J `compliance_gate_status` else
`not_evaluated`; `approved` is never inferred. Operator and approval reason are
placeholders; timestamp is ISO-8601 UTC.

## 7. Gate-readiness logic

Assessment only — not permission to mutate.

- `promote_gate_ready`: score JSON present, score evidence complete, no verifier
  status is `failed`.
- `decision_gate_ready`: `promote_gate_ready` and Phase 2J summary present.
- `finalization_gate_ready`: `decision_gate_ready` and
  `compliance_status == "approved"`.

## 8. Guardrails

- output only under `tmp/phase6b-approval-review/` (guarded dir)
- strict field whitelisting; output self-safety scan rejects external URLs,
  `file://`, operator path, `vault/`, `input_path`, `note_refs`,
  `next_allowed_action`, approval execution strings, affiliate/secret markers,
  and script/JS markup before writing
- wrapper rejects approval flags; dry-run only
- read-only: no vault, no network, no primitive execution; `dry_run: true`
- self-reference: denylist literals composed so the source carries no contiguous
  operator-path or approval execution literal

## 9. Output structure

`tmp/phase6b-approval-review/review-<product_id>-<week>.json` (type, product_id,
report_week, generated_at, score, compliance_status, verifier, governance,
sources[], operator, approval_reason, gates{3 booleans}, dry_run, statement) and
`...review-<product_id>-<week>.md` (readable mirror with evidence table, source
table, gate-readiness, dry-run statement, guardrail footer).

## 10. Test strategy

Deterministic pytest: existence/exec/`bash -n`/`py_compile`/`.gitignore`;
invalid product_id/week/arg-count; guardrail + approval flags; end-to-end after
the Phase 5D chain; JSON content; leakage guard; no vault write/read; gate logic;
missing-source degrade; cross-CWD; CI-C alignment; static boundary; docs update.

## 11. Acceptance criteria

- `run_phase6b_approval_review_packet.sh prod-laptop-stand 2026-W26` exits 0,
  prints the three status lines, and writes both outputs with `dry_run: true`.
- Outputs leak no operator path, vault path, `input_path`, `note_refs`,
  `next_allowed_action`, approval execution string, URL, or secret.
- Focused Phase 6B, Phase 6A, Phase 5D, and CI-C tests pass; full suite passes.
- No vault write; no approval primitive execution; no hardcoded operator path.

## 12. Verification commands

```
bash -n scripts/dev/run_phase6b_approval_review_packet.sh
python -m py_compile scripts/dev/build_approval_review_packet.py
python -m pytest -q tests/test_phase6b_dry_run_approval_review_packet.py
python -m pytest -q tests/test_phase6a_manual_approved_workflow_boundary.py tests/test_phase5d_ui_shell_demo_command.py tests/test_ci_c_runner_regression_guards.py
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
bash scripts/dev/run_phase6b_approval_review_packet.sh prod-laptop-stand 2026-W26
env -u AFFILIATE_REQUIRE_OPERATOR_RUNTIME python -m pytest -q
grep -RInE "/home/[^/]+/Affiliate-Ai" scripts/ || echo "scripts clean"
```

## 13. Known limitations

- Evidence packet only; it approves nothing and authorizes no mutation.
- `compliance_status` is a placeholder unless a whitelisted source provides an
  approved value; finalization readiness stays false otherwise.
- Operator identity is a placeholder; no authentication exists.

## 14. Final status target

`phase6b_status: success`
