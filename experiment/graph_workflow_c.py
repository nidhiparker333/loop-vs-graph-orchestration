"""Condition C, graph arm: an explicit node graph over the same prompts.

    REWRITE -> EVALUATE -> edge function picks the next node -> EVALUATE -> ...

The graph is literal here: `NODES` is a dict of named nodes and `next_node` is
the single edge function that chooses among them from the latest evaluation.
Each fix node repairs exactly one criterion and returns to EVALUATE.

It has no advantage the loop lacks. Same REWRITE, same EVALUATE, same FIX
template, same per-criterion instruction text, same attempt cap, and the same
single exit to human review. The only difference from the loop arm is that it
fixes the highest-priority failure alone instead of all failures at once.
"""
from __future__ import annotations

import prompts_condition_c as P
import shared

MAX_REWRITE_ATTEMPTS = P.MAX_REWRITE_ATTEMPTS

# Descriptive complexity metrics, counted before the run.
DISTINCT_PROMPTS = 3  # REWRITE, FIX, EVALUATE - identical text to the loop arm
DECISION_POINTS = 3  # (1) sufficiency  (2) pass  (3) which criterion to route to

TERMINAL = ("human_review", "done")


def _fix_node(criterion: str):
    """A node that repairs one criterion and hands back a new candidate."""

    def node(original: str, candidate: str, ctx: dict) -> str:
        raw = shared.call_json(
            "FIX", P.fix_prompt(original, candidate, [criterion]), ctx
        )
        return str(raw.get("title", "")).strip()

    node.criterion = criterion
    node.__name__ = f"fix_{criterion}"
    return node


# The graph. Eight named nodes: six repairs and two terminals.
NODES: dict = {f"fix_{c}": _fix_node(c) for c in P.PRIORITY}
NODE_NAMES = tuple(NODES) + TERMINAL


def next_node(evaluation: dict) -> str:
    """The single edge function: latest evaluation -> name of the next node.

    Human review is reachable only through `original_sufficient = false`, the
    same exit the loop arm has. There is no extra escape hatch here.
    """
    if not evaluation["original_sufficient"]:
        return "human_review"
    if evaluation["verdict"] == "PASS":
        return "done"
    failed = P.failed_criteria(evaluation)
    if not failed:
        return "done"  # unreachable at PASS_TOTAL = 12; guard, not a path
    return f"fix_{failed[0]}"


def run_title(item: dict, run_id: int) -> dict:
    original = item["title"]
    base = {"run_id": run_id, "workflow": "graph", "title_id": item["id"]}
    versions: list[str] = []
    evaluations: list[dict] = []
    visited: list[str] = []

    ctx = {**base, "route": None, "iteration": 1}
    raw = shared.call_json("REWRITE", shared.fill(shared.REWRITE, original=original), ctx)
    candidate = str(raw.get("title", "")).strip()
    versions.append(candidate)
    evaluations.append(shared.evaluate(original, candidate, ctx))

    node = next_node(evaluations[-1])
    visited.append(node)

    while node not in TERMINAL and len(versions) < MAX_REWRITE_ATTEMPTS:
        ctx = {**base, "route": node, "iteration": len(versions) + 1}
        candidate = NODES[node](original, versions[-1], ctx)
        versions.append(candidate)
        evaluations.append(shared.evaluate(original, candidate, ctx))
        node = next_node(evaluations[-1])
        visited.append(node)

    if node == "human_review":
        outcome = "HUMAN_REVIEW"
    elif node == "done":
        outcome = "PASS" if evaluations[-1]["verdict"] == "PASS" else "FAIL_CAP"
    else:
        outcome = "FAIL_CAP"  # left the loop on the attempt cap

    return {
        "title_id": item["id"],
        "workflow": "graph",
        "condition": "c",
        "original": original,
        "route": visited[0] if visited else None,
        "visited_nodes": visited,
        "versions": versions,
        "evaluations": evaluations,
        "iterations": len(versions),
        "outcome": outcome,
        "final_title": None if outcome == "HUMAN_REVIEW" else versions[-1],
    }
