# Operator Acceptance Pack

## 1. Purpose

The acceptance pack is a deterministic, read-only proof that another operator
can run to verify the Affiliate Product Intelligence OS behaves safely. It
exercises the full safe operator path in one command and confirms that no
business memory (vault) was written.

## 2. What the acceptance wrapper proves

`scripts/dev/run_phase3d_acceptance.sh` proves that, routing **only** through
the operator entrypoint `scripts/dev/command_center.sh`:

- `doctor` reports a healthy, guardrail-safe runtime.
- The safe Phase 2E/2F/2J dry-run chain completes (`final_status: success`).
- The single-product Phase 3A dashboard renders and writes a tmp artifact.
- The multi-product Phase 3B portfolio dashboard renders and writes a tmp artifact.
- All six expected tmp artifacts exist after the run.
- The run wrote **nothing** to `vault/products` or `vault/decisions`
  (before/after snapshot diff is zero).

It does **not** route to the approved Phase 2G/2H/2I vault-writing workflows.

## 3. Run with defaults

```
bash scripts/dev/run_phase3d_acceptance.sh
```

Defaults: csv `vault/samples/import/product-candidates.csv`, week `2026-W26`,
product_id `prod-laptop-stand`.

## 4. Run with override args

```
bash scripts/dev/run_phase3d_acceptance.sh <csv_path> <week> <product_id>
```

Either 0 args or exactly 3 args are accepted. Example:

```
bash scripts/dev/run_phase3d_acceptance.sh vault/samples/import/product-candidates.csv 2026-W26 prod-laptop-stand
```

## 5. Expected success output

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

## 6. Expected generated tmp artifacts

- `tmp/phase2e-import-score-report/scores/<product_id>.json`
- `tmp/phase2e-import-score-report/weekly-report-<week>.md`
- `tmp/phase2f-hermes/operational-summary-<week>.md`
- `tmp/phase2j-hermes-governance/governance-summary-<week>.md`
- `tmp/phase3a-dashboard/dashboard-<product_id>-<week>.md`
- `tmp/phase3b-portfolio-dashboard/portfolio-<week>.md`

All live under `tmp/` and are gitignored.

## 7. Vault safety guarantee (before/after diff)

The wrapper counts the files in the vault product and decision directories
**before** and **after** the run and requires the counts to be identical. It
does not assert the vault is empty, because a real vault may legitimately
contain files from prior approved operations. A non-zero diff fails acceptance.
Vault paths are never printed; only `vault_products_writes` and
`vault_decisions_writes` count labels are emitted.

## 8. Guardrails

- no database
- no FastAPI
- no UI
- no external APIs
- no affiliate content generation
- no autopublish
- no campaign launch
- no vault writes
- no approved Phase 2G/2H/2I routing

## 9. Troubleshooting

- **doctor gate fails**: an unsafe env flag is set
  (`ENABLE_AUTOPUBLISH`, `ENABLE_OPENAI_API_DIRECT`, `APPROVE_PROMOTE`,
  `APPROVE_DECISION`, or `APPROVE_FINALIZE` set to `true`). Unset it and re-run.
- **csv file missing**: the csv_path does not exist; pass a valid sample CSV.
- **invalid week**: week must match `^[0-9]{4}-W[0-9]{2}$` (e.g. `2026-W26`).
- **invalid product_id**: product_id must match `^[a-z0-9-]+$`.
- **missing expected artifact**: a downstream step did not produce its tmp
  output; inspect the failed step's redacted output on stderr.
- **vault diff detected**: a vault product/decision file count changed during
  the run; stop and investigate — the acceptance path must never write the vault.

## 10. Known limitations

- The `dry-run` step executes the real Phase 2E/2F/2J chain (tmp-only); it takes
  a few seconds and overwrites existing tmp artifacts.
- Determinism depends on the default sample CSV importing `prod-laptop-stand`;
  override args must reference a product_id that the CSV actually scores.
- The vault diff uses file counts, not content hashes; an equal-count
  replace-in-place within a single run would not be detected (the safe path
  performs no vault writes at all, so this is theoretical).
- `status`/`doctor` counts reflect the current tmp state and are not week-scoped.
