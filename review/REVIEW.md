# Adversarial review — Acquired portfolio backtest

Reviewed 2026-09-10 against `rules.md`, `backtest.py`, the CSVs, `results.csv`/`summary.json`
(as-of 2026-09-09), the earlier notes in this folder, and fresh yfinance pulls. No project file
outside `review/` was edited.

**Headline under review:** $23,727 invested → $99,843 (4.21x, XIRR 20.3%) vs S&P 500 TR 2.97x / 15.4%.

**Corrected headline (all fixes below applied):** ~$24,130 → ~$101,430 (4.20x, XIRR ~20.3%) vs S&P 2.97x / 15.4%.
The multiple, XIRR and the beat over the index are unchanged to the stated precision; the two dollar
figures move by ~2%.

---

## Findings, ranked by headline impact

### 1. Cost basis is understated for every dividend payer (script bug) — invested −$488, value −$1,712

**What's wrong.** `run_backtest` sets `buy_price = adj_close0 * sf` (line 222) and `lot_series` seeds
`shares = split_factor(...)` (line 135). `adj_close0` comes from `yf.download(auto_adjust=True)`, which is
adjusted for splits **and dividends**. Multiplying by the split factor undoes the split adjustment but
not the dividend adjustment, so `buy_price = actual_close × D(t0)`, where `D(t0) < 1` is Yahoo's
cumulative dividend factor from the buy date to today. The lot's value is scaled by the same `D(t0)`, so
per-lot `return_pct` is exactly right (it is the true total return) but the dollar cost and dollar value
of every dividend-paying lot are too small. Rule 28 ("cost equals the real close that day") is violated.

**Evidence.** `review/independent_lots.csv`, column `cost_ratio` = model cost ÷ actual close:
VZ ep41 0.612 (model $29.43, actual $48.09), HPE ep39 0.766, NSRGY ep43 0.789, QCOM ep45 0.793,
SBUX ep31 0.814, MSFT ep8 0.876, AAPL ep5 0.899. Non-payers (AMZN, TSLA, META pre-2024, SNAP...) are 1.000.
The `--selftest` fixtures have no dividends, so the test cannot catch this.

**Headline effect.** Re-running the sum with actual closes: invested $23,727 → **$24,215**, value
$99,843 → **$101,555**, multiple 4.208 → **4.194**, XIRR 20.34% → **20.30%**. Benchmark $70,496 →
$71,950, multiple 2.971 unchanged (it is funded with the same dollars). Ranking of best/worst lots is
unchanged; `gain_usd` for dividend payers is understated (e.g. MSFT ep8 $447 → $510, Hermès −$68.82 → −$70.92).

**Fix (backtest.py — this is a script bug, not a data error, so rule 16 does not apply).** Replace the
split-only factor with the full "real close ÷ adjusted close" factor `F(t) = Close_unadj(t) × S(t) / AdjClose(t)`:

- In `fetch_splits` also keep `raw[t]["Close"]` and `raw[t]["Adj Close"]` from the `auto_adjust=False`
  download (cache to `divfactor.csv`), giving `D(t) = AdjClose(t)/Close(t)` per ticker/date (this ratio
  cancels whatever split adjustment Yahoo applied to `Close`, so it is safe for every ticker).
- Add `def adj_factor(splits_df, div_df, ticker, date): return split_factor(...) / D(ticker, date)`
  (return `split_factor` unchanged when the ticker has no `div_df` column, e.g. manual-price tickers).
- Use `adj_factor` instead of `split_factor` at lines 135, 142, 146, 150 and 221. `buy_price` then equals
  the actual close; `actual_shares` at a takeout becomes `adj_shares / F(cur, date)`, which correctly
  equals 1 share grown by reinvested dividends. Today every cash/stock takeout is on a manual-price
  ticker (D = 1), so only the seed and `buy_price` lines change numbers, but do all five so the next
  Yahoo-priced takeout doesn't overpay.
- Add a dividend step to the `--selftest` fixture (e.g. AAA adj close 9.5 → 10 on the buy day with
  unadjusted 10) and assert `buy_price == 10`.

