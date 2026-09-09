"""Loading and validating evaluation items.

Every item must be scorable without a model in the loop. That constraint rules
out open-ended generation tasks, and it is deliberate: an LLM-judged suite
costs money to run, drifts as the judge changes, and inherits the judge's own
Dutch weaknesses, which is exactly what is under test here.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

VALID_TYPES = {"mcq", "exact"}
LETTERS = "ABCDEFGH"


@dataclass
class Item:
    id: str
    category: str
    type: str
    prompt: str
    answer: str
    choices: list[str] = field(default_factory=list)
    note: str = ""
    alt: list[str] = field(default_factory=list)
    difficulty: str = "core"
    source_file: str = ""

    @property
    def answer_index(self) -> int:
        return self.choices.index(self.answer) if self.answer in self.choices else -1

    @property
    def answer_letter(self) -> str:
        i = self.answer_index
        return LETTERS[i] if 0 <= i < len(LETTERS) else ""

    def render(self) -> str:
        """The exact text sent to the model."""
        if self.type == "mcq":
            opts = "\n".join(
                f"{LETTERS[i]}) {c}" for i, c in enumerate(self.choices)
            )
            return (
                f"{self.prompt}\n\n{opts}\n\n"
                "Antwoord uitsluitend met de letter van het juiste antwoord."
            )
        return f"{self.prompt}\n\nAntwoord uitsluitend met het gevraagde woord of de gevraagde zin."


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).strip().lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[.!?]+$", "", s)
    return re.sub(r"\s+", " ", s)


def load_items(path: Path) -> list[Item]:
    """Load every .jsonl file under `path` (or a single file)."""
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    items: list[Item] = []
    for f in files:
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{f.name}:{lineno}: invalid JSON: {e}") from e
            raw.setdefault("category", f.stem)
            items.append(Item(source_file=f.name, **raw))
    return items


def validate(items: list[Item]) -> list[str]:
    """Structural checks that must pass before the suite is worth running.

    These are the failure modes that silently inflate or deflate a score:
    a gold answer missing from its own options, duplicate items double-counting
    one skill, and answer keys clustered on one letter, which hands free marks
    to any model with a position bias.
    """
    problems: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_prompts: dict[str, str] = {}

    for it in items:
        where = f"{it.source_file}:{it.id}"
        if it.type not in VALID_TYPES:
            problems.append(f"{where}: unknown type {it.type!r}")
        if it.id in seen_ids:
            problems.append(f"{where}: duplicate id, first seen in {seen_ids[it.id]}")
        seen_ids[it.id] = it.source_file

        # Prompt and options together, not the prompt alone: several categories
        # legitimately reuse one carrier question ("Welke spelling is correct?")
        # and vary only the options, so keying on the prompt would flag the
        # entire category as duplicated.
        key = _norm(it.prompt) + "||" + "|".join(sorted(_norm(c) for c in it.choices))
        if key in seen_prompts:
            problems.append(f"{where}: duplicate item, first seen in {seen_prompts[key]}")
        seen_prompts[key] = where

        if not it.prompt.strip():
            problems.append(f"{where}: empty prompt")
        if not str(it.answer).strip():
            problems.append(f"{where}: empty answer")

        if it.type == "mcq":
            if len(it.choices) < 2:
                problems.append(f"{where}: fewer than two choices")
            if it.answer not in it.choices:
                problems.append(f"{where}: answer {it.answer!r} is not one of its choices")
            if len({_norm(c) for c in it.choices}) != len(it.choices):
                problems.append(f"{where}: duplicate choices")
        elif it.choices:
            problems.append(f"{where}: exact item should not carry choices")

    problems.extend(_position_balance(items))
    return problems


def _position_balance(items: list[Item], tolerance: float = 0.15) -> list[str]:
    """Flag answer keys concentrated on one letter.

    A model that always replies "B" should score at chance, not above it. With
    four options the expected share per position is 25%; anything beyond the
    tolerance means the suite rewards a fixed guess.
    """
    out: list[str] = []
    # Grouped by category and option count: a category that mixes two- and
    # three-option items has a different fair share for each, and judging
    # both against the larger count flags a balanced key as skewed.
    by_cat: dict[str, list[Item]] = {}
    for it in items:
        if it.type == "mcq":
            by_cat.setdefault(f"{it.category} ({len(it.choices)} opties)", []).append(it)

    for cat, its in sorted(by_cat.items()):
        n = len(its)
        if n < 8:
            continue
        counts: dict[str, int] = {}
        for it in its:
            counts[it.answer_letter] = counts.get(it.answer_letter, 0) + 1
        n_opts = max(len(it.choices) for it in its)
        expected = 1.0 / n_opts
        for letter, c in sorted(counts.items()):
            if abs(c / n - expected) > tolerance:
                out.append(
                    f"{cat}: answer position {letter} is {c}/{n} "
                    f"({100*c/n:.0f}%), expected about {100*expected:.0f}%"
                )
    return out


def chance_baseline(items: list[Item]) -> float:
    """Expected score for a model that guesses uniformly among the options.

    Published without being asked for, because a headline accuracy is
    meaningless until the reader knows what zero knowledge looks like, and
    mixed-format suites do not have an obvious chance level.
    """
    total = 0.0
    for it in items:
        total += 1.0 / len(it.choices) if it.type == "mcq" and it.choices else 0.0
    return total / len(items) if items else 0.0
