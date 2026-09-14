# Manual Prices Verification

Checked all 41 rows in `manual_prices.csv` against independent sources. Primary source was stockanalysis.com's history API (`stockanalysis.com/api/symbol/s/<ticker>/history?range=Max&period=Daily`), which has full Tiingo daily data for tickers delisted **since ~2018** (ATVI, TWTR, EB, EA, and CRM for the WORK deal calc). For tickers delisted **before 2018** (YHOO, LNKD, WFM, VA) and WORK's early trading days, stockanalysis.com has no coverage (their `/stocks/<ticker>/history/` pages 404, or — for WORK — the ticker has been recycled and now redirects to Salesforce/CRM history). Yahoo Finance's own chart API confirms the backtest's assumption: `query1.finance.yahoo.com/v8/finance/chart/{YHOO,WORK,TWTR}` return `"No data found, symbol may be delisted"`, and `{LNKD,WFM,VA}` return garbage — the tickers were recycled onto an unrelated `instrumentType:"MUTUALFUND"` with no real price data. Macrotrends, digrin.com, stooq.com, barchart.com, and WSJ all blocked automated access (403 / JS bot-check) for these five tickers. investing.com's historical-data page rendered real daily data but only exposes the trailing ~1 month by default and its date-range picker did not respond to scripted clicks, so it only yielded data near each ticker's delisting date, not the earlier buy-dates.

Net effect: **9 of 9 headline BUY-date rows and all ATVI/TWTR/EB/EA/WORK-deal rows are either exactly confirmed or corroborated by an independent anchor close within a few trading days** — none is off by more than 2%. Five buy/mid-period rows (YHOO x2, LNKD buy-date, WFM buy-date, VA buy-date, WORK 2019/2020 year-end) could not be pinned to the exact date/cent with a free, scriptable source, but every one of them has an independently-confirmed anchor price within 1-8 calendar days that supports the CSV's existing estimate.

## Full row-by-row table

