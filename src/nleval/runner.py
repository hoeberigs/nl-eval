"""Running a suite against a model, with an explicit spend ceiling."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Callable

from .items import Item, chance_baseline
from .score import Report, score_item

# Rough per-million-token prices in USD, input/output, used only to refuse a
# run that would exceed the stated ceiling. Deliberately over-estimates: the
# purpose is to stop an accidental large spend, so being wrong in the cautious
# direction is the correct failure.
PRICES = {
    "default": (3.00, 15.00),
    "mini": (0.30, 1.50),
    "nano": (0.10, 0.50),
    "haiku": (0.80, 4.00),
    "sonnet": (3.00, 15.00),
    "opus": (15.00, 75.00),
}


def _price_for(model: str) -> tuple[float, float]:
    m = model.lower()
    for key, price in PRICES.items():
        if key != "default" and key in m:
            return price
    return PRICES["default"]


def estimate_cost(items: list[Item], model: str, out_tokens: int = 12) -> dict:
    """Estimate spend before committing to it.

    Token counts are approximated from characters rather than tokenised
    exactly, because the estimate exists to gate a decision, not to bill.
    """
    chars = sum(len(i.render()) for i in items) + 200 * len(items)
    in_tok = chars / 3.5
    out_tok = out_tokens * len(items)
    pin, pout = _price_for(model)
    usd = in_tok / 1e6 * pin + out_tok / 1e6 * pout
    return {
        "items": len(items),
        "est_input_tokens": int(in_tok),
        "est_output_tokens": int(out_tok),
        "est_usd": round(usd, 4),
        "est_eur": round(usd * 0.92, 4),
        "price_basis_usd_per_mtok": {"input": pin, "output": pout},
    }


class BudgetExceeded(RuntimeError):
    pass


def run(
    items: list[Item],
    call: Callable[[str], str],
    model: str,
    max_spend_eur: float | None = None,
    sleep: float = 0.0,
    progress: bool = True,
) -> Report:
    """Run every item, refusing to start if the estimate breaches the ceiling."""
    est = estimate_cost(items, model)
    if max_spend_eur is not None and est["est_eur"] > max_spend_eur:
        raise BudgetExceeded(
            f"estimated EUR {est['est_eur']:.2f} exceeds the ceiling of "
            f"EUR {max_spend_eur:.2f} for {len(items)} items on {model}. "
            "Reduce the suite with --category or --limit, or raise --max-spend "
            "deliberately."
        )

    scorer = getattr(call, "score", None)
    results = []
    for n, it in enumerate(items, 1):
        try:
            # Minimal pairs are scored by likelihood where the provider can do
            # it, which is what the corpus intends; everything else, and every
            # provider without local weights, falls back to the forced choice.
            if scorer and it.category == "blimp" and len(it.choices) == 2:
                lp = scorer(list(it.choices))
                pick = it.choices[0] if lp[0] >= lp[1] else it.choices[1]
                results.append({
                    "id": it.id, "category": it.category,
                    "correct": pick == it.answer, "parsed": True,
                    "got": "logprob", "expected": it.answer_letter,
                    "scoring": "logprob",
                    "margin": round(abs(lp[0] - lp[1]), 5),
                    "raw": "",
                })
                if sleep:
                    time.sleep(sleep)
                continue
            reply = call(it.render())
        except Exception as e:  # a provider failure is data, not a crash
            reply = ""
            results.append(
                {
                    "id": it.id,
                    "category": it.category,
                    "correct": False,
                    "parsed": False,
                    "got": None,
                    "expected": it.answer,
                    "error": str(e)[:200],
                    "raw": "",
                }
            )
            continue
        results.append(score_item(reply, it))
        if progress and n % 25 == 0:
            print(f"  {n}/{len(items)}", file=sys.stderr, flush=True)
        if sleep:
            time.sleep(sleep)

    return Report(model=model, results=results, chance=chance_baseline(items))


def write_report(report: Report, out: Path) -> dict:
    summary = report.summary()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "summary": summary,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "results": report.results,
            },
            indent=1,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return summary
