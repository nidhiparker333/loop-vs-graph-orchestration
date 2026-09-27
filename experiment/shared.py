"""Shared layer: model client, prompts, frozen rubric thresholds, token logging.

Every model call in this experiment goes through `_call`, so token usage is
captured in exactly one place and cannot diverge between the two workflows.
"""
from __future__ import annotations

import json
import re
import time

import anthropic

MODEL = "claude-sonnet-5"
THINKING = {"type": "disabled"}
MAX_TOKENS = 1024
MAX_REWRITE_ATTEMPTS = 3

# Frozen rubric thresholds. See rubric.md.
PASS_TOTAL = 9
CRITERIA = [
    "product_clarity",
    "attribute_preservation",
    "readability",
    "searchability",
    "groundedness",
    "consistency",
]

# max_retries raised from the default 2 for the 1,000-title run: concurrency
# makes 429s likely. Infrastructure only, identical for both workflows.
_client = anthropic.Anthropic(max_retries=6)

# Every model call made during the process, in order.
CALL_LOG: list[dict] = []
# The same records indexed by (workflow, title_id), so a finished title's calls
# can be checkpointed to disk immediately.
CALLS_BY_TITLE: dict[tuple, list] = {}


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------

SYSTEM = (
    "You are a careful e-commerce catalog assistant. You never invent product "
    "attributes that are not present in the input. You respond with the "
    "requested JSON object and nothing else."
)

_STRUCTURE = "Target structure: [product type] [key attributes] [size/quantity]"
_NO_INVENT = "Do not add any information that is not present in the original title."

# --- used by the loop only ---
REWRITE = """Improve this e-commerce product title.

Original title:
{original}

{structure}
{no_invent}

Respond with JSON only: {{"title": "<the improved title>"}}"""

# --- used by both workflows, identical text ---
REVISE = """Revise this e-commerce product title to fix the specific problems listed.

Original title:
{original}

Current version:
{candidate}

Criteria that failed: {failed}
Critique: {critique}

{structure}
{no_invent}

Respond with JSON only: {{"title": "<the revised title>"}}"""

# --- used by both workflows, identical text ---
EVALUATE = """Evaluate a rewritten e-commerce product title.

Original title:
{original}

Rewritten title:
{candidate}

STEP 1 - Assess the ORIGINAL title only.
Can a complete, accurate product title be written from the original alone,
without inventing product information that is not present in it? Set
"original_sufficient" to false only if the core product cannot be confidently
identified from the original title. This judgement is about the ORIGINAL title,
never about the rewritten one.

STEP 2 - Score the REWRITTEN title on each criterion. 0 = fails,
1 = partially meets, 2 = meets.

product_clarity        0 cannot tell what it is | 1 category clear, product not | 2 unambiguous
attribute_preservation 0 dropped key attributes | 1 dropped minor ones | 2 all retained
readability            0 word salad | 1 awkward | 2 concise and well-ordered
searchability          0 stripped search terms | 1 some lost | 2 key terms retained
groundedness           0 invented an attribute | 1 implies beyond the original | 2 fully traceable
consistency            0 no structure | 1 partial | 2 follows [product type] [key attributes] [size/quantity]

Respond with JSON only:
{{"original_sufficient": true or false,
  "scores": {{"product_clarity": 0, "attribute_preservation": 0, "readability": 0,
             "searchability": 0, "groundedness": 0, "consistency": 0}},
  "failed_criteria": ["..."],
  "critique": "<one sentence naming the single most important fix>"}}"""

# --- used by the graph only ---
CLASSIFY = """Classify what this e-commerce product title needs.

Title:
{original}

MINOR   - the product is clearly identifiable; only wording, capitalisation,
          punctuation or word order need fixing.
MAJOR   - the product is identifiable from the title text alone, but the title
          needs restructuring or compressing. No new information is required.
UNCLEAR - the core product cannot be confidently identified from the title. Any
          complete rewrite would require inventing information.

Respond with JSON only: {{"route": "MINOR" or "MAJOR" or "UNCLEAR", "reason": "<one short sentence>"}}"""

LIGHT_REWRITE = """Lightly edit this e-commerce product title. It is already close to correct.

Original title:
{original}

Fix only wording, capitalisation, punctuation and word order. Preserve the
existing content and structure.
{no_invent}
{structure}

Respond with JSON only: {{"title": "<the edited title>"}}"""

RESTRUCTURE = """Restructure this e-commerce product title. The necessary information is
present but poorly organised.

Original title:
{original}

Reorder and compress the existing information into a clear title. Remove filler
and marketing language.
{no_invent}
{structure}

Respond with JSON only: {{"title": "<the restructured title>"}}"""


