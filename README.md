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
| Taalvorm | word order, Belgian versus Dutch variants, notation conventions, plus the 440 BLiMP-NL minimal pairs | 570 | MCQ; minimal pairs by likelihood where the provider can score, MCQ otherwise |
| Spelling en grammatica | de/het, diminutives, tussen-n and compounds, verb spelling (d/t/dt), the Taaladvies doubt cases (hen/hun, als/dan, die/dat, prepositions, inflection) | 273 | MCQ |
| Schrijven | rewrite a sentence with exactly one error | 69 | exact match against the corrected sentence; alternative corrections accepted where more than one is right |
| Lezen | practical passages: letters, leaflets, notices, contracts, rosters, with a question on a condition, exception, date or action; some answers are "dat staat er niet" | 60 | MCQ |
| Woordenschat | idioms, false friends with English and German | 92 | MCQ |
| KNM | kennis van de Nederlandse maatschappij: institutions, customs, geography, rights and duties | 120 | MCQ |
| ONA en register | orientation on the labour market; formal versus informal register | 50 | MCQ |
| Algemene kennis | Global-MMLU, Dutch split; an indicator, never a verdict | 299 | MCQ |

1,533 items in total, 794 of them written for this repository. Spreken and
Luisteren are out of scope: this is a text exam.

### The verdict rule

Each verdict-bearing section gets a Wilson 95% interval. It **passes** when the
lower bound clears the pass line, **fails** when the upper bound stays below
it, and is **undecided** otherwise. A small section cannot pass on a lucky
draw, and that is deliberate. The pass line is 0.80, an analogy to
"voldoende" chosen here; it is not a DUO threshold and the page says so.

A model passes the exam when it passes every verdict-bearing section, fails as
soon as it fails one, and is undecided otherwise. A run whose replies are
mostly provider errors is shown as "rijdt niet" with its reason, never as a
zero. The rule lives in one place, `src/nleval/publish.py`; the page renders
verdicts and never computes them.

## Results, 9 September 2026

| Model | Score (n=1533) | Verdict | Open or failed sections | Order-flip | Register-flip | Held-out |
|---|---:|---|---|---:|---:|---:|
| claude-haiku-4-5 | 89.8% | passed | all sections passed | 18.1% | 3.1% | 91.4% (no sign of contamination) |
| gpt-5-mini | 89.0% | undecided | Spelling en grammatica undecided | 25.0% | 8.8% | 90.8% (no sign of contamination) |
| GroNLP/gpt2-small-dutch | 87.3% on BLiMP-NL only, by likelihood | incomplete | | | | |
| gpt-5-nano | 81.3% | failed | Spelling en grammatica gezakt (74.0%); Lezen undecided; KNM undecided | 46.2% | 8.1% | 79.1% (no sign of contamination) |
| qwen2.5:7b (local) | 74.4% | failed | Spelling en grammatica undecided; Schrijven undecided; Lezen undecided; Woordenschat undecided; KNM gezakt (61.3%); ONA en register undecided | 30.8% | 1.7% | not run |
| gemma3:4b (local) | 68.2% | failed | Taalvorm undecided; Spelling en grammatica gezakt (64.8%); Schrijven undecided; Lezen gezakt (66.7%); Woordenschat undecided; KNM undecided; ONA en register undecided | not run | not run | not run |
| gemini-3.6-flash | did not run | did not run | provider quota error | | | |
| always-a (control) | 34.1% | failed | every section failed | not run | not run | not run |
| echo (control) | 0.0% | failed | every section failed | not run | not run | not run |

Three readings from the board:

- **claude-haiku-4-5 is the first model to pass the whole exam**, every
  verdict-bearing section above the line on its lower bound.
- **Spelling and grammar is the section that separates the models.** Haiku
  passes it; gpt-5-mini is undecided and gpt-5-nano fails it. The d/t items
  and the Taaladvies doubt cases do the work; the two OpenAI models also show
  a first-option habit on two-option items that the reversed-order probe
  measures directly.
- **Reading is decidable now.** With 60 passages both leading models pass
  Lezen; at 15 items no model could.
