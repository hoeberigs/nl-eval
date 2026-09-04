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


def _load(args) -> list:
    items = load_items(Path(args.items))
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
    ap.add_argument("--category", help="comma-separated categories")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default="results/report.json")
    ap.add_argument("--max-spend", type=float, default=1.0,
                    help="hard ceiling in EUR; the run refuses to start above it")
    ap.add_argument("--sleep", type=float, default=0.0)
    ap.add_argument("--validate", action="store_true", help="check the item set and exit")
    ap.add_argument("--estimate", action="store_true", help="print the cost estimate and exit")
    args = ap.parse_args(argv)

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
        print(json.dumps(estimate_cost(items, args.model), indent=2))
        return 0

    try:
        call = providers.get(args.provider, args.model)
    except providers.ProviderError as e:
        print(str(e), file=sys.stderr)
        return 2

    print(f"{len(items)} items · {args.provider}/{args.model} · ceiling EUR {args.max_spend:.2f}",
          file=sys.stderr)
    try:
        report = run(items, call, args.model, max_spend_eur=args.max_spend, sleep=args.sleep)
    except BudgetExceeded as e:
        print(f"refused to run: {e}", file=sys.stderr)
        return 3

    summary = write_report(report, Path(args.out))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
