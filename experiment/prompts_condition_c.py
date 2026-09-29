"""Condition C prompt source. Both arms import from here, so the text is shared.

Condition A confounded control flow with prompting: the graph had a classifier
and two specialised rewrite prompts the loop never saw. Condition C removes that.
Both arms use the same REWRITE, the same EVALUATE, and the same FIX template
built from the same per-criterion instructions.

The only difference between the arms is *which* failed criteria get passed to
FIX: the loop passes all of them at once, the graph passes the single
highest-priority one. When exactly one criterion has failed, the two arms emit
byte-identical prompts - `test_run_state.py` asserts this.
"""
from __future__ import annotations

import shared

MAX_REWRITE_ATTEMPTS = 4
PASS_TOTAL = 12

# Routing order for the graph's edge function. Groundedness first because an
# unsupported claim is the failure that matters most; readability last because
# it is the most cosmetic. The loop never consults this for routing - it only
# uses it to order the instructions it sends, so both arms word things the same.
PRIORITY = [
    "groundedness",
    "product_clarity",
    "attribute_preservation",
    "searchability",
    "consistency",
    "readability",
]

CRITERION_INSTRUCTION = {
    "groundedness": (
        "Remove any word or claim that is not supported by the original title. "
        "Do not infer attributes the original does not state."
    ),
    "product_clarity": (
        "Make the product itself unambiguous, using only what the original "
        "title already says."
    ),
    "attribute_preservation": (
        "Restore meaningful attributes from the original title that the current "
        "version dropped."
    ),
    "searchability": (
        "Retain the descriptive terms a shopper would search for, taken from "
        "the original title."
    ),
    "consistency": (
        "Reorder into the pattern [product type] [key attributes] "
        "[size/quantity]."
    ),
    "readability": (
        "Tighten the wording so it reads cleanly, without adding or removing "
        "information."
    ),
}

FIX = """Revise this e-commerce product title to fix the specific problems listed.

Original title:
{original}

Current version:
{candidate}

Fix the following:
{instructions}

{structure}
{no_invent}

Respond with JSON only: {{"title": "<the revised title>"}}"""


def failed_criteria(evaluation: dict) -> list[str]:
    """Criteria scoring below 2, in PRIORITY order.

    Taken from the numeric scores, never the model's free-text
    `failed_criteria` list, which is unvalidated and sometimes disagrees with
    the scores it returned alongside it.
    """
    scores = evaluation["scores"]
    return [c for c in PRIORITY if scores.get(c, 0) < 2]


def fix_prompt(original: str, candidate: str, criteria: list[str]) -> str:
    """Build the FIX prompt. Identical in both arms for the same criteria."""
    ordered = [c for c in PRIORITY if c in criteria]
    instructions = "\n".join(f"- {CRITERION_INSTRUCTION[c]}" for c in ordered)
    return shared.fill(
        FIX, original=original, candidate=candidate, instructions=instructions
    )
