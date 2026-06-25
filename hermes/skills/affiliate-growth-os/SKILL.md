# Affiliate Growth OS

## DESCRIPTION

Use this skill whenever the user asks about affiliate marketing, product discovery, product trend ranking, marketplace best sellers, commission comparison, affiliate content planning, campaign launch decisions, Shopee, Lazada, TikTok Shop, PartnerStack, Impact, Amazon Associates, or Hermes/Codex automation for affiliate operations.

This project is Affiliate Product Intelligence OS. It is not a generic affiliate content generator.

## PROJECT PRINCIPLES

- Hermes Agent is the orchestrator.
- Codex CLI is the implementation engine.
- Obsidian Vault is the only backend/project memory in Phase 1.
- The enabled Hermes Obsidian plugin/skill must be used for reading, creating, searching, and updating project notes.
- Affitor affiliate-skills under vendor/affiliate-skills is the reusable skill library.
- GitHub is used for source control, task audit, PR review, CI, and governance.
- tmux is used as the multi-agent warroom.
- Do not use a database in Phase 1.
- Do not create a separate Obsidian plugin in Phase 1.
- Do not autopublish unless ENABLE_AUTOPUBLISH=true.
- Do not generate affiliate content before product scoring.

## SOURCE OF TRUTH

Before doing project work, read:

1. CONTEXT.md
2. AGENT.md
3. AGENTS.md
4. docs/SCORING_SPEC.md
5. docs/WORKFLOW_SPEC.md
6. docs/OBSIDIAN_CONTRACT.md
7. docs/HERMES_OPERATING_RULES.md
8. docs/CODEX_IMPLEMENTATION_GUIDE.md
9. docs/GITHUB_WORKFLOW.md

Treat these files as the project source of truth.

## ACTIVATION RULE

Activate this skill when the user asks for:

- affiliate product discovery
- weekly product scan
- Shopee/Lazada/TikTok affiliate workflow
- product ranking
- product opportunity scoring
- commission comparison
- trending product analysis
- affiliate campaign planning
- affiliate content generation
- agent voting
- Codex implementation for this project
- Obsidian affiliate intelligence workflow

## DEFAULT WORKFLOW

1. Understand the user objective.
2. Read project source-of-truth files.
3. Use Obsidian as the only backend/project memory.
4. Start from product discovery and product opportunity scoring.
5. Use deterministic scoring before LLM-based analysis.
6. Send only top product candidates into agent analysis.
7. Use tmux warroom for major product/campaign decisions.
8. Require at least 3 agent votes before campaign launch.
9. Run compliance review before preparing content for publish.
10. Use Codex CLI for implementation tasks.
11. Store decisions in Obsidian.
12. Store meetings in Obsidian.
13. Store reports in Obsidian.
14. Do not autopublish unless explicitly enabled.

## PRODUCT OPPORTUNITY SCORE

Product Opportunity Score =

- 25% Demand Score
- 20% Trend Velocity Score
- 15% Marketplace Rank Score
- 15% Commission Score
- 10% Content Fit Score
- 10% Competition Gap Score
- 5% Risk Penalty Inverse

Decision thresholds:

- >= 85: launch
- 75-84: small_batch_test
- 65-74: watchlist
- < 65: reject

## REQUIRED AGENTS

For major product or campaign decisions, use at least these agents:

1. Product Miner Agent
2. Demand Intelligence Agent
3. Commission Economics Agent
4. Content Virality Agent
5. Compliance Risk Agent
6. Vote Chairman Agent

Minimum required voting agents:

- Product Miner Agent
- Demand Intelligence Agent
- Compliance Risk Agent

## AFFITOR SKILL LIBRARY

Affitor skills are located at:

vendor/affiliate-skills

Use this library as supporting knowledge and reusable workflows.

Do not load all skills into context at once.
Use registry.json first, then load only the specific SKILL.md files needed for the current task.

Recommended skill chains:

### Product discovery

- affiliate-program-search
- niche-opportunity-finder
- commission-calculator
- trending-content-scout
- content-angle-ranker

### Short video content

- trending-content-scout
- content-angle-ranker
- tiktok-script-writer
- compliance-checker

### SEO / blog

- keyword-cluster-architect
- affiliate-blog-builder
- comparison-post-writer
- seo-audit
- compliance-checker

### Weekly optimization

- performance-report
- conversion-tracker
- self-improver

## OBSIDIAN RULES

Use Obsidian for:

- product candidates
- trend signals
- marketplace signals
- commission signals
- agent meetings
- decisions
- content drafts
- compliance results
- weekly reports

Do not store private affiliate business data in GitHub.

Private business data must stay in Obsidian Vault.

## CODEX RULES

Use Codex CLI only for implementation tasks.

Before asking Codex to implement, create or reference a task file under:

codex/tasks/

Codex must read:

- AGENTS.md
- CONTEXT.md
- AGENT.md
- docs/SCORING_SPEC.md
- docs/OBSIDIAN_CONTRACT.md
- docs/CODEX_IMPLEMENTATION_GUIDE.md

Codex must not:

- add a database
- hardcode secrets
- implement autopublish
- commit private Obsidian data
- bypass tests
- change architecture without updating docs

## SAFETY RULES

- ENABLE_AUTOPUBLISH must default to false.
- ENABLE_OPENAI_API_DIRECT must default to false.
- Do not use OPENAI_API_KEY unless explicitly configured.
- Do not commit .env.
- Do not commit affiliate tokens.
- Do not commit payout data.
- Do not publish content without affiliate disclosure.
- Do not make unsupported medical, financial, or guaranteed-income claims.

## OUTPUT FORMAT

For major work, produce:

1. Objective
2. Inputs read
3. Product scoring result
4. Agent analysis
5. Votes
6. Decision
7. Required next action
8. Obsidian notes created or updated
9. Codex task created, if implementation is required
10. Risks and limitations