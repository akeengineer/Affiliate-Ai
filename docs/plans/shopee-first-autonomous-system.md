# Shopee-First Autonomous System Design

## Version

v1.0 — 2026-07-16

## Approved By

User (via Kiro session)

## Summary

This document defines the complete system design for turning the existing Affiliate Product Intelligence OS into a fully autonomous, Shopee-first affiliate intelligence system that runs unattended overnight on EC2.

## Constraints & Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Data source | Shopee scraping (primary) + Affiliate API (when approved) | API pending approval, scraping works now |
| AI runtime | Claude CLI + Codex CLI + AGY CLI | Already installed on EC2, subscription covers usage |
| Orchestrator | Hermes | Already installed, designed for this role |
| Autonomy level | Full autopilot except publish | User wants overnight automation, no publish in Phase 1 |
| Notification | LINE + Telegram + Discord | Multi-channel for redundancy |
| Backend | Obsidian Vault (Markdown + YAML frontmatter) | No database in Phase 1 per AGENTS.md |
| EC2 spec | 8GB+ RAM | Sufficient for scraping + CLI agents |
| Security hardening | Phase 8 (last) | User priority: working system first |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EC2 (8GB+ RAM)                              │
│                                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  CRON    │───▶│  Orchestrator │───▶│  Agent Runtime (tmux)    │  │
│  │ (nightly)│    │  (Hermes)     │    │                          │  │
│  └──────────┘    └──────┬───────┘    │  ┌─────┐ ┌─────┐ ┌────┐ │  │
│                         │            │  │Miner│ │Demand│ │Vote│ │  │
│                         ▼            │  │Agent│ │Agent │ │Chair│ │  │
│              ┌──────────────────┐    │  └──┬──┘ └──┬──┘ └──┬─┘ │  │
│              │  Shopee Scraper  │    │     │       │       │    │  │
│              │  (Playwright)    │    │     ▼       ▼       ▼    │  │
│              └────────┬─────────┘    │  ┌──────────────────────┐│  │
│                       │              │  │ Claude/Codex/AGY CLI  ││  │
│                       ▼              │  │ (AI reasoning layer)  ││  │
│              ┌──────────────────┐    │  └──────────────────────┘│  │
│              │  Obsidian Vault  │◀───┘                           │  │
│              │  (Markdown notes)│                                 │  │
│              └────────┬─────────┘                                │  │
│                       │                                          │  │
│                       ▼                                          │  │
│  ┌─────────────────────────────────────────────────────────────┐│  │
│  │  Pipeline: score_product → vote → compliance → report       ││  │
│  └─────────────────────────────┬───────────────────────────────┘│  │
│                                │                                 │  │
│                                ▼                                 │  │
│  ┌─────────────────────────────────────────────────────────────┐│  │
│  │  Notifier: LINE + Telegram + Discord (morning report)       ││  │
│  └─────────────────────────────────────────────────────────────┘│  │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent ↔ CLI Mapping

| Agent | Primary CLI | Role |
|-------|------------|------|
| Product Miner | `claude -p` | Scan Shopee, select candidates |
| Demand Intelligence | `claude -p` | Evaluate demand/trend signals |
| Commission Economics | `codex -q` | Calculate commission + ROI |
| Content Virality | `claude -p` | Analyze content fit potential |
| Compliance Risk | `agy -p` | Check compliance/legal risks |
| Vote Chairman | `claude -p` | Aggregate signals, make decisions |
| Hermes (Orchestrator) | `hermes` | Sequence, monitor, log |

## Nightly Autopilot Flow

```
02:00  CRON trigger
  │
  ▼
02:01  Hermes: start nightly run
  │
  ▼
02:05  Product Miner (claude): scan Shopee → 20-50 candidates
  │
  ▼
02:30  Demand + Commission + Virality agents: analyze → signal notes
  │
  ▼
03:00  Compliance agent (agy): check compliance
  │
  ▼
03:15  Vote Chairman (claude): vote → decision notes
  │
  ▼
03:30  score_product.py + generate_weekly_report.py
  │
  ▼
03:45  Agent brainstorm: generate ideas for next cycle
  │
  ▼
04:00  Notifier: send morning report → LINE + Telegram + Discord
  │
  ▼
07:00  User wakes → sees report → approve/reject ideas
```

## Phased Roadmap

### Phase 1 — Shopee Scraper + Pipeline Integration (Week 1-2)

Goal: Auto-scrape Shopee product data → feed into existing scoring pipeline.

Files to create:
- `scripts/shopee/scraper.py` — Playwright-based Shopee scraper
- `scripts/shopee/config.yaml` — Niche/keyword/category targets
- `scripts/shopee/to_candidate.py` — Transform scraped data → product_candidate note
- `tests/test_shopee_scraper.py` — Integration tests

Key behaviors:
- Scrape product name, price, sold count, rating, category, shop info
- Rate limiting + random delays + user-agent rotation
- Output: Obsidian-compatible product_candidate Markdown notes in vault

