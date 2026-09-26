"""Deterministic groundedness audit. No model involved.

The experiment uses the same model to generate titles and to score them, and
that evaluator has been observed both catching an invented product noun and
praising one. So this check does not ask a model anything: a rewritten title
may reorder, drop, recase or repunctuate the input's words, but it may not
introduce a new content word. Anything it introduces is flagged.

Conservative by design - it is meant to have very few false positives, at the
cost of missing some real fabrications:

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
# under-reports fabrication rather than inflating it with formatting noise.
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
    """Content words present in the output but not derivable from the input."""
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


def render(agg: dict, workflows=("loop", "graph")) -> list[str]:
    w: list[str] = []
    w.append("## Deterministic groundedness audit\n")
    w.append("No model involved. A rewritten title may reorder, drop, recase or")
    w.append("repunctuate the input's words; introducing a new content word is a")
    w.append("fabrication. Conservative: few false positives, some real misses.\n")
    w.append("| Metric | " + " | ".join(wf.upper() for wf in workflows) + " |")
    w.append("|---" * (len(workflows) + 1) + "|")
    rows = [
        ("Titles produced (not routed to human)", "produced"),
        ("Containing an invented word", "ungrounded"),
        ("...and PASSed the rubric anyway", "approved_ungrounded"),
        ("Ambiguous inputs given a title", "unclear_produced"),
        ("...of those, ungrounded", "unclear_ungrounded"),
    ]
    for label, key in rows:
        w.append(f"| {label} | " + " | ".join(str(agg.get(wf, {}).get(key, 0)) for wf in workflows) + " |")
    rate = []
    for wf in workflows:
        a = agg.get(wf, {})
        p, u = a.get("produced", 0), a.get("ungrounded", 0)
        rate.append(f"{u / p * 100:.1f}%" if p else "-")
    w.append("| **Fabrication rate** | " + " | ".join(rate) + " |")
    w.append("")
    for wf in workflows:
        ex = agg.get(wf, {}).get("examples", [])
        if not ex:
            continue
        w.append(f"### {wf.upper()} — flagged examples\n")
        for e in ex:
            w.append(f"- **{e['title_id']}** ({e['label']}) invented "
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


if __name__ == "__main__":
    main()
