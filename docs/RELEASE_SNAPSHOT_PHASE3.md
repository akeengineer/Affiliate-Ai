# Release Snapshot — Phase 3

## 1. Release objective

Freeze and document the operator-facing release: a deterministic, local-first,
read-only CLI that imports and scores sanitized product candidates, summarizes
them per product and across the portfolio, and proves safe operation without
writing business memory — all behind a single operator entrypoint.

## 2. Phase completion matrix (Phase 1 → Phase 3D)

| Phase | Scope | Task file | Proof / wrapper | Status |
| --- | --- | --- | --- | --- |
| Phase 1 | Bootstrap scoring + smoke | 001 | `run_phase1_smoke.sh` | ✅ |
| Phase 2A | Sample workflow | 004 | sample vault workflow | ✅ |
| Phase 2B | Hermes operational test | 005 | `check_hermes_runtime.sh` | ✅ |
| Phase 2C | Warroom proof | 006 | `run_phase2c_warroom_proof.sh` | ✅ |
| Phase 2D | Manual import | 007 | `import_product_candidates.py` | ✅ |
| Phase 2E | Import → score → report | 008 | `run_phase2e_import_score_report.sh` | ✅ |
| Phase 2F | Hermes import/score orchestration | 009 | `run_phase2f_hermes_orchestration.sh` | ✅ |
| Phase 2G | Approval promote gate | 010 | `run_phase2g_approval_promote.sh` | ✅ |
| Phase 2H | Manual decision review | 011 | `run_phase2h_decision_review.sh` | ✅ |
| Phase 2I | Decision finalization gate | 012 | `run_phase2i_decision_finalization.sh` | ✅ |
| Phase 2J | Hermes governance orchestration | 013 | `run_phase2j_governance_orchestration.sh` | ✅ |
| Phase 2K | Operating manual | 014 | `docs/PHASE2_OPERATING_MANUAL.md` | ✅ |
| Phase 3A | Single-product CLI dashboard | 015 | `run_phase3a_dashboard_summary.sh` | ✅ |
| Phase 3B | Portfolio CLI dashboard | 016 | `run_phase3b_portfolio_dashboard.sh` | ✅ |
| Phase 3C | Operator command center | 017 | `command_center.sh` | ✅ |
| Phase 3D | Operator acceptance pack | 018 | `run_phase3d_acceptance.sh` | ✅ |

Task files 001 and 004 through 018 carry the per-phase scope and acceptance.

## 3. Operator commands summary

```
bash scripts/dev/command_center.sh help
bash scripts/dev/command_center.sh status
bash scripts/dev/command_center.sh doctor
bash scripts/dev/command_center.sh dry-run vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
bash scripts/dev/command_center.sh product prod-laptop-stand 2026-W26
bash scripts/dev/command_center.sh portfolio 2026-W26 --top 5 --write
bash scripts/dev/run_phase3d_acceptance.sh
```

## 4. Acceptance command

```
bash scripts/dev/run_phase3d_acceptance.sh
```

## 5. Expected acceptance output

```
step: doctor -> PASS
step: dry-run -> PASS
step: product --write -> PASS
step: portfolio --top 5 --write -> PASS
artifact: tmp/phase2e-import-score-report/scores/prod-laptop-stand.json -> PRESENT
artifact: tmp/phase2e-import-score-report/weekly-report-2026-W26.md -> PRESENT
artifact: tmp/phase2f-hermes/operational-summary-2026-W26.md -> PRESENT
artifact: tmp/phase2j-hermes-governance/governance-summary-2026-W26.md -> PRESENT
artifact: tmp/phase3a-dashboard/dashboard-prod-laptop-stand-2026-W26.md -> PRESENT
artifact: tmp/phase3b-portfolio-dashboard/portfolio-2026-W26.md -> PRESENT
vault_products_writes: 0
vault_decisions_writes: 0
acceptance_status: success
```

## 6. Demo checklist

See `docs/DEMO.md` for narration. Quick checklist:

1. `bash scripts/dev/command_center.sh help`
2. `bash scripts/dev/command_center.sh doctor` → `doctor_status: success`
3. `bash scripts/dev/run_phase3d_acceptance.sh` → `acceptance_status: success`
4. `bash scripts/dev/command_center.sh product prod-laptop-stand 2026-W26`
5. `bash scripts/dev/command_center.sh portfolio 2026-W26 --top 5`

## 7. Production-readiness gaps

- no persistence layer beyond files
- no UI
- no auth
- no observability system
- no marketplace connectors
- no CI acceptance gate yet
- manual approvals remain CLI-driven

## 8. Test posture

Run the full suite:

```
python -m pytest -q
```

The suite is expected to pass cleanly. This document intentionally does **not**
hardcode a specific test count, to avoid brittle drift; run pytest for the
current authoritative result.
