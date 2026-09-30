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

## 1. The two checks disagree, in both directions

### First, a figure that means less than it looks

An earlier version of this document reported that **all 89 audit-flagged final
outputs passed the model rubric with `groundedness = 2`**, and treated that as
the headline.

It is accurate, and it follows directly from the PASS rule, which requires
`groundedness == 2`. A title that reached PASS could not have scored anything
else on that criterion — so "every flagged output that passed scored 2"
restates the pass rule rather than measuring the evaluator. Final outputs
are also a survivor population: any candidate the evaluator did object to was
revised, and only what survived reached the end.

The figure is kept here because it was published, with its limitation stated.

### The population that does answer the question

`audit.py` now cross-tabulates the check against the evaluator over **every
candidate the evaluator actually scored** — all 1,025 loop and 701 graph
`(version, evaluation)` pairs, not just final outputs.

Restricted to candidates the evaluator judged workable (it considered the
original title sufficient to rewrite):

| | loop | graph |
|---|---|---|
| Candidates scored | 725 | 700 |
| Flagged by the check | 71 | 40 |
| ...evaluator still scored groundedness 2 | 59 | 30 |
| ...evaluator scored below 2 | 12 | 10 |
| **Flagged candidates the evaluator passed** | **83%** | **75%** |

So the evaluator passed **83%** of the loop's flagged candidates and **75%** of
the graph's on the very criterion the check was testing. That is a real
disagreement rate, measured on a population where the answer was not fixed in
advance.

### The disagreement runs both ways

The evaluator also scored `groundedness < 2` on candidates the check did **not**
flag: **10 loop and 7 graph** within the workable scope, **16 loop and 7 graph**
across all scored candidates. Those are cases the evaluator caught and the check
missed — unsupported implications that introduce no new word, which this check
is structurally blind to.

Neither instrument dominates the other. The evaluator misses most of what the
check flags; the check misses things the evaluator catches. Two examples of the
first kind:

```
in   Pro 9 - Ivory - 4x6 ft - Fast Shipping
out  Pro 9 Rug - Ivory - 4x6 ft              →  11/12, groundedness 2, PASS

in   Pet Water Fountain ... Rust ... 50oz     ("Rust" is the colour)
out  Pet Water Fountain, BPA Free Plastic, Rust Resistant, ...
                                              →  12/12, groundedness 2, PASS
```

The second reads as a colour name being carried into a durability claim.

**What this supports:** on candidates the evaluator judged workable, it scored
full marks on groundedness for 83% (loop) and 75% (graph) of the candidates a
word-level check flagged as containing an untraceable word.

**What it does not support:** a claim that the rubric detects "0% of
fabrications". The flagged set is what the *check* objected to, and the check is
a heuristic (below), not an oracle — some of its flags are harmless. Nor is the
disagreement one-directional: the evaluator objected on candidates the check
passed (10 loop, 7 graph in scope; 16 and 7 overall). Neither instrument is a
ground truth for the other, and the true error rate of either is unmeasured
here. What can be said is that they disagree often, mostly in one direction, and
that using only the model's own score would have let most flagged candidates
through.

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

### Where the accepted-title gap comes from

Pairing by title: **25** titles the loop accepted, the graph did not; **2** went
the other way. Of those 25, **22 were routed UNCLEAR by the classifier** —
escalated before a rewrite was attempted:

| | count | |
|---|---|---|
| Routed UNCLEAR, intended label MINOR or MAJOR | **17** | the classifier over-escalated genuinely workable titles |
| Routed UNCLEAR, intended label UNCLEAR | **5** | truly ambiguous titles that the **loop accepted** |
| Not a routing case (one each: human review, error, attempt cap) | 3 | |

So the gap is mostly the classifier being conservative, and the two columns cut
opposite ways: 17 titles the graph arguably should have processed, and 5 the
loop arguably should not have. Neither count is large against 1,000.

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

### Are the paired differences bigger than chance?

Exact McNemar tests on the discordant pairs — the only titles that carry
information about a difference:

| Comparison | discordant | p |
|---|---|---|
| Audit flags, on the 674 both accepted | 31 loop-only vs 6 graph-only | **4.1 × 10⁻⁵** |
| Accepted (PASS), on all 1,000 | 25 loop-only vs 2 graph-only | **5.7 × 10⁻⁶** |

Both differences are far too lopsided to be chance **within this run**. That is
all this establishes: it shows the workflows really did behave differently on
these 1,000 titles, not that the effect would hold at the same size on a second
run, a different dataset, or a different model. Run-to-run stability is
unmeasured — there was only one run.

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
6. **The audit's `STRUCTURAL` allowlist was tuned on 30-title dry runs drawn
   from this same dataset.** It was not held out. Adding it moved a dry-run loop
   rate from 30.0% to 10.0%, so the tuning materially moved the numbers, and it
   was tuned by looking at data from the population it is now applied to.
7. **`titles_1000.json` was edited after those dry runs** (commit `cf05f15`,
   narrowing implausible size pools and adding token-set dedup). The dataset the
   allowlist was tuned against is therefore not byte-identical to the one that
   was finally run.
8. **The audit ignores tokens under 3 characters**, so a changed two-digit
   number — `9W` becoming `12W`, a quantity edited from 4 to 6 — would not be
   flagged. Checked against the saved run: **no output introduced a number
   absent from its input**, so this blind spot did not fire here. It remains a
   real gap for any future run.
9. **Two workflows differ in several ways at once.** No causal claim about
   routing.
10. **The same model generates and evaluates.** PASS and HUMAN_REVIEW counts
   depend on that evaluator, which section 1 gives reason to distrust.
11. **MINOR/MAJOR ground-truth labels are the author's**; the classifier
   disagreed on 181 of 999. Those are boundary judgements and do not affect cost.

## Operational notes

- 41 of 4,495 responses (0.9%) failed to parse. Retries recovered all but two
  titles, one per workflow, recorded as `ERROR` and excluded from rates. Every
  retry is counted as a real call with real tokens in both arms.
- A recurring parse failure was the model emitting prose between two JSON
  objects — *"Wait, I need to reconsider - I don't know the product type since
  it's not stated in the original title."*
- Wall clock at 12 workers: loop 265s, graph 292s.
