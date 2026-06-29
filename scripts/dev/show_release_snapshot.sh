#!/usr/bin/env bash
# Phase 3E read-only release snapshot.
#
# Prints docs/PROJECT_STATE.md, then a separator, then the live, read-only
# `command_center.sh status` output. It writes nothing — no tmp, no vault.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PROJECT_STATE="$REPO_ROOT/docs/PROJECT_STATE.md"
COMMAND_CENTER="$REPO_ROOT/scripts/dev/command_center.sh"

[ -f "$PROJECT_STATE" ] || { echo "Missing doc: $PROJECT_STATE" >&2; exit 1; }
[ -x "$COMMAND_CENTER" ] || { echo "Missing or non-executable command center: $COMMAND_CENTER" >&2; exit 1; }

cat "$PROJECT_STATE"

echo
echo "============================================================"
echo "Live command center status"
echo "============================================================"
echo

exec bash "$COMMAND_CENTER" status