- **No sign of contamination** on either hosted model: the public and
  held-out scores sit within the noise floor of the 163-item held-out set,
  and neither reproduces the canary.

Full per-section numbers, intervals, perron view and every run's estimated
cost are on the page and in `docs/results.json`.

## What this adds to what existed

Dutch is not an unserved language. [EuroEval](https://euroeval.com) runs a
Dutch track, [BLiMP-NL](https://doi.org/10.34973/tj4p-y007) provides 8,400
minimal pairs with human ratings, and Global-MMLU carries a Dutch translation
of MMLU. This suite uses the last two as layers and does not pretend they are
absent. What it adds:

- **Exam structure instead of one number.** A verdict per section with an
  interval and a published pass line.
- **Sections no translated benchmark has.** Werkwoordspelling, the Taaladvies
  doubt cases, KNM, ONA, Belgian versus Dutch variants, Dutch notation.
- **No judge model, including for writing.** Error correction has one right
  answer, or a short list of them, so Schrijven is exact-match.
- **Contamination is testable.** `heldout/` was gitignored from the first
  commit; `--holdout-status` refuses to call it clean if git ever tracked it;
  `docs/heldout-manifest.json` commits to ids and salted answer hashes. See
  [CANARY.md](CANARY.md).
- **Consistency is measured.** Options reversed and register swapped, both
  leaving the correct answer unchanged; reported as flip rates.

## Item quality

Items were written by hand and audited with a disagreement queue: every item
where two or more strong models agree on the same wrong answer was re-checked
by a person. Most flags were model errors (twelve provinces, a two-month
proeftijd, "wier", "koninkje"); the audit found and fixed five items with a
second defensible answer or an ambiguous prompt. The queue is a review aid,
never a judge: keys are decided by a person.

## Controls ship with the suite

`always-a` picks the first option and checks position balance. `echo` repeats
the prompt and checks that extraction never invents an answer. Both must fail.
They stay on the board as the floor.

## Running it

```bash
pip install -e .
nl-eval --validate
nl-eval --suite all --provider ollama --model qwen2.5:7b --out results/ollama__qwen2.5-7b.json
nl-eval --suite all --provider anthropic --model claude-haiku-4-5-20251001 --max-spend 0.50 --out results/anthropic__claude-haiku-4-5.json
nl-eval --consistency --suite core --limit 120 --provider anthropic --model claude-haiku-4-5-20251001 --out results/consistency__claude-haiku-4-5.json
nl-eval --suite holdout --provider anthropic --model claude-haiku-4-5-20251001 --out results/heldout__claude-haiku-4-5.json
nl-eval --contamination-check results/anthropic__claude-haiku-4-5.json results/heldout__claude-haiku-4-5.json
nl-eval --canary --provider anthropic --model claude-haiku-4-5-20251001 --out results/canary__claude-haiku-4-5.json
nl-eval --compare results/a.json results/b.json
nl-eval --publish results
```

Providers: `ollama`, `hf` (local likelihood scoring), `anthropic`, `openai`,
`google`, plus the controls. Keys come from `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `GEMINI_API_KEY`. Runs use a small thread pool and an
append-only checkpoint; a killed run resumes by item id from the finished
report, so a grown item set only pays for the new items, and every report
records its estimated cost.

### The spend ceiling is enforced

`--max-spend` refuses to start a run whose estimate exceeds it. Local providers
are priced at zero. A full hosted run on all items costs about EUR 0.20 on a
small model.

## Statistics

`--compare` reports McNemar with an exact binomial fallback, a paired
bootstrap interval on the difference, and the minimum detectable difference
for the item count, so two scores closer than the suite can resolve are not
reported as a ranking. Human alignment against the BLiMP-NL ratings is a
Spearman correlation over paradigms (`--human-ratings`).

## Known limits

- Human alignment on the BLiMP-NL paradigms needs the ratings file, which the
  publisher distributes behind an account; it is not computed on the board.
- The held-out split has 163 items; its noise floor is about 9 points, so it
  catches gross memorisation, not subtle leakage.
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
