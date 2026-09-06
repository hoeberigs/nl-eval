---
name: nl-eval
description: A Dutch language exam for models, read as an NS departure board.
colors:
  signal-blue: "#081858"
  board-ink: "#f4f6fb"
  board-dim: "#a9b8e0"
  remark-yellow: "#ffc917"
  board-seam: "rgba(255,255,255,.16)"
  station-tile: "#e9ebee"
  tile-ink: "#14203f"
  tile-mute: "#4c5a83"
  tile-rule: "#b9c0cf"
typography:
  display:
    fontFamily: "Phudu, Sofia Sans Condensed, system-ui, sans-serif"
    fontSize: "clamp(20px, 2.2vw, 31px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.06em"
  headline:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, system-ui, sans-serif"
    fontSize: "clamp(28px, 3vw, 36px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.02em"
  score:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, system-ui, sans-serif"
    fontSize: "34px"
    fontWeight: 700
    lineHeight: 1
  title:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.05
  flap:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    letterSpacing: "0.08em"
  body:
    fontFamily: "Sofia Sans, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.14em"
rounded:
  none: "0"
spacing:
  cell: "9px 6px"
  gutter: "clamp(16px, 3.3vw, 48px)"
  column-gap: "36px"
  section: "48px"
  section-gap: "36px"
components:
  flap:
    backgroundColor: "{colors.board-ink}"
    textColor: "{colors.signal-blue}"
    typography: "{typography.flap}"
    rounded: "{rounded.none}"
    padding: "8px 12px"
    width: "150px"
  flap-cancelled:
    backgroundColor: "transparent"
    textColor: "{colors.remark-yellow}"
    typography: "{typography.flap}"
    padding: "8px 0"
  legend-panel:
    backgroundColor: "{colors.board-ink}"
    textColor: "{colors.signal-blue}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
  code-block:
    backgroundColor: "{colors.signal-blue}"
    textColor: "{colors.board-ink}"
    rounded: "{rounded.none}"
    padding: "16px 18px"
---

# Design System: nl-eval

## Overview

**Creative North Star: "The NS Departure Board"**

The page is a station board, not a leaderboard. The first viewport is a deep signal-blue field with white condensed type; one row per model, the sections it passed listed as the stations it runs via, and a split-flap that says GESLAAGD, ONBESLIST or NIET GESLAAGD. Below the board the ground turns to light station tile and the voice turns to prose. Density is high on the board, calm on the tile.

**Key Characteristics:**
- Two grounds only: signal blue for the board, station tile for prose.
- One yellow, reserved for remarks, the pass line, the stamp and focus.
- State is a flap, a strikethrough or a mark before it is a colour.
- No boxes, cards, radius, gradients or shadows; rows ride hairline rules.
- One motion: the split-flap reveal.

## Colors

A three-colour board (blue, white, yellow) over a neutral tile ground.

