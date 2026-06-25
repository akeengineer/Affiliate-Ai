# Agent Operating Model

## Hermes Agent
Main orchestrator. Reads project docs, activates affiliate-growth-os skill, uses enabled Obsidian integration, starts tmux warroom, creates Codex tasks, and records decisions.

## Codex CLI
Implementation engine. Writes code, scripts, tests, docs updates, and GitHub workflow files. Codex must follow `AGENTS.md` and task files under `codex/tasks/`.

## Product Miner Agent
Finds product candidates and marketplace signals.

## Demand Intelligence Agent
Analyzes demand, trend velocity, Google Trends/TikTok/marketplace signals, and weekly momentum.

## Commission Economics Agent
Normalizes commission rate, cap, payout timing, expected value, and rejection/refund risk.

## Content Virality Agent
Evaluates hook strength, demoability, short-video fit, blog fit, and repeatability.

## Compliance Risk Agent
Checks affiliate disclosure, claims, regulated categories, platform policy risk, counterfeit risk, and autopublish restrictions.

## Vote Chairman Agent
Collects agent votes, applies decision thresholds, and writes final decision notes.
