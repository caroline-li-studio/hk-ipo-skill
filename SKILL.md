---
name: hk-ipo-skill
description: Analyze Hong Kong IPO subscription opportunities from live sources. Use when Codex needs to fetch and cross-check current or date-specific Hong Kong IPO retail subscription windows, list stocks available for 港股打新, score each active IPO, rank candidates, or explain IPO scoring factors.
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
3. Cross-check candidates across multiple sources. For each IPO, confirm stock code, company name, application start date, application close date, listing date, and key offer terms where available.
4. Determine active retail-subscription candidates only from confirmed application windows. Listing-only rows are not enough.
5. Use the rubric in [references/scoring.md](references/scoring.md) to assign final 0-100 scores, ratings, and explanations yourself.
6. Summarize in Chinese unless the user asks otherwise.
7. Cite the live sources used and call out conflicts or missing fields explicitly.
8. Keep the investment language cautious: this is a打新辅助评分, not financial advice.

Read [references/scoring.md](references/scoring.md) before changing weights or interpreting edge cases.

## Data Notes

This skill intentionally carries no historical IPO datasets. Every availability answer must be rebuilt from sources fetched during the current invocation.

Use [references/data_sources.md](references/data_sources.md) when explaining provenance, cross-check rules, or source limitations.
