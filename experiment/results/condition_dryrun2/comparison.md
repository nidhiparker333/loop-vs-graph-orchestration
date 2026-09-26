# Loop vs graph orchestration - measured results (Condition DRYRUN2)

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 1   Titles per run: 30
- Max rewrite attempts per title: 3
- PASS rule: total >= 9/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 64.0 | 73.0 | +9.0 (+14.1%) |
| Input tokens | 26474 | 28146 | +1672 (+6.3%) |
| Output tokens | 6041 | 6132 | +91 (+1.5%) |
| Total tokens | 32515 | 34278 | +1763 (+5.4%) |
| Avg iterations per title | 1.07 | 0.70 | -0.37 (-34.6%) |
| Avg calls per title | 2.13 | 2.43 | +0.30 (+14.1%) |
| PASS | 19.0 | 18.0 | -1.0 (-5.3%) |
| HUMAN_REVIEW | 10.0 | 12.0 | +2.0 (+20.0%) |
| FAIL_CAP | 1.0 | 0.0 | -1.0 (-100.0%) |
| JSON retry calls | 0.0 | 1.0 | +1.0 |
| Model time (s) | 98.0 | 107.2 | +9.2 (+9.4%) |
| Wall clock (s) | 15.9 | 16.0 | +0.1 (+0.6%) |
| Cost per run (calculated) | $0.1134 | $0.1176 | $+0.0043 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 11 | 2.0 | 2.8 | 1026.0 | 1341.9 |
| MAJOR | 8 | 2.5 | 3.9 | 1331.1 | 1982.2 |
| UNCLEAR | 11 | 2.0 | 1.0 | 961.8 | 332.6 |

## Graph classifier vs ground truth

A graph that over-routes to human review 'saves' tokens by doing less work.
Read this together with the token numbers.

| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |
|---|---|---|---|
| MINOR | 7 | 3 | 1 |
| MAJOR | 0 | 8 | 0 |
| UNCLEAR | 0 | 0 | 11 |

Classifier agreement with intended labels: 26/30 (87%)

Unrecognised classifier labels needing the MAJOR fallback: 0

### Cost-relevant accuracy: UNCLEAR vs not

MINOR and MAJOR both cost 3 calls, so confusing them does not change cost.
Only the UNCLEAR decision diverts work, so this is the split that matters
for the token comparison.

| | routed UNCLEAR | routed to work |
|---|---|---|
| intended UNCLEAR | 11 | 0 |
| intended MINOR/MAJOR | 1 | 18 |

Binary accuracy: 29/30 (96.7%)
- Missed ambiguous (sent to a rewrite anyway): 0
- Over-routed to human (work the loop did): 1 — inspect these; they inflate the graph's apparent saving.

## Orchestration complexity

Three descriptive metrics, reported side by side. Deliberately not
combined into a single score.

| Metric | LOOP | GRAPH |
|---|---|---|
| Workflow lines of code | 52 | 80 |
| Distinct model prompts | 3 | 5 |
| Explicit decision points | 2 | 3 |

LOC counting method, fixed before the code was written: non-blank,
non-comment lines in the workflow file only. Shared code is excluded
because it is identical for both. Docstrings count as lines.

## Per-run detail

| Run | Workflow | Calls | Input | Output | Total | PASS | HUMAN_REVIEW | FAIL_CAP |
|---|---|---|---|---|---|---|---|---|
| 1 | loop | 64 | 26474 | 6041 | 32515 | 19 | 10 | 1 |
| 1 | graph | 73 | 28146 | 6132 | 34278 | 18 | 12 | 0 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.