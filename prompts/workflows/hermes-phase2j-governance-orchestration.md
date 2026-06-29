# Hermes Phase 2J — Governance Orchestration Proof

## Activation

Activate the `affiliate-growth-os` skill before proceeding.

## Read first

Read these project source-of-truth files before any action:

1. CONTEXT.md
2. AGENT.md
3. AGENTS.md
4. docs/HERMES_OPERATING_RULES.md
5. docs/WORKFLOW_SPEC.md
6. docs/OBSIDIAN_CONTRACT.md
7. hermes/skills/affiliate-growth-os/SKILL.md

## Objective

Prove Hermes can safely orchestrate and summarize the governance chain
`Phase 2E -> Phase 2G -> Phase 2H -> Phase 2I` in a single safe dry-run.

- Live execution: Phase 2E (tmp-only) and Phase 2G dry-run.
- Static verification: Phase 2H and Phase 2I scripts + wrappers.
- No vault writes. No approved simulation.

## Guardrail checks — verify before running

Assert all of the following before proceeding:

- [ ] `ENABLE_AUTOPUBLISH` is `false` or unset.
- [ ] `ENABLE_OPENAI_API_DIRECT` is `false` or unset.
- [ ] `scripts/dev/run_phase2e_import_score_report.sh` exists and is executable.
- [ ] `scripts/dev/promote_product_candidates.py` exists.
- [ ] `scripts/dev/create_decision.py` exists.
- [ ] `scripts/dev/finalize_decision.py` exists.
- [ ] `scripts/dev/run_phase2g_approval_promote.sh` exists and is executable.
- [ ] `scripts/dev/run_phase2h_decision_review.sh` exists and is executable.
- [ ] `scripts/dev/run_phase2i_decision_finalization.sh` exists and is executable.
- [ ] `codex/tasks/013-phase2j-hermes-governance-orchestration.md` exists.
- [ ] Working directory is `/home/ubuntu/Affiliate-Ai`.

If any guardrail fails, stop and report the failure. Do not proceed.

## Command to run

```bash
bash scripts/dev/run_phase2j_governance_orchestration.sh <input-csv> <report-week> <product-id>
```

Example:

```bash
bash scripts/dev/run_phase2j_governance_orchestration.sh \
  vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
```

## Orchestration steps

1. Run Phase 2E live (writes only to `tmp/phase2e-import-score-report/`).
2. Read the scored JSON for the target `product-id` to obtain `score_decision`.
3. Run Phase 2G via its wrapper in dry-run (no `APPROVE_PROMOTE`) — no vault write.
4. Statically verify Phase 2H and Phase 2I scripts + wrappers exist. Do NOT run them.
5. Write the sanitized governance summary to
   `tmp/phase2j-hermes-governance/governance-summary-<week>.md`.

## Output — governance summary rules

The summary must:

- Include YAML frontmatter with `type: hermes_governance_summary`.
- Include `report_week`, `mode: dry_run`, `product_id`, `score_decision`,
  `promoted_status`, `decision_status`, `finalization_status`,
  `compliance_gate_status`, `next_allowed_action`.
- Include a blocked-risks section describing the approval gates that halt progression.
- Reference only relative `tmp/` paths.
- NOT reference private vault paths:
  - vault/products
  - vault/trends
  - vault/marketplace-signals
  - vault/commissions
  - vault/meetings
  - vault/decisions
  - vault/contents
  - vault/compliance
  - vault/reports
  - vault/.obsidian
- NOT include affiliate content text or campaign copy.
- NOT include external API URLs.

## Hard stops — Hermes must NOT

- Write to any private vault directory.
- Execute Phase 2H or Phase 2I.
- Call external APIs.
- Generate affiliate content or campaign copy.
- Launch a campaign or enable autopublish.
- Ask Codex to implement new features.

## Output format — Hermes report

Produce a final report with:

1. Objective
2. Guardrails verified
3. Governance chain status (product_id, score_decision, promoted/decision/finalization/compliance statuses)
4. Governance summary path written
5. Status: `success` or `blocked` (with reason)
