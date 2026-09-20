# Condition B preregistration — quality-threshold sensitivity test

Written and committed **before Condition B was run**. Not edited afterwards.

Condition A is frozen. Its results, findings and preregistration stand exactly
as committed in `242cb2c` and `acba0bd` and are not revisited here.

## What this is

A sensitivity test on one parameter of the frozen rubric: the total score
required to PASS.

| | Condition A | Condition B |
|---|---|---|
| `PASS_TOTAL` | 9 / 12 | 12 / 12 |
| Everything else | — | unchanged |

"Everything else" means: same model (`claude-sonnet-5`, thinking disabled), same
10 titles, same prompts byte-for-byte, same six rubric criteria and their 0/1/2
definitions, same hard gates (`groundedness == 2`, `product_clarity >= 1`), same
HUMAN_REVIEW behaviour and `original_sufficient` semantics, same 3-rewrite-attempt
cap, same 3-run protocol, same token logging.

One constant changes. Nothing else.

## Independent rationale for 12/12

The two thresholds represent two different and independently defensible quality
standards, chosen on their own merits rather than for their effect on either
workflow:

- **Condition A (9/12) — "acceptable / good enough."** A title passes while
  still scoring 1 ("partially meets") on up to three criteria. This is a
  realistic bar for a catalog where titles need to be serviceable, not perfect.
- **Condition B (12/12) — "strict."** Every criterion must be fully satisfied.
  This is a realistic bar for a catalog where a title is only acceptable if it
  is unambiguous, complete, readable, searchable, fully grounded and structurally
  consistent, with no partial credit anywhere.

Both are plausible product standards. Neither is the "correct" one. The question
is how the loop/graph comparison behaves across them.

## Question

Does the relative efficiency of uniform iterative processing versus explicit
state-dependent routing change when the quality threshold changes?

## What is deliberately not asserted

This preregistration makes **no claim about, and sets no requirement on, how
many iterations either workflow will perform.** Iteration counts are an outcome
to be measured, not a target. If the loop iterates more, less, or not at all at
12/12, that is the result.

Specifically: Condition B is not run in order to make the loop iterate, and the
result will not be evaluated against whether it did.

## Predictions

Recorded because they are cheap to record, and to be compared against whatever
actually happens. No weight is placed on them.

- Titles requiring at least one revision will increase in both workflows, since
  Condition A's passing titles averaged 11.33/12 (loop) and 11.19/12 (graph),
  below the new threshold.
- Some titles may exhaust the 3-attempt cap and end in `FAIL_CAP`. Condition A
  had zero.
- Direction of the loop-vs-graph gap: unknown. The graph's classify tax is
  unchanged and still paid on every title; whether the revision behaviour moves
  the balance is what the test measures.

Whatever the numbers say is the answer, including "no meaningful change."

## Reporting

- Condition B writes to `results/condition_b/`. Condition A's directories are
  not touched.
- Both conditions reported side by side. Neither is presented as the "real" one.
- The Condition A break-even figure (~39% ambiguous inputs by tokens) is a
  Condition-A-specific derived result and is not carried over to Condition B or
  generalised. If a break-even is computed for Condition B, it is computed
  separately from Condition B's own measurements.

## Limitations carried over from Condition A

Unchanged and still apply: n=10, one task, one model, one prompt set, no
statistical power; generator and evaluator are the same model, so pass rates are
not an independent quality measure; the 30% ambiguous-input ratio is a design
choice; thinking is disabled on both arms.
