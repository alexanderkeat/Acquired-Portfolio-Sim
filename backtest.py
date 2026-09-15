#!/usr/bin/env python3
"""Acquired podcast portfolio backtest. See docs/superpowers/specs/2026-09-04-acquired-portfolio-design.md.

Usage:
    .venv/bin/python backtest.py            # run on episodes.csv / events.csv
    .venv/bin/python backtest.py --logy      # chart.png with log y-axis
    .venv/bin/python backtest.py --selftest  # synthetic fixture, no network
"""
import sys
import json
import datetime as dt

import pandas as pd
import numpy as np

BENCH = "^SP500TR"
BENCH_FALLBACK = "SPY"
PRICE_CACHE = "prices.csv"
SPLITS_CACHE = "splits.csv"
DIVFACTOR_CACHE = "divfactor.csv"
# ponytail: suffix -> ISO currency code, for non-ADR foreign listings. Extend if a new
# exchange shows up in episodes.csv.
FX_SUFFIX = {
    ".T": "JPY", ".PA": "EUR", ".L": "GBP", ".HK": "HKD", ".TW": "TWD",
    ".KS": "KRW", ".CO": "DKK", ".SW": "CHF", ".DE": "EUR", ".AS": "EUR",
}


def _manual_series(manual_df, dates):
    """ticker -> Series on `dates`, linearly interpolated (by date) between manual_df's
    sparse (ticker, date, close) rows. NaN before the first point, held flat after the last."""
    out = {}
    for t, grp in manual_df.groupby("ticker"):
        grp = grp.sort_values("date")
        s = pd.Series(grp.close.values, index=pd.DatetimeIndex(grp.date))
        full = s.reindex(s.index.union(dates)).interpolate(method="time")
        out[t] = full.reindex(dates).ffill()
    return out


def load_manual_prices(dates, path="manual_prices.csv"):
    """Fallback closes for delisted tickers Yahoo has no history for. See _manual_series."""
    import os
    if not os.path.exists(path):
        return {}
    manual_df = pd.read_csv(path, parse_dates=["date"])
    return _manual_series(manual_df, dates)


def fetch_prices(tickers, start, end):
    """Download adjusted close for tickers (USD-converted), cached to PRICE_CACHE."""
    import os
    tickers = sorted(set(tickers))
    if os.path.exists(PRICE_CACHE):
        cached = pd.read_csv(PRICE_CACHE, index_col=0, parse_dates=True)
        # ponytail: a column that's all-NaN (ticker had zero data last run) doesn't count as
        # "present" -- otherwise a delisted ticker with no history poisons the cache forever.
        have = {t for t in tickers if t in cached.columns and cached[t].notna().any()}
        if have == set(tickers):
            return cached  # no staleness check beyond that, delete prices.csv to force a refetch
    import yfinance as yf
    fx_needed = {FX_SUFFIX[suf] for t in tickers for suf in FX_SUFFIX if t.endswith(suf)}
    fx_tickers = [f"{c}USD=X" for c in fx_needed]
    raw = yf.download(tickers + fx_tickers, start=start, end=end, auto_adjust=True,
                       progress=False, group_by="ticker")
    out = {}
    for t in tickers + fx_tickers:
        try:
            s = raw[t]["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw["Close"]
        except KeyError:
            s = pd.Series(dtype=float)
        out[t] = s
    df = pd.DataFrame(out)
    for t in tickers:
        for suf, cur in FX_SUFFIX.items():
            if t.endswith(suf) and t in df and f"{cur}USD=X" in df:
                df[t] = df[t] * df[f"{cur}USD=X"]
    df = df[[t for t in tickers]]
    df.to_csv(PRICE_CACHE)
    return df


def fetch_splits(tickers, start, end):
    """Download split ratios (yfinance convention: 10.0 for a 10:1 split, 0.05 for 1:20
    reverse) for tickers, wide (date x ticker), cached to SPLITS_CACHE. Also downloads the
    auto_adjust=False Close/Adj Close and derives the dividend-adjustment factor
    D(t) = AdjClose(t)/Close(t) per ticker/date, cached to DIVFACTOR_CACHE. Returns
    (splits_df, div_df)."""
    import os
    tickers = sorted(set(tickers))
    if os.path.exists(SPLITS_CACHE) and os.path.exists(DIVFACTOR_CACHE):
        cached = pd.read_csv(SPLITS_CACHE, index_col=0, parse_dates=True)
        cached_div = pd.read_csv(DIVFACTOR_CACHE, index_col=0, parse_dates=True)
        if {t for t in tickers if t in cached.columns} == set(tickers):
            return cached, cached_div  # a column present (even all-NaN) means "checked, no splits"
    import yfinance as yf
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, actions=True,
                       progress=False, group_by="ticker")
    raw_unadj = yf.download(tickers, start=start, end=end, auto_adjust=False,
                             progress=False, group_by="ticker")
    out = {}
    div_out = {}
    for t in tickers:
        try:
            s = raw[t]["Stock Splits"] if isinstance(raw.columns, pd.MultiIndex) else raw["Stock Splits"]
        except KeyError:
            s = pd.Series(dtype=float)
        out[t] = s
        try:
            close = raw_unadj[t]["Close"] if isinstance(raw_unadj.columns, pd.MultiIndex) else raw_unadj["Close"]
            adjclose = raw_unadj[t]["Adj Close"] if isinstance(raw_unadj.columns, pd.MultiIndex) else raw_unadj["Adj Close"]
            div_out[t] = adjclose / close
        except KeyError:
            div_out[t] = pd.Series(dtype=float)
    df = pd.DataFrame(out)
    div_df = pd.DataFrame(div_out)
    df.to_csv(SPLITS_CACHE)
    div_df.to_csv(DIVFACTOR_CACHE)
    return df, div_df


