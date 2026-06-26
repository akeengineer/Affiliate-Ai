#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_ROOT="$REPO_ROOT/tmp/phase2c-warroom"
VOTES_DIR="$OUTPUT_ROOT/votes"
DECISIONS_DIR="$OUTPUT_ROOT/decisions"
ARTIFACTS_MANIFEST="$OUTPUT_ROOT/artifacts.txt"
PRIVATE_VAULT_BASELINE="$OUTPUT_ROOT/private-vault-baseline.txt"
PRIVATE_VAULT_CURRENT="$OUTPUT_ROOT/private-vault-current.txt"
DECISION_PATH="$DECISIONS_DIR/decision-smart-desk-pad.md"

PRIVATE_VAULT_DIRS=(
  "$REPO_ROOT/vault/.obsidian"
  "$REPO_ROOT/vault/products"
  "$REPO_ROOT/vault/trends"
  "$REPO_ROOT/vault/marketplace-signals"
  "$REPO_ROOT/vault/commissions"
  "$REPO_ROOT/vault/meetings"
  "$REPO_ROOT/vault/decisions"
  "$REPO_ROOT/vault/contents"
  "$REPO_ROOT/vault/compliance"
  "$REPO_ROOT/vault/reports"
)

fail() {
  echo "$1" >&2
  exit 1
}

relative_repo_path() {
  local path="$1"
  printf '%s\n' "${path#$REPO_ROOT/}"
}

snapshot_private_vault() {
  local destination="$1"
  local dir

  : > "$destination"
  for dir in "${PRIVATE_VAULT_DIRS[@]}"; do
    printf '## %s\n' "$(relative_repo_path "$dir")" >> "$destination"
    if [ -d "$dir" ]; then
      find "$dir" -mindepth 1 -printf '%P|%TY-%Tm-%TdT%TH:%TM:%TS|%s\n' | LC_ALL=C sort >> "$destination"
    fi
    printf '\n' >> "$destination"
  done
}

[ -d "$OUTPUT_ROOT" ] || fail "Missing output root: $OUTPUT_ROOT"
[ -d "$VOTES_DIR" ] || fail "Missing votes directory: $VOTES_DIR"
[ -d "$DECISIONS_DIR" ] || fail "Missing decisions directory: $DECISIONS_DIR"
[ -f "$ARTIFACTS_MANIFEST" ] || fail "Missing artifacts manifest: $ARTIFACTS_MANIFEST"
[ -f "$PRIVATE_VAULT_BASELINE" ] || fail "Missing private vault baseline: $PRIVATE_VAULT_BASELINE"

vote_count="$(find "$VOTES_DIR" -maxdepth 1 -type f -name 'vote-*.md' | wc -l | tr -d ' ')"
decision_count="$(find "$DECISIONS_DIR" -maxdepth 1 -type f -name 'decision-*.md' | wc -l | tr -d ' ')"

[ "$vote_count" = "5" ] || fail "Expected 5 vote artifacts, found $vote_count"
[ "$decision_count" = "1" ] || fail "Expected 1 decision artifact, found $decision_count"

while IFS= read -r artifact_path; do
  [ -n "$artifact_path" ] || continue
  case "$artifact_path" in
    "$OUTPUT_ROOT"/*) ;;
    *) fail "Artifact outside output root: $artifact_path" ;;
  esac
  [ -f "$artifact_path" ] || fail "Missing artifact listed in manifest: $artifact_path"
done < "$ARTIFACTS_MANIFEST"

for vote_path in "$VOTES_DIR"/vote-*.md; do
  grep -q '^type: agent_vote$' "$vote_path" || fail "Missing type: agent_vote in $vote_path"
done

grep -q '^type: decision$' "$DECISION_PATH" || fail "Missing type: decision in $DECISION_PATH"
grep -q '^vote_count: 5$' "$DECISION_PATH" || fail "Decision vote_count must be 5"

snapshot_private_vault "$PRIVATE_VAULT_CURRENT"
diff -u "$PRIVATE_VAULT_BASELINE" "$PRIVATE_VAULT_CURRENT" >/dev/null || fail "Private vault paths changed"
rm -f "$PRIVATE_VAULT_CURRENT"

if grep -R -nE 'https?://|amzn\.to|[?&](tag|ref|aff_id|affiliate_id)=|shareasale|clickbank|impactradius|partnerize|linksynergy|rakuten' "$OUTPUT_ROOT" >/dev/null; then
  fail "Generated artifacts contain a real-looking affiliate link or URL"
fi

echo "phase2c_warroom_proof: success"
