# Shared evaluation rubric — FROZEN

Frozen 2026-09-19, before any workflow was run. Not modified after seeing results.

Both workflows use this rubric through the same evaluator prompt, byte-for-byte
identical. The evaluator receives only `(original, candidate)`. It is never told
which workflow produced the candidate, which iteration it is, or which route was
taken.

## Criteria — each scored 0, 1 or 2 (max 12)

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| `product_clarity` | Cannot tell what it is | Category clear, specific product not | Unambiguous |
| `attribute_preservation` | Dropped key attributes present in the original | Dropped minor ones | All meaningful attributes retained |
| `readability` | Unparseable / word salad | Understandable but awkward | Concise, well-ordered |
| `searchability` | Stripped useful search terms | Some lost | Key descriptive terms retained |
| `groundedness` | Invented an attribute not in the original | Ambiguous implication beyond the original | Every claim traceable to the original |
| `consistency` | No discernible structure | Partially follows the pattern | Follows `[product type] [key attributes] [size/quantity]` |

## Verdict rule

The verdict is computed in Python (`shared.verdict`), not by the model. The model
returns `original_sufficient` plus the six scores; the thresholds live in code.

```
HUMAN_REVIEW  if original_sufficient is false
PASS          if total >= 9  AND  groundedness == 2  AND  product_clarity >= 1
REVISE        otherwise
```

`groundedness == 2` and `product_clarity >= 1` are hard gates: a title that
invents an attribute cannot pass on total score alone.

## `original_sufficient`

Judged against the **original input**, never the candidate. A merely poor rewrite
must not trigger HUMAN_REVIEW. The test is: can a complete, accurate title be
written from the original alone, without inventing product information?

## Category definitions (used for the graph's routing and for ground-truth labels)

- **MINOR** — product identifiable; only wording, casing, punctuation or ordering need fixing.
- **MAJOR** — product identifiable from the title text alone, but structure is poor. Fixable by reordering and compressing what is already there. No new information required.
- **UNCLEAR** — core product cannot be confidently identified. Any complete rewrite would require inventing information.

## Caps

Maximum 3 rewrite attempts per title, in both workflows.
