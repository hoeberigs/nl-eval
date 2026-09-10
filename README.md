# nl-eval: Nederlands onder druk

How stable is a language model's Dutch? Every item is asked in its original
form and in six meaning-preserving variants; a model gets the item only when
it answers all seven correctly. That share, **worst-case accuracy**, is the
headline. Plain accuracy stays on the board as the ceiling a model reaches
when nothing is disturbed. No judge model anywhere, a held-out split that was
never committed, and controls on the board as the floor.

Live board: <https://hoeberigs.github.io/nl-eval/>

## Why worst case

On a fixed item set the best models sit within a few points of each other and
all of them clear any sensible line. Accuracy is a solved axis. What is not
solved is whether an answer survives a change that leaves the correct answer
untouched. Under any single variant the per-variant accuracy barely moves; the
worst case over all variants moves a lot, because the instability is spread
across items rather than concentrated in one perturbation. Only a per-item
aggregation exposes it, and it leaves headroom that can be tightened by adding
variants without touching an item.

## The battery

| Form | What changes | What stays |
|---|---|---|
| onverstoord | nothing | everything |
| opties omgekeerd | the options in reverse order | item and correct answer |
| opties geschud | a fixed other order of the options | idem |
| informele instructie | the answer instruction in informal Dutch | the item |
| Engelse instructie | the answer instruction in English | the item, in Dutch |
| afleidende zin | one irrelevant Dutch sentence before the item | the item |
| typefouten | two typos in the carrier question | the sentence or word under test |

A drop from original to worst case under 5 points is **stabiel**, under 15
**wankel**, above that **onstabiel**. There is no pass line and no verdict.

## The items

| Onderdeel | What it tests | Items | Scoring |
|---|---|---:|---|
| Taalvorm | word order, Belgian versus Dutch variants, notation conventions, plus the 440 BLiMP-NL minimal pairs | 570 | MCQ; minimal pairs by likelihood where the provider can score, MCQ otherwise |
| Spelling en grammatica | de/het, diminutives, tussen-n and compounds, verb spelling (d/t/dt), the Taaladvies doubt cases | 273 | MCQ |
| Schrijven | rewrite a sentence with exactly one error | 69 | exact match; alternative corrections accepted where more than one is right |
| Lezen | practical passages with a question on a condition, exception, date or action; some answers are "dat staat er niet" | 60 | MCQ |
| Woordenschat | idioms, false friends with English and German | 92 | MCQ |
| Algemene kennis | Global-MMLU, Dutch split; an indicator, outside the worst case | 299 | MCQ |

1,363 items, 624 written for this repository. The battery runs on a
stratified sample of the multiple-choice items (150 or 300 per model, noted
per row); the undisturbed score is computed on the full set. Text only:
speech is out of scope.

## Results, 10 September 2026

| Model | Worst case | Original (sample) | Drop | Band | Full set | Held-out |
|---|---:|---:|---:|---|---:|---:|
| claude-sonnet-5 | **90.0%** (n=150) | 98.0% | 8.0 | wankel | 93.3% | 97.4% (geen teken van besmetting) |
| gpt-5 | **87.3%** (n=150) | 92.0% | 4.7 | stabiel | 90.9% | 92.2% (geen teken van besmetting) |
| claude-haiku-4-5 | **78.7%** (n=300) | 90.3% | 11.7 | wankel | 89.4% | 90.8% (geen teken van besmetting) |
| gpt-5-mini | **75.7%** (n=300) | 90.3% | 14.7 | wankel | 88.3% | 90.2% (geen teken van besmetting) |
| gpt-5-nano | **63.3%** (n=300) | 83.0% | 19.7 | onstabiel | 80.2% | 77.8% (geen teken van besmetting) |
| qwen2.5:7b (local) | **52.0%** (n=300) | 75.7% | 23.7 | onstabiel | 74.6% | 71.2% (geen teken van besmetting) |
| gemma3:4b (local) | **39.7%** (n=300) | 69.0% | 29.3 | onstabiel | 67.3% | 70.6% (geen teken van besmetting) |
| llama3.2:3b (local) | **29.0%** (n=300) | 59.0% | 30.0 | onstabiel | 53.9% | 64.7% (geen teken van besmetting) |
| phi4-mini (local) | **23.7%** (n=300) | 53.3% | 29.7 | onstabiel | 52.3% | 66.7% (geen teken van besmetting) |
| GEITje-7B-ultra (local) | **22.0%** (n=300) | 61.0% | 39.0 | onstabiel | 53.9% | 56.9% (geen teken van besmetting) |
| GroNLP/gpt2-small-dutch | | | | BLiMP-NL only, by likelihood | 87.3% | |
| gemini-3.6-flash | did not run | | | provider quota error | | |
| always-a (control) | not tested | | | | 35.2% | not run |
| echo (control) | not tested | | | | 0.0% | not run |

