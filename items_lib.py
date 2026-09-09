"""Item helpers. Additive builders: write() for a new category, extend() and extend_exact() for an existing one."""
import json
from pathlib import Path

OUT = Path("items")

def mcq(cat, n, prompt, correct, distractors, note="", difficulty="core"):
    return {"_cat": cat, "id": f"{cat}-{n:03d}", "prompt": prompt, "_correct": correct,
            "_distractors": distractors, "note": note, "difficulty": difficulty}

def _emit(cat, rows, start):
    out = []
    for i, r in enumerate(rows):
        opts = list(r["_distractors"])
        pos = (start + i) % (len(opts) + 1)
        opts.insert(pos, r["_correct"])
        out.append({"id": r["id"], "category": cat, "type": "mcq", "prompt": r["prompt"],
                    "choices": opts, "answer": r["_correct"], "note": r["note"], "difficulty": r["difficulty"]})
    return out

def write(cat, rows):
    p = OUT / f"{cat}.jsonl"
    out = _emit(cat, rows, 0)
    p.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n", encoding="utf-8")
    print(f"{cat}: {len(out)} items (new)")

def extend(cat, rows):
    p = OUT / f"{cat}.jsonl"
    existing = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = {e["id"] for e in existing}
    rows = [r for r in rows if r["id"] not in ids]
    out = _emit(cat, rows, len(existing))
    with p.open("a", encoding="utf-8") as fh:
        for o in out: fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"{cat}: +{len(out)} -> {len(existing)+len(out)}")

def extend_exact(cat, rows):
    p = OUT / f"{cat}.jsonl"
    existing = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ids = {e["id"] for e in existing}
    rows = [r for r in rows if r["id"] not in ids]
    with p.open("a", encoding="utf-8") as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{cat}: +{len(rows)} -> {len(existing)+len(rows)}")

