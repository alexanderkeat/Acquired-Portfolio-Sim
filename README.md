# Acquired Portfolio Sim

Every episode of the [Acquired](https://www.acquired.fm) podcast opens with "this is not investment advice." What if it were?

This backtest buys **one share** of every publicly traded company covered on Acquired's main feed, at the close on the day the episode aired, from October 2015 onward, and compares it with the same dollars invested in the S&P 500 total return index on the same dates.

**Interactive report:** https://claude.ai/code/artifact/d36bbe9e-bbc7-4918-b4c8-37a264c92934

## Headline (as of 2026-09-11 close)

| | Acquired portfolio | S&P 500 TR, same dollars |
|---|---|---|
| Invested | $24,130 | $24,130 |
| Value | $102,977 | $71,860 |
| Multiple | 4.27x | 2.98x |
| XIRR | 20.5% | 15.4% |

114 episodes bought, 55 skipped as private or not about a company.

## Files

- `rules.md` — every methodology decision, numbered (36 so far). Start here.
- `episodes.csv` — one row per main-feed episode: subject, ticker, parent, status, source note.
- `events.csv` — corporate actions on held positions (takeouts, divestitures).
- `manual_prices.csv` — hand-researched closes for delisted tickers Yahoo no longer serves.
- `backtest.py` — pulls prices via yfinance, runs the simulation, writes `results.csv`, `timeseries.csv`, `summary.json`, `chart.png`. Has a `--selftest`.
- `build_report.py` — fills `report.html` from the outputs.
- `review/` — adversarial review notes and an independent recomputation.
- `batches/` — raw research output per 25-episode batch, kept as an audit trail.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas yfinance matplotlib
.venv/bin/python backtest.py --selftest
.venv/bin/python backtest.py
.venv/bin/python build_report.py
```

Corrections go in the CSVs, never the script.

## Caveats

Nine delisted tickers use sparse hand-researched prices. Cash from buyouts earns nothing. No taxes or fees. One share means results are dominated by whatever was expensive on air date, mostly pre-split Alphabet and Amazon. Unofficial fan project, not affiliated with Acquired. Not investment advice.
