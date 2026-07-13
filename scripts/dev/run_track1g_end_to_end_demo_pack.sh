#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

./.venv/bin/python scripts/dev/track1g_end_to_end_demo_pack.py "$@"
