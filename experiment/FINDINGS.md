# Findings

Written after the run. The measured numbers are in `results/comparison.md`; the
prediction made beforehand is in `PREREGISTRATION.md`, unedited.

## Answer to the research question

> Does giving an AI workflow explicit decision-based routing reduce unnecessary
> iteration and token usage without reducing output quality, compared with a more
> uniform iterative loop?

**On this dataset, with this model and these prompts: no.** The graph used
**+20% model calls** (24 vs 20) and **+8.8% total tokens** (10,697 vs 9,835),
for **identical quality outcomes** — both workflows produced 7 PASS and 3
HUMAN_REVIEW in every one of the three runs, with mean rubric scores of 11.33
(loop) and 11.19 (graph) out of 12.

The graph did what it was designed to do. It just didn't pay for itself here.

## The finding that matters most: the loop never iterated

Across all three runs, **every loop title completed in exactly one rewrite
attempt** (30/30 titles, `avg_iterations = 1.00`). The revise→re-evaluate cycle
never fired once.

This means the experiment did not test the scenario the research question was
really about. There was no "unnecessary iteration" to reduce, because there was
no iteration at all. `claude-sonnet-5` cleared a 9/12 bar on the first attempt
for every title it could work with.

So what the experiment actually compared was narrower than intended:

- one extra **classify** call on every title, versus
- one wasted **rewrite** call on ambiguous titles only

That is still a real comparison, and the result below follows from it. But it is
not evidence about loops that thrash, which is the case people usually have in
mind when they worry about loop token usage.

## Where each pattern won

| | Loop | Graph | |
|---|---|---|---|
| Workable title (MINOR/MAJOR) | 2.00 calls, 1,003.8 tok | 3.00 calls, 1,388.1 tok | graph **+384 tokens** |
| Ambiguous title (UNCLEAR) | 2.00 calls, 936.0 tok | 1.00 calls, 326.8 tok | graph **−609 tokens** |

The graph's routing worked exactly as designed on ambiguous inputs: **65% fewer
tokens**, because it never spent a rewrite on a title it was going to send to a
human anyway.

It just lost that gain seven times over on the titles that did need work.

## The structural asymmetry

**The graph's cost is unconditional. Its saving is conditional.**

Every item pays the classify tax, up front, whether or not routing helps. Only
*some* items — the ones routed away from work — pay it back.

### Derived break-even — Condition A only

From the measured per-title figures in this run:

| | Break-even share of ambiguous inputs |
|---|---|
| By total tokens | **38.7%** |
| By model calls | **50.0%** |
| **This dataset** | **30.0%** |

At 30% ambiguous inputs we were below the line, and the graph lost. Had the
dataset been ~40% ambiguous, the token result would have flipped.

**This number is specific to Condition A and does not generalise.** It is a
two-point extrapolation that assumes all of the following, every one of which
was true only of this run:

1. `claude-sonnet-5`, thinking disabled, these exact prompts.
2. `PASS_TOTAL = 9/12`. A different quality bar changes the per-title costs on
   both sides and therefore moves the line. (This is what Condition B tests.)
3. **The loop performed exactly one rewrite attempt per title.** A loop that
   iterates has a higher per-title cost, which moves the line in the graph's
   favour. The figure above is the break-even for a loop that does not loop.
4. Per-title costs scale linearly with the ambiguous share, and the three
   categories behave as they did here.
5. This dataset of 10 titles, whose difficulty distribution is a design choice.

It is a description of one measured configuration, not a rule of thumb, and it
should not be quoted without assumption 3 attached.

## Classifier accuracy, and a label I got wrong

Reported agreement with ground truth: **27/30 (90%)**. All three disagreements
are the same title, `t06`, in all three runs:

```
LED A19 E26 9W 5000K Daylight Dimmable 800lm 4 Pack
```

I labelled it MAJOR. The classifier called it MINOR every time, reasoning that
the product is clearly identifiable and the attributes just need reordering. It
then routed it to a light rewrite that scored **12/12 — a perfect score, the
best result of any title in the experiment.**

On the evidence, the classifier was right and my label was wrong. I have **not**
changed the frozen label, because the labels were fixed before the run and
editing them now would be exactly the kind of after-the-fact tuning this
experiment was set up to avoid. The honest reading is that 90% understates the
classifier, and the single disagreement was a disagreement about my taxonomy,
not a routing failure.

No unrecognised labels; the MAJOR fallback never fired.

## Prediction vs. outcome

Predicted net: **−2 to +4 model calls** for the graph. Actual: **+4** — the
pessimistic end of the range, and for exactly the reason the prediction named as
its downside branch: "or +1 if it does not." The loop's generic rewrite passed
MAJOR titles on the first attempt, so the graph's specialised RESTRUCTURE prompt
had nothing to recover.

The prediction's direction was right, its optimistic branch was wrong, and the
reason it was wrong (the loop not iterating) is the most interesting thing here.

## Complexity

| Metric | Loop | Graph |
|---|---|---|
| Workflow lines of code | 52 | 80 (+54%) |
| Distinct model prompts | 3 | 5 |
| Explicit decision points | 2 | 3 |

Reported side by side, not combined into a score. On this dataset the graph cost
54% more workflow code and two additional prompts to maintain, and returned
worse efficiency at equal quality. The added complexity did not earn its place
**here**. That is a statement about this dataset at 30% ambiguous inputs, not
about the pattern.

## Stability

Run-to-run variance was very low and did not threaten the result. Model calls
were identical across all three runs (20 loop / 24 graph). Total tokens varied by
102 (loop) and 63 (graph) — roughly 1%, against an 863-token gap between the
workflows. The gap is ~8x the spread, so it is not noise.

## Limitations

- **n=10, one task, one model, one set of prompts.** No statistical power, no
  significance testing. Illustrative, not a study.
- **The loop never iterated**, so this says nothing about loops that thrash —
  the case that motivates most concern about loop token usage.
- **The 30% ambiguous ratio was my design choice** and is the single biggest
  lever on the outcome. The break-even table above exists so a reader can
  reweight to their own mix.
- **Generator and evaluator are the same model**, so pass rates are not an
  independent quality measure. This affects both arms equally.
- **Thinking was disabled** on both arms. With adaptive thinking on, output
  tokens would be larger and more variable.
- **The evaluator's own calls dominate the budget.** Both workflows spend most
  of their tokens on evaluation, which is shared — so the orchestration
  difference is measured against a large common baseline.

## Worth investigating, not done here

- Raise the PASS threshold (or use a weaker model) until the loop actually
  iterates, then re-run. This is the experiment that would answer the original
  question about runaway iteration.
- Vary the ambiguous-input share across 10/30/50% and plot the crossover
  directly instead of deriving it from two points.
- Make the classifier cheaper (a smaller model, or a short deterministic
  pre-filter) and see how far it moves the break-even line.
