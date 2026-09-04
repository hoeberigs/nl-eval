"""Tests for answer extraction and item integrity.

Extraction is the part of an eval most likely to be quietly wrong, because a
too-permissive rule inflates every score and a too-strict one punishes models
that answer correctly in a sentence. Both failure modes are silent.

Run with: python tests/test_scoring.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nleval.items import Item, chance_baseline, load_items, validate
from nleval.score import extract_choice, normalise, score_item, wilson

FAILURES = []


def check(name, got, want):
    if got != want:
        FAILURES.append(f"{name}: expected {want!r}, got {got!r}")


ITEM = Item(id="t1", category="t", type="mcq", prompt="Welk lidwoord?",
            choices=["de", "het"], answer="het")
ITEM4 = Item(id="t2", category="t", type="mcq", prompt="Wat betekent X?",
             choices=["alpha", "beta", "gamma", "delta"], answer="gamma")


def test_extraction():
    # The requested format.
    check("bare letter", extract_choice("B", ITEM), "B")
    check("letter with paren", extract_choice("(B)", ITEM), "B")
    check("letter with dot", extract_choice("B.", ITEM), "B")
    check("lowercase", extract_choice("b", ITEM), "B")
    check("whitespace", extract_choice("  B \n", ITEM), "B")

    # Models that answer in a sentence must still be scored.
    check("lead-in", extract_choice("Antwoord: C", ITEM4), "C")
    check("dutch phrase", extract_choice("Het juiste antwoord is C.", ITEM4), "C")
    check("option text", extract_choice("gamma", ITEM4), "C")
    check("reasoned then concluded", extract_choice("Laten we kijken... dus C", ITEM4), "C")

    # A model that lists every option has not chosen one.
    check("lists all options", extract_choice("alpha, beta, gamma, delta", ITEM4), None)
    # Out-of-range letters are not valid selections.
    check("letter out of range", extract_choice("G", ITEM), None)
    check("empty", extract_choice("", ITEM), None)
    check("refusal", extract_choice("Dat weet ik niet.", ITEM4), None)


def test_scoring():
    r = score_item("B", ITEM)
    check("correct mcq", r["correct"], True)
    r = score_item("A", ITEM)
    check("wrong mcq", r["correct"], False)
    r = score_item("", ITEM)
    check("empty not correct", r["correct"], False)
    check("empty not parsed", r["parsed"], False)

    ex = Item(id="e1", category="t", type="exact", prompt="Meervoud van kind?", answer="kinderen")
    check("exact match", score_item("kinderen", ex)["correct"], True)
    check("exact in sentence", score_item("Het meervoud is kinderen.", ex)["correct"], True)
    check("exact wrong", score_item("kinds", ex)["correct"], False)
    # A substring must not count: "kind" inside "kinderen" is a different word.
    ex2 = Item(id="e2", category="t", type="exact", prompt="?", answer="kind")
    check("no substring credit", score_item("kinderen", ex2)["correct"], False)


def test_normalise():
    check("case and space", normalise("  HET  "), "het")
    check("trailing punct", normalise("het."), "het")
    check("curly quote", normalise("’t"), "'t")


def test_wilson():
    lo, hi = wilson(5, 10)
    check("wilson brackets p", lo < 0.5 < hi, True)
    lo, hi = wilson(0, 20)
    check("wilson lower bound non-negative", lo >= 0.0, True)
    check("wilson upper bound below one", hi < 1.0, True)


def test_itemset():
    items = load_items(Path(__file__).resolve().parents[1] / "items")
    check("item set loads", len(items) > 150, True)
    problems = validate(items)
    if problems:
        FAILURES.append(f"item set has {len(problems)} problems: {problems[:3]}")
    c = chance_baseline(items)
    check("chance baseline in range", 0.2 < c < 0.55, True)


if __name__ == "__main__":
    for fn in [test_extraction, test_scoring, test_normalise, test_wilson, test_itemset]:
        fn()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)})")
        for f in FAILURES:
            print("  " + f)
        raise SystemExit(1)
    print("all tests passed")
