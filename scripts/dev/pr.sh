#!/usr/bin/env bash
# Usage:
#   scripts/dev/pr.sh open <base> <head> <title> <body>
#   scripts/dev/pr.sh merge [--squash|--rebase|--merge] <pr_number_or_url>
#
# Requires: gh CLI authenticated (gh auth login)
# ponytail: minimal wrapper — delegates everything to gh, just saves typing

set -euo pipefail

cmd="${1:-}"
shift || true

case "$cmd" in
  open)
    base="${1:?usage: pr.sh open <base> <head> <title> <body>}"
    head="${2:?}"
    title="${3:?}"
    body="${4:-}"
    gh pr create --base "$base" --head "$head" --title "$title" --body "$body"
    ;;
  merge)
    strategy="--squash"
    if [[ "${1:-}" == --* ]]; then
      strategy="$1"
      shift
    fi
    target="${1:-}"
    if [ -n "$target" ]; then
      gh pr merge "$strategy" --auto "$target"
    else
      gh pr merge "$strategy" --auto
    fi
    ;;
  *)
    echo "Usage: pr.sh {open|merge} ..." >&2
    exit 1
    ;;
esac