### Phase 2 — Agent AI Runtime (Week 2-3)

Goal: Each agent uses Claude/Codex/AGY CLI for real AI analysis.

Files to create:
- `scripts/agents/agent_runner.py` — Unified CLI agent wrapper
- `scripts/agents/product_miner.py` — Product Miner agent logic
- `scripts/agents/demand_intel.py` — Demand Intelligence agent logic
- `scripts/agents/commission_econ.py` — Commission Economics agent logic
- `scripts/agents/content_virality.py` — Content Virality agent logic
- `scripts/agents/compliance_risk.py` — Compliance Risk agent logic
- `scripts/agents/vote_chairman.py` — Vote Chairman agent logic
- `scripts/agents/meeting.py` — Multi-agent brainstorming session
- `tests/test_agent_runner.py` — Agent runtime tests

Key behaviors:
- Each agent reads context from vault notes
- Calls appropriate CLI with structured prompt
- Writes output as Obsidian-compatible signal/vote/decision notes
- Respects guardrails defined in prompts/agents/*.md

### Phase 3 — Orchestrator + Scheduler (Week 3-4)

Goal: Full overnight automation via cron + Hermes.

Files to create:
- `scripts/orchestrator/nightly_run.py` — Full pipeline orchestration
- `scripts/orchestrator/state.py` — State tracking + resume capability
- `scripts/orchestrator/cron_setup.sh` — Crontab configuration
- `tests/test_orchestrator.py` — Orchestration tests

Key behaviors:
- Cron triggers at 02:00 daily
- Hermes sequences: scrape → analyze → score → vote → report
- Error handling with retry logic
- Partial failure recovery (resume from last checkpoint)
- State persisted in vault as run log notes

### Phase 4 — Multi-Channel Notification (Week 4)

Goal: Morning report delivery via LINE + Telegram + Discord.

Files to create:
- `scripts/notify/line_notify.py` — LINE Notify integration
- `scripts/notify/telegram_bot.py` — Telegram Bot integration
- `scripts/notify/discord_webhook.py` — Discord Webhook integration
- `scripts/notify/notifier.py` — Unified multi-channel notifier
- `scripts/notify/formatters.py` — Message formatting per channel
- `tests/test_notifier.py` — Notification tests

Key behaviors:
- Morning report: summary of overnight findings
- Error alerts: immediate notification on critical failures
- Idea proposals: agent brainstorm results for approval
- Configurable per-channel message formatting

### Phase 5 — Agent Brainstorming & Self-Improvement (Week 5)

Goal: Agents propose ideas, learn from results, improve over time.

Files to create:
- `scripts/agents/brainstorm.py` — Multi-agent discussion orchestration
- `scripts/agents/propose_idea.py` — Idea generation + notification
- `scripts/agents/learn_from_results.py` — Performance analysis + weight adjustment
- `scripts/agents/approval_handler.py` — Process user approve/reject responses
- `tests/test_brainstorm.py` — Brainstorming tests

Key behaviors:
- Agents discuss via sequential Claude CLI calls
- Generate idea notes with rationale
- Send idea summary for user approval
- Learn from historical scoring accuracy
- Adjust search keywords and scoring emphasis

### Phase 6 — Shopee API Integration (When API approved)

Goal: Switch from scraping to official Shopee Affiliate API.

Files to create:
- `scripts/shopee/api_client.py` — Official Shopee Affiliate API client
- `scripts/shopee/link_generator.py` — Affiliate link auto-generation
- `tests/test_shopee_api.py` — API integration tests

Key behaviors:
- Config toggle: `source: scraper` → `source: api`
- Enrich data with commission rates, conversion metrics
- Auto-generate affiliate links for approved products
- Graceful fallback to scraper if API fails

### Phase 7 — Enhancement (Week 7+)

- Content draft generator for review/post
- Portfolio performance dashboard (web UI)
- Multi-marketplace expansion (Lazada, TikTok Shop)
- A/B testing for scoring weights

### Phase 8 — Security Hardening (Last)

- Secret rotation automation
- Signed append-only audit store
- RBAC enforcement
- Vulnerability scanning
- Automated vault backup + disaster recovery

## Communication with Hermes

Hermes must know:
1. This document is the system design source of truth
2. Codex tasks under `codex/tasks/004-008` are the implementation backlog
3. Phase execution order is strict (1→2→3→4→5→6→7→8)
4. No publish/autopublish until explicitly approved in future phase
5. All agent outputs go to Obsidian Vault as Markdown notes
6. Overnight runs start at 02:00 via cron
7. Morning reports go to LINE + Telegram + Discord

## References

- `docs/SCORING_SPEC.md` — Scoring algorithm and thresholds
- `docs/WORKFLOW_SPEC.md` — Agent workflow definitions
- `docs/OBSIDIAN_CONTRACT.md` — Note schema contracts
- `docs/SECURITY.md` — Security baseline requirements
- `prompts/agents/*.md` — Individual agent prompt definitions
- `codex/tasks/001-003` — Existing completed/partial tasks
