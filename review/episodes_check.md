# Acquired Episode List — Verification Report

Method: fetched each acquired.fm episode page directly (`curl -sL`), read the page's embedded
JSON-LD `datePublished` (ISO-8601 UTC) and the matching human-readable date printed in the page
body, then converted UTC → America/Los_Angeles (the timezone the site publishes in) to get the
actual local calendar date. Also re-fetched the live RSS feed (`https://feeds.transistor.fm/acquired`)
with full timestamps (not just the date truncated in `review/rss_items.txt`) to check the CSV's
derivation logic.

## 1. Date spot-checks (16 episodes)

| ep | Title | CSV air_date | acquired.fm page date (local PT) | Match? |
|----|-------|--------------|-----------------------------------|--------|
| 1 | Pixar | 2015-10-15 | October 15, 2015 | ✅ match |
| 2 | Instagram | 2015-11-01 (Sun) | **October 31, 2015** (Sat) | ❌ **MISMATCH** (page is 1 day earlier) |
| 21 | Zillow + Trulia | 2016-10-13 | October 13, 2016 | ✅ match |
| 26 | The Amazon IPO | 2016-12-31 (Sat) | December 31, 2016 | ✅ match |
| 29 | The Snap Inc. IPO | 2017-03-04 (Sat) | March 4, 2017 | ✅ match |
| 43 | Blue Bottle Coffee | 2017-10-07 (Sat) | October 7, 2017 | ✅ match |
| 58 | Tesla | 2018-07-16 | July 16, 2018 | ✅ match (see URL note below) |
| 59 | The Xiaomi IPO | 2018-08-05 (Sun) | August 5, 2018 | ✅ match (see URL note below) |
| 71 | The Lyft IPO | 2019-03-30 (Sat) | March 30, 2019 | ✅ match (see URL note below) |
| 73 | The Uber IPO | 2019-05-11 (Sat) | **May 10, 2019** (Fri) | ❌ **MISMATCH** (page is 1 day earlier) |
| 124 | Nvidia Part I | 2022-03-27 (Sun) | **March 28, 2022** (Mon) | ❌ **MISMATCH** (page is 1 day *later*) |
| 140 | Costco | 2023-08-21 | August 21, 2023 | ✅ match (confirms scrape_notes correction) |
| 141 | Nvidia Part III | 2023-09-05 | **September 6, 2023** | ❌ **MISMATCH** (page is 1 day *later*) |
| 154 | Rolex | 2025-02-24 | February 24, 2025 | ✅ match (confirms scrape_notes correction) |
| 165 | Formula 1 | 2026-03-02 | March 2, 2026 | ✅ match |
| 168 | The Walt Disney Company | 2026-06-21 | June 21, 2026 | ✅ match |

**4 of 16 spot-checks disagree with the CSV.** Detail on each:

- **ep2 Instagram** — page JSON-LD `datePublished: 2015-10-31T07:00:00.000Z` → Oct 31, 2015 00:00 PDT.
  CSV/RSS says 2015-11-01 (RSS raw pubDate: `Sun, 01 Nov 2015 09:00:00 -0800`). The RSS pubDate and the
  website's own `datePublished` disagree by more than a timezone quirk (33 hours apart, and they even
  fall on different sides of the Nov 1, 2015 DST-fallback boundary) — this isn't a simple UTC-vs-local
  off-by-one, the two systems appear to just record different values for this very old episode.
- **ep73 The Uber IPO** — page says May 10, 2019 (a Friday); CSV says 2019-05-11 (Saturday). Notably,
  the CSV's own `source_note` already says "Uber IPO'd 2019-05-10 on NYSE" — i.e., the note text and
  the `air_date` column are internally inconsistent, and the real-world Uber IPO date (May 10, 2019,
  a Friday) matches the page, not the CSV's Saturday air_date.
- **ep124 Nvidia Part I** — page says March 28, 2022 (Monday); CSV/RSS says 2022-03-27 (Sunday). Raw
  RSS pubDate is `Sun, 27 Mar 2022 22:09:56 -0700`, i.e. genuinely late Sunday night Pacific — so the
  RSS date is very plausibly right and it's the website's `datePublished` field that's off by a day.
