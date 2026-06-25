# Operational AI Agents Plan

## Summary

This plan turns the current Affiliate Product Intelligence OS repository from an operational design into an operational system that AI agents can actually run.

The first working target is:

- Hermes Agent orchestrates from the EC2 Ubuntu root profile at `/root/.hermes`.
- The source of truth is the GitHub repository `https://github.com/akeengineer/Affiliate-Ai`.
- The EC2 working copy lives at `/home/ubuntu/Affiliate-Ai`.
- Codex CLI performs implementation work inside a real Git repository.
- tmux starts a real warroom that works from project prompts, task files, and Obsidian-compatible Markdown contracts.
- Scoring and reporting work from Markdown YAML frontmatter without a database or autopublish.

Current blockers found during planning:

- EC2 had Hermes and tmux available, but the project repository was not cloned there yet.
- EC2 did not have standalone `codex` available in `PATH`.
- The Hermes profile ready for orchestration was root's profile, not the `ubuntu` user's profile.
- The repo had templates and prompts, but no deterministic scoring script, tests, `vault/samples/`, or `agent_vote` template yet.
- Agent prompts were skeletons and did not yet define strict input/output contracts.

## Runtime Architecture

Use this operating model for Phase 1:

- Windows is only the access workstation for SSH and VS Code Remote SSH.
- EC2 Ubuntu is the agent runtime.
- GitHub is the engineering source of truth.
- Obsidian remains the only project/business memory backend.
- Hermes Agent uses the enabled Obsidian integration and root profile.
- Codex CLI works in the checked-out Git repo and follows `codex/tasks/*.md`.
- tmux is the multi-agent warroom runner.

The EC2 runtime must satisfy these checks before agent work starts:

```bash
tmux -V
hermes --version
python3 --version
git --version
node --version
npm --version
codex --version
sudo hermes status
```

Expected state:

- `sudo hermes status` shows root Hermes configured and authenticated.
- `sudo hermes skills list` shows `affiliate-growth-os`, `obsidian`, and `codex` enabled.
- `git status` works inside `/home/ubuntu/Affiliate-Ai`.
- `python3 -m pytest` can run from the project repository after dependencies are installed.

## Required Improvements

### 1. Make GitHub Pullable From EC2

EC2 must have GitHub access before the repo can be used as the runtime source of truth.

Recommended setup:

```bash
ssh-keygen -t ed25519 -C "Affiliate-Ai EC2 deploy key" -f ~/.ssh/affiliate_ai_ed25519 -N ""
cat ~/.ssh/affiliate_ai_ed25519.pub
```

Add the public key to GitHub:

```text
GitHub repo -> Settings -> Deploy keys -> Add deploy key
```

Use write access only if EC2/Codex must push branches back to GitHub.

Then configure EC2 SSH:

```bash
cat >> ~/.ssh/config <<'EOF'

Host github.com-affiliate-ai
  HostName github.com
  User git
  IdentityFile ~/.ssh/affiliate_ai_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
EOF

chmod 600 ~/.ssh/config ~/.ssh/affiliate_ai_ed25519
```

Verify:

```bash
git ls-remote git@github.com-affiliate-ai:akeengineer/Affiliate-Ai.git HEAD
```

Clone:

```bash
cd /home/ubuntu
git clone git@github.com-affiliate-ai:akeengineer/Affiliate-Ai.git Affiliate-Ai
cd /home/ubuntu/Affiliate-Ai
git status
```

### 2. Install And Verify Codex CLI On EC2

Codex CLI must exist on EC2 for Hermes to delegate coding tasks to Codex.

```bash
sudo npm install -g @openai/codex
codex --version
```

If Codex asks for authentication, complete the Codex CLI login flow on EC2. Do not commit Codex credentials or API keys.

### 3. Prepare Python Test Runtime

Set up the local development environment inside the EC2 repo:

```bash
cd /home/ubuntu/Affiliate-Ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m pytest
```

The first run may report no tests or fail until task `001-bootstrap-scoring` is implemented. That is acceptable only as a baseline finding.

### 4. Make Obsidian Markdown Contracts Operational

The current templates are generic and need concrete fields that deterministic scripts and agents can consume.

Required changes:

- Expand `docs/OBSIDIAN_CONTRACT.md` with per-note-type frontmatter contracts.
- Update `vault/templates/product-candidate-template.md`.
- Update `vault/templates/trend-signal-template.md`.
- Update `vault/templates/marketplace-signal-template.md`.
- Update `vault/templates/commission-signal-template.md`.
- Add `vault/templates/agent-vote-template.md`.
- Add sanitized sample notes under `vault/samples/`.

