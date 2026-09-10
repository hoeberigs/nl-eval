"""Worst-case accuracy under meaning-preserving variants.

Accuracy on a fixed item set saturates: the top models sit within a few
points of each other and all of them clear any sensible line. What does not
saturate is whether an answer survives a change that leaves the correct
answer untouched. Each item is asked in its original form and in six
variants; the item counts as known only when every form is answered
correctly. The variants never touch the sentence or word under test, so a
flip is instability, not a different question.
"""

from __future__ import annotations

import random
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from typing import Callable

from .items import LETTERS, Item
from .score import extract_choice

FORMAL_TAIL = "Antwoord uitsluitend met de letter van het juiste antwoord."
INFORMAL_TAIL = "Geef alleen de letter van het goede antwoord, verder niks."
ENGLISH_TAIL = "Answer with the letter of the correct option only."
DISTRACTOR = "Gisteren was het druk op het station en de koffie was op."

VARIANTS = ["origineel", "omgekeerd", "geschud", "informeel", "engels", "afleiding", "typefouten"]


def _tail(base: str, tail: str) -> str:
    return base.replace(FORMAL_TAIL, tail) if FORMAL_TAIL in base else base


def _typos(text: str, rng: random.Random) -> str:
    """Two typos in the carrier question only: the part before the first
    line break or opening quote, so the material under test is untouched."""
    cut = len(text)
    for marker in ("\n", "“", "\"", ":"):
        i = text.find(marker)
        if 0 < i < cut:
            cut = i
    head, rest = text[:cut], text[cut:]
    words = head.split(" ")
    idx = [i for i, w in enumerate(words) if len(w) >= 5 and w.isalpha()]
    rng.shuffle(idx)
    for k, i in enumerate(idx[:2]):
        w = words[i]
        if k == 0:
            j = rng.randrange(1, len(w) - 1)
            w = w[:j] + w[j + 1] + w[j] + w[j + 2:]
        else:
            j = rng.randrange(1, len(w) - 1)
            w = w[:j] + w[j + 1:]
        words[i] = w
    return " ".join(words) + rest


def variants(item: Item, seed: int = 20260910) -> list[tuple[str, Item, str]]:
    """(variant name, item as asked, rendered prompt)."""
    rng = random.Random(f"{seed}:{item.id}")
    out = [("origineel", item, item.render())]
    rev = replace(item, choices=list(reversed(item.choices)))
    out.append(("omgekeerd", rev, rev.render()))
    sh = list(item.choices)
    for _ in range(10):
        rng.shuffle(sh)
        if sh != list(item.choices) and sh != list(reversed(item.choices)):
            break
    shuf = replace(item, choices=sh)
    out.append(("geschud", shuf, shuf.render()))
    out.append(("informeel", item, _tail(item.render(), INFORMAL_TAIL)))
    out.append(("engels", item, _tail(item.render(), ENGLISH_TAIL)))
    out.append(("afleiding", item, DISTRACTOR + "\n\n" + item.render()))
    out.append(("typefouten", item, _typos(item.render(), rng)))
    return out


def _chosen(reply: str, asked: Item) -> str | None:
    letter = extract_choice(reply, asked)
    return None if letter is None else asked.choices[LETTERS.index(letter)]


def stratified(items: list[Item], limit: int | None) -> list[Item]:
    mcq = [i for i in items if i.type == "mcq" and len(i.choices) >= 2]
    if not limit or len(mcq) <= limit:
        return mcq
    by_cat: dict[str, list[Item]] = {}
    for it in mcq:
        by_cat.setdefault(it.category, []).append(it)
    cats, picked, i = sorted(by_cat), [], 0
    while len(picked) < limit and any(by_cat.values()):
        c = cats[i % len(cats)]
        if by_cat[c]:
            picked.append(by_cat[c].pop(0))
        i += 1
    return picked


def robustness(items: list[Item], call: Callable[[str], str], limit: int | None = None,
               workers: int = 6, exclude: tuple[str, ...] = ("civics", "register")) -> dict:
    todo = [i for i in stratified(items, None) if i.category not in exclude]
    todo = stratified(todo, limit)

    def one(it: Item) -> dict:
        row = {"id": it.id, "category": it.category, "answers": {}}
        for name, asked, prompt in variants(it):
            try:
                got = _chosen(call(prompt), asked)
            except Exception as e:  # provider failure is data
                got = None
                row.setdefault("errors", []).append(f"{name}: {str(e)[:80]}")
            row["answers"][name] = {"correct": got == it.answer, "got": got}
        row["worst_case"] = all(v["correct"] for v in row["answers"].values())
        row["n_correct"] = sum(v["correct"] for v in row["answers"].values())
        return row

    with ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(one, todo))

    n = len(rows)
    per_variant = {v: round(sum(r["answers"][v]["correct"] for r in rows) / n, 4) for v in VARIANTS} if n else {}
    worst = round(sum(r["worst_case"] for r in rows) / n, 4) if n else None
    by_cat: dict[str, dict] = {}
    for r in rows:
        c = by_cat.setdefault(r["category"], {"n": 0, "worst": 0, "orig": 0})
        c["n"] += 1; c["worst"] += r["worst_case"]; c["orig"] += r["answers"]["origineel"]["correct"]
    for c in by_cat.values():
        c["worst_case"] = round(c["worst"] / c["n"], 4); c["original"] = round(c["orig"] / c["n"], 4)
        del c["worst"], c["orig"]
    return {
        "items": n, "variants": VARIANTS, "per_variant": per_variant,
        "original": per_variant.get("origineel"), "worst_case": worst,
        "gap": round(per_variant["origineel"] - worst, 4) if n else None,
        "by_category": dict(sorted(by_cat.items())),
        "reading": "worst_case: share of items answered correctly under the original and all six variants",
        "detail": rows,
    }
