import json
from pathlib import Path

from nleval.items import Item, validate
from nleval.runner import run
from nleval.score import score_item


def _mcq(i, n_opts=2):
    opts = [f"opt{k}" for k in range(n_opts)]
    return Item(source_file="t.jsonl", id=f"t-{i:03d}", category="t", type="mcq",
                prompt=f"vraag {i}", choices=opts, answer=opts[i % n_opts])


def test_resume_reads_the_finished_report(tmp_path: Path):
    items = [_mcq(i) for i in range(6)]
    calls = []

    def call(prompt):
        calls.append(prompt)
        return "A"

    out = tmp_path / "r.json"
    rep = run(items[:4], call, "m", workers=1, out=out, progress=False)
    from nleval.runner import write_report
    write_report(rep, out)
    assert len(calls) == 4
    rep2 = run(items, call, "m", workers=1, out=out, progress=False)
    assert len(calls) == 6, "resume must pay only for the two new items"
    assert len(rep2.results) == 6


def test_alternative_answers_count_as_correct():
    it = Item(source_file="t.jsonl", id="x-001", category="schrijven", type="exact",
              prompt="Verbeter.", choices=[], answer="Zij hebben gelijk.", alt=["Ze hebben gelijk."])
    assert score_item("Ze hebben gelijk.", it)["correct"]
    assert score_item("Zij hebben gelijk.", it)["correct"]
    assert not score_item("Hun hebben gelijk.", it)["correct"]


def test_balance_is_judged_per_option_count():
    items = [_mcq(i, 2) for i in range(40)] + [_mcq(100 + i, 3) for i in range(9)]
    problems = [p for p in validate(items) if "position" in p]
    assert problems == [], problems
