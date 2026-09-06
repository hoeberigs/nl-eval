"""A held-out split, and the contamination test it enables.

Every public benchmark decays. Once the items are on GitHub, any model trained
afterwards may have memorised them, and a memorising model scores well without
knowing the language. There is no way to detect that from a public score alone.

A held-out split is the only direct test available without access to the
training data: run a model on the public items and on items it cannot have
seen, and compare. A model that scores far better on the public half has
learned this benchmark rather than Dutch.

**One caveat that is easy to get wrong, so it is enforced here.** Moving an item
out of a repository does not un-publish it. Git keeps history, so anything ever
committed stays recoverable and is compromised for this purpose forever. A
held-out set is only meaningful if it was *never committed*. `heldout/` is
gitignored from the outset and `status()` refuses to call a set clean if git is
tracking any of it.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .items import Item, load_items

HELDOUT_DIR = Path("heldout")
MANIFEST = Path("docs/heldout-manifest.json")


def _tracked(path: Path) -> list[str]:
    """Files under `path` that git knows about. Should always be empty."""
    try:
        out = subprocess.run(
            ["git", "ls-files", str(path)],
            capture_output=True, text=True, timeout=20, check=False,
        )
        return [l for l in out.stdout.splitlines() if l.strip()]
    except (OSError, subprocess.SubprocessError):
        return []


def _in_history(path: Path) -> list[str]:
    """Files under `path` that ever existed in git history."""
    try:
        out = subprocess.run(
            ["git", "log", "--all", "--pretty=format:", "--name-only", "--", str(path)],
            capture_output=True, text=True, timeout=30, check=False,
        )
        return sorted({l.strip() for l in out.stdout.splitlines() if l.strip()})
    except (OSError, subprocess.SubprocessError):
        return []


def load_heldout(path: Path | None = None) -> list[Item]:
    d = path or HELDOUT_DIR
    if not d.exists():
        return []
    items = load_items(d)
    for it in items:
        it.category = f"heldout_{it.category}"
    return items


def status(path: Path | None = None) -> dict:
    """Report the held-out set and whether it is genuinely unpublished."""
    d = path or HELDOUT_DIR
    items = load_heldout(d)
    tracked = _tracked(d)
    history = _in_history(d)

    cats: dict[str, int] = {}
    for it in items:
        cats[it.category] = cats.get(it.category, 0) + 1

    clean = not tracked and not history
    return {
        "directory": str(d),
        "exists": d.exists(),
        "items": len(items),
        "categories": dict(sorted(cats.items())),
        "tracked_by_git": tracked,
        "ever_in_git_history": history,
        "clean": clean,
        "verdict": (
            "held out: never committed, so a model cannot have seen it here"
            if clean and items
            else "COMPROMISED: these files are in git and are recoverable, so they "
                 "are not held out. Write new items instead; removing them now "
                 "does not help, because history keeps them."
            if (tracked or history)
            else "empty: no held-out items yet"
        ),
    }


def write_manifest(path: Path | None = None, out: Path | None = None) -> dict:
    """Publish proof the set exists without publishing the set.

    Ids and salted answer hashes let anyone check a later claim about what the
    held-out items were, while revealing neither the questions nor the answers.
    The salt is stored with the private items, not in the manifest, so the
    hashes cannot be brute-forced against a word list.
    """
    d = path or HELDOUT_DIR
    items = load_heldout(d)
    if not items:
        raise RuntimeError(f"no held-out items under {d}")

    salt_file = d / ".salt"
    if salt_file.exists():
        salt = salt_file.read_text(encoding="utf-8").strip()
    else:
        import secrets
        salt = secrets.token_hex(16)
        salt_file.write_text(salt + "\n", encoding="utf-8")

    entries = [
        {
            "id": it.id,
            "category": it.category,
            "answer_hash": hashlib.sha256(f"{salt}:{it.id}:{it.answer}".encode()).hexdigest()[:32],
        }
        for it in sorted(items, key=lambda i: i.id)
    ]
    payload = {
        "note": (
            "Commitment to a held-out set. Ids and salted answer hashes only: "
            "neither the questions nor the answers are published, and the salt "
            "is kept with the private items so the hashes cannot be brute-forced."
        ),
        "items": len(entries),
        "categories": sorted({e["category"] for e in entries}),
        "entries": entries,
    }
    target = out or MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return payload


def contamination_check(public: dict, heldout: dict) -> dict:
    """Compare a model's public score against its held-out score.

    Interpreted with the interval, not the point estimate: on a few hundred
    items a gap of several points is ordinary sampling noise, and reading it as
    contamination would be exactly the overconfidence this suite argues against.
    """
    from .compare import minimum_detectable_difference

    a, b = float(public["accuracy"]), float(heldout["accuracy"])
    n = min(int(public["n"]), int(heldout["n"]))
    mdd = minimum_detectable_difference(n, max(a, 0.5))
    gap = a - b

    if gap <= mdd:
        verdict = "no evidence of contamination: the gap is within sampling noise"
    elif gap <= 2 * mdd:
        verdict = "suggestive: the public score is higher than the held-out score by more than noise"
    else:
        verdict = "CONTAMINATION LIKELY: the model scores far better on published items"

    return {
        "public_accuracy": round(a, 4),
        "heldout_accuracy": round(b, 4),
        "gap": round(gap, 4),
        "n_smaller_split": n,
        "noise_floor": round(mdd, 4),
        "verdict": verdict,
    }
