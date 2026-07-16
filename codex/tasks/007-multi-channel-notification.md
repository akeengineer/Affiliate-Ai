# Codex Task: Multi-Channel Notification

## Task ID

007-multi-channel-notification

## Objective

Build a unified notification system that sends morning reports, error alerts, and idea proposals to LINE, Telegram, and Discord simultaneously.

## Files to read first

- AGENTS.md
- CONTEXT.md
- docs/plans/shopee-first-autonomous-system.md
- scripts/orchestrator/nightly_run.py

## Scope

- `scripts/notify/line_notify.py` — LINE Notify API client
- `scripts/notify/telegram_bot.py` — Telegram Bot API client
- `scripts/notify/discord_webhook.py` — Discord Webhook client
- `scripts/notify/notifier.py` — Unified dispatcher (sends to all channels)
- `scripts/notify/formatters.py` — Per-channel message formatting
- `scripts/notify/config.yaml` — Channel tokens/webhook URLs (references .env)
- `tests/test_notifier.py` — Tests

## Out of scope

- Two-way interaction (approve/reject via chat) — Phase 5
- Email notification
- Push notifications

## Acceptance criteria

- [ ] `python scripts/notify/notifier.py --type morning_report --input <report_path>` sends to all 3 channels
- [ ] LINE: sends via LINE Notify API with formatted summary
- [ ] Telegram: sends via Bot API with Markdown formatting
- [ ] Discord: sends via Webhook with embed formatting
- [ ] Supports message types: morning_report, error_alert, idea_proposal
- [ ] Each channel has appropriate message length limits handled (truncate with link to full report)
- [ ] Graceful failure: if one channel fails, others still send
- [ ] Credentials loaded from environment variables (LINE_NOTIFY_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK_URL)
- [ ] Tests pass with mocked HTTP responses
- [ ] No tokens in source code

## Tests required

- test_line_notify_send
- test_telegram_bot_send
- test_discord_webhook_send
- test_unified_notifier_all_channels
- test_notifier_partial_failure
- test_message_formatting_morning_report
- test_message_formatting_error_alert
- test_message_truncation

## Security constraints

- All tokens/credentials via environment variables only
- .env.example updated with placeholder keys
- No message content contains raw API keys or secrets
- Rate limiting respected per channel API limits

## Notes

- LINE Notify: https://notify-bot.line.me/
- Telegram Bot API: https://core.telegram.org/bots/api
- Discord Webhooks: https://discord.com/developers/docs/resources/webhook
- Morning report format: summary stats + top 3 products + decisions + any errors
- This task references design doc: docs/plans/shopee-first-autonomous-system.md Phase 4
