# Loop vs graph orchestration - measured results (Condition C)

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 1   Titles per run: 1000
- Max rewrite attempts per title: 4
- PASS rule: total >= 12/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 3575.0 | 3631.0 | +56.0 (+1.6%) |
| Input tokens | 1573558 | 1588373 | +14815 (+0.9%) |
| Output tokens | 347402 | 354311 | +6909 (+2.0%) |
| Total tokens | 1920960 | 1942684 | +21724 (+1.1%) |
| Avg iterations per title | 1.76 | 1.79 | +0.03 (+1.7%) |
| Avg calls per title | 3.58 | 3.63 | +0.05 (+1.4%) |
| PASS | 500.0 | 477.0 | -23.0 (-4.6%) |
| HUMAN_REVIEW | 303.0 | 303.0 | +0.0 (+0.0%) |
| FAIL_CAP | 194.0 | 218.0 | +24.0 (+12.4%) |
| JSON retry calls | 51.0 | 51.0 | +0.0 (+0.0%) |
| Errored titles | 3.0 | 2.0 | -1.0 (-33.3%) |
| Model time (s) | 6560.8 | 6144.8 | -416.0 (-6.3%) |
| Wall clock (s) | 554.5 | 518.3 | -36.2 (-6.5%) |
| Cost per run (calculated) | $6.6211 | $6.7199 | $+0.0987 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 400 | 4.0 | 4.0 | 2166.7 | 2183.4 |
| MAJOR | 300 | 4.5 | 4.7 | 2495.4 | 2559.1 |
| UNCLEAR | 300 | 2.1 | 2.1 | 1018.8 | 1005.3 |

## Graph node visits

**Executed** is how many times a node actually ran. **Planned** also
counts the node a title was routed to when it hit the attempt cap,
which never executed. Read the executed column.

| Node | Executed | Planned |
|---|---|---|
| `fix_consistency` | 601 | 790 |
| `done` | 0 | 477 |
| `human_review` | 0 | 303 |
| `fix_attribute_preservation` | 72 | 75 |
| `fix_searchability` | 53 | 66 |
| `fix_groundedness` | 54 | 64 |
| `fix_product_clarity` | 5 | 6 |
| `fix_readability` | 4 | 6 |

Executed fix-node runs: 789.


## Deterministic groundedness check

No model involved. A rewritten title may reorder, drop, recase or
repunctuate the input's words; a new content word that cannot be
traced to the input is flagged. These are POSSIBLE unsupported
additions, not confirmed errors: some flags are harmless wording
changes, and an unsupported claim that introduces no new word is
not detected.

| Metric | LOOP | GRAPH |
|---|---|---|
| Titles produced (not routed to human) | 694 | 695 |
| Flagged: contains an untraceable word | 61 | 50 |
| ...of those, passed the model rubric | 45 | 33 |
| Ambiguous inputs given a title | 5 | 2 |
| ...of those, flagged | 3 | 1 |
| **Audit-flagged rate** | 8.8% | 7.2% |

### LOOP - flagged examples (possible unsupported additions)

- **t0016** (MAJOR) added 'Razor' - FAIL_CAP, rubric 7/12, groundedness 2
  - in:  `CK Damascus Pattern Steel Cream Razo Full Chef Knife`
  - out: `Chef Knife CK Damascus Pattern Steel Cream Razor Full`
- **t0026** (MAJOR) added '2700K' - FAIL_CAP, rubric 9/12, groundedness 1
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LED Bulb Frosted Glass Forest Green 2700K`
- **t0043** (MAJOR) added 'Proof', 'Double', 'Wall', 'Sweat', 'Proof' - FAIL_CAP, rubric 11/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle - Tritan, Blush Pink, Leak Proof, Double Wall, Sweat Proof`
- **t0047** (MAJOR) added 'Vacuum', 'Insulated', 'Spill-Proof', 'Lid' - FAIL_CAP, rubric 11/12, groundedness 1
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `Stainless Steel Vacuum Insulated Travel Tumbler with Spill-Proof Lid, Sky Blue`
- **t0048** (MINOR) added 'Finish' - PASS, rubric 12/12, groundedness 2
  - in:  `SAUCEPAN ENAMELED CAST IRON GRAPHITE EVEN HEAT BASE DISHWASHER SAFE TEMPERED GLASS LID 6 QT`
  - out: `Enameled Cast Iron Saucepan with Graphite Finish, Even Heat Base, Dishwasher Safe, Tempered Glass Lid, 6 Qt`
- **t0074** (MAJOR) added 'Included' - PASS, rubric 12/12, groundedness 2
  - in:  `Super Soft Versatile Extra Durable Resistance Band Set Natural Latex Forest Green Snap Resistant Door Anchor Comfortable`
  - out: `Resistance Band Set - Natural Latex, Forest Green, Snap Resistant, Extra Durable, Super Soft, Comfortable, Door Anchor Included`
