#!/usr/bin/env python3
"""Regenerate report.html's embedded DATA + hero numbers + as-of date from
summary.json / results.csv / episodes.csv / timeseries.csv.

Usage: python3 build_report.py
Edits report.html in place; everything outside the patched spans is untouched.
"""
import csv
import datetime
import json
import re

REPORT = "report.html"


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def truncate_reason(note):
    """Last ';'-clause of source_note, truncated ~90 chars at a word boundary."""
    clause = note.split(";")[-1].strip()
    if len(clause) > 90:
        clause = clause[:90].rsplit(" ", 1)[0] + "..."
    return clause


def build_episodes():
    results = {r["ep_num"]: r for r in load_csv("results.csv")}
    episodes = load_csv("episodes.csv")
    rows = []
    for ep in episodes:
        n = ep["ep_num"]
        r = results[n]
        skipped = r["status"] == "skipped"
        manual = 1 if "manual_prices" in r["flag"] else 0
        reason = truncate_reason(ep["source_note"]) if skipped else ""
        rows.append([
            int(n), r["title"], r["air_date"], ep["subject"], r["ticker"], r["status"],
            None if skipped else float(r["buy_price"]),
            None if skipped else float(r["current_value"]),
            None if skipped else float(r["return_pct"]),
            None if skipped else float(r["gain_usd"]),
            manual, reason,
        ])
    return rows


def build_weekly():
    # ponytail: same downsample as before - Friday rows only, no partial-week tail.
    rows = load_csv("timeseries.csv")
    weekly = []
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        if d.weekday() == 4:  # Friday
            weekly.append([
                r["date"],
                round(float(r["invested"]), 2),
                round(float(r["portfolio_value"]), 2),
                round(float(r["benchmark_value"]), 2),
            ])
    return weekly


def money2(x):
    return f"${x:,.2f}"


def money0(x):
    return f"${x:,.0f}"


def pct1(x):
    return f"{x * 100:.1f}%"


def patch(html, pattern, replacement, count=1):
    new_html, n = re.subn(pattern, lambda m: replacement, html, count=count, flags=re.DOTALL)
    if n != count:
        raise RuntimeError(f"expected {count} match(es) for {pattern!r}, got {n}")
    return new_html


def main():
    summary = json.load(open("summary.json"))
    episodes = build_episodes()
    weekly = build_weekly()
    n_episodes = len(episodes)
    as_of = load_csv("timeseries.csv")[-1]["date"]

    data = {"episodes": episodes, "weekly": weekly}
    data_json = json.dumps(data, separators=(",", ":"))

    html = open(REPORT).read()

    html = patch(html, r"const DATA = \{.*?\};", "const DATA = " + data_json + ";")

    html = patch(
        html,
        r'<p class="asof">As of [\d-]+ &middot; \d+ main-feed episodes reviewed</p>',
        f'<p class="asof">As of {as_of} &middot; {n_episodes} main-feed episodes reviewed</p>',
    )

    total_invested = summary["total_invested"]
    portfolio_value = summary["portfolio_value"]
    benchmark_value = summary["benchmark_value"]
    port_gain = portfolio_value - total_invested
    port_ahead = portfolio_value - benchmark_value
    port_delta_class = "pos" if port_gain >= 0 else "neg"

    hero = f"""<div class="hero">
  <div class="tile accent">
    <span class="label">Total invested</span>
    <span class="value mono">{money2(total_invested)}</span>
    <span class="sub">{summary["n_bought"]} buys, one share each</span>
  </div>
  <div class="tile accent">
    <span class="label">Portfolio value today</span>
    <span class="value mono">{money2(portfolio_value)}</span>
    <span class="sub delta {port_delta_class}">{summary["multiple"]:.2f}&times; &middot; {"+" if port_gain >= 0 else "-"}{money2(abs(port_gain))}</span>
  </div>
  <div class="tile">
    <span class="label">vs. S&amp;P 500 (same $, same dates)</span>
    <span class="value mono">{money2(benchmark_value)}</span>
    <span class="sub delta">{summary["benchmark_multiple"]:.2f}&times; &middot; portfolio {"+" if port_ahead >= 0 else "-"}{money0(abs(port_ahead))} ahead</span>
  </div>
  <div class="tile">
    <span class="label">XIRR (money-weighted)</span>
    <span class="value mono">{pct1(summary["xirr"])}</span>
    <span class="sub">vs. {pct1(summary["benchmark_xirr"])} for the S&amp;P 500 TR</span>
  </div>
</div>"""
    html = patch(html, r'<div class="hero">.*?\n</div>\n\n<section id="chart-section">',
                 hero + '\n\n<section id="chart-section">')

    html = patch(
        html,
        r"<h2>All \d+ episodes</h2>",
        f"<h2>All {n_episodes} episodes</h2>",
    )

    html = patch(
        html,
        r"Figures as of [\d-]+\.",
        f"Figures as of {as_of}.",
    )

    with open(REPORT, "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()
