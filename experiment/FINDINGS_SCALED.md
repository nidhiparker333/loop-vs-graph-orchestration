# Findings — 1,000 titles, Condition A (PASS ≥ 9/12)

One run, 1,000 titles, `claude-sonnet-5`, thinking disabled. 4,495 model calls,
$7.49, ~9 minutes wall clock. Raw data in `results/condition_scaled/`.

The 10-title pilot (`FINDINGS.md`) stands unedited as a separate, earlier result.

## Read this first: what is being compared

Two **complete workflows**, not one variable.

- **Loop** — a single generic rewrite prompt, then evaluate, then revise and
  re-evaluate until PASS, HUMAN_REVIEW, or the 3-attempt cap.
- **Graph** — a classifier call, then one of two *specialised* rewrite prompts
  (light edit or restructure) chosen by the route, then the same evaluate /
  revise cycle. Ambiguous inputs stop at the classifier.

They differ in at least three ways at once: the presence of a routing step, the
number of prompts (3 vs 5), and the wording of the rewrite instruction itself.
Any difference in results is a difference between these two workflows as built.

**This work does not isolate a causal benefit of graph routing.** Attributing
the outcome to routing specifically would require holding the prompts constant,
which was not done.

## Headline

| | loop | graph | |
|---|---|---|---|
| Model calls | 2,078 | 2,417 | +16.3% |
| Total tokens | 1,060,219 | 1,121,956 | +5.8% |
| Cost | $3.69 | $3.81 | +$0.12 |
| PASS | 699 | 676 | |
| HUMAN_REVIEW | 300 | 322 | |
| Audit-flagged outputs | 59 of 699 (8.4%) | 30 of 677 (4.4%) | |
| Ambiguous inputs sent to human | 295/300 | 300/300 | |
| Workflow LOC | 52 | 80 | +54% |

The graph workflow used more calls and more tokens, produced fewer accepted
titles, sent more work to human review, and had fewer of its outputs flagged by
the word-level audit. These point in different directions. There is no winner.

## 1. Every audit-flagged output passed the model rubric

89 outputs contained at least one content word the deterministic check could not
trace to the input. **All 89 passed the model rubric** — 59/59 loop, 30/30 graph
— and every one scored `groundedness = 2`, the criterion defined as "every claim
traceable to the original".

```
in   Pro 9 - Ivory - 4x6 ft - Fast Shipping
out  Pro 9 Rug - Ivory - 4x6 ft              →  11/12, groundedness 2, PASS

in   Pet Water Fountain ... Rust ... 50oz     ("Rust" is the colour)
out  Pet Water Fountain, BPA Free Plastic, Rust Resistant, ...
                                              →  12/12, groundedness 2, PASS
```

The second reads as a colour name being carried into a durability claim.

**What this supports:** on these 89 outputs, the model rubric and a word-level
check disagreed completely, and the rubric never objected.

**What it does not support:** a claim that the rubric detects "0% of
fabrications". The 89 are outputs the *audit* flagged, and the audit is a
heuristic (below), not an oracle. Outputs the audit did not flag were not
independently checked, so the rubric's true miss rate is unmeasured. What can be
said is that the two checks disagreed on every case where the audit objected,
and that the disagreement is one-directional.

## 2. What the audit measures, and what it does not

`audit.py` flags a content word in the output that cannot be found in the input
by substring match, after lowercasing, stripping non-alphanumerics, forgiving
simple plurals, and skipping function words and a list of unit/measure labels
(`size`, `pack`, `inch`, …).

It is a **heuristic for possible unsupported additions**, not a validated
measure of factual error. Specifically:

- **Some flags are harmless.** `Slate Grey` → `Slate Grey Finish` adds a word
  that asserts little. These are counted as flags.
- **Some unsupported claims go unflagged.** Reordering words can change meaning
  without adding any; the audit cannot see that. Anything it misses is invisible
  here.
- **The allowlist is a judgement call.** Adding unit/measure words moved the
  loop's flag rate from 30.0% to 10.0% on a 30-title sample. That is a large
  swing driven by one design decision, documented in `audit.py`.

Flag counts are therefore reported as **audit flags**, not as confirmed errors
and not as a fabrication rate.

### One exclusion, stated openly

The `major_abbrev` generator style truncates words (`Double Wall` → `Doub`), and
both workflows expand them back. That is reconstruction of something the
generator removed, and it affects both arms nearly equally.

| | loop | graph |
|---|---|---|
| Flagged, all causes | 59 (8.4%) | 30 (4.4%) |
| From `major_abbrev` truncation | 20 | 18 |
| Remaining flags | 39 (5.6%) | 12 (1.8%) |

