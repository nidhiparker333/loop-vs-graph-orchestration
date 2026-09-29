# Condition C preregistration — control flow with the prompts held constant

Written and committed **before Condition C was run**. Not edited afterwards.

Conditions A and B are untouched. Condition C writes to
`experiment/results/condition_c/` and shares nothing with them but the dataset,
the evaluator, and the token-logging layer.

## Why this condition exists

Condition A could not support a causal claim about routing, and said so. Its two
workflows differed in three ways at once:

| | Condition A loop | Condition A graph |
|---|---|---|
| Pre-classifier | none | yes |
| Rewrite prompts | one generic | two specialised (light / restructure) |
| Distinct prompts | 3 | 5 |

Any difference in the results could have come from the routing, from the
specialised prompt wording, or from the extra call. There was no way to tell.

**Condition C removes the prompt confound.** Both arms use the same prompt text,
the same model, the same evaluator, the same thresholds and the same attempt
cap. The only thing that differs is control flow: what the workflow does with a
failed evaluation.

## What is held constant

Both arms use, byte-for-byte:

- `REWRITE` from `shared.py`, unchanged.
- `EVALUATE` from `shared.py`, unchanged.
- One `FIX` template from `prompts_condition_c.py`, built from the same
  per-criterion instruction strings.

`test_run_state.py` asserts that for any evaluation with exactly one failed
criterion, the two arms produce **identical prompt bytes**. They can only differ
when more than one criterion has failed.

Also identical:

- Model `claude-sonnet-5`, thinking disabled, no temperature (400 on this model).
- `PASS_TOTAL = 12` — every criterion must score 2.
- `MAX_REWRITE_ATTEMPTS = 4`.
- Failed criteria are read from the **numeric scores** (`< 2`), never the model's
  free-text `failed_criteria` list, which is unvalidated.
- Human review is reachable **only** when the evaluator returns
  `original_sufficient = false`. The graph gets no additional exits.
- Neither arm uses a pre-classifier.
- The same `shared._call` token logging, JSON retry policy, per-title
  checkpointing and resume.

## The two arms

**Loop** (`loop_workflow_c.py`) — one fixed path, every time.

```
REWRITE -> EVALUATE
   |
   +-- PASS or HUMAN_REVIEW -> stop
   |
   +-- otherwise: FIX (all failed criteria at once) -> EVALUATE -> repeat
                  until PASS, HUMAN_REVIEW, or 4 attempts
```

**Graph** (`graph_workflow_c.py`) — an explicit node graph over the same prompts.

Eight named nodes: `fix_groundedness`, `fix_product_clarity`,
`fix_attribute_preservation`, `fix_searchability`, `fix_consistency`,
`fix_readability`, `human_review`, `done`. One edge function, `next_node`,
chooses the next node from the latest evaluation:

```
original_sufficient is false  -> human_review
verdict is PASS               -> done
otherwise                     -> fix_<highest-priority failed criterion>
```

Each fix node repairs **one** criterion and returns to EVALUATE. Routing
priority, from `prompts_condition_c.PRIORITY`:

```
groundedness > product_clarity > attribute_preservation
             > searchability > consistency > readability
```

Groundedness is first because an unsupported claim is the failure that matters
most; readability is last because it is the most cosmetic. The loop arm uses the
same order, but only to order the instructions it sends — never to choose.

**So the single manipulated variable is:** fix everything that failed at once,
versus fix the most important failure alone and re-evaluate.

## Metrics

Reported in `FINDINGS_C.md`, in the same shape as Condition A:

- Model calls, input/output tokens, cost.
- PASS, HUMAN_REVIEW, FAIL_CAP and ERROR counts.
- Iterations to PASS, and the full distribution of iteration counts per arm.
- For the graph: how often each of the eight nodes was entered.
- The deterministic groundedness check, on final outputs **and** on every
  scored candidate.
- Paired exact McNemar tests on the titles both arms attempted.
- Complexity: workflow lines of code, distinct prompts, decision points.
- Limits.

## Stopping rules

1. **Dry run on the first 50 titles.** If the loop arm averages **under 1.5
   iterations**, stop and report. A threshold that does not make the loop loop
   means the design is testing nothing, and the full run is not worth paying
   for.
2. If the dry run passes, estimate the full-run cost from its measured tokens,
   report the estimate, and wait for explicit go-ahead.
3. One run over all 1,000 titles. No second run, no tuning between runs.

No prompt, threshold, priority order or cap is changed after any run. If the
result is uninteresting, it is reported as uninteresting.

## Known limits, stated in advance

- **One run.** No run-to-run variance estimate, as in Condition A.
- **Same synthetic dataset**, with the same designed 30% ambiguous share and the
  same author-generated construction.
- **Same model and evaluator**, so the pass rates still depend on an evaluator
  this project has already shown to disagree with a word-level check.
- **The priority order is a design choice.** A different order is a different
  graph, and could produce a different result.
- **Fixing one criterion at a time is not the only possible graph.** This tests
  one routing policy, not branching in general.
- **`PASS_TOTAL = 12` is strict by construction**, chosen to force iteration.
  Results do not transfer to a 9/12 bar, which is what Condition A used.
- The audit's known blind spots carry over: flags are possible unsupported
  additions rather than confirmed errors, tokens under 3 characters are skipped,
  and the `STRUCTURAL` allowlist was tuned on dry runs from this dataset.

## Predictions

*To be completed by the author before the first run. Left blank deliberately —
a prediction written after seeing any Condition C output is not a prediction.*

<!--
Fill in below, then commit this file. Nothing calls the API until it is
committed. Useful shapes: which arm uses more model calls, which reaches PASS
more often, whether the graph's one-at-a-time repairs converge in fewer or more
iterations, which nodes dominate, and whether the audit-flag rates differ.
-->

**Model calls:**

**PASS rate:**

**Iterations to PASS:**

**Node distribution:**

**Audit flags:**

**Overall:**
