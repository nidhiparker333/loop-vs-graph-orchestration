# Loop vs graph orchestration - measured results (Condition DRYRUN)

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
| Model calls | 66.0 | 79.0 | +13.0 (+19.7%) |
| Input tokens | 27863 | 30915 | +3052 (+11.0%) |
| Output tokens | 6194 | 6648 | +454 (+7.3%) |
| Total tokens | 34057 | 37563 | +3506 (+10.3%) |
| Avg iterations per title | 1.10 | 0.80 | -0.30 (-27.3%) |
| Avg calls per title | 2.20 | 2.63 | +0.43 (+19.5%) |
| PASS | 24.0 | 23.0 | -1.0 (-4.2%) |
| HUMAN_REVIEW | 6.0 | 7.0 | +1.0 (+16.7%) |
| FAIL_CAP | 0.0 | 0.0 | +0.0 |
| JSON retry calls | 0.0 | 1.0 | +1.0 |
| Model time (s) | 104.0 | 115.6 | +11.6 (+11.2%) |
| Wall clock (s) | 11.9 | 13.2 | +1.3 (+10.9%) |
| Cost per run (calculated) | $0.1177 | $0.1283 | $+0.0106 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 12 | 2.2 | 3.1 | 1121.3 | 1516.8 |
| MAJOR | 12 | 2.3 | 3.0 | 1233.8 | 1446.8 |
| UNCLEAR | 6 | 2.0 | 1.0 | 966.0 | 333.5 |

## Graph classifier vs ground truth

A graph that over-routes to human review 'saves' tokens by doing less work.
Read this together with the token numbers.

| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |
|---|---|---|---|
| MINOR | 7 | 5 | 0 |
| MAJOR | 3 | 8 | 1 |
| UNCLEAR | 0 | 0 | 6 |

Classifier agreement with intended labels: 21/30 (70%)

Unrecognised classifier labels needing the MAJOR fallback: 0

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
| 1 | loop | 66 | 27863 | 6194 | 34057 | 24 | 6 | 0 |
| 1 | graph | 79 | 30915 | 6648 | 37563 | 23 | 7 | 0 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.