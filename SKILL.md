---
name: hk-ipo-skill
description: Analyze Hong Kong IPO subscription opportunities. Use when Codex needs to list Hong Kong stocks available for retail IPO subscription at a specific date or time, score each active IPO, rank 港股打新 candidates, explain IPO scoring factors, or inspect the local HK IPO prediction project derived from /Users/jialu/Documents/Codex/HK IPO.
---

# HK IPO Skill

Use this skill to answer questions such as:

- "今天有哪些港股可以打新？给我评分。"
- "2026-03-23 可以申购哪些港股？排序并分析。"
- "帮我看 00664.HK 是否值得打新。"

## Quick Start

For current or date-specific IPO availability, use live web sources first. Search and open the source pages listed in [references/data_sources.md](references/data_sources.md), then use the scoring rubric to reason over the evidence.

Use the bundled evidence extractor only as a local cache fallback or for historical smoke tests:

```bash
python ~/.codex/skills/hk-ipo-skill/scripts/score_active_ipos.py --as-of YYYY-MM-DD --format markdown
```

Use `--format json` when the result should feed another tool. Use `--top N` to limit output.

The script reads the local HK IPO project from `HK_IPO_PROJECT` when set; otherwise it tries:

1. `/Users/jialu/Documents/Codex/HK IPO`
2. `/Users/jialu/Documents/Code/HK IPO`
3. the current working directory

## Workflow

1. Parse the user's date/time. If absent, use the current local date.
2. Query live sources first: AASTOCKS IPO, ETNet IPO calendar/info, Futu/Moomoo IPO pages, CNYES/财华/券商 IPO calendars, and issuer/prospectus pages when needed.
3. Determine active retail-subscription candidates from live application/open/close dates. Treat listing-only rows as not sufficient unless application dates show the date falls inside the subscription window.
4. Use the rubric in [references/scoring.md](references/scoring.md) to assign final 0-100 scores, ratings, and explanations yourself.
5. Summarize in Chinese unless the user asks otherwise.
6. Keep the investment language cautious: this is a打新辅助评分, not financial advice.
7. Use `score_active_ipos.py` only if live sources are unavailable or as a cache sanity check. If live and local cache disagree, prefer live sources and mention the conflict.

## Scoring Semantics

The script produces evidence fields, not final investment decisions:

- `evidence_quality`: rough completeness band.
- `deterministic_priority`: sorting hint only, useful for table order.
- `evidence_drivers`: extracted quantitative facts.
- `risk_notes`: missing-data warnings.

Codex should provide the final `score` and `rating` using reasoning over the evidence, not by copying `deterministic_priority`.

Read [references/scoring.md](references/scoring.md) before changing weights or interpreting edge cases.

## Data Notes

The source project was committed and pushed to `https://github.com/caroline-li-studio/hk-ipo` before this skill was created. It contains the original pipeline and local artifacts used by this skill.

The local scorer prefers `data/processed/ipo_clean_enriched.csv` because it contains historical and upcoming IPO rows with `apply_start_date`, but local processed files are stale by nature. Never use local data as the only source for a live/date-specific availability answer when web access is available.

Use [references/data_sources.md](references/data_sources.md) when explaining provenance or limitations.
