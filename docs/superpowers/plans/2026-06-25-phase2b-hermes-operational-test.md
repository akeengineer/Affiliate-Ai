# Phase 2B Hermes Operational Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove Hermes can operate Affiliate Product Intelligence OS safely by reading the project source of truth, using the enabled Obsidian integration, running the existing sanitized smoke workflow, and writing only sanitized Markdown output.

**Architecture:** Keep Phase 2B as a thin operational harness around the existing Phase 2A smoke workflow. Add one Hermes-facing prompt file, one deterministic runtime check script, one task file for Codex governance, and one ignored runtime output directory under `tmp/phase2b-hermes/`. Do not add product logic, content generation, or private vault writes.

**Tech Stack:** Bash, Markdown, Hermes CLI/runtime, existing Python scripts, git, tmux-free local verification

---

### Task 1: Define the Codex task and Hermes workflow prompt

**Files:**
- Create: `codex/tasks/005-phase2b-hermes-operational-test.md`
- Create: `prompts/workflows/hermes-phase2b-operational-test.md`

- [ ] **Step 1: Write the task file**

Create a task file that pins scope to runtime verification only:

```md
# Task 005 — Phase 2B Hermes Operational Test

## Objective

Verify Hermes can operate this project safely using the existing deterministic smoke workflow and sanitized output only.

## Read first

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/HERMES_OPERATING_RULES.md
- docs/OBSIDIAN_CONTRACT.md
- docs/WORKFLOW_SPEC.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md
- scripts/dev/run_phase1_smoke.sh
- hermes/skills/affiliate-growth-os/SKILL.md

## Scope

Create:

- `prompts/workflows/hermes-phase2b-operational-test.md`
- `scripts/dev/check_hermes_runtime.sh`

Update if needed:

- `.gitignore`

## Requirements

- Hermes must use `affiliate-growth-os`.
- Hermes must treat Obsidian as the only backend/project memory.
- Hermes must read the source-of-truth docs before acting.
- Hermes may run or request `scripts/dev/run_phase1_smoke.sh`.
- Hermes output must be sanitized Markdown only.
- Output path must be `tmp/phase2b-hermes/hermes-operational-summary.md`.
- No private vault writes.
- No external APIs.
- No content generation.
- No autopublish.
- No Codex implementation request unless explicitly asked.
```

- [ ] **Step 2: Write the Hermes prompt file**

Create a single prompt that Hermes can run directly:

```md
# Phase 2B Hermes Operational Test

## Objective

Prove Hermes can operate Affiliate Product Intelligence OS safely in a sanitized local-only test.

## Required setup

- Activate `affiliate-growth-os`.
- Use Obsidian as the only backend/project memory.
- Respect `ENABLE_AUTOPUBLISH=false`.
- Do not call external APIs.
- Do not generate affiliate content.
- Do not ask Codex to implement anything.

## Source of truth

Read these files before acting:

1. `CONTEXT.md`
2. `AGENT.md`
3. `AGENTS.md`
4. `docs/HERMES_OPERATING_RULES.md`
5. `docs/OBSIDIAN_CONTRACT.md`
6. `docs/WORKFLOW_SPEC.md`
7. `docs/CODEX_IMPLEMENTATION_GUIDE.md`
8. `hermes/skills/affiliate-growth-os/SKILL.md`

## Allowed actions

1. Read the files above.
2. Confirm Obsidian integration is enabled.
3. Run or instruct `scripts/dev/check_hermes_runtime.sh`.
4. Run or instruct `scripts/dev/run_phase1_smoke.sh`.
5. Write one sanitized Markdown summary file to `tmp/phase2b-hermes/hermes-operational-summary.md`.

## Forbidden actions

- Do not write to `vault/products/`
- Do not write to `vault/meetings/`
- Do not write to `vault/decisions/`
- Do not write to `vault/reports/`
- Do not write to `vault/contents/`
- Do not write to `vault/compliance/`
- Do not generate affiliate content
- Do not call external APIs
- Do not enable autopublish
- Do not create a Codex task for implementation unless the user explicitly asks

## Required output file

Write exactly one sanitized Markdown file to:

`tmp/phase2b-hermes/hermes-operational-summary.md`

Required frontmatter:

```yaml
type: weekly_report
report_id: hermes-operational-test
report_week:
generated_at:
candidate_count:
launch_count:
small_batch_test_count:
watchlist_count:
reject_count:
created_at:
updated_at:
status: generated
source_root: vault/samples
```

## Required body sections

1. Objective
2. Inputs Read
3. Runtime Checks
4. Smoke Workflow Result
5. Obsidian Usage Confirmation
6. Safety Constraints Confirmed
7. Risks and Limitations
8. Final Status
```

