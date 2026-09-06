"""Scoring a model against human acceptability judgments, not just a key.

Accuracy answers "how often was the model right". It cannot answer the more
interesting question: **does the model find the same things hard that people
do?** A model at 85% that fails exactly where Dutch speakers hesitate is a
different object from one at 85% that fails on violations every native speaker
catches instantly, and a leaderboard cannot tell them apart.

BLiMP-NL makes that question answerable, because nine of the ten hand-written
sentences per paradigm carry acceptability ratings on a 7-point scale from at
least 30 native speakers. For each paradigm, the mean rating of the grammatical
sentence minus the mean rating of the ungrammatical one is how obvious the
violation is to people. Correlating that against the model's per-paradigm
accuracy gives a human-alignment score.

This works on ordinary forced-choice answers; it does not need log-probabilities.

**The ratings are not redistributed here.** They live in the Radboud data
repository under CC BY-SA 4.0, which is share-alike and stricter than the
CC-BY on the sentence pairs, and the portal asks for an account. Download them
yourself and point this module at the file; nothing is fetched automatically
and nothing is bundled.

    https://doi.org/10.34973/tj4p-y007
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

RATINGS_DOI = "https://doi.org/10.34973/tj4p-y007"
DEFAULT_PATHS = [
    Path("data/blimp_nl_ratings.tsv"),
    Path("data/blimp_nl_ratings.csv"),
]


class RatingsUnavailable(RuntimeError):
    pass


def spearman(xs: list[float], ys: list[float]) -> float:
    """Rank correlation, ties averaged. No scipy dependency.

    Rank rather than Pearson because the two scales are not comparable: one is
    a mean 7-point rating, the other a proportion, and only their ordering is
    meaningfully shared.
    """
    n = len(xs)
    if n < 3:
        return float("nan")

    def rank(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def load_ratings(path: Path | None = None) -> dict[str, float]:
    """Load per-paradigm human acceptability deltas.

    Accepts a delimited file carrying at least a paradigm (or phenomenon)
    column and either a ready-made delta column, or separate mean ratings for
    the grammatical and ungrammatical sentence. Column names are matched
    loosely because the published file's exact header is not guaranteed
    stable, and a benchmark that breaks on a renamed column is a benchmark
    nobody re-runs.
    """
    candidates = [path] if path else DEFAULT_PATHS
    src = next((p for p in candidates if p and p.exists()), None)
    if src is None:
        raise RatingsUnavailable(
            "no BLiMP-NL ratings file found. They are not redistributed with this "
            f"repository: download them from {RATINGS_DOI} (CC BY-SA 4.0, the portal "
            "asks for an account) and save as data/blimp_nl_ratings.tsv"
        )

    text = src.read_text(encoding="utf-8", errors="replace")
    delim = "\t" if text.count("\t") > text.count(",") else ","
    rows = list(csv.DictReader(text.splitlines(), delimiter=delim))
    if not rows:
        raise RatingsUnavailable(f"{src} has no rows")

    cols = {c.lower().strip(): c for c in rows[0]}

    def pick(*names):
        for n in names:
            for low, orig in cols.items():
                if n in low:
                    return orig
        return None

    key = pick("paradigm", "phenomenon", "condition")
    delta = pick("delta", "difference", "diff")
    good = pick("rating_good", "mean_good", "acceptable", "grammatical")
    bad = pick("rating_bad", "mean_bad", "ungrammatical")
    if not key or not (delta or (good and bad)):
        raise RatingsUnavailable(
            f"{src}: could not find a paradigm column plus either a delta column "
            f"or separate good/bad rating columns. Saw: {list(cols.values())[:12]}"
        )

    acc: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        k = (r.get(key) or "").strip().lower()
        if not k:
            continue
        try:
            v = float(r[delta]) if delta else float(r[good]) - float(r[bad])
        except (TypeError, ValueError):
            continue
        acc[k].append(v)
    return {k: sum(v) / len(v) for k, v in acc.items() if v}


def human_alignment(results: list[dict], items: list, ratings: dict[str, float]) -> dict:
    """Correlate per-paradigm model accuracy with human acceptability deltas."""
    # note field carries "<phenomenon> · <paradigm> · BLiMP-NL (CC-BY-4.0)"
    para = {}
    for it in items:
        if it.category != "blimp":
            continue
        bits = [b.strip().lower() for b in (it.note or "").split("·")]
        para[it.id] = (bits[1] if len(bits) > 1 else (bits[0] if bits else ""))

    hits: dict[str, list[int]] = defaultdict(list)
    for r in results:
        p = para.get(r["id"])
        if p:
            hits[p].append(1 if r["correct"] else 0)

    xs, ys, rows = [], [], []
    for p, marks in sorted(hits.items()):
        if p not in ratings or len(marks) < 3:
            continue
        acc = sum(marks) / len(marks)
        xs.append(ratings[p])
        ys.append(acc)
        rows.append({"paradigm": p, "n": len(marks), "model_accuracy": round(acc, 4),
                     "human_delta": round(ratings[p], 3)})

    if len(xs) < 3:
        return {
            "available": False,
            "reason": f"only {len(xs)} paradigms matched between the run and the ratings file",
        }
    rho = spearman(xs, ys)
    return {
        "available": True,
        "paradigms": len(xs),
        "spearman_rho": round(rho, 4),
        "reading": (
            "positive means the model finds the same violations easy that Dutch "
            "speakers do; near zero means it is right often but for different reasons"
        ),
        "per_paradigm": rows,
    }
