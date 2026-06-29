#!/usr/bin/env bash
# Phase 4E Static Demo Bundle Operator Command.
#
# Single operator command that runs the existing safe static demo chain
# end-to-end (Phase 3D acceptance -> 4B snapshot -> 4C catalog -> 4D verifier)
# and writes a small operator summary. Orchestration only: no new business
# logic, no UI, no backend, no vault writes, no approved-workflow triggering.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ACCEPTANCE_WRAPPER="$REPO_ROOT/scripts/dev/run_phase3d_acceptance.sh"
SNAPSHOT_WRAPPER="$REPO_ROOT/scripts/dev/run_phase4b_ui_snapshot.sh"
CATALOG_WRAPPER="$REPO_ROOT/scripts/dev/run_phase4c_snapshot_catalog.sh"
VERIFIER_WRAPPER="$REPO_ROOT/scripts/dev/run_phase4d_demo_verifier.sh"

OUT_DIR="$REPO_ROOT/tmp/phase4e-demo-bundle"
OUT_REL="tmp/phase4e-demo-bundle"
WEEK_RE='^[0-9]{4}-W[0-9]{2}$'

PRIVATE_VAULT_PATHS=(
  "vault/products" "vault/decisions" "vault/trends" "vault/marketplace-signals"
  "vault/commissions" "vault/meetings" "vault/contents" "vault/compliance"
  "vault/reports" "vault/.obsidian"
)

TMP_OUT=""
cleanup() { [ -z "$TMP_OUT" ] || rm -f "$TMP_OUT"; }
trap cleanup EXIT

fail() {
  echo "$1" >&2
  exit 1
}

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/dev/run_phase4e_demo_bundle.sh <week>" >&2
  exit 1
fi

WEEK="$1"

# ── Guardrails ───────────────────────────────────────────────────────────────
[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH=true is not allowed"
[ "${ENABLE_OPENAI_API_DIRECT:-false}" != "true" ] || fail "ENABLE_OPENAI_API_DIRECT=true is not allowed"
[ "${APPROVE_PROMOTE:-false}" != "true" ] || fail "APPROVE_PROMOTE=true is not allowed"
[ "${APPROVE_DECISION:-false}" != "true" ] || fail "APPROVE_DECISION=true is not allowed"
[ "${APPROVE_FINALIZE:-false}" != "true" ] || fail "APPROVE_FINALIZE=true is not allowed"

printf '%s' "$WEEK" | grep -Eq "$WEEK_RE" || fail "week must match $WEEK_RE, got: $WEEK"

for wrapper in "$ACCEPTANCE_WRAPPER" "$SNAPSHOT_WRAPPER" "$CATALOG_WRAPPER" "$VERIFIER_WRAPPER"; do
  [ -x "$wrapper" ] || fail "Missing or non-executable wrapper: $wrapper"
done

TMP_OUT="$(mktemp)"

# ── Run a step, require its success token, or fail non-zero ──────────────────
run_step() {
  local label="$1" token="$2"
  shift 2
  if "$@" >"$TMP_OUT" 2>&1 && grep -q "$token" "$TMP_OUT"; then
    echo "demo_step: $label -> PASS"
  else
    echo "demo_step: $label -> FAIL"
    sed 's#vault/[A-Za-z0-9._/-]*#[vault-path-redacted]#g' "$TMP_OUT" >&2
    echo "demo_bundle_status: not_ready"
    echo "phase4e_status: failed"
    exit 1
  fi
}

run_step "acceptance" "acceptance_status: success" bash "$ACCEPTANCE_WRAPPER"
run_step "snapshot" "phase4b_status: success" bash "$SNAPSHOT_WRAPPER" "$WEEK"
run_step "catalog" "phase4c_status: success" bash "$CATALOG_WRAPPER"
run_step "verifier" "phase4d_status: success" bash "$VERIFIER_WRAPPER"

# ── Write operator summary (guarded output dir) ──────────────────────────────
case "$OUT_DIR" in
  */"$OUT_REL") ;;
  *) fail "refusing to write to unguarded output directory: $OUT_DIR" ;;
esac

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR/demo-bundle-summary.json" "$OUT_DIR/DEMO_BUNDLE.md"

GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat >"$OUT_DIR/demo-bundle-summary.json" <<EOF
{
  "type": "phase4e_demo_bundle",
  "status": "ready",
  "report_week": "$WEEK",
  "generated_at": "$GENERATED_AT",
  "steps": {
    "acceptance": "PASS",
    "snapshot": "PASS",
    "catalog": "PASS",
    "verifier": "PASS"
  },
  "artifacts": {
    "phase4b_snapshot": "tmp/phase4b-ui-snapshot",
    "phase4c_catalog": "tmp/phase4c-snapshot-catalog",
    "phase4d_verification": "tmp/phase4d-demo-verifier"
  },
  "guardrails": {
    "no_database": true,
    "no_fastapi": true,
    "no_backend": true,
    "no_external_apis": true,
    "no_external_urls": true,
    "no_vault_writes": true,
    "no_approval_mutation": true,
    "no_raw_artifact_export": true
  }
}
EOF

cat >"$OUT_DIR/DEMO_BUNDLE.md" <<EOF
# Phase 4E Demo Bundle

Status: ready

Report week: $WEEK

## Commands run

- run_phase3d_acceptance.sh
- run_phase4b_ui_snapshot.sh $WEEK
- run_phase4c_snapshot_catalog.sh
- run_phase4d_demo_verifier.sh

## Demo outputs

- tmp/phase4b-ui-snapshot/
- tmp/phase4c-snapshot-catalog/
- tmp/phase4d-demo-verifier/

## How to open

- tmp/phase4b-ui-snapshot/index.html
- tmp/phase4c-snapshot-catalog/index.html

## Verification

- tmp/phase4d-demo-verifier/verification-report.md
- tmp/phase4d-demo-verifier/verification-summary.json

## Guardrails

- no database
- no FastAPI
- no backend
- no external APIs
- no external URLs
- no vault writes
- no approval mutation
- no raw artifact export

## Known limitations

- static snapshot only
- stale until rebuilt
- no live refresh
- no UI shell/router
- no production deployment
EOF

# ── Self-safety guard on written output ──────────────────────────────────────
for out_file in "$OUT_DIR/demo-bundle-summary.json" "$OUT_DIR/DEMO_BUNDLE.md"; do
  if grep -Eq 'https?://' "$out_file"; then
    fail "output contains an external URL: $out_file"
  fi
  for vp in "${PRIVATE_VAULT_PATHS[@]}"; do
    if grep -qF "$vp" "$out_file"; then
      fail "output contains a private vault path: $out_file"
    fi
  done
done

# ── Final operator output ────────────────────────────────────────────────────
echo "demo_bundle_path: $OUT_REL"
echo "demo_bundle_file: demo-bundle-summary.json"
echo "demo_bundle_file: DEMO_BUNDLE.md"
echo "demo_bundle_status: ready"
echo "phase4e_status: success"
