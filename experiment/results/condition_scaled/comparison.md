# Loop vs graph orchestration - measured results (Condition SCALED)

- Model: `claude-sonnet-5`, thinking disabled, no temperature set (400 on this model)
- Runs: 1   Titles per run: 1000
- Max rewrite attempts per title: 3
- PASS rule: total >= 9/12, groundedness == 2, product_clarity >= 1
- Token counts are API-reported (`usage`), not estimates.
- Pricing: $2.0/MTok in, $10.0/MTok out. Source: platform.claude.com/docs/en/about-claude/pricing, verified 2026-09-19

## Headline

Mean across runs, with (min-max) where runs differed.

| Metric | LOOP | GRAPH | Difference |
|---|---|---|---|
| Model calls | 2078.0 | 2417.0 | +339.0 (+16.3%) |
| Input tokens | 864545 | 926786 | +62241 (+7.2%) |
| Output tokens | 195674 | 195170 | -504 (-0.3%) |
| Total tokens | 1060219 | 1121956 | +61737 (+5.8%) |
| Avg iterations per title | 1.02 | 0.70 | -0.32 (-31.4%) |
| Avg calls per title | 2.08 | 2.42 | +0.34 (+16.3%) |
| PASS | 699.0 | 676.0 | -23.0 (-3.3%) |
| HUMAN_REVIEW | 300.0 | 322.0 | +22.0 (+7.3%) |
| FAIL_CAP | 0.0 | 1.0 | +1.0 |
| JSON retry calls | 26.0 | 13.0 | -13.0 (-50.0%) |
| Errored titles | 1.0 | 1.0 | +0.0 (+0.0%) |
| Model time (s) | 3163.1 | 3481.0 | +317.9 (+10.1%) |
| Wall clock (s) | 264.9 | 291.5 | +26.6 (+10.0%) |
| Cost per run (calculated) | $3.6858 | $3.8053 | $+0.1194 |

## Per category

Mean model calls and total tokens per title, by intended label.
Labels are ground truth, never shown to either workflow.

| Category | n | LOOP calls | GRAPH calls | LOOP tokens | GRAPH tokens |
|---|---|---|---|---|---|
| MINOR | 400 | 2.1 | 3.0 | 1080.9 | 1435.9 |
| MAJOR | 300 | 2.1 | 3.1 | 1108.9 | 1494.7 |
| UNCLEAR | 300 | 2.0 | 1.0 | 984.0 | 330.6 |

## Graph classifier vs ground truth

A graph that over-routes to human review 'saves' tokens by doing less work.
Read this together with the token numbers.

| Intended | Routed MINOR | Routed MAJOR | Routed UNCLEAR |
|---|---|---|---|
| MINOR | 251 | 133 | 15 |
| MAJOR | 48 | 246 | 6 |
| UNCLEAR | 0 | 0 | 300 |

Classifier agreement with intended labels: 797/999 (80%)

Unrecognised classifier labels needing the MAJOR fallback: 0

### Cost-relevant accuracy: UNCLEAR vs not

MINOR and MAJOR both cost 3 calls, so confusing them does not change cost.
Only the UNCLEAR decision diverts work, so this is the split that matters
for the token comparison.

| | routed UNCLEAR | routed to work |
|---|---|---|
| intended UNCLEAR | 300 | 0 |
| intended MINOR/MAJOR | 21 | 678 |

Binary accuracy: 978/999 (97.9%)
- Missed ambiguous (sent to a rewrite anyway): 0
- Over-routed to human (work the loop did): 21 — inspect these; they inflate the graph's apparent saving.

## Deterministic groundedness audit

No model involved. A rewritten title may reorder, drop, recase or
repunctuate the input's words; introducing a new content word is a
fabrication. Conservative: few false positives, some real misses.

| Metric | LOOP | GRAPH |
|---|---|---|
| Titles produced (not routed to human) | 699 | 677 |
| Containing an invented word | 59 | 30 |
| ...and PASSed the rubric anyway | 59 | 30 |
| Ambiguous inputs given a title | 5 | 0 |
| ...of those, ungrounded | 3 | 0 |
| **Fabrication rate** | 8.4% | 4.4% |

### LOOP — flagged examples

