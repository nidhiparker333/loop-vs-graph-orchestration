# Loop vs graph orchestration

Two AI workflows, the same 1,000 product titles, the same model, the same
rubric. Every model call, token count and intermediate output is saved.

**Result:** the graph workflow used 16.3% more model calls and 5.8% more tokens,
accepted 23 fewer titles, sent 22 more to human review, and had roughly half as
many outputs flagged by a word-level groundedness check. These point in
different directions; no winner is declared.

**The finding with the widest reach is not about orchestration.** A word-level
check with no model in it flagged candidates containing a content word that
could not be traced back to the input. On candidates the evaluator judged
workable, it scored full marks on groundedness for **83%** of the loop's flagged
candidates and **75%** of the graph's — the very criterion it was being asked
about.

The disagreement runs both ways: the evaluator also objected on candidates the
check passed (10 loop, 7 graph in that scope). Neither is ground truth for the
other. But a pipeline relying only on the model's own groundedness score would
have let most flagged candidates through.

An earlier version of this README led with "all 89 flagged outputs passed the
rubric with groundedness 2". That is accurate, but it follows directly from the
PASS rule, which requires `groundedness == 2` — so no passing title could have
scored otherwise. The figures above are measured over every scored candidate instead,
where the answer was not fixed in advance.

→ **[experiment/FINDINGS_SCALED.md](experiment/FINDINGS_SCALED.md)** — the full
result, what it supports, and what it does not.

## What was compared

Two **complete workflows**, not one isolated variable.

```
LOOP                                  GRAPH

Generic rewrite                       Classify
   |                                     |
   v                        +------------+------------+
Evaluate                    |            |            |
   |                      MINOR        MAJOR       UNCLEAR
   +-- PASS ------> done     |            |            |
   +-- HUMAN_REVIEW-> stop   v            v            v
   |                    Light rewrite  Restructure  Human review
   v                    (specialised)  (specialised)  (stop)
Revise --> Evaluate          |            |
   (max 3 attempts)          +-----+------+
                                   v
                                Evaluate
                                   |
                         +-- PASS ------> done
                         +-- HUMAN_REVIEW-> stop
                                   |
                                   v
                                Revise  (max 3 attempts)
```

They differ in three ways at once: the routing step, the number of prompts
(3 vs 5), and the wording of the rewrite instruction. **This does not isolate a
causal benefit of routing** — that would require holding the prompts constant.

Both workflows share the same evaluator prompt byte-for-byte, the same rubric,
the same PASS rule, and the same 3-attempt cap.

**The graph contains the same revise loop as the loop workflow**, and the loop
revised 22 of 1,000 titles. So in practice this compares a routed pipeline
against an unrouted one more than it compares looping against branching — the
looping machinery was largely idle in both workflows.

## Results at a glance

| | loop | graph |
|---|---|---|
| Model calls | 2,078 | 2,417 |
| Total tokens | 1,060,219 | 1,121,956 |
| Cost | $3.69 | $3.81 |
| Accepted (PASS) | 699 | 676 |
| Sent to human review | 300 | 322 |
| Audit-flagged final outputs | 59 of 699 | 30 of 677 |
| Paired: of 674 both accepted | 54 flagged | 29 flagged |
| Flagged candidates the evaluator passed | 83% | 75% |
| Workflow lines of code | 52 | 80 |

Audit flags mark **possible unsupported additions** found by a word-level check.
They are not confirmed errors, and the check misses unsupported claims that
introduce no new word. See
[FINDINGS_SCALED.md §1–§2](experiment/FINDINGS_SCALED.md).

The paired differences are lopsided enough to rule out chance within this run
(exact McNemar: audit flags 31 vs 6, p ≈ 4×10⁻⁵; accepted 25 vs 2, p ≈ 6×10⁻⁶).
That says the workflows behaved differently on these 1,000 titles — not that the
effect would repeat at the same size on another run.

## Condition C — the same comparison with the prompts held constant

Condition A could not attribute its result to routing, because its two arms also
differed in prompt count and rewrite wording. **Condition C removes that
confound**: the two workflows shared the same prompt templates — rewrite,
evaluation, and the per-criterion fix instructions. They differed after
evaluation. The graph fixed the highest-priority failed criterion, one at a
time; the loop addressed all failed criteria together. `PASS_TOTAL = 12`, 4-attempt
cap, 1,000 titles, $13.34.

| | loop | graph |
|---|---|---|
| Model calls | 3,575 | 3,631 (+1.6%) |
| PASS | **500** | 477 |
| HUMAN_REVIEW | 303 | 303 |
| FAIL_CAP | 194 | **218** |
| Audit-flagged, paired on 425 both passed | 31 | 29 (p = 0.79) |

**Most of Condition A's cost gap came from something other than branching.**
With the prompt templates shared, the graph cost 1.6% more calls instead of
16.3% — the earlier figure largely reflected the classifier call and the extra
prompts rather than the routing.

**Routing did not produce a clear quality gain here.** The graph passed 23
fewer titles, reached the attempt cap 24 more times (paired p = 0.038), and
produced outputs the audit could not distinguish from the loop's (paired
p = 0.79).

Of five preregistered predictions: three supported, one not supported, one
mixed. The strict threshold also made the loop iterate — 1.76 attempts per title
against Condition A's 1.02 — which showed that iteration seldom recovers a title
that failed once: 685 of 1,000 resolved on the first attempt and 206 reached the
cap, with few in between.

