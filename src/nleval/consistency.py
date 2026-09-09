"""Consistency: does the answer survive a change that should not matter?

Accuracy measures whether a model lands on the right option. It says nothing
about whether it would land there again if the question were asked slightly
differently. Two perturbations here are chosen because neither changes what
the correct answer is, so any change in the model's choice is the model's
instability and nothing else.

**Option order reversed.** The same item with its choices listed back to front.
A model that tracks content picks the same sentence; a model with a position
habit picks the same letter. This is the cleanest robustness probe there is,
and it is the direct complement of the always-a control.

**Register of the instruction swapped.** The one line telling the model how
to answer is re-phrased from the informal to the formal register (or back).
The task is identical; only the politeness changes. A model whose answers
shift with how politely it is asked is measuring the asker, not the Dutch.

Both are reported as flip rates over the items where the original run had a
parseable answer. A flip is counted whenever the chosen *content* differs,
which for reversed options means the letter must change for the answer to be
consistent.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

from .items import LETTERS, Item
from .score import extract_choice

FORMAL_TAIL = "Antwoord uitsluitend met de letter van het juiste antwoord."
INFORMAL_TAIL = "Geef alleen de letter van het goede antwoord, verder niks."


def _render_with_tail(item: Item, tail: str) -> str:
    base = item.render()
    return base.replace(FORMAL_TAIL, tail) if FORMAL_TAIL in base else base


def perturb_reverse(item: Item) -> Item:
    return replace(item, choices=list(reversed(item.choices)))


def _chosen_content(reply: str, item: Item) -> str | None:
    letter = extract_choice(reply, item)
    if letter is None:
        return None
    return item.choices[LETTERS.index(letter)]


def consistency(
    items: list[Item],
    call: Callable[[str], str],
    limit: int | None = None,
) -> dict:
    """Run each MCQ item under both perturbations and count content flips."""
    mcq = [i for i in items if i.type == "mcq" and len(i.choices) >= 2]
    if limit and len(mcq) > limit:
        # Stratified, not head-of-list: the first N items by file order are
        # one or two categories, and a flip rate measured on those says
        # nothing about the exam. Round-robin over categories in a fixed
        # order gives every section a share.
        by_cat: dict[str, list] = {}
        for it in mcq:
            by_cat.setdefault(it.category, []).append(it)
        picked, i = [], 0
        cats = sorted(by_cat)
        while len(picked) < limit and any(by_cat.values()):
            c = cats[i % len(cats)]
            if by_cat[c]:
                picked.append(by_cat[c].pop(0))
            i += 1
        mcq = picked

    rev_flips = reg_flips = 0
    rev_n = reg_n = 0
    details = []

    for it in mcq:
        try:
            base_reply = call(it.render())
        except Exception:
            continue
        base = _chosen_content(base_reply, it)
        if base is None:
            continue

        # 1. reversed option order: same content must be chosen
        rev = perturb_reverse(it)
        try:
            r = _chosen_content(call(rev.render()), rev)
        except Exception:
            r = None
        if r is not None:
            rev_n += 1
            if r != base:
                rev_flips += 1

        # 2. informal instruction: same content must be chosen
        try:
            g = _chosen_content(call(_render_with_tail(it, INFORMAL_TAIL)), it)
        except Exception:
            g = None
        if g is not None:
            reg_n += 1
            if g != base:
                reg_flips += 1

        details.append({"id": it.id, "base": base[:60],
                        "reversed": (r or "")[:60], "informal": (g or "")[:60]})

    return {
        "items_probed": len(mcq),
        "order_reversed": {
            "n": rev_n,
            "flips": rev_flips,
            "flip_rate": round(rev_flips / rev_n, 4) if rev_n else None,
            "reading": "share of answers that changed content when the options were listed back to front",
        },
        "register_swapped": {
            "n": reg_n,
            "flips": reg_flips,
            "flip_rate": round(reg_flips / reg_n, 4) if reg_n else None,
            "reading": "share of answers that changed when the instruction was phrased informally",
        },
        "detail": details,
    }
