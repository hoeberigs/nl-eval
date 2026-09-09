"""Rewrite the results table in README.md from docs/results.json, so the
README never carries a number the board does not."""
import json, re, datetime
from pathlib import Path

d = json.loads(Path("docs/results.json").read_text(encoding="utf-8"))
pct = lambda x: f"{x*100:.1f}%"
NL = {"geslaagd": "passed", "onbeslist": "undecided", "niet geslaagd": "failed", "onvolledig": "incomplete", "rijdt niet": "did not run"}
rows = []
for r in d["runs"]:
    name = {"hf.co/BramVanroy/GEITje-7B-ultra-GGUF:Q4_K_M": "GEITje-7B-ultra"}.get(r["model"], r["model"].replace("-20251001", "")) + (" (control)" if r["is_control"] else " (local)" if r["provider"] in ("ollama",) else "")
    if r["failed"]:
        rows.append(f"| {name} | did not run | {NL[r['verdict']]} | provider quota error | | | |"); continue
    if r["n"] < 600:
        rows.append(f"| {name} | {pct(r['accuracy'])} on BLiMP-NL only, by likelihood | {NL[r['verdict']]} | | | | |"); continue
    bearing = [s for s in r["sections"] if s["verdict_bearing"]]
    if bearing and all(s["verdict"] == "gezakt" for s in bearing):
        open_secs = "every section failed"
    else:
      open_secs = "; ".join(f"{s['label']} {NL.get(s['verdict'], s['verdict'])}" + (f" ({pct(s['accuracy'])})" if s['verdict']=="gezakt" else "") for s in r["sections"] if s["verdict_bearing"] and s["verdict"] != "geslaagd")
    c = r.get("consistency"); ho = r.get("heldout")
    of = pct(c["order_reversed"]["flip_rate"]) if c and c["order_reversed"]["flip_rate"] is not None else "not run"
    rf = pct(c["register_swapped"]["flip_rate"]) if c and c["register_swapped"]["flip_rate"] is not None else "not run"
    h = (pct(ho["heldout_accuracy"]) + (" (no sign of contamination)" if "no evidence" in ho["verdict"] else " (" + ho["verdict"].split(":")[0] + ")")) if ho else "not run"
    rows.append(f"| {name} | {pct(r['accuracy'])} | {NL[r['verdict']]} | {open_secs or 'all sections passed'} | {of} | {rf} | {h} |")
n = max(r["n"] for r in d["runs"])
stamp = datetime.datetime.strptime(d["generated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%-d %B %Y")
table = (f"## Results, {stamp}\n\n| Model | Score (n={n}) | Verdict | Open or failed sections | Order-flip | Register-flip | Held-out |\n"
         "|---|---:|---|---|---:|---:|---:|\n" + "\n".join(rows) + "\n")
p = Path("README.md"); s = p.read_text(encoding="utf-8")
s2 = re.sub(r"## Results, .*?\n\n\|.*?\n(?=\n)", table, s, count=1, flags=re.S)
assert s2 != s or table in s, "results table not found"
p.write_text(s2, encoding="utf-8"); print("README results table regenerated:", len(rows), "rows")
