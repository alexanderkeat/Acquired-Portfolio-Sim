# Acquired (acquired.fm) — Visual Brand Notes

Sources: https://www.acquired.fm/ (homepage HTML), stylesheet at
`https://cdn.prod.website-files.com/68575598833e9d27c4de294b/css/acquiredfm.webflow.shared.782d4c766.min.css`
(Webflow-hosted site, custom domain fonts at `fonts.acquired.fm`).

## 1. Color palette (from CSS custom properties, verified — not guessed)

Correction to the common assumption: the **current** site is not navy+gold. Default theme:

- **Background**: warm off-white, `#fffcf5` (`--warm-white`) — dark mode / footer uses near-black `#1b1915` (`--black`)
- **Foreground / body text**: near-black `#1b1915` (`--black`) on light; `#fffcf5` on dark
- **Accent (primary brand color)**: bright mint/teal `#28f1c0` (`--acquired-teal--500`), with a deeper teal `#17cb9f` (`--acquired-teal--600`) for hover/secondary states
- **Link color**: inherits `--accent` (the mint teal above)

Secondary palette exists as **per-episode theme colors** (each episode/company gets its own accent — teal, coral, gold, cobalt, sage, orange, brown, charcoal), e.g.:
- gold: `#c4a355` (500) / `#4d3904` (dark) / `#f7ebd1` (light)
- coral: `#ba4d4d`, cobalt: `#3865d0`, sage: `#5fa832`, orange: `#e88a2f`

So gold/navy is one of several episode accent themes, not the site's own brand color — the site itself now reads cream + near-black + mint teal. Use the mint teal (`#28f1c0`/`#17cb9f`) as the accent if matching the current live brand; use gold only if intentionally evoking the podcast's older/legacy look.

## 2. Typography

- **Display/heading font**: `"Founders Grotesk Condensed"` (weights 400/500), fallback stack `Tahoma, sans-serif`. Condensed grotesk, used uppercase with `letter-spacing: .03em` on headings/nav/buttons.
- **Body font**: `"Reckless Standard S"` (weights 400/500, incl. italics), fallback `"Times New Roman", sans-serif`. A quirky, high-contrast serif — this is Acquired's signature "voice" font for body copy and pull quotes.
- **Secondary serif**: `"Reckless Condensed M"` — condensed variant of the same serif family, used for large display type.
- **UI/sans font**: `Geist` (weight 400) — used for smaller UI chrome.
- Line-height: 145% body, 110–120% headings. Letter-spacing: `.01em` body, `.03em` display.
- Uppercase + letter-spacing is used consistently for nav items, badges, and buttons.

**Not on Google Fonts** — all four (Founders Grotesk Condensed, Reckless Standard S, Reckless Condensed M, Geist) are custom/licensed fonts self-hosted at `fonts.acquired.fm` and Webflow's CDN. Closest Google Fonts fallbacks for the report:
- Founders Grotesk Condensed → **Oswald** (condensed grotesk, similar weight/proportions)
- Reckless Standard S / Reckless Condensed M → **Fraunces** (quirky high-contrast serif, closest personality match; Playfair Display is a safer but blander alternative)
- Geist → **Inter** (near-identical geometric UI sans; Geist's own designer cites Inter as a close cousin)

## 3. Logo

The wordmark is not a raster image — it's an **inline SVG** embedded directly in the page markup (`<svg viewBox="0 0 1044 135">`, aspect ratio ≈ 7.7:1, wide horizontal lockup), so there's no standalone logo file URL to link to. It renders as "ACQUIRED" in a bold, uppercase, condensed sans (matches the Founders Grotesk Condensed display font), tight letter-spacing, single color (black on light backgrounds / warm-white on dark) — no gradient or effects.
Favicon: `https://cdn.prod.website-files.com/.../69523717d3e337d888a80099_favicon.png` (32x32 PNG, light variant) with a separate dark-mode favicon.

**Do not download/embed the actual logo.** To evoke it with pure CSS/text in the report:
```css
.acquired-wordmark {
  font-family: 'Oswald', Tahoma, sans-serif; /* stand-in for Founders Grotesk Condensed */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em; /* wider than source's .03em reads better at small sizes in a fallback font */
  color: #1b1915; /* or accent teal #17cb9f for a colored variant */
}
```
Text content: `ACQUIRED`.

## 4. UI motifs

- **Buttons**: fully rounded pills (`border-radius: var(--r-full)`), uppercase label, letter-spaced, ~50–56px tall, background-blur behind translucent fills; hover swaps fill to the mint teal accent.
- **Cards** (episode items): small radius (`--r-sm`/`--r-2xs`, roughly 4–8px), thin 1px border, generous internal padding — not sharp rectangles, not heavily rounded.
- **No visible rule/divider elements** in the CSS (no dedicated `.divider`/`hr` styling found) — sections separate via whitespace and background-color blocks rather than lines.
- Per-episode "theme" system: each episode page swaps `--background`/`--foreground`/`--accent` to that company's color story (e.g., Disney navy, Ferrari burgundy, Hermès gold) — this is the source of Acquired's reputation for rich, company-specific color moods even though the site chrome itself is neutral cream/black/teal.
