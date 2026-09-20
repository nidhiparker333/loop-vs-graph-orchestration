"""Approach B: decision-based routing.

    do -> evaluate -> decide what happens next.

The graph classifies first, so an insufficient input is detected *before* a
rewrite is spent on it. Note that the graph contains a loop: the revise/evaluate
cycle inside the MINOR and MAJOR branches is the same loop as Approach A,
entered conditionally.
"""
from __future__ import annotations

import shared

# Descriptive complexity metrics, counted before the run. See PREREGISTRATION.md.
DISTINCT_PROMPTS = 5  # CLASSIFY, LIGHT_REWRITE, RESTRUCTURE, REVISE, EVALUATE
DECISION_POINTS = 3  # (1) route MINOR/MAJOR/UNCLEAR  (2) verdict  (3) rewrite-attempt cap

ROUTES = ("MINOR", "MAJOR", "UNCLEAR")
FALLBACK_ROUTE = "MAJOR"  # used only if the classifier returns an unrecognised label


def run_title(item: dict, run_id: int) -> dict:
    original = item["title"]
    base = {"run_id": run_id, "workflow": "graph", "title_id": item["id"]}

    # --- decision point 1: route ---
    cls = shared.call_json(
        "CLASSIFY",
        shared.fill(shared.CLASSIFY, original=original),
        {**base, "route": None, "iteration": 0},
    )
    route_raw = str(cls.get("route", "")).strip().upper()
    route = route_raw if route_raw in ROUTES else FALLBACK_ROUTE

    result = {
        "title_id": item["id"],
        "workflow": "graph",
        "original": original,
        "route": route,
        "route_raw": route_raw,
        "route_fallback_used": route_raw not in ROUTES,
        "route_reason": cls.get("reason", ""),
        "versions": [],
        "evaluations": [],
        "iterations": 0,
        "outcome": "HUMAN_REVIEW",
        "final_title": None,
    }

    if route == "UNCLEAR":
        return result  # stop: one model call, no rewrite spent

    first_prompt = "LIGHT_REWRITE" if route == "MINOR" else "RESTRUCTURE"
    first_template = shared.LIGHT_REWRITE if route == "MINOR" else shared.RESTRUCTURE

    versions: list[str] = []
    evaluations: list[dict] = []

    for attempt in range(1, shared.MAX_REWRITE_ATTEMPTS + 1):
        ctx = {**base, "route": route, "iteration": attempt}

        if attempt == 1:
            raw = shared.call_json(
                first_prompt, shared.fill(first_template, original=original), ctx
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

    result.update(
        {
            "versions": versions,
            "evaluations": evaluations,
            "iterations": len(versions),
            "outcome": outcome,
            "final_title": None if outcome == "HUMAN_REVIEW" else versions[-1],
        }
    )
    return result
