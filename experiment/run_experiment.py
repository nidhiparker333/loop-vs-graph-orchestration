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
import time
from concurrent.futures import ThreadPoolExecutor
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


def load_titles(dataset: str = "test_titles.json"):
    data = json.loads((HERE / dataset).read_text(encoding="utf-8"))
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


def enrich(results: list[dict], calls: list[dict], wall: dict) -> None:
    """Attach per-title calls, tokens, cost and model time. Post-hoc, so the
    workflow code itself is never touched to add instrumentation."""
    idx: dict[tuple, list] = {}
    for c in calls:
        idx.setdefault((c["workflow"], c["title_id"]), []).append(c)
    for r in results:
        cs = idx.get((r["workflow"], r["title_id"]), [])
        inp = sum(c["input_tokens"] for c in cs)
        out = sum(c["output_tokens"] for c in cs)
        r["model_calls"] = len(cs)
        r["input_tokens"] = inp
        r["output_tokens"] = out
        r["total_tokens"] = inp + out
        r["est_cost_usd"] = round(cost(inp, out), 6)
        r["model_time_s"] = round(sum(c["latency_s"] for c in cs), 2)
        r["review_decision"] = (
            "human_review" if r["outcome"] == "HUMAN_REVIEW"
            else "auto_accepted" if r["outcome"] == "PASS"
            else "needs_attention"
        )
        r["workflow_wall_s"] = wall.get(r["workflow"])


def write_samples(per_run: list[dict], labels: dict, outdir: Path, n_per: int = 6) -> None:
    """A manually reviewable sample: same titles for both workflows, side by side."""
    run = per_run[0]
    by_id = {}
    for r in run["results"]:
        by_id.setdefault(r["title_id"], {})[r["workflow"]] = r
    lines = ["# Reviewable sample of outputs", ""]
    lines += [f"From run {run['run_id']}. {n_per} titles per intended label, "
              "loop and graph side by side on the same input.", ""]
    for cat in ("MINOR", "MAJOR", "UNCLEAR"):
        ids = [i for i in by_id if labels.get(i) == cat][:n_per]
        lines += [f"## {cat}", ""]
        for tid in ids:
            pair = by_id[tid]
            src = next(iter(pair.values()))
            lines += [f"**{tid}** — original:", "", f"> {src['original']}", ""]
            for wf in WORKFLOWS:
                r = pair.get(wf)
                if not r:
                    continue
                final = r["final_title"] or "_(routed to human review)_"
                sc = r["evaluations"][-1]["total"] if r["evaluations"] else "-"
                lines.append(
                    f"- **{wf}** → {r['outcome']} (route={r.get('route') or '-'}, "
                    f"score={sc}/12, calls={r['model_calls']}, "
                    f"{r['total_tokens']} tok, ${r['est_cost_usd']:.5f})  \n  {final}"
                )
            lines.append("")
    (outdir / "samples.md").write_text("\n".join(lines), encoding="utf-8")


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
        "cost_usd": round(cost(sum(x["input_tokens"] for x in c),
                               sum(x["output_tokens"] for x in c)), 5),
        "model_time_s": round(sum(x["latency_s"] for x in c), 1),
        "wall_s": r[0].get("workflow_wall_s", 0) if r else 0,
    }


