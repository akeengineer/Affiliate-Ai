# Agent Dispatch — Workspace Steering

When the user asks you to implement, build, fix, test, refactor, or design code in this project, follow this auto-dispatch protocol instead of writing code yourself.

## Protocol

### 1. Classify the Task

Determine if the task is **small** or **large**:

- **Small** (single file, simple scope): dispatch immediately without asking
- **Large** (multiple files, architecture, complex): present a plan first, wait for user confirmation

Signals for small: mentions one file, short description, simple verbs (fix, add, implement single thing)
Signals for large: redesign/overhaul/restructure/migrate, multiple files/modules, long complex description

### 2. Check Concurrency

Before dispatching, check if agents are already running:

```
Use list_processes to see active background processes.
```

If an agent is running, ask the user:
> "An agent is currently working on [task title]. Would you like me to:
> a) Queue this task until it finishes
> b) Dispatch in parallel (both agents run simultaneously)"

### 3. Select Agent and Dispatch

Based on task type:
- **reasoning/design/review** → Claude-CLI (via `claude -p`)
- **implementation/test/refactor** → Codex-CLI (via `codex -q`)

**Dispatch command** (use `control_pwsh_process` with action "start"):

```
command: python scripts/agents/kiro_dispatch.py --agent [codex|claude] --type [type] --prompt "[full description]"
cwd: [project root]
```

Tell the user what you're doing:
> "Dispatching to [Codex-CLI/Claude-CLI]... I'll monitor progress and report when done."

### 4. Monitor Progress

Poll the process output every 10-15 seconds using `get_process_output`:

- Report meaningful progress updates to the user if output changes
- Watch for the `===RESULT===` marker indicating completion

### 5. Collect and Report

When the process completes (you see `===RESULT===` in output):

1. Parse the JSON after the marker
2. Report to user:
   - Status (success/fail/partial)
   - What was accomplished
   - Files created/modified
   - Tests run and results
   - Any errors
   - Suggested next steps

### 6. Handle Failures

If the agent fails:
- Report the error clearly
- Offer to retry with the fallback agent (Claude↔Codex)
- If user says yes, re-dispatch with the other agent

## Project Config

- Agent config: `.agents/config.yaml`
- Claude prompt: `.agents/prompts/claude-cli-agent.md`
- Codex prompt: `.agents/prompts/codex-cli-agent.md`
- Results saved to: `.agents/results/`
- State tracked in: `.agents/state/`

## Large Task Plan Format

When presenting a plan for large tasks:

```
This looks like a multi-step task. Here's my plan:

1. [Claude] Design [component] interface
2. [Codex] Implement [module A]
3. [Codex] Implement [module B] (can run parallel with #2)
4. [Codex] Write tests

Shall I proceed?
```

## Constraints

- NEVER write implementation code directly — always dispatch to agents
- ALWAYS respect project rules in `.agents/prompts/shared-context.md`
- ALWAYS save results for traceability
- If `claude` or `codex` CLI is not installed, inform the user and suggest installation