def split_factor(splits_df, ticker, date):
    """S(date) = product of split ratios for `ticker` occurring strictly after `date`.
    1.0 for tickers with no splits (or no split data at all, e.g. manual_prices tickers)."""
    if ticker not in splits_df.columns:
        return 1.0
    s = splits_df[ticker].dropna()
    s = s[s != 0]
    if s.empty:
        return 1.0
    return float(s[s.index > pd.Timestamp(date)].prod())


def adj_factor(splits_df, div_df, ticker, date):
    """F(date) = S(date) / D(ticker, date), where D = AdjClose/Close on that date is Yahoo's
    cumulative dividend-adjustment factor. Multiplying an adjusted close by F(date) undoes
    both the split *and* dividend adjustment, recovering the actual close paid that day. Falls
    back to split_factor alone when `ticker` has no div data (e.g. manual_prices tickers)."""
    sf = split_factor(splits_df, ticker, date)
    if div_df is None or ticker not in div_df.columns:
        return sf
    d = div_df[ticker].dropna()
    if d.empty:
        return sf
    val = d.asof(pd.Timestamp(date))
    if pd.isna(val):
        return sf
    return sf / float(val)


def buy_fill(prices, ticker, air_date):
    """First close on/after air_date. Returns (date, price) or (None, None) if no data at all."""
    if ticker not in prices.columns or prices[ticker].dropna().empty:
        return None, None
    s = prices[ticker].dropna()
    after = s[s.index >= pd.Timestamp(air_date)]
    if after.empty:
        return None, None
    return after.index[0], float(after.iloc[0])


