# Loop vs graph orchestration - measured results (Condition C_DRYRUN)

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 1   Titles per run: 50
- Max rewrite attempts per title: 4
- PASS rule: total >= 12/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 162.0 | 186.0 | +24.0 (+14.8%) |
| Input tokens | 70663 | 81104 | +10441 (+14.8%) |
| Output tokens | 15615 | 18238 | +2623 (+16.8%) |
| Total tokens | 86278 | 99342 | +13064 (+15.1%) |
| Avg iterations per title | 1.60 | 1.84 | +0.24 (+15.0%) |
| Avg calls per title | 3.24 | 3.72 | +0.48 (+14.8%) |
| PASS | 27.0 | 22.0 | -5.0 (-18.5%) |
| HUMAN_REVIEW | 18.0 | 17.0 | -1.0 (-5.6%) |
| FAIL_CAP | 5.0 | 11.0 | +6.0 (+120.0%) |
| JSON retry calls | 2.0 | 2.0 | +0.0 (+0.0%) |
| Errored titles | 0.0 | 0.0 | +0.0 |
| Model time (s) | 292.9 | 328.9 | +36.0 (+12.3%) |
| Wall clock (s) | 30.4 | 33.5 | +3.1 (+10.2%) |
| Cost per run (calculated) | $0.2975 | $0.3446 | $+0.0471 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 18 | 3.7 | 3.8 | 1966.9 | 2043.9 |
| MAJOR | 14 | 4.1 | 5.4 | 2326.9 | 2941.1 |
| UNCLEAR | 18 | 2.1 | 2.4 | 1016.5 | 1187.5 |

## Graph node visits

Every entry into a named node, across all titles.

| Node | Times entered |
|---|---|
| `fix_consistency` | 34 |
| `done` | 22 |
| `human_review` | 17 |
| `fix_groundedness` | 11 |
| `fix_attribute_preservation` | 4 |
| `fix_searchability` | 3 |
| `fix_product_clarity` | 1 |

## Deterministic groundedness check

No model involved. A rewritten title may reorder, drop, recase or
repunctuate the input's words; a new content word that cannot be
traced to the input is flagged. These are POSSIBLE unsupported
additions, not confirmed errors: some flags are harmless wording
changes, and an unsupported claim that introduces no new word is
not detected.

| Metric | LOOP | GRAPH |
|---|---|---|
| Titles produced (not routed to human) | 32 | 33 |
| Flagged: contains an untraceable word | 5 | 5 |
| ...of those, passed the model rubric | 4 | 1 |
| Ambiguous inputs given a title | 0 | 1 |
| ...of those, flagged | 0 | 1 |
| **Audit-flagged rate** | 15.6% | 15.2% |

### LOOP - flagged examples (possible unsupported additions)

- **t0016** (MAJOR) added 'Razor' - PASS, rubric 12/12, groundedness 2
  - in:  `CK Damascus Pattern Steel Cream Razo Full Chef Knife`
  - out: `Chef Knife - Damascus Pattern Cream Razor Steel - Full Size`
- **t0026** (MAJOR) added '2700K' - FAIL_CAP, rubric 9/12, groundedness 2
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LED Bulb, LB, Frosted Glass, Forest Green, 2700K`
- **t0043** (MAJOR) added 'Proof', 'Double', 'Wall', 'Sweat', 'Proof' - PASS, rubric 12/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle - Tritan, Blush Pink, Leak Proof, Double Wall Insulated, Sweat Proof`
- **t0047** (MAJOR) added 'Vacuum', 'Insulated', 'Spill-Proof' - PASS, rubric 12/12, groundedness 2
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `Stainless Steel Vacuum Insulated Travel Tumbler Cup, Sky Blue, Spill-Proof`
- **t0048** (MINOR) added 'Finish' - PASS, rubric 12/12, groundedness 2
  - in:  `SAUCEPAN ENAMELED CAST IRON GRAPHITE EVEN HEAT BASE DISHWASHER SAFE TEMPERED GLASS LID 6 QT`
  - out: `Enameled Cast Iron Saucepan with Graphite Finish, Even Heat Base, Dishwasher Safe, Tempered Glass Lid, 6 Qt`