- **t0090** (UNCLEAR) added 'Rug' - PASS, rubric 12/12, groundedness 2
  - in:  `N120 - Silver - 2x3 ft - New Arrival`
  - out: `Rug N120 Silver New Arrival 2x3 ft`
- **t0092** (MAJOR) added 'Included' - FAIL_CAP, rubric 10/12, groundedness 2
  - in:  `Resistance Band Set for home and travel use with Natural Latex construction in Forest Green featuring Snap Resistant and Door Anchor`
  - out: `Resistance Band Set, Natural Latex, Snap Resistant, Door Anchor Included, Forest Green, For Home and Travel Use`

### GRAPH - flagged examples (possible unsupported additions)

- **t0016** (MAJOR) added 'Handle' - FAIL_CAP, rubric 10/12, groundedness 2
  - in:  `CK Damascus Pattern Steel Cream Razo Full Chef Knife`
  - out: `Chef Knife Damascus Pattern Steel Cream Handle`
- **t0026** (MAJOR) added '2700K' - FAIL_CAP, rubric 9/12, groundedness 1
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LED Bulb, Frosted Glass, Forest Green, 2700K`
- **t0043** (MAJOR) added 'Proof', 'Double', 'Wall', 'Sweat', 'Proof' - FAIL_CAP, rubric 11/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle Tritan, Blush Pink, Leak Proof, Double Wall, Sweat Proof`
- **t0047** (MAJOR) added 'Vacuum', 'Insulated', 'Spill-Proof', 'Lid' - FAIL_CAP, rubric 11/12, groundedness 1
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `Stainless Steel Vacuum Insulated Travel Tumbler with Spill-Proof Lid, Sky Blue`
- **t0073** (UNCLEAR) added 'Filter' - PASS, rubric 12/12, groundedness 2
  - in:  `Universal Fit HD2 - Recycled Paper - OEM`
  - out: `HD2 Filter - Universal Fit, Recycled Paper, OEM`
- **t0074** (MAJOR) added 'Included' - PASS, rubric 12/12, groundedness 2
  - in:  `Super Soft Versatile Extra Durable Resistance Band Set Natural Latex Forest Green Snap Resistant Door Anchor Comfortable`
  - out: `Resistance Band Set - Natural Latex, Snap Resistant, Extra Durable, Super Soft, Comfortable, Forest Green - Door Anchor Included`
- **t0113** (MAJOR) added '3-Piece' - PASS, rubric 12/12, groundedness 2
  - in:  `3 Qt 5 Qt 8 Qt 3pc Set Mixing Bowl Set Melamine Sky Blue Nesting`
  - out: `Melamine Nesting Mixing Bowl Set, Sky Blue - 3 Qt, 5 Qt, 8 Qt, 3-Piece Set`
- **t0197** (MINOR) added 'Included' - PASS, rubric 12/12, groundedness 2
  - in:  `Resistance Band Set - Natural Latex - Burgundy - Door Anchor - Carry Bag - Snap Resistant`
  - out: `Resistance Band Set - Natural Latex, Burgundy, Snap Resistant - Door Anchor, Carry Bag Included`

## Check vs evaluator, over every scored candidate

The table above covers final outputs only, which hides the cases where
the evaluator did object and the candidate was revised. This covers every
candidate the evaluator scored.

"Workable" means the evaluator judged the original title sufficient to
rewrite, so escalation candidates are excluded.

**Workable candidates**

| Metric | LOOP | GRAPH |
|---|---|---|
| Candidates scored | 1454 | 1484 |
| Flagged by the check | 134 | 116 |
| ...evaluator still scored groundedness 2 | 100 | 84 |
| ...evaluator scored below 2 | 34 | 32 |
| Not flagged, evaluator scored below 2 | 26 | 32 |
| **Flagged candidates the evaluator passed on groundedness** | 75% | 72% |

**All scored candidates**

| Metric | LOOP | GRAPH |
|---|---|---|
| Candidates scored | 1757 | 1787 |
| Flagged by the check | 177 | 166 |
| ...evaluator still scored groundedness 2 | 117 | 101 |
| ...evaluator scored below 2 | 60 | 65 |
| Not flagged, evaluator scored below 2 | 32 | 35 |
| **Flagged candidates the evaluator passed on groundedness** | 66% | 61% |

The bottom row is the disagreement rate. The row above it is the reverse
case: the evaluator objecting where the check saw nothing. Both happen, so
neither instrument dominates the other.

## Paired comparison: titles every workflow accepted

Same inputs, all workflows produced a title, so none is credited for
declining work. Flags are possible unsupported additions, not
confirmed errors.

| Metric | LOOP | GRAPH |
|---|---|---|
| Titles | 425 | 425 |
| Audit-flagged | 31 (7.3%) | 29 (6.8%) |
| Flagged in both | 23 | 23 |
| Flagged in this one only | 8 | 6 |

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
| 1 | loop | 3575 | 1573558 | 347402 | 1920960 | 500 | 303 | 194 |
| 1 | graph | 3631 | 1588373 | 354311 | 1942684 | 477 | 303 | 218 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.