Minimum required note types for the first working loop:

- `product_candidate`
- `trend_signal`
- `marketplace_signal`
- `commission_signal`
- `agent_vote`
- `decision`
- `compliance_result`
- `weekly_report`

GitHub may contain templates and sanitized samples only. Real products, private notes, affiliate links, payout data, and secrets must remain outside Git.

### 5. Implement Deterministic Scoring Before Agent Voting

Task `codex/tasks/001-bootstrap-scoring.md` must be clarified before implementation so Codex does not guess the schema.

It should define:

- exact frontmatter field names for component scores
- required vs optional fields
- missing-signal confidence behavior
- JSON output shape
- CLI usage
- sample input path
- acceptance criteria

The implementation should create:

- `scripts/dev/score_product.py`
- `tests/test_score_product.py`

The scoring script must:

- parse Markdown YAML frontmatter
- validate score inputs are 0-100
- calculate Product Opportunity Score exactly from `docs/SCORING_SPEC.md`
- return `launch`, `small_batch_test`, `watchlist`, or `reject`
- run without external API calls
- avoid any database dependency

### 6. Make Agent Prompts Executable Contracts

The prompt files under `prompts/agents/` must become operational instructions, not short descriptions.

Each agent prompt should include:

- role
- allowed inputs
- forbidden actions
- required output format
- Obsidian note type to create or update
- compliance and data privacy guardrails

Hard rules:

- Do not generate affiliate content before product scoring.
- Do not send unscored products to voting.
- Do not launch a campaign without score, at least 3 votes, decision note, and compliance result.
- Do not store private business data in GitHub.

### 7. Make tmux Warroom Runnable

`scripts/tmux/start-affiliate-warroom.sh` currently only opens panes and echoes agent names. It must be upgraded after runtime setup is clean.

The first runnable version should:

- start from `/home/ubuntu/Affiliate-Ai`
- open panes for Hermes, Codex, and core agents
- load the correct prompt/task files
- avoid autopublish
- make it clear where each agent should write output

### 8. Add Weekly Report Proof

After scoring works, add a report generator that proves the product-intelligence pipeline can run end to end.

Expected behavior:

- read scored candidates or sample notes
- group products by decision
- show missing signals and compliance status
- output Markdown compatible with Obsidian
- avoid generating affiliate content

## Test Plan

Runtime checks on EC2:

```bash
ssh god-of-ai 'tmux -V && hermes --version && python3 --version && git --version'
ssh god-of-ai 'codex --version'
ssh god-of-ai 'cd /home/ubuntu/Affiliate-Ai && git status'
ssh god-of-ai 'sudo hermes status'
```

Repository checks:

```bash
cd /home/ubuntu/Affiliate-Ai
source .venv/bin/activate
python -m pytest
git status --short
```

Scoring tests to add:

- `>= 85` returns `launch`
- `75-84` returns `small_batch_test`
- `65-74` returns `watchlist`
- `< 65` returns `reject`
- score below 0 fails validation
- score above 100 fails validation
- missing signal reduces confidence
- malformed frontmatter fails clearly
- sanitized sample markdown produces deterministic JSON

Workflow checks to add:

- tmux script starts a session on EC2
- each agent prompt declares input and output format
- weekly report generator creates Markdown from sample data
- `.gitignore` continues to exclude private vault directories

## Execution Order

1. Configure GitHub deploy key for EC2.
2. Clone `Affiliate-Ai` into `/home/ubuntu/Affiliate-Ai`.
3. Install and verify Codex CLI on EC2.
4. Create Python virtual environment and install dev dependencies.
5. Run baseline tests.
6. Clarify task `001-bootstrap-scoring`.
7. Implement scoring script and scoring tests.
8. Harden Obsidian templates and add sanitized samples.
9. Add weekly report generator and tests.
10. Expand agent prompts into executable contracts.
11. Upgrade tmux warroom script.
12. Run end-to-end sample workflow.

## Security Defaults

- Do not commit `.env`.
- Do not commit API keys, OAuth tokens, SSH keys, affiliate links, payout data, or private Obsidian notes.
- Do not add PostgreSQL, MySQL, SQLite, DynamoDB, or any database in Phase 1.
- Do not enable autopublish.
- Keep `ENABLE_AUTOPUBLISH=false`.
- Keep `ENABLE_OPENAI_API_DIRECT=false`.
- Use GitHub for engineering governance only.
- Use Obsidian for affiliate intelligence and business memory.
