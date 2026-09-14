"""Independent recomputation. Reads results.csv/episodes.csv (read-only), fetches UNADJUSTED
closes from yfinance, and compares the model's cost basis / value with a proper
"1 actual share at the actual close, dividends reinvested" total-return computation."""
import pandas as pd, numpy as np, yfinance as yf, json, sys
R = pd.read_csv("results.csv", parse_dates=["buy_date"])
ok = R[R.buy_price.notna()].copy()
manual = ok.flag.fillna("").str.contains("manual_prices")
live = ok[~manual].copy()
FX = {".T":"JPY",".PA":"EUR",".HK":"HKD",".TW":"TWD",".DE":"EUR"}
tick = sorted(set(live.ticker)) + ["^SP500TR"]
fx = sorted({FX[s] for t in tick for s in FX if t.endswith(s)})
raw = yf.download(tick + [f"{c}USD=X" for c in fx], start="2015-10-01", end="2026-09-11",
                  auto_adjust=False, actions=True, progress=False, group_by="ticker")
def col(t, f): return raw[t][f].dropna()
END = pd.Timestamp("2026-09-09")
rows = []
for _, r in live.iterrows():
    t = r.ticker
    close, adj = col(t, "Close"), col(t, "Adj Close")
    fxs = None
    for s, c in FX.items():
        if t.endswith(s): fxs = col(f"{c}USD=X", "Close")
    d0 = close.index[close.index >= r.buy_date][0]
    splits = col(t, "Stock Splits"); splits = splits[(splits != 0) & (splits.index > d0)]
    S = float(splits.prod()) if len(splits) else 1.0   # yfinance Close is split-adjusted even with auto_adjust=False
    P0 = close.loc[d0] * S; A0 = adj.loc[d0]
    AT = adj.loc[adj.index <= END].iloc[-1]; PT = close.loc[close.index <= END].iloc[-1]
    if fxs is not None:
        f0 = fxs.loc[fxs.index <= d0].iloc[-1]; fT = fxs.loc[fxs.index <= END].iloc[-1]
        P0 *= f0; PT *= fT
    else: f0 = fT = 1.0
    tr_mult = AT / A0                       # total return multiple, 1 share, divs reinvested
    true_value = P0 * tr_mult
    d = r.buy_price / P0                    # model cost / actual close  (dividend understatement)
    rows.append(dict(ep=r.ep_num, ticker=t, buy_date=d0.date(), actual_close_usd=round(P0,2),
                     model_buy=r.buy_price, cost_ratio=round(d,4), model_value=r.current_value,
                     price_only_value=round(PT*S,2), true_tr_value=round(true_value,2),
                     model_mult=round(r.current_value/r.buy_price,3), true_mult=round(tr_mult,3),
                     S=S, event=("divest/event" if r.current_value != r.current_value else "")))
D = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(D.to_string())
D.to_csv("review/independent_lots.csv", index=False)

# headline recompute: manual lots unchanged; live lots rescaled by 1/cost_ratio (lots with a
# divest event are linear in the adj-price scale, so the same rescale applies)
man = ok[manual]
inv_true = D.actual_close_usd.sum() + man.buy_price.sum()
val_true = (D.model_value / D.cost_ratio).sum() + man.current_value.sum()
print("\nmodel invested %.0f value %.0f mult %.3f" % (ok.buy_price.sum(), ok.current_value.sum(), ok.current_value.sum()/ok.buy_price.sum()))
print("true  invested %.0f value %.0f mult %.3f" % (inv_true, val_true, val_true/inv_true))
# benchmark: same rescale per lot
B = col("^SP500TR", "Close")
def bmult(d): 
    b0 = B.loc[B.index >= pd.Timestamp(d)].iloc[0]; return B.loc[B.index <= END].iloc[-1]/b0
bench_model = sum(r.buy_price * bmult(r.buy_date) for _, r in ok.iterrows())
bench_true = sum(p * bmult(d) for p, d in zip(D.actual_close_usd, D.buy_date)) + sum(r.buy_price*bmult(r.buy_date) for _, r in man.iterrows())
print("bench model %.0f (summary says 70496) mult %.3f | bench true %.0f mult %.3f" % (bench_model, bench_model/ok.buy_price.sum(), bench_true, bench_true/inv_true))

def xirr(flows, term_date, term_val):
    flows = list(flows) + [(term_date, term_val)]; t0 = flows[0][0]
    npv = lambda r: sum(a/(1+r)**((pd.Timestamp(d)-pd.Timestamp(t0)).days/365) for d, a in flows)
    lo, hi = -0.9, 5
    for _ in range(200):
        mid = (lo+hi)/2
        if npv(lo)*npv(mid) <= 0: hi = mid
        else: lo = mid
    return (lo+hi)/2
cf_model = [(pd.Timestamp(d), -p) for d, p in zip(ok.buy_date, ok.buy_price)]
print("xirr model port %.4f bench %.4f" % (xirr(cf_model, END, ok.current_value.sum()), xirr(cf_model, END, bench_model)))
cf_true = [(pd.Timestamp(d), -p) for d, p in zip(D.buy_date, D.actual_close_usd)] + [(pd.Timestamp(d), -p) for d, p in zip(man.buy_date, man.buy_price)]
cf_true.sort()
print("xirr true  port %.4f bench %.4f" % (xirr(cf_true, END, val_true), xirr(cf_true, END, bench_true)))
# concentration
D["true_gain"] = D.true_tr_value - D.actual_close_usd
g = D.groupby("ticker").true_gain.sum().sort_values(ascending=False)
print("\ntop gain by ticker (true):\n", g.head(8).round(0), "\ntotal true gain", round(D.true_gain.sum(),0))
