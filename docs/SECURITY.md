# Security Policy

## Secrets

Never commit:

- `.env`
- API keys
- OpenAI/Anthropic/Gemini keys
- affiliate dashboard tokens
- Obsidian REST API keys
- SSH/private keys
- payout/bank data

## GitHub settings to enable

- Secret scanning
- Push protection
- Dependabot alerts
- Branch protection or rulesets for `main`

## Phase 1 security posture

Local-first, `.env` based, no cloud deployment, no autopublish.
