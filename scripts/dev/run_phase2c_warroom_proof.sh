#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TMUX_SCRIPT="$REPO_ROOT/scripts/tmux/start-affiliate-warroom.sh"
TASK_FILE="$REPO_ROOT/codex/tasks/006-phase2c-warroom-proof.md"
WORKFLOW_PROMPT="$REPO_ROOT/prompts/workflows/phase2c-warroom-proof.md"
OUTPUT_ROOT="$REPO_ROOT/tmp/phase2c-warroom"
VOTES_DIR="$OUTPUT_ROOT/votes"
DECISIONS_DIR="$OUTPUT_ROOT/decisions"
ARTIFACTS_MANIFEST="$OUTPUT_ROOT/artifacts.txt"
PRIVATE_VAULT_BASELINE="$OUTPUT_ROOT/private-vault-baseline.txt"
PRIVATE_VAULT_CURRENT="$OUTPUT_ROOT/private-vault-current.txt"
SESSION_NAME="affiliate-warroom-phase2c"

SAMPLE_PRODUCT="$REPO_ROOT/vault/samples/products/smart-desk-pad.md"
SAMPLE_TREND="$REPO_ROOT/vault/samples/signals/trend-smart-desk-pad.md"
SAMPLE_MARKETPLACE="$REPO_ROOT/vault/samples/signals/marketplace-smart-desk-pad.md"
SAMPLE_COMMISSION="$REPO_ROOT/vault/samples/signals/commission-smart-desk-pad.md"
SAMPLE_COMPLIANCE="$REPO_ROOT/vault/samples/compliance/compliance-smart-desk-pad.md"

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

require_file() {
  local path="$1"
  [ -f "$path" ] || fail "Missing required file: $path"
}

extract_frontmatter_value() {
  local file_path="$1"
  local key="$2"

  awk -F': ' -v key="$key" '
    BEGIN { in_block = 0 }
    /^---$/ {
      if (in_block == 0) {
        in_block = 1
        next
      }
      exit
    }
    in_block == 1 && $1 == key {
      sub(/^[^:]+: /, "")
      print
      exit
    }
  ' "$file_path"
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

write_vote() {
  local slug="$1"
  local agent_name="$2"
  local vote="$3"
  local confidence_score="$4"
  local created_at="$5"
  local findings="$6"
  local rationale="$7"
  local required_action="$8"
  shift 8

  local output_path="$VOTES_DIR/vote-$slug-smart-desk-pad.md"
  local input_path

  {
    cat <<EOF
---
type: agent_vote
vote_id: vote-$slug-smart-desk-pad
product_id: $PRODUCT_ID
agent_name: $agent_name
vote: $vote
confidence_score: $confidence_score
blocking_issues:
  - none
required_actions:
  - $required_action
status: complete
created_at: $created_at
updated_at: $created_at
---
# Agent Vote

## Inputs Read
EOF
    for input_path in "$@"; do
      printf -- "- %s\n" "$(relative_repo_path "$input_path")"
    done
    cat <<EOF

## Findings
$findings

## Rationale
$rationale

## Required Actions
- $required_action
EOF
  } > "$output_path"

  printf '%s\n' "$output_path" >> "$ARTIFACTS_MANIFEST"
}

write_decision() {
  local output_path="$DECISIONS_DIR/decision-smart-desk-pad.md"

  cat <<EOF > "$output_path"
---
type: decision
decision_id: decision-smart-desk-pad
product_id: $PRODUCT_ID
final_decision: small_batch_test
vote_count: 5
compliance_status: approved
required_actions:
  - Keep standard disclosure language in every proof follow-up.
  - Recheck commission evidence before any launch recommendation.
decision_summary: Mixed votes resolve to a safe small_batch_test outcome in proof mode.
status: complete
created_at: 2026-06-26T15:25:00Z
updated_at: 2026-06-26T15:25:00Z
---
# Decision

## Score Summary
- product_name: $PRODUCT_NAME
- demand_score: $DEMAND_SCORE
- trend_velocity_score: $TREND_SCORE
- marketplace_rank_score: $MARKETPLACE_SCORE
- commission_score: $COMMISSION_SCORE
- content_fit_score: $CONTENT_SCORE
- competition_gap_score: $COMPETITION_SCORE
- risk_score: $RISK_SCORE

## Votes
- Product Miner Agent: watchlist
- Demand Intelligence Agent: small_batch_test
- Commission Economics Agent: watchlist
- Content Virality Agent: launch
- Compliance Risk Agent: small_batch_test

## Decision
The proof keeps the output deterministic and safe. Demand and content signals are strong in the sanitized sample, but the commission and risk posture justify stopping at small_batch_test.

## Required Actions
- Keep standard disclosure language in every proof follow-up.
- Recheck commission evidence before any launch recommendation.
EOF

  printf '%s\n' "$output_path" >> "$ARTIFACTS_MANIFEST"
}

[ "${ENABLE_AUTOPUBLISH:-false}" != "true" ] || fail "ENABLE_AUTOPUBLISH must not be true"

require_file "$TMUX_SCRIPT"
require_file "$TASK_FILE"
require_file "$WORKFLOW_PROMPT"
require_file "$SAMPLE_PRODUCT"
require_file "$SAMPLE_TREND"
require_file "$SAMPLE_MARKETPLACE"
require_file "$SAMPLE_COMMISSION"
require_file "$SAMPLE_COMPLIANCE"

rm -rf "$OUTPUT_ROOT"
mkdir -p "$VOTES_DIR" "$DECISIONS_DIR"

snapshot_private_vault "$PRIVATE_VAULT_BASELINE"

PRODUCT_ID="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "product_id")"
PRODUCT_NAME="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "product_name")"
DEMAND_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "demand_score")"
TREND_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "trend_velocity_score")"
MARKETPLACE_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "marketplace_rank_score")"
COMMISSION_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "commission_score")"
CONTENT_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "content_fit_score")"
COMPETITION_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "competition_gap_score")"
RISK_SCORE="$(extract_frontmatter_value "$SAMPLE_PRODUCT" "risk_score")"

