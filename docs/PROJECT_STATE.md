# Project State

Affiliate Product Intelligence OS — current system state as of the Phase 3
release freeze.

## 1. Current architecture

- **Local-first CLI workflow.** All operator actions run as local scripts; there
  is no server process.
- **Obsidian-style vault as file-based business memory.** Markdown notes with
  YAML frontmatter under `vault/` are the only backend/project memory.
- **Deterministic Python scripts and bash wrappers.** Scoring, reporting,
  import, and dashboards are deterministic Python; each is fronted by a bash
  wrapper enforcing guardrails.
- **Hermes dry-run governance proofs.** Hermes orchestration is proven via safe
  dry-runs (Phase 2F/2J) that write tmp artifacts only.
- **GitHub branch/PR/squash workflow.** Engineering control plane; feature
  branches, pull requests, and squash merges.
- **No database.** No relational/NoSQL store; files only.
- **No FastAPI.** No web service layer.
- **No UI.** Operator interaction is CLI text only.

## 2. Current operator commands

```
bash scripts/dev/command_center.sh help
bash scripts/dev/command_center.sh status
bash scripts/dev/command_center.sh doctor
bash scripts/dev/command_center.sh dry-run vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
bash scripts/dev/command_center.sh product prod-laptop-stand 2026-W26
bash scripts/dev/command_center.sh portfolio 2026-W26 --top 5 --write
bash scripts/dev/run_phase3d_acceptance.sh
```

The command center (`help`, `status`, `doctor`, `dry-run`, `product`,
`portfolio`) is the single operator entrypoint. The acceptance pack
(`run_phase3d_acceptance.sh`) drives the safe path end to end.

### Static read-only UI shell demo commands (Phase 4E / 5B-5D)

```
bash scripts/dev/run_phase4e_demo_bundle.sh 2026-W26
bash scripts/dev/run_phase5b_ui_shell.sh 2026-W26
bash scripts/dev/run_phase5c_ui_shell_verifier.sh
bash scripts/dev/run_phase5d_ui_shell_demo.sh 2026-W26
```

These are local, read-only static demo commands; they never write the vault,
call external services, or trigger approved workflows.

## 3. Artifact map

### tmp outputs

Generated, gitignored working outputs:

- `tmp/phase1-smoke/`
- `tmp/phase2c-warroom/`
- `tmp/phase2d-import/`
- `tmp/phase2e-import-score-report/` (`scores/*.json`, `weekly-report-<week>.md`, products)
- `tmp/phase2f-hermes/`
- `tmp/phase2h-decision-review/`
- `tmp/phase2i-decision-finalization/`
- `tmp/phase2j-hermes-governance/`
- `tmp/phase3a-dashboard/`
- `tmp/phase3b-portfolio-dashboard/`
- `tmp/phase4e-demo-bundle/`
- `tmp/phase5b-ui-shell/`
- `tmp/phase5c-ui-shell-verifier/`
- `tmp/phase5d-ui-shell-demo/`

### vault memory outputs

Gitignored business memory areas (Obsidian vault):

- `vault/products`
- `vault/decisions`
- `vault/trends`
- `vault/marketplace-signals`
- `vault/commissions`
- `vault/meetings`
- `vault/contents`
- `vault/compliance`
- `vault/reports`

These are **gitignored business memory areas**. Writes to `vault/products` and
`vault/decisions` require **explicit manual approval gates** (Phase 2G promote,
Phase 2H decision review, Phase 2I finalization, each guarded by an `APPROVE_*`
flag). The default read-only operator path writes none of them.

### docs

