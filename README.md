# nl-eval

A Dutch-language evaluation suite for language models, in three layers: **native
Dutch grammar**, **translated breadth**, and **applied Dutch** that no existing
benchmark covers.

```bash
nl-eval --suite all          # all three layers, scored separately
nl-eval --suite core         # the 307 hand-written items, no network needed
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

## Where this sits (prior art)

**Dutch is not an unserved language, and this is not the first Dutch benchmark.**
Anyone evaluating a model on Dutch should start with the work below, not here.

| Project | Covers | Note |
|---|---|---|
| [EuroEval](https://euroeval.com) (formerly ScandEval) | Sentiment, NER, linguistic acceptability (ScaLA-nl), reading comprehension, knowledge | The main live Dutch leaderboard. Maintained, reports confidence intervals, runnable as a library. **Start here.** |
| [Open Dutch LLM Leaderboard](https://huggingface.co/spaces/BramVanroy/open_dutch_llm_leaderboard) | Translated ARC, HellaSwag, MMLU, TruthfulQA | Discontinued in favour of EuroEval; still online |
| [DUMB](https://arxiv.org/abs/2305.13026) (GroNLP) | 9 Dutch NLU tasks | Encoder-oriented |
| [BLiMP-NL](https://direct.mit.edu/coli/article/51/4/1267/128735/) | 9,000 native minimal pairs, 22 phenomena, human acceptability | Used here as L1 |
| [Fietje](https://arxiv.org/abs/2412.15450) | A Dutch LLM plus its evaluation framework | |

So what is this for? Three narrow things the above leave open:

1. **Most Dutch leaderboard tasks are machine-translated** (SQuAD-nl, ARC-nl,
   MMLU-nl). Native-built Dutch evaluation is the minority, so this suite
   labels every layer by provenance and refuses to blend them.
2. **Orthography, register and notation are untested anywhere I could find.**
   `de`/`het`, the tussen-n, d/t/dt, u/je register, Dutch number and date
   conventions. BLiMP-NL covers syntax, not spelling or politeness register.
3. **BLiMP-NL's human ratings are underused.** Scoring model–human correlation
   is a stronger claim than accuracy, and almost nothing does it. This suite
   implements it: see "Does the model find the same things hard that people do".
4. **Close models are usually reported as ranked when they are not
   distinguishable.** Every run here publishes the smallest gap it could detect,
   and `--compare` settles two runs with a paired test rather than an ordering.

Treat this as a supplement to EuroEval, not a replacement for it.

## The three layers

| Layer | Source | What it measures | Licence |
|---|---|---|---|
| **L1 grammar** | [BLiMP-NL](https://huggingface.co/datasets/juletxara/blimp-nl) — 9,000 minimal pairs, 22 phenomena, 84 paradigms, human acceptability from 30+ raters | Native Dutch syntax | CC-BY-4.0 |
| **L2 breadth** | Global-MMLU (nl), ~14.3k | Knowledge and reasoning, comparable across languages | Apache-2.0 |
| **L3 applied** | 307 hand-written items, 10 categories | Orthography, register, notation, civics, false friends, BE/NL | MIT |

L1 and L2 are **fetched at run time and never redistributed**. They download on
first use into a gitignored cache under `.cache/sources/`, so their licences
stay with their publishers and this repository ships only the adapter. Full
citations in [ATTRIBUTION.md](ATTRIBUTION.md).

`--suite core` needs no network at all.

### The layers are never blended into one number

A single headline mixing native grammar with translated knowledge cannot be read
as either. The runner scores per category, and the chance baseline is published
next to every score because it differs by layer: L1 is two-option (0.50), L2 is
four-option (0.25), L3 is mixed (0.352).

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
| `echo` | 0.000 | 0.352 | The scorer awards no free marks; every reply logged unparseable |
| `always-a` | 0.358 | 0.352 | +0.6pp over chance, so the answer key is position-balanced |

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

## Scoring minimal pairs properly

BLiMP-NL is designed to be scored by comparing the **log-likelihood** a model
assigns to the grammatical and the ungrammatical sentence, not by asking it to
pick one. A forced choice can be right for the wrong reason, and it measures
instruction-following as much as grammar.

Chat APIs will not return the likelihood of text they did not generate, so this
needs local weights:

```bash
pip install 'nl-eval[local]'
nl-eval --suite blimp --provider hf --model GroNLP/gpt2-small-dutch
```

The runner uses likelihood automatically for minimal pairs whenever the
provider can supply it, and falls back to the forced choice otherwise. Each
result records which mode produced it.

### Why this matters, on one model and the same 440 items

| Scoring | Accuracy | Note |
|---|---:|---|
| Log-probability | **87.3%** | 95% CI 83.8–90.1% |
| Forced choice | **0.0%** | 440/440 replies unparseable |

Identical model, identical items. `GroNLP/gpt2-small-dutch` knows Dutch grammar
perfectly well; it simply cannot follow a multiple-choice instruction, because
it is a base model rather than an instruction-tuned one. Scored by forced choice
it looks like it knows nothing, which would have been a completely false
reading. Sum versus mean matters too: the score uses **mean** per-token
log-probability, because a sum would systematically prefer whichever sentence
tokenises shorter and would measure tokenisation rather than grammar.

## Contamination

These items are public, so a model trained after publication may have seen them.
[CANARY.md](CANARY.md) carries a GUID that exists nowhere else:

```bash
nl-eval --canary --provider openai --model gpt-5-mini
```

If a model reproduces it, it trained on this repository and its score is void. A
negative is weak evidence rather than proof. The three layers carry different
risk and should not be read as if they shared one: BLiMP-NL and MMLU predate
most training cutoffs and are very likely in large corpora already, while L3 was
published here first. The honest fix is a held-out split that is never
published, which does not exist yet and is the most valuable next addition.

## Can one model actually beat another

Most leaderboards print two accuracies and order the rows, which invites the
reader to believe a two-point gap is real. On a suite this size it usually is
not.

```bash
nl-eval --compare results/model-a.json results/model-b.json
```

```json
{
  "accuracy_a": 0.7302, "accuracy_b": 0.7460, "difference": -0.0159,
  "ci95": [-0.1058, 0.0741],
  "a_right_b_wrong": 37, "b_right_a_wrong": 40,
  "p_value": 0.81971,
  "verdict": "not distinguishable on this suite",
  "minimum_detectable_difference": 0.132
}
```

Two tests, answering different questions. **McNemar** looks only at the items
where exactly one model was right, because items they both got right or both
got wrong carry no information about which is better; below 25 discordant pairs
it falls back to an exact binomial test rather than trusting a chi-square
approximation on a handful of observations. A **paired bootstrap** resamples
items with the pairing intact and gives an interval for the difference itself.

### How small a gap can this suite even see

Every run reports `min_detectable_difference`: the smallest accuracy gap the
suite could reliably detect at that size.

| Suite | Items | Smallest detectable gap |
|---|---:|---:|
| `--suite core` | 307 | **11.3 pp** |
| `--suite all` (default sampling) | 928 | **6.0 pp** |
| `--suite all --per-phenomenon 90` | ~2,000 | **4.1 pp** |
| full BLiMP-NL | 9,000 | **1.9 pp** |

So the core layer alone cannot rank models that are close. Run `--suite all`
before drawing a conclusion, and treat any ordering inside the detectable gap
as unresolved rather than as a ranking.

## Does the model find the same things hard that people do

Accuracy says how often a model was right. It cannot say whether a model
failing at 85% fails where Dutch speakers hesitate, or on violations every
native speaker catches instantly.

BLiMP-NL makes that answerable: nine of the ten hand-written sentences per
paradigm carry 7-point acceptability ratings from at least 30 native speakers.
Per paradigm, the mean rating of the grammatical sentence minus the
ungrammatical one is how obvious that violation is to people. Correlating it
against the model's per-paradigm accuracy gives a human-alignment score, and it
works on ordinary forced-choice answers with no log-probabilities needed.

```bash
nl-eval --suite blimp --provider openai --model gpt-5-mini \
        --human-ratings data/blimp_nl_ratings.tsv
```

Adds `human_alignment` with a Spearman rho and a per-paradigm breakdown.
Positive means the model finds the same violations easy that people do; near
zero means it is often right for different reasons.

**The ratings are not bundled and are not downloaded automatically.** They live
in the Radboud repository at <https://doi.org/10.34973/tj4p-y007> under
**CC BY-SA 4.0**, which is share-alike and stricter than the CC-BY on the
sentence pairs, and the portal asks for an account. Download them yourself and
save as `data/blimp_nl_ratings.tsv`.

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
- **The human alignment score is paradigm-level, not item-level.** It
  correlates per-paradigm accuracy against per-paradigm human deltas, which is
  what forced-choice answers support. Item-level correlation would need
  log-probabilities per sentence.
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
