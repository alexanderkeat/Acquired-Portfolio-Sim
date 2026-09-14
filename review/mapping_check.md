# Acquired Portfolio — Adversarial Mapping Review

Reviewed 2026-09-10. episodes.csv read-only; corrections below go into the CSVs per rules.md #16, never the script.

---

## TOP — WRONG findings (fix these first)

### 1. ep43 Blue Bottle Coffee — parent classified 3 weeks too early (WRONG)
Nestlé only **announced** a deal for 68% of Blue Bottle on 2017-09-14. Per a law-firm summary of the deal (KO Law, which negotiated it) and multiple press accounts, **the transaction actually closed at the end of October 2017** — after the ep43 air date of **2017-10-07**. The show's own established rule (see Jet.com/ep18, GitHub/ep56, WeWork/ep83, all correctly skipped in this same CSV because the deal hadn't closed by air date) says an announced-but-not-closed deal doesn't count as "acquired." Blue Bottle should fail that same test.

- Evidence: https://kofirm.com/blue-bottle-coffee-sale-to-nestle ("the international transaction closed at the end of October, and the KO team helped negotiate both the management and seller terms") vs. announcement date https://techcrunch.com/2017/09/14/nestle-acquires-a-majority-stake-in-blue-bottle-coffee/ (present-tense "is acquiring", no closing terms).
- **Fix (primary):** row 44 (ep43) → `ticker=`, `parent=`, `status=skipped`, note "Nestlé's 68% Blue Bottle deal announced 2017-09-14 but did not close until end of Oct 2017, after the 2017-10-07 air date; private at air date, no public parent yet (consistent with Jet.com/GitHub/WeWork treatment elsewhere in this dataset)."
- **Alternative fix** if you'd rather keep it a "parent" row on the theory that 3 weeks is immaterial: shift nothing else, but you must then also apply finding #1b below.