- **ep141 Nvidia Part III** — page says September 6, 2023; CSV/RSS says 2023-09-05. Raw RSS pubDate
  is `Tue, 05 Sep 2023 23:47:30 -0700`, i.e. 23:47 Tuesday night Pacific — again the RSS date looks
  right and the website field looks like it rounded to the next day.

**Note on the "RSS is UTC" hypothesis in the task prompt:** it doesn't hold for the *current* feed —
re-fetching the raw feed shows pubDates already carry explicit non-UTC offsets (`-0700`/`-0800`,
i.e. Pacific time), not `Z`/UTC. So `review/rss_items.txt`'s truncated dates are reliable Pacific
calendar dates already. The 4 mismatches above instead look like errors/quirks in **acquired.fm's own**
`datePublished` metadata (interestingly, in the *opposite* direction from the task's hypothesis for
2 of the 4 — the website date is a day *later*, not earlier, for ep124 and ep141) rather than errors
introduced by the CSV's RSS-based derivation.

**Bonus finding — 3 wrong URLs in `episodes.csv`:** the `source_note` URLs for three episodes point to
the *wrong* episode entirely:
- ep58 Tesla → CSV has `.../the-slack-dpo` (that slug is actually S4E9 "The Slack DPO"). Correct URL:
  `https://www.acquired.fm/episodes/season-3-episode-1tesla`
- ep59 Xiaomi IPO → CSV has `.../the-shopify-ipo` (that slug is actually S5E2 "The Shopify IPO").
  Correct URL: `https://www.acquired.fm/episodes/season-3-episode-2the-xiaomi-ipo`
- ep71 Lyft IPO → CSV has `.../the-uber-ipo` (duplicate of ep73's URL). Correct URL:
  `https://www.acquired.fm/episodes/season-4-episode-4-the-lyft-ipo`

These were found via the sitemap (`https://www.acquired.fm/sitemap.xml`) and used to re-run the
Tesla/Xiaomi/Lyft spot-checks above on the *correct* pages (dates for all three do match the CSV,
per the table — only the URLs were wrong, not the dates).

## 2. Season 12 Episode 1 — "The NFL"

- `https://www.acquired.fm/episodes/the-nfl` currently serves a **remastered re-release**. Its own
  page text says explicitly: *"Note: This is a remastered release of our original January 2023
  episode, updated to today's Acquired production standards. It also features a full hour+ ..."*
  and *"we decided to remaster our NFL episode to today's Acquired production quality standards."*
- The remastered page's own JSON-LD metadata tags it as **Season 19** (`"seasonNumber": "19"`,
  `episodeNumber` empty), `datePublished 2026-01-27T02:45:00Z` → Jan 26, 2026 local (matches
  `review/rss_items.txt` line `S19E-|full|Mon, 26 Jan 2026|The NFL`). So on the live site/feed today,
  "The NFL" is *not* labeled S12E1 at all — it's an unnumbered S19 item, which is why it wasn't
  picked up by the "has both season+episode number" filter either way.
