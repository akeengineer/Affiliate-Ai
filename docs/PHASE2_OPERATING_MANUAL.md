# Phase 2 Operating Manual / Runbook

Operator-facing runbook for running the Affiliate Product Intelligence OS
Phase 2 governance pipeline end-to-end, safely.

> This is an operations document. It introduces no new behavior. Every command
> below maps to an already-merged, tested workflow.

---

## 1. Purpose of Phase 2

Phase 2 turns raw product candidates into **finalized, human-approved decisions**
through a deterministic, gated pipeline:

```
import (2D) -> score+report (2E) -> promote (2G) -> decide (2H) -> finalize (2I)
```

Phase 2F and Phase 2J are **Hermes orchestration proofs** that prove the chain
can be driven and summarized safely without bypassing any gate.

Phase 2 is a **product intelligence system**, not a content generator. No
affiliate content is produced and nothing is published.

---

## 2. Current capability summary

| Phase | Capability | Writes vault? |
|-------|-----------|---------------|
| 2D | Manual CSV import → product_candidate notes | no (writes target dir) |
| 2E | Import + deterministic score + weekly report | no (tmp only) |
| 2F | Hermes orchestration proof of 2E | no (tmp only) |
| 2G | Approval promote gate → `vault/products/` | only with `APPROVE_PROMOTE=true` |
| 2H | Manual decision review → `vault/decisions/` (draft) | only with `APPROVE_DECISION=true` |
| 2I | Decision finalization gate (draft → complete) | only with `APPROVE_FINALIZE=true` |
| 2J | Hermes governance orchestration proof (dry-run only) | never |

Full automated test suite: **99 tests passing** (before Phase 2K).

---

## 3. Hard guardrails

These are enforced by the scripts and must never be relaxed:

- **no database**
- **no FastAPI**
- **no UI**
- **no external APIs**
- **no affiliate content generation**
- **no autopublish**
- **no campaign launch**
- **no vault writes by default**
- **all vault writes require explicit approval** (`APPROVE_PROMOTE`,
  `APPROVE_DECISION`, `APPROVE_FINALIZE`, or the `--approve` flag)

Two environment flags hard-fail every wrapper when set to `true`:

- `ENABLE_AUTOPUBLISH=true` → blocked
- `ENABLE_OPENAI_API_DIRECT=true` → blocked

Both default to `false`/unset.

---

## 4. Workflow map

```
Phase 2D  manual CSV import
   │  import_product_candidates.py  →  product_candidate notes
   ▼
Phase 2E  import-score-report
   │  run_phase2e_import_score_report.sh  →  tmp/phase2e-import-score-report/
   ▼
Phase 2F  Hermes import-score-report orchestration (proof)
   │  run_phase2f_hermes_orchestration.sh  →  tmp/phase2f-hermes/
   ▼
Phase 2G  approval promote gate
   │  run_phase2g_approval_promote.sh  →  vault/products/ (approved only)
   ▼
Phase 2H  manual decision review
   │  run_phase2h_decision_review.sh  →  vault/decisions/ draft (approved only)
   ▼
Phase 2I  decision finalization gate
   │  run_phase2i_decision_finalization.sh  →  decision draft → complete (approved only)
   ▼
Phase 2J  Hermes governance orchestration proof (dry-run only)
      run_phase2j_governance_orchestration.sh  →  tmp/phase2j-hermes-governance/
```

---

## 5. Exact command examples

All commands run from the repo root with the venv active:

```bash
cd /home/ubuntu/Affiliate-Ai
source .venv/bin/activate
```

### Phase 2D — manual CSV import

```bash
python scripts/dev/import_product_candidates.py \
  --input-csv vault/samples/import/product-candidates.csv \
  --output-dir tmp/phase2d-import \
  --dry-run
```

### Phase 2E — import-score-report

```bash
bash scripts/dev/run_phase2e_import_score_report.sh \
  vault/samples/import/product-candidates.csv 2026-W26
```

### Phase 2F — Hermes import-score-report orchestration

```bash
bash scripts/dev/run_phase2f_hermes_orchestration.sh \
  vault/samples/import/product-candidates.csv 2026-W26
```

### Phase 2G — approval promote gate

```bash
# dry-run (default, no vault write)
bash scripts/dev/run_phase2g_approval_promote.sh \
  tmp/phase2e-import-score-report 2026-W26

# approved (writes vault/products/)
APPROVE_PROMOTE=true bash scripts/dev/run_phase2g_approval_promote.sh \
  tmp/phase2e-import-score-report 2026-W26
```

### Phase 2H — manual decision review

```bash
# dry-run (default, no vault write)
bash scripts/dev/run_phase2h_decision_review.sh \
  prod-laptop-stand small_batch_test 2026-W26

# approved (writes vault/decisions/ as draft)
APPROVE_DECISION=true bash scripts/dev/run_phase2h_decision_review.sh \
  prod-laptop-stand small_batch_test 2026-W26
```

### Phase 2I — decision finalization gate

```bash
# dry-run (default, no vault mutation)
FINALIZATION_REASON="Compliance approved; manual review completed" \
bash scripts/dev/run_phase2i_decision_finalization.sh \
  dec-prod-laptop-stand-2026-W26

# approved (draft → complete, in place)
FINALIZATION_REASON="Compliance approved; manual review completed" \
APPROVE_FINALIZE=true \
bash scripts/dev/run_phase2i_decision_finalization.sh \
  dec-prod-laptop-stand-2026-W26
```

### Phase 2J — Hermes governance orchestration proof (dry-run only)

```bash
bash scripts/dev/run_phase2j_governance_orchestration.sh \
  vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
```

### Full safe dry-run (convenience wrapper, Phase 2K)

```bash
bash scripts/dev/run_phase2_full_dry_run.sh \
  vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
```