- [ ] **Step 3: Sanity-check the prompt file**

Run: `sed -n '1,240p' prompts/workflows/hermes-phase2b-operational-test.md`

Expected: The file names the allowed actions, forbidden actions, and output path exactly once each.

- [ ] **Step 4: Commit**

```bash
git add codex/tasks/005-phase2b-hermes-operational-test.md prompts/workflows/hermes-phase2b-operational-test.md
git commit -m "docs: add phase 2b hermes operational test plan"
```

### Task 2: Add deterministic Hermes runtime checks

**Files:**
- Create: `scripts/dev/check_hermes_runtime.sh`
- Modify: `.gitignore`

- [ ] **Step 1: Write the failing runtime check expectation**

Document the command that will be used during implementation:

```bash
bash scripts/dev/check_hermes_runtime.sh
```

Expected before implementation: `No such file or directory`

- [ ] **Step 2: Implement the runtime check script**

Create the script with these checks only:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/home/ubuntu/Affiliate-Ai"
EXPECTED_REMOTE_PRIMARY="git@github.com:akeengineer/Affiliate-Ai.git"
EXPECTED_REMOTE_ALIAS="git@github.com-affiliate-ai:akeengineer/Affiliate-Ai.git"
OUTPUT_ROOT="$REPO_ROOT/tmp/phase2b-hermes"

cd "$REPO_ROOT"

remote_url="$(git remote get-url origin)"
skills_output="$(sudo hermes skills list)"

case "$remote_url" in
  "$EXPECTED_REMOTE_PRIMARY"|"$EXPECTED_REMOTE_ALIAS") ;;
  *)
    echo "Unexpected origin remote: $remote_url" >&2
    exit 1
    ;;
esac

printf '%s\n' "$skills_output" | rg -q 'affiliate-growth-os'
printf '%s\n' "$skills_output" | rg -q 'obsidian'
printf '%s\n' "$skills_output" | rg -q 'codex'
test -x scripts/dev/run_phase1_smoke.sh

if [ "${ENABLE_AUTOPUBLISH:-false}" = "true" ]; then
  echo "ENABLE_AUTOPUBLISH must not be true" >&2
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"

echo "repo_root: $REPO_ROOT"
echo "origin_remote: $remote_url"
echo "skills: ok"
echo "smoke_script: ok"
echo "autopublish: false"
echo "final_status: success"
```

- [ ] **Step 3: Ignore runtime-only output**

Append to `.gitignore`:

```gitignore
tmp/phase2b-hermes/
```

- [ ] **Step 4: Verify**

Run: `bash -n scripts/dev/check_hermes_runtime.sh`

Expected: exit `0`

Run: `scripts/dev/check_hermes_runtime.sh`

Expected:

```text
repo_root: /home/ubuntu/Affiliate-Ai
origin_remote: ...
skills: ok
smoke_script: ok
autopublish: false
final_status: success
```

- [ ] **Step 5: Commit**

```bash
git add scripts/dev/check_hermes_runtime.sh .gitignore
git commit -m "chore: add hermes runtime checks"
```

### Task 3: Verify end-to-end Hermes-safe flow

**Files:**
- Test: `scripts/dev/check_hermes_runtime.sh`
- Test: `scripts/dev/run_phase1_smoke.sh`
- Test: `prompts/workflows/hermes-phase2b-operational-test.md`

- [ ] **Step 1: Run deterministic verification**

Run:

```bash
bash -n scripts/dev/check_hermes_runtime.sh
bash -n scripts/dev/run_phase1_smoke.sh
source .venv/bin/activate && python -m pytest -q
scripts/dev/check_hermes_runtime.sh
scripts/dev/run_phase1_smoke.sh 2026-W26
git status --short | grep "tmp/phase2b-hermes" && echo "BAD" || echo "OK"
```

Expected:

```text
12 passed
repo_root: /home/ubuntu/Affiliate-Ai
...
final_status: success
scored_products: 1
...
final_status: success
OK
```

- [ ] **Step 2: Manual Hermes run checklist**

Run or instruct Hermes with:

```bash
sudo hermes run --prompt-file prompts/workflows/hermes-phase2b-operational-test.md
```

If `hermes run --prompt-file` is not the exact CLI shape on this machine, use the equivalent Hermes command that runs a prompt file without changing its contents.

Expected:

- Hermes reads the source-of-truth files first
- Hermes does not request Codex implementation
- Hermes runs or instructs the smoke workflow
- Hermes writes only `tmp/phase2b-hermes/hermes-operational-summary.md`
- Hermes does not write to private vault directories

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "test: verify hermes operational flow"
```