→ **[experiment/FINDINGS_C.md](experiment/FINDINGS_C.md)** · preregistration in
[CONDITION_C_PREREGISTRATION.md](experiment/CONDITION_C_PREREGISTRATION.md),
committed before the run.

## Limits

- **One run** at n=1,000. No run-to-run variance estimate.
- **Synthetic titles**, generated by the author, with a **designed 30% ambiguous
  share** — which sits just below the measured 36% token break-even, so a
  different mix reverses the token result.
- **One model, one prompt set, one task.**
- **The loop revised only 22 of 1,000 titles.** A loop that iterates hard — the
  case that motivates most concern about loop cost — is untested.
- **The audit is a heuristic** with an author-chosen allowlist. Some flags are
  harmless wording changes; some unsupported claims go unflagged.

## Layout

```
experiment/
    FINDINGS_SCALED.md          the 1,000-title result          <- start here
    FINDINGS.md                 the 10-title pilot, unedited
    PREREGISTRATION.md          prediction, committed before the pilot ran
    CONDITION_B_PREREGISTRATION.md   preregistered, not yet run
    rubric.md                   frozen rubric, scoring, PASS rule
    titles_1000.json            the 1,000-title dataset
    test_titles.json            the 10 pilot titles
    generate_titles.py          seeded dataset generator
    shared.py                   client, prompts, token logging, evaluator
    loop_workflow.py            the loop
    graph_workflow.py           the graph
    audit.py                    deterministic groundedness check
    run_experiment.py           runner and aggregation
    test_run_state.py           local tests, no API calls
    results/
        condition_scaled/       the 1,000-title run (raw)
        run_1..3/               the pilot's three runs (raw)
        condition_dryrun*/       small validation runs
```

Where to look:

- **the model is called** — `shared._call`, the only place that touches the API
- **tokens are recorded** — `shared._call`, into `shared.CALL_LOG`
- **the loop works** — `loop_workflow.run_title`
- **graph routing works** — `graph_workflow.run_title`
- **evaluation works** — `shared.evaluate` and `shared.verdict`
- **the audit works** — `audit.invented_words`

## Preregistration, and what it covers

`PREREGISTRATION.md` was committed in `242cb2c`, **before the first run**. It
covers the **10-title pilot**: the rubric, the scoring, the PASS rule, the
category definitions and a prediction about model calls.

The 1,000-title dataset and `audit.py` came **afterwards**, in response to what
the pilot showed. They are not covered by that preregistration. The rubric, PASS
rule and both workflows were unchanged between the pilot and the scaled run; the
dataset and the audit are additions, and the scaled run is therefore not a
preregistered test of a prior hypothesis.

`CONDITION_B_PREREGISTRATION.md` was written and committed before any Condition
B run. Condition B has not been run.

**One statement in the preregistration was later refined, and is left in
place.** It says the two workflows differ in "exactly one thing: *when*
ambiguity is detected". They also differ in prompt count and in the wording of
the rewrite instruction. The preregistration is not edited, because editing a
preregistration after seeing results would remove the value it exists to
provide. The fuller description is in `FINDINGS_SCALED.md` and above.

`git log --reverse` shows the ordering.

## The 10-title pilot

`FINDINGS.md` records an earlier run over 10 hand-written titles, three
repetitions. It is kept as written. Its headline — the graph costing more for
equal quality — held up at n=1,000. Its derived break-even (38.7%, extrapolated
from two points) was superseded by the measured 36.0%.

The pilot's most useful contribution was showing that the loop never iterated,
which is what prompted Condition B.

## Running it

Requires Python 3.10+ and an Anthropic API key.

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install anthropic     # Windows
# python3 -m venv .venv && .venv/bin/pip install anthropic   # macOS / Linux
```

```bash
export ANTHROPIC_API_KEY=...          # PowerShell: $env:ANTHROPIC_API_KEY = "..."
```

Local tests and the dataset generator make **no API calls and cost nothing**:

```bash
.venv/Scripts/python.exe experiment/test_run_state.py
.venv/Scripts/python.exe experiment/generate_titles.py --report
```

The generator is seeded, so it reproduces `titles_1000.json` byte for byte.

Reproduce the 1,000-title run (**~$7.50**, ~9 minutes):

```bash
.venv/Scripts/python.exe experiment/run_experiment.py --dataset titles_1000.json --runs 1 --condition scaled
```

Re-audit a finished run without spending anything:

```bash
.venv/Scripts/python.exe experiment/audit.py experiment/results/condition_scaled/run_1
```

Useful flags: `--limit N` (first N titles), `--workers N` (concurrency, default
12), `--pass-total N` (rubric threshold), `--condition LABEL` (output
directory). A run checkpoints per title to `progress.jsonl`; re-running the same
command resumes and does not re-pay for completed titles.

## Integrity notes

- Token counts are API-reported (`usage`), never estimated.
- Ground-truth labels are stripped before any model call.
- The evaluator sees only `(original, candidate)` — never the workflow name,
  iteration or route.
- The PASS rule lives in code (`shared.verdict`), not in the model's judgement.
- JSON parse retries are logged as real model calls with real tokens, in both
  workflows identically.
- Prompt caching is not used, so it cannot confound the token comparison.
- The rubric was frozen and committed before the first run.

## Reviewing this

[REVIEW.md](REVIEW.md) lists what this work claims, what it does not, and the
weaknesses already known to the author.
