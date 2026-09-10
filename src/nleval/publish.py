"""Collect run reports into the published payload, structured as the exam.

Every run writes its own report; this gathers them into one file the page can
read. Control runs are kept and labelled rather than filtered out: they are the
evidence that a score means something, and a leaderboard that hides its own
baselines is asking to be taken on trust.

The payload is shaped like the exam the page describes. Categories roll up
into sections (taalvorm, schrijven, lezen, ...), each section gets a Wilson
interval and a three-state verdict against a published pass line, and the
consistency and held-out reports attach to the run they belong to. The page
renders verdicts; it never computes them, so the rule lives in one place.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .score import wilson

CONTROLS = {"echo", "always-a", "always"}

# The pass line is an analogy to "voldoende", chosen here and stated on the
# page; it is not a DUO threshold. A section passes only when the lower bound
# of its interval clears it, fails only when the upper bound stays below it,
# and is otherwise undecided: a small section cannot pass on a lucky draw.
PASS_LINE = 0.80

SECTIONS = [
    {
        "id": "taalvorm", "label": "Taalvorm", "verdict": True,
        "categories": ["word_order", "variants", "formatting", "blimp"],
        "what": "woordvolgorde, Belgische en Nederlandse varianten, notatieconventies en de BLiMP-NL minimale paren",
    },
    {
        "id": "grammatica", "label": "Spelling en grammatica", "verdict": True,
        "categories": ["de_het", "diminutives", "spelling", "werkwoordspelling", "taaladvies"],
        "what": "lidwoorden, verkleinwoorden, tussen-n en samenstellingen, werkwoordspelling (d/t) en de twijfelgevallen van Taaladvies",
    },
    {
        "id": "schrijven", "label": "Schrijven", "verdict": True,
        "categories": ["schrijven"],
        "what": "foutieve zin herschrijven; exact vergeleken met de verbeterde zin, zonder beoordelaarsmodel",
    },
    {
        "id": "lezen", "label": "Lezen", "verdict": True,
        "categories": ["lezen"],
        "what": "korte Nederlandse passages met een begripsvraag",
    },
    {
        "id": "woordenschat", "label": "Woordenschat", "verdict": True,
        "categories": ["idioms", "false_friends"],
        "what": "uitdrukkingen en valse vrienden met het Engels en Duits",
    },
    {
        "id": "knm", "label": "KNM", "verdict": True,
        "categories": ["civics"],
        "what": "kennis van de Nederlandse maatschappij: instituties, gewoonten, geografie",
    },
    {
        "id": "ona", "label": "ONA en register", "verdict": True,
        "categories": ["register"],
        "what": "oriëntatie op de arbeidsmarkt en formeel versus informeel taalgebruik",
    },
    {
        "id": "kennis", "label": "Algemene kennis", "verdict": False,
        "categories": ["mmlu_nl"],
        "what": "Global-MMLU in het Nederlands; indicator, geen oordeel, want MMLU is zwaar besmet",
    },
]


def _is_control(provider: str, model: str) -> bool:
    """Identify a control run from either the filename or the recorded model.

    Keying on the filename alone mislabelled a control as a real model once a
    file had been renamed, and a control silently promoted into the leaderboard
    is the one error this file exists to prevent.
    """
    blob = f"{provider} {model}".lower()
    return provider in CONTROLS or any(c in blob for c in ("echo", "always-a", "always a"))


def _section_rows(by_category: dict) -> tuple[list[dict], str]:
    rows = []
    for sec in SECTIONS:
        n = correct = 0
        for cat in sec["categories"]:
            c = by_category.get(cat)
            if not c:
                continue
            n += int(c["n"])
            correct += int(round(float(c["accuracy"]) * int(c["n"])))
        if n == 0:
            verdict = "niet afgelegd"
            acc, lo, hi = None, None, None
        else:
            acc = correct / n
            lo, hi = wilson(correct, n)
            if not sec["verdict"]:
                verdict = "indicatie"
            elif lo >= PASS_LINE:
                verdict = "geslaagd"
            elif hi < PASS_LINE:
                verdict = "gezakt"
            else:
                verdict = "onbeslist"
        rows.append({
            "id": sec["id"], "label": sec["label"], "verdict_bearing": sec["verdict"],
            "n": n, "correct": correct,
            "accuracy": round(acc, 4) if acc is not None else None,
            "ci95": [round(lo, 4), round(hi, 4)] if lo is not None else None,
            "verdict": verdict,
        })

    bearing = [r for r in rows if r["verdict_bearing"]]
    if any(r["verdict"] == "niet afgelegd" for r in bearing):
        overall = "onvolledig"
    elif any(r["verdict"] == "gezakt" for r in bearing):
        overall = "niet geslaagd"
    elif all(r["verdict"] == "geslaagd" for r in bearing):
        overall = "geslaagd"
    else:
        overall = "onbeslist"
    return rows, overall


def _hardest(mains: list[tuple[str, dict]], runs: list[dict], top: int = 12) -> list[dict]:
    """The items most models miss, with the question and the key.

    Ranked by how many full-suite, non-control, non-failed runs got them
    wrong. Items are public, so showing them costs nothing and tells a reader
    where Dutch is hard for models rather than only how hard.
    """
    eligible = {r["model"] for r in runs if not r["is_control"] and not r["failed"] and r["n"] > 600}
    if not eligible:
        return []
    prompts: dict[str, dict] = {}
    for f in Path("items").glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                it = json.loads(line)
                prompts[it["id"]] = it
    missed: dict[str, list[str]] = {}
    label = {}
    for stem, doc in mains:
        model = doc["summary"].get("model", stem)
        if model not in eligible:
            continue
        for r in doc.get("results", []):
            if r.get("parsed") and not r.get("correct") and r["id"] in prompts:
                missed.setdefault(r["id"], []).append(model)
    ranked = sorted(missed.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:top]
    out = []
    for iid, models in ranked:
        it = prompts[iid]
        q = it["prompt"].strip().split("\n")
        question = q[-1].strip() if len(q) > 1 else q[0].strip()
        context = " ".join(q[:-1]).strip() if len(q) > 1 else ""
        out.append({
            "id": iid, "category": it["category"], "question": question[:220],
            "context": context[:260], "answer": it["answer"], "missed_by": sorted(models),
            "of": len(eligible),
        })
    return out


def _phenomena(mains: list[tuple[str, dict]], runs: list[dict]) -> list[dict]:
    """BLiMP-NL accuracy per linguistic phenomenon, per complete run.

    Twenty items per phenomenon is too few for a verdict, so these carry no
    verdict: they show where in the grammar a model's errors concentrate.
    """
    try:
        from .sources import load_blimp
        blimp = load_blimp()
    except Exception:
        return []
    phen_of = {it.id: (it.note.split(" · ")[0].strip() if it.note else "?") for it in blimp}
    complete = [r["model"] for r in runs if not r["is_control"] and not r["failed"] and r["n"] > 600]
    if not complete:
        return []
    acc: dict[str, dict[str, list[int]]] = {}
    for stem, doc in mains:
        model = doc["summary"].get("model", stem)
        if model not in complete:
            continue
        for r in doc.get("results", []):
            ph = phen_of.get(r["id"])
            if ph:
                acc.setdefault(ph, {}).setdefault(model, []).append(1 if r.get("correct") else 0)
    out = []
    for ph in sorted(acc):
        row = {"phenomenon": ph, "n": max(len(v) for v in acc[ph].values()), "by_model": {}}
        for m in complete:
            v = acc[ph].get(m)
            row["by_model"][m] = round(sum(v) / len(v), 3) if v else None
        row["mean"] = round(sum(x for x in row["by_model"].values() if x is not None) / max(1, sum(1 for x in row["by_model"].values() if x is not None)), 3)
        out.append(row)
    out.sort(key=lambda r: r["mean"])
    return out


def _load_json(f: Path) -> dict | None:
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def collect(results_dir: Path, items_meta: dict, out: Path) -> dict:
    from .holdout import contamination_check

    consistency: dict[str, dict] = {}
    heldout: dict[str, dict] = {}
    canary: dict[str, dict] = {}
    robust: dict[str, dict] = {}
    mains: list[tuple[str, dict]] = []

    for f in sorted(results_dir.glob("*.json")):
        doc = _load_json(f)
        if not doc:
            continue
        stem = f.stem
        if stem.startswith("robustness__") and "robustness" in doc:
            r = doc["robustness"]
            robust[doc.get("model", stem)] = {k: v for k, v in r.items() if k != "detail"}
            continue
        if stem.startswith("canary__") and "reproduced" in doc:
            canary[doc.get("model", stem)] = {"reproduced": doc["reproduced"], "probes": doc["probes"], "verdict": doc.get("verdict")}
            continue
        if stem.startswith("consistency__") and "consistency" in doc:
            rep = {k: v for k, v in doc["consistency"].items() if k != "detail"}
            consistency[doc.get("model", stem)] = rep
            continue
        s = doc.get("summary")
        if not s:
            continue
        if stem.startswith("heldout__"):
            heldout[s.get("model", stem)] = s
            continue
        mains.append((stem, doc))

    runs = []
    for stem, doc in mains:
        s = doc["summary"]
        provider = stem.split("__")[0]
        model = s.get("model", stem)
        sections, overall = _section_rows(s.get("by_category", {}))
        ho = heldout.get(model)
        # A run whose replies are mostly provider errors (quota, a retired
        # model id) is not a measurement of the model. It stays on the board
        # as a run that did not go, with its reason, rather than as a zero.
        items = doc.get("results", [])
        n_err = sum(1 for r in items if r.get("error"))
        failed = bool(items) and n_err / len(items) > 0.5
        if failed:
            overall = "rijdt niet"
            reason = next((r["error"] for r in items if r.get("error")), "")
            reason = " ".join(reason.split())[:140]
        else:
            reason = None
        runs.append(
            {
                "provider": provider,
                "model": model,
                "is_control": _is_control(provider, str(model)),
                "n": s["n"],
                "accuracy": s["accuracy"],
                "ci95": s.get("ci95"),
                "chance": s.get("chance_baseline"),
                "lift": s.get("lift_over_chance"),
                "unparsed": s.get("unparsed_replies", 0),
                "by_category": s.get("by_category", {}),
                "sections": sections,
                "verdict": overall,
                "failed": failed,
                "est_cost_eur": s.get("est_cost_eur"),
                "canary": canary.get(model),
                "robustness": robust.get(model),
                "error_share": round(n_err / len(items), 3) if items else 0.0,
                "failure_reason": reason,
                "consistency": consistency.get(model),
                "heldout": (
                    {"n": ho["n"], "accuracy": ho["accuracy"], "ci95": ho.get("ci95"),
                     **contamination_check(s, ho)}
                    if ho else None
                ),
                "generated_at": doc.get("generated_at"),
            }
        )

    # Real models first by accuracy, controls last: the controls are the floor,
    # not competitors.
    # Complete runs first, then incomplete ones (a partial exam is not a
    # rank), then failed runs, then the controls.
    runs.sort(key=lambda r: (r["is_control"], r["failed"], r["n"] < 600, -r["accuracy"]))

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardest": _hardest(mains, runs),
        "phenomena": _phenomena(mains, runs),
        "pass_line": PASS_LINE,
        "sections": [{k: v for k, v in sec.items()} for sec in SECTIONS],
        "items": items_meta,
        "runs": runs,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    return payload
