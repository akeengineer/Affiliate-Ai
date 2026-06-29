# Task 018 - Phase 3D Operator Acceptance Pack

## Objective

Provide a deterministic acceptance/demo pack that another operator can run to
verify the system safely. It drives the operator entrypoint
(`command_center.sh`) end to end, checks the expected tmp artifacts, and proves
the run wrote nothing to the vault.

## Design decisions (confirmed)

- One-shot phase proof wrapper: `scripts/dev/run_phase3d_acceptance.sh`
  (uses the `run_phase3d_` prefix).
- Routes through `scripts/dev/command_center.sh` ONLY; never calls downstream
  wrappers directly and never routes to approved Phase 2G/2H/2I workflows.
- Print-only; no new Phase 3D artifact, no new tmp directory, no `.gitignore`
  change.
- Vault safety via before/after snapshot diff (not assert-empty), so a real
  vault with prior approved files does not cause a false failure.
- Never emits private vault slash paths; uses `vault_products_writes` /
  `vault_decisions_writes` labels.

## Read first

- AGENTS.md
- CONTEXT.md
- scripts/dev/command_center.sh
- docs/ACCEPTANCE.md
- docs/DEMO.md

## Scope

Create:

- `codex/tasks/018-phase3d-operator-acceptance-pack.md`
- `scripts/dev/run_phase3d_acceptance.sh`
- `docs/ACCEPTANCE.md`
- `docs/DEMO.md`
- `tests/test_phase3d_operator_acceptance_pack.py`

Update:

- `scripts/dev/README.md` (script index entry)

Do not modify `.gitignore`, Phase 2, Phase 3A, Phase 3B, or Phase 3C workflows
unless a real bug is found.

## Command

```
bash scripts/dev/run_phase3d_acceptance.sh
bash scripts/dev/run_phase3d_acceptance.sh <csv_path> <week> <product_id>
```

Accepts 0 args (deterministic defaults: `vault/samples/import/product-candidates.csv`,
`2026-W26`, `prod-laptop-stand`) or exactly 3 args. 1 or 2 args fail non-zero.

## Acceptance flow

1. Validate args (`week` `^[0-9]{4}-W[0-9]{2}$`, `product_id` `^[a-z0-9-]+$`,
   csv must exist).
2. Capture before snapshot of vault product/decision file counts.
3. `command_center.sh doctor` → require `doctor_status: success`.
4. `command_center.sh dry-run <csv> <week> <product_id>` → require `final_status: success`.
5. `command_center.sh product <product_id> <week> --write` → require `phase3a_status: success`.
6. `command_center.sh portfolio <week> --top 5 --write` → require `phase3b_status: success`.
7. Verify the six expected tmp artifacts exist.
8. Capture after snapshot; require before == after.
9. Print `acceptance_status: success`; any failure prints `acceptance_status: failed`
   and exits non-zero.

## Guardrails

- No database, FastAPI, UI, external APIs, affiliate content, autopublish,
  campaign launch, or vault writes.
- Route via `command_center.sh` only; never 2G/2H/2I or approved scripts.

## Tests

`tests/test_phase3d_operator_acceptance_pack.py` covers existence/executability,
docs presence, happy path (exit 0, four PASS lines, six artifacts, vault diff
zero), guardrail-flag failures, arg validation, static safety checks (only
command_center is referenced), no vault slash paths in output, and that the docs
mention the guardrails and the before/after diff model.
