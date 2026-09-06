# nl-eval: het inburgeringsexamen voor taalmodellen

A Dutch benchmark for language models, structured the way the Netherlands
tests people who move here: an exam with sections, a pass line per section,
and a verdict. No judge model anywhere. Every item is scored deterministically,
a held-out split makes contamination testable, and consistency probes report
how much of a score is positional habit rather than Dutch.

Live board: <https://hoeberigs.github.io/nl-eval/>

## The exam

| Onderdeel | What it tests | Items | Scoring |
|---|---|---:|---|
| Taalvorm | de/het, diminutives, spelling (tussen-n, compounds), word order, Belgian/Dutch variants, formatting conventions, plus the BLiMP-NL minimal pairs | 665 | MCQ; minimal pairs by likelihood where the provider can score, MCQ otherwise |
| Schrijven | rewrite a flawed sentence correctly | 35 | exact match against the corrected sentence |
| Lezen | short passages (letters, leaflets, notices) with a comprehension question | 15 | MCQ |
| Woordenschat | idioms, false friends with English and German | 58 | MCQ |
| KNM | kennis van de Nederlandse maatschappij: institutions, customs, geography | 54 | MCQ |
| ONA en register | orientation on the labour market; formal vs informal register | 26 | MCQ |
| Algemene kennis | Global-MMLU, Dutch split; an indicator, never a verdict | 299 | MCQ |

Spreken and Luisteren are out of scope: this is a text exam.

### The verdict rule

Each verdict-bearing section gets a Wilson 95% interval. It **passes** when the
lower bound clears the pass line, **fails** when the upper bound stays below
it, and is **undecided** otherwise. A small section cannot pass on a lucky
draw, and that is deliberate. The pass line is 0.80, an analogy to
"voldoende" chosen here; it is not a DUO threshold and the page says so.

A model passes the exam when it passes every verdict-bearing section, fails as
soon as it fails one, and is undecided otherwise. A run whose replies are
mostly provider errors is shown as "rijdt niet" with its reason, never as a
zero.

The rule lives in one place, `src/nleval/publish.py`; the page renders
verdicts and never computes them.

## Results, September 2026

| Model | Score (n=1132) | Verdict | Order-flip | Register-flip | Held-out |
|---|---:|---|---:|---:|---:|
| claude-haiku-4-5 | 89.7% [87.9, 91.4] | undecided (Lezen, KNM) | 20.8% | 1.7% | 94.5% |
| gpt-5-mini | 87.9% [85.9, 89.7] | undecided (Lezen) | 21.7% | 10.8% | 93.1% |
| qwen2.5:7b (local) | 74.2% [71.6, 76.7] | failed (KNM 63.0%) | 30.8% | 1.7% | — |
| GroNLP/gpt2-small-dutch | 87.3% on BLiMP-NL only, by likelihood | incomplete | — | — | — |
| always-a (control) | 35.4% | failed | | | |
| echo (control) | 0.0% | failed | | | |

Read the flips with the scores: the two hosted models answer about nine in ten
items correctly and change one answer in five when the options are merely
listed in reverse order. gpt-5-mini also shifts one in ten answers when the
instruction is phrased informally; haiku barely moves. Neither shows a
public-versus-held-out gap beyond the noise floor, and neither reproduces the
canary.

Full per-section numbers, intervals and the perron view are on the page and in
`docs/results.json`.

## What this adds to what existed

Dutch is not an unserved language. [EuroEval](https://euroeval.com) runs a
Dutch track, [BLiMP-NL](https://doi.org/10.34973/tj4p-y007) provides 8,400
minimal pairs with human ratings, and Global-MMLU carries a Dutch translation
of MMLU. This suite uses the last two as layers and does not pretend they are
absent. What it adds:

- **Exam structure instead of one number.** A verdict per section with an
  interval and a published pass line.
- **No judge model, including for writing.** Error correction has one right
  answer, so Schrijven is exact-match.
- **Contamination is testable.** `heldout/` was gitignored from the first
  commit; `--holdout-status` refuses to call it clean if git ever tracked it;
  `docs/heldout-manifest.json` commits to ids and salted answer hashes. See
  [CANARY.md](CANARY.md).
- **Consistency is measured.** Options reversed and register swapped, both
  leaving the correct answer unchanged; reported as flip rates.
- **KNM and ONA.** Society and labour-market knowledge that no translated
  benchmark contains.

## Controls ship with the suite

`always-a` picks the first option and checks position balance. `echo` repeats
the prompt and checks that extraction never invents an answer. Both must fail.
They stay on the board as the floor.

## Running it

```bash
pip install -e .
nl-eval --validate                                   # item files, position balance, chance baseline
nl-eval --suite all --provider ollama --model qwen2.5:7b --out results/ollama__qwen2.5-7b.json
nl-eval --suite all --provider anthropic --model claude-haiku-4-5-20251001 --max-spend 0.50 --out results/anthropic__claude-haiku-4-5.json
nl-eval --consistency --suite core --limit 120 --provider anthropic --model claude-haiku-4-5-20251001 --out results/consistency__claude-haiku-4-5.json
nl-eval --suite holdout --provider anthropic --model claude-haiku-4-5-20251001 --out results/heldout__claude-haiku-4-5.json
nl-eval --contamination-check results/anthropic__claude-haiku-4-5.json results/heldout__claude-haiku-4-5.json
nl-eval --canary --provider anthropic --model claude-haiku-4-5-20251001
nl-eval --compare results/a.json results/b.json     # McNemar, paired bootstrap, minimum detectable difference
nl-eval --publish results                            # writes docs/results.json
```

Providers: `ollama`, `hf` (local likelihood scoring), `anthropic`, `openai`,
`google`, plus the controls. Keys come from `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `GEMINI_API_KEY`. Runs use a small thread pool and an
append-only checkpoint, so a killed run resumes by item id and a grown item set
only pays for the new items.

### The spend ceiling is enforced

`--max-spend` refuses to start a run whose estimate exceeds it. Local providers
are priced at zero. A full hosted run on all items typically costs under one
euro on a small model.

## Statistics

`--compare` reports McNemar with an exact binomial fallback, a paired
bootstrap interval on the difference, and the minimum detectable difference
for the item count, so two scores closer than the suite can resolve are not
reported as a ranking. Human alignment against the BLiMP-NL ratings is a
Spearman correlation over paradigms (`--human-ratings`).

## Known limits

- Lezen has 15 items; even a perfect model cannot pass at the 0.80 line. It
  shows as undecided. More reading items are the next addition.
- The held-out split has 73 items, so its noise floor is about 14 points; it
  catches gross memorisation only.
- Global-MMLU is an indicator; MMLU is among the most contaminated benchmarks.
- Gemini has not been run: the key available returned quota errors on every
  current model id.
- The pass line is a documented choice, not a norm.

## Tests

```bash
python -m pytest
```

## Licence and attribution

Code and hand-written items: MIT. BLiMP-NL: CC-BY-4.0 (human ratings CC BY-SA
4.0), Suijkerbuijk et al., Computational Linguistics 2025. Global-MMLU: Apache
2.0, Cohere Labs; Dutch split only. See [ATTRIBUTION.md](ATTRIBUTION.md).