### Primary
- **Signal Blue** (#081858): the board field, the code block, the footer rule and the flap's own type colour.
- **Board Ink** (#f4f6fb): board type, the flap face, the legend panel, and the pass bands on the perron.

### Secondary
- **Remark Yellow** (#ffc917): the generation stamp, the yellow rule under the strip and between board columns, the Opmerkingen line, undecided sections in the via line, undecided bands, the pass line, a cancelled run's flap text, text selection and every focus ring.

### Neutral
- **Board Dim** (#a9b8e0): column heads, intervals, provider line, struck sections, axis figures and the outline of a failed band.
- **Board Seam** (rgba 255,255,255,.16): every hairline rule on the board.
- **Station Tile** (#e9ebee): the prose ground.
- **Tile Ink** (#14203f) and **Tile Mute** (#4c5a83): prose text and notes.
- **Tile Rule** (#b9c0cf): hairlines between prose sections and table rows.

### Named Rules
**The One Yellow Rule.** Yellow is the board's only accent and it means "attention": remarks, the pass line, undecided. It never fills a surface larger than a band.

**The Mark Before Hue Rule.** Every verdict is carried by a word (flap), a strike (via line), or a glyph (check, wave, cross) before any colour is applied.

## Typography

**Display Font:** Phudu (falls back to Sofia Sans Condensed)
**Board Font:** Sofia Sans Condensed
**Body Font:** Sofia Sans

**Character:** a hard, upright signage voice on the board; the same family's text cousin for prose, so the two grounds read as one station.

### Hierarchy
- **Display** (700, clamp 20 to 31px, uppercase, .06em): the masthead only.
- **Headline** (700, clamp 28 to 36px, uppercase): prose section heads.
- **Score** (700, 34px, tabular): the leading number in each row; its interval sits under it at 13px.
- **Title** (700, 24px): model names; 22px for perron track names and h3.
- **Flap** (700, 18px, uppercase, .08em): verdict text.
- **Body** (400, 18px, 1.5, max 68ch): prose; 17px in data tables.
- **Label** (600, 14px, uppercase, .14em): column heads and the perron head.

**The Tabular Rule.** Every number on the page uses tabular figures and a comma decimal.

## Layout

The board is a two-column grid: the table column capped at 780px, the perron takes the rest, a 2px yellow rule between them with 36px on either side. Page gutters are clamp(16px, 3.3vw, 48px). The strip is 74px tall with a 2px yellow bottom rule. Cells are 9px by 6px; column heads 10px. The board claims min-height 100vh.

Prose sections are 1344px max, 48px top padding, 36px apart on a tile hairline; two-column prose uses auto-fit at 320px with a 40px gap.

Responsive: under 1100px the perron drops below the board, the vertical yellow rule becomes horizontal, and the 100vh claim is released. Under 700px body drops to 17px, scores to 28px, names to 20px, flaps to 14px, and perron tracks stack the label above the rail. Tables scroll inside their own container; the page never scrolls sideways.

## Elevation & Depth

No shadows, no gradients, no blur. Depth is two tones (blue field, tile ground) and hairline seams. The only lifted surface is the flap and legend, both flat board ink on blue.

**The Hard Edge Rule.** Everything meets at a hard edge. Hover on a row is a 4% white wash, nothing more.

## Shapes

Radius is 0 everywhere. Rows are separated by 1px seams; structural divisions are 2px yellow or blue rules. The flap is a rectangle with a 1px seam across its middle (the split-flap hinge). Perron bands are 10px-tall bars; a failed band is an outline in dim rather than a fill.

## Components

### Board Row
A run, sorted with controls last. Score with interval, model name over provider, then the via line, the remark line, and on hover, focus or click a per-section detail line (accuracy, interval, n). The whole cell is one button with aria-expanded; failed and control rows render at half opacity.

### Via Line
Passed sections in ink, undecided in yellow, failed struck in dim, separated by middots.

### Flap
Board ink rectangle, blue uppercase text, hinge seam. A run that did not ride shows the cancelled variant: yellow text, no face.

### Perron Track
96px tall row: section name left, rail right. One band per model stacked at 14px pitch, a 2px yellow pass line, labels in dim, an axis from 50 to 100 with the pass mark in yellow.

### Legend Panel
The one calm panel on the field: ink on blue, glyph then word for each verdict, the pass rule, the click hint. Body font, inline-block.

### Prose Section and Data Table
Headline, two-column body, optional table. Table heads in tile mute under a 2px tile-ink rule; rows on tile hairlines; first column in condensed uppercase; numeric cells right-aligned.

### Motion
Flaps rotate in from rotateX(-90deg) over 450ms; rows fade up 6px over 500ms, staggered 70ms per row, replayed on sort. Both live only inside prefers-reduced-motion: no-preference.

## Do's and Don'ts

### Do:
- **Do** render every figure from results.json; nothing is typed by hand.
- **Do** pin the interval beside every score and verdict.
- **Do** keep contrast at AA or better: ink on blue about 16:1, dim on blue about 8:1, yellow on blue about 10:1, mute on tile about 5.7:1.
- **Do** carry every state as a word or glyph first.
- **Do** keep the yellow focus ring (3px, 2px offset) on every interactive element.

### Don't:
- **Don't** add cards, boxes, radius, shadows or gradients.
- **Don't** introduce a second accent or a per-model colour.
- **Don't** add motion beyond the flap; nothing animates under reduced motion.
- **Don't** let a table widen the page; it scrolls in its own container.