- **t0026** (MAJOR) invented '2700K' - PASS, rubric 10/12, groundedness 2
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LED Bulb, LB Frosted Glass, Forest Green, 2700K`
- **t0029** (UNCLEAR) invented 'Rug' - PASS, rubric 11/12, groundedness 2
  - in:  `Pro 9 - Ivory - 4x6 ft - Fast Shipping`
  - out: `Pro 9 Rug - Ivory - 4x6 ft`
- **t0043** (MAJOR) invented 'Proof', 'Double', 'Wall', 'Sweat', 'Proof' - PASS, rubric 11/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle - Tritan, Blush Pink, Leak Proof, Double Wall, Sweat Proof, IWB`
- **t0047** (MAJOR) invented 'Vacuum', 'Insulated', 'Spill-Proof', 'Lid' - PASS, rubric 12/12, groundedness 2
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `Stainless Steel Vacuum Insulated Travel Tumbler with Spill-Proof Lid, Sky Blue`
- **t0074** (MAJOR) invented 'Included' - PASS, rubric 11/12, groundedness 2
  - in:  `Super Soft Versatile Extra Durable Resistance Band Set Natural Latex Forest Green Snap Resistant Door Anchor Comfortable`
  - out: `Resistance Band Set - Natural Latex, Snap Resistant, Extra Durable, Super Soft, Comfortable, Forest Green - Door Anchor Included`
- **t0093** (MINOR) invented 'Included' - PASS, rubric 12/12, groundedness 2
  - in:  `resistance band set natural latex lavender 5 levels carry bag snap resistant`
  - out: `Resistance Band Set - Natural Latex, Lavender, Snap Resistant, Carry Bag Included - 5 Levels`
- **t0160** (MINOR) invented 'Included' - PASS, rubric 12/12, groundedness 2
  - in:  `5 Levels Carry Bag Snap Resistant 4 Pack Terracotta Resistance Band Set Natural Latex`
  - out: `Resistance Band Set Natural Latex Terracotta Snap Resistant 5 Levels - 4 Pack Carry Bag Included`
- **t0186** (MAJOR) invented 'Finish' - PASS, rubric 10/12, groundedness 2
  - in:  `Floor Lamp for home and travel use with Brushed Brass construction in Slate Grey featuring Weighted Base available in 58"`
  - out: `Floor Lamp with Brushed Brass Construction, Slate Grey Finish, Weighted Base - 58"`

### GRAPH — flagged examples

- **t0026** (MAJOR) invented '2700K' - PASS, rubric 12/12, groundedness 2
  - in:  `LB Frosted Glass Forest Green 2700 LED Bulb`
  - out: `LB LED Bulb Frosted Glass Forest Green 2700K`
- **t0043** (MAJOR) invented 'Double', 'Wall', 'Proof' - PASS, rubric 12/12, groundedness 2
  - in:  `IWB Tritan Blush Pink Leak Doub Swea Insulated Water Bottle`
  - out: `Insulated Water Bottle Tritan Double Wall Leak Proof Blush Pink`
- **t0047** (MAJOR) invented 'Vacuum' - PASS, rubric 12/12, groundedness 2
  - in:  `TT Stainless Steel Sky Blue Cup Spil Vacu Travel Tumbler`
  - out: `TT Stainless Steel Vacuum Travel Tumbler Cup - Sky Blue`
- **t0223** (MAJOR) invented 'Weighted', 'Sturdy' - PASS, rubric 11/12, groundedness 2
  - in:  `CSP Sisal Rope Lavender Weig Incl Stur Cat Scratching Post`
  - out: `Cat Scratching Post with Sisal Rope, Lavender, Weighted, Sturdy`
- **t0273** (MAJOR) invented 'Knurl' - PASS, rubric 12/12, groundedness 2
  - in:  `AD Cast Iron Terracotta Quic Knur Adjustable Dumbbell`
  - out: `Cast Iron Adjustable Dumbbell - Terracotta, Quick Knurl, AD`
- **t0295** (MINOR) invented 'Resistant' - PASS, rubric 12/12, groundedness 2
  - in:  `Pet  Water  Fountain  BPA Free Plastic  Rust  Ultra Quiet Pump  50oz  Set of 4`
  - out: `Pet Water Fountain, BPA Free Plastic, Rust Resistant, Ultra Quiet Pump, 50oz, Set of 4`
- **t0331** (MAJOR) invented 'Ultra' - PASS, rubric 11/12, groundedness 2
  - in:  `PWF Ceramic Mustard Carb LED Ultr Pet Water Fountain`
  - out: `PWF Ceramic Pet Water Fountain, Mustard, LED, Ultra Carb`
- **t0347** (MAJOR) invented 'Stain', 'Resistant' - PASS, rubric 12/12, groundedness 2
  - in:  `AR Low Pile Polypropylene Olive Stai Pet Non Area Rug`
  - out: `AR Low Pile Polypropylene Area Rug - Olive, Pet Stain Resistant`

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
| 1 | loop | 2078 | 864545 | 195674 | 1060219 | 699 | 300 | 0 |
| 1 | graph | 2417 | 926786 | 195170 | 1121956 | 676 | 322 | 1 |

Interpretation, limitations and the preregistered prediction: see
`PREREGISTRATION.md` and the README.