def lot_series(prices, dates, ticker, buy_date, events, splits_df, div_df, manual_tickers=frozenset()):
    """Daily (value, flag) for one ACTUAL share bought in `ticker` on buy_date, walking events.
    `shares` here is always adj_shares = actual_shares * F(t) on the currently held ticker;
    actual shares at any moment = adj_shares / F(cur, t)."""
    ev = events[events.ticker == ticker].sort_values("date")
    ev = ev[ev.date >= buy_date]
    shares, cash, cur = adj_factor(splits_df, div_df, ticker, buy_date), 0.0, ticker
    manual_used = ticker in manual_tickers
    segments = []  # (start, end, ticker_or_None, shares, cash)
    seg_start = buy_date
    for _, row in ev.iterrows():
        segments.append((seg_start, row.date, cur, shares, cash))
        if row.type == "cash_takeout":
            actual_shares = shares / adj_factor(splits_df, div_df, cur, row.date)
            cash += actual_shares * row.cash_per_share
            shares, cur = 0.0, None
        elif row.type == "stock_takeout":
            actual_shares = shares / adj_factor(splits_df, div_df, cur, row.date)
            if not pd.isna(row.cash_per_share):
                cash += actual_shares * row.cash_per_share
            cur = row.acquirer_ticker
            shares = actual_shares * row.ratio * adj_factor(splits_df, div_df, cur, row.date)
            manual_used = manual_used or cur in manual_tickers
        elif row.type == "divest":
            _, px = buy_fill(prices, cur, row.date)
            cash += shares * (px if px is not None else 0.0)
            shares, cur = 0.0, None
        seg_start = row.date
    segments.append((seg_start, dates[-1] + pd.Timedelta(days=1), cur, shares, cash))

    flag = ""
    if cur is not None and cur in prices.columns and not prices[cur].dropna().empty:
        last_real = prices[cur].dropna().index[-1]
        if last_real < dates[-1] and cur not in set(ev.ticker):
            flag = f"{cur} price history ends {last_real.date()}, no event found; carried forward"
    if manual_used:
        flag = "manual_prices" if not flag else f"{flag}; manual_prices"

    vals = pd.Series(0.0, index=dates)
    for start, end, tkr, sh, ca in segments:
        mask = (dates >= start) & (dates < end)
        if not mask.any():
            continue
        if tkr is None or sh == 0:
            vals[mask] = ca
        elif tkr in prices.columns:
            px = prices[tkr].reindex(dates).ffill()
            vals[mask] = sh * px[mask] + ca
        else:
            vals[mask] = ca  # no price data for this ticker at all
    return vals, flag