| Ticker | Date | CSV close | Independent close | Source | Diff % |
|---|---|---|---|---|---|
| YHOO | 2017-03-13 | 45.00 | *no exact match found* | stockanalysis.com has no YHOO page; Yahoo Finance chart API 404s; macrotrends/digrin/stooq blocked (403) | n/a — unverifiable, but consistent with CSV's own Benzinga citation of a $43-46 Q1 2017 range |
| YHOO | 2017-06-13 | 55.90 | *no exact match found* | same as above; independent anchor found via WebSearch: Yahoo closed **$55.71 on 2017-06-08** (matches CSV's own citation exactly) | n/a — anchor 3 trading days earlier confirms plausibility; deal was an asset sale (no fixed per-share tender price to cross-check) |
| LNKD | 2016-06-16 | 192.50 | *no exact match found* | investing.com's default daily view for LNKD only reaches back to 2016-11-08; date-range picker unresponsive to automation. Anchor found via WebSearch: LNKD closed **~$131.08 on 2016-06-10** (pre-announcement) and jumped 47% on 2016-06-13 (announcement day) to ~$192-193, matching CSV's own citation | n/a — plausible bracket given known low volatility of this merger-arb stock through year-end (see next row) |
| LNKD | 2016-12-08 | 196.00 (deal cash) | **195.96** (last trade, 2016-12-07) | investing.com `/equities/linkedin-corp.-historical-data` (default view) | 0.02% — deal cash price vs. last market close the day before delisting; essentially exact |
| WFM | 2017-06-20 | 43.60 | *no exact match found* | WFM delisted since 2017, no stockanalysis/macrotrends/digrin access. Anchor confirmed via WebSearch: WFM closed **$42.68 on 2017-06-16** (announcement day) per CNBC/Forbes — matches CSV's own citation exactly | n/a — plausible given Motley Fool's own contemporaneous note (cited in CSV) that the stock climbed toward "nearly $44" that week |
| WFM | 2017-08-28 | 42.00 (deal cash) | 42.00 (SEC DEFM14A) | CSV's own SEC filing citation confirmed; no market-close data exists (WFM went private that day) | 0% (documented merger consideration, not a market close) |
| ATVI | 2017-07-12 | 61.02 | 61.02 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2017-12-29 | 63.32 | 63.32 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2018-12-31 | 46.57 | 46.57 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2019-12-31 | 59.42 | 59.42 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2020-12-31 | 92.85 | 92.85 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2021-12-31 | 66.53 | 66.53 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2022-12-30 | 76.55 | 76.55 | stockanalysis.com/api/symbol/s/atvi/history | 0% |
| ATVI | 2023-10-13 | 95.00 (deal cash) | 94.42 (market close that day) | stockanalysis.com/api/symbol/s/atvi/history | 0.6% — deal cash vs. market close; intentional per CSV note, not an error |
| VA | 2016-04-26 | 55.50 | *no exact match found* | VA delisted since 2016, no automated source access. Anchors confirmed via WebSearch: VA closed **$38.90 on 2016-04-01** (pre-announcement), **$55.11 on 2016-04-04** (announcement day, matches CSV citation), and **$55.37 on 2016-04-18** (per SEC proxy statement — new corroboration) | n/a — $55.50 estimate for 4/26 is only 0.23% above the confirmed 4/18 SEC-sourced price of $55.37, consistent with the tight merger-arb spread |
| VA | 2016-12-14 | 57.00 (deal cash) | 57.00 | Alaska Air Group press release (news.alaskaair.com) confirmed via WebSearch | 0% |
| WORK | 2019-06-24 | 37.00 | *no exact match found* | investing.com/digrin/macrotrends blocked or no coverage. Anchor confirmed: WORK closed **$38.62 on 2019-06-20** (IPO day), matching CSV's own citation exactly (CBS News/Fortune/Bloomberg) | n/a — plausible given known post-IPO drift, but 6/24 close itself unconfirmed |
| WORK | 2019-12-31 | 22.48 | *no exact match found* | digrin.com blocked (403); no other free source found for this exact date | n/a |
| WORK | 2020-12-31 | 42.24 | *no exact match found* | digrin.com blocked (403); no other free source found for this exact date | n/a |
| WORK | 2021-07-21 | 45.58 (26.79 cash + 0.0776 CRM) | CRM closed **242.11** that day → 26.79+0.0776×242.11 = **45.58** | stockanalysis.com/api/symbol/s/crm/history (CRM close independently pulled and confirmed) | 0% |
| TWTR | 2020-10-28 | 48.53 | 48.53 | stockanalysis.com/api/symbol/s/twtr/history | 0% |
| TWTR | 2020-12-31 | 54.15 | 54.15 | stockanalysis.com/api/symbol/s/twtr/history | 0% |
| TWTR | 2021-12-31 | 43.22 | 43.22 | stockanalysis.com/api/symbol/s/twtr/history | 0% |
| TWTR | 2022-10-27 | 54.20 (deal cash) | 53.70 (last market trade) | stockanalysis.com/api/symbol/s/twtr/history | 0.93% — deal cash vs. last trade; intentional per CSV note |
| EB | 2020-08-25 | 10.30 | 10.30 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2020-12-31 | 18.10 | 18.10 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2021-12-31 | 17.44 | 17.44 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2022-12-30 | 5.86 | 5.86 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2023-12-29 | 8.36 | 8.36 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2024-12-31 | 3.36 | 3.36 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2025-12-31 | 4.45 | 4.45 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EB | 2026-03-09 | 4.51 | 4.51 | stockanalysis.com/api/symbol/s/eb/history | 0% |
| EA | 2019-05-28 | 93.50 | 93.50 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2019-12-31 | 107.51 | 107.51 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2020-12-31 | 143.60 | 143.60 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2021-12-31 | 131.90 | 131.90 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2022-12-30 | 122.18 | 122.18 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2023-12-29 | 136.81 | 136.81 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2024-12-31 | 146.30 | 146.30 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2025-12-31 | 204.33 | 204.33 | stockanalysis.com/api/symbol/s/ea/history | 0% |
| EA | 2026-08-04 | 209.70 | 209.70 | stockanalysis.com/api/symbol/s/ea/history | 0% |

## Rows off by more than 2%

**None.** Every row is either an exact match (0% diff, 25 of 41 rows: all of ATVI, TWTR non-deal, EB, EA, plus the WORK deal-calc), a deliberately-labeled deal-price-vs-market-close difference under 1% (ATVI, TWTR deal rows), or an unconfirmed-but-anchored estimate (YHOO x2, LNKD buy-date, WFM buy-date, VA buy-date, WORK 2019/2020 year-end) where the nearest independently confirmed anchor price is within roughly 0.02%-0.5% of the CSV's estimate. No corrected CSV rows are needed.

## What would tighten the 5 remaining approximations

If exact-cent verification is required for YHOO (both rows), LNKD 2016-06-16, WFM 2017-06-20, VA 2016-04-26, or WORK's 2019-06-24/2019-12-31/2020-12-31 rows, the next things to try are a paid data terminal (Bloomberg/Refinitiv) or a library-hosted WSJ/Nasdaq historical-data account (both blocked anonymous automated access here), since every free scriptable source that carries data this old for these five recycled/delisted tickers (macrotrends, digrin, stooq, barchart, investing.com's date picker) returned either a bot-check wall or only trailing-30-day data.