def fill(template: str, **kw) -> str:
    return template.format(structure=_STRUCTURE, no_invent=_NO_INVENT, **kw)


# --------------------------------------------------------------------------
# Model call + token logging
# --------------------------------------------------------------------------

_FENCE = re.compile(r"^\s*`{3}(?:json)?\s*|\s*`{3}\s*$")


MAX_PARSE_ATTEMPTS = 3


class ParseFailure(RuntimeError):
    """Raised when a call could not be parsed after MAX_PARSE_ATTEMPTS."""


# Raw text of every unparseable response, for diagnosis. Not model calls -
# those are already in CALL_LOG.
PARSE_FAILURES: list[dict] = []


def reset_run_state() -> None:
    """Clear every per-run accumulator. Must be called at the start of each run.

    CALL_LOG, CALLS_BY_TITLE and PARSE_FAILURES all accumulate for the life of
    the process. Clearing only CALL_LOG leaves the other two carrying the
    previous run's records, which would let run 2 attribute run 1's calls and
    parse failures to itself. Resetting all three together is the only safe
    form; keep them in one function so a future accumulator cannot be missed.
    """
    CALL_LOG.clear()
    CALLS_BY_TITLE.clear()
    PARSE_FAILURES.clear()


def _loads(text: str):
    s = _FENCE.sub("", text.strip())
    if not s:
        raise ValueError("empty response text")
    return json.loads(s)


def _call(prompt_name: str, user: str, ctx: dict) -> str:
    """The single place the API is touched. Logs API-reported token usage."""
    t0 = time.time()
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking=THINKING,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    u = resp.usage
    text = "".join(b.text for b in resp.content if b.type == "text")
    rec = (
        {
            **ctx,
            "prompt": prompt_name,
            "input_tokens": u.input_tokens,
            "output_tokens": u.output_tokens,
            "total_tokens": u.input_tokens + u.output_tokens,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
            "stop_reason": resp.stop_reason,
            "latency_s": round(time.time() - t0, 3),
        }
    )
    CALL_LOG.append(rec)
    CALLS_BY_TITLE.setdefault((ctx.get("workflow"), ctx.get("title_id")), []).append(rec)
    return text


def call_json(prompt_name: str, user: str, ctx: dict):
    """Call the model and parse JSON, retrying up to MAX_PARSE_ATTEMPTS.

    Every attempt is logged as a real model call with real tokens, identically
    for both workflows. Raises ParseFailure if all attempts fail; the caller
    decides what to do, so one bad response cannot abort a whole run.
    """
    attempt_user = user
    last = ""
    for attempt in range(1, MAX_PARSE_ATTEMPTS + 1):
        name = prompt_name if attempt == 1 else f"{prompt_name}_retry{attempt - 1}"
        text = _call(name, attempt_user, ctx)
        try:
            return _loads(text)
        except (json.JSONDecodeError, ValueError) as exc:
            last = text
            PARSE_FAILURES.append(
                {**ctx, "prompt": name, "attempt": attempt,
                 "error": str(exc), "raw": text[:500]}
            )
            attempt_user = user + (
                "\n\nYour previous response was not valid JSON. Respond with the "
                "JSON object only - no surrounding text, no markdown fences, no "
                "explanation."
            )
    raise ParseFailure(
        f"{prompt_name}: {MAX_PARSE_ATTEMPTS} attempts failed; last raw={last[:200]!r}"
    )


# --------------------------------------------------------------------------
# Shared evaluator
# --------------------------------------------------------------------------


def verdict(original_sufficient: bool, scores: dict) -> str:
    """Frozen verdict rule. Computed in code, not by the model. See rubric.md."""
    if not original_sufficient:
        return "HUMAN_REVIEW"
    total = sum(scores[c] for c in CRITERIA)
    if total >= PASS_TOTAL and scores["groundedness"] == 2 and scores["product_clarity"] >= 1:
        return "PASS"
    return "REVISE"


def evaluate(original: str, candidate: str, ctx: dict) -> dict:
    """Identical for both workflows. Sees only (original, candidate)."""
    raw = call_json("EVALUATE", fill(EVALUATE, original=original, candidate=candidate), ctx)
    scores = {c: int(raw.get("scores", {}).get(c, 0)) for c in CRITERIA}
    suff = bool(raw.get("original_sufficient", True))
    return {
        "original_sufficient": suff,
        "scores": scores,
        "total": sum(scores.values()),
        "failed_criteria": raw.get("failed_criteria", []),
        "critique": raw.get("critique", ""),
        "verdict": verdict(suff, scores),
    }
