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
- `docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`
- `docs/RELEASE_SNAPSHOT_PHASE7.md`
- `docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md`
- `docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md`
- `docs/PHASE7H_OPERATOR_RUNBOOK.md`
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

Phase 7D-P finalizes the runtime wrapper implementation blueprint in
`docs/PHASE7D_RUNTIME_WRAPPER_IMPLEMENTATION_BLUEPRINT.md`. Phase 7D runtime
readiness remains blocked, and runtime implementation is still future high-risk
work. No runtime wrapper exists yet. No approval mutation or vault read/write is
introduced. The Phase 2G/2H/2I primitives remain unchanged, and the Phase 7B
audit verifier remains read-only/evidence-only.

Phase 7E records the release snapshot and historical blocked-state context in
`docs/RELEASE_SNAPSHOT_PHASE7.md`.

Phase 7F records the post-Phase-7D runtime live state in
`docs/RELEASE_SNAPSHOT_PHASE7_RUNTIME_LIVE.md`. It is docs/tests/task-only and
does not change runtime behavior, wrapper logic, or approval logic.

Phase 7G provides the safe operator acceptance/demo pack documented in
`docs/PHASE7G_OPERATOR_ACCEPTANCE_DEMO_PACK.md`. The safe demo pack exists for
prevented, blocked, invalid, and static guard observations only. It adds no new
mutation path, and Phase 7D wrapper behavior is unchanged.

Phase 7H provides the hardened operator runbook in
`docs/PHASE7H_OPERATOR_RUNBOOK.md`. The operator runbook exists, adds no new mutation path,
and keeps Phase 7D wrapper behavior unchanged. It is
docs/tests/task-only and introduces no backend/API/database behavior.

Phase 7D runtime implementation is now intentionally present as a manual-gated
single-wrapper boundary:

- shell entrypoint: `scripts/dev/run_phase7d_single_gate_wrapper.sh`
- Python core: `scripts/dev/execute_single_gate_approval.py`
- focused runtime tests: `tests/test_phase7d_single_gate_wrapper.py`
- task record: `codex/tasks/048-phase7d-single-gate-runtime-wrapper.md`

The current runtime status is:

- `phase7d_runtime_readiness: implemented_manual_gate`
- exactly one selected gate per invocation
- evidence-first decision derivation
- safe vault-read supplements only for product/decision note state checks
- wrapper writes audits directly under `tmp/phase7d-single-gate-wrapper/`
- wrapper does not write vault state directly
- selected primitive is the only allowed mutation surface after preconditions pass

The Phase 2G/2H/2I primitives remain unchanged, the Phase 7B audit verifier
remains read-only/evidence-only, and the runtime boundary still forbids
approve-all, global approval, multi-gate execution, next-gate automation, chain
execution, autopublish, backend/API/database behavior, and production
deployment.

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
- Runtime single-gate manual approval wrapper:
  `run_phase7d_single_gate_wrapper.sh` -> `execute_single_gate_approval.py`
  (selected-gate-only; evidence-first; safe vault-read supplements; audit writes
  under `tmp/phase7d-single-gate-wrapper/`; wrapper performs no direct vault
  write)
- Safe operator acceptance/demo pack:
  `run_phase7g_safe_demo_pack.sh` -> `build_phase7g_operator_acceptance_summary.py`
  (non-production tmp inputs; no primitive execution; summaries under
  `tmp/phase7g-operator-acceptance/`)

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
- **safe operator acceptance/demo pack** (Phase 7G)

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

## 9. Phase 8A durable audit store design

Phase 8A adds the durable audit store design in
`docs/PHASE8A_DURABLE_AUDIT_STORE_DESIGN.md`. The durable audit store design
exists; `durable_audit_store_status` is `design_only`. Phase 8A adds no
storage implementation and no database/backend/API. Phase 7D wrapper behavior
is unchanged, `phase7d_runtime_readiness` remains `implemented_manual_gate`,
and audit artifacts remain tmp-local. Phase 8B (local append-only audit store
prototype) is the next recommended phase.

## 10. Phase 8B local append-only audit store prototype