def run_backtest(episodes, events, today, fetch_fn, manual_fn=load_manual_prices, splits_fn=fetch_splits):
    episodes = episodes.copy()
    episodes["air_date"] = pd.to_datetime(episodes.air_date)
    events = events.copy()
    events["date"] = pd.to_datetime(events.date)

    bought = episodes[(episodes.status != "skipped") & episodes.ticker.notna() & (episodes.ticker != "")].copy()
    skipped = episodes[~episodes.index.isin(bought.index)]

    all_tickers = set(bought.ticker) | set(events.acquirer_ticker.dropna())
    start = bought.air_date.min()
    fetch_end = today + pd.Timedelta(days=1)  # yfinance `end` is exclusive; include today's close once it prints
    prices = fetch_fn(sorted(all_tickers | {BENCH}), start, fetch_end)
    bench_ticker = BENCH if BENCH in prices.columns and not prices[BENCH].dropna().empty else BENCH_FALLBACK
    if bench_ticker not in prices.columns:
        prices = pd.concat([prices, fetch_fn([BENCH_FALLBACK], start, fetch_end)], axis=1)
    splits, div_df = splits_fn(sorted(all_tickers), start, fetch_end)

    today = min(today, prices[bench_ticker].dropna().index[-1])  # ponytail: as-of = last completed close, not the calendar date
    dates = pd.bdate_range(start, today)
    manual = manual_fn(dates)
    manual_tickers = set()
    for t, s in manual.items():
        if t in all_tickers:  # ponytail: manual file wins outright; Yahoo keeps stubs for delisted tickers (EA)
            prices[t] = s
            manual_tickers.add(t)

    results = []
    lot_vals = pd.DataFrame(0.0, index=dates, columns=bought.index)
    invested_steps = pd.Series(0.0, index=dates)
    bench_vals = pd.DataFrame(0.0, index=dates, columns=bought.index)

    for idx, row in bought.iterrows():
        buy_date, adj_close0 = buy_fill(prices, row.ticker, row.air_date)
        if buy_date is None:
            results.append(dict(ep_num=row.ep_num, title=row.title, air_date=row.air_date.date(),
                                 ticker=row.ticker, status=row.status, buy_date=None, buy_price=None,
                                 split_factor=None, current_value=None, return_pct=None, gain_usd=None,
                                 flag="no price data at all; excluded from value series"))
            continue
        sf = adj_factor(splits, div_df, row.ticker, buy_date)
        buy_price = adj_close0 * sf  # actual close that day -- the real cost of 1 actual share
        vals, flag = lot_series(prices, dates, row.ticker, buy_date, events, splits, div_df, manual_tickers)
        lot_vals[idx] = vals
        invested_steps.loc[buy_date] += buy_price
        _, bpx = buy_fill(prices, bench_ticker, row.air_date)
        bench_px = prices[bench_ticker].reindex(dates).ffill()
        bshares = buy_price / bpx
        bv = pd.Series(0.0, index=dates)
        bv[dates >= buy_date] = bshares * bench_px[dates >= buy_date]
        bench_vals[idx] = bv
        cur_val = float(vals.iloc[-1])
        results.append(dict(ep_num=row.ep_num, title=row.title, air_date=row.air_date.date(),
                             ticker=row.ticker, status=row.status, buy_date=buy_date.date(),
                             buy_price=round(buy_price, 2), split_factor=round(sf, 6),
                             current_value=round(cur_val, 2),
                             return_pct=round((cur_val / buy_price - 1) * 100, 1),
                             gain_usd=round(cur_val - buy_price, 2), flag=flag))

    for _, row in skipped.iterrows():
        results.append(dict(ep_num=row.ep_num, title=row.title, air_date=row.air_date.date(),
                             ticker=row.get("ticker", ""), status=row.status, buy_date=None,
                             buy_price=None, split_factor=None, current_value=None, return_pct=None,
                             gain_usd=None, flag=row.get("source_note", "skipped")))

    results_df = pd.DataFrame(results)
    invested = invested_steps.cumsum()
    timeseries = pd.DataFrame({
        "date": dates, "invested": invested.values,
        "portfolio_value": lot_vals.sum(axis=1).values,
        "benchmark_value": bench_vals.sum(axis=1).values,
    })

    ok = results_df[results_df.buy_price.notna()]
    cashflows = [(d, -p) for d, p in zip(ok.buy_date, ok.buy_price)]
    port_val = float(timeseries.portfolio_value.iloc[-1])
    bench_val = float(timeseries.benchmark_value.iloc[-1])
    total_invested = float(timeseries.invested.iloc[-1])
    summary = dict(
        total_invested=round(total_invested, 2),
        portfolio_value=round(port_val, 2),
        multiple=round(port_val / total_invested, 3) if total_invested else None,
        xirr=xirr(cashflows, today.date(), port_val),
        benchmark_value=round(bench_val, 2),
        benchmark_multiple=round(bench_val / total_invested, 3) if total_invested else None,
        benchmark_xirr=xirr(cashflows, today.date(), bench_val),
        n_bought=int(ok.shape[0]),
        n_skipped=int(skipped.shape[0]),
        n_flagged=int((results_df.flag != "").sum()) if "flag" in results_df else 0,
        best_by_return=ok.sort_values("return_pct", ascending=False).head(5)[["title", "return_pct"]].values.tolist(),
        worst_by_return=ok.sort_values("return_pct").head(5)[["title", "return_pct"]].values.tolist(),
        best_by_gain=ok.sort_values("gain_usd", ascending=False).head(5)[["title", "gain_usd"]].values.tolist(),
        worst_by_gain=ok.sort_values("gain_usd").head(5)[["title", "gain_usd"]].values.tolist(),
    )
    return results_df, timeseries, summary


def xirr(cashflows, terminal_date, terminal_value):
    """cashflows: [(date, amount)]; terminal_value added as a positive flow today. Bisection."""
    flows = [(d, a) for d, a in cashflows] + [(terminal_date, terminal_value)]
    t0 = flows[0][0]

    def npv(rate):
        return sum(amt / (1 + rate) ** ((d - t0).days / 365.0) for d, amt in flows)

    lo, hi = -0.99, 10.0
    if npv(lo) * npv(hi) > 0:
        return None  # ponytail: no sign change (e.g. total loss or degenerate case) -> give up
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2, 4)


