"""Approach A: uniform iterative loop.

    do -> evaluate -> improve -> repeat until PASS, HUMAN_REVIEW, or the cap.

Every title enters the same process. The loop has no routing: it learns that an
input is insufficient only *after* it has already spent a rewrite call on it.
"""
from __future__ import annotations

import shared

# Descriptive complexity metrics, counted before the run. See PREREGISTRATION.md.
DISTINCT_PROMPTS = 3  # REWRITE, REVISE, EVALUATE
DECISION_POINTS = 2  # (1) verdict PASS / HUMAN_REVIEW / REVISE  (2) rewrite-attempt cap


def run_title(item: dict, run_id: int) -> dict:
    original = item["title"]
    base = {"run_id": run_id, "workflow": "loop", "title_id": item["id"], "route": None}
    versions: list[str] = []
    evaluations: list[dict] = []

    for attempt in range(1, shared.MAX_REWRITE_ATTEMPTS + 1):
        ctx = {**base, "iteration": attempt}

        if attempt == 1:
            raw = shared.call_json(
                "REWRITE", shared.fill(shared.REWRITE, original=original), ctx
            )
        else:
            prev = evaluations[-1]
            raw = shared.call_json(
                "REVISE",
                shared.fill(
                    shared.REVISE,
                    original=original,
                    candidate=versions[-1],
                    failed=", ".join(prev["failed_criteria"]) or "none",
                    critique=prev["critique"],
                ),
                ctx,
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
        "original": original,
        "route": None,
        "versions": versions,
        "evaluations": evaluations,
        "iterations": len(versions),
        "outcome": outcome,
        "final_title": None if outcome == "HUMAN_REVIEW" else versions[-1],
    }