Phase 8B adds the local append-only audit store prototype documented in
`docs/PHASE8B_LOCAL_APPEND_ONLY_AUDIT_STORE.md`. The local append-only audit
store prototype exists: `scripts/dev/ingest_phase8b_audit_record.py` reads one
existing audit artifact and `scripts/dev/run_phase8b_audit_ingest.sh` wraps
it; both write only under `tmp/phase8b-audit-store/`.
`durable_audit_store_status` is now `local_append_only_prototype`. Phase 8B
adds no backend/API/database and makes no Phase 7D wrapper behavior change;
it performs no primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8C
(verifier/reporting over JSONL) is the next recommended phase.

## 11. Phase 8C audit store verifier / reporting over JSONL

Phase 8C adds the read-only JSONL verifier/reporting documented in
`docs/PHASE8C_AUDIT_STORE_VERIFIER_REPORTING.md`. The JSONL verifier/reporting
exists: `scripts/dev/verify_phase8c_audit_store.py` reads the Phase 8B
`audit-records.jsonl` store read-only and `scripts/dev/run_phase8c_audit_report.sh`
wraps it; both write only under `tmp/phase8c-audit-report/`.
`durable_audit_store_status` is now `jsonl_verifier_reporting`. Phase 8C adds
no backend/API/database and makes no Phase 7D wrapper behavior change; it
performs no primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8D
(query CLI or optional SQLite index design) is the next recommended phase.

## 12. Phase 8D audit store query CLI over JSONL

Phase 8D adds the read-only JSONL query CLI documented in
`docs/PHASE8D_AUDIT_STORE_QUERY_CLI.md`. The JSONL query CLI exists:
`scripts/dev/query_phase8d_audit_store.py` reads the Phase 8B
`audit-records.jsonl` store read-only and
`scripts/dev/run_phase8d_audit_query.sh` wraps it; both write only under
`tmp/phase8d-audit-query/`. `durable_audit_store_status` is now
`jsonl_query_cli`. Phase 8D adds no backend/API/database and makes no Phase
7D wrapper behavior change, no Phase 8B ingest behavior change, and no Phase
8C verifier behavior change; it performs no primitive execution and no vault
read/write. `phase7d_runtime_readiness` remains `implemented_manual_gate`.
Phase 8E (optional SQLite index design or an audit export pack) is the next
recommended phase.

## 13. Phase 8E audit export pack

Phase 8E adds the read-only audit export pack documented in
`docs/PHASE8E_AUDIT_EXPORT_PACK.md`. The audit export pack exists:
`scripts/dev/build_phase8e_audit_export_pack.py` reads the Phase 8B JSONL
store and the optional Phase 8C/8D reports read-only and
`scripts/dev/run_phase8e_audit_export.sh` wraps it; both write only under
`tmp/phase8e-audit-export/`. `durable_audit_store_status` is now
`export_pack`. Phase 8E adds no backend/API/database and makes no Phase 7D
wrapper behavior change, no Phase 8B ingest behavior change, no Phase 8C
verifier behavior change, and no Phase 8D query behavior change; it performs
no primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8F
(export integrity/signing design or an optional SQLite index design) is the
next recommended phase.

## 14. Phase 8F export integrity / signing design

Phase 8F adds the export integrity/signing design documented in
`docs/PHASE8F_EXPORT_INTEGRITY_SIGNING_DESIGN.md`. The export integrity/
signing design exists; `signing_implementation_status` is `design_only`.
Phase 8F adds no signing implementation and no database/backend/API. Phase
7D wrapper behavior is unchanged, `phase7d_runtime_readiness` remains
`implemented_manual_gate`, and `durable_audit_store_status` is now
`export_integrity_signing_design`. Phase 8G (Export Integrity Verifier
Prototype) is the next recommended phase.

## 15. Phase 8G export integrity verifier