def mrange(values: list[float], dp: int = 1) -> str:
    if len(set(values)) == 1:
        return f"{values[0]:.{dp}f}"
    return f"{statistics.mean(values):.{dp}f} ({min(values):.{dp}f}-{max(values):.{dp}f})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument(
        "--pass-total",
        type=int,
        default=None,
        help="Rubric total required to PASS. Condition A = 9, Condition B = 12.",
    )
    ap.add_argument(
        "--condition",
        default="a",
        help="Condition label. 'a' writes to results/; anything else to results/condition_<x>/.",
    )
    ap.add_argument("--dataset", default="test_titles.json")
    ap.add_argument("--workers", type=int, default=12, help="Concurrent titles per workflow.")
    ap.add_argument("--limit", type=int, default=None, help="Use only the first N titles.")
    args = ap.parse_args()

    if args.pass_total is not None:
        shared.PASS_TOTAL = args.pass_total
    base = RESULTS if args.condition == "a" else RESULTS / f"condition_{args.condition}"
    print(f"condition={args.condition}  PASS_TOTAL={shared.PASS_TOTAL}/12  -> {base}")

    titles = load_titles(args.dataset)
    n_runs = args.runs
    if args.smoke:
        sel = [t for t in titles if t["id"] in SMOKE_IDS]
        titles = sel if sel else titles[:6]
        n_runs = 1
        print(f"SMOKE MODE: {len(titles)} titles, 1 run")
    if args.limit:
        titles = titles[: args.limit]
        print(f"LIMIT: first {len(titles)} titles")

    labels = {t["id"]: t["intended_label"] for t in titles}
    clean = [strip_label(t) for t in titles]

    base.mkdir(parents=True, exist_ok=True)
    per_run = []

    for run_id in range(1, n_runs + 1):
        shared.CALL_LOG.clear()
        print(f"\n=== run {run_id}/{n_runs} ===")

        verbose = len(clean) <= 20
        results = []
        wall = {}
        for wf, mod in (("loop", loop_workflow), ("graph", graph_workflow)):
            t0 = time.time()
            done = [0]

            def one(item, mod=mod, wf=wf):
                r = mod.run_title(item, run_id)
                done[0] += 1
                if verbose:
                    print(f"  {wf:<5} {item['id']}: {r['outcome']:<12}"
                          f" route={str(r.get('route')):<8} iterations={r['iterations']}")
                elif done[0] % 100 == 0:
                    print(f"  {wf}: {done[0]}/{len(clean)}  ({time.time() - t0:.0f}s)")
                return r

            with ThreadPoolExecutor(max_workers=args.workers) as ex:
                results.extend(ex.map(one, clean))
            wall[wf] = round(time.time() - t0, 1)
            print(f"  {wf} done in {wall[wf]}s")

        calls = list(shared.CALL_LOG)
        enrich(results, calls, wall)
        out = base / (f"smoke_run_{run_id}" if args.smoke else f"run_{run_id}")
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

    write_comparison(per_run, labels, smoke=args.smoke, outdir=base, condition=args.condition)
    return 0


def write_comparison(
    per_run: list[dict], labels: dict, smoke: bool, outdir: Path, condition: str
) -> None:
    lines: list[str] = []
    w = lines.append

    w(f"# Loop vs graph orchestration - measured results (Condition {condition.upper()})\n")
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
        ("Model time (s)", "model_time_s", 1),
        ("Wall clock (s)", "wall_s", 1),
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
    w("### Cost-relevant accuracy: UNCLEAR vs not\n")
    w("MINOR and MAJOR both cost 3 calls, so confusing them does not change cost.")
    w("Only the UNCLEAR decision diverts work, so this is the split that matters")
    w("for the token comparison.\n")
    tp = fp = tn = fn = 0
    for r in per_run:
        for res in r["results"]:
            if res["workflow"] != "graph":
                continue
            pred = res["route"] == "UNCLEAR"
            act = labels.get(res["title_id"]) == "UNCLEAR"
            tp += pred and act
            fp += pred and not act
            fn += (not pred) and act
            tn += (not pred) and not act
    n = tp + fp + fn + tn
    if n:
        w("| | routed UNCLEAR | routed to work |")
        w("|---|---|---|")
        w(f"| intended UNCLEAR | {tp} | {fn} |")
        w(f"| intended MINOR/MAJOR | {fp} | {tn} |")
        w(f"\nBinary accuracy: {(tp + tn)}/{n} ({(tp + tn) / n * 100:.1f}%)")
        w(f"- Missed ambiguous (sent to a rewrite anyway): {fn}")
        w(f"- Over-routed to human (work the loop did): {fp}"
          " — inspect these; they inflate the graph's apparent saving.")
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

    path = outdir / ("smoke_comparison.md" if smoke else "comparison.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    write_samples(per_run, labels, outdir)
    print(f"\nwrote {path} and {outdir / 'samples.md'}")


if __name__ == "__main__":
    sys.exit(main())
