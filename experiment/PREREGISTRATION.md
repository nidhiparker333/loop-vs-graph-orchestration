# Preregistration

Written and committed **before the experiment was run**. Not edited afterwards.
If the results contradict anything here, the results stand and this file remains
as written.

## Research question

Does giving an AI workflow explicit decision-based routing reduce unnecessary
iteration and token usage without reducing output quality, compared with a more
uniform iterative loop?

Scoped to this task, dataset, model, prompts and rubric. This is not a claim
about orchestration patterns in general.

## Setup

- Model: `claude-sonnet-5`, `thinking: {"type": "disabled"}`, no `temperature`
  set (non-default values return 400 on this model), no `effort` set.
- Same model, same 10 inputs, same rubric, same evaluator prompt for both arms.
- 3 full runs, preserved separately.
- Maximum 3 rewrite attempts per title in both arms.

## What differs between the arms

Exactly one thing: **when** ambiguity is detected.

Both workflows can detect an insufficient input, with the same criteria and the
same evaluator. The loop detects it *after* spending a rewrite call. The graph
detects it *before*, via a classifier.

## Prediction (recorded before running)

Per-title model calls:

| Category | Loop | Graph | Graph vs loop |
|---|---|---|---|
| UNCLEAR (3 titles) | 2 | 1 | -1 each |
| MINOR passing first try (4 titles) | 2 | 3 | +1 each |
| MAJOR (3 titles) | 4 if the generic rewrite fails once | 3 if the targeted restructure passes | -1 each, or +1 if it does not |

**Net predicted range for the graph: between -2 and +4 model calls.**

The graph may well come out **behind** on model calls. Tokens could still favour
it, because the classify call is small (one label plus a short reason) while the
loop's wasted rewrite on an UNCLEAR title generates a full title.

I do not know which way this lands.

## Stated in advance

- If the spread across the 3 runs is wider than the gap between the two
  workflows, that is the finding, and it will be reported as such.
- The dataset is 3/10 UNCLEAR. That ratio is a design choice and is the single
  biggest lever on the outcome. Per-category results are reported so a reader
  can reweight.
- Generator and evaluator are the same model. Absolute pass rates are therefore
  not an independent measure of quality. This affects both arms equally.
- n=10. No statistical power, no significance claims.
- A graph that over-routes to human review "saves" tokens by doing less work.
  Classifier accuracy against the ground-truth labels is reported alongside the
  token numbers, and they must be read together.

## Complexity reporting

Three descriptive metrics, reported side by side, deliberately **not** combined
into a single score:

1. Workflow lines of code (non-blank, non-comment, workflow file only)
2. Number of distinct model prompts
3. Number of explicit decision points

Counting method fixed before the code was written.
