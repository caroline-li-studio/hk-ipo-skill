# Scoring Reference

## Active IPO Filter

An IPO is considered active for an `as_of` date when:

1. `apply_start_date <= as_of`, and
2. `as_of <= apply_end_date`.

Confirm application dates from live or archived web sources fetched during the current invocation. Do not infer an active window from listing date alone.

## LLM Scoring Rubric

Assign the final 0-100 score manually from extracted evidence:

- Demand / heat, 30 points: public subscription multiple, subscriber count, and market attention. Strong positive when demand is high but not obviously overheated.
- Allocation practicality, 15 points: one-lot success rate, entry fee, and whether a retail subscriber has a realistic allocation chance.
- Deal quality, 20 points: sponsor quality, industry, cornerstone information, issue size, valuation clues, and pricing range.
- Market/listing signal, 20 points: gray market data, first-day data if already known, recent HK IPO sentiment, and days to listing.
- Data confidence, 15 points: completeness, source quality, and cross-source agreement. Penalize heavily when key facts are missing or only one source confirms the window.

For a past-date analysis, avoid using post-date trading outcomes unless the user explicitly requests a hindsight review.

## Rating Bands

- `A`: score >= 80
- `B`: score >= 65
- `C`: score >= 50
- `D`: score < 50

## Interpretation

Prefer explaining the top 3 positive and negative drivers. Mention missing data explicitly when it affects confidence. Always add that IPO subscriptions can lose money and that the score is only a decision aid.
