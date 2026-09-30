# Decisions

Choices that are hard to reverse, or easy to forget the reason for. Newest last.

## Decided

**Stack: Python, standard library plus the `anthropic` SDK.** No orchestration
framework. A graph here is a `match` on a route string and a dict of state — the
point is to keep the routing visible in the code, since a framework would have
abstracted away the thing being measured. Explicitly rejected: LangGraph, because using it for something
called "graph orchestration" would have made the comparison about the framework.

**One place touches the API.** `shared._call` is the only function that calls
the model, so token accounting cannot drift between the two workflows. Every
retry, including JSON parse retries, is logged there as a real call.

**The verdict rule lives in code, not in the model.** `shared.verdict` applies
the frozen thresholds; the model returns scores and a sufficiency judgement.
This keeps the PASS rule fixed even if the model's phrasing drifts.

**The rubric and the prediction were committed before the first run**
(`242cb2c`). `PREREGISTRATION.md` and `FINDINGS.md` are never edited after the
fact — including where the preregistration's description of the workflows
differing in "exactly one thing" was later refined. Clarifications go in the
findings and the README, not into the frozen record.

**Instrumentation is attached post-hoc.** Per-title cost, timing and audit
fields are computed in `run_experiment.enrich` and `audit.py` from saved
results, so neither workflow file is touched to add measurement.

**Groundedness is checked without a model.** `audit.py` exists because the same
model generates and scores, and the results gave reason to check that criterion
independently. It is a heuristic for possible unsupported
additions, not a validated error measure, and it is reported as such.

**Runs checkpoint per title.** `progress.jsonl` makes a crash cost nothing on a
re-run. An `ERROR` outcome is deliberately *not* treated as done, so a title
whose work never completed is retried rather than being permanently cached as a
failure.

**Condition C shares prompt templates across both workflows.** Rewrite,
evaluation and the per-criterion fix instructions are the same in each; the
workflows differ after evaluation, in how many failed criteria they address per
round. Results in `experiment/FINDINGS_C.md`.

**The 10-title pilot is kept, not replaced.** It is labelled superseded and
retained with its results, because it is what prompted the scaled run and the
audit.

## Open

**Condition B has not been run.** `experiment/CONDITION_B_PREREGISTRATION.md`
raises `PASS_TOTAL` from 9 to 12 as a quality-threshold sensitivity test. It is
preregistered and unrun.

**One run at n=1,000.** A second run would give the run-to-run variance estimate
the current result lacks. About $7.50.

**The audit's `STRUCTURAL` allowlist was tuned on dry runs drawn from this same
dataset**, not a held-out sample. A sensitivity check over the saved results
would cost nothing and has not been done.

**Condition A does not isolate routing.** Its two workflows differ in the
routing step, the prompt count and the rewrite wording. Condition C addresses
this by sharing the same prompt templates across both workflows; see
`experiment/FINDINGS_C.md`.
