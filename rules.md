# Acquired Portfolio — Rules

Decisions made on 2026-09-04. Update this file whenever a rule changes.

## What gets bought
1. **Main feed only.** No ACQ2, Arena Show, or specials.
2. **One share per episode**, bought at the close on the air date. Weekend/holiday air dates buy at the next close.
3. **Multi-part series** count each part as its own episode and buy again.
4. **Subject is public** → buy the subject's ticker.
5. **Subject was acquired before air date** → buy the public acquirer (Instagram → META, Pixar → DIS). If the acquirer later divests the subject, **sell that share on the divestiture date** and hold cash.
6. **Subject is private, no public parent** → skip, but count and report it.
7. **Non-US companies** → buy one US ADR share where one exists; otherwise the primary listing converted to USD daily.

## What happens after buying
8. **Dividends reinvested** (total return). Splits tracked.
9. **Cash takeout** → position becomes cash at the deal price, held at 0% thereafter.
10. **Stock takeout** → shares convert into acquirer shares at the exchange ratio, plus any cash component.
11. **Delisted tickers with missing Yahoo history** → valued at deal price from the deal date; flagged in results.

## Benchmark and reporting
12. **Benchmark:** same dollars, same dates, into S&P 500 total return (`^SP500TR`, fallback SPY adjusted).
13. **Metrics:** total invested, current value, multiple, money-weighted annualized return (XIRR), per-episode return and contribution.
14. **Ignored:** transaction costs, taxes, interest on cash.

## Process
15. Research done by Sonnet sub-agents, ~25 episodes per batch, one source note per row.
16. Corrections go into the CSVs only, never the script.
17. Deliverables: `episodes.csv`, `events.csv`, `backtest.py`, `results.csv`, `timeseries.csv`, `chart.png`, `report.html`.

## Review decisions (2026-09-04)
18. **WeWork (ep83)** → skipped. SoftBank's rescue stake was announced but not closed at air date and never gave control.
19. **Overture (ep30)** → buy Yahoo (YHOO); divest 2017-06-13 when Yahoo sold its operating business to Verizon.
20. **AOL (ep41)** → buy Verizon; divest 2021-09-01 when Verizon sold AOL/Yahoo to Apollo.
21. **Opsware (ep39)** → buy HPE; divest 2017-09-01 on the Micro Focus software spin-merger. Marked approx.
22. **GitHub (ep56)** → skipped. Microsoft deal announced the day before but closed months later; strict air-date rule.
23. **Organic products** (Google Maps, AWS, Disney+) → `public` on the parent's own ticker.
24. **Delisted tickers with no Yahoo history** (YHOO, LNKD, TWTR, ATVI, WFM, VA, WORK) → sparse hand-researched closes in `manual_prices.csv`, linearly interpolated; flagged in results.
25. **Xiaomi (ep59)** → 1810.HK converted to USD; the US ADR only starts in 2024.
26. **Ticker class picks:** Zillow Z, Berkshire BRK-B, Formula 1 FWONK, Alphabet GOOGL.
27. **Late takeouts found during the run:** Eventbrite (ep97) cash takeout by Bending Spoons at $4.50 on 2026-03-10; Electronic Arts (ep74) cash takeout by PIF/Silver Lake/Affinity at $210 on 2026-08-04. Both use `manual_prices.csv` history.
28. **Splits:** one share means one actual share on air date. The script scales each lot by the split factor after its buy date so cost equals the real close that day (e.g. NVDA at ~$280 in 2022, not $28).
29. **Manual prices override Yahoo** for any ticker in `manual_prices.csv`, because Yahoo keeps misleading stubs for some delisted tickers.
30. **As-of date** = last completed close in the benchmark series, not the calendar date. Refresh by deleting `prices.csv` and `splits.csv`, then rerunning `backtest.py`; `build_report.py` regenerates `report.html` from the outputs.

## Adversarial review fixes (2026-09-10, see review/REVIEW.md)
31. **Cost basis uses the real close.** Adjusted closes also fold in dividends, so the script now scales each lot by real close ÷ adjusted close on the buy date. Per-lot returns were already right; dollar cost and value were understated for dividend payers.
32. **Blue Bottle (ep43)** → skipped. Nestlé's deal closed late October 2017, after the 2017-10-07 air date. Same standard as Jet, GitHub, WeWork.
33. **Yahoo divest price** corrected to $52.00 on 2017-06-13.
34. **Uber IPO (ep73)** note clarified: IPO was 2019-05-10, episode aired Sat 2019-05-11, bought Mon 2019-05-13. Date kept from RSS.
35. **Porsche (ep138)** stays on Frankfurt P911.DE. The US ADR DRPRY exists but is illiquid; documented judgment call.
36. **Not changed on purpose:** SSP 1.33 and SFTBY 2.0/4.0 adjustment factors match Yahoo's price series and are correct; Meituan had no reverse split; the "NFL" remaster (S12E1) is excluded as a rebroadcast and would be skipped anyway; the Sony Financial spin-off (~4% of the SONY lot) is not modelled.