def make_chart(timeseries, logy, path="chart.png"):
    # ponytail: styled to match report.html (Acquired brand: cream, near-black, teal, gold)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    BG, INK, MUTED, TEAL, GOLD, GRID = "#fffcf5", "#1b1915", "#8c8574", "#0e7d61", "#7a5f28", "#efe8d6"
    fig, ax = plt.subplots(figsize=(11, 5.6), facecolor=BG)
    ax.set_facecolor(BG)
    t = timeseries
    ax.fill_between(t.date, t.portfolio_value, color=TEAL, alpha=0.08, linewidth=0)
    ax.plot(t.date, t.portfolio_value, color=TEAL, lw=2.2, label="Acquired portfolio")
    ax.plot(t.date, t.benchmark_value, color=GOLD, lw=1.8, label="S&P 500 total return, same dollars")
    ax.plot(t.date, t.invested, color=MUTED, lw=1.4, ls=(0, (4, 3)), label="Cash invested")
    for col, color in (("portfolio_value", TEAL), ("benchmark_value", GOLD), ("invested", MUTED)):
        ax.annotate(f"${t[col].iloc[-1]/1000:,.0f}k", (t.date.iloc[-1], t[col].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center", color=color, fontsize=9, fontweight="bold")
    if logy:
        ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v/1000:,.0f}k"))
    ax.grid(axis="y", color=GRID, lw=1); ax.set_axisbelow(True)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID); ax.tick_params(colors=MUTED, length=0)
    ax.set_title("THE ACQUIRED PORTFOLIO VS. THE S&P 500", loc="left", color=INK, fontsize=13, fontweight="bold", pad=18)
    ax.text(0, 1.02, "One share of every company covered, bought on air date, Oct 2015 onward. "
            "Same dollars into the S&P 500 total return index on the same dates.",
            transform=ax.transAxes, color=MUTED, fontsize=8.5)
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=BG)


def main():
    logy = "--logy" in sys.argv
    episodes = pd.read_csv("episodes.csv")
    events = pd.read_csv("events.csv")
    today = pd.Timestamp(dt.date.today())
    results_df, timeseries, summary = run_backtest(episodes, events, today, fetch_prices)
    results_df.to_csv("results.csv", index=False)
    timeseries.to_csv("timeseries.csv", index=False)
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    make_chart(timeseries, logy)
    print(json.dumps(summary, indent=2, default=str))


