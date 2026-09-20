# Loop vs graph orchestration - measured results

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 1   Titles per run: 3
- Max rewrite attempts per title: 3
- PASS rule: total >= 9/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

**SMOKE RUN - not the real experiment.**

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 6.0 | 7.0 | +1.0 (+16.7%) |
| Input tokens | 2377 | 2558 | +181 (+7.6%) |
| Output tokens | 557 | 505 | -52 (-9.3%) |
| Total tokens | 2934 | 3063 | +129 (+4.4%) |
| Avg iterations per title | 1.00 | 0.67 | -0.33 (-33.0%) |
| Avg calls per title | 2.00 | 2.33 | +0.33 (+16.5%) |
| PASS | 2.0 | 2.0 | +0.0 (+0.0%) |
| HUMAN_REVIEW | 1.0 | 1.0 | +0.0 (+0.0%) |
| FAIL_CAP | 0.0 | 0.0 | +0.0 |
| JSON retry calls | 0.0 | 0.0 | +0.0 |
| Cost per run (calculated) | $0.0103 | $0.0102 | $-0.0002 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 1 | 2.0 | 3.0 | 984.0 | 1331.0 |
| MAJOR | 1 | 2.0 | 3.0 | 1018.0 | 1406.0 |
| UNCLEAR | 1 | 2.0 | 1.0 | 932.0 | 326.0 |

## Graph classifier vs ground truth

A graph that over-routes to human review 'saves' tokens by doing less work.
Read this together with the token numbers.

| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |
|---|---|---|---|
| MINOR | 1 | 0 | 0 |
| MAJOR | 0 | 1 | 0 |
| UNCLEAR | 0 | 0 | 1 |

Classifier agreement with intended labels: 3/3 (100%)

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
| 1 | loop | 6 | 2377 | 557 | 2934 | 2 | 1 | 0 |
| 1 | graph | 7 | 2558 | 505 | 3063 | 2 | 1 | 0 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.