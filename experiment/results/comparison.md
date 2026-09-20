# Loop vs graph orchestration - measured results

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 3   Titles per run: 10
- Max rewrite attempts per title: 3
- PASS rule: total >= 9/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 20.0 | 24.0 | +4.0 (+20.0%) |
| Input tokens | 8058 (8053-8061) | 8926 (8924-8929) | +868 (+10.8%) |
| Output tokens | 1777 (1734-1828) | 1772 (1745-1808) | -5 (-0.3%) |
| Total tokens | 9835 (9787-9889) | 10697 (10669-10732) | +863 (+8.8%) |
| Avg iterations per title | 1.00 | 0.70 | -0.30 (-30.0%) |
| Avg calls per title | 2.00 | 2.40 | +0.40 (+20.0%) |
| PASS | 7.0 | 7.0 | +0.0 (+0.0%) |
| HUMAN_REVIEW | 3.0 | 3.0 | +0.0 (+0.0%) |
| FAIL_CAP | 0.0 | 0.0 | +0.0 |
| JSON retry calls | 0.0 | 0.0 | +0.0 |
| Cost per run (calculated) | $0.0339 | $0.0356 | $+0.0017 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 4 | 2.0 | 3.0 | 976.1 | 1347.3 |
| MAJOR | 3 | 2.0 | 3.0 | 1040.8 | 1442.6 |
| UNCLEAR | 3 | 2.0 | 1.0 | 936.0 | 326.8 |

## Graph classifier vs ground truth

A graph that over-routes to human review 'saves' tokens by doing less work.
Read this together with the token numbers.

| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |
|---|---|---|---|
| MINOR | 12 | 0 | 0 |
| MAJOR | 3 | 6 | 0 |
| UNCLEAR | 0 | 0 | 9 |

Classifier agreement with intended labels: 27/30 (90%)

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
| 1 | loop | 20 | 8061 | 1828 | 9889 | 7 | 3 | 0 |
| 1 | graph | 24 | 8924 | 1745 | 10669 | 7 | 3 | 0 |
| 2 | loop | 20 | 8059 | 1769 | 9828 | 7 | 3 | 0 |
| 2 | graph | 24 | 8929 | 1762 | 10691 | 7 | 3 | 0 |
| 3 | loop | 20 | 8053 | 1734 | 9787 | 7 | 3 | 0 |
| 3 | graph | 24 | 8924 | 1808 | 10732 | 7 | 3 | 0 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.