# Data Sources And Limitations

## Live Sources First

Use live sources before local cache for any question about "today", a specific date, current subscriptions, or whether an IPO can be subscribed:

- AASTOCKS IPO main page: `https://www.aastocks.com/sc/stocks/market/ipo/mainpage.aspx`
- ETNet IPO calendar/info: `https://www.etnet.com.hk/www/tc/stocks/ipo-calendar.php` and `https://www.etnet.com.hk/www/tc/stocks/ipo-info.php`
- Futu/Moomoo HK IPO pages: `https://www.moomoo.com/hans/quote/hk/ipo?from=futunn` and related issuer pages
- CNYES HK IPO: `https://www.cnyes.com/hkstock/ipo`
- Hong Kong broker IPO calendars such as 新質證券 and 耀才/財華 pages when search finds them
- HKEX listing documents or the prospectus when issue details need confirmation

The key fields to extract are stock code, company name, application start date, application close date, listing date, offer price/range, lot size or entry fee, sponsor, industry, and public subscription/margin/lottery details when available.

## Local Project Fallback

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
- Local processed data is only a fallback/cache. Prefer live sources for date-specific availability.
- Backtests show stronger signal for some T2 classification tasks than for early-stage return regression. The skill should be LLM-first: extract evidence deterministically, then let Codex reason with the scoring rubric.
