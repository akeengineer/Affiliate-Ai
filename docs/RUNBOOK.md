# Runbook

## Initialize repo

```bash
git init
git add .
git commit -m "bootstrap affiliate product intelligence os"
```

## Add remote

```bash
git remote add origin git@github.com:<owner>/affiliate-product-intelligence-os.git
git branch -M main
git push -u origin main
```

## Start a Codex task

```bash
git checkout -b feature/bootstrap-scoring
codex
```

Prompt:

```text
Read AGENTS.md and codex/tasks/001-bootstrap-scoring.md. Implement exactly. Add tests.
```
