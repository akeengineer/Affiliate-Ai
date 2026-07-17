# Codex Task: Agent Brainstorming & Self-Improvement

## Task ID

008-agent-brainstorming

## Objective

Enable agents to brainstorm new ideas collaboratively, propose them to the user for approval, and learn from historical results to improve over time.

## Files to read first

- AGENTS.md
- CONTEXT.md
- docs/WORKFLOW_SPEC.md
- docs/plans/shopee-first-autonomous-system.md
- scripts/agents/agent_runner.py
- scripts/agents/meeting.py
- vault/templates/agent-meeting-template.md

## Scope

- `scripts/agents/brainstorm.py` — Multi-agent discussion orchestration
- `scripts/agents/propose_idea.py` — Generate idea notes + send for approval
- `scripts/agents/learn_from_results.py` — Analyze past performance, adjust parameters
- `scripts/agents/approval_handler.py` — Process user approve/reject responses
- `scripts/agents/config/learning.yaml` — Learning parameters, weight bounds
- `tests/test_brainstorm.py` — Tests

## Out of scope

- Two-way chat interaction (future enhancement)
- Fully autonomous weight changes without bounds
- Publishing content

## Acceptance criteria

- [ ] `brainstorm.py` runs multi-agent discussion via sequential Claude CLI calls
- [ ] Discussion output saved as agent_meeting note in vault
- [ ] `propose_idea.py` extracts actionable ideas from meeting notes
- [ ] Ideas formatted as proposal notes with rationale, expected impact, required approval
- [ ] Proposals sent via notifier for user review
- [ ] `learn_from_results.py` compares past predictions vs actual outcomes
- [ ] Learning adjusts: search keywords, niche priorities, scoring weight emphasis (within bounds)
- [ ] Changes logged as learning_log notes in vault
- [ ] `approval_handler.py` marks ideas as approved/rejected based on user input
- [ ] Approved ideas feed into next nightly_run configuration
- [ ] All adjustments bounded by learning.yaml limits (no extreme shifts)
- [ ] Tests pass

## Tests required

- test_brainstorm_multi_agent_flow
- test_brainstorm_output_format
- test_propose_idea_extraction
- test_learning_weight_adjustment
- test_learning_bounds_enforcement
- test_approval_handler_approve
- test_approval_handler_reject

## Security constraints

- Weight adjustments bounded (max ±10% per cycle)
- No autonomous scope expansion beyond configured niches
- All learning changes logged and auditable
- User approval required for new niche/category additions

## Notes

- Brainstorming format: Chairman poses question → each agent responds → Chairman synthesizes
- Ideas might include: new niche to explore, keyword to add, content angle, timing change
- Learning uses simple heuristics (not ML) — compare scored predictions vs actual performance
- This task references design doc: docs/plans/shopee-first-autonomous-system.md Phase 5
