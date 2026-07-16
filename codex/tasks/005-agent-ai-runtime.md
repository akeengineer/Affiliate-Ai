# Codex Task: Agent AI Runtime

## Task ID

005-agent-ai-runtime

## Objective

Build a unified agent runner that invokes Claude CLI, Codex CLI, and AGY CLI to perform real AI analysis on product candidates, producing signal/vote/decision notes in the Obsidian vault.

## Files to read first

- AGENTS.md
- CONTEXT.md
- docs/SCORING_SPEC.md
- docs/WORKFLOW_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- docs/plans/shopee-first-autonomous-system.md
- prompts/agents/product-miner-agent.md
- prompts/agents/demand-intelligence-agent.md
- prompts/agents/commission-economics-agent.md
- prompts/agents/content-virality-agent.md
- prompts/agents/compliance-risk-agent.md
- prompts/agents/vote-chairman-agent.md

## Scope

- `scripts/agents/agent_runner.py` — Unified wrapper: select CLI, build prompt, call, parse output
- `scripts/agents/product_miner.py` — Product Miner: analyze candidates, rank interest
- `scripts/agents/demand_intel.py` — Demand Intelligence: write trend_signal notes
- `scripts/agents/commission_econ.py` — Commission Economics: write commission_signal notes
- `scripts/agents/content_virality.py` — Content Virality: write marketplace_signal notes
- `scripts/agents/compliance_risk.py` — Compliance Risk: write compliance_result notes
- `scripts/agents/vote_chairman.py` — Vote Chairman: aggregate signals, write decision notes
- `scripts/agents/meeting.py` — Multi-agent brainstorming session
- `tests/test_agent_runner.py` — Tests

## Out of scope

- Scraping (Task 004)
- Orchestration/scheduling (Task 006)
- Notification (Task 007)
- Self-improvement loop (Task 008)

## Acceptance criteria

- [ ] `agent_runner.py` can invoke claude/codex/agy CLI with structured prompts
- [ ] Each agent reads product_candidate notes from vault as context
- [ ] Each agent writes output as properly-formatted Obsidian note (correct frontmatter type)
- [ ] Product Miner outputs ranked candidate list
- [ ] Demand/Commission/Virality agents output signal notes linked to product_id
- [ ] Compliance agent outputs compliance_result note
- [ ] Vote Chairman aggregates all signals and outputs decision note with vote
- [ ] Meeting script produces agent_meeting note with ideas list
- [ ] All agent outputs include `created_at` and `updated_at` timestamps
- [ ] Timeout handling: 60s per agent call, graceful failure
- [ ] Tests pass with mocked CLI responses
- [ ] No API keys hardcoded; uses environment or CLI auth

## Tests required

- test_agent_runner_cli_selection
- test_agent_runner_prompt_building
- test_agent_runner_timeout_handling
- test_product_miner_output_format
- test_demand_intel_signal_note
- test_commission_econ_signal_note
- test_compliance_risk_result_note
- test_vote_chairman_decision_note
- test_meeting_brainstorm_output

## Security constraints

- Agent prompts include guardrails (no affiliate link generation before scoring)
- No autopublish actions
- CLI calls use existing auth (no new credentials)
- Agent outputs sanitized before writing to vault

## Notes

- Agent CLI mapping: Product Miner/Demand/Virality/Chairman → claude -p, Commission → codex -q, Compliance → agy -p
- Prompts must include relevant context from vault notes (candidate + existing signals)
- Each agent respects forbidden actions defined in its prompt file
- This task references design doc: docs/plans/shopee-first-autonomous-system.md Phase 2
