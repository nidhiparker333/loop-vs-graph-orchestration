"""Condition C, loop arm: one fixed path, every time.

    REWRITE -> EVALUATE -> FIX (all failed criteria at once) -> EVALUATE -> ...

No routing, no classifier, no extra exits. The only way out is PASS,
HUMAN_REVIEW, or the attempt cap.
"""
from __future__ import annotations

import prompts_condition_c as P
import shared

MAX_REWRITE_ATTEMPTS = P.MAX_REWRITE_ATTEMPTS

# Descriptive complexity metrics, counted before the run.
DISTINCT_PROMPTS = 3  # REWRITE, FIX, EVALUATE - all shared with the graph arm
DECISION_POINTS = 2  # (1) verdict PASS / HUMAN_REVIEW / continue  (2) attempt cap


def run_title(item: dict, run_id: int) -> dict:
    original = item["title"]
    base = {"run_id": run_id, "workflow": "loop", "title_id": item["id"], "route": None}
    versions: list[str] = []
    evaluations: list[dict] = []
    fixed_criteria: list[list[str]] = []

    for attempt in range(1, MAX_REWRITE_ATTEMPTS + 1):
        ctx = {**base, "iteration": attempt}

        if attempt == 1:
            raw = shared.call_json(
                "REWRITE", shared.fill(shared.REWRITE, original=original), ctx
            )
        else:
            failed = P.failed_criteria(evaluations[-1])
            fixed_criteria.append(failed)
            raw = shared.call_json(
                "FIX", P.fix_prompt(original, versions[-1], failed), ctx
            )

        candidate = str(raw.get("title", "")).strip()
        versions.append(candidate)

        ev = shared.evaluate(original, candidate, ctx)
        evaluations.append(ev)

        if ev["verdict"] in ("PASS", "HUMAN_REVIEW"):
            break

    last = evaluations[-1]["verdict"]
    outcome = last if last in ("PASS", "HUMAN_REVIEW") else "FAIL_CAP"

    return {
        "title_id": item["id"],
        "workflow": "loop",
        "condition": "c",
        "original": original,
        "route": None,
        "versions": versions,
        "evaluations": evaluations,
        "fixed_criteria": fixed_criteria,
        "iterations": len(versions),
        "outcome": outcome,
        "final_title": None if outcome == "HUMAN_REVIEW" else versions[-1],
    }
