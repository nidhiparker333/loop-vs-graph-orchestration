"""Run both workflows over the frozen dataset, N times, and write the comparison.

    python run_experiment.py            # 3 full runs (the preregistered protocol)
    python run_experiment.py --smoke    # 1 run, 3 titles, to validate plumbing cheaply

Ground-truth labels are stripped before any workflow sees a title. They are used
only for post-hoc per-category reporting and classifier scoring.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import graph_workflow
import loop_workflow
import shared

HERE = Path(__file__).parent
RESULTS = HERE / "results"

# Pricing per million tokens, claude-sonnet-5, from platform.claude.com/docs/en/about-claude/pricing
# verified 2026-09-19. Sonnet 5 introductory $2/$10 is now the standard price.
PRICE_IN_PER_MTOK = 2.00
PRICE_OUT_PER_MTOK = 10.00
PRICING_SOURCE = "platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19"

SMOKE_IDS = ("t01", "t05", "t08")
WORKFLOWS = ("loop", "graph")


def load_titles():
    data = json.loads((HERE / "test_titles.json").read_text(encoding="utf-8"))
    return data["titles"]


def strip_label(item: dict) -> dict:
    """Ground truth never reaches a prompt."""
    return {"id": item["id"], "title": item["title"]}


def cost(inp: float, out: float) -> float:
    return inp / 1e6 * PRICE_IN_PER_MTOK + out / 1e6 * PRICE_OUT_PER_MTOK


def loc(path: Path) -> int:
    """Non-blank, non-comment lines. Declared counting method; docstrings count."""
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def summarise(calls: list[dict], results: list[dict], workflow: str) -> dict:
    c = [x for x in calls if x["workflow"] == workflow]
    r = [x for x in results if x["workflow"] == workflow]
    n = len(r)
    return {
        "model_calls": len(c),
        "input_tokens": sum(x["input_tokens"] for x in c),
        "output_tokens": sum(x["output_tokens"] for x in c),
        "total_tokens": sum(x["total_tokens"] for x in c),
        "retry_calls": sum(1 for x in c if x["prompt"].endswith("_retry")),
        "titles": n,
        "pass": sum(1 for x in r if x["outcome"] == "PASS"),
        "human_review": sum(1 for x in r if x["outcome"] == "HUMAN_REVIEW"),
        "fail_cap": sum(1 for x in r if x["outcome"] == "FAIL_CAP"),
        "avg_iterations": round(sum(x["iterations"] for x in r) / n, 2) if n else 0,
        "avg_calls_per_title": round(len(c) / n, 2) if n else 0,
    }


def mrange(values: list[float], dp: int = 1) -> str:
    if len(set(values)) == 1:
        return f"{values[0]:.{dp}f}"
    return f"{statistics.mean(values):.{dp}f} ({min(values):.{dp}f}-{max(values):.{dp}f})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    titles = load_titles()
    n_runs = args.runs
    if args.smoke:
        titles = [t for t in titles if t["id"] in SMOKE_IDS]
        n_runs = 1
        print(f"SMOKE MODE: {len(titles)} titles, 1 run")

    labels = {t["id"]: t["intended_label"] for t in titles}
    clean = [strip_label(t) for t in titles]

    RESULTS.mkdir(exist_ok=True)
    per_run = []

    for run_id in range(1, n_runs + 1):
        shared.CALL_LOG.clear()
        print(f"\n=== run {run_id}/{n_runs} ===")

        results = []
        for item in clean:
            lr = loop_workflow.run_title(item, run_id)
            print(f"  loop  {item['id']}: {lr['outcome']:<12} iterations={lr['iterations']}")
            results.append(lr)
        for item in clean:
            gr = graph_workflow.run_title(item, run_id)
            print(
                f"  graph {item['id']}: {gr['outcome']:<12} route={gr['route']:<8}"
                f" iterations={gr['iterations']}"
            )
            results.append(gr)

        calls = list(shared.CALL_LOG)
        out = RESULTS / (f"smoke_run_{run_id}" if args.smoke else f"run_{run_id}")
        out.mkdir(exist_ok=True)
        for wf in WORKFLOWS:
            (out / f"{wf}_results.json").write_text(
                json.dumps([r for r in results if r["workflow"] == wf], indent=2),
                encoding="utf-8",
            )
        (out / "calls.json").write_text(json.dumps(calls, indent=2), encoding="utf-8")

        per_run.append(
            {
                "run_id": run_id,
                "results": results,
                "calls": calls,
                "summary": {wf: summarise(calls, results, wf) for wf in WORKFLOWS},
            }
        )
        print(f"  -> {out}")

    write_comparison(per_run, labels, smoke=args.smoke)
    return 0


def write_comparison(per_run: list[dict], labels: dict, smoke: bool) -> None:
    lines: list[str] = []
    w = lines.append

    w("# Loop vs graph orchestration - measured results\n")
    w(f"- Model: `{shared.MODEL}`, thinking disabled, no temperature set (400 on this model)")
    w(f"- Runs: {len(per_run)}   Titles per run: {per_run[0]['summary']['loop']['titles']}")
    w(f"- Max rewrite attempts per title: {shared.MAX_REWRITE_ATTEMPTS}")
    w(f"- PASS rule: total >= {shared.PASS_TOTAL}/12, groundedness == 2, product_clarity >= 1")
    w(f"- Token counts are API-reported (`usage`), not estimates.")
    w(f"- Pricing: ${PRICE_IN_PER_MTOK}/MTok in, ${PRICE_OUT_PER_MTOK}/MTok out. Source: {PRICING_SOURCE}")
    if smoke:
        w("\n**SMOKE RUN - not the real experiment.**")
    w("")

    # ---- headline table ----
    w("## Headline\n")
    w("Mean across runs, with (min-max) where runs differed.\n")
    w("| Metric | LOOP | GRAPH | Difference |")
    w("|---|---|---|---|")

    metrics = [
        ("Model calls", "model_calls", 1),
        ("Input tokens", "input_tokens", 0),
        ("Output tokens", "output_tokens", 0),
        ("Total tokens", "total_tokens", 0),
        ("Avg iterations per title", "avg_iterations", 2),
        ("Avg calls per title", "avg_calls_per_title", 2),
        ("PASS", "pass", 1),
        ("HUMAN_REVIEW", "human_review", 1),
        ("FAIL_CAP", "fail_cap", 1),
        ("JSON retry calls", "retry_calls", 1),
    ]
    means = {wf: {} for wf in WORKFLOWS}
    for label, key, dp in metrics:
        vals = {wf: [r["summary"][wf][key] for r in per_run] for wf in WORKFLOWS}
        for wf in WORKFLOWS:
            means[wf][key] = statistics.mean(vals[wf])
        lo, gr = means["loop"][key], means["graph"][key]
        delta = gr - lo
        pct = f" ({delta / lo * 100:+.1f}%)" if lo else ""
        w(f"| {label} | {mrange(vals['loop'], dp)} | {mrange(vals['graph'], dp)} | {delta:+.{dp}f}{pct} |")

    lo_cost = cost(means["loop"]["input_tokens"], means["loop"]["output_tokens"])
    gr_cost = cost(means["graph"]["input_tokens"], means["graph"]["output_tokens"])
    w(f"| Cost per run (calculated) | ${lo_cost:.4f} | ${gr_cost:.4f} | ${gr_cost - lo_cost:+.4f} |")
    w("")

    # ---- per category ----
    w("## Per category\n")
    w("Mean model calls and total tokens per title, by intended label.")
    w("Labels are ground truth, never shown to either workflow.\n")
    w("| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |")
    w("|---|---|---|---|---|---|")
    for cat in ("MINOR", "MAJOR", "UNCLEAR"):
        ids = [tid for tid, lab in labels.items() if lab == cat]
        if not ids:
            continue
        row = [cat, str(len(ids))]
        for metric in ("calls", "tokens"):
            for wf in WORKFLOWS:
                vals = []
                for r in per_run:
                    sel = [c for c in r["calls"] if c["workflow"] == wf and c["title_id"] in ids]
                    vals.append(
                        len(sel) / len(ids)
                        if metric == "calls"
                        else sum(c["total_tokens"] for c in sel) / len(ids)
                    )
                row.append(f"{statistics.mean(vals):.1f}")
        w(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} |")
    w("")

    # ---- classifier ----
    w("## Graph classifier vs ground truth\n")
    w("A graph that over-routes to human review 'saves' tokens by doing less work.")
    w("Read this together with the token numbers.\n")
    w("| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |")
    w("|---|---|---|---|")
    correct = total = 0
    for cat in ("MINOR", "MAJOR", "UNCLEAR"):
        counts = {r: 0 for r in graph_workflow.ROUTES}
        for r in per_run:
            for res in r["results"]:
                if res["workflow"] == "graph" and labels.get(res["title_id"]) == cat:
                    counts[res["route"]] += 1
                    total += 1
                    if res["route"] == cat:
                        correct += 1
        w(f"| {cat} | {counts['MINOR']} | {counts['MAJOR']} | {counts['UNCLEAR']} |")
    w(f"\nClassifier agreement with intended labels: {correct}/{total}"
      f" ({correct / total * 100:.0f}%)" if total else "")
    fallbacks = sum(
        1 for r in per_run for res in r["results"]
        if res["workflow"] == "graph" and res.get("route_fallback_used")
    )
    w(f"\nUnrecognised classifier labels needing the MAJOR fallback: {fallbacks}")
    w("")

    # ---- complexity ----
    w("## Orchestration complexity\n")
    w("Three descriptive metrics, reported side by side. Deliberately not")
    w("combined into a single score.\n")
    w("| Metric | LOOP | GRAPH |")
    w("|---|---|---|")
    w(f"| Workflow lines of code | {loc(HERE / 'loop_workflow.py')} | {loc(HERE / 'graph_workflow.py')} |")
    w(f"| Distinct model prompts | {loop_workflow.DISTINCT_PROMPTS} | {graph_workflow.DISTINCT_PROMPTS} |")
    w(f"| Explicit decision points | {loop_workflow.DECISION_POINTS} | {graph_workflow.DECISION_POINTS} |")
    w("")
    w("LOC counting method, fixed before the code was written: non-blank,")
    w("non-comment lines in the workflow file only. Shared code is excluded")
    w("because it is identical for both. Docstrings count as lines.")
    w("")

    # ---- per run ----
    w("## Per-run detail\n")
    w("| Run | Workflow | Calls | Input | Output | Total | PASS | HUMAN_REVIEW | FAIL_CAP |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in per_run:
        for wf in WORKFLOWS:
            s = r["summary"][wf]
            w(f"| {r['run_id']} | {wf} | {s['model_calls']} | {s['input_tokens']} |"
              f" {s['output_tokens']} | {s['total_tokens']} | {s['pass']} |"
              f" {s['human_review']} | {s['fail_cap']} |")
    w("")
    w("Interpretation, limitations and the preregistered prediction: see")
    w("`PREREGISTRATION.md` and the README.")

    path = RESULTS / ("smoke_comparison.md" if smoke else "comparison.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    sys.exit(main())
