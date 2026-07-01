# Scoring Reference

## Active IPO Filter

An IPO is considered active for an `as_of` date when:

1. `apply_start_date <= as_of`, and
2. `as_of <= apply_end_date` if `apply_end_date` exists, otherwise `as_of <= min(listing_date, apply_start_date + active_window_days)`.

The default `active_window_days` is 7. This is a pragmatic fallback because the enriched local dataset often has `apply_start_date` and `listing_date` but not application close dates.

## LLM Scoring Rubric

Assign the final 0-100 score manually from extracted evidence:

- Demand / heat, 30 points: public subscription multiple, subscriber count, and market attention. Strong positive when demand is high but not obviously overheated.
- Allocation practicality, 15 points: one-lot success rate, entry fee, and whether a retail subscriber has a realistic allocation chance.
- Deal quality, 20 points: sponsor quality, industry, cornerstone information, issue size, valuation clues, and pricing range.
- Market/listing signal, 20 points: gray market data, first-day data if already known, recent HK IPO sentiment, and days to listing.
- Data confidence, 15 points: completeness and source quality. Penalize heavily when key facts are missing.

Use `deterministic_priority` only as a sorting hint. It is not the final score.

## Rating Bands

- `A`: score >= 80
- `B`: score >= 65
- `C`: score >= 50
- `D`: score < 50

## Interpretation

Prefer explaining the top 3 positive and negative drivers. Mention missing data explicitly when it affects confidence. Always add that IPO subscriptions can lose money and that the score is only a decision aid.
