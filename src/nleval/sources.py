"""External Dutch benchmarks, fetched at run time and never redistributed.

Two decisions are worth stating, because both were choices rather than
conveniences.

**Native over translated.** Translating an English benchmark into Dutch mostly
measures how well a model handles translated English. The items keep their
source-language shape, culture-bound knowledge does not survive the trip, and
the phenomena that are genuinely hard in Dutch have no English original to
translate from: there is no English sentence that becomes "welk lidwoord hoort
bij beleid". So the grammar layer comes from a corpus built in Dutch by Dutch
linguists, and translation is used only where breadth is the point and
comparability across languages is the reason to want it.

**Fetched, not vendored.** These corpora carry their own licences. Copying
their rows into this repository would make this repository a redistributor and
raise a relicensing question for every downstream user. Downloading them on
demand into a local cache avoids that entirely: the licence stays with the
publisher, and this repo ships only the adapter. Attribution for both lives in
ATTRIBUTION.md and is required by their licences, not optional courtesy.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .items import Item

ROWS_API = "https://datasets-server.huggingface.co/rows"
SPLITS_API = "https://datasets-server.huggingface.co/splits"
UA = {"User-Agent": "nl-eval (https://github.com/hoeberigs/nl-eval)"}

CACHE = Path(os.environ.get("NL_EVAL_CACHE", ".cache/sources"))

SOURCES = {
    "blimp": {
        "dataset": "juletxara/blimp-nl",
        "licence": "CC-BY-4.0",
        "title": "BLiMP-NL: a corpus of Dutch minimal pairs and acceptability judgments",
        "authors": "Suijkerbuijk, Prins, de Heer Kloots, Zuidema & Frank",
        "url": "https://huggingface.co/datasets/juletxara/blimp-nl",
        "native": True,
    },
    "mmlu": {
        "dataset": "CohereLabs/Global-MMLU",
        "licence": "Apache-2.0",
        "title": "Global-MMLU (Dutch subset)",
        "authors": "Cohere Labs",
        "url": "https://huggingface.co/datasets/CohereLabs/Global-MMLU",
        "native": False,
    },
}


class SourceError(RuntimeError):
    pass


def _get(url: str, timeout: int = 60, attempts: int = 5) -> dict:
    """Fetch with backoff.

    Assembling BLiMP-NL means 22 config requests in quick succession, which the
    public datasets server rate-limits. A 429 is a wait instruction rather than
    an error, and retrying politely is the difference between a suite that
    assembles itself on first use and one that fails.
    """
    delay = 1.5
    last: Exception | None = None
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504) and attempt < attempts - 1:
                wait = float(e.headers.get("Retry-After") or 0) or delay
                time.sleep(min(wait, 20))
                delay *= 2
                continue
            break
        except Exception as e:  # network, schema drift
            last = e
            if attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            break
    raise SourceError(f"{url}\n  {type(last).__name__}: {last}") from last


def _cached(key: str, build) -> list[dict]:
    """Fetch once, reuse thereafter. The cache is gitignored, never committed."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{key}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    rows = build()
    f.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def _rows(dataset: str, config: str, split: str, limit: int) -> list[dict]:
    ds = urllib.parse.quote(dataset, safe="")
    out: list[dict] = []
    offset = 0
    while len(out) < limit:
        take = min(100, limit - len(out))
        page = _get(
            f"{ROWS_API}?dataset={ds}&config={config}&split={split}"
            f"&offset={offset}&length={take}"
        )
        got = page.get("rows", [])
        if not got:
            break
        out.extend(r["row"] for r in got)
        offset += len(got)
        if offset >= page.get("num_rows_total", 0):
            break
    return out


def _configs(dataset: str) -> list[str]:
    ds = urllib.parse.quote(dataset, safe="")
    payload = _get(f"{SPLITS_API}?dataset={ds}")
    return sorted({s["config"] for s in payload.get("splits", [])})


# --------------------------------------------------------------------------
# BLiMP-NL: minimal pairs
# --------------------------------------------------------------------------
def load_blimp(per_phenomenon: int = 20) -> list[Item]:
    """One forced choice per minimal pair: which sentence is the Dutch one.

    Sampled evenly across phenomena rather than taken from the top of the file,
    because the corpus is ordered by phenomenon and an unsampled prefix would
    score a model on anaphor agreement and nothing else.

    The pair is presented as a two-option choice so that any chat model can be
    scored. That is deliberately weaker than the corpus's intended use, which
    compares the log-probability of the two sentences; a model may pick the
    right sentence for the wrong reason. Where a provider exposes log-probs,
    prefer that mode and say which mode a published score used.
    """
    meta = SOURCES["blimp"]

    def build() -> list[dict]:
        rows: list[dict] = []
        for n, cfg in enumerate(_configs(meta["dataset"])):
            if n:
                time.sleep(0.4)  # 22 configs in a burst trips the rate limit
            for r in _rows(meta["dataset"], cfg, "train", per_phenomenon):
                r["_config"] = cfg
                rows.append(r)
        return rows

    raw = _cached(f"blimp_{per_phenomenon}", build)

    items: list[Item] = []
    for i, r in enumerate(raw, 1):
        good, bad = (r.get("sentence_good") or "").strip(), (r.get("sentence_bad") or "").strip()
        if not good or not bad or good == bad:
            continue
        # Alternate which option is correct so the answer key stays balanced.
        choices = [good, bad] if i % 2 else [bad, good]
        phen = (r.get("linguistic_phenomenon") or r.get("_config") or "").strip()
        items.append(
            Item(
                id=f"blimp-{i:04d}",
                category="blimp",
                type="mcq",
                prompt="Welke van deze twee zinnen is grammaticaal correct Nederlands?",
                choices=choices,
                answer=good,
                note=f"{phen} · {r.get('paradigm','')} · BLiMP-NL (CC-BY-4.0)",
                difficulty="core",
                source_file="blimp-nl",
            )
        )
    return items


# --------------------------------------------------------------------------
# Global-MMLU: translated breadth
# --------------------------------------------------------------------------
def load_mmlu(limit: int = 300) -> list[Item]:
    """Dutch Global-MMLU, for breadth and cross-language comparability.

    Kept explicitly separate from the native layers and never blended into a
    single headline: a score that mixes translated knowledge with native
    grammar cannot be read as either.
    """
    meta = SOURCES["mmlu"]

    def build() -> list[dict]:
        return _rows(meta["dataset"], "nl", "test", limit)

    raw = _cached(f"mmlu_nl_{limit}", build)

    items: list[Item] = []
    letters = ["A", "B", "C", "D"]
    for i, r in enumerate(raw, 1):
        q = (r.get("question") or "").strip()
        opts = [(r.get(f"option_{c.lower()}") or "").strip() for c in letters]
        gold = (r.get("answer") or "").strip().upper()
        if not q or not all(opts) or gold not in letters:
            continue
        if len({o.lower() for o in opts}) != len(opts):
            continue
        items.append(
            Item(
                id=f"mmlu-{i:04d}",
                category="mmlu_nl",
                type="mcq",
                prompt=q,
                choices=opts,
                answer=opts[letters.index(gold)],
                note=f"{r.get('subject','')} · Global-MMLU nl (Apache-2.0) · vertaald",
                difficulty="core",
                source_file="global-mmlu-nl",
            )
        )
    return items


LOADERS = {"blimp": load_blimp, "mmlu": load_mmlu}


def load_source(name: str, **kw) -> list[Item]:
    if name not in LOADERS:
        raise SourceError(f"unknown source {name!r}; available: {', '.join(sorted(LOADERS))}")
    return LOADERS[name](**kw)