### GRAPH - flagged examples (possible unsupported additions)

- **t0016** (MAJOR) added 'Razor' - FAIL_CAP, rubric 10/12, groundedness 2
  - in:  `CK Damascus Pattern Steel Cream Razo Full Chef Knife`
  - out: `Chef Knife Damascus Pattern Steel Cream Razor Full`
- **t0026** (MAJOR) added '2700K' - FAIL_CAP, rubric 10/12, groundedness 1
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LED Bulb Frosted Glass Forest Green 2700K`
- **t0029** (UNCLEAR) added 'Rug' - PASS, rubric 12/12, groundedness 2
  - in:  `Pro 9 - Ivory - 4x6 ft - Fast Shipping`
  - out: `Pro 9 Rug - Ivory - 4x6 ft`
- **t0043** (MAJOR) added 'Proof', 'Double', 'Wall', 'Sweat', 'Proof' - FAIL_CAP, rubric 11/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle - Tritan, Blush Pink, Leak Proof, Double Wall, Sweat Proof`
- **t0047** (MAJOR) added 'Vacuum', 'Insulated', 'Spill-Proof', 'Lid' - FAIL_CAP, rubric 11/12, groundedness 1
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `Stainless Steel Vacuum Insulated Travel Tumbler with Spill-Proof Lid, Sky Blue`

## Check vs evaluator, over every scored candidate

The table above covers final outputs only, which hides the cases where
the evaluator did object and the candidate was revised. This covers every
candidate the evaluator scored.

"Workable" means the evaluator judged the original title sufficient to
rewrite, so escalation candidates are excluded.

**Workable candidates**

| Metric | LOOP | GRAPH |
|---|---|---|
| Candidates scored | 62 | 75 |
| Flagged by the check | 10 | 19 |
| ...evaluator still scored groundedness 2 | 9 | 8 |
| ...evaluator scored below 2 | 1 | 11 |
| Not flagged, evaluator scored below 2 | 0 | 0 |
| **Flagged candidates the evaluator passed on groundedness** | 90% | 42% |

**All scored candidates**

| Metric | LOOP | GRAPH |
|---|---|---|
| Candidates scored | 80 | 92 |
| Flagged by the check | 14 | 20 |
| ...evaluator still scored groundedness 2 | 11 | 8 |
| ...evaluator scored below 2 | 3 | 12 |
| Not flagged, evaluator scored below 2 | 0 | 0 |
| **Flagged candidates the evaluator passed on groundedness** | 79% | 40% |

The bottom row is the disagreement rate. The row above it is the reverse
case: the evaluator objecting where the check saw nothing. Both happen, so
neither instrument dominates the other.

## Paired comparison: titles every workflow accepted

Same inputs, all workflows produced a title, so none is credited for
declining work. Flags are possible unsupported additions, not
confirmed errors.

| Metric | LOOP | GRAPH |
|---|---|---|
| Titles | 21 | 21 |
| Audit-flagged | 1 (4.8%) | 0 (0.0%) |
| Flagged in both | 0 | 0 |
| Flagged in this one only | 1 | 0 |

Read alongside the accepted / human-review counts above: a workflow
that declines more work has fewer outputs available to flag.

## Orchestration complexity

Three descriptive metrics, reported side by side. Deliberately not
combined into a single score.

| Metric | LOOP | GRAPH |
|---|---|---|
| Workflow lines of code | 50 | 81 |
| Distinct model prompts | 3 | 3 |
| Explicit decision points | 2 | 3 |

LOC counting method, fixed before the code was written: non-blank,
non-comment lines in the workflow file only. Shared code is excluded
because it is identical for both. Docstrings count as lines.

## Per-run detail

| Run | Workflow | Calls | Input | Output | Total | PASS | HUMAN_REVIEW | FAIL_CAP |
|---|---|---|---|---|---|---|---|---|
| 1 | loop | 162 | 70663 | 15615 | 86278 | 27 | 18 | 5 |
| 1 | graph | 186 | 81104 | 18238 | 99342 | 22 | 17 | 11 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.