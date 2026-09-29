"""Deterministic groundedness check. No model involved.

The same model generates titles and scores them, and that evaluator has been
observed both catching an untraceable product noun and praising one. So this
check does not ask a model anything: a rewritten title may reorder, drop,
recase or repunctuate the input's words, and a content word that cannot be
traced back to the input is flagged.

This is a HEURISTIC FOR POSSIBLE UNSUPPORTED ADDITIONS, not a validated measure
of factual error:

  * a flag is not a confirmed error - "Slate Grey" -> "Slate Grey Finish" adds
    a word that asserts very little, and is still flagged
  * an unsupported claim that introduces no new word, such as a reordering that
    changes meaning, is invisible to this check
  * the STRUCTURAL allowlist below is a judgement call that materially moves
    the counts

Conservative by design - few false positives, at the cost of real misses:

  * comparison is on letters and digits only, so "Slip-On" == "slip on" and
    "32oz" == "32 oz" never flag
  * a token counts as grounded if it appears anywhere in the input as a
    substring, which forgives compounding and splitting
  * simple plural and -es forms are forgiven
  * function words and tokens shorter than 3 characters are skipped

Run standalone against a finished run directory:

    python audit.py results/condition_scaled/run_1
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "on", "of", "to", "by",
    "at", "from", "its", "it", "this", "that", "these", "those", "is", "are",
    "was", "were", "be", "been", "as", "into", "per", "via", "plus", "each",
}

# Unit and measure labels. Writing "Size XS" where the input said "XS", or
# "12 inch" where it said 12", labels an existing attribute rather than
# asserting a new one. Allowlisting these keeps the check conservative: it
# under-reports rather than inflating the count with formatting noise.
STRUCTURAL = {
    "size", "sizes", "pack", "count", "set", "piece", "pieces", "pc", "pcs",
    "color", "colors", "colour", "colours", "inch", "inches", "foot", "feet",
    "ounce", "ounces", "quart", "quarts", "pound", "pounds", "liter", "liters",
    "litre", "litres", "watt", "watts", "lumen", "lumens", "gram", "grams",
}

_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def invented_words(original: str, output: str) -> list[str]:
    """Content words in the output that cannot be traced to the input.

    Returns candidates for review, not confirmed errors. See the module
    docstring for what this misses and what it over-flags.
    """
    if not output:
        return []
    hay = _norm(original)
    found: list[str] = []
    for tok in _WORD.findall(output):
        low = tok.lower()
        if low in STOPWORDS or low in STRUCTURAL or len(low) < 3:
            continue
        n = _norm(low)
        if not n or n in hay:
            continue
        if n.endswith("s") and n[:-1] in hay:
            continue
        if n.endswith("es") and n[:-2] in hay:
            continue
        found.append(tok)
    return found


def audit_results(results: list[dict], labels: dict) -> dict:
    """Attach per-title audit fields and return aggregate counts per workflow."""
    agg: dict[str, dict] = {}
    for r in results:
        inv = invented_words(r["original"], r.get("final_title") or "")
        r["invented_words"] = inv
        r["grounded"] = not inv
        wf = r["workflow"]
        a = agg.setdefault(wf, {
            "produced": 0, "ungrounded": 0, "approved_ungrounded": 0,
            "unclear_produced": 0, "unclear_ungrounded": 0, "examples": [],
        })
        if not r.get("final_title"):
            continue
        is_unclear = labels.get(r["title_id"]) == "UNCLEAR"
        a["produced"] += 1
        a["unclear_produced"] += is_unclear
        if inv:
            a["ungrounded"] += 1
            a["unclear_ungrounded"] += is_unclear
            if r["outcome"] == "PASS":
                a["approved_ungrounded"] += 1
            if len(a["examples"]) < 8:
                a["examples"].append({
                    "title_id": r["title_id"],
                    "label": labels.get(r["title_id"], "?"),
                    "original": r["original"],
                    "final_title": r["final_title"],
                    "invented": inv,
                    "outcome": r["outcome"],
                    "rubric_total": r["evaluations"][-1]["total"] if r["evaluations"] else None,
                    "rubric_groundedness": (
                        r["evaluations"][-1]["scores"]["groundedness"] if r["evaluations"] else None
                    ),
                })
    return agg


def audit_candidates(results: list[dict]) -> dict:
    """Cross-tabulate the check against the evaluator over EVERY scored candidate.

    `audit_results` only sees each title's final output. That hides the cases
    where the evaluator did object - it objected, the candidate was revised, and
    only the survivor reached the end. This looks at every (version, evaluation)
    pair the evaluator actually scored, so the two checks can be compared on the
    same population.

    Two scopes are reported, because they answer different questions:
      "all"      - every scored candidate
      "workable" - only candidates whose evaluator judged the ORIGINAL title
                   sufficient, i.e. cases where a rewrite was the right call
                   at all. Escalation candidates are excluded.
    """
    out: dict[str, dict] = {}
    for r in results:
        wf = r["workflow"]
        for scope in ("all", "workable"):
            out.setdefault(wf, {}).setdefault(scope, {
                "candidates": 0, "flagged": 0, "flagged_g2": 0,
                "flagged_glt2": 0, "unflagged_glt2": 0, "unflagged_g2": 0,
            })
        for version, ev in zip(r.get("versions", []), r.get("evaluations", [])):
            flagged = bool(invented_words(r["original"], version))
            g2 = ev["scores"]["groundedness"] == 2
            scopes = ["all"] + (["workable"] if ev.get("original_sufficient") else [])
            for scope in scopes:
                a = out[wf][scope]
                a["candidates"] += 1
                a["flagged"] += flagged
                a["flagged_g2"] += flagged and g2
                a["flagged_glt2"] += flagged and not g2
                a["unflagged_glt2"] += (not flagged) and not g2
                a["unflagged_g2"] += (not flagged) and g2
    return out


def render_candidates(agg: dict, workflows=("loop", "graph")) -> list[str]:
    w: list[str] = []
    w.append("## Check vs evaluator, over every scored candidate\n")
    w.append("The table above covers final outputs only, which hides the cases where")
    w.append("the evaluator did object and the candidate was revised. This covers every")
    w.append("candidate the evaluator scored.\n")
    w.append('"Workable" means the evaluator judged the original title sufficient to')
    w.append("rewrite, so escalation candidates are excluded.\n")
    for scope, title in (("workable", "Workable candidates"), ("all", "All scored candidates")):
        w.append(f"**{title}**\n")
        w.append("| Metric | " + " | ".join(wf.upper() for wf in workflows) + " |")
        w.append("|---" * (len(workflows) + 1) + "|")
        rows = [
            ("Candidates scored", "candidates"),
            ("Flagged by the check", "flagged"),
            ("...evaluator still scored groundedness 2", "flagged_g2"),
            ("...evaluator scored below 2", "flagged_glt2"),
            ("Not flagged, evaluator scored below 2", "unflagged_glt2"),
        ]
        for label, key in rows:
            w.append(f"| {label} | " + " | ".join(
                str(agg.get(wf, {}).get(scope, {}).get(key, 0)) for wf in workflows) + " |")
        rate = []
        for wf in workflows:
            a = agg.get(wf, {}).get(scope, {})
            f, g = a.get("flagged", 0), a.get("flagged_g2", 0)
            rate.append(f"{g / f * 100:.0f}%" if f else "-")
        w.append("| **Flagged candidates the evaluator passed on groundedness** | "
                 + " | ".join(rate) + " |")
        w.append("")
    w.append("The bottom row is the disagreement rate. The row above it is the reverse")
    w.append("case: the evaluator objecting where the check saw nothing. Both happen, so")
    w.append("neither instrument dominates the other.")
    w.append("")
    return w


def render(agg: dict, workflows=("loop", "graph")) -> list[str]:
    w: list[str] = []
    w.append("## Deterministic groundedness check\n")
    w.append("No model involved. A rewritten title may reorder, drop, recase or")
    w.append("repunctuate the input's words; a new content word that cannot be")
    w.append("traced to the input is flagged. These are POSSIBLE unsupported")
    w.append("additions, not confirmed errors: some flags are harmless wording")
    w.append("changes, and an unsupported claim that introduces no new word is")
    w.append("not detected.\n")
    w.append("| Metric | " + " | ".join(wf.upper() for wf in workflows) + " |")
    w.append("|---" * (len(workflows) + 1) + "|")
    rows = [
        ("Titles produced (not routed to human)", "produced"),
        ("Flagged: contains an untraceable word", "ungrounded"),
        ("...of those, passed the model rubric", "approved_ungrounded"),
        ("Ambiguous inputs given a title", "unclear_produced"),
        ("...of those, flagged", "unclear_ungrounded"),
    ]
    for label, key in rows:
        w.append(f"| {label} | " + " | ".join(str(agg.get(wf, {}).get(key, 0)) for wf in workflows) + " |")
    rate = []
    for wf in workflows:
        a = agg.get(wf, {})
        p, u = a.get("produced", 0), a.get("ungrounded", 0)
        rate.append(f"{u / p * 100:.1f}%" if p else "-")
    w.append("| **Audit-flagged rate** | " + " | ".join(rate) + " |")
    w.append("")
    for wf in workflows:
        ex = agg.get(wf, {}).get("examples", [])
        if not ex:
            continue
        w.append(f"### {wf.upper()} - flagged examples (possible unsupported additions)\n")
        for e in ex:
            w.append(f"- **{e['title_id']}** ({e['label']}) added "
                     f"{', '.join(repr(x) for x in e['invented'])} - "
                     f"{e['outcome']}, rubric {e['rubric_total']}/12, "
                     f"groundedness {e['rubric_groundedness']}")
            w.append(f"  - in:  `{e['original']}`")
            w.append(f"  - out: `{e['final_title']}`")
        w.append("")
    return w


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    run_dir = Path(sys.argv[1])
    here = Path(__file__).parent
    labels: dict = {}
    for ds in ("titles_1000.json", "test_titles.json"):
        p = here / ds
        if p.exists():
            for t in json.loads(p.read_text(encoding="utf-8"))["titles"]:
                labels.setdefault(t["id"], t["intended_label"])
    results = []
    for wf in ("loop", "graph"):
        f = run_dir / f"{wf}_results.json"
        if f.exists():
            results += json.loads(f.read_text(encoding="utf-8"))
    agg = audit_results(results, labels)
    print("\n".join(render(agg)))
    print("\n".join(render_candidates(audit_candidates(results))))


if __name__ == "__main__":
    main()
