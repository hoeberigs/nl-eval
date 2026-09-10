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
    fontFamily: "Sofia Sans Condensed 800, system-ui"
    fontSize: "clamp(20px, 2.2vw, 31px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.06em"
  headline:
    fontFamily: "Sofia Sans Condensed, system-ui"
    fontSize: "clamp(28px, 3vw, 36px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.02em"
  score:
    fontFamily: "Sofia Sans Condensed, system-ui"
    fontSize: "34px"
    fontWeight: 700
    lineHeight: 1
  title:
    fontFamily: "Sofia Sans Condensed, system-ui"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.05
  flap:
    fontFamily: "Sofia Sans Condensed, system-ui"
    fontSize: "18px"
    fontWeight: 700
    letterSpacing: "0.08em"
  body:
    fontFamily: "Sofia Sans, system-ui"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Sofia Sans Condensed, system-ui"
    fontSize: "14px"
    fontWeight: 600
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
  legend-panel:
    backgroundColor: "{colors.board-ink}"
    textColor: "{colors.signal-blue}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
---

# Design System: nl-eval

## Overview

**Creative North Star: "The NS Departure Board"**

A station board, not a leaderboard: one row per model, sections that lose more than ten points listed as stations it runs via, a flap reading the stability band, WANKEL or NIET the stability band. Below the board, light tile and prose.

**Key Characteristics:**
- One yellow: remarks, stability band, stamp, focus.
- State is a flap, strike or glyph before it is a colour.
- No boxes, cards, radius, gradients or shadows; rows ride hairlines.

## Colors

### Primary
- **Signal Blue** (#081858): board field, code block, footer rule, flap type.
- **Board Ink** (#f4f6fb): board type, flap face, legend panel, passed bands.

### Secondary
- **Remark Yellow** (#ffc917): stamp, the 2px strip and column rules, remark lines, sections that lose more than ten points and bands, stability band, cancelled-run flap text, selection, focus rings.

### Neutral
- **Board Dim** (#a9b8e0): column heads, intervals, provider, struck sections, failed-band outline.
- **Board Seam** (rgba 255,255,255,.16): every board hairline.
- **Station Tile** (#e9ebee), **Tile Ink** (#14203f), **Tile Mute** (#4c5a83), **Tile Rule** (#b9c0cf): prose ground, text, notes, hairlines.

**The One Yellow Rule.** Yellow means attention and never fills anything larger than a band.

**The Mark Before Hue Rule.** A verdict is a word, strike or glyph (check, wave, cross) before colour.

## Typography

**Display Font:** Sofia Sans Condensed 800
**Board Font:** Sofia Sans Condensed
**Body Font:** Sofia Sans

### Hierarchy
- **Display** (700, clamp 20 to 31px, uppercase, .06em): masthead only.
- **Headline** (700, clamp 28 to 36px, uppercase): prose section heads.
- **Score** (700, 34px, tabular): row lead; interval beneath at 13px.
- **Title** (700, 24px): model names; 22px track names.
- **Flap** (700, 18px, uppercase, .08em): verdict text.
- **Body** (400, 18px, 1.5, max 68ch): prose; 17px in tables.
- **Label** (600, 14px, uppercase, .14em): column and perron heads.

**The Tabular Rule.** Every number is tabular with a comma decimal.

## Layout

 Prose: 1344px max, sections 48px top and 36px apart on a tile hairline, two columns at auto-fit 320px, 40px gap.

Under 1100px the perron drops below the board, the column rule turns horizontal, the natural height claim is released. Under 700px body is 17px, scores 28px, names 20px, flaps 14px, track labels stack above the rail. Tables scroll in their own container; the page never scrolls sideways.

## Elevation & Depth

No shadows, gradients or blur; depth is two tones and hairline seams.

**The Hard Edge Rule.** Everything meets at a hard edge; row hover is a 4% white wash, nothing more.

## Shapes

Radius 0. Rows on 1px seams, structure on 2px rules. The flap carries a 1px hinge seam. Bands are 10px bars; failed bands are dim outlines.

## Components

### Board Row
Score with interval, name over provider, via line, remark line, and per-section detail (accuracy, interval, n) on click or keyboard focus (hover only paints a wash, so the board never reflows under the pointer) via one aria-expanded button. Controls sort last.

### Via Line
Passed in ink, undecided in yellow, failed struck in dim, middot-separated.

### Flap
Ink rectangle, blue uppercase text, hinge seam. A run that did not ride shows the cancelled variant: yellow text, no face.

### Perron Track
96px row: section name left, rail right; one band per model at 14px pitch, 2px yellow stability band, 50 to 100 axis with the pass mark in yellow.

### Legend Panel
The one calm panel: glyph then word per verdict, pass rule, click hint.

### Prose Section and Data Table
Headline, two-column body, optional table: heads in tile mute on a 2px ink rule, rows on tile hairlines, first column condensed uppercase, numbers right-aligned.

### Motion
Flaps rotate in from rotateX(-90deg) over 450ms; rows fade up 6px over 500ms, staggered 70ms, replayed on sort; both only under prefers-reduced-motion: no-preference.

## Do's and Don'ts

### Do:
- **Do** pin the interval beside every score and verdict.
- **Do** hold AA or better: ink on blue about 16:1, dim 8:1, yellow 10:1, mute on tile 5.7:1.
- **Do** keep the 3px yellow focus ring on every interactive element.

### Don't:
- **Don't** add cards, boxes, radius, shadows, gradients, a second accent or per-model colours.
- **Don't** animate beyond the flap, or at all under reduced motion.
- **Don't** let a table widen the page.


## Small screens

Under 700px the Uitslag column is hidden and the verdict flap is rendered directly under the provider line, above the via line, so the verdict stays in the first viewport without sideways scrolling. Under 1100px the board, then the verdict line and legend, then the perron stack vertically; the perron is sticky beside the rows only on wide screens.


## Code

Commands and file names use the system monospace stack `ui-monospace, SFMono-Regular, Menlo, monospace` at 0.9em; blocks sit on the signal blue with board ink, scrollbars themed with the dim token. It carries real commands only, never a costume for "technical".


## Reframe, 10 September 2026

The exam vocabulary is gone. The score cell carries worst-case accuracy with the undisturbed score beneath it; the flap carries the stability band and the drop; the via line marks sections that lose more than ten points under pressure (yellow, wave) or sit under 60% (struck, cross). On the perron a band runs from worst case (left) to undisturbed (right); untested models are a 2px tick in the dim token. No stability band.