- `docs/PROJECT_STATE.md` (this file)
- `docs/RELEASE_SNAPSHOT_PHASE3.md`
- `docs/ROADMAP.md`
- `docs/ACCEPTANCE.md`, `docs/DEMO.md`
- `docs/PHASE2_OPERATING_MANUAL.md`, `docs/PHASE2_GOVERNANCE_FLOW.md`
- `docs/SCORING_SPEC.md`, `docs/WORKFLOW_SPEC.md`, `docs/OBSIDIAN_CONTRACT.md`
- `docs/SECURITY.md`, `docs/GITHUB_WORKFLOW.md`, `docs/RUNBOOK.md`
- `docs/UI_SHELL.md`, `docs/UI_SHELL_BOUNDARY.md`
- `docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md`
- `docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md`
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`
- `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md`
- `docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md`
- `docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`
- `docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md`
- `docs/RELEASE_SNAPSHOT_PHASE6.md`

Phase 6A defines the **manual-approved workflow boundary** in
`docs/MANUAL_APPROVED_WORKFLOW_BOUNDARY.md`: no approval mutation exists in
Phase 6A, no new vault writes are introduced, and no backend/API/database is
introduced. The existing manual-approved primitives remain unchanged; future
Phase 6B+ are separate implementation phases.

Phase 6D defines the **manual approval execution boundary** in
`docs/MANUAL_APPROVAL_EXECUTION_BOUNDARY.md`: no runtime approval command exists
yet, no vault read/write is introduced, and no approval mutation is introduced.
The Phase 2G/2H/2I primitives remain unchanged; a future approval execution
requires the Phase 6B packet and a Phase 6C `ready` verifier verdict.

Phase 6F defines the future **single-gate manual approval wrapper boundary** in
`docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_BOUNDARY.md`: no runtime wrapper exists
yet, no vault read/write is introduced, and no approval mutation is introduced.
The Phase 2G/2H/2I primitives remain unchanged; a future wrapper execution
requires the Phase 6B packet, a Phase 6C `ready` verifier verdict, and a Phase 6E
execution plan, and must be single-gate only.

Phase 6G defines the future **manual approval audit verifier boundary** in
`docs/MANUAL_APPROVAL_AUDIT_VERIFIER_BOUNDARY.md`: no runtime audit verifier
exists yet, no vault read/write is introduced, and no approval mutation is
introduced. The Phase 2G/2H/2I primitives remain unchanged; Phase 6G expects
future audit artifacts to reference the Phase 6B packet, Phase 6C verifier, and
Phase 6E execution plan, and the future audit verifier must be read-only and
evidence-only.

Phase 6A-6G are complete, and Phase 6H updates the release snapshot in
`docs/RELEASE_SNAPSHOT_PHASE6.md`. Phase 6 remains read-only/manual-approved: no
runtime approval wrapper exists yet, no runtime audit verifier exists yet, no
vault read/write is introduced by Phase 6H, and no approval mutation is
introduced. The Phase 2G/2H/2I primitives remain unchanged. The safe read-only
chain is `5D -> 6B -> 6C -> 6E`.

Phase 7A plans the future read-only audit verifier implementation in
`docs/MANUAL_APPROVAL_AUDIT_VERIFIER_IMPLEMENTATION_PLAN.md`. The Phase 2G/2H/2I
primitives remain unchanged, and the verifier must be read-only and
evidence-only.

Phase 7B implements that plan as a runtime read-only audit verifier
(`scripts/dev/verify_manual_approval_audit.py`, wrapped by
`scripts/dev/run_phase7b_audit_verifier.sh`). It validates one JSON audit
artifact and writes reports only under `tmp/phase7b-audit-verifier/`. No approval
wrapper exists yet, no approval mutation exists, no vault read/write is
introduced, and no primitive execution occurs; the Phase 2G/2H/2I primitives
remain unchanged.

Phase 7C plans the future runtime single-gate manual approval wrapper in
`docs/SINGLE_GATE_MANUAL_APPROVAL_WRAPPER_IMPLEMENTATION_PLAN.md`. No runtime
wrapper exists yet, no approval mutation is introduced, and no vault read/write
is introduced. The Phase 2G/2H/2I primitives remain unchanged, the Phase 7B
audit verifier remains read-only/evidence-only, and Phase 7D is the future
high-risk runtime implementation phase.

Phase 7D-R completes the high-risk readiness review in
`docs/HIGH_RISK_SINGLE_GATE_WRAPPER_READINESS_REVIEW.md`. Phase 7D runtime
readiness remains blocked. No runtime wrapper exists yet, no approval mutation is
introduced, and no vault read/write is introduced. The Phase 2G/2H/2I primitives
remain unchanged, the Phase 7B audit verifier remains read-only/evidence-only,
and Phase 7D is the future high-risk runtime implementation phase.

### scripts

- Deterministic core: `score_product.py`, `generate_weekly_report.py`,
  `import_product_candidates.py`, `dashboard_summary.py`,
  `portfolio_dashboard.py`
- Manual-gated (vault-writing) cores: `promote_product_candidates.py`,
  `create_decision.py`, `finalize_decision.py`
- Wrappers: `run_phase2e_*`, `run_phase2f_*`, `run_phase2g_*`, `run_phase2h_*`,
  `run_phase2i_*`, `run_phase2j_*`, `run_phase2_full_dry_run.sh`,
  `run_phase3a_dashboard_summary.sh`, `run_phase3b_portfolio_dashboard.sh`
- Operator: `command_center.sh`, `run_phase3d_acceptance.sh`,
  `show_release_snapshot.sh`
- Static read-only UI shell demo: `run_phase4e_demo_bundle.sh`,
  `run_phase5b_ui_shell.sh`, `run_phase5c_ui_shell_verifier.sh`,
  `run_phase5d_ui_shell_demo.sh`
- Runtime read-only audit verifier: `verify_manual_approval_audit.py`, wrapped by
  `run_phase7b_audit_verifier.sh` (reads one audit artifact; writes only under
  `tmp/phase7b-audit-verifier/`; no vault write, no primitive execution)

## 4. Guardrails

- no database
- no FastAPI
- no UI
- no external APIs
- no affiliate content generation
- no autopublish
- no campaign launch
- no vault writes by default

Note: `no UI` here means no UI framework or interactive server UI; Phase 5
provides a static read-only UI shell only (inline CSS, zero JavaScript).

## 5. What the system can do now

- sanitized CSV import
- scoring
- weekly report
- Hermes operational proof
- governance dry-run proof
- manual-gated promote/decision/finalization
- single-product dashboard
- portfolio dashboard
- command center
- acceptance demo pack
- Phase 4E static demo bundle command
- **static read-only UI shell** (Phase 5B)
- **UI shell verifier** / acceptance gate (Phase 5C)
- **UI shell demo bundle** command (Phase 5D)
- **runtime read-only manual approval audit verifier** (Phase 7B)

## 6. What the system cannot do yet

- no interactive/server UI or frontend framework (a static read-only UI shell exists)
- no API
- no database
- no real marketplace connector
- no content generation
- no autopublish
- no campaign launch
- no automatic approval

## 7. Known limitations

- The scores directory is **not week-partitioned**; all `scores/*.json` are read.
- Phase 3B `--week` is a **label / artifact selector, not a score filter**.
- `status` counts are **snapshots** of the current tmp state.
- The acceptance sample is **tied to `prod-laptop-stand`** (the sample CSV).
- `dry-run` **writes tmp artifacts** (tmp-only; no vault).
- The acceptance **vault diff is count/list based**, not content-hash based.

## 8. Security and compliance posture

- **No secrets committed.** `.env`, keys, tokens, payout data are gitignored.
- **No affiliate links emitted.** Outputs never carry affiliate tracking URLs.
- **Output scrubbers** reject vault paths, affiliate URLs, secrets, and affiliate
  content markers in dashboard/acceptance output.
- **Vault writes are manual-gated** behind explicit `APPROVE_*` flags
  (Phase 2G/2H/2I).
- The **command center does not route to approved Phase 2G/2H/2I workflows**;
  only safe read-only / dry-run paths are reachable from it.

See `docs/SECURITY.md` and `docs/OBSIDIAN_CONTRACT.md` for the full policy.