Readings from the board:

- **Worst case separates what accuracy blurs.** The four hosted models span
  nine points of accuracy and fifteen points of worst case.
- **The most stable model is not the highest-scoring one.** gpt-5 loses 4.7
  points between original and worst case; claude-sonnet-5 scores higher and
  loses 8.0, most of it on reading passages with one irrelevant sentence in
  front of them.
- **The mid-tier collapses on the Dutch-specific sections.** Haiku and
  gpt-5-mini look like gpt-5 on accuracy and sit twelve points behind it on
  worst case; their losses concentrate on de/het and the Taaladvies cases.
- **Every local model is onstabiel.** qwen2.5 loses 24 points between
  original and worst case, gemma3 29, llama3.2 30, phi4-mini 30, GEITje 39:
  a Dutch fine-tune of Mistral 7B that scores 61% undisturbed keeps 22% of
  its items under pressure.
- **No sign of contamination** on any hosted model against the held-out set,
  and no model reproduces the canary.

## What this adds to what existed

Dutch is not an unserved language. [EuroEval](https://euroeval.com) runs a
Dutch track, [BLiMP-NL](https://doi.org/10.34973/tj4p-y007) provides 8,400
minimal pairs with human ratings, and Global-MMLU carries a Dutch translation
of MMLU. This suite uses the last two as layers and does not pretend they are
absent. What it adds:

- **Worst case over a variant battery as the headline**, with the per-variant
  and per-section drops as the diagnosis.
- **Sections no translated benchmark has.** Werkwoordspelling, the Taaladvies
  doubt cases, Belgian versus Dutch variants, Dutch notation.
- **No judge model, including for writing.** Error correction has one right
  answer, or a short list of them.
- **Contamination is testable.** `heldout/` was gitignored from the first
  commit; `--holdout-status` refuses to call it clean if git ever tracked it;
  `docs/heldout-manifest.json` commits to ids and salted answer hashes. See
  [CANARY.md](CANARY.md).
- **Where, not only how much.** The items most models miss, and the BLiMP-NL
  pairs broken down by linguistic phenomenon.

## Item quality

Items were written by hand and audited with a disagreement queue: every item
where two or more strong models agree on the same wrong answer was re-checked
by a person. Of roughly 620 hand-written items, three are missed by both
frontier models and all three keys hold. The queue is a review aid, never a
judge.

## Running it

```bash
pip install -e .
nl-eval --validate
nl-eval --suite all --provider anthropic --model claude-sonnet-5 --max-spend 2.50 --out results/anthropic__claude-sonnet-5.json
nl-eval --robustness --suite core --limit 300 --provider anthropic --model claude-sonnet-5 --out results/robustness__claude-sonnet-5.json
nl-eval --suite holdout --provider anthropic --model claude-sonnet-5 --out results/heldout__claude-sonnet-5.json
nl-eval --canary --provider anthropic --model claude-sonnet-5 --out results/canary__claude-sonnet-5.json
nl-eval --compare results/a.json results/b.json
nl-eval --publish results
```

Providers: `ollama` (any Ollama model, including Hugging Face GGUF builds),
`hf` (local likelihood scoring), `anthropic`, `openai`, `google`, plus the
controls. Keys come from `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY`. Runs resume by item id from the finished report; every
report records its estimated cost; `--max-spend` refuses a run whose estimate
exceeds it. The battery costs seven times its sample: about €2 for a frontier
model on 300 items.

## Statistics

`--compare` reports McNemar with an exact binomial fallback, a paired
bootstrap interval on the difference, and the minimum detectable difference
for the item count. Human alignment against the BLiMP-NL ratings is a
Spearman correlation over paradigms (`--human-ratings`); the ratings file is
distributed behind a publisher account and is not computed on the board.

## Known limits

- The battery is a sample; the sample size is on every row.
- The six variants are a choice; more can be added, and each addition makes
  the worst case stricter.
- Global-MMLU is an indicator; MMLU is among the most contaminated benchmarks.
- Gemini has not been run: the key available returned quota errors on every
  current model id.

## Tests

```bash
python -m pytest
```

## Licence and attribution

Code and hand-written items: MIT. BLiMP-NL: CC-BY-4.0 (human ratings CC BY-SA
4.0), Suijkerbuijk et al., Computational Linguistics 2025. Global-MMLU: Apache
2.0, Cohere Labs; Dutch split only. See [ATTRIBUTION.md](ATTRIBUTION.md).
