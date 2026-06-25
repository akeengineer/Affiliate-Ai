# GitHub Workflow

## Purpose

GitHub is the engineering control plane for this project.

GitHub stores:

- source code
- specifications
- Codex task files
- GitHub Actions workflows
- templates
- sanitized samples

GitHub must not store:

- `.env`
- API keys or tokens
- real affiliate links
- payout data
- private Obsidian business notes

## Branching

- `main`: protected stable branch
- `feature/*`: new implementation
- `fix/*`: bug fixes
- `docs/*`: documentation changes
- `chore/*`: maintenance

## Pull request requirements

Every PR should include:

- linked task or issue
- changed files summary
- tests run
- security impact
- Obsidian data impact

## Recommended branch protection

Protect `main` with:

- Require pull request before merging
- Require status checks to pass
- Require conversation resolution
- Block force pushes
- Restrict direct pushes if working with collaborators
