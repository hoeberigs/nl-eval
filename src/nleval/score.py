"""Answer extraction and scoring.

Extraction is where an eval quietly loses its validity. A model that knows the
answer but wraps it in a sentence must not be marked wrong, and a model that
lists every option must not be marked right because the gold letter appears
somewhere in its reply. The rules below are deliberately narrow and are applied
in a fixed order.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

from .items import LETTERS, Item


def normalise(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).strip().lower()
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[.!?,;:]+$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def extract_choice(reply: str, item: Item) -> str | None:
    """Recover the selected option letter from a free-text reply."""
    if not reply:
        return None
    valid = set(LETTERS[: len(item.choices)])
    text = reply.strip()

    # 1. A bare letter, the format actually requested.
    m = re.fullmatch(r"\s*\(?([A-Ha-h])\)?\s*[.):]?\s*", text)
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()

    # 2. A letter in answer position at the start or after a lead-in.
    m = re.search(
        r"(?:^|\b(?:antwoord|answer|het juiste antwoord is|optie|keuze)\b[:\s]*)"
        r"\(?([A-Ha-h])\)?(?=[\s.):,]|$)",
        text,
        re.I,
    )
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()

    # 3. The full text of exactly one option, and no other.
    norm = normalise(text)
    hits = [
        LETTERS[i]
        for i, c in enumerate(item.choices)
        if re.search(r"(?<!\w)" + re.escape(normalise(c)) + r"(?!\w)", norm)
    ]
    if len(hits) == 1:
        return hits[0]

    # 4. A trailing letter, for replies that reason first and conclude after.
    # The letter must stand alone: without the leading boundary, a reply that
    # merely lists the options ("alpha, beta, gamma, delta") matches on the
    # final letter of the last word and is scored as a confident answer.
    m = re.search(r"(?:^|[\s:>*\-])\(?([A-Ha-h])\)?[.)]?\s*$", text)
    if m and m.group(1).upper() in valid:
        return m.group(1).upper()

    return None


def score_item(reply: str, item: Item) -> dict:
    """Score one reply. Unparseable replies are recorded, never silently wrong."""
    if item.type == "mcq":
        got = extract_choice(reply, item)
        return {
            "id": item.id,
            "category": item.category,
            "correct": got == item.answer_letter,
            "parsed": got is not None,
            "got": got,
            "expected": item.answer_letter,
            "raw": (reply or "")[:400],
        }

    got = normalise(reply)
    # Models often answer in a sentence; accept the gold string as a whole word.
    accepted = [normalise(item.answer)] + [normalise(a) for a in getattr(item, "alt", [])]
    exact = got in accepted
    contained = bool(
        re.search(r"(?<!\w)" + re.escape(normalise(item.answer)) + r"(?!\w)", got)
    )
    return {
        "id": item.id,
        "category": item.category,
        "correct": exact or contained,
        "parsed": bool(got),
        "got": (reply or "")[:120],
        "expected": item.answer,
        "raw": (reply or "")[:400],
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson interval, so small per-category samples carry honest error bars."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


@dataclass
class Report:
    model: str
    results: list[dict]
    chance: float
    alignment: dict | None = None

    def summary(self) -> dict:
        n = len(self.results)
        k = sum(1 for r in self.results if r["correct"])
        unparsed = sum(1 for r in self.results if not r["parsed"])
        lo, hi = wilson(k, n)

        by_cat: dict[str, list[dict]] = {}
        for r in self.results:
            by_cat.setdefault(r["category"], []).append(r)

        cats = {}
        for c, rs in sorted(by_cat.items()):
            ck = sum(1 for r in rs if r["correct"])
            clo, chi = wilson(ck, len(rs))
            cats[c] = {
                "n": len(rs),
                "correct": ck,
                "accuracy": round(ck / len(rs), 4),
                "ci": [round(clo, 4), round(chi, 4)],
            }

        from .compare import minimum_detectable_difference
        return {
            "model": self.model,
            "n": n,
            "correct": k,
            "accuracy": round(k / n, 4) if n else 0.0,
            "ci95": [round(lo, 4), round(hi, 4)],
            "chance_baseline": round(self.chance, 4),
            "lift_over_chance": round((k / n) - self.chance, 4) if n else 0.0,
            "unparsed_replies": unparsed,
            # The smallest accuracy gap this many items could reliably detect.
            # Published on every run so a reader can see when the suite is
            # simply too small to settle a question, instead of inferring
            # significance from the ordering of a leaderboard.
            "min_detectable_difference": round(
                minimum_detectable_difference(n, max(k / n, 0.5) if n else 0.7), 4
            ),
            "by_category": cats,
            **({"human_alignment": self.alignment} if self.alignment else {}),
        }
