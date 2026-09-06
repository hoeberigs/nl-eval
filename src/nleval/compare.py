"""Deciding whether one model actually beats another.

A leaderboard that prints "71.2% / 69.4%" and orders the rows invites the
reader to believe the gap is real. On 189 items a two-point gap is well inside
sampling noise, so the ordering is often reporting a coin flip.

Two tests are used here, and they answer different questions.

**McNemar** asks whether the models disagree asymmetrically. It looks only at
the items where exactly one of them was right, because the items they both got
right or both got wrong carry no information about which is better. This is the
correct test for paired binary outcomes on the same items, and it is the one
most benchmark comparisons should be using and are not.

**A paired bootstrap** gives an interval for the difference itself. Resampling
items (not answers) keeps the pairing intact, so it accounts for the fact that
both models faced exactly the same questions.

Both are reported because a p-value without an effect size is half an answer.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class Comparison:
    model_a: str
    model_b: str
    n_common: int
    acc_a: float
    acc_b: float
    diff: float
    ci95: tuple[float, float]
    b_only: int  # a right, b wrong
    c_only: int  # b right, a wrong
    mcnemar_stat: float
    p_value: float
    verdict: str

    def to_dict(self) -> dict:
        return {
            "model_a": self.model_a,
            "model_b": self.model_b,
            "n_common": self.n_common,
            "accuracy_a": round(self.acc_a, 4),
            "accuracy_b": round(self.acc_b, 4),
            "difference": round(self.diff, 4),
            "ci95": [round(self.ci95[0], 4), round(self.ci95[1], 4)],
            "a_right_b_wrong": self.b_only,
            "b_right_a_wrong": self.c_only,
            "mcnemar": round(self.mcnemar_stat, 3),
            "p_value": round(self.p_value, 5),
            "verdict": self.verdict,
        }


def _norm_sf(z: float) -> float:
    """Two-sided normal tail probability."""
    return math.erfc(abs(z) / math.sqrt(2))


def _binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial test at p=0.5, for small discordant counts.

    The chi-square approximation McNemar normally uses is unreliable when the
    models disagree on only a handful of items, which is exactly the situation
    on a suite this size. Falling back to the exact test there avoids reporting
    a confident p-value derived from four observations.
    """
    if n == 0:
        return 1.0
    total = 2.0 ** n
    tail = 0.0
    for i in range(n + 1):
        if abs(i - n / 2) >= abs(k - n / 2):
            tail += math.comb(n, i)
    return min(1.0, tail / total)


def compare(
    results_a: list[dict],
    results_b: list[dict],
    model_a: str,
    model_b: str,
    iterations: int = 10000,
    seed: int = 42,
) -> Comparison:
    """Compare two runs on the items they both attempted."""
    by_a = {r["id"]: bool(r["correct"]) for r in results_a}
    by_b = {r["id"]: bool(r["correct"]) for r in results_b}
    common = sorted(set(by_a) & set(by_b))
    n = len(common)
    if n == 0:
        return Comparison(model_a, model_b, 0, 0, 0, 0, (0, 0), 0, 0, 0, 1.0,
                          "no items in common")

    a = [by_a[i] for i in common]
    b = [by_b[i] for i in common]
    acc_a = sum(a) / n
    acc_b = sum(b) / n

    # Discordant pairs: the only items that carry information about which model
    # is better. Concordant items cancel and are excluded by construction.
    b_only = sum(1 for x, y in zip(a, b) if x and not y)
    c_only = sum(1 for x, y in zip(a, b) if y and not x)
    disc = b_only + c_only

    if disc == 0:
        stat, p = 0.0, 1.0
    elif disc < 25:
        stat, p = float(min(b_only, c_only)), _binom_two_sided(b_only, disc)
    else:
        # continuity-corrected McNemar
        stat = (abs(b_only - c_only) - 1) ** 2 / disc
        p = _norm_sf(math.sqrt(stat))

    # Paired bootstrap over items, preserving the pairing.
    rng = random.Random(seed)
    diffs = []
    idx = range(n)
    for _ in range(iterations):
        sample = [rng.choice(idx) for _ in idx]
        da = sum(a[i] for i in sample) / n
        db = sum(b[i] for i in sample) / n
        diffs.append(da - db)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs)) - 1]

    if p >= 0.05:
        verdict = "not distinguishable on this suite"
    elif acc_a > acc_b:
        verdict = f"{model_a} is better"
    else:
        verdict = f"{model_b} is better"

    return Comparison(
        model_a=model_a, model_b=model_b, n_common=n,
        acc_a=acc_a, acc_b=acc_b, diff=acc_a - acc_b, ci95=(lo, hi),
        b_only=b_only, c_only=c_only, mcnemar_stat=stat, p_value=p,
        verdict=verdict,
    )


def minimum_detectable_difference(n: int, acc: float = 0.7, power: float = 0.8) -> float:
    """The smallest accuracy gap this many items could reliably detect.

    Published so a reader can see when the suite is simply too small to settle
    a question, rather than inferring significance from the ordering of rows.
    """
    if n <= 0:
        return 1.0
    z_a, z_b = 1.96, 0.84 if power >= 0.8 else 0.52
    se = math.sqrt(2 * acc * (1 - acc) / n)
    return (z_a + z_b) * se
