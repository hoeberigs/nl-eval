"""Rewrite the results table in README.md from docs/results.json."""
import json, re, datetime
from pathlib import Path

d = json.loads(Path("docs/results.json").read_text(encoding="utf-8"))
pct = lambda x: f"{x*100:.1f}%"
NAMES = {"hf.co/BramVanroy/GEITje-7B-ultra-GGUF:Q4_K_M": "GEITje-7B-ultra"}
rows = []
for r in d["runs"]:
    name = NAMES.get(r["model"], r["model"].replace("-20251001", "")) + (" (control)" if r["is_control"] else " (local)" if r["provider"] == "ollama" else "")
    ho = r.get("heldout")
    h = (pct(ho["heldout_accuracy"]) + " (" + ho["verdict"].split(":")[0] + ")") if ho else "not run"
    if r["failed"]:
        rows.append(f"| {name} | did not run | | | provider quota error | | |"); continue
    if r["n"] < 600:
        rows.append(f"| {name} | | | | BLiMP-NL only, by likelihood | {pct(r['accuracy'])} | |"); continue
    rb = r.get("robustness")
    if rb:
        rows.append(f"| {name} | **{pct(rb['worst_case'])}** (n={rb['items']}) | {pct(rb['original'])} | {rb['gap']*100:.1f} | {rb['band']} | {pct(r['accuracy'])} | {h} |")
    else:
        rows.append(f"| {name} | not tested | | | | {pct(r['accuracy'])} | {h} |")
stamp = datetime.datetime.strptime(d["generated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%-d %B %Y")
table = (f"## Results, {stamp}\n\n| Model | Worst case | Original (sample) | Drop | Band | Full set | Held-out |\n"
         "|---|---:|---:|---:|---|---:|---:|\n" + "\n".join(rows) + "\n")
p = Path("README.md"); s = p.read_text(encoding="utf-8")
s2 = re.sub(r"## Results, .*?\n\n\|.*?\n(?=\n)", table, s, count=1, flags=re.S)
assert s2 != s or table in s, "results table not found"
p.write_text(s2, encoding="utf-8"); print("README results table regenerated:", len(rows), "rows")