Phase 8G adds the local hash-only export integrity verifier documented in
`docs/PHASE8G_EXPORT_INTEGRITY_VERIFIER.md`. The export integrity verifier
exists: `scripts/dev/verify_phase8g_export_integrity.py` reads a Phase 8E
export manifest read-only and `scripts/dev/run_phase8g_export_integrity.sh`
wraps it; both write only under `tmp/phase8g-export-integrity/`.
`durable_audit_store_status` is now `export_integrity_verifier`, and
`signing_implementation_status` remains `not_implemented`. Phase 8G adds no
signing implementation, no key generation, and no database/backend/API; it
makes no Phase 8E export behavior change and no Phase 7D wrapper behavior
change; it performs no primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8H
(Detached Signature Design Finalization, or Export Integrity Verifier
Hardening) is the next recommended phase.

## 16. Phase 8H export integrity verifier hardening

Phase 8H hardens the export integrity verifier documented in
`docs/PHASE8H_EXPORT_INTEGRITY_VERIFIER_HARDENING.md`. The export integrity
verifier is now hardened: `scripts/dev/verify_phase8g_export_integrity.py`
adds a stable report schema, an issue taxonomy, severity, incident
classification, reviewer action mapping, and a Phase 8E manifest
compatibility matrix, while keeping its existing CLI shape and output paths
under `tmp/phase8g-export-integrity/`. `durable_audit_store_status` is now
`export_integrity_verifier_hardened`, and `signing_implementation_status`
remains `not_implemented`. Phase 8H adds no signing implementation, no key
generation, and no database/backend/API; it makes no Phase 8E export
behavior change and no Phase 7D wrapper behavior change; it performs no
primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8I
(Detached Signature Design Finalization) is the next recommended phase.

## 17. Phase 8I detached signature design finalization

Phase 8I finalizes the detached signature design documented in
`docs/PHASE8I_DETACHED_SIGNATURE_DESIGN_FINALIZATION.md`. The detached
signature design is finalized: `durable_audit_store_status` is now
`detached_signature_design_finalized`, `signing_implementation_status`
remains `design_only`, and `signature_runtime_status` is
`not_implemented`. Phase 8I adds no signing implementation, no signature
verifier, no key generation, and no database/backend/API; it makes no
Phase 8G/8H verifier behavior change, no Phase 8E export behavior change,
and no Phase 7D wrapper behavior change; it performs no primitive
execution and no vault read/write. `phase7d_runtime_readiness` remains
`implemented_manual_gate`. Phase 8J (Detached Signature Verifier Design) is
the next recommended phase.

## 18. Phase 8J detached signature verifier design

Phase 8J designs the detached signature verifier flow documented in
`docs/PHASE8J_DETACHED_SIGNATURE_VERIFIER_DESIGN.md`. The detached
signature verifier design now exists: `durable_audit_store_status` is now
`detached_signature_verifier_design`, `signing_implementation_status`
remains `design_only`, `signature_runtime_status` remains
`not_implemented`, and `signature_verifier_runtime_status` is
`not_implemented`. `major_phase_branch_workflow` is `enabled`. Phase 8J
adds no signature verifier implementation, no signing implementation, no
key generation, and no database/backend/API; it makes no Phase 8G/8H
verifier behavior change, no Phase 8E export behavior change, and no
Phase 7D wrapper behavior change; it performs no primitive execution and
no vault read/write. `phase7d_runtime_readiness` remains
`implemented_manual_gate`. Phase 8K (Key Management Design) is the next
recommended phase.

## 19. Phase 8K key management design

Phase 8K designs key management governance documented in
`docs/PHASE8K_KEY_MANAGEMENT_DESIGN.md`. The key management design now
exists: `durable_audit_store_status` is now `key_management_design`,
`signing_implementation_status` remains `design_only`,
`signature_runtime_status` remains `not_implemented`,
`signature_verifier_runtime_status` remains `not_implemented`, and
`key_management_runtime_status` is `not_implemented`.
`major_phase_branch_workflow` is `enabled`. Phase 8K adds no key
management implementation, no key generation, no signing implementation,
and no database/backend/API; it makes no Phase 7D wrapper behavior
change; it performs no primitive execution and no vault read/write.
`phase7d_runtime_readiness` remains `implemented_manual_gate`. Phase 8L
(Local Detached Signature Prototype) is the next recommended phase.
