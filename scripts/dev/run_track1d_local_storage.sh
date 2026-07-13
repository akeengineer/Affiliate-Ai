#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

./.venv/bin/python scripts/dev/run_track1d_local_storage.py "$@"
