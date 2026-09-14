You are researching Acquired podcast episodes for a stock backtest. Read /Users/alexanderkeat/Documents/Linkedin Posts/rules.md first.

Input: /Users/alexanderkeat/Documents/Linkedin Posts/batches/in_N.csv (N given below). Columns: ep_num,title,air_date,subject,ticker,parent,status,source_note. Fill subject,ticker,parent,status and append a short reason to source_note. Keep ep_num,title,air_date unchanged.

For EACH episode determine, as of the air_date:
- subject: the company the episode is about (short name).
- status: `public` if the subject itself traded publicly on air_date; `parent` if the subject had been acquired/was a subsidiary of a public company on air_date (buy the parent); `skipped` if private with no public parent, or the episode isn't about a company (e.g. a person, a country, an industry).
- ticker: the Yahoo Finance ticker to BUY. For status=public it is the subject's ticker; for status=parent it is the parent's ticker; blank if skipped. Prefer US listings/ADRs (e.g. NTDOY, LVMUY, TSM, NVO, HESAY). If no US listing, use the Yahoo primary listing with suffix (e.g. 7974.T, MC.PA). For delisted companies use the historical ticker (LNKD, TWTR, ATVI, etc.).
- parent: the parent company name if status=parent, else blank.
- source_note: existing note + "; " + one-line justification (e.g. "acquired by Facebook 2012, public parent META").

Edge rules: multi-part episodes each get the same mapping. Episodes about a company whose parent is itself now a different ticker (e.g. Google→GOOGL) use the ticker valid on air_date and note renames. Episodes about acquisitions where the acquirer is public → parent. If the subject IPO'd after air_date, it is still `skipped` (we buy on air date only). Ticker changes (FB→META) are handled by Yahoo, use the current symbol unless the company was delisted.

Also produce corporate-action events for any ticker you assigned, occurring AFTER air_date up to 2026-09-04:
- cash_takeout: company acquired for cash (date = deal close date, cash_per_share).
- stock_takeout: acquired for stock (date, acquirer_ticker, ratio shares of acquirer per share, cash_per_share if mixed).
- divest: the parent sold/spun off the episode's subject (date). Only applies to status=parent rows.
Columns: ticker,date,type,cash_per_share,acquirer_ticker,ratio,note. Dates YYYY-MM-DD. Include ep_num(s) in note. If a takeout price is uncertain, give best figure and say "approx" in note.

Use WebSearch/WebFetch to verify anything you're not sure of (episode page at acquired.fm describes the subject; Wikipedia for deal terms). Be accurate over fast.

Write:
- /Users/alexanderkeat/Documents/Linkedin Posts/batches/out_N.csv (same columns as input, all rows filled, properly CSV-quoted)
- /Users/alexanderkeat/Documents/Linkedin Posts/batches/events_N.csv (header + rows, may be header-only)
Report back: counts of public/parent/skipped, and every row you were unsure about with why.
