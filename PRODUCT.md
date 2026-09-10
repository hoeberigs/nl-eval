# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS on GitHub Pages from `/docs`, no framework and no chart
library. The page reads `docs/results.json`, which `nl-eval --publish` builds
from the run reports in `results/`. Every number on the page is rendered from
that file at runtime; nothing is hard-coded. The benchmark itself is a Python
package (`src/nleval`) with a CLI. Existing codebase, not a greenfield decision.

## Users

People choosing or building a language model for Dutch: ML engineers at Dutch
companies comparing hosted models, researchers and open-model builders who
want a Dutch signal that is not a translation, and journalists or procurement
staff who want a defensible yes-or-no rather than a leaderboard position.
They arrive from GitHub or a link, technically literate, and sceptical of
benchmark numbers by default.

## Product Purpose

Answer how stable a model's Dutch is: every item is asked in its original
form and in six meaning-preserving variants, and the headline is the share
of items a model gets right under all of them. Success is a reader who leaves
knowing a model's worst case, how much it loses under pressure and where, and
whether the score can be trusted at all.

## Positioning

Worst-case accuracy over a variant battery rather than a single accuracy
number, on Dutch-specific sections rather than a translated English
benchmark. Three properties a neighbouring benchmark cannot copy cheaply: every item is scored without a judge model (multiple choice,
likelihood on minimal pairs, exact-match error correction), so the score is
reproducible and free of judge bias; a never-committed held-out split and a
canary make contamination testable rather than assumed; and consistency
probes (options reversed, register swapped) report how much of a score is
positional habit. Prior art is acknowledged on the page: EuroEval, BLiMP-NL,
Global-MMLU. This suite supplements them; it does not pretend they are absent.

## Constraints and durable facts

- No judge model, ever. If an item cannot be scored deterministically it does
  not go in.
- Layers are never blended into one number. Per-section results with Wilson
  intervals, the chance baseline, and the controls (echo, always-a) stay
  visible on the page as the floor.
- No pass line and no verdict. The board reports levels, drops and where the
  drops sit; the stability bands (stabiel, wankel, onstabiel) are published
  thresholds on the drop, not judgements.
- Spreken and Luisteren (speech) are out of scope and the page says so.
- Global-MMLU is presented as an indicator, never as evidence, because MMLU
  is heavily contaminated.
- The spend ceiling in the CLI is enforced. Costs of every published run are
  in the run report.
- Attribution: BLiMP-NL (CC-BY-4.0; human ratings CC BY-SA 4.0), Global-MMLU
  (Apache-2.0), hand-written items MIT. Attribution stays on the page.

## Terminology

- **Taalvorm** — word order, variants, formatting and the BLiMP-NL minimal
  pairs; **Spelling en grammatica** — de/het, diminutives, spelling, verb
  spelling, Taaladvies cases.
- **Schrijven** — exact-match error correction: the model rewrites a flawed
  sentence; scored against the corrected string.
- **Lezen** — short passage comprehension in Dutch.
- **Worst-case** — share of items answered correctly under the original form
  and all six variants of the battery.
- **Drop** — original minus worst-case, in accuracy points; banded as
  stabiel, wankel, onstabiel.
- **Flip rate** — share of answers that change under a perturbation that does
  not change the correct answer.
- **Held-out gap** — public minus held-out accuracy, read against the minimum
  detectable difference.

## Accessibility

Colour never carries a state alone; bands and drops are also words and
symbols. Contrast in light and dark checked before shipping. Tables scroll in
their own container, never the page.

## Open decisions

- Visitor mode and visual world for this surface are recorded in the surface
  brief and DESIGN.md, not here.