Minimal alternative if you refuse to touch the script: report `total_invested` from actual closes
(available in `review/independent_lots.csv`) and rescale each lot by `1/cost_ratio` in `build_report.py`.
Not recommended — it leaves `results.csv` wrong.

### 2. ep43 Blue Bottle / NSRGY should be skipped — invested −$85, value −$121

Nestlé announced the 68% stake 2017-09-14 and closed it at end of October 2017; air date is 2017-10-07.
By the dataset's own precedent (Jet ep18, GitHub ep56, WeWork ep83 all skipped for announced-not-closed
deals) this row fails the rule-5 test. Separately, Nestlé sold Blue Bottle to Centurium Capital
~2026-04-27, so even if kept the lot is missing a divest event. Sources in `review/mapping_check.md` §1/1b.

**Fix (episodes.csv row ep43):** `ticker=`, `parent=`, `status=skipped`, note the close date. Counts
become 114 bought / 55 skipped. If you keep it instead, add to events.csv:
`NSRGY,2026-04-27,divest,,,,"ep43; Nestlé sold Blue Bottle to Centurium Capital ~2026-04-27; sell per rule 5"`
(NSRGY adj close that day $102.25 vs $95.76 held today, i.e. +$6.49).

**Headline effect.** On top of #1: invested $24,215 → $24,130, value $101,555 → $101,433, multiple 4.204.

### 3. YHOO divest price is wrong — value −$3.90

`manual_prices.csv` sells YHOO on 2017-06-13 at $55.90 (extrapolated from a $55.71 close on 06-08).
Two independent lookups put the actual 2017-06-13 close at **$52.00** (and $52.58 on 06-16, the last
YHOO session — consistent with the low-$52 range that week). Source: historicalstockprice.com YHOO history,
cross-checked with Fortune/Yahoo Finance coverage of the Altaba conversion (`mapping_check.md` §2).

**Fix (manual_prices.csv):** `YHOO,2017-06-13,52.00,...`. ep30 return 24.2% → 15.6%.

### 4. Non-split factors in `splits.csv` — how the script actually handles them

`split_factor` (line 106) multiplies every non-zero entry in Yahoo's "Stock Splits" series strictly after
the buy date. Whether that is right depends on whether Yahoo *also* adjusted the price series by the
same factor. Checked each odd factor against the unadjusted `Close` series (`yf.download(auto_adjust=False)`):

| Ticker | Yahoo factor | Real event | Yahoo prices adjusted? | Lots affected | Model effect |
|---|---|---|---|---|---|
| HPE 2017-04-03 | 1.3348 | DXC spin | **No** (Close 13.78 → 13.63, continuous; Adj/Close ratio 0.766 flat across it) | none (ep39 bought 08-04) | none |
| HPE 2017-09-01 | 1.289 | Micro Focus spin-merger | **No** (Close 14.01 → 14.31) | ep39 | shares ×1.289 with no offsetting price adjustment. Cost = 13.58 × 0.766 × 1.289 = **$13.41** (coincidentally ≈ real $13.58, because 0.766 × 1.289 ≈ 0.99). Divest cash = 1.289 × adj(09-01) = **$14.12**. True value of 1 HPE share on 09-01 = $14.31 HPE + 0.13733 MF ADS × ~$28.4 = **~$18.2**. After fix #1 the model gives 1.289 × 14.31 = $18.45, i.e. the spurious factor happens to approximate the spun-off value. Net headline effect ≈ +$4. |
| FWONK 2016-04-18 | 1.366 | tracking-stock recap | n/a | none | none |
| FWONK 2023-07-20 | 1.017 | Liberty Live reclass (real date 08-03) | Close continuous | none (ep165 bought 2026-03-02) | none |
| SSP 2025-12-08 | 1.33 | poison-pill rights dividend (non-economic; SEC 8-K 2025-11-26) | **Yes** — Yahoo divided all pre-12-08 prices by 1.33 (Close 3.27 on 12-05 vs 4.52 on 12-08 = real ~4.35 → 4.52) | ep16 | Cancels exactly: cost = (17.73/1.33) × D × 1.33 = 17.73 × D; divest cash on 2020-10-19 = 1.33 × (real/1.33) × D = real × D. Value $10.12 vs SSP's ~$10.6 close that day × D 0.955. **Correct — do not remove this row**, removing it would make the lot 25% too small. |
| SFTBY 2019-07-11 | 2.0 | **real** for ADR holders: ordinary 2:1 split 2019-06-28, ADR ratio stayed 0.5 sh/ADR | Yes | ep51, ep69 | Correct. Cost $39.14 vs actual ADR close $39.35 (dividend factor only). The "1:10 reverse split" claim in the earlier research is wrong. |
| SFTBY 2026-01-08 | 4.0 | real (Tokyo 4:1 effective 2026-01-01, ADR 01-08) | Yes | ep51, ep69 | Correct. |

