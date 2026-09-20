# Loop and Graph Engineering

A small, controlled experiment comparing two orchestration patterns on the same
task, with the same model, the same inputs and the same rubric.

**Research question.** Does giving an AI workflow explicit decision-based routing
reduce unnecessary iteration and token usage without reducing output quality,
compared with a more uniform iterative loop?

Scoped to this task, dataset, model, prompts and rubric. This is an illustrative
experiment (n=10), not a study, and it makes no claim about orchestration
patterns in general.

## The two patterns

```
LOOP                                  GRAPH

Rewrite                               Classify
   |                                     |
   v                        +------------+------------+
Evaluate                    |            |            |
   |                      MINOR        MAJOR       UNCLEAR
   +-- PASS ------> done     |            |            |
   +-- HUMAN_REVIEW-> stop   v            v            v
   |                    Light rewrite  Restructure  Human review
   v                         |            |          (stop)
Revise --> Evaluate          +-----+------+
   (max 3 attempts)                v
                               Evaluate
                                  |
                        +-- PASS ------> done
                        +-- HUMAN_REVIEW-> stop
                                  |
                                  v
                               Revise  (max 3 attempts)
```

Both workflows can detect an insufficient input, using the same criteria and the
same evaluator. **The only difference is when.** The loop finds out after
spending a rewrite call; the graph finds out before.

The graph contains a loop: the revise/evaluate cycle inside the MINOR and MAJOR
branches is the same loop, entered conditionally.

## Layout

```
experiment/
    PREREGISTRATION.md    prediction + limitations, committed before the run
    rubric.md             frozen rubric, scoring, PASS rule
    test_titles.json      10 titles + ground-truth labels (stripped before prompts)
    shared.py             client, prompts, token logging, shared evaluator
    loop_workflow.py      Approach A
    graph_workflow.py     Approach B
    run_experiment.py     runner + aggregation
    results/
        run_1/ run_2/ run_3/   loop_results.json, graph_results.json, calls.json
        comparison.md          the measured comparison
```

Where to look:
- **the model is called** — `shared._call`, the only place that touches the API
- **token usage is recorded** — `shared._call`, appending to `shared.CALL_LOG`
- **the loop works** — `loop_workflow.run_title`
- **graph routing works** — `graph_workflow.run_title`
- **evaluation works** — `shared.evaluate` and `shared.verdict`

## Running it

Needs an Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

```bash
.venv/Scripts/python.exe experiment/run_experiment.py --smoke
```

```bash
.venv/Scripts/python.exe experiment/run_experiment.py
```

`--smoke` runs 3 titles once to check the plumbing. The full run is 3 complete
runs, preserved separately, as preregistered.

## Integrity notes

- Token counts are API-reported (`usage`), never estimated.
- Ground-truth labels are stripped before any model call.
- The evaluator sees only `(original, candidate)` — never the workflow name,
  iteration or route.
- The PASS rule lives in code (`shared.verdict`), not in the model's judgement.
- JSON parse retries are logged as real model calls with real tokens, in both
  workflows identically.
- Prompt caching is not used, so it cannot confound the token comparison.
- The rubric and the prediction were frozen and committed before the first run.