- The remastered page does not itself restate the exact original 2023 air date beyond "January 2023."
  Web search (aggregated from Apple Podcasts / other podcast directories) reports the original
  release as **January 25, 2023**, described as "Season 12, Episode 1." I could not independently
  load Apple's or Podchaser's page content directly (blocked/JS-rendered) to re-verify that season
  label byte-for-byte, so treat "S12E1" as **corroborated but not directly re-confirmed on a primary
  source** — Sources:
  - [The NFL – Acquired – Apple Podcasts](https://podcasts.apple.com/ph/podcast/the-nfl/id1050462261?i=1000606224407)
  - [The NFL | Acquired](https://www.acquired.fm/episodes/the-nfl)
- **Internal corroboration:** `review/rss_items.txt` shows `S12E2|full|Tue, 21 Feb 2023|LVMH` as the
  first item of Season 12 in the current feed. A "The NFL" release on Jan 25, 2023 fits perfectly
  before that as S12E1, with no other candidate for the slot — same pattern as the Costco/Rolex
  corrections already documented in scrape_notes.md.
- **Conclusion: the hypothesis is confirmed.** "The NFL" (original air date ~Jan 25, 2023, S12E1) is a
  real, missing, numbered main-feed deep dive that isn't a public company (so it would be a "skipped"
  row, not scored). If added: **170 total episodes / 55 skipped** (currently 169/54).

## 3. Other missing or extra numbered main-feed episodes

Cross-checked every `S#E#|full|...` line in `review/rss_items.txt` (176 rows) against every
`S#E#` parsed from `episodes.csv`'s `source_note` column (169 rows). Result:

- **In RSS as numbered+full but NOT in episodes.csv (7 rows):** all 7 are titles already excluded by
  scrape_notes.md's stated rules, and correctly so — no missed deep dive:
  - S1E18 "Special: An Acquirer's View into M&A..." (excluded: "Special:" title)
  - S1E27 "Special: A Conversation with Microsoft's Head of Strategic Investments..." (excluded: "Special:")
  - S1E29 "Special: 2016 Review and 2017 Predictions" (excluded: "Special:")
  - S1E51 "2017 Holiday Special" (excluded: holiday special)
  - S10E7 "Arena Show Part I..." (excluded: Arena Show)
  - S10E8 "Arena Show Part II..." (excluded: Arena Show)
  - S13E5 "Holiday Special 2023" (excluded: holiday special)
- **In episodes.csv but not matching any RSS numbered+full row:** none (0). Every one of the 169 CSV
  rows' `S#E#` note corresponds to a real numbered `full`-type RSS item.
- 169 (CSV) = 176 (RSS numbered/full) − 7 (correctly excluded specials) ✓ arithmetic checks out.
- Cross-checked the sitemap (214 `/episodes/*` URLs) against the URLs referenced in episodes.csv;
  the ~55 sitemap URLs not referenced by the CSV are all the same category of exclusion (Specials,
  Holiday Specials, Arena Show, ACQ2-style interviews/sessions, bonus episodes, "the-nfl" itself) —
  no unlabeled numbered deep dive slug was found hiding in the sitemap.
- Net: **the only missing numbered main-feed episode found is "The NFL" / S12E1** (Section 2 above).

## 4. Judgment calls — unnumbered "full" episodes with a public-company subject

For each, I fetched its acquired.fm page and checked (a) whether the page's own JSON-LD assigns it a
season/episode number, and (b) how the site itself categorizes/badges the page.

| Episode | RSS type | RSS date | Page season/ep (JSON-LD) | Site badge/category |
|---|---|---|---|---|
| NVIDIA CEO Jensen Huang | full | Sun, 15 Oct 2023 | no season/episode number | **"Interviews"** (badge links to `/features/interviews`) |
| Spotify CEO Daniel Ek | full | Wed, 17 May 2023 | no season/episode number | **"Interviews"** |
| Uber CEO Dara Khosrowshahi | full | Mon, 12 Jun 2023 | no season/episode number | **"Interviews"** |
| The Mark Zuckerberg Interview | bonus | Tue, 17 Sep 2024 | Season 15, no episode number | **"Interviews"** |
| Short: The Death of Sega | full | Mon, 17 Apr 2023 | no season/episode number | **"Interviews"** |
| Special: Spotify + Gimlet/Anchor Quick Take | bonus | Mon, 18 Feb 2019 | no season/episode number | **"Interviews"** |

Facts, no recommendation:
- All six are tagged `itunes:episodeType=full` or `bonus` in the RSS feed, but **none carry an
  `itunes:episode` number**, so they were already excluded by the CSV's stated "numbered only" filter
  regardless of the "Interviews" categorization.
- All six are labeled **"Interviews"** by acquired.fm itself (a literal on-page badge/link to
  `/features/interviews`), including the two whose titles look like regular episodes ("Short: The
  Death of Sega" and the Spotify/Gimlet "Special:") and the two CEO-interview titles that read like
  they could be deep dives (Jensen Huang, Daniel Ek, Dara Khosrowshahi are all full-length "full"
  episodes about public companies, not obviously shorter than a numbered episode).
  This confirms the site treats "Interviews" as a distinct section from the numbered "Episodes"
  season/episode sequence — consistent with, but independent evidence for, excluding them.
  The Mark Zuckerberg Interview is additionally typed `bonus` in RSS and tagged to Season 15 (same
  season as the S15E1 live show) but still has no episode number.
- No page-level evidence contradicts the CSV's exclusion of any of the six; this section is provided
  so the exclusion rule can be reviewed against the site's own categorization, per your instruction not
  to have this agent make the final call.