**Rule of thumb:** a `splits.csv` entry is right iff Yahoo applied the same factor to the price series.
Only the two HPE rows fail that test.

**Fix (CSV-only, optional, +$4):** delete the two HPE rows from `splits.csv` and change the HPE row in
`events.csv` from `divest` to `cash_takeout` with `cash_per_share=18.21` (HPE $14.31 + Micro Focus ADS
0.13732611 × ~$28.4; the MF leg is an estimate from Micro Focus's 8-K, note "approx"). Then cost is the
real $13.58 and value $18.21 without relying on a coincidence. Note `splits.csv` is regenerated when
deleted (rule 30), so the deletion has to be re-applied after a refresh — or leave it as is and accept the
$4 error.

### 5. MPNGY and SONY — nothing mis-modelled, one small omission

- **MPNGY (ep106).** Fresh yfinance: no split recorded; unadjusted Close 20.58 (04-02) → 20.68 (04-06)
  → 22.58 (04-08), continuous with 3690.HK ~HK$80 × 2 shares/ADS ÷ 7.8. SEC F-6EF filings from 2019 and
  2025 both say 1 ADS = 2 Class B shares. **The "1:100 reverse split 2026-04-06" claim is false**
  (almost certainly a confusion with Lixiang Education's April 2026 ADS ratio change). No action.
- **SONY (ep122).** Sony distributed 1 Sony Financial Group share per Sony share (record 2025-09-30,
  effective 10-01); JPMorgan distributed SFGI ADRs to SONY ADR holders. Yahoo recorded no dividend or
  split and SONY's Close/Adj Close are identical around 10-01, so the model silently drops the SFGI
  stub — roughly 4–5% of Sony's value at the time (SFGI ~¥1.0–1.2T vs Sony ~¥26T). Effect on the lot:
  ~+$4–5 on a $117 position. **Fix (optional):** add `SONY,2025-10-01,...` as a `cash_takeout`-style
  partial is not supported by the script; simplest honest treatment is a note in `results.csv`/report
  ("excludes ~4% SFGI spin-off"). Not worth a script change.

### 6. Air-date discrepancies (ep2, 73, 124, 141) — ≤ $15 each

`episodes_check.md` §1. RSS pubDates carry Pacific offsets and are the better source; acquired.fm's
`datePublished` looks off by a day for ep124/ep141. Sensitivity if you adopt the page dates:
ep2 META: buy still 2015-11-02 (both dates are a weekend) — no change. ep124 NVDA: buy still 2022-03-28 — no change.
ep73 UBER: 2019-05-10 (IPO day, real close $41.57) instead of 05-13 ($37.10): cost +$4.47, value same.
ep141 NVDA: 2023-09-06 ($469.2 real) instead of 09-05 ($485.48): cost −$16.3. The CSV's own ep73
`source_note` says the IPO was 05-10, so at least fix that inconsistency (either date or note).

### 7. Missing episode: S12E1 "The NFL" (~2023-01-25) — counts only

Not a company; would be `skipped`. Add the row for completeness: 170 episodes / 55 skipped (56 with
Blue Bottle). No dollar effect.

### 8. ep138 Porsche — judgment call, document it

A US OTC ADR (DRPRY, ~9,500 shares/day) existed at air date; rule 7 says use the ADR. Keeping P911.DE is
defensible on liquidity but the `source_note` "no US ADR" is false. Switching would change the lot from
cost $118.72 → $11.83 and value ~$58 → ~$6 (−$107 invested, −$52 value). **Fix:** either switch, or edit
the note to "DRPRY exists but is too thin; using primary listing". Recommend the latter.

### 9. Minor / confirmed OK

- All 12 `events.csv` rows confirmed (dates and prices). Stitcher/SSP divest is 2020-10-19 vs actual close
  2020-10-16: 1 trading day, immaterial.
- All 41 `manual_prices.csv` rows confirmed or anchored within 2% except YHOO 06-13 (finding #3).
- Manual-price lots (YHOO, LNKD, TWTR, ATVI, WFM, VA, WORK, EB, EA) ignore dividends entirely (rule 8 says
  reinvest). ATVI 2017–2023 paid ~$3.4/share cumulative; EA ~$4; the rest negligible. Understates value by
  ~$8 total. Acceptable; say "dividends ignored on hand-priced delisted tickers" in the report.
- `n_flagged=63` counts skipped rows (their `flag` is the source note). Cosmetic; if reported, say 9 lots
  flagged for manual pricing.
- Three wrong episode URLs in `episodes.csv` source notes (ep58, 59, 71) — see `episodes_check.md`.

---

## XIRR and benchmark — verified

- **Benchmark.** `^SP500TR` is the S&P 500 total-return index; each lot's `buy_price` is invested at the
  first index close on/after the air date and marked at the last index close. `review/independent_check.py`
  rebuilt this from a fresh download and got **$70,496 — the exact `summary.json` figure**. One nit: the
  benchmark buys at the air-date close (`buy_fill(prices, bench_ticker, row.air_date)`) while the stock
  buys at `buy_date`, which can differ by a day for foreign-holiday fills. Negligible.
- **XIRR.** Cash flows are `−buy_price` on each `buy_date` plus the terminal value on the as-of date;
  bisection on [−99%, 1000%] with ACT/365 day count; the same flows are used for portfolio and benchmark,
  so the 20.3% vs 15.4% comparison is like-for-like. Independent recompute: 0.2034 / 0.1539, matching.
  Because finding #1 scales cost and value of each lot together, XIRR moves only through re-weighting:
  20.34% → 20.30%. Benchmark XIRR unchanged.
- **As-of date** correctly clipped to the last completed `^SP500TR` close (2026-09-09).

---

## Verdict

**The headline is defensible.** The two ratios people will quote — 4.2x vs 3.0x, and 20% vs 15% money-
weighted — survive every correction found; the largest change to either is 0.014x on the multiple. The
per-lot returns are true total returns and the benchmark is a genuine like-for-like total-return
comparison. What is *not* accurate as posted are the dollar figures: "$23,727 invested" is ~2% too low
because dividend-adjusted prices were used as cost, and "$99,843" is low by the same mechanism.

Concentration caveat worth stating in the post (from `independent_check.py`): of ~$77k of gain, GOOGL
lots contribute ~$35k, AMZN ~$12.6k, AAPL ~$6.2k, NVDA ~$5.7k, TSLA ~$5.2k — five tickers are ~83% of
the gain, and six of the GOOGL lots are 2016–2018 "Google product" episodes (rule 23).

### Must fix before posting

1. **Cost-basis / dividend factor (finding #1)** — script change in `backtest.py` as specified; re-run.
   Headline becomes ~$24.2k → ~$101.5k. Without this, the two dollar figures in the post are wrong.
2. **Blue Bottle ep43 → skipped (finding #2)**, or add the 2026-04-27 NSRGY divest. Consistency with the
   dataset's own rule.
3. **YHOO 2017-06-13 → $52.00 (finding #3)** in `manual_prices.csv`.
4. **Fix the ep73 date/note contradiction** (finding #6) — one of them is wrong on its face.

### Should fix (cheap, improves rigor, no headline effect)

5. HPE: delete the two spin-off rows from `splits.csv` and make the 2017-09-01 event a `cash_takeout`
   at ~$18.21 (finding #4).
6. Add "The NFL" S12E1 as a skipped row; fix the ep58/59/71 URLs; correct the Porsche note.
7. Say in the report that the SONY lot excludes the ~4% Sony Financial spin-off and that hand-priced
   delisted tickers ignore dividends.

### Do not "fix"

- SSP 1.33 and SFTBY 2.0 / 4.0 in `splits.csv` — they match Yahoo's price adjustments and are correct.
- MPNGY — no reverse split happened.
