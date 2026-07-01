---
name: hk-ipo-skill
description: Analyze Hong Kong IPO subscription opportunities from live sources. Use when Codex needs to fetch and cross-check current or date-specific Hong Kong IPO retail subscription windows, list stocks available for 港股打新, estimate subscription/allocation difficulty, score each active IPO, rank candidates, or explain IPO scoring factors.
---

# HK IPO Skill

Use this skill to answer questions such as:

- "今天有哪些港股可以打新？给我评分。"
- "2026-03-23 可以申购哪些港股？排序并分析。"
- "帮我看 00664.HK 是否值得打新。"

## Quick Start

For current or date-specific IPO availability, always fetch live web sources for this invocation. Search and open the source pages listed in [references/data_sources.md](references/data_sources.md), cross-check at least two independent sources for each active IPO when possible, then use the scoring rubric to reason over the evidence.

Do not use local CSV files, cached datasets, legacy model artifacts, or previous run outputs as a substitute for live source checks.

## Workflow

1. Parse the user's date/time. If absent, use the current Hong Kong date.
2. Fetch live or archived web pages during the current run: AASTOCKS IPO, ETNet IPO calendar/info, Futu/Moomoo IPO pages, CNYES/财华/券商 IPO calendars, and issuer/prospectus pages when needed.
3. Cross-check candidates across multiple sources. For each IPO, confirm stock code, company name, application start date, application close date, listing date, key offer terms, and demand/allocation difficulty metrics where available.
4. Determine active retail-subscription candidates only from confirmed application windows. Listing-only rows are not enough.
5. Extract the best available "当时" demand evidence: public subscription multiple, margin/孖展 multiple or amount, applicant count, one-lot success rate, broker predicted allocation, or final allotment only if the user asks for hindsight.
6. Use the rubric in [references/scoring.md](references/scoring.md) to assign final 0-100 scores, ratings, and explanations yourself.
7. Summarize in Chinese unless the user asks otherwise.
8. Cite the live sources used and call out conflicts or missing fields explicitly.
9. Keep the investment language cautious: this is a打新辅助评分, not financial advice.

## Default Output Contract

Use this structure unless the user asks for another format:

1. One-line answer: date, number of active IPOs, and top candidate.
2. Ranked table with required columns: rank, stock code/name, subscription window, offer terms/entry fee, subscription or margin multiple, predicted/known allocation difficulty, score/rating, short rationale.
3. Per-stock notes: top positive drivers, top risks, and source-confidence notes.
4. Exclusions: listing-only or already-closed IPOs that might be confused with active subscriptions.
5. Sources and cautionary note.

When the user asks for backtesting or post-listing review, add a separate backtest table only for IPOs whose relevant outcomes have already occurred. Include dark-pool/gray-market, listing open, and first-day close data when available. For IPOs without completed outcomes, do not include empty backtest rows; state briefly that results are not out yet.

If a required metric is unavailable, write `未披露/未找到` and lower the data-confidence component rather than inventing a value.

Read [references/scoring.md](references/scoring.md) before changing weights or interpreting edge cases.

## Data Notes

This skill intentionally carries no historical IPO datasets. Every availability answer must be rebuilt from sources fetched during the current invocation.

Use [references/data_sources.md](references/data_sources.md) when explaining provenance, cross-check rules, or source limitations.