Both rows are reported. Excluding the truncation cases widens the relative gap
rather than narrowing it. Whether that exclusion is appropriate is a judgement
a reader may disagree with; the unexcluded numbers are right there.

## 3. Output quality and human-review burden, together

Reporting flags alone would flatter whichever workflow refused more work. The
two move together and belong in one table.

| | loop | graph |
|---|---|---|
| Titles accepted (PASS) | 699 | 676 |
| Sent to human review | 300 | 322 |
| Ended at the attempt cap | 0 | 1 |
| Errored (unparseable after 3 tries) | 1 | 1 |

The graph accepted 23 fewer titles and sent 22 more to a human.

### Paired comparison: the 674 titles both workflows accepted

The cleanest like-for-like view. Same inputs, both workflows produced a title,
so neither is credited for declining work.

| | loop | graph |
|---|---|---|
| Titles | 674 | 674 |
| Audit-flagged | **54 (8.0%)** | **29 (4.3%)** |
| Flagged in both | 23 | 23 |
| Flagged in one only | 31 | 6 |

On identical inputs that both workflows chose to answer, the loop's outputs were
flagged roughly twice as often. These are audit flags, not confirmed errors.

Whether the graph's 22 extra human reviews are worth its 25 fewer flags depends
on the relative cost of a review and of an unsupported claim reaching a catalog.
Those costs are not measured here and no figure is assumed for them.

## 4. Both workflows detect ambiguity; they act at different points

The loop's escape hatch works: it routed **295 of 300** ambiguous inputs to human
review. It is not blind to ambiguity. It decides after generating a candidate,
and 3 of the 5 it let through were audit-flagged.

The graph's classifier caught 300/300, with 21 false positives out of 699
workable inputs (97.9% binary accuracy on the UNCLEAR/not split). Those 21 are
work the loop did and the graph declined; they are counted against the graph in
the table above.

MINOR↔MAJOR confusion was heavy (181 of 999) but does not change cost, since
both routes take three calls.

## 5. Token break-even, conditional on this setup

| | tokens per title |
|---|---|
| Workable input, loop | 1,093 |
| Workable input, graph | 1,461 → routing overhead **+368** |
| Ambiguous input, loop | 984 |
| Ambiguous input, graph | 331 → routing saving **−653** |

Break-even share of ambiguous inputs: **36.0%**. This dataset was 30%, below the
line, which is why the graph cost more.

This figure holds **only for this dataset, this model, this prompt set, and
`PASS_TOTAL = 9`**, with a loop that revised 22 of 1,000 titles. It is a
description of one measured configuration. A loop that iterates more raises its
own per-title cost and moves the line. Do not carry 36% to another setting.

## 6. Complexity

| Metric | loop | graph |
|---|---|---|
| Workflow lines of code | 52 | 80 |
| Distinct model prompts | 3 | 5 |
| Explicit decision points | 2 | 3 |

Descriptive, deliberately not combined into a score.

## Limits

These bound every number above.

1. **One run at n=1,000.** No run-to-run variance estimate. Within-run precision
   is good; stability across runs is unmeasured.
2. **Synthetic titles, generated by the author** (`generate_titles.py`), with a
   **designed 30% ambiguous share** that sits just below the measured 36%
   break-even. A different mix reverses the token result.
3. **One model, one prompt set, one task.** Nothing here transfers to other
   models or tasks without re-measuring.
4. **The loop revised only 22 of 1,000 titles** (`avg_iterations = 1.02`). The
   case that motivates most concern about loop cost — a loop that iterates hard
   — is untested. Condition B (`PASS_TOTAL = 12`) is preregistered and unrun.
5. **The audit is a heuristic**, conservative by construction, with an allowlist
   chosen by the author. Flags are not confirmed errors; misses are invisible.
6. **Two workflows differ in several ways at once.** No causal claim about
   routing.
7. **The same model generates and evaluates.** PASS and HUMAN_REVIEW counts
   depend on that evaluator, which section 1 gives reason to distrust.
8. **MINOR/MAJOR ground-truth labels are the author's**; the classifier
   disagreed on 181 of 999. Those are boundary judgements and do not affect cost.

## Operational notes

- 41 of 4,495 responses (0.9%) failed to parse. Retries recovered all but two
  titles, one per workflow, recorded as `ERROR` and excluded from rates. Every
  retry is counted as a real call with real tokens in both arms.
- A recurring parse failure was the model emitting prose between two JSON
  objects — *"Wait, I need to reconsider - I don't know the product type since
  it's not stated in the original title."*
- Wall clock at 12 workers: loop 265s, graph 292s.
