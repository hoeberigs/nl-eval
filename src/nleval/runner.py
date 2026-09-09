"""Running a suite against a model, with a spend ceiling, concurrency and resume.

The first full-size hosted runs were killed by a ten-minute timeout with
nothing written: a thousand sequential calls at a second each overruns any
sane limit, and a report that only exists at the end loses everything when the
process dies. Both are fixed structurally rather than by asking for patience.
Calls run in a small pool, and every finished item is appended to a checkpoint
immediately, so a killed run resumes from where it stopped instead of paying
for the same tokens twice.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    "flash": (0.15, 0.60),
    "haiku": (0.80, 4.00),
    "sonnet": (3.00, 15.00),
    "opus": (15.00, 75.00),
}


LOCAL_PROVIDERS = ("ollama", "hf", "echo", "always")


def _price_for(model: str, provider: str = "") -> tuple[float, float]:
    # A model running on this machine costs nothing per token. Pricing it as
    # if hosted made the spend guard refuse a free run, which is the guard
    # failing in the wrong direction.
    if provider in LOCAL_PROVIDERS:
        return (0.0, 0.0)
    m = model.lower()
    for key, price in PRICES.items():
        if key != "default" and key in m:
            return price
    return PRICES["default"]


def estimate_cost(items: list[Item], model: str, out_tokens: int = 12, provider: str = "") -> dict:
    """Estimate spend before committing to it.

    Token counts are approximated from characters rather than tokenised
    exactly, because the estimate exists to gate a decision, not to bill.
    """
    chars = sum(len(i.render()) for i in items) + 200 * len(items)
    in_tok = chars / 3.5
    out_tok = out_tokens * len(items)
    pin, pout = _price_for(model, provider)
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


def _checkpoint_path(out: Path | None) -> Path | None:
    return out.with_suffix(out.suffix + ".partial") if out else None


def _load_checkpoint(path: Path | None, out: Path | None = None) -> dict[str, dict]:
    """Everything already scored for this output: the finished report first,
    then any live or finished checkpoint on top.

    The report is the durable record. Resuming from the checkpoint alone
    lost a thousand answers once, because a top-up run's checkpoint replaced
    the previous one and the next resume only knew about the top-up.
    """
    done: dict[str, dict] = {}
    if out and out.exists():
        try:
            for r in json.loads(out.read_text(encoding="utf-8")).get("results", []):
                if "id" in r and not r.get("error"):
                    done[r["id"]] = r
        except (json.JSONDecodeError, OSError):
            pass
    if not path:
        return done
    candidates = [path.with_suffix(path.suffix + ".done"), path]
    lines: list[str] = []
    for c in candidates:
        if c.exists():
            lines.extend(c.read_text(encoding="utf-8").splitlines())
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
            done[r["id"]] = r
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def _score_one(it: Item, call: Callable[[str], str], scorer) -> dict:
    try:
        # Minimal pairs are scored by likelihood where the provider can do
        # it, which is what the corpus intends; everything else, and every
        # provider without local weights, falls back to the forced choice.
        if scorer and it.category.endswith("blimp") and len(it.choices) == 2:
            lp = scorer(list(it.choices))
            pick = it.choices[0] if lp[0] >= lp[1] else it.choices[1]
            return {
                "id": it.id, "category": it.category,
                "correct": pick == it.answer, "parsed": True,
                "got": "logprob", "expected": it.answer_letter,
                "scoring": "logprob",
                "margin": round(abs(lp[0] - lp[1]), 5),
                "raw": "",
            }
        reply = call(it.render())
    except Exception as e:  # a provider failure is data, not a crash
        return {
            "id": it.id, "category": it.category,
            "correct": False, "parsed": False, "got": None,
            "expected": it.answer, "error": str(e)[:200], "raw": "",
        }
    return score_item(reply, it)


def run(
    items: list[Item],
    call: Callable[[str], str],
    model: str,
    max_spend_eur: float | None = None,
    sleep: float = 0.0,
    progress: bool = True,
    workers: int = 8,
    out: Path | None = None,
    resume: bool = True,
    provider: str = "",
) -> Report:
    """Run every item, refusing to start if the estimate breaches the ceiling."""
    est = estimate_cost(items, model, provider=provider)
    if max_spend_eur is not None and est["est_eur"] > max_spend_eur:
        raise BudgetExceeded(
            f"estimated EUR {est['est_eur']:.2f} exceeds the ceiling of "
            f"EUR {max_spend_eur:.2f} for {len(items)} items on {model}. "
            "Reduce the suite with --category or --limit, or raise --max-spend "
            "deliberately."
        )

    ckpt = _checkpoint_path(out)
    done = _load_checkpoint(ckpt, out) if resume else {}
    todo = [it for it in items if it.id not in done]
    if done and progress:
        print(f"  resuming: {len(done)} already scored, {len(todo)} to go",
              file=sys.stderr, flush=True)

    scorer = getattr(call, "score", None)
    # Local likelihood scoring holds a model in memory; hosted calls are I/O
    # bound. One is safe to parallelise, the other is not worth it.
    pool = 1 if scorer else max(1, workers)

    lock = threading.Lock()
    fh = ckpt.open("a", encoding="utf-8") if ckpt else None
    finished = 0
    t0 = time.time()

    def record(r: dict) -> None:
        nonlocal finished
        with lock:
            done[r["id"]] = r
            if fh:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
            finished += 1
            if progress and finished % 50 == 0:
                rate = finished / max(time.time() - t0, 1e-9)
                print(f"  {finished}/{len(todo)}  ({rate:.1f}/s)", file=sys.stderr, flush=True)

    try:
        if pool == 1:
            for it in todo:
                record(_score_one(it, call, scorer))
                if sleep:
                    time.sleep(sleep)
        else:
            with ThreadPoolExecutor(max_workers=pool) as ex:
                futs = {ex.submit(_score_one, it, call, scorer): it for it in todo}
                for f in as_completed(futs):
                    record(f.result())
    finally:
        if fh:
            fh.close()

    # Emit in item order regardless of completion order.
    results = [done[it.id] for it in items if it.id in done]
    return Report(model=model, results=results, chance=chance_baseline(items))


def write_report(report: Report, out: Path, extra: dict | None = None) -> dict:
    summary = report.summary()
    if extra:
        summary.update(extra)
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
    # The checkpoint has served its purpose once the report exists.
    ckpt = _checkpoint_path(out)
    if ckpt and ckpt.exists():
        ckpt.rename(out.with_suffix(out.suffix + ".partial.done"))
    return summary
