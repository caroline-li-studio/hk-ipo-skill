# Data Sources And Limitations

## Local Project

Default project path:

`/Users/jialu/Documents/Codex/HK IPO`

Original user path may also appear as:

`/Users/jialu/Documents/Code/HK IPO`

The project has been pushed to:

`https://github.com/caroline-li-studio/hk-ipo`

## Important Files

- `data/processed/ipo_clean_enriched.csv`: preferred scoring dataset. It has broad coverage and application start dates.
- `data/processed/ipo_deals.csv`: normalized pipeline dataset. Useful for model features, but current application date fields may be blank.
- `data/models/<version>/<stage>/bundle.joblib`: legacy trained prediction bundles. Treat them as optional historical artifacts, not the primary skill workflow.
- `data/reports/backtest_summary.json`: optional context for discussing why old ML predictions should not be overtrusted.

## Known Limitations

- Some source systems disagree on stock code formatting. Normalize codes to five digits plus `.HK` where possible.
- `apply_end_date` is often unavailable. The scorer estimates the active window from `apply_start_date` and `listing_date`.
- Current local data may not include IPOs announced after the latest collection run.
- Backtests show stronger signal for some T2 classification tasks than for early-stage return regression. The skill should be LLM-first: extract evidence deterministically, then let Codex reason with the scoring rubric.