[ -n "$PRODUCT_ID" ] || fail "Failed to read product_id from $SAMPLE_PRODUCT"
[ -n "$PRODUCT_NAME" ] || fail "Failed to read product_name from $SAMPLE_PRODUCT"

: > "$ARTIFACTS_MANIFEST"

write_vote \
  "product-miner" \
  "Product Miner Agent" \
  "watchlist" \
  "74" \
  "2026-06-26T15:20:00Z" \
  "The sanitized product note is complete enough for review, but the proof keeps the entry conservative until broader sample assortment is compared." \
  "This vote stays below launch because the proof mode is demonstrating safe coordination, not proving market breadth." \
  "Compare more sanitized desk-accessory samples before a wider launch recommendation." \
  "$SAMPLE_PRODUCT" "$SAMPLE_MARKETPLACE"

write_vote \
  "demand-intelligence" \
  "Demand Intelligence Agent" \
  "small_batch_test" \
  "82" \
  "2026-06-26T15:21:00Z" \
  "The trend sample and product note both point to steady demand momentum in the sanitized dataset." \
  "A small_batch_test is the smallest next step that still respects the strong trend signal." \
  "Recheck weekly trend direction before any escalation beyond a small batch." \
  "$SAMPLE_PRODUCT" "$SAMPLE_TREND"

write_vote \
  "commission-economics" \
  "Commission Economics Agent" \
  "watchlist" \
  "71" \
  "2026-06-26T15:22:00Z" \
  "The sample commission signal is serviceable, but the payout picture is not strong enough to justify a launch vote." \
  "The safest deterministic proof output is to keep the product on watchlist until economics improve." \
  "Confirm payout durability in sanitized follow-up evidence before recommending launch." \
  "$SAMPLE_PRODUCT" "$SAMPLE_COMMISSION"

write_vote \
  "content-virality" \
  "Content Virality Agent" \
  "launch" \
  "86" \
  "2026-06-26T15:23:00Z" \
  "The desk setup use case remains easy to demonstrate repeatedly without needing generated affiliate copy." \
  "This is the strongest upside signal in the proof set, so the vote stays positive even though it does not override other safeguards." \
  "Keep the content assessment tied to product fit only, not to campaign execution." \
  "$SAMPLE_PRODUCT" "$SAMPLE_TREND" "$SAMPLE_MARKETPLACE"

write_vote \
  "compliance-risk" \
  "Compliance Risk Agent" \
  "small_batch_test" \
  "91" \
  "2026-06-26T15:24:00Z" \
  "The sanitized compliance note supports a controlled next step as long as disclosure remains mandatory." \
  "Compliance is acceptable for a proof-level small batch recommendation, but not for autopublish or unsupported claims." \
  "Carry affiliate disclosure language into every future content review." \
  "$SAMPLE_PRODUCT" "$SAMPLE_COMPLIANCE"

write_decision

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  tmux kill-session -t "$SESSION_NAME"
fi

WARROOM_SESSION="$SESSION_NAME" \
WARROOM_PROOF_MODE="true" \
WARROOM_PREPARE_VAULT_DIRS="false" \
WARROOM_OUTPUT_DISPLAY="tmp/phase2c-warroom/" \
WARROOM_READ_SCOPE="vault/samples/" \
WARROOM_WORKFLOW_PROMPT="$WORKFLOW_PROMPT" \
WARROOM_TASK_FILE="$TASK_FILE" \
ENABLE_AUTOPUBLISH="false" \
bash "$TMUX_SCRIPT"

vote_count="$(find "$VOTES_DIR" -maxdepth 1 -type f -name 'vote-*.md' | wc -l | tr -d ' ')"
decision_count="$(find "$DECISIONS_DIR" -maxdepth 1 -type f -name 'decision-*.md' | wc -l | tr -d ' ')"

[ "$vote_count" = "5" ] || fail "Expected 5 vote artifacts, found $vote_count"
[ "$decision_count" = "1" ] || fail "Expected 1 decision artifact, found $decision_count"
tmux has-session -t "$SESSION_NAME" 2>/dev/null || fail "Missing tmux session: $SESSION_NAME"

snapshot_private_vault "$PRIVATE_VAULT_CURRENT"
diff -u "$PRIVATE_VAULT_BASELINE" "$PRIVATE_VAULT_CURRENT" >/dev/null || fail "Private vault directories changed during proof"
rm -f "$PRIVATE_VAULT_CURRENT"

cat "$ARTIFACTS_MANIFEST"
