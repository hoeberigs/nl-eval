# nl-eval

A Dutch-language evaluation suite for language models. **189 items across 10 categories**, every
one objectively scorable.

Most multilingual evaluations test Dutch by translating English items, which measures translation
quality rather than Dutch. This suite tests the things that are hard *because* they are Dutch:
`de`/`het` assignment, the tussen-n, diminutive formation, separable verbs and subclause word
order, idioms, English false friends, and the `u`/`je` register distinction that governs every
piece of Dutch business correspondence.

## No judge, by design

Every item is multiple choice or exact string match. Nothing here needs an LLM judge, which means:

- **It costs cents, not euros.** A full run is roughly 30k input tokens.
- **It is deterministic.** Re-running gives the same score, so a change in the number is a change
  in the model.
- **It has no judge bias.** An LLM-judged Dutch suite inherits the judge's own Dutch weaknesses,
  which is precisely what is under test.

## Controls come with the suite

An evaluation that cannot be gamed by accident needs its own controls, so two are built in and
cost nothing to run:

```bash
nl-eval --provider echo       # answers nothing at all
nl-eval --provider always-a   # always answers "A"
```

| Control | Accuracy | Chance baseline | Reading |
|---|---|---|---|
| `echo` | 0.000 | 0.339 | The scorer awards no free marks; 189/189 replies logged unparseable |
| `always-a` | 0.355 | 0.339 | +1.6pp over chance, so the answer key is position-balanced |

If `always-a` ever scores well above chance, the answer key has drifted onto one letter and the
suite is measuring formatting habits. `--validate` checks for this automatically.

The chance baseline is **0.339**, not 0.25: `de_het` and `spelling` are two-option items. It is
published next to every score, because an accuracy figure means nothing until you know what zero
knowledge looks like.

## Categories

| Category | Items | What it probes |
|---|---:|---|
| `de_het` | 40 | Article assignment, including the `-heid`/`-ing`/`ge-` regularities |
| `spelling` | 27 | Tussen-n, `d`/`t`/`dt`, 't kofschip, past participles of loanwords |
| `civics` | 24 | Provinces and their capitals, institutions, national dates |
| `idioms` | 22 | Figurative meaning, with literal readings as distractors |
| `diminutives` | 18 | `-je`/`-tje`/`-pje`/`-kje`/`-etje` and vowel doubling |
| `false_friends` | 18 | `eventueel`, `actueel`, `brutaal`, `miljard` vs `biljoen` |
| `word_order` | 12 | V2, verb-final subclauses, separable verbs, `om ... te` |
| `register` | 10 | `u`/`uw` vs `je`/`jouw` consistency within a sentence |
| `formatting` | 10 | Decimal comma, thousands point, dates, postcodes, currency |
| `variants` | 8 | Belgian versus Netherlands Dutch |

## Usage

```bash
git clone https://github.com/hoeberigs/nl-eval.git
cd nl-eval
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Check the item set and see the chance baseline, no API calls:

```bash
nl-eval --validate
```

Estimate what a run would cost before running it:

```bash
nl-eval --estimate --model gpt-5-mini
```

Run against a model:

```bash
export OPENAI_API_KEY=...
nl-eval --provider openai --model gpt-5-mini --max-spend 0.50
```

```bash
export ANTHROPIC_API_KEY=...
nl-eval --provider anthropic --model claude-haiku-4-5-20251001 --max-spend 0.50
```

### The spend ceiling is enforced, not advisory

`--max-spend` is a euro ceiling checked **before the first API call**. The run refuses to start if
the estimate exceeds it and tells you what to cut. The default is €1.00, and the price table
deliberately over-estimates, because the purpose is to prevent an accidental spend and being
cautious is the correct direction to be wrong in.

Narrow a run rather than raising the ceiling:

```bash
nl-eval --provider openai --model gpt-5 --category de_het,spelling --limit 40
```

## Interpreting a result

Report the accuracy **with its interval and against the baseline**. Per-category samples run from
8 to 40 items, so a category score carries a wide Wilson interval and small differences between
two models on one category are usually noise. The suite emits these automatically:

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

Watch `unparsed_replies`. A model that ignores the output format is being scored on instruction
following as much as on Dutch, and a high count means the headline number is understated.

## Adding items

Items are JSONL, one object per line, in `items/`:

```json
{"id": "de_het-041", "category": "de_het", "type": "mcq",
 "prompt": "Welk lidwoord hoort bij \"vergunning\"?",
 "choices": ["de", "het"], "answer": "de",
 "note": "Woorden op -ing zijn de-woorden."}
```

Then run `nl-eval --validate`, which checks that gold answers appear among their own options, that
no item is duplicated, and that answer positions stay balanced.

`tools_build_items.py` regenerates the files from source lists and assigns answer positions
round-robin, which is how the balance is maintained as items are added.

## Tests

```bash
python tests/test_scoring.py
```

These cover answer extraction, which is where an eval most easily goes wrong in silence. One case
in there is not hypothetical: an early version scored the reply "alpha, beta, gamma, delta" as a
confident "A", because the last word ends in that letter. A model listing every option would have
been given credit for choosing one.

## Limits

- **Multiple choice is recognition, not production.** A model can pick `pannenkoek` from two
  options and still misspell it when writing freely.
- **Coverage is uneven by design.** Categories are sized by how many items could be written with
  confident gold answers, not to equal weight.
- **Prescriptive norms.** Answers follow the official spelling (`Woordenlijst Nederlandse Taal`)
  and standard Netherlands Dutch, except in `variants`.
- **No open generation, translation or long-form coherence.** Those need a judge, which this suite
  deliberately avoids.

## Licence

MIT. See [LICENSE](LICENSE).
