# Attribution

nl-eval combines three layers. Only one of them is mine. The other two are
published corpora that this repository **fetches at run time and never
redistributes**: their rows are downloaded on first use into a gitignored cache
under `.cache/sources/`, so the licence stays with the publisher and this
repository ships only the adapter.

Attribution below is required by those licences, not offered as courtesy.

---

## L1 — BLiMP-NL (native Dutch grammar)

**9,000 minimal pairs · 22 linguistic phenomena · 84 paradigms**

A corpus of Dutch minimal pairs and acceptability judgments, built in Dutch by
Dutch linguists rather than translated. Each item is a grammatical sentence
paired with a minimally different ungrammatical one. Nine of the ten
hand-written sentences per paradigm carry human acceptability ratings from at
least 30 participants each, plus self-paced reading times.

- Authors: Michelle Suijkerbuijk, Zoë Prins, Marianne de Heer Kloots,
  Willem Zuidema, Stefan L. Frank
- Published in *Computational Linguistics* (MIT Press)
- Dataset: https://huggingface.co/datasets/juletxara/blimp-nl
- Paper: https://direct.mit.edu/coli/article/51/4/1267/128735/
- **Licence: CC-BY-4.0**

Used here as forced-choice items ("which of these two sentences is grammatical
Dutch?"). That is deliberately weaker than the corpus's intended use, which
compares the log-probability the model assigns to each sentence. A forced
choice can be right for the wrong reason, so any published score states which
scoring mode produced it.

The human ratings are the part worth building on: they allow scoring
model–human *correlation* rather than bare accuracy, which is a stronger claim
than a leaderboard position.

## L2 — Global-MMLU, Dutch subset (translated breadth)

**~14.3k questions · 42 languages**

Multitask knowledge and reasoning, translated and quality-controlled across
languages. Included for breadth and for cross-language comparability, and kept
strictly separate from the native layers.

- Authors: Cohere Labs and contributors
- Dataset: https://huggingface.co/datasets/CohereLabs/Global-MMLU
- **Licence: Apache-2.0**

Read this layer for what it is. Translated items largely measure how a model
handles translated English: the questions keep their source-language shape, and
culture-bound knowledge does not survive the trip. A model can do well here
while handling actual Dutch badly, which is precisely why L1 and L3 exist.

## L3 — nl-eval core (applied Dutch)

**189 hand-written items · 10 categories**

`de`/`het` assignment, tussen-n and d/t/dt spelling, diminutive formation,
separable verbs and subclause word order, idioms, English false friends, u/je
register, Dutch number and date notation, NL civics, and Belgian versus
Netherlands Dutch.

- Author: Linda Hoeberigs
- **Licence: MIT** (this repository)

This layer exists because translation cannot produce it. There is no English
item that becomes "welk lidwoord hoort bij *beleid*", and no English source for
the tussen-n or for the u/je distinction that governs Dutch business
correspondence.

**Caveat worth stating:** these items are written by one author and have not
been reviewed by a second native speaker. Answers follow the official spelling
(*Woordenlijst Nederlandse Taal*) and standard Netherlands Dutch, except in the
`variants` category. A native review is advisable before publishing results
from this layer.

---

## Why the layers are never blended into one number

A single headline mixing native grammar with translated knowledge cannot be
read as either. The runner therefore scores per category and reports the layers
separately, and the chance baseline is published next to every score because it
differs per layer: L1 is two-option (0.50), L2 is four-option (0.25), and L3 is
mixed (0.339).

## Citing

If you use the combined suite, cite the underlying corpora, not just this
repository:

```bibtex
@article{blimpnl,
  title   = {{BLiMP-NL}: A Corpus of {D}utch Minimal Pairs and Acceptability
             Judgments for Language Model Evaluation},
  author  = {Suijkerbuijk, Michelle and Prins, Zo\"e and
             de Heer Kloots, Marianne and Zuidema, Willem and Frank, Stefan L.},
  journal = {Computational Linguistics},
  year    = {2025}
}

@misc{globalmmlu,
  title  = {Global-{MMLU}},
  author = {{Cohere Labs}},
  year   = {2024},
  howpublished = {\url{https://huggingface.co/datasets/CohereLabs/Global-MMLU}}
}
```
