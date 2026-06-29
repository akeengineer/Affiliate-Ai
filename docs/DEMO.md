# Operator Demo Script

## 1. Demo objective

Show, in a few minutes, that the Affiliate Product Intelligence OS provides a
single safe operator entrypoint that scores products, summarizes them, and
proves it does so **without** writing business memory (vault) or touching any
approved launch workflow.

## 2. Demo prep

```
cd /home/ubuntu/Affiliate-Ai
source .venv/bin/activate    # optional; only needed if you also run pytest
```

No other setup is required. The demo reads the committed sample CSV and writes
only to gitignored `tmp/` artifacts.

## 3. Demo flow

### a. Command center help

```
bash scripts/dev/command_center.sh help
```

### b. Command center doctor

```
bash scripts/dev/command_center.sh doctor
```

Expect every `check: ... -> PASS` line and `doctor_status: success`.

### c. Phase 3D acceptance wrapper (the main event)

```
bash scripts/dev/run_phase3d_acceptance.sh
```

Expect four `step: ... -> PASS` lines, six `artifact: ... -> PRESENT` lines,
`vault_products_writes: 0`, `vault_decisions_writes: 0`, and
`acceptance_status: success`.

### d. Inspect the product dashboard

```
bash scripts/dev/command_center.sh product prod-laptop-stand 2026-W26
```

### e. Inspect the portfolio dashboard

```
bash scripts/dev/command_center.sh portfolio 2026-W26 --top 5
```

## 4. Narration script for the operator

1. "Everything goes through one entrypoint — `command_center.sh`. Here is its help."
2. "First, `doctor`. It checks the required scripts and that no unsafe flags are
   enabled. All green."
3. "Now the acceptance pack. One command drives the whole safe path: doctor, the
   Phase 2E/2F/2J dry-run, the single-product dashboard, and the portfolio
   dashboard — and it verifies the artifacts exist."
4. "Notice `vault_products_writes: 0` and `vault_decisions_writes: 0`. The pack
   compares the vault before and after and proves nothing was written."
5. "Finally we can read the product and portfolio dashboards directly — these are
   read-only views of what was scored."

## 5. Expected outputs

- `doctor`: ten `PASS` checks and `doctor_status: success`.
- `run_phase3d_acceptance.sh`: four PASS steps, six PRESENT artifacts, zero
  vault writes, `acceptance_status: success`.
- `product`: the single-product field block ending in `phase3a_status: success`.
- `portfolio`: portfolio counts and a Top N table ending in `phase3b_status: success`.

## 6. What this demo intentionally does NOT prove

- It does not promote a product, create a decision, or finalize a decision
  (Phase 2G/2H/2I are deliberately not run — they require explicit manual approval
  and would write the vault).
- It does not launch any campaign or generate affiliate content.
- It does not call external APIs, a database, or any UI/API service.
- It does not validate real marketplace data; it uses the sanitized sample CSV.

## 7. Next phase recommendation

After acceptance passes, the next operator-facing step is to exercise the
manual approval gates (Phase 2G promote, Phase 2H decision review, Phase 2I
finalization) in a controlled environment where vault writes are expected and
reviewed — outside the read-only acceptance path proven here.
