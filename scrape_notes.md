# Acquired Podcast — Main Feed Episode List: Scrape Notes

## Total count
**169 main-feed, numbered episodes**, chronologically from Episode 1 (Pixar, 2015-10-15) through Episode 169 (Disney: The Renaissance and the Empire, 2026-08-09), as of 2026-09-04.

## Sources used
1. **RSS feed** — https://feeds.transistor.fm/acquired (primary source; fetched directly via curl, 216 `<item>` entries, parsed for title, `itunes:season`, `itunes:episode`, `itunes:episodeType`, `pubDate`, and `link`).
2. **acquired.fm sitemap** — https://www.acquired.fm/sitemap.xml (214 `/episodes/*` URLs; used to build correct per-episode source URLs, since most `<link>` fields in the RSS feed point to the bare homepage rather than the episode page).
3. **Individual acquired.fm episode pages** (spot-checked) — e.g. https://www.acquired.fm/episodes/rolex, https://www.acquired.fm/episodes/costco, https://www.acquired.fm/episodes/the-nfl — used to resolve date discrepancies (see below).
4. **Wikipedia** — https://en.wikipedia.org/wiki/Acquired_(podcast) — has no episode table, but states "214 episodes as of June 4, 2026," which was used as a cross-check.
5. `acquired.fm/episodes` (the paginated web listing) could not be fully paginated — its pagination is client-side JS, so a static fetch only ever returns the first page (~20 episodes) regardless of `?page=N`. It was used for spot checks instead of full pagination.

## Cross-check
- Counting all non-trailer items in the RSS feed with pubDate ≤ 2026-06-04 gives **213**, closely matching Wikipedia's stated "214 episodes as of June 4, 2026." This confirms Wikipedia's count refers to *all* main-feed items (numbered episodes + bonus/interview/"Special:" episodes + Arena Show, but excluding ACQ2, which is a separate feed/section), not the narrower "numbered season episode" definition used for this CSV.
- The acquired.fm sitemap independently lists 214 `/episodes/` pages, consistent with the same total.
- Our filtered count of 169 is the subset of that ~214 total after removing: episodes with no `itunes:season`/`itunes:episode` number (all bonus-type items, "ACQ Sessions", interview-only episodes, live-show announcements without a number, and the podcast trailer), plus items excluded by title even though numbered (see below).

## Filtering rules applied
- **Included:** only RSS items with both `itunes:season` and `itunes:episode` populated, AND whose title does not match a special/holiday/Arena pattern.
- **Excluded regardless of numbering:**
  - Titles starting with "Special:" (interview specials), e.g. S1E18, S1E27, S1E29, S4E3 ("Special: Spotify + Gimlet/Anchor...").
  - "Holiday Special" episodes: S1E51 ("2017 Holiday Special"), S13E5 ("Holiday Special 2023").
  - "Arena Show" episodes: S10E7 and S10E8 ("Arena Show Part I / Part II").
  - "The NFL" (Jan 2026 release) — confirmed via https://www.acquired.fm/episodes/the-nfl to be **a remastered rebroadcast of the original January 2023 episode**, so it is excluded as a rebroadcast. (It also has no `itunes:episode` number in the feed, so it would have been excluded either way.)
- **Excluded via "numbered only" rule** (naturally covers ACQ2-style crossovers, bonus episodes, and interview-only sessions without needing separate rules): all `itunes:episodeType=bonus` items, all "ACQ Sessions"/"Sessions:"/standalone CEO-interview episodes with no episode number (e.g. Charlie Munger, NVIDIA CEO Jensen Huang, Uber CEO Dara Khosrowshahi, Spotify CEO Daniel Ek, Howard Marks & Andrew Marks, 7 Powers with Hamilton Helmer, Michael Mauboussin Master Class, etc.), the two large live-event announcement/recap episodes with no number ("Acquired Live at Radio City Music Hall", "Chase Center + Summer Update"), and the podcast trailer.
- **Included despite being "live" episodes:** episodes that ARE part of the regular numbered sequence even though recorded live or with heavy guest content, e.g. S1E23 "NeXT (Live show at the GeekWire Summit)", S3E7 "Venmo (live with Andrew Kortina)", and S15E1 "Acquired LIVE from Chase Center (with Daniel Ek, Emily Chang, Jensen Huang and Mark Zuckerberg)" — these carry real season/episode numbers in the feed and are full deep-dive episodes, not brief specials, so they were kept.
- Multi-part deep dives (Nvidia I/II/III, Netflix Part 1/2, Berkshire Hathaway I/II/III, Standard Oil I/II, Andreessen Horowitz I/II, Google Part I/II/III, Microsoft Volume I/II, Nintendo's Origins + Nintendo: The Console Wars, etc.) are each listed as their own row, per instructions.

## Date discrepancies found and resolved
The RSS feed's `pubDate` is **not reliable as an original air date** for episodes that were later re-uploaded/re-edited by Acquired — in at least two cases the pubDate jumped forward by more than a year relative to where the episode sits in its own season's numbering sequence:

1. **"Costco" (S13E2)** — RSS pubDate: 2026-03-03. This is out of sequence (S13E1 aired 2023-07-24, S13E3 aired 2023-09-05). Verified via https://www.acquired.fm/episodes/costco, whose page states the air date as **2023-08-21**, "Season 13 | episode 2" — fits perfectly between E1 and E3. **Used 2023-08-21 in the CSV.**
2. **"Rolex" (S16E2)** — RSS pubDate: 2026-03-04. Also out of sequence (S16E1 aired 2025-01-26, S16E3 aired 2025-03-23). Verified via https://www.acquired.fm/episodes/rolex, which states the air date as **2025-02-24** — again fits perfectly between E1 and E3. **Used 2025-02-24 in the CSV.**

All 167 other numbered episodes had RSS pubDates that fit monotonically into their season's chronological sequence (verified programmatically — dates strictly increase by episode number within every season except the two cases above), so RSS pubDate was trusted as the air date for those.

## Borderline / uncertain items worth flagging
- **"Costco" and "Rolex"** (see above) — their true original air dates required deduction/verification outside the RSS feed; flagged in case Acquired's own metadata is later corrected or disputes this reading.
- **S12E1 appears to be missing** from the feed entirely — Season 12 jumps from (nonexistent) E1 directly to E2 (LVMH, 2023-02-21). Could not find any RSS item or web reference for a "Season 12 Episode 1." This is left as a gap; no episode was fabricated to fill it.
- **"The NFL"** — technically could be viewed as a new episode (added ~1 hour of new follow-up content) rather than a pure rebroadcast, but since Acquired's own episode page explicitly calls it "a remastered release of our original January 2023 episode," it was excluded per the task's rebroadcast-exclusion rule.
- **Season numbering vs. website "season" labels**: the RSS feed's `itunes:season` field (S1–S20, monotonically increasing) differs from the season labels acquired.fm's own web page displays for recent episodes (e.g. "Sp26", "F25", "Su25" — quarter+year labels). The CSV's `source_note` uses the RSS-style `S#E#` numbering per the task's instructions, since that's the "Season N Episode M" scheme described in the request.
- A handful of RSS `<link>` fields pointed only to the bare homepage (`http://acquired.fm/`) rather than the episode page; correct episode URLs for these were resolved via the acquired.fm sitemap and, for 18 titles with wording differences between the RSS title and the website slug (e.g. RSS "Google Part I: Origins of Search" vs. website slug `google`; single-word titles like "ESPN", "Nest", "GitHub", "PowerPoint" whose slugs are oddly formatted, e.g. `season-2-episode-3nest`), matched manually by inspecting the sitemap.