def selftest():
    dates = pd.bdate_range("2020-01-01", "2020-01-10")
    aaa = pd.Series([10, 11, 12, 12, 13, 13, 14, 14], index=dates, dtype=float)  # dividend-adjusted step at idx2
    bbb = pd.Series([20, 20, 21, 22, 23, 24, 25, 26], index=dates, dtype=float)
    bench = pd.Series(np.linspace(100, 110, len(dates)), index=dates)
    fixture = pd.DataFrame({"AAA": aaa, "BBB": bbb, BENCH: bench})

    def fake_fetch(tickers, start, end):
        return fixture[[t for t in tickers if t in fixture.columns]]

    episodes = pd.DataFrame([
        dict(ep_num=1, title="Ep A", air_date="2020-01-01", subject="A", ticker="AAA", parent="", status="public", source_note=""),
        dict(ep_num=2, title="Ep B", air_date="2020-01-01", subject="B", ticker="BBB", parent="", status="public", source_note=""),
        dict(ep_num=3, title="Ep C private", air_date="2020-01-01", subject="C", ticker="", parent="", status="skipped", source_note="private co"),
        dict(ep_num=4, title="Ep D delisted", air_date="2020-01-01", subject="D", ticker="ZZZ", parent="", status="public", source_note=""),
    ])
    events = pd.DataFrame([
        dict(ticker="AAA", date="2020-01-06", type="cash_takeout", cash_per_share=50, acquirer_ticker="", ratio=None, note="deal"),
        dict(ticker="BBB", date="2020-01-09", type="divest", cash_per_share=None, acquirer_ticker="", ratio=None, note="spinoff sold"),
    ])
    today = pd.Timestamp("2020-01-10")

    # ZZZ: no yfinance history at all, only two manual points (buy date + deal date).
    manual_df = pd.DataFrame([
        dict(ticker="ZZZ", date="2020-01-01", close=100.0, note="buy"),
        dict(ticker="ZZZ", date="2020-01-09", close=700.0, note="deal"),
    ])
    manual_df["date"] = pd.to_datetime(manual_df.date)
    fake_manual = lambda dates: _manual_series(manual_df, dates)  # ponytail: in-memory only, never touches manual_prices.csv

    mid = pd.Timestamp("2020-01-06")
    d0, d1 = manual_df.date.iloc[0], manual_df.date.iloc[1]
    expected_mid = 100.0 + (700.0 - 100.0) * (mid - d0).days / (d1 - d0).days
    wide_dates = pd.bdate_range("2019-12-30", "2020-01-10")
    zzz_series = _manual_series(manual_df, wide_dates)["ZZZ"]
    assert abs(zzz_series[mid] - expected_mid) < 1e-9, (zzz_series[mid], expected_mid)
    assert pd.isna(zzz_series[pd.Timestamp("2019-12-30")])  # before the first manual point
    assert zzz_series[pd.Timestamp("2020-01-10")] == 700.0  # held flat after the last point

    fake_splits = lambda tickers, start, end: (pd.DataFrame(), pd.DataFrame())  # ponytail: no columns -> split_factor()==1.0, no div data -> adj_factor falls back to it

    results_df, timeseries, summary = run_backtest(episodes, events, today, fake_fetch, fake_manual, fake_splits)

    # AAA bought at 10 (2020-01-01), takeout on 01-06 -> cash = 1*50 = 50, held flat.
    # BBB bought at 20 (2020-01-01), divested on 01-09 at close 25 -> cash = 25.
    aaa_row = results_df[results_df.ticker == "AAA"].iloc[0]
    bbb_row = results_df[results_df.ticker == "BBB"].iloc[0]
    assert aaa_row.buy_price == 10.0, aaa_row.buy_price
    assert aaa_row.current_value == 50.0, aaa_row.current_value
    assert bbb_row.buy_price == 20.0, bbb_row.buy_price
    assert bbb_row.current_value == 25.0, bbb_row.current_value

    # ZZZ: delisted, no yfinance data, filled from manual_prices -- held flat at 700 from
    # the deal date onward, and flagged so it's traceable in results.csv.
    zzz_row = results_df[results_df.ticker == "ZZZ"].iloc[0]
    assert zzz_row.buy_price == 100.0, zzz_row.buy_price
    assert zzz_row.current_value == 700.0, zzz_row.current_value
    assert zzz_row.flag == "manual_prices", zzz_row.flag

    assert summary["n_skipped"] == 1
    assert summary["n_bought"] == 3
    final_port = float(timeseries.portfolio_value.iloc[-1])
    assert abs(final_port - 775.0) < 1e-6, final_port
    assert summary["total_invested"] == 130.0
    assert timeseries.invested.is_monotonic_increasing
    assert (timeseries.portfolio_value >= 0).all()

    # --- split-adjustment cases (no network: splits come from fake splits_fn) ---

    # TEN: 10:1 split on 01-10, after the 01-01 buy. Actual close is 100 flat; auto_adjust
    # halves... er, tenths it pre-split (adj_close=10), so 1 actual share = 10 adj_shares.
    # A cash_takeout on 01-15 (post-split) at $15/actual-share should pay out 10*15=150,
    # since the holder now actually holds 10 shares (post-split) not 1.
    dates_ten = pd.bdate_range("2020-01-01", "2020-01-20")
    adj_ten = pd.Series(10.0, index=dates_ten)
    adj_ten[dates_ten >= pd.Timestamp("2020-01-10")] = 100.0
    fixture_ten = pd.DataFrame({"TEN": adj_ten, BENCH: pd.Series(100.0, index=dates_ten)})
    splits_ten = pd.DataFrame({"TEN": [10.0]}, index=[pd.Timestamp("2020-01-10")])
    episodes_ten = pd.DataFrame([
        dict(ep_num=10, title="Ep Ten", air_date="2020-01-01", subject="T", ticker="TEN",
             parent="", status="public", source_note=""),
    ])
    events_ten = pd.DataFrame([
        dict(ticker="TEN", date="2020-01-15", type="cash_takeout", cash_per_share=15,
             acquirer_ticker="", ratio=None, note="deal"),
    ])
    ten_results, _, _ = run_backtest(
        episodes_ten, events_ten, pd.Timestamp("2020-01-20"),
        lambda tickers, start, end: fixture_ten[[t for t in tickers if t in fixture_ten.columns]],
        lambda dates: {},
        lambda tickers, start, end: (splits_ten[[t for t in tickers if t in splits_ten.columns]], pd.DataFrame()))
    ten_row = ten_results.iloc[0]
    assert abs(ten_row.buy_price - 100.0) < 1e-9, ten_row.buy_price
    assert abs(ten_row.split_factor - 10.0) < 1e-9, ten_row.split_factor
    assert abs(ten_row.current_value - 150.0) < 1e-9, ten_row.current_value

    # REV: 1-for-20 reverse split (yfinance ratio 0.05) after the buy -- mirrors the SPCE bug:
    # adj_close reads 600 but the actual close paid that day was 30.
    dates_rev = pd.bdate_range("2020-01-01", "2020-01-10")
    fixture_rev = pd.DataFrame({"REV": pd.Series(600.0, index=dates_rev), BENCH: pd.Series(100.0, index=dates_rev)})
    splits_rev = pd.DataFrame({"REV": [0.05]}, index=[pd.Timestamp("2020-01-05")])
    episodes_rev = pd.DataFrame([
        dict(ep_num=11, title="Ep Rev", air_date="2020-01-01", subject="R", ticker="REV",
             parent="", status="public", source_note=""),
    ])
    events_rev = pd.DataFrame(columns=["ticker", "date", "type", "cash_per_share", "acquirer_ticker", "ratio", "note"])
    rev_results, _, _ = run_backtest(
        episodes_rev, events_rev, pd.Timestamp("2020-01-10"),
        lambda tickers, start, end: fixture_rev[[t for t in tickers if t in fixture_rev.columns]],
        lambda dates: {},
        lambda tickers, start, end: (splits_rev[[t for t in tickers if t in splits_rev.columns]], pd.DataFrame()))
    rev_row = rev_results.iloc[0]
    assert abs(rev_row.buy_price - 30.0) < 1e-9, rev_row.buy_price
    assert abs(rev_row.split_factor - 0.05) < 1e-9, rev_row.split_factor

    # DIV: dividend payer, no splits. Adj close on the buy day is 9.5 (dividend-adjusted) but
    # the actual unadjusted close paid that day was 10 -- D = AdjClose/Close = 0.95 flat. This
    # is the SPCE-style bug in reverse (VZ/MSFT/etc. in review/independent_lots.csv): buy_price
    # must recover the real $10 close, not the $9.50 adjusted one.
    dates_div = pd.bdate_range("2020-01-01", "2020-01-10")
    fixture_div = pd.DataFrame({"DIV": pd.Series(9.5, index=dates_div), BENCH: pd.Series(100.0, index=dates_div)})
    div_df_fake = pd.DataFrame({"DIV": pd.Series(0.95, index=dates_div)})
    episodes_div = pd.DataFrame([
        dict(ep_num=12, title="Ep Div", air_date="2020-01-01", subject="V", ticker="DIV",
             parent="", status="public", source_note=""),
    ])
    events_div = pd.DataFrame(columns=["ticker", "date", "type", "cash_per_share", "acquirer_ticker", "ratio", "note"])
    div_results, _, _ = run_backtest(
        episodes_div, events_div, pd.Timestamp("2020-01-10"),
        lambda tickers, start, end: fixture_div[[t for t in tickers if t in fixture_div.columns]],
        lambda dates: {},
        lambda tickers, start, end: (pd.DataFrame(), div_df_fake[[t for t in tickers if t in div_df_fake.columns]]))
    div_row = div_results.iloc[0]
    assert div_row.buy_price == 10.0, div_row.buy_price
    assert abs(div_row.current_value - (10.0 / 9.5) * 9.5) < 1e-9, div_row.current_value  # shares (1/D) x adj close = actual value

    print("selftest OK")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
