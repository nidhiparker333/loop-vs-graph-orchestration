# Findings — 1,000 titles, Condition A (PASS ≥ 9/12)

One run, 1,000 titles, `claude-sonnet-5`, thinking disabled. 4,495 model calls,
$7.49 total, ~9 minutes wall clock. Raw data in `results/condition_scaled/`.

The 10-title pilot (`FINDINGS.md`) stands unedited as a separate result.

## Headline

| | loop | graph | |
|---|---|---|---|
| Model calls | 2,078 | 2,417 | **+16.3%** |
| Total tokens | 1,060,219 | 1,121,956 | **+5.8%** |
| Cost | $3.69 | $3.81 | **+$0.12** |
| PASS | 699 | 676 | |
| HUMAN_REVIEW | 300 | 322 | |
| Fabrication rate | **8.4%** | **4.4%** | |
| Ambiguous inputs caught | 295/300 (98.3%) | 300/300 (100%) | |
| Workflow LOC | 52 | 80 | +54% |

**The graph cost more and fabricated less.** Neither difference is large, and
they point in opposite directions, so there is no winner to declare.

## 1. The evaluator caught none of the fabrications

Of 89 titles containing an invented content word, **89 passed the rubric** —
59/59 for the loop, 30/30 for the graph. Every one scored `groundedness = 2`,
the criterion defined as "every claim traceable to the original".

```
in   Pro 9 - Ivory - 4x6 ft - Fast Shipping
out  Pro 9 Rug - Ivory - 4x6 ft          →  11/12, groundedness 2, PASS

in   Pet Water Fountain ... Rust ... 50oz    ("Rust" is the colour)
out  Pet Water Fountain, BPA Free Plastic, Rust Resistant, ...
                                          →  12/12, groundedness 2, PASS
```

The second is the clearest: a colour name was silently promoted into a durability
claim, and the judge scored it perfect.

This is the strongest result here, and it is not about loops or graphs. **An LLM
scoring its own output detected 0% of a failure mode a 40-line deterministic
check found immediately.** Anyone using LLM-as-judge for groundedness should
assume the same until they prove otherwise.

## 2. Fabrication: the difference is real, but smaller than the raw numbers

Raw rates are 8.4% (loop) vs 4.4% (graph). Part of that is an artifact of the
dataset: the `major_abbrev` style truncates words (`Double Wall` → `Doub`), and
both workflows reconstruct them. That is inference, not free invention, and it
affects both arms almost equally (20 loop, 18 graph).

Excluding it:

| | loop | graph |
|---|---|---|
| Flagged, all causes | 59 (8.4%) | 30 (4.4%) |
| From truncation reconstruction | 20 | 18 |
| **Genuine invention** | **39 (5.6%)** | **12 (1.8%)** |

Removing the artifact makes the gap wider in relative terms, roughly 3×. The
loop invents more because it produces more titles it should not have produced.

## 3. Both patterns detect ambiguity; only one acts before spending

The loop's escape hatch works. It routed **295 of 300** ambiguous inputs to human
review. It is not blind to ambiguity — it is 98.3% effective at spotting it.

But it decides *after* generating a candidate, and the 5 it let through produced
3 fabrications. The graph caught 300/300 and produced **zero** titles for
ambiguous inputs.

The classifier's cost-relevant accuracy: perfect recall on ambiguous inputs, 21
false positives out of 699 workable ones (97.9% binary accuracy). Those 21 are
work the loop did and the graph declined — they flatter the graph's token number
and are counted against it here.

MINOR↔MAJOR confusion was heavy (181 of 999) but costs nothing: both routes take
3 calls.

## 4. Break-even, now measured rather than extrapolated

| | tokens per title |
|---|---|
| Workable input: loop | 1,093 |
| Workable input: graph | 1,461 → **routing tax +368** |
| Ambiguous input: loop | 984 |
| Ambiguous input: graph | 331 → **routing saving −653** |

Break-even share of ambiguous inputs: **36.0%**. This dataset was 30%, so the
graph lost. The pilot extrapolated 38.7% from 10 titles; the measured figure at
n=1,000 is 36.0%.

Still conditional on: this model, these prompts, `PASS_TOTAL = 9`, and a loop
that barely iterates (see below).

## 5. The loop still did not really iterate

`avg_iterations = 1.02`. Even on a harder, longer dataset, 98% of titles passed
or bailed on the first attempt. The revise→re-evaluate cycle fired 23 times in
1,000 titles.

So this experiment **still has not tested a loop that thrashes** — the case that
motivates most concern about loop token usage. Condition B (`PASS_TOTAL = 12`) is
preregistered and unrun; it exists to change this.

## 6. Complexity

| Metric | loop | graph |
|---|---|---|
| Workflow lines of code | 52 | 80 |
| Distinct model prompts | 3 | 5 |
| Explicit decision points | 2 | 3 |

Descriptive, not combined. The graph costs 54% more workflow code and two extra
prompts, returns 16% more model calls and 5.8% more tokens, and roughly thirds
the genuine-invention rate. Whether that trade is worth it depends entirely on
what a fabricated product title costs you — which is a business question this
experiment cannot answer.

## Operational notes

- 41 responses failed to parse across 4,495 calls (0.9%); the retry recovered
  all but 2 titles, one per workflow, recorded as `ERROR` and excluded from
  rates. Every retry is counted as a real call with real tokens in both arms.
- A recurring parse failure was the model emitting reasoning between two JSON
  objects — *"Wait, I need to reconsider - I don't know the product type since
  it's not stated in the original title."* The model caught the ambiguity and
  broke the response format doing it.
- Graph wall clock 291s vs loop 265s at 12 workers.

## Limitations

- **One run.** No run-to-run variance estimate at this n. The 1,000 titles give
  within-run precision, not stability across runs.
- **n=1,000 but one task, one model, one prompt set.** Nothing here generalises
  to other tasks or models.
- **The 30% ambiguous ratio is a design choice** and sits just below the measured
  36% break-even. A different mix reverses the token result.
- **The audit is conservative by construction** — substring matching, plural
  forms and unit labels forgiven. It under-reports fabrication. The rates are
  floors, not estimates.
- **Ground-truth MINOR/MAJOR labels are mine** and the classifier disagreed on
  181 of them. Those disagreements are boundary judgements, not errors, and
  they do not affect cost.
