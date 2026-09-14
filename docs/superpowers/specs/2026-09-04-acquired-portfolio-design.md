# Acquired Portfolio Backtest — Design

**Question:** If you bought one share of every publicly traded company covered by the Acquired podcast (main feed) on the day the episode aired, how would that portfolio have performed, historically and today?

## Scope

- **Episodes:** main feed only (acquired.fm), from episode 1 in 2015 through the latest episode as of 2026-09-04. No ACQ2, Arena Show, or specials.
- **One share per episode.** Multi-part series (e.g. Nvidia parts I–III) count each part as a separate episode and buy again.
- **Subject → security mapping:**
  - Subject trades publicly at air date → buy that ticker.
  - Subject was acquired before air date and the acquirer is public (Instagram → META, Pixar → DIS, Whole Foods → AMZN) → buy the acquirer. If the acquirer later divests the subject, sell that share on the divestiture close and hold cash.
  - Subject is private with no public parent (Epic Games, SpaceX, Stripe) → row marked `skipped`, counted and reported.
  - Non-US companies: buy one US ADR share where one exists (NTDOY, LVMUY, TSM, etc.). Otherwise buy one share of the primary listing and convert to USD daily via yfinance FX.
- **Purchase timing:** close on air date. Weekend/holiday air dates buy at the next trading close.

## Corporate actions on held positions

Recorded in `events.csv` and applied by the script:

| type | fields | effect |
|---|---|---|
| `cash_takeout` | date, cash_per_share | position → cash, held at 0% thereafter |
| `stock_takeout` | date, acquirer_ticker, ratio, cash_per_share (optional) | shares × ratio of acquirer, plus any cash |
| `divest` | date | sell the parent share at close, hold cash |

Splits and dividends come from yfinance adjusted closes (dividends treated as reinvested, i.e. total return).

**Known limitation:** Yahoo often lacks price history for delisted tickers (LNKD, TWTR, ATVI, …). For those, value the position at the deal price from the deal date forward and, where pre-deal history is missing, from the purchase date forward at cost until the deal. Every such row is flagged in the results.

## Benchmark

Same dollars invested on the same dates into an S&P 500 total return proxy (`^SP500TR`, fallback `SPY` adjusted close). Dollar-weighted, so the comparison is fair to the drip-in nature of the portfolio.

## Outputs

Summary metrics for portfolio and benchmark: total invested, current value, multiple, money-weighted annualized return (XIRR). Per-episode: buy date, buy price, current value, return, contribution to total gain, status (held / taken out / divested / skipped).

## Files

```
episodes.csv    ep_num, title, air_date, subject, ticker, parent, status, source_note
events.csv      ticker, date, type, cash_per_share, acquirer_ticker, ratio, note
backtest.py     load CSVs → fetch prices → daily portfolio + benchmark series → results
results.csv     per-episode table
timeseries.csv  date, invested, portfolio_value, benchmark_value
chart.png       portfolio vs benchmark vs cash invested
report.html     artifact: curve, summary block, sortable per-episode table
```

`status` values in episodes.csv: `public`, `parent`, `skipped`.

## Research pipeline (Sonnet sub-agents)

1. One agent scrapes the full main-feed episode list (number, title, air date) from acquired.fm into `episodes.csv` with empty mapping columns.
2. Episodes split into batches of ~25. One agent per batch fills `subject, ticker, parent, status, source_note` and appends any corporate-action rows to `events.csv`. Each row carries a one-line source note.
3. Human/lead review of the CSVs, focusing on `parent` and `skipped` rows and every event, before the backtest runs.
4. Hand corrections go only into the CSVs, never the script.

## Testing

- `backtest.py` has a small self-check: a synthetic two-ticker fixture with one split, one dividend, and one cash takeout must produce a known portfolio value.
- Sanity checks on real data: no negative values, invested series is monotone, every `public`/`parent` row has a price on its buy date or an explanatory flag.

## Out of scope

Transaction costs, taxes, interest on cash, ACQ2/specials, position sizing other than one share.
