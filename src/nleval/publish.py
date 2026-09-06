"""Collect run reports into the published leaderboard payload.

Every run writes its own report; this gathers them into one file the page can
read. Control runs are kept and labelled rather than filtered out: they are the
evidence that a score means something, and a leaderboard that hides its own
baselines is asking to be taken on trust.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

CONTROLS = {"echo", "always-a", "always"}


def _is_control(provider: str, model: str) -> bool:
    """Identify a control run from either the filename or the recorded model.

    Keying on the filename alone mislabelled a control as a real model once a
    file had been renamed, and a control silently promoted into the leaderboard
    is the one error this file exists to prevent.
    """
    blob = f"{provider} {model}".lower()
    return provider in CONTROLS or any(c in blob for c in ("echo", "always-a", "always a"))


def collect(results_dir: Path, items_meta: dict, out: Path) -> dict:
    runs = []
    for f in sorted(results_dir.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        s = doc.get("summary")
        if not s:
            continue
        provider = f.stem.split("__")[0]
        runs.append(
            {
                "provider": provider,
                "model": s.get("model", f.stem),
                "is_control": _is_control(provider, str(s.get("model", ""))),
                "n": s["n"],
                "accuracy": s["accuracy"],
                "ci95": s.get("ci95"),
                "chance": s.get("chance_baseline"),
                "lift": s.get("lift_over_chance"),
                "unparsed": s.get("unparsed_replies", 0),
                "by_category": s.get("by_category", {}),
                "generated_at": doc.get("generated_at"),
            }
        )

    # Real models first by accuracy, controls last: the controls are the floor,
    # not competitors.
    runs.sort(key=lambda r: (r["is_control"], -r["accuracy"]))

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items": items_meta,
        "runs": runs,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    return payload
