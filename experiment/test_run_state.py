"""Local tests for per-run accounting. Makes no API calls and costs nothing.

    python test_run_state.py

Covers the bug where CALL_LOG was cleared between runs but CALLS_BY_TITLE and
PARSE_FAILURES were not, so a second run in the same process could attribute
the first run's calls and parse failures to itself.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import run_experiment  # noqa: E402
import shared  # noqa: E402

BASE = HERE / "results" / "condition_selftest"
N_TITLES = 6
FAIL_TITLE = "t0003"

_real_call = shared._call
_made: list[int] = [0]


def fake_call(prompt_name: str, user: str, ctx: dict) -> str:
    """Stand-in for shared._call: same bookkeeping, no network."""
    _made[0] += 1
    rec = {**ctx, "prompt": prompt_name, "input_tokens": 700, "output_tokens": 120,
           "total_tokens": 820, "cache_read_input_tokens": 0,
           "cache_creation_input_tokens": 0, "stop_reason": "end_turn",
           "latency_s": 0.01}
    shared.CALL_LOG.append(rec)
    shared.CALLS_BY_TITLE.setdefault((ctx.get("workflow"), ctx.get("title_id")), []).append(rec)
    if ctx.get("title_id") == FAIL_TITLE:
        return "not json"                      # fails every attempt, on purpose
    if prompt_name.startswith("EVALUATE"):
        return json.dumps({"original_sufficient": True,
                           "scores": {c: 2 for c in shared.CRITERIA},
                           "failed_criteria": [], "critique": "ok"})
    if prompt_name.startswith("CLASSIFY"):
        return json.dumps({"route": "MINOR", "reason": "ok"})
    return json.dumps({"title": "Mock Title"})


def run(n_runs: int) -> None:
    sys.argv = ["run_experiment", "--dataset", "titles_1000.json",
                "--limit", str(N_TITLES), "--runs", str(n_runs),
                "--condition", "selftest", "--workers", "4"]
    run_experiment.main()


def read(run_id: int, name: str):
    p = BASE / f"run_{run_id}" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main() -> int:
    shared._call = fake_call
    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            failures.append(name)

    # ---- two runs in one process must not pool their accounting ----
    shutil.rmtree(BASE, ignore_errors=True)
    print("two runs in one process:")
    run(2)

    c1, c2 = read(1, "calls.json"), read(2, "calls.json")
    check("run 2 records its own calls, not run 1 + run 2",
          len(c1) == len(c2), f"run1={len(c1)} run2={len(c2)}")
    check("no call appears in both runs' logs",
          {id(x) for x in c1}.isdisjoint({id(x) for x in c2}) and
          all(x["run_id"] == 1 for x in c1) and all(x["run_id"] == 2 for x in c2),
          "run_id stamped correctly")

    p1, p2 = read(1, "parse_failures.json") or [], read(2, "parse_failures.json") or []
    check("parse failures do not accumulate across runs",
          len(p1) == len(p2) and len(p1) > 0, f"run1={len(p1)} run2={len(p2)}")

    for rid in (1, 2):
        res = read(rid, "loop_results.json")
        tot = sum(r["model_calls"] for r in res)
        own = len([c for c in read(rid, "calls.json") if c["workflow"] == "loop"])
        check(f"run {rid}: per-title call counts sum to that run's loop calls",
              tot == own, f"{tot} == {own}")

    # ---- resuming must not re-pay, and must not double-count ----
    print("\nresume from checkpoint:")
    before = _made[0]
    run(1)
    check("resume made no model calls", _made[0] == before, f"{_made[0] - before} calls")
    c1b = read(1, "calls.json")
    check("resumed run reports the same call count as the original",
          len(c1b) == len(c1), f"{len(c1b)} == {len(c1)}")

    # ---- reset_run_state clears everything ----
    print("\nreset_run_state:")
    shared.CALL_LOG.append({"x": 1})
    shared.CALLS_BY_TITLE[("loop", "tXXXX")] = [{"x": 1}]
    shared.PARSE_FAILURES.append({"x": 1})
    shared.reset_run_state()
    check("clears all three accumulators",
          not shared.CALL_LOG and not shared.CALLS_BY_TITLE and not shared.PARSE_FAILURES)

    shutil.rmtree(BASE, ignore_errors=True)
    shared._call = _real_call
    print("\n" + ("all checks passed" if not failures else f"FAILED: {failures}"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