### 1b. ep43 — separately, an un-recorded 2026 divestiture (missing from events.csv either way)
Nestlé has **sold** Blue Bottle Coffee to Centurium Capital (Luckin Coffee's largest shareholder), announced with Nestlé's Q1-2026 results (2026-04-23) and reported completed around **2026-04-27**.
- Evidence: https://insideretail.asia/2026/04/27/nestle-completes-blue-bottle-sale-to-chinas-centurium-capital/ ; https://www.foodnavigator.com/Article/2026/04/27/nestle-sells-blue-bottle-coffee-as-big-food-rethinks-serviceled-diversification/
- **Fix:** if ep43 is kept as an NSRGY "parent" row (see 1, alternative), add to events.csv: `NSRGY,2026-04-27,divest,,,,"ep43; Nestlé sold Blue Bottle Coffee to Centurium Capital, reported completed ~2026-04-27; sell NSRGY per rule 5"`. As of today (2026-09-10) this event predates the as-of date and is currently missing, so the backtest is holding an NSRGY share it should have sold in April.

### 2. ep30 Overture/YHOO — divestiture sale price is wrong (WRONG)
events.csv sells YHOO on 2017-06-13 at **$55.90**. Two independent historical-price lookups put YHOO's actual close on 2017-06-13 at **$52.00** (with 2017-06-16, the last trading day before the Altaba rename, closing at $52.58 — consistent with a stock sitting in the low-$52s that week, not mid-$50s).
- Evidence: historicalstockprice.com YHOO historical closes (2017-06-13: $52.00; 2017-06-16: $52.58), cross-checked against multiple sources independently citing the $52.58 figure for 2017-06-16 (e.g. https://finance.yahoo.com/news/whats-altaba-worth-190900717.html, https://fortune.com/2017/06/16/alibaba-stock-yahoo-altaba/). The Verizon deal itself did close exactly on 2017-06-13 (confirmed via https://www.cnbc.com/2017/06/13/verizon-completes-yahoo-acquisition-marissa-mayer-resigns.html and https://techcrunch.com/2017/06/13/verizon-closes-4-5b-acquisition-of-yahoo-marissa-mayer-resigns-memo/ — divestiture date itself is right, only the price is off).
- **Fix:** events.csv row `YHOO,2017-06-13,divest,,,,...` → change the effective sale price used by the backtest from $55.90 to **$52.00** (roughly a 7% overstatement of the exit value of that lot).

### 3. ep138 Porsche — a US ADR existed and the rule says to use it (DEBATABLE→WRONG under a strict reading)
Rule 7 says "non-US companies → buy one US ADR share where one exists." A US OTC ADR for Porsche AG, **DRPRY**, was already trading by the 2023-06-26 air date (Yahoo Finance `firstTradeDate` = 2022-11-11, well before air date). The CSV instead used the Frankfurt primary listing P911.DE on the stated grounds "no US ADR."
- Evidence: Yahoo Finance chart metadata for DRPRY (`firstTradeDate: 1668177000` = 2022-11-11); OTC listing confirmed at https://www.morningstar.com/stocks/pinx/drpry/quote and https://www.nasdaq.com/market-activity/stocks/drpry.
- Actual closes on 2023-06-26: P911.DE = **EUR 108.85** (volume 256,845); DRPRY = **USD 11.833** (volume **9,500 shares** — vs. P911.DE's much deeper liquidity). Since the show consistently prefers the (often thin) US ADR elsewhere in this dataset (LVMUY, HESAY, NTDOY, TCEHY, MPNGY all used over the primary foreign listing), strict consistency would point to DRPRY here too, even though it's the least liquid of that group.
- **Fix (if consistency with rule 7 wins):** row 139 (ep138) → `ticker=DRPRY` (buy at $11.833 close 2023-06-26), note updated to reflect DRPRY exists via the Bank of NY Mellon Level-1 unsponsored program.
- **If liquidity is the tiebreaker instead:** keep P911.DE, but the source_note's "no US ADR" claim should be corrected to "US OTC ADR DRPRY exists but is too illiquid to be a reasonable index price; using primary Frankfurt listing P911.DE instead."

---

## A. Hard cases

**ep21 Zillow+Trulia (Z), 2016-10-13.** Z (class C, non-voting) is the more liquid/conventional trading symbol. Closes 2016-10-13: **Z $32.06** (vol 2,232,642) vs **ZG $32.00** (vol 868,136). Closes 2026-09-09 (last full session before today): **Z $32.14** (vol 2,940,439) vs **ZG $32.805** (vol 1,036,557). Z is consistently ~2-3x the volume of ZG on both dates — Z is the right pick. OK. (stockanalysis.com history API)

**ep30 Overture (YHOO), 2017-03-13; divest 2017-06-13.** Yahoo did own Overture at air date (2003 acquisition, uncontested) and remained independent public YHOO until the Operating Business sale to Verizon closed 2017-06-13 (confirmed https://www.cnbc.com/2017/06/13/verizon-completes-yahoo-acquisition-marissa-mayer-resigns.html); the residual entity (mostly Alibaba/Yahoo Japan stakes) was renamed Altaba (AABA) with the ticker switch effective 2017-06-19. Divest date 2017-06-13 is correct. **Divest price is WRONG — see finding #2 above** ($55.90 used vs. actual ~$52.00 close).

**ep38 Booking.com (BKNG), 2017-07-25.** BKNG's Yahoo/stockanalysis price history is continuous back through the PCLN-ticker era (same CIK, symbol renamed Feb 2018, not delisted/relisted), so 2017 coverage is fine. OK. Booking Holdings' 25-for-1 stock split: confirmed effective with **payable date 2026-04-02** and split-adjusted trading beginning **2026-04-06** (ex-date) — matches the CSV's "~2026-04-06." OK. (https://www.streetinsider.com/Corporate+News/Booking+Holdings+announces+25-to-1+stock+split+effective+April+2026/26021797.html)

**ep39 Opsware (HPE), 2017-08-04; divest 2017-09-01.** Confirmed lineage and dates: Opsware→HP 2007 (cash)→HP split into HPQ/HPE 2015→HPE software business (including the Opsware-descended line) spun off and merged into Micro Focus, **completed 2017-09-01** (https://www.globenewswire.com/news-release/2017/09/01/1106512/...). Exchange ratio confirmed: **0.13732611 Micro Focus ADS per HPE share** held as of the record date 2017-08-21.
Value check: HPE close 2017-08-04 = **$13.58**. HPE close 2017-09-01 (post-spin, hardware-only residual) = **$14.31**. Micro Focus's own 8-K priced the spun stake at ~$6.3B for ~222M ADSs (≈$28.4/ADS) as of the 2017-08-31 LSE close. So one HPE share bought 2017-08-04 was worth, on 2017-09-01: **$14.31 (residual HPE) + 0.13732611 × ~$28.4 (MF ADS) ≈ $3.90 ≈ $18.21 total** — roughly a 34% gain in under a month, mostly reflecting the value unlock from separating the software business rather than true business performance. (MF ADS price is an approximation from the aggregate $6.3B/222M figure; a precise per-share MCRO.L close for 2017-09-01 could not be pulled directly.) OK on dates/ratio; the $18.21 figure should be treated as an estimate, not exact.

**ep41 AOL (VZ), 2017-09-17; divest 2021-09-01.** Confirmed: Apollo Funds completed the acquisition of Verizon Media (AOL+Yahoo) on **2021-09-01** (https://www.apollo.com/insights-news/pressreleases/2021/09/apollo-funds-complete-acquisition-of-yahoo-161530593; deal announced 2021-05-03). Divest date OK.

**ep43 Blue Bottle (NSRGY), 2017-10-07.** See findings #1 and #1b above — **WRONG**, deal hadn't closed by air date, and a 2026 divestiture is also missing. NSRGY ADR ratio: confirmed **1 ADR = 1 ordinary share** (Nestlé's own investor FAQ, https://www.nestle.com/investors/faqs/adrs-faqs).

**ep51/ep69 SoftBank (SFTBY).** Confirmed 4:1 forward split of the SFTBY ADR effective **2026-01-08**, tracking the Tokyo-listed ordinary shares' own split (https://news.futunn.com/en/post/67024733/softbank-group-adr-to-carry-out-4-for-1-stock). Could **not** independently confirm the claimed 2019-07-11 2:1 ADR-ratio change from primary sources — DEBATABLE / unconfirmed, flag for further research rather than treated as verified. ep69 ARM & SoftBank: confirmed SoftBank still holds a clear majority of Arm as of 2026 (**~86-87%** per May 2026 SEC/press reporting, e.g. https://www.tradingkey.com/analysis/stocks/us-stocks/261921505-arm-300b-softbank-87-stake-wins-cpu-fuels-wall-street-tradingkey) — no divestiture, correctly un-recorded. OK.

**ep55 T-Mobile/Sprint (TMUS), 2018-05-21.** Confirmed Sprint (S) was still separately public at air date; T-Mobile/Sprint merger closed **2020-04-01**, with non-SoftBank Sprint holders converting at **0.10256 TMUS per Sprint share** (SEC 8-K, https://www.sec.gov/Archives/edgar/data/1283699/000119312520043713/d886254dex991.htm). One-share rule reasonably picks TMUS as the surviving/larger entity; noting Sprint as the alternative per the task. OK as documented.

**ep80 Google Maps (GOOGL), 2019-08-26.** Nothing odd — Maps is an organic Google/Alphabet product, GOOGL public throughout. OK.

**ep82 Atari (ALATA.PA), 2019-10-15.** ALATA.PA is the correct Euronext Paris/Growth Yahoo symbol for Atari SA. Close 2019-10-15 (unadjusted): **EUR 53.23**. Yahoo's auto-adjusted (post-reverse-split) price for that date is ≈53.23/200 ≈ **EUR 0.27**, matching the ~EUR 0.26 figure cited in the task. Reverse split confirmed: **1-for-200**, effective **2026-05-05** (announced 2026-03-16, completed 2026-05-05, new ISIN FR00140173Y6 — https://www.actusnews.com/en/atari/pr/2026/05/05/atari-completes-reverse-stock-split). Lineage: Infogrames Entertainment SA acquired Atari, Inc. (Bushnell's 1972 company, by then long since sold through Time Warner/Hasbro/JTS ownership) piecemeal from 2001, completing full ownership in Oct 2008, then renamed itself **Atari SA** in 2009 — so today's Atari SA is a legal continuation of Infogrames wearing the Atari brand, not a re-founding of Bushnell's original company. OK, matches CSV note.

**ep106 Meituan (MPNGY), 2021-03-10.** Confirmed ADR ratio: **1 ADS = 2 Class B ordinary shares** (consistent across SEC F-6 filings 2018-2025). Close 2021-03-10: MPNGY (unsponsored ADR) = **$80.93**; 3690.HK = **HKD 317.00** → at the pegged USD/HKD rate (~7.78) that's ≈$40.75/ordinary share × 2 = **≈$81.49 ADS-equivalent**, matching MPNGY's $80.93 close within ~0.7%. MPNGY is the standard/most commonly quoted unsponsored ADR vs. MPNGF; no evidence MPNGF is more liquid. OK.

**ep134 LVMH (LVMUY), 2023-02-21.** Confirmed ADR ratio: **1 LVMUY = 0.2 LVMH ordinary share** (1:5). Close 2023-02-21: LVMUY = **$171.41**; MC.PA = **EUR 808.90** → at ~1.069 EUR/USD that day, ≈$864.7 × 0.2 = **≈$172.9**, matching LVMUY within ~1%. OK.

**ep144 Hermès (HESAY), fill 2024-02-20.** 2024-02-19 was indeed Presidents' Day (US market holiday), so the 2024-02-20 fill is correct. Confirmed ADR ratio: **1 HESAY = 0.1 RMS ordinary share** (per otcmarkets.com listing). Close 2024-02-20: HESAY = **$239.87**; RMS.PA = **EUR 2219.5** → at ~1.082 EUR/USD, ≈$2401.5 × 0.1 = **≈$240.15**, matching HESAY within ~0.1%. OK.

**ep165 Formula 1 (FWONK), 2026-03-02.** FWONK (Series C) vs FWONA (Series A) — FWONK is the standard higher-volume tracking-stock class typically used as "the" F1 stock; no evidence anything corporate happened to it between the 2026-08-2023 tracking-stock reclassification and today. Explicitly confirmed no split/reclassification occurred between 2026-03-02 and 2026-09-09 (still trading, e.g. $96.18 on 2026-07-24, same ticker/structure). OK.

**ep42 HTC (2498.TW), 2017-09-21.** Confirmed 2498.TW is HTC Corp on TWSE. Close 2017-09-21: **TWD 69.30**; USD/TWD that day ≈30.19 → **≈USD $2.30**, close to the backtest's $2.25 (small variance likely from FX-timing/rounding). Google's $1.1B deal (announced 2017-09-21, same as air date, per HTC's own newsroom) was for Pixel-team/IP licensing only, not the whole company — HTC correctly stays public. OK.

**ep59 Xiaomi IPO (1810.HK), fill 2018-08-06.** Close 2018-08-06: **HKD 17.22**; USD/HKD pegged ≈7.849 → **≈USD $2.19**, matching the backtest's $2.19 essentially exactly. No US ADR existed at the time — could not pin down XIACY's exact launch date from public sources, but it is a recent (post-2018) addition consistent with the CSV's "~2024" claim; not contradicted by anything found. OK.

**ep138 Porsche (P911.DE), 2023-06-26.** See finding #3 above — **DEBATABLE/WRONG under strict rule 7**, a US ADR (DRPRY) did exist. Close 2023-06-26: P911.DE = **EUR 108.85** (unadjusted; current adjusted-close of 97.13 reflects three years of subsequent dividends, not a restatement error). The task's cited "$105.94 adjusted USD" figure could not be reconciled exactly against a same-day EUR/USD conversion of the raw close (~$118.7); likely reflects a stale/differently-adjusted historical pull rather than a live error, but flagging the discrepancy for the backtest maintainer to double check its FX/adjustment methodology.

**ep40 The Square IPO (XYZ), 2017-08-16.** Ticker rename (SQ→XYZ) preserves the same underlying security/CIK; Yahoo/stockanalysis history is continuous back to the 2015 IPO. OK.

**ep16 Midroll+Stitcher (SSP), 2016-07-12.** Confirmed: Scripps acquired Midroll in **July 2015** ($55M) and Stitcher **announced 2016-06-06** ($4.5M) — both well before the 2016-07-12 air date. Stitcher→SiriusXM sale confirmed **closed 2020-10-16** per Scripps' own press release (https://scripps.com/press-releases/scripps-completes-sale-of-stitcher-to-siriusxm/), the CSV/events.csv divest date of 2020-10-19 is a few days after the actual close — minor (3 trading-day) lag, worth tightening but not a material pricing error. DEBATABLE: consider moving the divest date to 2020-10-16 (or the next trading day) for precision.

**ep36 Whole Foods (WFM) / ep14 LinkedIn (LNKD).** Confirmed both still traded independently on their air dates: WFM (Amazon deal announced 2017-06-16, didn't close until 2017-08-28, air date 2017-06-20 — still public); LNKD (Microsoft deal announced 2016-06-13, closed 2016-12-08, air date 2016-06-16 — still public). OK.

---

## B. Skipped rows — spot check

Full scan of all 54 `skipped` rows found no cases where the subject actually had public status or a public majority owner at air date beyond what's already correctly noted. Specifically:

- ep18 Jet — OK-skip (Walmart deal announced 2016-08-08, closed 2016-09-19; air 2016-08-29 is before close; Jet.com was never itself public).
- ep34 BAMTech — OK-skip (Disney held only 33% minority in May 2017 per the episode's own air-date window; MLB Advanced Media, the majority/private owner, is not public).
- ep56 GitHub — OK-skip (Microsoft deal announced 2018-06-04, closed 2018-10-26; air date 2018-06-05 is one day after announcement, well before close).
- ep83 WeWork — OK-skip (SoftBank's Oct 2019 rescue was an economic stake, not control, and WeWork itself stayed private).
- ep98 Epic Games — OK-skip (Tencent's stake is a ~40% minority; Epic remained privately controlled by Tim Sweeney).
- ep119 CAA — OK-skip. Confirmed: TPG (CAA's majority owner) did not IPO until **2022-01-18**, after the 2021-12-21 air date — TPG was private at air date.
- ep115/ep116 Standard Oil — OK-skip (dissolved by 1911 antitrust action; no single successor entity).
- ep145 Renaissance Technologies — OK-skip (private hedge fund/partnership).
- ep151 IKEA — OK-skip (owned by INGKA/Interogo foundations, non-profit structure, no public parent).
- ep152 Mars — OK-skip (privately held by the Mars family).
- ep162 Trader Joe's — OK-skip (owned by Aldi Nord/Albrecht family foundations, private).
- ep167 Vanguard — OK-skip (mutual/fund-owned structure, not a stock).
- ep155 IPL — OK-skip (BCCI-run league, not a company with equity).
- ep156 Epic Systems — OK-skip (privately held, founder-controlled, never IPO'd).
- ep85 TikTok — OK-skip (ByteDance-owned, private).
- ep78 Huawei — OK-skip (employee-owned, unlisted).
- ep61 Recode — OK-skip (Vox Media is private).
- ep57 Rover — OK-skip (private, both merging entities).
- ep86 Convoy — OK-skip (private; shut down 2023, never public).
- ep107 Rec Room — OK-skip (private).
- ep94 SpaceX — OK-skip (still private as of 2026-09-10).
- ep95 Harpo — OK-skip (private production company).

No corrections needed in section B.

---

## C. Parent rows — ownership-continuity check

All parent rows checked for (a) parent-owned-subject-at-air-date and (b) still-owned-as-of-2026-09-10 unless a divestiture is recorded.

- ep1 Pixar/DIS — still owned. OK.
- ep2 Instagram/META — still owned. OK.
- ep3 Twitch/AMZN — still owned. OK.
- ep5 Siri/AAPL — still owned. OK.
- ep6 Lucasfilm/DIS — still owned. OK.
- ep7 YouTube/GOOGL — still owned. OK.
- ep8 Acompli-Sunrise-Wunderlist/MSFT — Wunderlist was shut down in 2020, but that's a discontinuation, not a sale/divestiture (nobody else acquired it), so no divest event is needed. OK as documented.
- ep9 Writely/GOOGL — still owned. OK.
- ep13 Push Pop Press/META — still owned. OK.
- ep15 ExactTarget/CRM — still owned. OK.
- ep16 Stitcher/SSP — divested to SiriusXM, event recorded (2020-10-19 in CSV vs. actual close 2020-10-16 — see minor date note in section A). OK with a 3-day precision caveat.
- ep17 Waze/GOOGL — still owned. OK.
- ep19 Android/GOOGL — still owned. OK.
- ep22 NeXT/AAPL — still owned (folded into Apple, no separate entity to divest). OK.
- ep23 Skype/MSFT — still owned. OK.
- ep25 Marvel/DIS — still owned. OK.
- ep27 P.A. Semi+AuthenTec/AAPL — still owned. OK.
- ep30 Overture/YHOO — divested, recorded, but **price is wrong (finding #2)**.
- ep32 Oculus/META — still owned. OK.
- ep35 SoundJam/AAPL — still owned (became iTunes, internal). OK.
- ep38 Booking/BKNG — still owned. OK.
- ep39 Opsware/HPE — divested, recorded and dated correctly (2017-09-01). OK.
- ep41 AOL/VZ — divested, recorded and dated correctly (2021-09-01). OK.
- ep43 Blue Bottle/NSRGY — **WRONG classification at air date (finding #1) and missing 2026 divestiture (finding #1b)**.
- ep47 Beats/AAPL — still owned. OK.
- ep48 Zappos/AMZN — still owned. OK.
- ep50 Nest/GOOGL — still owned (as Google Nest). OK.
- ep54 PowerPoint/MSFT — still owned. OK.
- ep63 Behance/ADBE — still owned. OK.
- ep64 Venmo/PYPL — still owned. OK.
- ep68 ESPN/DIS — still ~80% Disney-owned (Hearst 20%), no divestiture. OK.
- ep69 ARM/SFTBY — SoftBank still holds a clear majority (~86-87% as of mid-2026); the "no divestiture" treatment is correct even after Arm's 2023 IPO. OK.
- ep70 Instagram/META — still owned (duplicate of ep2/ep7 subject, same status). OK.
- ep88 WhatsApp/META — still owned. OK.
- ep158 Google/GOOGL — still owned (Google is Alphabet's core subsidiary). OK.
- ep165 Formula 1/FWONK — no change to the tracking-stock structure since air date. OK.

No additional un-recorded divestitures found in section C beyond the Blue Bottle/Nestlé case already flagged.

---

## Summary of required CSV changes

1. **episodes.csv row 44 (ep43 Blue Bottle):** reclassify to `skipped` (deal not closed until end-Oct 2017, after the 2017-10-07 air date) — **or**, if kept as `parent`/NSRGY, add the offsetting divest event below.
2. **events.csv:** add `NSRGY,2026-04-27,divest,,,,ep43; Nestlé sold Blue Bottle Coffee to Centurium Capital, ~closed 2026-04-27` (only if ep43 stays a parent row).
3. **events.csv YHOO divest row:** correct the 2017-06-13 sale price from $55.90 to **$52.00**.
4. **episodes.csv row 139 (ep138 Porsche):** either switch `ticker` to `DRPRY` (buy $11.833 close 2023-06-26) for strict rule-7 consistency, or keep P911.DE but correct the source_note's "no US ADR" claim (DRPRY exists, just very thin).
5. **events.csv Stitcher/SSP divest date:** consider tightening 2020-10-19 → 2020-10-16 (actual deal-close date per Scripps' press release); low materiality.