---

## 6. Dry-run vs approved mode

| Mode | How to trigger | Vault effect |
|------|----------------|--------------|
| **dry-run** | default — no approval env var / no `--approve` | none; artifacts go to `tmp/` |
| **approved** | explicit `APPROVE_*=true` env var (or `--approve`) | writes/mutates the relevant `vault/` path |

Rules:

- Dry-run is always the default. You must **opt in** to any vault write.
- Approval is per-phase and not sticky — each phase requires its own approval.
- 2J has **no approved mode**; it is dry-run only by design.

---

## 7. Runtime output paths (safe, gitignored)

These hold transient runtime artifacts and are safe to delete anytime:

- `tmp/phase2e-import-score-report/` — imported notes, score JSON, weekly report
- `tmp/phase2f-hermes/` — Hermes operational summary
- `tmp/phase2g-approval-promote/` — promote audit
- `tmp/phase2h-decision-review/` — decision artifact (dry-run) + audit
- `tmp/phase2i-decision-finalization/` — finalization audit
- `tmp/phase2j-hermes-governance/` — governance summary

All `tmp/` subdirectories above are gitignored.

---

## 8. Private vault output paths (business memory)

Written only under explicit approval and **never committed to GitHub**:

- `vault/products/` — promoted, scored product memory (Phase 2G approved)
- `vault/decisions/` — decision memory: draft (Phase 2H) → complete (Phase 2I)

Both are gitignored.

---

## 9. What is safe to commit vs. never commit

**Safe to commit:**

- Scripts under `scripts/dev/`
- Docs under `docs/`
- Task files under `codex/tasks/`
- Tests under `tests/`
- Templates under `vault/templates/` and sanitized samples under `vault/samples/`

**Never commit:**

- `tmp/` (any runtime output)
- `vault/products/`, `vault/decisions/`, and all other private vault dirs
  (`vault/trends/`, `vault/marketplace-signals/`, `vault/commissions/`,
  `vault/meetings/`, `vault/contents/`, `vault/compliance/`, `vault/reports/`)
- `.env`, secrets, affiliate tokens, payout data

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `destination already exists` | target `vault/products/<id>.md` or decision file already present | remove it or use a different `--report-week`; never overwrite blindly |
| `Product note not found` / `decision note not found` | upstream phase not run/approved | run the prior phase in approved mode first |
| `score JSON not found` | Phase 2E not run for that product | re-run Phase 2E; confirm `tmp/phase2e-import-score-report/scores/<id>.json` |
| `compliance_status must be 'approved'` | Phase 2I called on a decision not yet compliance-approved | set `compliance_status: approved` on the decision (via 2H `--compliance-status approved`) before finalizing |
| `ENABLE_AUTOPUBLISH=true is not allowed` | autopublish flag set | unset `ENABLE_AUTOPUBLISH` (must be `false`/unset) |
| `ENABLE_OPENAI_API_DIRECT=true is not allowed` | direct-API flag set | unset `ENABLE_OPENAI_API_DIRECT` (must be `false`/unset) |
| `product-id must match ^[a-z0-9-]+$` / `product_id must match` | invalid/unsafe product id | use lowercase letters, digits, hyphens only (path-traversal guard) |
| `status must be draft to finalize` (already complete) | decision already finalized | this is expected — no re-finalize; do not retry |

---

## 11. Cleanup commands for local runtime artifacts

```bash
# remove all Phase 2 runtime tmp output (safe — gitignored)
rm -rf tmp/phase2e-import-score-report \
       tmp/phase2f-hermes \
       tmp/phase2g-approval-promote \
       tmp/phase2h-decision-review \
       tmp/phase2i-decision-finalization \
       tmp/phase2j-hermes-governance

# remove local test/demo vault artifacts (business memory — only if intended)
rm -f vault/products/prod-laptop-stand.md \
      vault/decisions/dec-prod-laptop-stand-2026-W26.md
```

---

## 12. PR / Git hygiene

- **Always start from clean main:** `git checkout main && git fetch origin && git reset --hard origin/main`.
- **Avoid committing `tmp/`** — it is runtime only.
- **Avoid committing `vault/`** private dirs — business memory stays local.
- **Use explicit `git add` only** — never `git add -A` / `git add .`; add named files so no private data is swept in.
- Run `git status --short` before commit and confirm only intended files appear.

---

## 13. Operator checklist — before running approved commands

- [ ] `ENABLE_AUTOPUBLISH` is unset/false.
- [ ] `ENABLE_OPENAI_API_DIRECT` is unset/false.
- [ ] The dry-run for this phase succeeded first.
- [ ] You reviewed the dry-run audit under `tmp/`.
- [ ] The target vault path does not already exist (no overwrite).
- [ ] For finalize: `compliance_status` is `approved`.
- [ ] You intend to write business memory to `vault/` and accept it stays local.

---

## 14. Operator checklist — before opening a PR

- [ ] Branch started from clean `main`.
- [ ] `git status --short` shows only intended source/doc/test files.
- [ ] No `tmp/` paths staged.
- [ ] No `vault/products/` or `vault/decisions/` paths staged.
- [ ] No secrets, tokens, payout data, or `.env`.
- [ ] `python -m pytest -q` passes.

---

## 15. What Phase 2 does not do yet

- No dashboard or summary CLI (planned: Phase 3A).
- No UI of any kind (planned: Phase 3B read-only, 3C approval panels).
- No marketplace connectors / live data fetch (planned: Phase 4, read-only / manual-approved).
- No affiliate content generation, no campaign launch, no autopublish.
- No automated (LLM-driven) approval — every vault write is a human decision.

See `docs/PHASE2_GOVERNANCE_FLOW.md` for the governance model and future phases.
