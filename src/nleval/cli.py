"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import providers
from .items import chance_baseline, load_items, validate
from .runner import BudgetExceeded, estimate_cost, run, write_report

DEFAULT_ITEMS = Path(__file__).resolve().parents[2] / "items"


SUITES = {
    "core":  "the hand-written items in items/ (applied Dutch)",
    "holdout": "the private held-out items in heldout/, never committed",
    "blimp": "BLiMP-NL minimal pairs, native Dutch grammar (CC-BY-4.0)",
    "mmlu":  "Global-MMLU Dutch, translated knowledge (Apache-2.0)",
    "all":   "every layer, scored and reported separately",
}


def _load(args) -> list:
    """Assemble the requested layers.

    The layers stay separate in the report by design: a single number blending
    native grammar with translated knowledge cannot be read as either, so the
    runner scores per category and the suites keep distinct category names.
    """
    want = [w.strip() for w in (args.suite or "core").split(",")]
    if "all" in want:
        want = ["core", "blimp", "mmlu"]

    items: list = []
    if "core" in want:
        items += load_items(Path(args.items))
    if "holdout" in want:
        from .holdout import load_heldout
        held = load_heldout()
        if not held:
            print("no held-out items found under heldout/ (see --holdout-status)",
                  file=sys.stderr)
            sys.exit(4)
        items += held
    if "blimp" in want or "mmlu" in want:
        from .sources import SourceError, load_blimp, load_mmlu
        try:
            if "blimp" in want:
                items += load_blimp(per_phenomenon=args.per_phenomenon)
            if "mmlu" in want:
                items += load_mmlu(limit=args.mmlu_limit)
        except SourceError as e:
            print(f"could not load an external source:\n  {e}", file=sys.stderr)
            print("  (external layers download on first use and are cached under "
                  ".cache/sources; --suite core needs no network)", file=sys.stderr)
            sys.exit(4)
    if args.category:
        wanted = {c.strip().lower() for c in args.category.split(",")}
        items = [i for i in items if i.category.lower() in wanted]
    if args.limit:
        items = items[: args.limit]
    return items


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nl-eval", description="Dutch-language LLM evaluation suite")
    ap.add_argument("--items", default=str(DEFAULT_ITEMS))
    ap.add_argument("--provider", default="echo", choices=sorted(providers.REGISTRY))
    ap.add_argument("--model", default="echo")
    ap.add_argument("--suite", default="core",
                    help="comma-separated layers: " + ", ".join(SUITES))
    ap.add_argument("--per-phenomenon", type=int, default=20,
                    help="BLiMP-NL items sampled per linguistic phenomenon (22 phenomena)")
    ap.add_argument("--mmlu-limit", type=int, default=300,
                    help="Global-MMLU Dutch questions to pull")
    ap.add_argument("--category", help="comma-separated categories")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default="results/report.json")
    ap.add_argument("--max-spend", type=float, default=1.0,
                    help="hard ceiling in EUR; the run refuses to start above it")
    ap.add_argument("--sleep", type=float, default=0.0)
    ap.add_argument("--workers", type=int, default=8,
                    help="parallel calls for hosted providers (local likelihood scoring is always 1)")
    ap.add_argument("--no-resume", action="store_true",
                    help="ignore an existing .partial checkpoint and start over")
    ap.add_argument("--validate", action="store_true", help="check the item set and exit")
    ap.add_argument("--compare", nargs=2, metavar=("A.json","B.json"),
                    help="compare two run reports: McNemar plus a paired bootstrap")
    ap.add_argument("--publish", metavar="DIR",
                    help="collect every report in DIR into docs/results.json and exit")
    ap.add_argument("--estimate", action="store_true", help="print the cost estimate and exit")
    ap.add_argument("--holdout-status", action="store_true",
                    help="report the held-out set and whether git ever saw it")
    ap.add_argument("--holdout-manifest", action="store_true",
                    help="publish ids and salted answer hashes, never the items")
    ap.add_argument("--contamination-check", nargs=2, metavar=("PUBLIC.json","HELDOUT.json"),
                    help="compare a model's public score against its held-out score")
    ap.add_argument("--robustness", action="store_true",
                    help="ask each MCQ item in its original form and six meaning-preserving variants; report worst-case accuracy")
    ap.add_argument("--consistency", action="store_true",
                    help="re-ask each MCQ with options reversed and with an informal instruction; report flip rates")
    ap.add_argument("--canary", action="store_true",
                    help="ask the model for this suite's canary GUID; a clean model cannot produce it")
    ap.add_argument("--human-ratings", metavar="FILE",
                    help="BLiMP-NL acceptability ratings; adds a model-human alignment score")
    args = ap.parse_args(argv)

    if args.compare:
        from .compare import compare, minimum_detectable_difference
        docs = []
        for f in args.compare:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
            docs.append((d["summary"].get("model", Path(f).stem), d["results"]))
        cmp = compare(docs[0][1], docs[1][1], docs[0][0], docs[1][0])
        out = cmp.to_dict()
        out["minimum_detectable_difference"] = round(
            minimum_detectable_difference(cmp.n_common), 4
        )
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.publish:
        from .publish import collect
        cats: dict[str, int] = {}
        # Describe the suite that was actually requested, not just the local
        # items directory: publishing --suite all while reporting only the core
        # item count understates the benchmark on its own leaderboard.
        allitems = _load(argparse.Namespace(**{**vars(args), "category": None, "limit": None}))
        for i in allitems:
            cats[i.category] = cats.get(i.category, 0) + 1
        meta = {
            "total": len(allitems),
            "categories": dict(sorted(cats.items())),
            "chance_baseline": round(chance_baseline(allitems), 4),
        }
        out = Path("docs/results.json")
        payload = collect(Path(args.publish), meta, out)
        print(f"wrote {out} with {len(payload['runs'])} run(s)", file=sys.stderr)
        return 0

    if args.holdout_status:
        from .holdout import status
        st = status()
        print(json.dumps(st, indent=2, ensure_ascii=False))
        return 0 if st["clean"] or not st["items"] else 1

    if args.holdout_manifest:
        from .holdout import MANIFEST, write_manifest
        try:
            payload = write_manifest()
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 4
        print(f"wrote {MANIFEST} committing to {payload['items']} held-out items",
              file=sys.stderr)
        return 0

    if args.contamination_check:
        from .holdout import contamination_check
        docs = [json.loads(Path(f).read_text(encoding="utf-8"))["summary"]
                for f in args.contamination_check]
        print(json.dumps(contamination_check(docs[0], docs[1]), indent=2, ensure_ascii=False))
        return 0

    if args.robustness:
        from .robustness import robustness
        items = _load(args)
        try:
            call = providers.get(args.provider, args.model)
        except providers.ProviderError as e:
            print(str(e), file=sys.stderr)
            return 2
        rep = robustness(items, call, limit=args.limit, workers=args.workers)
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"model": args.model, "provider": args.provider, "robustness": rep}, indent=1, ensure_ascii=False))
        print(json.dumps({k: v for k, v in rep.items() if k != "detail"}, indent=2, ensure_ascii=False))
        return 0

    if args.consistency:
        from .consistency import consistency
        items = _load(args)
        try:
            call = providers.get(args.provider, args.model)
        except providers.ProviderError as e:
            print(str(e), file=sys.stderr)
            return 2
        rep = consistency(items, call, limit=args.limit)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"model": args.model, "consistency": rep}, indent=1, ensure_ascii=False))
        slim = {k: v for k, v in rep.items() if k != "detail"}
        print(json.dumps(slim, indent=2, ensure_ascii=False))
        return 0

    if args.canary:
        from .canary import run_canary
        try:
            call = providers.get(args.provider, args.model)
        except providers.ProviderError as e:
            print(str(e), file=sys.stderr)
            return 2
        result = {"model": args.model, "provider": args.provider, **run_canary(call)}
        if args.out and args.out != "results/run.json":
            out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=1, ensure_ascii=False))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    items = _load(args)
    if not items:
        print("no items matched", file=sys.stderr)
        return 2

    problems = validate(items)
    if args.validate:
        cats: dict[str, int] = {}
        for i in items:
            cats[i.category] = cats.get(i.category, 0) + 1
        print(json.dumps({
            "items": len(items),
            "categories": dict(sorted(cats.items())),
            "chance_baseline": round(chance_baseline(items), 4),
            "problems": problems,
        }, indent=2, ensure_ascii=False))
        return 1 if problems else 0

    if problems:
        print("item set has problems; run --validate to see them", file=sys.stderr)
        for p in problems[:10]:
            print("  " + p, file=sys.stderr)
        return 1

    if args.estimate:
        print(json.dumps(estimate_cost(items, args.model, provider=args.provider), indent=2))
        return 0

    try:
        call = providers.get(args.provider, args.model)
    except providers.ProviderError as e:
        print(str(e), file=sys.stderr)
        return 2

    print(f"{len(items)} items · {args.provider}/{args.model} · ceiling EUR {args.max_spend:.2f}",
          file=sys.stderr)
    try:
        report = run(items, call, args.model, max_spend_eur=args.max_spend, sleep=args.sleep,
                     workers=args.workers, out=Path(args.out), resume=not args.no_resume,
                     provider=args.provider)
    except BudgetExceeded as e:
        print(f"refused to run: {e}", file=sys.stderr)
        return 3

    # Optional: how well the model's difficulty profile matches human judgment.
    if args.human_ratings or any(i.category == "blimp" for i in items):
        from .human import RatingsUnavailable, human_alignment, load_ratings
        try:
            ratings = load_ratings(Path(args.human_ratings) if args.human_ratings else None)
            report.alignment = human_alignment(report.results, items, ratings)
        except RatingsUnavailable as e:
            if args.human_ratings:
                print(f"human alignment skipped: {e}", file=sys.stderr)

    summary = write_report(report, Path(args.out), extra={"provider": args.provider, "est_cost_eur": estimate_cost(items, args.model, provider=args.provider)["est_eur"]})
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
