# Phase 2C Warroom Proof

You are operating the tmux warroom in deterministic proof mode.

## Proof objective

Show that the warroom opens with the expected panes, prompt targets, task target, and safe instructions while proof artifacts are written only under `tmp/phase2c-warroom/`.

## Read first

- `AGENTS.md`
- `AGENT.md`
- `CONTEXT.md`
- `docs/WORKFLOW_SPEC.md`
- `docs/OBSIDIAN_CONTRACT.md`
- `docs/HERMES_OPERATING_RULES.md`
- `docs/CODEX_IMPLEMENTATION_GUIDE.md`
- `codex/tasks/006-phase2c-warroom-proof.md`

## Proof rules

- Read sanitized samples only from `vault/samples/`.
- Write proof artifacts only to `tmp/phase2c-warroom/`.
- Do not write anywhere under `vault/`.
- Do not touch private vault directories.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not enable autopublish.
- Do not use live marketplace data.

## Expected artifacts

- `tmp/phase2c-warroom/votes/vote-product-miner-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-demand-intelligence-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-commission-economics-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-content-virality-smart-desk-pad.md`
- `tmp/phase2c-warroom/votes/vote-compliance-risk-smart-desk-pad.md`
- `tmp/phase2c-warroom/decisions/decision-smart-desk-pad.md`

## tmux proof notes

- Session name: `affiliate-warroom-phase2c`
- Default session `affiliate-warroom` must remain separate.
- If the proof runs headless, print:
  `tmux attach -t affiliate-warroom-phase2c`
