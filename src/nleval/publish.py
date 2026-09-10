"""Collect run reports into the published payload.

Every run writes its own report; this gathers them into one file the page can
read. Controls are kept and labelled, never filtered out.

The headline is worst-case accuracy: the share of items a model answers
correctly in the original form and under every meaning-preserving variant of
the robustness battery. Plain accuracy stays visible as the ceiling a model
reaches when nothing is disturbed. There is no pass line and no verdict; the
board reports levels, drops and where the drops sit.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .score import wilson

CONTROLS = {"echo", "always-a", "always"}
RETIRED = {"civics", "register", "heldout_civics", "heldout_register"}

# Drop from original to worst case, in accuracy points, that separates the bands.
BANDS = {"stabiel": 0.05, "wankel": 0.15}

SECTIONS = [
    {"id": "taalvorm", "label": "Taalvorm", "indicator": False,
     "categories": ["word_order", "variants", "formatting", "blimp"],
     "what": "woordvolgorde, Belgische en Nederlandse varianten, notatieconventies en de BLiMP-NL minimale paren"},
    {"id": "grammatica", "label": "Spelling en grammatica", "indicator": False,
     "categories": ["de_het", "diminutives", "spelling", "werkwoordspelling", "taaladvies"],
     "what": "lidwoorden, verkleinwoorden, tussen-n en samenstellingen, werkwoordspelling (d/t) en de twijfelgevallen van Taaladvies"},
    {"id": "schrijven", "label": "Schrijven", "indicator": False,
     "categories": ["schrijven"],
     "what": "een zin met precies één fout herschrijven; exact vergeleken met de verbeterde zin, zonder beoordelaarsmodel"},
    {"id": "lezen", "label": "Lezen", "indicator": False,
     "categories": ["lezen"],
     "what": "brieven, bijsluiters, berichten, contracten en roosters met een vraag over een voorwaarde, uitzondering, datum of actie"},
    {"id": "woordenschat", "label": "Woordenschat", "indicator": False,
     "categories": ["idioms", "false_friends"],
     "what": "uitdrukkingen en valse vrienden met het Engels en Duits"},
    {"id": "kennis", "label": "Algemene kennis", "indicator": True,
     "categories": ["mmlu_nl"],
     "what": "Global-MMLU in het Nederlands; indicatie, want MMLU zit in vrijwel elke trainingsset"},
]


def _is_control(provider: str, model: str) -> bool:
    blob = f"{provider} {model}".lower()
    return provider in CONTROLS or any(c in blob for c in ("echo", "always-a", "always a"))


def _band(gap: float | None) -> str:
    if gap is None:
        return "niet getest"
    if gap < BANDS["stabiel"]:
        return "stabiel"
    if gap < BANDS["wankel"]:
        return "wankel"
    return "onstabiel"


def _accuracy(results: list[dict]) -> tuple[int, int]:
    live = [r for r in results if r.get("category") not in RETIRED]
    return sum(1 for r in live if r.get("correct")), len(live)


def _sections(results: list[dict], rob: dict | None) -> list[dict]:
    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r.get("category", ""), []).append(r)
    rob_cat = (rob or {}).get("by_category", {})
    out = []
    for sec in SECTIONS:
        rows = [r for c in sec["categories"] for r in by_cat.get(c, [])]
        n = len(rows)
        correct = sum(1 for r in rows if r.get("correct"))
        lo, hi = wilson(correct, n) if n else (None, None)
        rn = sum(rob_cat[c]["n"] for c in sec["categories"] if c in rob_cat)
        if rn:
            orig = sum(rob_cat[c]["original"] * rob_cat[c]["n"] for c in sec["categories"] if c in rob_cat) / rn
            worst = sum(rob_cat[c]["worst_case"] * rob_cat[c]["n"] for c in sec["categories"] if c in rob_cat) / rn
        else:
            orig = worst = None
        out.append({
            "id": sec["id"], "label": sec["label"], "indicator": sec["indicator"],
            "n": n, "accuracy": round(correct / n, 4) if n else None,
            "ci95": [round(lo, 4), round(hi, 4)] if n else None,
            "sample_n": rn or None,
            "original": round(orig, 4) if orig is not None else None,
            "worst_case": round(worst, 4) if worst is not None else None,
            "drop": round(orig - worst, 4) if orig is not None else None,
        })
    return out


def _load_json(f: Path) -> dict | None:
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _prompts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in Path("items").glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                it = json.loads(line)
                out[it["id"]] = it
    return out


def _hardest(mains: list[tuple[str, dict]], runs: list[dict], top: int = 12) -> list[dict]:
    eligible = {r["model"] for r in runs if not r["is_control"] and not r["failed"] and r["n"] > 600}
    if not eligible:
        return []
    prompts = _prompts()
    missed: dict[str, list[str]] = {}
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
        out.append({"id": iid, "category": it["category"], "question": question[:220],
                    "context": context[:260], "answer": it["answer"], "missed_by": sorted(models), "of": len(eligible)})
    return out


def _phenomena(mains: list[tuple[str, dict]], runs: list[dict]) -> list[dict]:
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
        vals = [x for x in row["by_model"].values() if x is not None]
        row["mean"] = round(sum(vals) / max(1, len(vals)), 3)
        out.append(row)
    out.sort(key=lambda r: r["mean"])
    return out


def _contamination(public_results: list[dict], heldout_doc: dict) -> dict | None:
    from .compare import minimum_detectable_difference
    pc, pn = _accuracy(public_results)
    hc, hn = _accuracy(heldout_doc.get("results", []))
    if not pn or not hn:
        return None
    a, b = pc / pn, hc / hn
    n = min(pn, hn)
    mdd = minimum_detectable_difference(n, max(a, 0.5))
    gap = a - b
    verdict = ("geen teken van besmetting" if gap <= mdd else
               "verdacht: de openbare score ligt meer dan de ruis boven de held-out score" if gap <= 2 * mdd else
               "waarschijnlijk besmet")
    return {"n": hn, "public_accuracy": round(a, 4), "heldout_accuracy": round(b, 4),
            "gap": round(gap, 4), "noise_floor": round(mdd, 4), "verdict": verdict}


def collect(results_dir: Path, items_meta: dict, out: Path) -> dict:
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
            robust[doc.get("model", stem)] = doc["robustness"]
            continue
        if stem.startswith("canary__") and "reproduced" in doc:
            canary[doc.get("model", stem)] = {"reproduced": doc["reproduced"], "probes": doc["probes"]}
            continue
        if stem.startswith("consistency__") and "consistency" in doc:
            consistency[doc.get("model", stem)] = {k: v for k, v in doc["consistency"].items() if k != "detail"}
            continue
        s = doc.get("summary")
        if not s:
            continue
        if stem.startswith("heldout__"):
            heldout[s.get("model", stem)] = doc
            continue
        mains.append((stem, doc))

    runs = []
    for stem, doc in mains:
        s = doc["summary"]
        provider = stem.split("__")[0]
        model = s.get("model", stem)
        items = doc.get("results", [])
        n_err = sum(1 for r in items if r.get("error"))
        failed = bool(items) and n_err / len(items) > 0.5
        reason = " ".join(next((r["error"] for r in items if r.get("error")), "").split())[:140] if failed else None
        correct, n = _accuracy(items)
        acc = correct / n if n else 0.0
        lo, hi = wilson(correct, n) if n else (0.0, 0.0)
        rob = robust.get(model)
        rob_summary = None
        if rob:
            rob_summary = {k: v for k, v in rob.items() if k not in ("detail", "by_category")}
            rob_summary["band"] = _band(rob.get("gap"))
            pv = rob.get("per_variant", {})
            worst_variant = min(((v, k) for k, v in pv.items() if k != "origineel"), default=None)
            rob_summary["weakest_variant"] = {"name": worst_variant[1], "accuracy": worst_variant[0]} if worst_variant else None
        ho = heldout.get(model)
        runs.append({
            "provider": provider, "model": model,
            "is_control": _is_control(provider, str(model)),
            "failed": failed, "failure_reason": reason,
            "n": n, "correct": correct, "accuracy": round(acc, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "unparsed": s.get("unparsed_replies", 0),
            "est_cost_eur": 0.0 if _is_control(provider, str(model)) else s.get("est_cost_eur"),
            "sections": _sections(items, rob),
            "robustness": rob_summary,
            "consistency": consistency.get(model),
            "heldout": _contamination(items, ho) if ho else None,
            "canary": canary.get(model),
            "generated_at": doc.get("generated_at"),
        })

    def key(r: dict):
        tested = r["robustness"] is not None and not r["failed"]
        return (r["is_control"], r["failed"], r["n"] < 600, not tested,
                -(r["robustness"]["worst_case"] if tested else r["accuracy"]))
    runs.sort(key=key)

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bands": BANDS,
        "sections": SECTIONS,
        "items": items_meta,
        "hardest": _hardest(mains, runs),
        "phenomena": _phenomena(mains, runs),
        "runs": runs,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    return payload
