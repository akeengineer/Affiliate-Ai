# Product Opportunity Scoring Spec

## Objective
Rank affiliate product candidates before content generation.

## Formula

```text
Product Opportunity Score =
  25% Demand Score
+ 20% Trend Velocity Score
+ 15% Marketplace Rank Score
+ 15% Commission Score
+ 10% Content Fit Score
+ 10% Competition Gap Score
+  5% Risk Penalty Inverse
```

Risk Penalty Inverse = `100 - risk_score`.

## Decision thresholds

- `>= 85`: launch
- `75-84`: small_batch_test
- `65-74`: watchlist
- `< 65`: reject

## Rules

- All component scores must be 0-100.
- Missing signals must reduce confidence.
- The function must be deterministic.
- No external API calls inside the scoring function.
- Unit tests must cover all thresholds and missing-signal behavior.
