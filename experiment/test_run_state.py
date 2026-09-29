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
_called_titles: set = set()


def fake_call(prompt_name: str, user: str, ctx: dict) -> str:
    """Stand-in for shared._call: same bookkeeping, no network."""
    _made[0] += 1
    _called_titles.add(ctx.get("title_id"))
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
    global FAIL_TITLE
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

    # ---- resuming must re-pay only for work that did not complete ----
    print("\nresume from checkpoint:")
    before = _made[0]
    _called_titles.clear()
    run(1)
    check("resume re-ran only the errored title, nothing else",
          _called_titles == {FAIL_TITLE},
          f"re-ran {sorted(_called_titles)}")
    check("resume cost far less than a full run",
          0 < (_made[0] - before) < len(c1),
          f"{_made[0] - before} calls vs {len(c1)} for a full run")
    c1b = read(1, "calls.json")
    check("resumed run reports the same call count as the original",
          len(c1b) == len(c1), f"{len(c1b)} == {len(c1)}")

    # ---- original_sufficient must be parsed strictly ----
    print("\nstrict boolean parsing:")
    check("the string \"false\" is False, not truthy",
          shared.as_bool("false") is False and shared.as_bool("False") is False)
    check("real booleans pass through",
          shared.as_bool(True) is True and shared.as_bool(False) is False)
    check("a missing or unrecognised value keeps the default",
          shared.as_bool(None) is True and shared.as_bool("maybe") is True
          and shared.as_bool("maybe", default=False) is False)
    check('evaluate() escalates on original_sufficient: "false"',
          shared.verdict(shared.as_bool("false"), {c: 2 for c in shared.CRITERIA})
          == "HUMAN_REVIEW",
          "a perfect 12/12 must still escalate")

    # ---- a checkpointed ERROR must be retried, not treated as done ----
    print("\nresume retries errored titles:")
    shutil.rmtree(BASE, ignore_errors=True)
    keep, FAIL_TITLE = FAIL_TITLE, "t0002"
    run(1)
    errs1 = [r for r in read(1, "loop_results.json") if r["outcome"] == "ERROR"]
    check("first pass produced an errored title", len(errs1) == 1, FAIL_TITLE)

    FAIL_TITLE = None                       # the transient failure clears
    before_retry = _made[0]
    _called_titles.clear()
    run(1)
    res2 = read(1, "loop_results.json")
    errs2 = [r for r in res2 if r["outcome"] == "ERROR"]
    check("resume re-ran the errored title", _made[0] > before_retry,
          f"{_made[0] - before_retry} calls")
    check("the errored title now has a real outcome", len(errs2) == 0)
    check("resume re-ran that title and no other",
          _called_titles == {"t0002"}, f"re-ran {sorted(_called_titles)}")
    check("every title is still present exactly once",
          len(res2) == N_TITLES and len({r["title_id"] for r in res2}) == N_TITLES)
    FAIL_TITLE = keep

    # ---- Condition C: both arms must emit identical prompt bytes ----
    print("\ncondition C prompt parity:")
    import graph_workflow_c as GC
    import loop_workflow_c as LC
    import prompts_condition_c as P

    orig = "LB Frosted Glass Forest Green 2700 LED Bulb"
    cand = "LED Bulb, Frosted Glass, Forest Green"
    parity = True
    for crit in P.PRIORITY:
        ev = {"scores": {c: (0 if c == crit else 2) for c in shared.CRITERIA},
              "original_sufficient": True, "verdict": "REVISE"}
        failed = P.failed_criteria(ev)
        loop_text = P.fix_prompt(orig, cand, failed)            # loop: all failures
        node = GC.next_node(ev)
        graph_text = P.fix_prompt(orig, cand, [node[len("fix_"):]])  # graph: routed one
        if loop_text != graph_text or node != f"fix_{crit}":
            parity = False
    check("single-failure FIX prompts are byte-identical across both arms",
          parity, f"checked all {len(P.PRIORITY)} criteria")

    check("both arms share REWRITE and EVALUATE verbatim",
          "REWRITE" in dir(shared) and "EVALUATE" in dir(shared)
          and not hasattr(P, "REWRITE") and not hasattr(P, "EVALUATE"),
          "prompts_condition_c defines only FIX")

    ev_multi = {"scores": dict({c: 2 for c in shared.CRITERIA},
                               groundedness=0, readability=0),
                "original_sufficient": True, "verdict": "REVISE"}
    check("the graph routes to the highest-priority failure",
          GC.next_node(ev_multi) == "fix_groundedness",
          "groundedness outranks readability")
    check("the loop sends every failure at once, the graph only one",
          len(P.failed_criteria(ev_multi)) == 2
          and P.fix_prompt(orig, cand, P.failed_criteria(ev_multi))
          != P.fix_prompt(orig, cand, ["groundedness"]),
          "they diverge only when more than one criterion failed")

    ev_insuff = {"scores": {c: 2 for c in shared.CRITERIA},
                 "original_sufficient": False, "verdict": "HUMAN_REVIEW"}
    check("human review is reachable only via original_sufficient = false",
          GC.next_node(ev_insuff) == "human_review"
          and set(GC.NODE_NAMES) == {f"fix_{c}" for c in P.PRIORITY} | {"human_review", "done"},
          f"{len(GC.NODE_NAMES)} nodes")
    check("both arms use the same attempt cap",
          LC.MAX_REWRITE_ATTEMPTS == GC.MAX_REWRITE_ATTEMPTS == 4)

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
