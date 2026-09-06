# nl-eval

A Dutch-language evaluation suite for language models, in three layers: **native
Dutch grammar**, **translated breadth**, and **applied Dutch** that no existing
benchmark covers.

```bash
nl-eval --suite all          # all three layers, scored separately
nl-eval --suite core         # the 189 hand-written items, no network needed
nl-eval --validate           # check the item set, no API calls, no spend
```

## Why not just translate an English benchmark

That is the obvious move and it is the weaker one.

1. **It is already done.** [Global-MMLU](https://huggingface.co/datasets/CohereLabs/Global-MMLU)
   ships a Dutch subset of ~14.3k questions under Apache-2.0. Re-translating
   MMLU duplicates free work.
2. **Translated items largely measure translated English.** The questions keep
   their source-language shape, and culture-bound knowledge does not survive
   the trip. A model can score well on translated Dutch while handling actual
   Dutch badly.
3. **The hardest Dutch has no English source.** There is no English sentence
   that becomes *"welk lidwoord hoort bij beleid"*. `de`/`het`, the tussen-n,
   and the u/je register that governs Dutch business correspondence cannot be
   produced by translating anything.

So this suite uses translation only where breadth is the point, takes its
grammar layer from a corpus built in Dutch, and hand-writes the rest.

## The three layers

| Layer | Source | What it measures | Licence |
|---|---|---|---|
| **L1 grammar** | [BLiMP-NL](https://huggingface.co/datasets/juletxara/blimp-nl) — 9,000 minimal pairs, 22 phenomena, 84 paradigms, human acceptability from 30+ raters | Native Dutch syntax | CC-BY-4.0 |
| **L2 breadth** | Global-MMLU (nl), ~14.3k | Knowledge and reasoning, comparable across languages | Apache-2.0 |
| **L3 applied** | 189 hand-written items, 10 categories | Orthography, register, notation, civics, false friends, BE/NL | MIT |

L1 and L2 are **fetched at run time and never redistributed**. They download on
first use into a gitignored cache under `.cache/sources/`, so their licences
stay with their publishers and this repository ships only the adapter. Full
citations in [ATTRIBUTION.md](ATTRIBUTION.md).

`--suite core` needs no network at all.

### The layers are never blended into one number

A single headline mixing native grammar with translated knowledge cannot be read
as either. The runner scores per category, and the chance baseline is published
next to every score because it differs by layer: L1 is two-option (0.50), L2 is
four-option (0.25), L3 is mixed (0.339).

## No judge, by design

Every item is multiple choice or exact string match. Nothing needs an LLM to
grade it, which means:

- **A full core run costs about €0.01** on a small model (~30k input tokens).
- **Scores are deterministic.** A change in the number is a change in the model.
- **No judge bias.** An LLM-judged Dutch suite inherits the judge's own Dutch
  weaknesses, which is exactly what is under test.

## Controls ship with the suite

An evaluation that cannot be gamed by accident needs its own baselines, so two
are built in and cost nothing:

```bash
nl-eval --provider echo       # answers nothing at all
nl-eval --provider always-a   # always answers "A"
```

| Control | Accuracy | Chance | Reading |
|---|---|---|---|
| `echo` | 0.000 | 0.339 | The scorer awards no free marks; 189/189 replies logged unparseable |
| `always-a` | 0.354 | 0.339 | +1.6pp over chance, so the answer key is position-balanced |

If `always-a` ever scores well above chance, the answer key has drifted onto one
letter and the suite is measuring letter preference. `--validate` checks this
automatically, including for the externally-sourced layers.

## Running it

```bash
git clone https://github.com/hoeberigs/nl-eval.git
cd nl-eval
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Free, no key, no network:

```bash
nl-eval --validate
nl-eval --provider echo --suite core
```

Free, local model via [Ollama](https://ollama.com):

```bash
ollama pull qwen2.5:7b
nl-eval --provider ollama --model qwen2.5:7b --suite all
```

Hosted models:

```bash
export OPENAI_API_KEY=...
nl-eval --provider openai --model gpt-5-mini --suite all --max-spend 0.50
```

```bash
export ANTHROPIC_API_KEY=...
nl-eval --provider anthropic --model claude-haiku-4-5-20251001 --suite core --max-spend 0.50
```

### The spend ceiling is enforced, not advisory

`--max-spend` is a euro ceiling checked **before the first API call**. The run
refuses to start if the estimate exceeds it and says what to cut. The default is
€1.00 and the price table deliberately over-estimates: the purpose is to prevent
an accidental spend, so being wrong in the cautious direction is correct.

Narrow a run rather than raising the ceiling:

```bash
nl-eval --suite core --category de_het,spelling --limit 40
```

## Interpreting a result

Report accuracy **with its interval and against the baseline**. Per-category
samples run from 8 to 40 items in L3, so a category score carries a wide Wilson
interval and small differences between two models on one category are usually
noise. The suite emits these automatically:

```json
{
  "accuracy": 0.7196,
  "ci95": [0.6513, 0.7791],
  "chance_baseline": 0.3386,
  "lift_over_chance": 0.381,
  "unparsed_replies": 2,
  "by_category": { "de_het": { "n": 40, "accuracy": 0.85, "ci": [0.706, 0.932] } }
}
```

Watch `unparsed_replies`. A model that ignores the output format is being scored
on instruction-following as much as on Dutch, and a high count means the
headline number is understated.

## Publishing a leaderboard

```bash
nl-eval --provider openai --model gpt-5-mini --out results/gpt-5-mini.json
nl-eval --publish results        # writes docs/results.json
```

`docs/` is served by GitHub Pages. Control runs are kept and labelled rather
than filtered out: a leaderboard that hides its own baselines is asking to be
taken on trust.

## Known limits

- **BLiMP-NL is scored as a forced choice here**, not by comparing the
  log-probability of each sentence as the corpus intends. A forced choice can be
  right for the wrong reason. Where a provider exposes log-probs, prefer that and
  state which mode a published score used.
- **The human acceptability ratings are not yet used.** They are the most
  valuable part of BLiMP-NL, because they allow scoring model–human correlation
  rather than bare accuracy. That is the next thing worth building.
- **Multiple choice is recognition, not production.** A model can pick
  `pannenkoek` from two options and still misspell it when writing freely.
- **L3 is written by one author** and has not been reviewed by a second native
  speaker. Answers follow the official spelling (*Woordenlijst Nederlandse
  Taal*) and standard Netherlands Dutch, except in `variants`. A native review
  is advisable before publishing L3 results.
- **L2 inherits Global-MMLU's translation quality**, including any errors in it.

## Tests

```bash
python tests/test_scoring.py
```

These cover answer extraction, where an eval most easily goes wrong in silence.
One case is not hypothetical: an early version scored the reply
"alpha, beta, gamma, delta" as a confident "A", because the last word ends in
that letter. A model listing every option would have been credited with choosing
one.

## Licence

MIT for this repository. The external layers keep their own licences; see
[ATTRIBUTION.md](ATTRIBUTION.md).
